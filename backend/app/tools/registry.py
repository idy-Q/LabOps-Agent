"""工具注册中心与审计拦截机制 (Tools Registry & Audit Interceptor)

负责：
1. @tool 注册装饰器
2. 自动化生成符合 OpenAI Function Calling 标准的 JSON Schema
3. 统一分发执行工具函数并自动持久化写入 AuditLog 审计日志表
"""

import inspect
import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union, get_args, get_origin
from sqlalchemy.orm import Session

from app.db.models import AuditLog

logger = logging.getLogger(__name__)


@dataclass
class ToolMetadata:
    """已注册工具的元数据结构"""

    name: str
    description: str
    func: Callable
    parameters_schema: Dict[str, Any]
    requires_db: bool = False
    requires_trace_id: bool = False

    def to_openai_schema(self) -> Dict[str, Any]:
        """生成 OpenAI Function Calling 标准描述结构"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters_schema,
            },
        }


# 全局工具注册表
_TOOL_REGISTRY: Dict[str, ToolMetadata] = {}


def _parse_param_docs_from_docstring(docstring: Optional[str]) -> Dict[str, str]:
    """从函数 docstring 中提取参数描述"""
    if not docstring:
        return {}
    param_docs: Dict[str, str] = {}
    lines = docstring.strip().splitlines()
    for line in lines:
        line = line.strip()
        # 匹配 :param name: 描述
        m_sphinx = re.match(r"^:param\s+([a-zA-Z0-9_]+)\s*:\s*(.+)$", line)
        if m_sphinx:
            param_docs[m_sphinx.group(1)] = m_sphinx.group(2).strip()
            continue
        # 匹配 - name: 描述 或 name: 描述
        m_google = re.match(r"^[-*]?\s*([a-zA-Z0-9_]+)\s*:\s*(.+)$", line)
        if m_google:
            param_docs[m_google.group(1)] = m_google.group(2).strip()
    return param_docs


def _type_to_json_schema(py_type: Any) -> Dict[str, Any]:
    """将 Python 类型转换为 JSON Schema 类型描述"""
    if py_type is inspect.Parameter.empty:
        return {"type": "string"}

    origin = get_origin(py_type)
    args = get_args(py_type)

    # 展开 Union / Optional 类型
    if origin is Union:
        non_none = [arg for arg in args if arg is not type(None)]
        if len(non_none) == 1:
            return _type_to_json_schema(non_none[0])
        return {"type": "string"}

    # 处理 Literal 枚举
    try:
        from typing import Literal
        if origin is Literal:
            return {"type": "string", "enum": list(args)}
    except ImportError:
        pass

    if issubclass(py_type if isinstance(py_type, type) else object, str):
        return {"type": "string"}
    if issubclass(py_type if isinstance(py_type, type) else object, bool):
        return {"type": "boolean"}
    if issubclass(py_type if isinstance(py_type, type) else object, int):
        return {"type": "integer"}
    if issubclass(py_type if isinstance(py_type, type) else object, float):
        return {"type": "number"}
    if origin in (list, List) or issubclass(py_type if isinstance(py_type, type) else object, list):
        item_schema = _type_to_json_schema(args[0]) if args else {"type": "string"}
        return {"type": "array", "items": item_schema}
    if origin in (dict, Dict) or issubclass(py_type if isinstance(py_type, type) else object, dict):
        return {"type": "object"}

    return {"type": "string"}


def generate_function_schema(func: Callable, tool_name: str, description: str) -> Dict[str, Any]:
    """从函数类型注解与文档生成 JSON Schema"""
    sig = inspect.signature(func)
    doc = func.__doc__ or ""
    param_docs = _parse_param_docs_from_docstring(doc)

    properties: Dict[str, Any] = {}
    required: List[str] = []

    # 排除系统级内部参数 (如 db 会话与 trace_id 链路编号)
    system_param_names = {"db", "trace_id"}

    for param_name, param in sig.parameters.items():
        if param_name in system_param_names:
            continue
        if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue

        param_schema = _type_to_json_schema(param.annotation)
        if param_name in param_docs:
            param_schema["description"] = param_docs[param_name]

        properties[param_name] = param_schema

        if param.default is inspect.Parameter.empty:
            required.append(param_name)

    schema: Dict[str, Any] = {
        "type": "object",
        "properties": properties,
    }
    if required:
        schema["required"] = required
    return schema


def tool(name: Optional[str] = None, description: Optional[str] = None) -> Callable:
    """注册工具函数的装饰器

    支持用法:
    @tool
    def my_tool(...): ...

    @tool(name="custom_name", description="自定义工具描述")
    def my_tool(...): ...
    """

    def decorator(fn: Callable) -> Callable:
        actual_name = name or fn.__name__
        if description:
            actual_doc = description
        elif fn.__doc__ and fn.__doc__.strip():
            actual_doc = fn.__doc__.strip().splitlines()[0]
        else:
            actual_doc = actual_name

        sig = inspect.signature(fn)
        requires_db = "db" in sig.parameters
        requires_trace_id = "trace_id" in sig.parameters

        params_schema = generate_function_schema(fn, actual_name, actual_doc)

        metadata = ToolMetadata(
            name=actual_name,
            description=actual_doc,
            func=fn,
            parameters_schema=params_schema,
            requires_db=requires_db,
            requires_trace_id=requires_trace_id,
        )

        _TOOL_REGISTRY[actual_name] = metadata
        return fn

    if callable(name):
        actual_func = name
        name = None
        return decorator(actual_func)

    return decorator


def get_tool(name: str) -> Optional[ToolMetadata]:
    """根据名称查找工具元数据"""
    return _TOOL_REGISTRY.get(name)


def list_tools() -> List[ToolMetadata]:
    """返回当前已注册的所有工具列表"""
    return list(_TOOL_REGISTRY.values())


def get_tools_schemas() -> List[Dict[str, Any]]:
    """返回符合 OpenAI Function Calling 标准的全部工具描述列表"""
    return [item.to_openai_schema() for item in _TOOL_REGISTRY.values()]


def clear_registry() -> None:
    """清空工具注册表 (主要用于单测隔离)"""
    _TOOL_REGISTRY.clear()


def execute_tool(
    name: str,
    args: Union[Dict[str, Any], str],
    db: Optional[Session] = None,
    trace_id: Optional[str] = None,
) -> Dict[str, Any]:
    """统一派发工具执行，并在执行前后自动持久化 AuditLog 审计日志

    :param name: 工具名称
    :param args: 工具调用参数 (字典或 JSON 字符串)
    :param db: SQLAlchemy 数据库会话
    :param trace_id: 分布式调用链路跟踪编号
    :return: 工具执行输出结果字典
    """
    close_db_on_finish = False
    if db is None:
        try:
            from app.db.session import SessionLocal
            db = SessionLocal()
            close_db_on_finish = True
        except Exception as e:
            logger.warning("execute_tool 无法初始化独立数据库会话: %s", str(e))
            db = None

    try:
        # 1. 参数解析
        parsed_args: Dict[str, Any] = {}
        if isinstance(args, str):
            try:
                parsed_args = json.loads(args) if args.strip() else {}
            except json.JSONDecodeError as err:
                error_msg = f"工具入参 JSON 解析失败: {str(err)}"
                _save_audit_log(
                    db=db,
                    trace_id=trace_id,
                    tool_name=name,
                    tool_args=args,
                    tool_result={"status": "error", "message": error_msg},
                    status="FAILED",
                )
                return {"status": "error", "message": error_msg}
        elif isinstance(args, dict):
            parsed_args = args
        else:
            parsed_args = {}

        tool_meta = get_tool(name)
        if not tool_meta:
            error_msg = f"未注册的工具: '{name}'"
            _save_audit_log(
                db=db,
                trace_id=trace_id,
                tool_name=name,
                tool_args=parsed_args,
                tool_result={"status": "error", "message": error_msg},
                status="FAILED",
            )
            return {"status": "error", "message": error_msg}

        # 2. 组装实际执行入参 (注入 db 或 trace_id 并过滤模型幻觉参数)
        call_kwargs = dict(parsed_args)
        sig = inspect.signature(tool_meta.func)
        if "db" in sig.parameters and "db" not in call_kwargs:
            call_kwargs["db"] = db
        if "trace_id" in sig.parameters and "trace_id" not in call_kwargs:
            call_kwargs["trace_id"] = trace_id

        # 智能参数别名映射 (提高大模型 Function Calling 参数调用的容错与鲁棒性)
        param_aliases = {
            "asset_no": ["device_id", "asset_id"],
            "device_id": ["asset_no", "device_no"],
            "ticket_no": ["ticket_id"],
            "ticket_id": ["ticket_no"],
        }
        for target_p, aliases in param_aliases.items():
            if target_p in sig.parameters and target_p not in call_kwargs:
                for alias in aliases:
                    if alias in call_kwargs:
                        call_kwargs[target_p] = call_kwargs[alias]
                        break

        has_var_keyword = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
        if not has_var_keyword:
            valid_params = set(sig.parameters.keys())
            unexpected = set(call_kwargs.keys()) - valid_params
            if unexpected:
                logger.warning("工具 %s 接收到多余参数，已自动过滤: %s", name, unexpected)
                call_kwargs = {k: v for k, v in call_kwargs.items() if k in valid_params}

        # 3. 执行工具
        try:
            raw_result = tool_meta.func(**call_kwargs)
            if isinstance(raw_result, dict):
                result = raw_result
            else:
                result = {"status": "success", "data": raw_result}

            # 4. 成功时持久化 AuditLog
            _save_audit_log(
                db=db,
                trace_id=trace_id,
                tool_name=name,
                tool_args=parsed_args,
                tool_result=result,
                status="SUCCESS",
            )
            return result

        except Exception as exc:
            logger.exception("执行工具 %s 发生异常: %s", name, str(exc))
            if db is not None:
                try:
                    db.rollback()
                except Exception:
                    pass
            result = {"status": "error", "message": f"工具执行异常: {str(exc)}"}
            _save_audit_log(
                db=db,
                trace_id=trace_id,
                tool_name=name,
                tool_args=parsed_args,
                tool_result=result,
                status="FAILED",
            )
            return result
    finally:
        if close_db_on_finish and db is not None:
            db.close()


def _save_audit_log(
    db: Optional[Session],
    trace_id: Optional[str],
    tool_name: str,
    tool_args: Any,
    tool_result: Any,
    status: str,
) -> None:
    """写入 AuditLog 数据表记录 (具备循环引用与超长非结构化对象安全降级)"""
    if db is None:
        return

    try:
        try:
            args_str = json.dumps(tool_args, ensure_ascii=False, default=str) if tool_args is not None else None
        except Exception:
            args_str = str(tool_args)[:4000]

        try:
            res_str = json.dumps(tool_result, ensure_ascii=False, default=str) if tool_result is not None else None
        except Exception:
            res_str = str(tool_result)[:4000]

        audit = AuditLog(
            trace_id=trace_id,
            tool_name=tool_name,
            tool_args=args_str,
            tool_result=res_str,
            status=status,
        )
        db.add(audit)
        db.commit()
    except Exception as e:
        try:
            db.rollback()
        except Exception:
            pass
        logger.warning("记录工具调用审计日志失败: %s", str(e))

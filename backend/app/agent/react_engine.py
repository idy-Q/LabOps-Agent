"""手写轻量级 ReAct 调度引擎 (Agent Core)

基于第一性原理与原生 Python 手写，无任何第三方黑盒 Agent 框架（如 LangChain）。
具备：
1. 白盒化 ReAct (Reasoning + Acting) 状态机循环 (带 max_steps 保护)
2. 双模驱动（支持真实商业大模型 OpenAI 兼容端点 + 零依赖确定性本地 Mock 大脑）
3. 同步调用 `run()` 与流式生成器 `stream_run()`（输出标准结构化事件，供 SSE 联动）
4. 全流程自动持久化写入 AuditLog 与 ChatHistory 表
"""

import json
import logging
import re
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Generator, List, Optional
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import ChatHistory
from app.agent.prompts import SYSTEM_PROMPT
from app.tools.registry import execute_tool, get_tools_schemas

logger = logging.getLogger(__name__)


@dataclass
class AgentEvent:
    """Agent 流式事件结构 (用于阶段 4 SSE 标准契约)"""

    type: str  # think, tool_start, tool_end, content, done
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type, **self.data}


@dataclass
class AgentResult:
    """Agent 同步执行结果"""

    session_id: str
    trace_id: str
    content: str
    thought: str
    steps: int
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)


class MockDecisionBrain:
    """确定性本地规则推理大脑 (Mock Brain)

    用于无 API Key、断网离线、自动化单测与答辩免死金牌演示。
    具备对机房巡检、超温告警、工单创建与流转、资产台账检索与借还的确定性多步状态决策能力。
    """

    @classmethod
    def decide(cls, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """根据当前对话历史和工具返回结果，决定下一步行为 (思考/调工具/最终回复)"""
        user_prompt = ""
        for m in messages:
            if m.get("role") == "user":
                user_prompt = m.get("content", "")

        # 收集已执行过的工具名与结果
        executed_tools: List[str] = []
        tool_results: Dict[str, Any] = {}
        for m in messages:
            if m.get("role") == "tool":
                t_name = m.get("name", "")
                executed_tools.append(t_name)
                try:
                    tool_results[t_name] = json.loads(m.get("content", "{}"))
                except Exception:
                    tool_results[t_name] = {}

        # 提取关键实体
        device_match = re.search(r"(DEV[_-][A-Z0-9]+-[0-9]+|DEV-[A-Z]+-[0-9]+)", user_prompt, re.IGNORECASE)
        device_id = device_match.group(1).upper().replace("_", "-") if device_match else "DEV-SRV-201"

        ticket_match = re.search(r"(TK-[0-9]{8}-[A-Za-z0-9]+)", user_prompt, re.IGNORECASE)
        ticket_no = ticket_match.group(1).upper() if ticket_match else None

        # -------------------------------------------------------------
        # 决策逻辑 1：工单状态推进流转 (update_ticket_status)
        # -------------------------------------------------------------
        is_ticket_update = (
            any(kw in user_prompt for kw in ["更新工单", "修改工单", "办结工单", "办结", "结单", "关闭工单", "解决工单", "处理工单"])
            or (ticket_no and any(kw in user_prompt for kw in ["更新", "改", "处理", "解决", "关闭", "办结", "推进", "状态"]))
        )
        if is_ticket_update:
            if "update_ticket_status" not in executed_tools:
                target_status = "RESOLVED"
                if any(kw in user_prompt for kw in ["关闭", "办结", "CLOSED", "归档"]):
                    target_status = "CLOSED"
                elif any(kw in user_prompt for kw in ["解决", "RESOLVED", "已解决"]):
                    target_status = "RESOLVED"
                elif any(kw in user_prompt for kw in ["处理中", "进行中", "PROCESSING"]):
                    target_status = "PROCESSING"
                elif any(kw in user_prompt for kw in ["待办", "PENDING"]):
                    target_status = "PENDING"

                target_tk = ticket_no or "TK-20260901-001"
                append_match = re.search(r"(?:说明|记录|备注|处置|追加)[：:\s]*([^\n，。]+)", user_prompt)
                desc_append = append_match.group(1).strip() if append_match else "管理员指令推进工单状态"

                return {
                    "thought": f"管理员请求推进工单状态，调用 update_ticket_status 将工单 {target_tk} 更新为 {target_status}。",
                    "tool_calls": [
                        {
                            "id": f"call_{uuid.uuid4().hex[:8]}",
                            "function": {
                                "name": "update_ticket_status",
                                "arguments": json.dumps(
                                    {
                                        "ticket_no": target_tk,
                                        "status": target_status,
                                        "description_append": desc_append,
                                    },
                                    ensure_ascii=False,
                                ),
                            },
                        }
                    ],
                }

            u_res = tool_results.get("update_ticket_status", {})
            msg = u_res.get("message", "工单状态已更新")
            return {
                "thought": "已完成工单状态更新并留痕，向管理员返回流转结果。",
                "content": f"【工单状态流转通知】\n{msg}",
            }

        # -------------------------------------------------------------
        # 决策逻辑 2：资产健康状态变更 (update_asset_health)
        # -------------------------------------------------------------
        is_asset_health_update = (
            any(kw in user_prompt for kw in ["更新设备健康", "变更健康", "修改健康", "健康状态改为", "状态改为健康", "标记为健康", "标记为良好", "标记为正常", "设为正常", "设为良好", "恢复健康"])
            or (device_match and any(kw in user_prompt for kw in ["健康状态更新为", "健康更新为", "设为"]) and any(h in user_prompt for h in ["HEALTHY", "WARNING", "OVERHEAT", "OFFLINE", "良好", "正常", "预警", "过热", "离线"]))
        )
        if is_asset_health_update:
            if "update_asset_health" not in executed_tools:
                target_health = "HEALTHY"
                if any(kw in user_prompt for kw in ["HEALTHY", "良好", "正常"]):
                    target_health = "HEALTHY"
                elif any(kw in user_prompt for kw in ["WARNING", "预警"]):
                    target_health = "WARNING"
                elif any(kw in user_prompt for kw in ["OVERHEAT", "过热", "高温"]):
                    target_health = "OVERHEAT"
                elif any(kw in user_prompt for kw in ["OFFLINE", "离线", "故障"]):
                    target_health = "OFFLINE"

                return {
                    "thought": f"管理员请求更新设备健康等级，调用 update_asset_health 将设备 {device_id} 标记为 {target_health}。",
                    "tool_calls": [
                        {
                            "id": f"call_{uuid.uuid4().hex[:8]}",
                            "function": {
                                "name": "update_asset_health",
                                "arguments": json.dumps(
                                    {"asset_no": device_id, "health_status": target_health},
                                    ensure_ascii=False,
                                ),
                            },
                        }
                    ],
                }

            h_res = tool_results.get("update_asset_health", {})
            return {
                "thought": "设备健康状态更新完毕，向管理员同步台账变更。",
                "content": f"【设备健康变更通知】\n{h_res.get('message', '设备健康状态更新完成')}",
            }

        # -------------------------------------------------------------
        # 决策逻辑 3：设备资产借用登记 (borrow_asset)
        # -------------------------------------------------------------
        if any(kw in user_prompt for kw in ["借用", "借出", "借走"]):
            if "borrow_asset" not in executed_tools:
                borrower = "科研教师"
                name_match = re.search(r"([^\s，。]+?(?:老师|同学|教授|工程师|工)|张三|李四|王五)", user_prompt)
                if name_match and name_match.group(1).strip():
                    borrower = name_match.group(1).strip()
                else:
                    alt_match = re.search(r"(?:帮|给|借给|借用人[是：:\s]*)([^\s，。]+?)(?:办理|借)", user_prompt)
                    if alt_match and alt_match.group(1).strip():
                        borrower = alt_match.group(1).strip()

                return {
                    "thought": f"管理员发起资产借用申请，调用 borrow_asset 工具办理设备 {device_id} 的借用登记。",
                    "tool_calls": [
                        {
                            "id": f"call_{uuid.uuid4().hex[:8]}",
                            "function": {
                                "name": "borrow_asset",
                                "arguments": json.dumps({"asset_no": device_id, "borrower": borrower}, ensure_ascii=False),
                            },
                        }
                    ],
                }
            b_res = tool_results.get("borrow_asset", {})
            return {
                "thought": "资产借用登记操作完成，向管理员同步最新台账变动。",
                "content": f"【资产借用登记通知】\n{b_res.get('message', '借用操作已处理')}",
            }

        # -------------------------------------------------------------
        # 决策逻辑 4：设备资产归还 (return_asset)
        # -------------------------------------------------------------
        if "归还" in user_prompt:
            if "return_asset" not in executed_tools:
                return {
                    "thought": f"管理员发起设备归还申请，调用 return_asset 工具恢复设备 {device_id} 为可用状态。",
                    "tool_calls": [
                        {
                            "id": f"call_{uuid.uuid4().hex[:8]}",
                            "function": {
                                "name": "return_asset",
                                "arguments": json.dumps({"asset_no": device_id}, ensure_ascii=False),
                            },
                        }
                    ],
                }
            r_res = tool_results.get("return_asset", {})
            return {
                "thought": "资产归还已入库，向管理员同步台账状态。",
                "content": f"【资产归还登记通知】\n{r_res.get('message', '归还操作已处理')}",
            }

        # -------------------------------------------------------------
        # 决策逻辑 5：规章制度与规范检索 (query_regulations)
        # -------------------------------------------------------------
        is_query_regulations = (
            any(kw in user_prompt for kw in ["规章", "制度", "规范", "用电", "应急", "PDU", "功率", "功耗", "借用规则", "审批流程", "上限", "维保", "预案", "滤网", "巡检要求", "巡检时间", "巡检频次", "巡检周期", "空调故障"])
            or ("巡检" in user_prompt and any(kw in user_prompt for kw in ["规定", "要求", "怎么做", "时间", "周期", "频次", "标准", "指引"]))
            or (any(kw in user_prompt for kw in ["怎么处理", "如何处理", "处置流程", "处置预案", "处理预案", "应急方案", "应急措施"]) and not device_match)
        ) and not any(kw in user_prompt for kw in ["查询工单", "创建工单"])
        if is_query_regulations:
            if "query_regulations" not in executed_tools:
                return {
                    "thought": "用户询问机房管理规章制度或应急规范，调用 query_regulations 工具进行检索。",
                    "tool_calls": [
                        {
                            "id": f"call_{uuid.uuid4().hex[:8]}",
                            "function": {
                                "name": "query_regulations",
                                "arguments": json.dumps({"query": user_prompt}, ensure_ascii=False),
                            },
                        }
                    ],
                }
            
            r_res = tool_results.get("query_regulations", "")
            if isinstance(r_res, dict):
                reg_text = r_res.get("data") or r_res.get("message") or str(r_res)
            else:
                reg_text = str(r_res)
            return {
                "thought": "检索到相关规章制度与应急预案，根据条款回答用户并标注来源。",
                "content": f"【规章制度查询结果】\n{reg_text}",
            }

        # -------------------------------------------------------------
        # 决策逻辑 6：机房监控与设备健康/超温排查流程 (get_server_metrics)
        # -------------------------------------------------------------
        if any(kw in user_prompt for kw in ["指标", "监控", "温度", "巡检", "排查", "超温", "传感器", "cpu", "内存"]):
            if "get_server_metrics" not in executed_tools:
                return {
                    "thought": f"管理员指令涉及设备排查，优先感知设备 {device_id} 的实时运行指标与温度传感器数据。",
                    "tool_calls": [
                        {
                            "id": f"call_{uuid.uuid4().hex[:8]}",
                            "function": {
                                "name": "get_server_metrics",
                                "arguments": json.dumps({"device_id": device_id}, ensure_ascii=False),
                            },
                        }
                    ],
                }

            metrics = tool_results.get("get_server_metrics", {})
            # 严格校验：若工具返回错误（如设备编号不存在），如实向管理员报告，不虚构正常指标
            if metrics.get("status") == "error":
                err_msg = metrics.get("message", f"未在机房资产台账中找到编号为 '{device_id}' 的设备，请核实设备编号")
                return {
                    "thought": f"设备 {device_id} 传感器感知反馈异常或不存在，向管理员如实反馈排查结论。",
                    "content": f"【机房设备排查提示】\n排查异常：{err_msg}",
                }

            is_overheat = metrics.get("health_status") == "OVERHEAT" or metrics.get("temperature", 0) > 40.0

            if is_overheat and "create_ticket" not in executed_tools:
                temp = metrics.get("temperature", 43.5)
                return {
                    "thought": f"传感器数据表明设备 {device_id} 核心温度达到 {temp}℃（>40℃），处于 OVERHEAT 严重状态！按机房应急规程必须立即自动创建高优先级排查工单。",
                    "tool_calls": [
                        {
                            "id": f"call_{uuid.uuid4().hex[:8]}",
                            "function": {
                                "name": "create_ticket",
                                "arguments": json.dumps(
                                    {
                                        "title": f"{device_id} 核心温度过热紧急处置工单",
                                        "description": f"实时监控监测到设备核心温度达到 {temp}℃，超过安全阈值 40℃，散热负荷异常，触发 OVERHEAT 报警，需现场检修风道与制冷。",
                                        "priority": "HIGH",
                                        "device_id": device_id,
                                    },
                                    ensure_ascii=False,
                                ),
                            },
                        }
                    ],
                }

            # 工具调用全部闭环，输出最终总结
            ticket_res = tool_results.get("create_ticket", {}).get("ticket", {})
            t_no = ticket_res.get("ticket_no", "TK-待指派")
            temp = metrics.get("temperature", 31.5)
            status_code = metrics.get("health_status", "HEALTHY")

            if is_overheat:
                content = (
                    f"【机房运维排查汇报】\n"
                    f"- 目标设备：`{device_id}` ({metrics.get('device_name', '服务器')})\n"
                    f"- 物理位置：{metrics.get('location', '实训楼201')}\n"
                    f"- 核心指标：温度 **{temp}℃**（[超温告警] 超过40℃安全红线），CPU占用率 {metrics.get('cpu_usage', 88.5)}%\n"
                    f"- 研判等级：**{status_code}**（严重过热警报）\n"
                    f"- 闭环操作：系统已自动为您生成高优先级维修工单（工单号：`{t_no}`），并持久化写入数据库。\n"
                    f"- 处置建议：请通知后勤运维人员现场核验散热风扇与机房空调温控。"
                )
            else:
                content = (
                    f"【机房设备指标正常汇报】\n"
                    f"- 目标设备：`{device_id}` ({metrics.get('device_name', '服务器')})\n"
                    f"- 核心指标：温度 **{temp}℃**（正常），CPU占用率 {metrics.get('cpu_usage', 30.0)}%\n"
                    f"- 研判等级：**HEALTHY**（运行良好）\n"
                    f"- 处置结论：设备各项温湿度指标均在安全阈值以内，无需创建工单。"
                )
            return {"thought": "已完成指标采集与分析闭环，为管理员呈现清晰排查报告。", "content": content}

        # -------------------------------------------------------------
        # 决策逻辑 6：主动直接创建工单 (create_ticket)
        # -------------------------------------------------------------
        is_direct_create_ticket = any(
            kw in user_prompt for kw in ["创建工单", "新建工单", "提交工单", "提工单", "建立工单", "发起工单"]
        )
        if is_direct_create_ticket:
            if "create_ticket" not in executed_tools:
                title_match = re.search(r"(?:创建工单|新建工单|提交工单|提工单|建立工单|发起工单)[：:\s]*(.+)", user_prompt)
                raw_title = title_match.group(1).strip() if title_match else user_prompt
                priority = "HIGH" if any(kw in user_prompt for kw in ["紧急", "高", "CRITICAL", "HIGH"]) else "MEDIUM"
                target_dev = device_match.group(1).upper() if device_match else None

                return {
                    "thought": "管理员请求新建运维工单，调用 create_ticket 工具持久化入库。",
                    "tool_calls": [
                        {
                            "id": f"call_{uuid.uuid4().hex[:8]}",
                            "function": {
                                "name": "create_ticket",
                                "arguments": json.dumps(
                                    {
                                        "title": raw_title[:60],
                                        "description": f"管理员指令提单：{raw_title}",
                                        "priority": priority,
                                        "device_id": target_dev,
                                    },
                                    ensure_ascii=False,
                                ),
                            },
                        }
                    ],
                }

            t_res = tool_results.get("create_ticket", {})
            return {
                "thought": "工单创建完毕，向管理员呈现工单详情与编号。",
                "content": f"【工单创建成功】\n{t_res.get('message', '工单创建成功')}",
            }

        # -------------------------------------------------------------
        # 决策逻辑 7：查询资产台账 (query_assets)
        # -------------------------------------------------------------
        is_query_assets = (
            any(kw in user_prompt for kw in ["查询资产", "资产列表", "台账", "查设备", "查看设备", "设备台账", "搜索设备", "查询设备", "检索资产", "设备列表"])
            or ("资产" in user_prompt and any(kw in user_prompt for kw in ["查询", "查看", "检索", "列表", "搜索", "有哪些"]))
            or ("设备" in user_prompt and any(kw in user_prompt for kw in ["查询", "查看", "检索", "列表", "搜索", "有哪些"]) and not any(kw in user_prompt for kw in ["指标", "监控", "温度", "巡检", "排查", "超温", "借用", "借出", "归还"]))
        )
        if is_query_assets:
            if "query_assets" not in executed_tools:
                q_args: Dict[str, Any] = {"limit": 5}
                if "服务器" in user_prompt:
                    q_args["category"] = "服务器"
                elif "网络" in user_prompt:
                    q_args["category"] = "网络设备"
                elif any(k in user_prompt for k in ["温控", "配电", "空调", "UPS"]):
                    q_args["category"] = "配电温控"
                elif any(k in user_prompt for k in ["教学", "实验"]):
                    q_args["category"] = "实验教学"

                if any(k in user_prompt for k in ["过热", "OVERHEAT", "高温"]):
                    q_args["health_status"] = "OVERHEAT"
                elif any(k in user_prompt for k in ["预警", "WARNING"]):
                    q_args["health_status"] = "WARNING"
                elif any(k in user_prompt for k in ["正常", "良好", "HEALTHY"]):
                    q_args["health_status"] = "HEALTHY"
                elif any(k in user_prompt for k in ["离线", "OFFLINE"]):
                    q_args["health_status"] = "OFFLINE"

                if any(k in user_prompt for k in ["可借", "空闲", "AVAILABLE"]):
                    q_args["borrow_status"] = "AVAILABLE"
                elif any(k in user_prompt for k in ["已借", "使用中", "IN_USE"]):
                    q_args["borrow_status"] = "IN_USE"

                if "GPU" in user_prompt:
                    q_args["keyword"] = "GPU"

                return {
                    "thought": "管理员请求检索资产台账，调用 query_assets 工具查询机房设备记录。",
                    "tool_calls": [
                        {
                            "id": f"call_{uuid.uuid4().hex[:8]}",
                            "function": {
                                "name": "query_assets",
                                "arguments": json.dumps(q_args, ensure_ascii=False),
                            },
                        }
                    ],
                }
            q_res = tool_results.get("query_assets", {})
            count = q_res.get("count", 0)
            assets = q_res.get("assets", [])
            if count == 0:
                assets_brief = "（暂未检索到符合条件的设备资产）"
            else:
                assets_brief = "\n".join(
                    [f"- `{a.get('asset_no')}`: {a.get('name')} [{a.get('health_status')}]（位置: {a.get('location')}，借用状态: {a.get('borrow_status')}）" for a in assets[:5]]
                )
            return {
                "thought": "已检索到最新台账，向管理员汇总展示。",
                "content": f"【资产台账查询结果】\n共检索到 {count} 条相关资产记录：\n{assets_brief}",
            }

        # -------------------------------------------------------------
        # 决策逻辑 8：查询工单列表 (query_tickets)
        # -------------------------------------------------------------
        if any(kw in user_prompt for kw in ["查询工单", "工单列表", "待办工单", "历史工单", "所有工单", "查看工单", "检索工单"]) or (
            "工单" in user_prompt and any(kw in user_prompt for kw in ["查询", "查看", "检索", "列表", "有哪些", "待办"]) and not any(kw in user_prompt for kw in ["创建", "新建", "提交", "提工单", "发起"])
        ):
            if "query_tickets" not in executed_tools:
                t_args: Dict[str, Any] = {"limit": 5}
                if "待办" in user_prompt:
                    t_args["status"] = "PENDING"
                elif "处理中" in user_prompt:
                    t_args["status"] = "PROCESSING"
                elif "已解决" in user_prompt:
                    t_args["status"] = "RESOLVED"
                elif any(k in user_prompt for k in ["关闭", "办结", "已关闭"]):
                    t_args["status"] = "CLOSED"

                if any(k in user_prompt for k in ["紧急", "高优先级", "CRITICAL", "HIGH"]):
                    t_args["priority"] = "HIGH"

                if ticket_match:
                    t_args["ticket_no"] = ticket_match.group(1).upper()
                if device_match:
                    t_args["device_id"] = device_match.group(1).upper()

                return {
                    "thought": "管理员请求查询工单，调用 query_tickets 检索符合条件的运维工单。",
                    "tool_calls": [
                        {
                            "id": f"call_{uuid.uuid4().hex[:8]}",
                            "function": {
                                "name": "query_tickets",
                                "arguments": json.dumps(t_args, ensure_ascii=False),
                            },
                        }
                    ],
                }
            t_res = tool_results.get("query_tickets", {})
            count = t_res.get("count", 0)
            tickets = t_res.get("tickets", [])
            if count == 0:
                tk_brief = "（当前未检索到符合条件的工单记录）"
            else:
                tk_brief = "\n".join(
                    [f"- `{t.get('ticket_no')}`: {t.get('title')} [{t.get('status')}]（优先级: {t.get('priority')}）" for t in tickets[:5]]
                )
            return {
                "thought": "已获取工单列表，呈现给管理员。",
                "content": f"【工单列表检索结果】\n当前系统共有 {count} 条符合条件的工单记录：\n{tk_brief}",
            }

        # 原逻辑9已被移至上方

        # 默认通用回复
        return {
            "thought": "用户进行常规询问，说明管家职能并提供运维指引。",
            "content": (
                "您好！我是高校机房智能运维管家（LabOps-Agent）。\n"
                "我具备机房服务器指标感知、温度超标（>40℃）自动工单闭环、资产借还登记与台账审计能力。\n"
                "您可以对我发送指令，例如：\n"
                "- `“查询DEV-SRV-201监控指标，若异常请自动提单”`\n"
                "- `“帮张老师办理DEV-SRV-202借出登记”`\n"
                "- `“查询当前机房全部异常设备台账”`"
            ),
        }


class ReActEngine:
    """手写 ReAct 调度引擎核心类"""

    def __init__(self, max_steps: Optional[int] = None):
        self.max_steps = max_steps or settings.REACT_MAX_STEPS
        self.mock_mode = settings.AGENT_MOCK_MODE.lower()

    def _should_use_mock(self) -> bool:
        """判定当前是否应采用本地 Mock 大脑"""
        if self.mock_mode == "mock":
            return True
        if self.mock_mode == "real":
            return False
        # auto 模式下：若无 Key 则默认自动降级为 Mock 大脑
        return not bool((settings.OPENAI_API_KEY or "").strip())

    def _call_llm(self, messages: List[Dict[str, Any]], tools_schemas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """统一调用决策大脑（真实 OpenAI 协议 API 或确定性 Mock 大脑）"""
        if self._should_use_mock():
            return MockDecisionBrain.decide(messages)

        try:
            from openai import OpenAI

            client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL,
            )
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL_NAME,
                messages=messages,
                tools=tools_schemas if tools_schemas else None,
                tool_choice="auto" if tools_schemas else None,
                temperature=0.2,
            )
            choice = response.choices[0]
            msg = choice.message
            tool_calls = []
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    tool_calls.append(
                        {
                            "id": tc.id,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                    )
            return {
                "thought": getattr(msg, "reasoning_content", None) or "模型分析用户意图并制定执行策略。",
                "content": msg.content or "",
                "tool_calls": tool_calls,
            }
        except Exception as exc:
            logger.warning("调用远程大模型 API 失败，自动容灾回退至本地 Mock 大脑: %s", str(exc))
            return MockDecisionBrain.decide(messages)

    def stream_run(
        self,
        user_prompt: str,
        session_id: Optional[str] = None,
        db: Optional[Session] = None,
        max_steps: Optional[int] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """流式生成器：执行 ReAct 状态机循环并实时产出结构化事件 (供 SSE 使用)"""
        active_session_id = session_id or f"sess-{uuid.uuid4().hex[:8]}"
        trace_id = f"trace-{uuid.uuid4().hex[:8]}"
        limit_steps = max_steps or self.max_steps
        tools_schemas = get_tools_schemas()

        # 持久化用户初始提问到 ChatHistory
        if db is not None:
            try:
                user_record = ChatHistory(
                    session_id=active_session_id,
                    role="user",
                    content=user_prompt,
                )
                db.add(user_record)
                db.commit()
            except Exception as e:
                db.rollback()
                logger.warning("记录用户会话历史失败: %s", str(e))

        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        step = 0
        final_content = ""
        accumulated_thought: List[str] = []

        while step < limit_steps:
            step += 1
            decision = self._call_llm(messages, tools_schemas)

            # 1. 产生思考过程事件
            thought_text = decision.get("thought", "")
            if thought_text:
                accumulated_thought.append(thought_text)
                yield AgentEvent(type="think", data={"thought": thought_text, "step": step}).to_dict()

            tool_calls = decision.get("tool_calls", [])

            # 2. 如果决策需要调用工具 (Acting 阶段)
            if tool_calls:
                # 规范化并记录 assistant 的 tool_calls 消息
                raw_tool_calls = []
                for idx, tc in enumerate(tool_calls):
                    call_id = tc.get("id") or f"call_{step}_{idx}"
                    fn_data = tc.get("function", {})
                    fn_name = fn_data.get("name", "")
                    fn_args = fn_data.get("arguments", "{}")
                    if not isinstance(fn_args, str):
                        fn_args = json.dumps(fn_args, ensure_ascii=False)
                    raw_tool_calls.append({
                        "id": call_id,
                        "type": "function",
                        "function": {
                            "name": fn_name,
                            "arguments": fn_args,
                        },
                    })

                messages.append({
                    "role": "assistant",
                    "content": decision.get("content") or "",
                    "tool_calls": raw_tool_calls,
                })

                for idx, tc in enumerate(tool_calls):
                    call_id = raw_tool_calls[idx]["id"]
                    t_name = tc["function"]["name"]
                    raw_args = tc["function"]["arguments"]

                    try:
                        args_dict = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                    except Exception:
                        args_dict = {}

                    # 推送 tool_start 事件
                    yield AgentEvent(
                        type="tool_start",
                        data={"name": t_name, "args": args_dict, "step": step},
                    ).to_dict()

                    # 统一分发执行工具并持久化 AuditLog
                    result = execute_tool(
                        name=t_name,
                        args=args_dict,
                        db=db,
                        trace_id=trace_id,
                    )

                    # 推送 tool_end 事件
                    yield AgentEvent(
                        type="tool_end",
                        data={"name": t_name, "result": result, "step": step},
                    ).to_dict()

                    # 将对应工具的执行结果接入会话上下文
                    messages.append({
                        "role": "tool",
                        "name": t_name,
                        "tool_call_id": call_id,
                        "content": json.dumps(result, ensure_ascii=False, default=str),
                    })

                # 本轮工具全部执行完毕，继续进入下一轮 while 思考研判
                continue

            # 3. 如果决策直接给出回答 (Final Answer 阶段)
            content_text = decision.get("content", "")
            final_content = content_text
            yield AgentEvent(
                type="content",
                data={"text": content_text, "delta": content_text},
            ).to_dict()
            break

        # 若达到最大步数仍未结束，进行保护性截断
        if step >= limit_steps and not final_content:
            fallback = f"【系统提示】Agent 执行已达单次最大推理步数上限（max_steps={limit_steps}），已安全截断。"
            final_content = fallback
            yield AgentEvent(type="content", data={"text": fallback, "delta": fallback}).to_dict()

        # 持久化 Assistant 最终回复与推理链到 ChatHistory
        full_thought_str = "\n".join(accumulated_thought) if accumulated_thought else None
        if db is not None:
            try:
                assistant_record = ChatHistory(
                    session_id=active_session_id,
                    role="assistant",
                    content=final_content,
                    thought=full_thought_str,
                )
                db.add(assistant_record)
                db.commit()
            except Exception as e:
                db.rollback()
                logger.warning("记录 Assistant 会话历史失败: %s", str(e))

        # 产出 done 结束事件
        yield AgentEvent(
            type="done",
            data={
                "session_id": active_session_id,
                "trace_id": trace_id,
                "total_steps": step,
            },
        ).to_dict()

    def run(
        self,
        user_prompt: str,
        session_id: Optional[str] = None,
        db: Optional[Session] = None,
        max_steps: Optional[int] = None,
    ) -> AgentResult:
        """同步执行入口：聚合流式事件并返回完整结果"""
        final_content = ""
        thoughts: List[str] = []
        tool_calls: List[Dict[str, Any]] = []
        active_session_id = session_id or ""
        trace_id = ""
        steps = 0

        for event in self.stream_run(user_prompt=user_prompt, session_id=session_id, db=db, max_steps=max_steps):
            e_type = event.get("type")
            if e_type == "think":
                thoughts.append(event.get("thought", ""))
            elif e_type == "tool_start":
                tool_calls.append({"name": event.get("name"), "args": event.get("args")})
            elif e_type == "content":
                final_content = event.get("text", "")
            elif e_type == "done":
                active_session_id = event.get("session_id", active_session_id)
                trace_id = event.get("trace_id", "")
                steps = event.get("total_steps", steps)

        return AgentResult(
            session_id=active_session_id,
            trace_id=trace_id,
            content=final_content,
            thought="\n".join(thoughts),
            steps=steps,
            tool_calls=tool_calls,
        )

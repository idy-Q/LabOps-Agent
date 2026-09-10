"""阶段 2 工具集与注册审计自动化测试套件

测试项覆盖：
1. 工具注册中心 (Tool Registry) 与 OpenAI Function Calling Schema 自动化生成校验
2. 服务器健康指标监控工具 (get_server_metrics)：正常设备、超温设备 (>40℃) 报警、非存在设备与离线兜底
3. 运维工单全生命周期工具 (create_ticket, query_tickets, update_ticket_status)：自动编号、持久化、多条件筛选、状态推进
4. 资产台账与借还工具 (query_assets, borrow_asset, return_asset, update_asset_health)：多维查询、防重复借出安全校验、资产归还、健康变更
5. 统一调度拦截与 AuditLog 审计日志持久化校验 (成功记录、失败记录、入参/出参 JSON 结构化)
"""

import json
import os
import tempfile
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.init_db import init_db
from app.db.models import Asset, AuditLog, Ticket
from app.tools.registry import (
    clear_registry,
    execute_tool,
    get_tool,
    get_tools_schemas,
    list_tools,
    tool,
)
import app.tools as tools_module
from app.tools.metric_tools import get_server_metrics
from app.tools.ticket_tools import create_ticket, query_tickets, update_ticket_status
from app.tools.asset_tools import borrow_asset, query_assets, return_asset, update_asset_health


@pytest.fixture(scope="function")
def test_db():
    """每个测试函数创建独立的临时 SQLite 数据库并预置初始种子数据"""
    temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_file.close()
    test_db_url = f"sqlite:///{temp_file.name}"

    engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    init_db(seed=True, custom_engine=engine, custom_session_factory=TestingSession)

    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()
        if os.path.exists(temp_file.name):
            try:
                os.remove(temp_file.name)
            except Exception:
                pass


# ---------------------------------------------------------
# 1. 工具注册中心与 Schema 校验
# ---------------------------------------------------------
def test_tool_registry_and_schema_generation():
    """验证 @tool 装饰器、工具元数据提取与 OpenAI Function Calling 标准 Schema"""
    registered = list_tools()
    registered_names = [t.name for t in registered]

    # 验证核心业务工具已全部自动注册
    expected_tools = [
        "get_server_metrics",
        "create_ticket",
        "query_tickets",
        "update_ticket_status",
        "query_assets",
        "borrow_asset",
        "return_asset",
        "update_asset_health",
    ]
    for exp in expected_tools:
        assert exp in registered_names, f"工具 {exp} 未能正确注册入工具中心"

    # 验证 OpenAI Schema 规范
    schemas = get_tools_schemas()
    assert len(schemas) == len(registered)

    metric_schema = next(s for s in schemas if s["function"]["name"] == "get_server_metrics")
    assert metric_schema["type"] == "function"
    assert "parameters" in metric_schema["function"]
    assert "device_id" in metric_schema["function"]["parameters"]["properties"]
    assert "device_id" in metric_schema["function"]["parameters"]["required"]
    # 验证内部 db 会话参数已被排除在对外 Schema 之外
    assert "db" not in metric_schema["function"]["parameters"]["properties"]


def test_custom_tool_registration():
    """验证动态注册自定义工具"""
    @tool(name="custom_ping", description="测试探针工具")
    def ping_tool(host: str, count: int = 4) -> dict:
        return {"host": host, "count": count, "pong": True}

    t = get_tool("custom_ping")
    assert t is not None
    assert t.name == "custom_ping"
    assert t.description == "测试探针工具"
    assert "host" in t.parameters_schema["required"]
    assert "count" not in t.parameters_schema.get("required", [])


# ---------------------------------------------------------
# 2. 服务器健康指标监控工具测试 (metric_tools)
# ---------------------------------------------------------
def test_get_server_metrics_overheat(test_db):
    """验证设备核心温度 >40℃ 时自动识别为 OVERHEAT 报警"""
    # DEV-SRV-201 在种子数据中标记为 OVERHEAT
    res = get_server_metrics(device_id="DEV-SRV-201", db=test_db)
    assert res["status"] == "success"
    assert res["device_id"] == "DEV-SRV-201"
    assert res["temperature"] > 40.0
    assert res["health_status"] == "OVERHEAT"
    assert res["alert"] is True
    assert res["alert_level"] == "CRITICAL"
    assert "高温告警" in res["alert_message"]


def test_get_server_metrics_healthy(test_db):
    """验证正常设备指标处于 HEALTHY 且无告警"""
    res = get_server_metrics(device_id="DEV-SRV-202", db=test_db)
    assert res["status"] == "success"
    assert res["device_id"] == "DEV-SRV-202"
    assert res["temperature"] <= 40.0
    assert res["health_status"] == "HEALTHY"
    assert res["alert"] is False
    assert res["alert_level"] == "NORMAL"


def test_get_server_metrics_not_found(test_db):
    """验证查询不存在设备时的友好错误返回"""
    res = get_server_metrics(device_id="DEV-NON-EXISTENT", db=test_db)
    assert res["status"] == "error"
    assert "未在机房资产台账中找到" in res["message"]


def test_get_server_metrics_standalone():
    """验证在无数据库注入时的传感器指标模拟兜底能力"""
    res = get_server_metrics(device_id="DEV-SRV-201", db=None)
    assert res["status"] == "success"
    assert res["health_status"] == "OVERHEAT"
    assert res["temperature"] > 40.0

    res_normal = get_server_metrics(device_id="DEV-SRV-202", db=None)
    assert res_normal["status"] == "success"
    assert res_normal["health_status"] == "HEALTHY"


# ---------------------------------------------------------
# 3. 运维工单工具测试 (ticket_tools)
# ---------------------------------------------------------
def test_create_and_query_tickets(test_db):
    """验证工单自动编号分配、持久化写入与条件筛选"""
    # 1. 创建新工单
    res = create_ticket(
        title="2号机房精密空调突发排水管道漏水",
        description="实训楼201空调压缩机下方出现积水，需紧急排查并疏通管道。",
        priority="HIGH",
        device_id="DEV-UPS-201",
        creator="LabOps-Agent",
        db=test_db,
    )
    assert res["status"] == "success"
    ticket_data = res["ticket"]
    assert ticket_data["ticket_no"].startswith("TK-")
    assert ticket_data["priority"] == "HIGH"
    assert ticket_data["status"] == "PENDING"
    assert ticket_data["device_id"] == "DEV-UPS-201"

    # 验证写入 SQLite 数据库
    db_ticket = test_db.query(Ticket).filter(Ticket.ticket_no == ticket_data["ticket_no"]).first()
    assert db_ticket is not None
    assert db_ticket.title == "2号机房精密空调突发排水管道漏水"

    # 2. 多条件查询工单
    q_res = query_tickets(status="PENDING", priority="HIGH", db=test_db)
    assert q_res["status"] == "success"
    assert q_res["count"] >= 1
    found_nos = [t["ticket_no"] for t in q_res["tickets"]]
    assert ticket_data["ticket_no"] in found_nos


def test_update_ticket_status(test_db):
    """验证工单状态推进流转与处置内容追加"""
    # 获取一条种子工单
    seed_ticket = test_db.query(Ticket).first()
    target_no = seed_ticket.ticket_no

    res = update_ticket_status(
        ticket_no=target_no,
        status="RESOLVED",
        description_append="已现场清洗冷凝器并更换散热硅脂，机柜温度已降至 32℃。",
        db=test_db,
    )
    assert res["status"] == "success"
    assert res["ticket"]["status"] == "RESOLVED"
    assert "更换散热硅脂" in res["ticket"]["description"]

    # 数据库核验
    updated = test_db.query(Ticket).filter(Ticket.ticket_no == target_no).first()
    assert updated.status == "RESOLVED"
    assert "[追加处置]" in updated.description

    # 测试非法状态校验
    invalid_res = update_ticket_status(ticket_no=target_no, status="UNKNOWN_STATUS", db=test_db)
    assert invalid_res["status"] == "error"
    assert "无效的工单状态" in invalid_res["message"]


# ---------------------------------------------------------
# 4. 资产台账与借还工具测试 (asset_tools)
# ---------------------------------------------------------
def test_query_assets_with_filters(test_db):
    """验证资产台账多维度检索 (关键词、分类、健康等级)"""
    # 关键词模糊搜索
    res_kw = query_assets(keyword="GPU", db=test_db)
    assert res_kw["status"] == "success"
    assert any("GPU" in a["name"] or "GPU" in (a["specs"] or "") for a in res_kw["assets"])

    # 过滤健康状态为 OVERHEAT 的设备
    res_overheat = query_assets(health_status="OVERHEAT", db=test_db)
    assert res_overheat["status"] == "success"
    for a in res_overheat["assets"]:
        assert a["health_status"] == "OVERHEAT"


def test_asset_borrow_and_duplicate_prevention(test_db):
    """验证资产借用登记与核心防重复借出拦截校验"""
    # DEV-SRV-202 在种子数据中处于 AVAILABLE 状态
    target_asset = "DEV-SRV-202"

    # 1. 正常借出
    res1 = borrow_asset(asset_no=target_asset, borrower="张三老师", db=test_db)
    assert res1["status"] == "success"
    assert res1["asset"]["borrow_status"] == "IN_USE"
    assert res1["asset"]["borrower"] == "张三老师"

    # 数据库核验
    a = test_db.query(Asset).filter(Asset.asset_no == target_asset).first()
    assert a.borrow_status == "IN_USE"
    assert a.borrower == "张三老师"

    # 2. 防重复借出校验：再次尝试借出已被占用的设备，应被拦截冲突
    res2 = borrow_asset(asset_no=target_asset, borrower="李四同学", db=test_db)
    assert res2["status"] == "conflict"
    assert "无法重复借出" in res2["message"]

    # 状态保持未变
    test_db.refresh(a)
    assert a.borrow_status == "IN_USE"
    assert a.borrower == "张三老师"


def test_asset_return_and_health_update(test_db):
    """验证资产归还与健康状态变更"""
    # DEV-SRV-201 在种子数据中处于 IN_USE 状态
    target_asset = "DEV-SRV-201"

    # 1. 办理归还
    res_ret = return_asset(asset_no=target_asset, db=test_db)
    assert res_ret["status"] == "success"
    assert res_ret["asset"]["borrow_status"] == "AVAILABLE"
    assert res_ret["asset"]["borrower"] is None

    # 重复归还预警
    res_ret_again = return_asset(asset_no=target_asset, db=test_db)
    assert res_ret_again["status"] == "warning"
    assert "无需重复归还" in res_ret_again["message"]

    # 2. 更新健康状态
    res_health = update_asset_health(asset_no=target_asset, health_status="HEALTHY", db=test_db)
    assert res_health["status"] == "success"
    assert res_health["asset"]["health_status"] == "HEALTHY"

    # 数据库核验
    a = test_db.query(Asset).filter(Asset.asset_no == target_asset).first()
    assert a.health_status == "HEALTHY"


# ---------------------------------------------------------
# 5. 统一调度入口 execute_tool 与 AuditLog 审计日志持久化测试
# ---------------------------------------------------------
def test_execute_tool_audit_logging_success(test_db):
    """验证每次工具执行成功后自动写入 AuditLog 审计表"""
    trace_id = "test-trace-1001"
    args = {"device_id": "DEV-SRV-201"}

    res = execute_tool(
        name="get_server_metrics",
        args=args,
        db=test_db,
        trace_id=trace_id,
    )
    assert res["status"] == "success"

    # 检查 AuditLog 表中是否成功生成审计记录
    logs = test_db.query(AuditLog).filter(AuditLog.trace_id == trace_id).all()
    assert len(logs) == 1
    log = logs[0]
    assert log.tool_name == "get_server_metrics"
    assert log.status == "SUCCESS"

    parsed_args = json.loads(log.tool_args)
    assert parsed_args["device_id"] == "DEV-SRV-201"

    parsed_res = json.loads(log.tool_result)
    assert parsed_res["status"] == "success"
    assert parsed_res["temperature"] > 40.0


def test_execute_tool_audit_logging_failure(test_db):
    """验证工具入参损坏或未注册工具时记录 FAILED 状态审计日志"""
    trace_id = "test-trace-fail-001"

    # 1. 尝试执行不存在的工具
    res = execute_tool(
        name="non_existent_tool_xyz",
        args={"foo": "bar"},
        db=test_db,
        trace_id=trace_id,
    )
    assert res["status"] == "error"

    fail_log = test_db.query(AuditLog).filter(AuditLog.trace_id == trace_id).first()
    assert fail_log is not None
    assert fail_log.status == "FAILED"
    assert "未注册的工具" in fail_log.tool_result

    # 2. 尝试传入非法 JSON 字符串参数
    trace_id_json_err = "test-trace-json-err"
    res_bad_json = execute_tool(
        name="get_server_metrics",
        args="{malformed_json: ...}",
        db=test_db,
        trace_id=trace_id_json_err,
    )
    assert res_bad_json["status"] == "error"
    assert "JSON 解析失败" in res_bad_json["message"]

    log_bad_json = test_db.query(AuditLog).filter(AuditLog.trace_id == trace_id_json_err).first()
    assert log_bad_json is not None
    assert log_bad_json.status == "FAILED"


# ---------------------------------------------------------
# 6. 边界值与异常防御性测试
# ---------------------------------------------------------
def test_metric_warning_device(test_db):
    """验证处于 WARNING 预警状态设备的指标采集"""
    res = get_server_metrics(device_id="DEV-UPS-201", db=test_db)
    assert res["status"] == "success"
    assert res["health_status"] == "WARNING"
    assert res["alert"] is True
    assert res["alert_level"] == "WARNING"


def test_ticket_tools_edge_cases(test_db):
    """验证工单模块边界值：异常优先级容错、空结果过滤"""
    # 1. 传入非常规优先级 -> 自动容错为 MEDIUM
    res = create_ticket(
        title="边缘测试工单",
        description="测试非常规优先级容错",
        priority="SUPER_CRITICAL_UNKNOWN",
        db=test_db,
    )
    assert res["status"] == "success"
    assert res["ticket"]["priority"] == "MEDIUM"

    # 2. 条件不匹配查询 -> 返回空列表而不是报错
    res_empty = query_tickets(device_id="DEV-NON-EXISTENT-XYZ", db=test_db)
    assert res_empty["status"] == "success"
    assert res_empty["count"] == 0
    assert len(res_empty["tickets"]) == 0

    # 3. 更新不存在的工单
    res_not_found = update_ticket_status(ticket_no="TK-99999999-NOTFOUND", status="RESOLVED", db=test_db)
    assert res_not_found["status"] == "error"
    assert "未找到工单" in res_not_found["message"]


def test_asset_tools_edge_cases(test_db):
    """验证资产工具边界值：空参数、不存在设备借还、非法健康状态变更"""
    # 1. 空编号借出
    res_blank = borrow_asset(asset_no="", borrower="", db=test_db)
    assert res_blank["status"] == "error"
    assert "不能为空" in res_blank["message"]

    # 2. 借用不存在设备
    res_not_exist = borrow_asset(asset_no="DEV-GHOST-404", borrower="测试员", db=test_db)
    assert res_not_exist["status"] == "error"
    assert "未在台账中检索到" in res_not_exist["message"]

    # 3. 归还不存在设备
    res_ret_ghost = return_asset(asset_no="DEV-GHOST-404", db=test_db)
    assert res_ret_ghost["status"] == "error"
    assert "未在台账中检索到" in res_ret_ghost["message"]

    # 4. 非法健康状态
    res_bad_health = update_asset_health(asset_no="DEV-SRV-201", health_status="SUPER_BROKEN", db=test_db)
    assert res_bad_health["status"] == "error"
    assert "无效的健康状态" in res_bad_health["message"]


def test_execute_tool_filtering_hallucinated_params(test_db):
    """验证工具分发时自动过滤模型幻觉参数，避免 TypeError"""
    res = execute_tool(
        name="get_server_metrics",
        args={"device_id": "DEV-SRV-202", "hallucinated_fake_param": "unexpected_val"},
        db=test_db,
    )
    assert res["status"] == "success"
    assert res["device_id"] == "DEV-SRV-202"


def test_execute_tool_parameter_alias_mapping(test_db):
    """验证智能参数别名映射 (device_id <-> asset_no, ticket_id <-> ticket_no)"""
    # 1. 向借用工具传入 device_id，应自动映射为 asset_no
    res_borrow = execute_tool(
        name="borrow_asset",
        args={"device_id": "DEV-LAB-105", "borrower": "王老师"},
        db=test_db,
    )
    assert res_borrow["status"] == "success"
    assert res_borrow["asset"]["asset_no"] == "DEV-LAB-105"

    # 2. 向归还工具传入 device_id，应自动映射为 asset_no
    res_ret = execute_tool(
        name="return_asset",
        args={"device_id": "DEV-LAB-105"},
        db=test_db,
    )
    assert res_ret["status"] == "success"

    # 3. 向工单更新工具传入 ticket_id，应自动映射为 ticket_no
    seed_t = test_db.query(Ticket).first()
    res_tk = execute_tool(
        name="update_ticket_status",
        args={"ticket_id": seed_t.ticket_no, "status": "CLOSED"},
        db=test_db,
    )
    assert res_tk["status"] == "success"
    assert res_tk["ticket"]["status"] == "CLOSED"


def test_execute_tool_circular_reference_audit_logging(test_db):
    """验证传入带有循环引用的对象时，AuditLog 安全降级序列化而不崩溃"""
    trace_id = "test-circular-001"
    circular_dict = {"device_id": "DEV-SRV-202"}
    circular_dict["self"] = circular_dict

    res = execute_tool(
        name="get_server_metrics",
        args=circular_dict,
        db=test_db,
        trace_id=trace_id,
    )
    assert res["status"] == "success"

    log = test_db.query(AuditLog).filter(AuditLog.trace_id == trace_id).first()
    assert log is not None
    assert log.status == "SUCCESS"
    assert "DEV-SRV-202" in log.tool_args


def test_ticket_creation_concurrency_retry(test_db):
    """验证工单创建在编号碰撞或多重并发重试下的防冲突能力"""
    res1 = create_ticket(title="并发测试工单1", description="desc1", db=test_db)
    res2 = create_ticket(title="并发测试工单2", description="desc2", db=test_db)
    assert res1["status"] == "success"
    assert res2["status"] == "success"
    assert res1["ticket"]["ticket_no"] != res2["ticket"]["ticket_no"]



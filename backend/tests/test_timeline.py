"""FEAT-03: 工单流转与资产履历时序时间轴 (Timeline Drawer) 自动化验证测试套件

测试项覆盖：
1. 工单流转时间轴端点 (GET /api/tickets/{ticket_no_or_id}/timeline) 按 ID 和工单号检索
2. 工单提单创建、流转记录与 Agent 工具审计节点聚合与时序排序
3. 工单 PATCH 状态流转自动记录 TicketWorkflow
4. 资产全生命周期履历时间轴端点 (GET /api/assets/{asset_no}/timeline) 采购投产、借还时序与关联工单聚合
5. 资产履历按数字 ID 与编号查询
6. 边界与异常分支 (工单/资产 404，非法参数等)
7. ticket_tools.update_ticket_status 状态变更自动写表闭环
8. asset_tools.borrow_asset 与 return_asset 借还流转记录 (AssetBorrowLog) 自动创建与闭环更新
"""

import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import Base, get_db
from app.db.models import (
    Ticket,
    Asset,
    AssetDetail,
    AssetBorrowLog,
    TicketWorkflow,
    AuditLog,
)
from app.db.init_db import init_db
from app.tools import ticket_tools, asset_tools


@pytest.fixture(scope="module")
def timeline_test_env():
    """创建时间轴测试专用物理隔离测试数据库"""
    temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_file.close()
    test_db_url = f"sqlite:///{temp_file.name}"

    engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    init_db(seed=True, custom_engine=engine, custom_session_factory=TestingSessionLocal)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield {
        "engine": engine,
        "session_factory": TestingSessionLocal,
    }

    app.dependency_overrides.clear()
    engine.dispose()
    if os.path.exists(temp_file.name):
        try:
            os.remove(temp_file.name)
        except Exception:
            pass


@pytest.fixture(scope="module")
def client(timeline_test_env):
    """FastAPI TestClient 夹具"""
    return TestClient(app)


# ==================== 1. 工单时间轴测试 ====================

def test_ticket_timeline_by_id(client):
    """测试通过工单数字 ID 查询流转全景时间轴"""
    res = client.get("/api/tickets/1/timeline")
    assert res.status_code == 200
    data = res.json()
    assert "ticket" in data
    assert "timeline" in data
    assert "summary" in data

    assert data["ticket"]["id"] == 1
    assert data["ticket"]["ticket_no"] == "TK-20260901-001"
    assert data["summary"]["total_nodes"] >= 2  # 包含 CREATED 与 PROCESSING 流转节点

    # 验证提单起始节点 (CREATED)
    created_node = data["timeline"][0]
    assert created_node["node_type"] == "CREATED"
    assert "工单创建" in created_node["title"]
    assert created_node["previous_status"] is None
    assert created_node["next_status"] == "PENDING"
    assert created_node["duration_from_start"] == "+0分钟"


def test_ticket_timeline_by_ticket_no(client):
    """测试通过工单编号 (如 TK-20260901-001) 查询流转全景时间轴"""
    res = client.get("/api/tickets/TK-20260901-001/timeline")
    assert res.status_code == 200
    data = res.json()
    assert data["ticket"]["ticket_no"] == "TK-20260901-001"

    # 验证种子数据中的流转节点 (TK-20260901-001 存在 PENDING -> PROCESSING 流转)
    wf_nodes = [n for n in data["timeline"] if n["node_type"] == "PROCESSING"]
    assert len(wf_nodes) >= 1
    wf_node = wf_nodes[0]
    assert wf_node["operator"] == "王主管"
    assert wf_node["previous_status"] == "PENDING"
    assert wf_node["next_status"] == "PROCESSING"
    assert "超温" in wf_node["comment"]


def test_ticket_timeline_not_found(client):
    """测试查询不存在的工单返回 404"""
    res1 = client.get("/api/tickets/99999/timeline")
    assert res1.status_code == 404

    res2 = client.get("/api/tickets/TK-NON-EXISTENT-999/timeline")
    assert res2.status_code == 404


def test_ticket_update_auto_workflow_audit(client, timeline_test_env):
    """测试 PATCH /api/tickets/{id} 状态变迁时自动生成流转记录"""
    # 1. 创建一张新测试工单
    new_ticket = {
        "title": "时间轴流转测试工单",
        "description": "用于验证 PATCH 工单状态变迁时自动向 ticket_workflows 插入记录",
        "priority": "HIGH",
        "status": "PENDING",
        "device_id": "DEV-SRV-201",
        "creator": "自动化测试",
    }
    create_res = client.post("/api/tickets/", json=new_ticket)
    assert create_res.status_code == 201
    ticket_id = create_res.json()["id"]
    ticket_no = create_res.json()["ticket_no"]

    # 2. 推进状态为 PROCESSING，传入 operator 与 comment
    patch_res = client.patch(
        f"/api/tickets/{ticket_id}",
        json={
            "status": "PROCESSING",
            "operator": "李技术员",
            "comment": "李技术员已接单并在机房现场排查",
        },
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "PROCESSING"

    # 3. 再次推进为 RESOLVED，缺省 operator
    resolve_res = client.patch(
        f"/api/tickets/{ticket_id}",
        json={
            "status": "RESOLVED",
            "comment": "故障排查修复完成，恢复正常",
        },
    )
    assert resolve_res.status_code == 200
    assert resolve_res.json()["status"] == "RESOLVED"

    # 4. 请求时间轴，验证流转链条完整性
    timeline_res = client.get(f"/api/tickets/{ticket_no}/timeline")
    assert timeline_res.status_code == 200
    tl_data = timeline_res.json()
    assert tl_data["summary"]["total_nodes"] == 3  # CREATED + PROCESSING + RESOLVED

    nodes = tl_data["timeline"]
    assert nodes[0]["node_type"] == "CREATED"

    assert nodes[1]["node_type"] == "PROCESSING"
    assert nodes[1]["operator"] == "李技术员"
    assert "现场排查" in nodes[1]["comment"]

    assert nodes[2]["node_type"] == "RESOLVED"
    assert nodes[2]["operator"] == "系统管理员"  # 缺省降级为系统管理员
    assert "故障排查修复完成" in nodes[2]["comment"]


# ==================== 2. 资产履历时间轴测试 ====================

def test_asset_timeline_by_asset_no(client):
    """测试通过资产编号 (如 DEV-SRV-201) 查询全生命周期履历时序图谱"""
    res = client.get("/api/assets/DEV-SRV-201/timeline")
    assert res.status_code == 200
    data = res.json()

    assert "asset" in data
    assert "timeline" in data
    assert "summary" in data

    assert data["asset"]["asset_no"] == "DEV-SRV-201"
    assert data["summary"]["total_events"] >= 3

    # 1. 验证采购投产节点 (COMMISSIONING)
    comm_node = data["timeline"][0]
    assert comm_node["node_type"] == "COMMISSIONING"
    assert "投产" in comm_node["title"]
    assert "Dell" in comm_node["metadata"]["brand"]

    # 2. 验证借调流转节点 (BORROW) (SEED_BORROW_LOGS 中有 DEV-SRV-201 借调给李老师)
    borrow_nodes = [n for n in data["timeline"] if n["node_type"] == "BORROW"]
    assert len(borrow_nodes) >= 1
    assert borrow_nodes[0]["operator"] == "李老师"

    # 3. 验证关联工单事件节点 (INCIDENT / MAINTENANCE) (SEED_TICKETS 中有关联 DEV-SRV-201 的超温工单)
    ticket_nodes = [n for n in data["timeline"] if n["node_type"] in ("INCIDENT", "MAINTENANCE")]
    assert len(ticket_nodes) >= 1


def test_asset_timeline_by_id(client):
    """测试通过资产数字 ID 查询履历"""
    res = client.get("/api/assets/1/timeline")
    assert res.status_code == 200
    data = res.json()
    assert data["asset"]["id"] == 1


def test_asset_timeline_not_found(client):
    """测试查询不存在的设备返回 404"""
    res = client.get("/api/assets/NON-EXISTENT-DEVICE/timeline")
    assert res.status_code == 404


# ==================== 3. 工具层写表闭环测试 ====================

def test_ticket_tools_update_status_workflow(timeline_test_env):
    """测试 ticket_tools.update_ticket_status 自动写入流转表闭环"""
    session = timeline_test_env["session_factory"]()
    try:
        # 创建待测试工单
        t = Ticket(
            ticket_no="TK-TOOL-TEST-001",
            title="测试工具状态流转写表",
            description="验证 update_ticket_status 自动插入 TicketWorkflow",
            priority="LOW",
            status="PENDING",
            creator="测试员",
        )
        session.add(t)
        session.commit()

        # 调用工具更新工单状态
        result = ticket_tools.update_ticket_status(
            ticket_no="TK-TOOL-TEST-001",
            status="PROCESSING",
            description_append="Agent 自动排查散热风扇状态正常",
            db=session,
        )
        assert result["status"] == "success"

        # 检查是否成功插入 TicketWorkflow
        wf = (
            session.query(TicketWorkflow)
            .filter(TicketWorkflow.ticket_id == "TK-TOOL-TEST-001")
            .first()
        )
        assert wf is not None
        assert wf.previous_status == "PENDING"
        assert wf.next_status == "PROCESSING"
        assert wf.operator == "LabOps-Agent"
        assert "散热风扇" in wf.comment
    finally:
        session.close()


def test_asset_tools_borrow_and_return_log_lifecycle(timeline_test_env):
    """测试 asset_tools.borrow_asset 与 return_asset 借还记录自动闭环"""
    session = timeline_test_env["session_factory"]()
    try:
        # 新增一台空闲设备
        dev = Asset(
            asset_no="DEV-TOOL-TEST-901",
            name="时间轴闭环测试服务器",
            category="服务器",
            location="实训楼201-测试机柜",
            health_status="HEALTHY",
            borrow_status="AVAILABLE",
        )
        session.add(dev)
        session.commit()

        # 1. 办理借调
        borrow_res = asset_tools.borrow_asset(
            asset_no="DEV-TOOL-TEST-901",
            borrower="王科研",
            db=session,
        )
        assert borrow_res["status"] == "success"
        assert borrow_res["asset"]["borrow_status"] == "IN_USE"

        # 检查是否生成了 AssetBorrowLog
        blog = (
            session.query(AssetBorrowLog)
            .filter(
                AssetBorrowLog.asset_id == "DEV-TOOL-TEST-901",
                AssetBorrowLog.return_status == "BORROWING",
            )
            .first()
        )
        assert blog is not None
        assert blog.borrower_name == "王科研"
        assert blog.log_no.startswith("BORROW-")
        assert blog.actual_return_time is None

        # 2. 办理归还
        return_res = asset_tools.return_asset(
            asset_no="DEV-TOOL-TEST-901",
            db=session,
        )
        assert return_res["status"] == "success"
        assert return_res["asset"]["borrow_status"] == "AVAILABLE"

        # 检查 AssetBorrowLog 是否已闭环为 RETURNED
        session.refresh(blog)
        assert blog.return_status == "RETURNED"
        assert blog.actual_return_time is not None
    finally:
        session.close()


# ==================== 4. 增强与边界测试 (审计节点、查询参数、空白容错、状态兜底) ====================

def test_ticket_timeline_with_audit_logs_and_ordering(client, timeline_test_env):
    """测试当存在关联 AuditLog 工具调用时，时间轴包含 AUTOMATION 节点且 CREATED 恒处于首位"""
    session = timeline_test_env["session_factory"]()
    try:
        # 1. 创建带有明确编号的工单
        t = Ticket(
            ticket_no="TK-AUDIT-TEST-888",
            title="审计时序排序测试工单",
            description="用于测试 Agent 工具调用记录与提单时序优先级",
            priority="CRITICAL",
            status="PENDING",
            creator="系统巡检引擎",
        )
        session.add(t)
        session.commit()

        # 2. 插入关联的 AuditLog 审计日志 (模拟 Agent 自动化工具执行)
        al = AuditLog(
            trace_id="TRACE-AUDIT-TEST-001",
            tool_name="update_ticket_status",
            tool_args='{"ticket_no": "TK-AUDIT-TEST-888", "status": "PROCESSING"}',
            tool_result='{"status": "success", "ticket_no": "TK-AUDIT-TEST-888"}',
            status="SUCCESS",
        )
        session.add(al)
        session.commit()

        # 3. 查询时间轴
        res = client.get("/api/tickets/TK-AUDIT-TEST-888/timeline")
        assert res.status_code == 200
        data = res.json()

        # 验证 CREATED 节点永远是第一位
        timeline = data["timeline"]
        assert len(timeline) >= 2
        assert timeline[0]["node_type"] == "CREATED"
        assert timeline[0]["duration_from_start"] == "+0分钟"

        # 验证 AUTOMATION 节点存在且属性正确
        audit_nodes = [n for n in timeline if n["node_type"] == "AUTOMATION"]
        assert len(audit_nodes) == 1
        an = audit_nodes[0]
        assert an["operator"] == "LabOps-Agent"
        assert "update_ticket_status" in an["title"]
        assert an["metadata"]["tool_name"] == "update_ticket_status"
    finally:
        session.close()


def test_ticket_update_via_query_params(client, timeline_test_env):
    """测试 PATCH /api/tickets/{id} 支持通过 URL 查询参数指定 operator 与 comment"""
    # 1. 创建测试工单
    create_res = client.post(
        "/api/tickets/",
        json={
            "title": "查询参数流转工单",
            "description": "验证 Query 参数透传",
            "priority": "LOW",
            "status": "PENDING",
            "creator": "自动化测试",
        },
    )
    assert create_res.status_code == 201
    tid = create_res.json()["id"]
    tno = create_res.json()["ticket_no"]

    # 2. 通过 URL 查询参数传递 operator 与 comment
    patch_res = client.patch(
        f"/api/tickets/{tid}?operator=%E5%BC%A0%E5%B7%A5%E7%A8%8B&comment=%E9%80%9A%E8%BF%87URL%E5%8F%82%E6%95%B0%E6%B5%81%E8%BD%AC",
        json={"status": "PROCESSING"},
    )
    assert patch_res.status_code == 200

    # 3. 校验时间轴中的流转记录
    tl_res = client.get(f"/api/tickets/{tno}/timeline")
    assert tl_res.status_code == 200
    nodes = tl_res.json()["timeline"]
    wf_node = [n for n in nodes if n["node_type"] == "PROCESSING"][0]
    assert wf_node["operator"] == "张工程"
    assert "通过URL参数流转" in wf_node["comment"]


def test_ticket_timeline_whitespace_tolerance(client):
    """测试工单时间轴端点对带有首尾空格的 ID 与编号具备鲁棒容错性"""
    res1 = client.get("/api/tickets/%201%20/timeline")
    assert res1.status_code == 200
    assert res1.json()["ticket"]["id"] == 1

    res2 = client.get("/api/tickets/%20TK-20260901-001%20/timeline")
    assert res2.status_code == 200
    assert res2.json()["ticket"]["ticket_no"] == "TK-20260901-001"


def test_ticket_tools_custom_operator(timeline_test_env):
    """测试 ticket_tools.update_ticket_status 支持自定义 operator 处置人"""
    session = timeline_test_env["session_factory"]()
    try:
        t = Ticket(
            ticket_no="TK-CUSTOM-OP-001",
            title="自定义操作人测试工单",
            description="验证 operator 参数支持",
            priority="LOW",
            status="PENDING",
            creator="测试员",
        )
        session.add(t)
        session.commit()

        result = ticket_tools.update_ticket_status(
            ticket_no="TK-CUSTOM-OP-001",
            status="RESOLVED",
            description_append="赵技术员现场加固散热模块完成",
            operator="现场技术员赵工",
            db=session,
        )
        assert result["status"] == "success"

        wf = (
            session.query(TicketWorkflow)
            .filter(TicketWorkflow.ticket_id == "TK-CUSTOM-OP-001")
            .first()
        )
        assert wf is not None
        assert wf.operator == "现场技术员赵工"
        assert wf.next_status == "RESOLVED"
    finally:
        session.close()


def test_asset_timeline_with_returned_status_null_actual_time(client, timeline_test_env):
    """测试当借还记录为 RETURNED 但 actual_return_time 为空时的鲁棒容错与 COMMISSIONING 始终置顶"""
    session = timeline_test_env["session_factory"]()
    try:
        # 新增一台测试设备
        dev = Asset(
            asset_no="DEV-RETURN-TEST-999",
            name="验收入库边界测试设备",
            category="服务器",
            location="实训楼101-机架A",
            health_status="HEALTHY",
            borrow_status="AVAILABLE",
        )
        session.add(dev)
        session.commit()

        # 构造一条 return_status='RETURNED' 但 actual_return_time=None 的借调日志
        from datetime import datetime, timedelta
        now = datetime.now()
        blog = AssetBorrowLog(
            log_no="BORROW-TEST-NULLTIME-001",
            asset_id="DEV-RETURN-TEST-999",
            borrower_username="test_user",
            borrower_name="测试教师",
            purpose="教学研讨",
            borrow_time=now - timedelta(days=2),
            expected_return_time=now - timedelta(days=1),
            actual_return_time=None,  # 故意为 None
            return_status="RETURNED",
            approver="测试核验员",
        )
        session.add(blog)
        session.commit()

        # 请求资产履历时间轴
        res = client.get("/api/assets/DEV-RETURN-TEST-999/timeline")
        assert res.status_code == 200
        data = res.json()

        timeline = data["timeline"]
        # 1. 验证 COMMISSIONING 严格位于首位
        assert timeline[0]["node_type"] == "COMMISSIONING"
        assert timeline[0]["duration_from_start"] == "投产首日"

        # 2. 验证尽管 actual_return_time 为空，RETURN 节点依然生成并闭环
        return_nodes = [n for n in timeline if n["node_type"] == "RETURN"]
        assert len(return_nodes) == 1
        assert "验收入库归还" in return_nodes[0]["title"]
    finally:
        session.close()


def test_format_asset_duration_logic():
    """测试资产全生命周期时段格式化函数的边界覆盖"""
    from app.api.assets import format_asset_duration

    assert format_asset_duration(0) == "投产首日"
    assert format_asset_duration(-10) == "投产首日"
    assert format_asset_duration(3600) == "投产首日 (+1小时)"
    assert format_asset_duration(86400 * 1 + 10) == "投产第 2 天"
    assert format_asset_duration(86400 * 29) == "投产第 30 天"
    assert format_asset_duration(86400 * 30) == "投产 1 个月整"
    assert format_asset_duration(86400 * 45) == "投产 1 个月 15 天"
    assert format_asset_duration(86400 * 365) == "投产 1 年整"


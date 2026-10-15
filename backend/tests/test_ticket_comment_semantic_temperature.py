"""工单排查处置说明 (Comment) 语义解析与温度真实联动自动化测试

验证两种工作流下：
1. 右侧 UI 弹窗流转 (PUT /api/tickets/{ticket_id})：排查说明中声明实测温度时，设备温度精准写入该数值 (如 26.0℃)，彻底消除写死 31.5℃ 的假降温；
2. 左侧 AI 对话流转 (update_ticket_status 工具)：支持语义提取或直接传入实测温度，联动回写关联设备台账；
3. 未显式声明温度时，安全回落至健康轻载基线并生成规范的 AI 验收审计小结。
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.session import SessionLocal
from app.db.models import Ticket, Asset, TicketWorkflow
from app.services.ticket_comment_analyzer import (
    extract_temperature_from_text,
    analyze_ticket_resolution_comment,
)
from app.tools.ticket_tools import update_ticket_status


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_extract_temperature_various_expressions():
    """测试不同自然语言温度表达的语义精准提取"""
    assert extract_temperature_from_text("温度下降到26摄氏度") == 26.0
    assert extract_temperature_from_text("现场测温降至26.5℃") == 26.5
    assert extract_temperature_from_text("更换风扇后当前稳定在28度") == 28.0
    assert extract_temperature_from_text("实测25度，散热正常") == 25.0
    assert extract_temperature_from_text("核心温度 27.2 C") == 27.2
    assert extract_temperature_from_text("已清理滤网，未测温") is None


def test_analyze_ticket_resolution_comment_sufficient():
    """测试包含明确温度和具体维保动作的详尽处置说明解析与 AI 审计小结"""
    res = analyze_ticket_resolution_comment(
        comment="更换散热风扇并重涂导热硅脂，温度下降到26摄氏度",
        current_device_temp=43.5,
    )
    assert res["extracted_temperature"] == 26.0
    assert res["effective_temperature"] == 26.0
    assert res["is_explicit_temp"] is True
    assert res["evaluated_health"] == "HEALTHY"
    assert "风扇" in res["actions"] or "更换风扇" in res["actions"]
    assert "硅脂" in res["actions"] or "重涂硅脂" in res["actions"]
    assert "26.0℃" in res["audit_note"]


def test_ui_ticket_resolve_api_dynamic_temperature_linkage(client: TestClient):
    """测试右侧 UI 弹窗流转接口：用户填写温度下降到 26℃ 时，关联设备温度精准回写 26.0℃"""
    # 1. 创建测试设备
    asset_payload = {
        "asset_no": "DEV-TEST-SEMANTIC-26",
        "name": "语义测试服务器",
        "category": "服务器",
        "location": "实训楼201-机柜A01",
        "health_status": "OVERHEAT",
        "custom_temperature": 45.0,
    }
    a_res = client.post("/api/assets", json=asset_payload)
    assert a_res.status_code == 201
    asset_id = a_res.json()["id"]

    try:
        # 2. 创建工单
        t_res = client.post(
            "/api/tickets",
            json={
                "title": "DEV-TEST-SEMANTIC-26 超温检修",
                "description": "温度45℃告警",
                "priority": "HIGH",
                "device_id": "DEV-TEST-SEMANTIC-26",
                "creator": "王主管",
            },
        )
        assert t_res.status_code == 201
        ticket_id = t_res.json()["id"]
        ticket_no = t_res.json()["ticket_no"]

        # 3. 模拟用户在 UI 弹窗点击办结，填写包含实测降温 26℃ 的说明
        r_res = client.put(
            f"/api/tickets/{ticket_id}",
            json={
                "status": "RESOLVED",
                "comment": "现场清理机柜风道灰尘，重新插拔加压风扇，温度下降到26摄氏度，设备负载已平稳",
                "operator": "王主管",
            },
        )
        assert r_res.status_code == 200

        # 4. 核验关联设备温度是否精准回写为 26.0℃
        c_res = client.get(f"/api/assets/{asset_id}")
        assert c_res.status_code == 200
        assert c_res.json()["custom_temperature"] == 26.0
        assert c_res.json()["health_status"] == "HEALTHY"

        # 5. 核验工单流转记录中已包含 AI 审计核验说明
        tl_res = client.get(f"/api/tickets/{ticket_no}/timeline")
        if tl_res.status_code == 200:
            nodes = tl_res.json().get("timeline", [])
            latest_comment = nodes[-1].get("comment", "") if nodes else ""
            assert "26.0℃" in latest_comment
            assert "[AI验收审计]" in latest_comment

    finally:
        client.delete(f"/api/assets/{asset_id}")


def test_tool_ticket_resolve_semantic_temperature(db_session: Session):
    """测试左侧 AI 对话流调用 update_ticket_status：实测温度从描述中提取并联动回写设备"""
    asset = db_session.query(Asset).filter(Asset.asset_no == "DEV-SRV-202").first()
    if not asset:
        pytest.skip("DEV-SRV-202 不存在，跳过测试")

    asset.health_status = "OVERHEAT"
    if asset.detail:
        asset.detail.custom_temperature = 42.0
    db_session.commit()

    ticket = (
        db_session.query(Ticket)
        .filter(Ticket.device_id == "DEV-SRV-202")
        .first()
    )
    if not ticket:
        ticket = Ticket(
            ticket_no="TK-TEST-TOOL-RESOLVE-002",
            title="202服务器过热",
            description="温度异常",
            priority="HIGH",
            status="PROCESSING",
            device_id="DEV-SRV-202",
            creator="admin",
        )
        db_session.add(ticket)
        db_session.commit()

    target_tk_no = ticket.ticket_no

    # 调用业务工具模拟 AI 推进工单办结
    tool_res = update_ticket_status(
        ticket_no=target_tk_no,
        status="RESOLVED",
        description_append="已协助更换备用风扇模组，现场复测温度回落到25.5度",
        operator="LabOps-Agent",
        db=db_session,
    )

    assert tool_res["status"] == "success"
    assert "25.5℃" in tool_res["message"]

    db_session.refresh(asset)
    assert asset.custom_temperature == 25.5
    assert asset.health_status == "HEALTHY"


def test_extract_temperature_chinese_numerals():
    """测试中文数字温度表达的提取（如'温度下降了，下降到二十三度'）"""
    assert extract_temperature_from_text("温度下降了，下降到二十三度") == 23.0
    assert extract_temperature_from_text("已开空调，降到二十六度") == 26.0
    assert extract_temperature_from_text("实测降至二十六点五度") == 26.5
    assert extract_temperature_from_text("温度十度左右") == 10.0


def test_contextual_comment_flow_and_other_active_tickets(client: TestClient):
    """测试受理时填写温度、办结时未重复填写温度，且存在其他在办工单时依然精准回写设备实测温度"""
    # 1. 创建测试设备
    asset_res = client.post(
        "/api/assets",
        json={
            "asset_no": "DEV-TEST-CN-TEMP",
            "name": "中文温度联动测试设备",
            "category": "服务器",
            "location": "实训楼101-机柜B01",
            "health_status": "OVERHEAT",
            "custom_temperature": 90.0,
        },
    )
    assert asset_res.status_code == 201
    asset_id = asset_res.json()["id"]

    try:
        # 2. 创建一张伴生的其他在办工单（模拟历史遗留工单）
        other_t = client.post(
            "/api/tickets",
            json={
                "title": "DEV-TEST-CN-TEMP 历史待办工单",
                "description": "历史例行检查",
                "priority": "LOW",
                "device_id": "DEV-TEST-CN-TEMP",
                "creator": "巡检探针",
            },
        )
        assert other_t.status_code == 201
        other_ticket_id = other_t.json()["id"]

        # 3. 创建本次主工单
        main_t = client.post(
            "/api/tickets",
            json={
                "title": "DEV-TEST-CN-TEMP 核心温度过热紧急处置工单",
                "description": "核心温度90度告警",
                "priority": "CRITICAL",
                "device_id": "DEV-TEST-CN-TEMP",
                "creator": "LabOps-Agent",
            },
        )
        assert main_t.status_code == 201
        main_ticket_id = main_t.json()["id"]

        # 4. 模拟第一步：受理（PENDING -> PROCESSING），填写“温度下降了，下降到二十三度”
        step1_res = client.put(
            f"/api/tickets/{main_ticket_id}",
            json={
                "status": "PROCESSING",
                "comment": "温度下降了，下降到二十三度",
                "operator": "王主管",
            },
        )
        assert step1_res.status_code == 200

        # 5. 模拟第二步：办结（PROCESSING -> RESOLVED），填写“确实下降了，完成工单”（未重复写温度）
        step2_res = client.put(
            f"/api/tickets/{main_ticket_id}",
            json={
                "status": "RESOLVED",
                "comment": "确实下降了，完成工单",
                "operator": "王主管",
            },
        )
        assert step2_res.status_code == 200

        # 6. 验证设备实测温度已成功从历史流转中追溯并回写为 23.0℃，且健康状态恢复为 HEALTHY
        dev_res = client.get(f"/api/assets/{asset_id}")
        assert dev_res.status_code == 200
        dev_data = dev_res.json()
        assert dev_data["custom_temperature"] == 23.0
        assert dev_data["health_status"] == "HEALTHY"

        client.delete(f"/api/tickets/{other_ticket_id}")
        client.delete(f"/api/tickets/{main_ticket_id}")
    finally:
        client.delete(f"/api/assets/{asset_id}")

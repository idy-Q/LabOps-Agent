"""站内待办与超期督促通知服务自动化测试套件

测试项覆盖：
1. GET /api/notifications 查询李老师初始预置超期未读待办与未读数
2. POST /api/notifications/{id}/read 成功将待办标记为已读并更新未读数
3. POST /api/notifications/{id}/read 针对不存在的通知返回 404
4. POST /api/notifications/urge 管理员主动发起催办，成功解析借调教师并下发待办
5. POST /api/notifications/urge 支持附言留言与异常设备编号 404 容错
6. Agent 工具 send_overdue_urge_notification 单元测试
7. MockDecisionBrain 意图识别：精准识别“催还李老师”、“催促李老师”、“发催还通知”并调度闭环
"""

import json
import os
import tempfile
from datetime import datetime, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import Base, get_db
from app.db.models import UserNotification, Asset, AssetBorrowLog, User
from app.db.init_db import init_db
from app.tools.asset_tools import send_overdue_urge_notification
from app.agent.react_engine import MockDecisionBrain


@pytest.fixture(scope="module")
def notif_test_env():
    """创建物理隔离的测试数据库环境并填充标准种子数据"""
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
def client(notif_test_env):
    return TestClient(app)


# ==================== 1. REST API 端点测试 ====================

def test_get_notifications_teacher_li(client):
    """测试获取李老师的初始站内待办通知列表"""
    resp = client.get("/api/notifications?username=teacher_li")
    assert resp.status_code == 200
    data = resp.json()
    assert "unread_count" in data
    assert "items" in data
    assert data["unread_count"] >= 1

    items = data["items"]
    assert len(items) >= 1
    first = items[0]
    assert first["username"] == "teacher_li"
    assert "DEV-SRV-201" in first["title"]
    assert "超期" in first["title"]
    assert first["is_read"] is False
    assert first["notice_type"] == "OVERDUE_URGE"


def test_get_notifications_all_or_empty(client):
    """测试获取无待办用户与全部用户的通知列表"""
    resp_empty = client.get("/api/notifications?username=non_existent_user_999")
    assert resp_empty.status_code == 200
    data_empty = resp_empty.json()
    assert data_empty["unread_count"] == 0
    assert len(data_empty["items"]) == 0

    resp_all = client.get("/api/notifications")
    assert resp_all.status_code == 200
    data_all = resp_all.json()
    assert data_all["unread_count"] >= 1


def test_mark_notification_read(client, notif_test_env):
    """测试标记通知为已读功能"""
    # 1. 查找一条未读记录
    resp_list = client.get("/api/notifications?username=teacher_li")
    items = resp_list.json()["items"]
    target_id = items[0]["id"]

    # 2. 标记已读
    resp_read = client.post(f"/api/notifications/{target_id}/read")
    assert resp_read.status_code == 200
    read_data = resp_read.json()
    assert read_data["status"] == "success"
    assert read_data["is_read"] is True

    # 3. 再次查询，该记录已为已读
    resp_after = client.get("/api/notifications?username=teacher_li")
    after_items = resp_after.json()["items"]
    matched = next((it for it in after_items if it["id"] == target_id), None)
    assert matched is not None
    assert matched["is_read"] is True


def test_mark_notification_read_404(client):
    """测试标记不存在的通知为已读返回 404"""
    resp = client.post("/api/notifications/999999/read")
    assert resp.status_code == 404
    assert "不存在" in resp.json()["detail"]


def test_send_urge_notification_api(client):
    """测试管理员发起设备催还，生成借调人待办"""
    payload = {
        "asset_no": "DEV-SRV-201",
        "remark": "下周实验教学急需使用该算力卡，请务必于周三前归还！",
    }
    resp = client.post("/api/notifications/urge", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "李老师" in data["message"]
    notif = data["notification"]
    assert notif["username"] == "teacher_li"
    assert notif["asset_no"] == "DEV-SRV-201"
    assert notif["is_read"] is False
    assert "下周实验教学急需使用" in notif["content"]


def test_send_urge_notification_invalid_asset(client):
    """测试对不存在的设备发起催还返回 404"""
    payload = {
        "asset_no": "DEV-SRV-INVALID-999",
    }
    resp = client.post("/api/notifications/urge", json=payload)
    assert resp.status_code == 404
    assert "不存在" in resp.json()["detail"]


# ==================== 2. Agent 运维工具层测试 ====================

def test_send_overdue_urge_notification_tool(notif_test_env):
    """测试 Agent 工具 send_overdue_urge_notification 执行"""
    db = notif_test_env["session_factory"]()
    try:
        res = send_overdue_urge_notification(
            asset_no="DEV-SRV-201",
            urge_message="Agent 自动研判超期触发站内催办",
            db=db,
        )
        assert res["status"] == "success"
        assert "李老师" in res["message"]
        notif = res["notification"]
        assert notif["username"] == "teacher_li"
        assert notif["asset_no"] == "DEV-SRV-201"
        assert notif["is_read"] is False

        # 测试异常参数
        err_res = send_overdue_urge_notification(asset_no="", db=db)
        assert err_res["status"] == "error"

        err_res2 = send_overdue_urge_notification(asset_no="DEV-NO-SUCH", db=db)
        assert err_res2["status"] == "error"
    finally:
        db.close()


# ==================== 3. MockDecisionBrain 意图识别测试 ====================

def test_mock_decision_brain_urge_intent():
    """测试 MockDecisionBrain 对催还意图的精准捕获与多工具调度"""
    prompts = [
        "催还李老师",
        "催促李老师还设备 DEV-SRV-201",
        "给李老师发催还通知",
        "向李老师发送催办通知",
        "催办李老师还设备",
    ]

    for p in prompts:
        decision = MockDecisionBrain.decide([{"role": "user", "content": p}], "ADMIN", "王主管")
        assert "tool_calls" in decision, f"Prompt '{p}' 未触发工具调用"
        calls = decision["tool_calls"]
        tool_names = [c["function"]["name"] for c in calls]
        # 必须包含起草催告公函与外发待办通知两项工具
        assert "draft_overdue_notice" in tool_names, f"Prompt '{p}' 缺少 draft_overdue_notice"
        assert "send_overdue_urge_notification" in tool_names, f"Prompt '{p}' 缺少 send_overdue_urge_notification"


def test_mock_decision_brain_urge_completion():
    """测试工具执行完成后，MockDecisionBrain 产出包含通知下发与公函的闭环回复"""
    messages = [
        {"role": "user", "content": "向李老师发送催办通知 DEV-SRV-201"},
        {
            "role": "tool",
            "name": "draft_overdue_notice",
            "content": json.dumps({
                "status": "success",
                "markdown_content": "### 实验室仪器设备超期使用归还催告单\n\n主送：李老师",
            }),
        },
        {
            "role": "tool",
            "name": "send_overdue_urge_notification",
            "content": json.dumps({
                "status": "success",
                "message": "已成功向借调责任人李老师 (teacher_li) 下发站内超期催还待办通知！",
            }),
        },
    ]

    decision = MockDecisionBrain.decide(messages, "ADMIN", "王主管")
    assert "tool_calls" not in decision or len(decision.get("tool_calls", [])) == 0
    content = decision.get("content", "")
    assert "站内催还待办已下发" in content
    assert "李老师" in content
    assert "实验室仪器设备超期使用归还催告单" in content


def test_urge_notification_idempotency(client):
    """测试连续多次对同一未归还设备发起催办时，保持未读幂等性，不无限堆叠重复记录"""
    # 连续发起两次催办
    resp1 = client.post("/api/notifications/urge", json={"asset_no": "DEV-SRV-201", "remark": "第一次催办"})
    assert resp1.status_code == 200
    id1 = resp1.json()["notification"]["id"]

    resp2 = client.post("/api/notifications/urge", json={"asset_no": "DEV-SRV-201", "remark": "第二次催办加急"})
    assert resp2.status_code == 200
    id2 = resp2.json()["notification"]["id"]

    # 应该复用同一条未读记录并更新内容
    assert id1 == id2
    assert "第二次催办加急" in resp2.json()["notification"]["content"]

    # 验证未读数没有翻倍增加
    resp_list = client.get("/api/notifications?username=teacher_li")
    unreads = [it for it in resp_list.json()["items"] if not it["is_read"] and it["asset_no"] == "DEV-SRV-201"]
    assert len(unreads) == 1

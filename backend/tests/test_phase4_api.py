"""阶段 4 前后端联动与流式 SSE 接口测试套件"""

import json
import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import Base, get_db
from app.db.models import Ticket, Asset, ChatHistory
from app.db.init_db import init_db


@pytest.fixture(scope="module")
def phase4_test_env():
    """创建阶段 4 物理隔离测试数据库"""
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
def client(phase4_test_env):
    """阶段 4 测试客户端"""
    with TestClient(app) as c:
        yield c


def test_metrics_summary_endpoint(client):
    """测试机房运行监控综合大盘接口 /api/metrics/summary"""
    resp = client.get("/api/metrics/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"

    summary = data["data"]
    assert "overview" in summary
    assert "assets" in summary
    assert "tickets" in summary
    assert "nodes" in summary

    overview = summary["overview"]
    assert overview["avg_temperature"] > 0
    assert overview["avg_cpu_load"] >= 0
    assert overview["total_power_watts"] > 0
    assert 0 <= overview["system_health_rate"] <= 100

    assets = summary["assets"]
    assert assets["total"] >= 5
    assert assets["healthy"] >= 1

    tickets = summary["tickets"]
    assert tickets["total"] >= 1

    nodes = summary["nodes"]
    assert len(nodes) > 0
    assert any("DEV-SRV-201" == n["device_id"] for n in nodes)


def test_chat_stream_empty_prompt(client):
    """测试空输入内容 422 拦截"""
    resp = client.post("/api/chat/stream", json={"prompt": "   "})
    assert resp.status_code == 422


def test_chat_stream_sse_greeting(client):
    """测试常规问答 SSE 流式输出格式与事件结构"""
    resp = client.post(
        "/api/chat/stream",
        json={"prompt": "你好，请介绍一下你自己", "session_id": "sess-test-greet-401"},
    )
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers["content-type"]

    lines = resp.text.strip().split("\n\n")
    events = []
    for line in lines:
        if line.startswith("data: "):
            payload = json.loads(line[6:])
            events.append(payload)

    event_types = [e["type"] for e in events]
    assert "think" in event_types
    assert "content" in event_types
    assert "done" in event_types

    done_event = next(e for e in events if e["type"] == "done")
    assert done_event["session_id"] == "sess-test-greet-401"


def test_chat_stream_sse_tool_and_mutation(client):
    """测试工具调用触发工单突变事件 (ticket_mutation) 的流式分发"""
    resp = client.post(
        "/api/chat/stream",
        json={
            "prompt": "查询DEV-SRV-201监控指标，若异常请自动提单",
            "session_id": "sess-test-triage-402",
        },
    )
    assert resp.status_code == 200
    lines = resp.text.strip().split("\n\n")
    events = []
    for line in lines:
        if line.startswith("data: "):
            payload = json.loads(line[6:])
            events.append(payload)

    event_types = [e["type"] for e in events]
    assert "think" in event_types
    assert "tool_start" in event_types
    assert "tool_end" in event_types
    assert "ticket_mutation" in event_types
    assert "content" in event_types
    assert "done" in event_types

    # 验证工单突变事件数据包
    mutation = next(e for e in events if e["type"] == "ticket_mutation")
    assert mutation["action"] == "create"
    assert mutation["ticket_no"].startswith("TK-")


def test_chat_stream_sse_citation(client):
    """测试规章检索触发规章溯源事件 (citation) 的流式分发"""
    resp = client.post(
        "/api/chat/stream",
        json={
            "prompt": "机房用电安全和机架功耗限制是怎样的？",
            "session_id": "sess-test-rag-403",
        },
    )
    assert resp.status_code == 200
    lines = resp.text.strip().split("\n\n")
    events = []
    for line in lines:
        if line.startswith("data: "):
            payload = json.loads(line[6:])
            events.append(payload)

    event_types = [e["type"] for e in events]
    assert "citation" in event_types
    citation = next(e for e in events if e["type"] == "citation")
    assert "source" in citation
    assert len(citation["source"]) > 0


def test_chat_history_and_sessions(client):
    """测试会话历史列表及会话概要接口"""
    # 1. 查询指定 session 历史
    resp = client.get("/api/chat/history?session_id=sess-test-greet-401")
    assert resp.status_code == 200
    histories = resp.json()
    assert len(histories) >= 2
    roles = [h["role"] for h in histories]
    assert "user" in roles
    assert "assistant" in roles

    # 2. 查询最近活跃会话
    resp_sess = client.get("/api/chat/sessions")
    assert resp_sess.status_code == 200
    sess_data = resp_sess.json()
    assert sess_data["status"] == "success"
    session_ids = [s["session_id"] for s in sess_data["data"]]
    assert "sess-test-greet-401" in session_ids


def test_chat_stream_sse_asset_mutation(client):
    """测试资产借还触发资产突变事件 (asset_mutation) 的流式分发"""
    resp = client.post(
        "/api/chat/stream",
        json={
            "prompt": "帮李老师办理设备 DEV-SRV-202 的借用登记",
            "session_id": "sess-test-borrow-404",
        },
    )
    assert resp.status_code == 200
    lines = resp.text.strip().split("\n\n")
    events = []
    for line in lines:
        if line.startswith("data: "):
            payload = json.loads(line[6:])
            events.append(payload)

    event_types = [e["type"] for e in events]
    assert "asset_mutation" in event_types
    mutation = next(e for e in events if e["type"] == "asset_mutation")
    assert mutation["action"] == "borrow_asset"
    assert mutation["asset"]["asset_no"] == "DEV-SRV-202"
    assert mutation["asset"]["borrow_status"] == "IN_USE"


def test_chat_multi_turn_context_continuity(client):
    """测试跨轮次多轮会话记忆连续性与代词上下文解析闭环"""
    session_id = "sess-test-multiturn-405"

    # 第一轮：自动创建工单
    resp1 = client.post(
        "/api/chat/stream",
        json={"prompt": "查询DEV-SRV-201监控指标，若异常请自动提单", "session_id": session_id},
    )
    assert resp1.status_code == 200
    events1 = [
        json.loads(line[6:])
        for line in resp1.text.strip().split("\n\n")
        if line.startswith("data: ")
    ]
    ticket_mut1 = next((e for e in events1 if e["type"] == "ticket_mutation"), None)
    assert ticket_mut1 is not None
    created_tk = ticket_mut1["ticket_no"]
    assert created_tk.startswith("TK-")

    # 第二轮：通过代词/上下文指令“把刚才的工单办结关闭”流转同一张工单
    resp2 = client.post(
        "/api/chat/stream",
        json={"prompt": "把刚才的工单办结关闭", "session_id": session_id},
    )
    assert resp2.status_code == 200
    events2 = [
        json.loads(line[6:])
        for line in resp2.text.strip().split("\n\n")
        if line.startswith("data: ")
    ]
    ticket_mut2 = next((e for e in events2 if e["type"] == "ticket_mutation"), None)
    assert ticket_mut2 is not None
    assert ticket_mut2["action"] == "update"
    assert ticket_mut2["ticket_no"] == created_tk
    assert ticket_mut2["ticket"]["status"] == "CLOSED"


def test_chat_history_edge_cases_and_boundaries(client):
    """测试会话历史边界情况 (空会话ID、非存在会话、limit 参数上限校验)"""
    # 1. 查询不存在的 session_id 返回空列表而非报错
    resp_empty = client.get("/api/chat/history?session_id=nonexistent_sess_999")
    assert resp_empty.status_code == 200
    assert resp_empty.json() == []

    # 2. limit 边界校验: limit=0 触发 422 校验失败
    resp_bad_limit = client.get("/api/chat/history?limit=0")
    assert resp_bad_limit.status_code == 422

    # 3. limit 超出 200 触发 422
    resp_over_limit = client.get("/api/chat/history?limit=201")
    assert resp_over_limit.status_code == 422


def test_tool_start_end_pairing(client):
    """测试 tool_start 与 tool_end 事件中携带一致的 tool_call_id"""
    resp = client.post(
        "/api/chat/stream",
        json={"prompt": "查询当前所有待办工单", "session_id": "sess-test-tool-pair-406"},
    )
    assert resp.status_code == 200
    events = [
        json.loads(line[6:])
        for line in resp.text.strip().split("\n\n")
        if line.startswith("data: ")
    ]
    starts = [e for e in events if e["type"] == "tool_start"]
    ends = [e for e in events if e["type"] == "tool_end"]
    assert len(starts) >= 1
    assert len(starts) == len(ends)

    for s in starts:
        assert "tool_call_id" in s
        matching_end = next((e for e in ends if e.get("tool_call_id") == s["tool_call_id"]), None)
        assert matching_end is not None
        assert matching_end["name"] == s["name"]


def test_chat_stream_student_rbac_interception(client):
    """测试通过 SSE API 发送学生身份的越权借调指令时被直接拦截"""
    resp = client.post(
        "/api/chat/stream",
        json={
            "prompt": "借用 DEV-SRV-201",
            "session_id": "sess-sse-student-rbac",
            "user_role": "STUDENT",
            "user_name": "张同学",
            "user_department": "计算机科学与技术2201班",
        },
    )
    assert resp.status_code == 200
    events = [
        json.loads(line[6:])
        for line in resp.text.strip().split("\n\n")
        if line.startswith("data: ")
    ]
    # 不应触发任何工具调用或资产突变
    assert not any(e["type"] == "tool_start" and e.get("name") == "borrow_asset" for e in events)
    assert not any(e["type"] == "asset_mutation" for e in events)

    # 应返回权限拦截说明
    content_event = next((e for e in events if e["type"] == "content"), None)
    assert content_event is not None
    assert "权限拦截警报" in content_event["text"]
    assert "张同学" in content_event["text"]


def test_chat_stream_teacher_borrow_locked(client):
    """测试通过 SSE API 发送教师身份的借用指令时，借调人自动锁定为教师姓名"""
    resp = client.post(
        "/api/chat/stream",
        json={
            "prompt": "帮李明同学借用 DEV-SRV-201",
            "session_id": "sess-sse-teacher-rbac",
            "user_role": "TEACHER",
            "user_name": "李老师",
            "user_department": "计算机学院",
        },
    )
    assert resp.status_code == 200
    events = [
        json.loads(line[6:])
        for line in resp.text.strip().split("\n\n")
        if line.startswith("data: ")
    ]
    # 工具调用 borrow_asset 的 borrower 参数必须是李老师
    tool_start = next((e for e in events if e["type"] == "tool_start" and e.get("name") == "borrow_asset"), None)
    assert tool_start is not None
    assert tool_start["args"]["borrower"] == "李老师"



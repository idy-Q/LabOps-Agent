"""全机房主动自治巡检与《运行健康研判简报》自动化单元与集成测试套件"""

import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.init_db import init_db
from app.db.models import Asset, Ticket
from app.services.patrol_service import execute_autonomous_patrol
from app.tools.registry import get_tool, execute_tool
from app.agent.react_engine import ReActEngine, MockDecisionBrain


@pytest.fixture(scope="function")
def test_db():
    """每个测试用例独立的 SQLite 内存/临时数据库沙箱"""
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


def test_execute_autonomous_patrol_basic(test_db):
    """测试巡检主服务能够正确遍历资产、计算KPI、识别超温异常并出具简报"""
    result = execute_autonomous_patrol(db=test_db, operator="测试巡检员")

    assert result["status"] == "success"
    assert result["batch_no"].startswith("PTR-")
    assert result["operator"] == "测试巡检员"

    # 1. KPI 校验
    kpi = result["kpi"]
    assert kpi["total_scanned"] > 0
    assert kpi["avg_temperature"] > 0
    assert kpi["total_power_watts"] > 0

    # 2. 异常清单校验 (初始种子数据中 DEV-SRV-201 为 OVERHEAT，DEV-SRV-205 为 OFFLINE)
    abnormal = result["abnormal_devices"]
    assert len(abnormal) > 0

    overheat_devs = [d for d in abnormal if d["asset_no"] == "DEV-SRV-201"]
    assert len(overheat_devs) == 1
    assert overheat_devs[0]["is_overheat"] is True
    # 种子库中 DEV-SRV-201 已预置初始工单 TK-20260901-001，故防重复策略命中 EXISTING
    assert overheat_devs[0]["ticket_action"] == "EXISTING"
    assert overheat_devs[0]["ticket_no"] == "TK-20260901-001"

    # 3. 校验针对未建工单的异常设备 (如 DEV-SRV-205) 自动闭环提单
    created = result["created_tickets"]
    assert len(created) > 0
    created_dev_ids = [t["device_id"] for t in created]
    assert "DEV-SRV-205" in created_dev_ids

    # 4. 校验数据库持久化
    first_tk = created[0]
    db_tk = test_db.query(Ticket).filter(Ticket.ticket_no == first_tk["ticket_no"]).first()
    assert db_tk is not None
    assert db_tk.status == "PENDING"

    # 5. 校验健康评分与评级
    assert 0 <= result["health_score"] <= 100
    assert result["posture_level"] in ["EXCELLENT", "GOOD", "WARN", "CRITICAL"]

    # 6. 校验 Markdown 报告
    md = result["markdown_report"]
    assert "# 📋 高校实验室 IT 基础设施运行健康研判简报" in md
    assert result["batch_no"] in md
    assert "DEV-SRV-201" in md


def test_autonomous_patrol_duplicate_ticket_prevention(test_db):
    """测试防重复提单机制：已存在进行中工单的设备不会重复产生新工单"""
    # 第一次巡检：为没有工单的离线设备自动创建工单
    res1 = execute_autonomous_patrol(db=test_db, operator="第一轮巡检")
    assert len(res1["created_tickets"]) > 0

    initial_ticket_count = test_db.query(Ticket).count()

    # 第二次巡检：全设备均已有工单，核验防重拦截
    res2 = execute_autonomous_patrol(db=test_db, operator="第二轮巡检")
    assert len(res2["created_tickets"]) == 0  # 不应新增任何重复工单

    # 数据库工单总数严格保持一致
    current_ticket_count = test_db.query(Ticket).count()
    assert current_ticket_count == initial_ticket_count

    # 异常清单中应全部标注为 EXISTING 并关联对应工单
    for d in res2["abnormal_devices"]:
        if d.get("is_overheat") or d.get("is_offline"):
            assert d["ticket_action"] == "EXISTING"
            assert d["ticket_no"] is not None


def test_patrol_tool_registry_and_execute(test_db):
    """测试 run_autonomous_patrol 工具已成功在注册中心注册并可统一调度"""
    tool_entry = get_tool("run_autonomous_patrol")
    assert tool_entry is not None
    assert "主动自治巡检" in tool_entry.description

    # 通过统一分发器调用
    tool_res = execute_tool(
        name="run_autonomous_patrol",
        args={"operator": "调度器集成测试"},
        db=test_db,
    )
    assert tool_res["status"] == "success"
    assert "report" in tool_res
    assert tool_res["report"]["batch_no"].startswith("PTR-")


def test_api_metrics_patrol_endpoint(test_db):
    """测试 POST /api/metrics/patrol API 端点接口响应"""
    client = TestClient(app)
    response = client.post("/api/metrics/patrol")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"
    assert "data" in data
    assert "health_score" in data["data"]
    assert "markdown_report" in data["data"]


def test_react_engine_patrol_intent_recognition(test_db):
    """测试 ReAct 决策大脑意图识别与端到端闭环"""
    # 1. 意图识别测试：多种口语化与全网巡检提示词均能精准识别
    prompts_to_patrol = [
        "请执行机房全网主动自治体检，并出具健康研判简报",
        "机房巡检",
        "巡检",
        "自主巡检",
        "进行巡检",
        "做巡检",
        "机房体检",
        "系统体检",
        "机房健康态势",
        "生成健康研判报告",
    ]
    for p in prompts_to_patrol:
        decision = MockDecisionBrain.decide([{"role": "user", "content": p}])
        assert "tool_calls" in decision, f"Failed on prompt: {p}"
        assert decision["tool_calls"][0]["function"]["name"] == "run_autonomous_patrol", f"Failed on prompt: {p}"

    # 2. 规程排除与设备定向巡检精准分流
    reg_decision = MockDecisionBrain.decide([{"role": "user", "content": "机房巡检规范和应急预案是什么"}])
    assert reg_decision.get("tool_calls", [{}])[0].get("function", {}).get("name") == "query_regulations"

    dev_decision = MockDecisionBrain.decide([{"role": "user", "content": "巡检设备 DEV-SRV-201 的当前健康状态"}])
    assert dev_decision.get("tool_calls", [{}])[0].get("function", {}).get("name") == "get_server_metrics"

    # 3. 多轮对话防实体污染测试：前轮提及某设备，后轮发起全机房巡检不受污染
    multi_turn_history = [
        {"role": "user", "content": "查询设备 DEV-SRV-201 的监控指标"},
        {"role": "assistant", "content": "DEV-SRV-201 处于高温运行。"},
        {"role": "user", "content": "进行机房巡检"},
    ]
    multi_decision = MockDecisionBrain.decide(multi_turn_history)
    assert multi_decision.get("tool_calls", [{}])[0].get("function", {}).get("name") == "run_autonomous_patrol"

    # 4. 端到端 ReAct run 测试
    engine = ReActEngine()
    result = engine.run("全机房自主巡检", db=test_db)
    assert any(tc["name"] == "run_autonomous_patrol" for tc in result.tool_calls)
    assert "健康研判简报" in result.content or "巡检" in result.content

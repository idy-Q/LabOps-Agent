"""阶段 2 ReAct 调度引擎核心状态机自动化测试套件

测试项覆盖：
1. 基础对话与指引响应 (无工具直接回复)
2. 单步工具调用流式事件流 (think -> tool_start -> tool_end -> content -> done)
3. 多步 ReAct 状态机循环闭环：
   感知(get_server_metrics > 40℃) -> 研判(OVERHEAT) -> 闭环操作(create_ticket) -> 汇报总结
4. 业务状态流转与双向数据联动核验 (SQLite tickets 表真实写入、AuditLog 审计入库)
5. 资产借还流程驱动 (borrow_asset 与 return_asset)
6. 最大步数上限保护 (max_steps 截断，防止死循环)
7. 会话历史 (ChatHistory) 完整持久化 (用户输入、Assistant 输出、Thought 思考链)
"""

import os
import tempfile
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.agent.react_engine import ReActEngine, AgentResult
from app.db.init_db import init_db
from app.db.models import Asset, AuditLog, ChatHistory, Ticket


@pytest.fixture(scope="function")
def engine_test_db():
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
# 1. 基础对话与直接回复测试
# ---------------------------------------------------------
def test_engine_greeting_direct_response(engine_test_db):
    """测试常规打招呼或通用提问时无需调用工具，直接给出人设回复"""
    engine = ReActEngine()
    session_id = "sess-greet-001"

    result = engine.run(
        user_prompt="你好，请问你是谁？你能做什么？",
        session_id=session_id,
        db=engine_test_db,
    )

    assert isinstance(result, AgentResult)
    assert "LabOps-Agent" in result.content
    assert result.steps >= 1
    assert len(result.tool_calls) == 0

    # 验证 ChatHistory 持久化
    histories = engine_test_db.query(ChatHistory).filter(ChatHistory.session_id == session_id).all()
    assert len(histories) == 2
    user_hist = next(h for h in histories if h.role == "user")
    assistant_hist = next(h for h in histories if h.role == "assistant")
    assert "你能做什么" in user_hist.content
    assert "LabOps-Agent" in assistant_hist.content


# ---------------------------------------------------------
# 2. 多步 ReAct 端到端状态机闭环测试 (指标排查 -> 超温 -> 自动提单)
# ---------------------------------------------------------
def test_engine_overheat_triage_and_ticket_creation_loop(engine_test_db):
    """测试核心多步 ReAct 状态循环：
    Step 1: 调用 get_server_metrics(DEV-SRV-201) -> 返回 43.5℃ OVERHEAT
    Step 2: 研判超温，调用 create_ticket(title=...) -> 自动生成并写入工单
    Step 3: 汇总排查结果，向用户返回结构化报告
    """
    engine = ReActEngine()
    session_id = "sess-overheat-001"
    user_prompt = "查询 DEV-SRV-201 的监控指标，若异常请自动创建紧急排查工单"

    # 执行流式生成器并校验事件流
    events = list(engine.stream_run(user_prompt=user_prompt, session_id=session_id, db=engine_test_db))

    event_types = [e["type"] for e in events]
    assert "think" in event_types
    assert "tool_start" in event_types
    assert "tool_end" in event_types
    assert "content" in event_types
    assert "done" in event_types

    # 提取调用过的工具名称
    called_tool_names = [e["name"] for e in events if e["type"] == "tool_start"]
    assert "get_server_metrics" in called_tool_names
    assert "create_ticket" in called_tool_names

    # 校验最终输出内容
    content_events = [e for e in events if e["type"] == "content"]
    final_text = content_events[-1]["text"]
    assert "DEV-SRV-201" in final_text
    assert "OVERHEAT" in final_text or "过热" in final_text
    assert "TK-" in final_text

    # 校验数据库真实状态联动 (SQLite 真实写入工单)
    created_ticket = (
        engine_test_db.query(Ticket)
        .filter(Ticket.device_id == "DEV-SRV-201", Ticket.creator == "LabOps-Agent")
        .order_by(Ticket.id.desc())
        .first()
    )
    assert created_ticket is not None
    assert created_ticket.priority == "HIGH"
    assert created_ticket.status == "PENDING"
    assert created_ticket.ticket_no.startswith("TK-")

    # 校验 AuditLog 审计日志持久化 (两次工具调用均有记录)
    done_event = next(e for e in events if e["type"] == "done")
    trace_id = done_event["trace_id"]
    audit_records = engine_test_db.query(AuditLog).filter(AuditLog.trace_id == trace_id).all()
    assert len(audit_records) >= 2
    audit_tools = [a.tool_name for a in audit_records]
    assert "get_server_metrics" in audit_tools
    assert "create_ticket" in audit_tools
    for a in audit_records:
        assert a.status == "SUCCESS"

    # 校验 ChatHistory 思考链持久化
    assistant_chat = (
        engine_test_db.query(ChatHistory)
        .filter(ChatHistory.session_id == session_id, ChatHistory.role == "assistant")
        .first()
    )
    assert assistant_chat is not None
    assert assistant_chat.thought is not None
    assert len(assistant_chat.thought) > 10


# ---------------------------------------------------------
# 3. 正常指标查询测试 (无需提单单步闭环)
# ---------------------------------------------------------
def test_engine_healthy_server_metrics_flow(engine_test_db):
    """测试正常服务器查询时，感知后确认指标正常，不触发工单创建"""
    engine = ReActEngine()
    session_id = "sess-healthy-001"

    res = engine.run(
        user_prompt="请帮我巡检一下 DEV-SRV-202 的运行指标",
        session_id=session_id,
        db=engine_test_db,
    )

    assert res.steps >= 1
    tool_names = [t["name"] for t in res.tool_calls]
    assert "get_server_metrics" in tool_names
    assert "create_ticket" not in tool_names
    assert "HEALTHY" in res.content or "正常" in res.content


# ---------------------------------------------------------
# 4. 资产借还流转状态机测试
# ---------------------------------------------------------
def test_engine_borrow_and_return_asset_flow(engine_test_db):
    """测试设备资产借出与归还业务流程驱动"""
    engine = ReActEngine()

    # 1. 办理借用
    borrow_res = engine.run(
        user_prompt="请帮李老师办理实验设备 DEV-SRV-202 的借用登记",
        session_id="sess-borrow-001",
        db=engine_test_db,
    )
    assert any(tc["name"] == "borrow_asset" for tc in borrow_res.tool_calls)

    # 核验数据库中设备已变为 IN_USE
    a = engine_test_db.query(Asset).filter(Asset.asset_no == "DEV-SRV-202").first()
    assert a.borrow_status == "IN_USE"
    assert "李老师" in a.borrower

    # 2. 办理归还
    return_res = engine.run(
        user_prompt="请办理 DEV-SRV-202 设备的归还登记",
        session_id="sess-return-001",
        db=engine_test_db,
    )
    assert any(tc["name"] == "return_asset" for tc in return_res.tool_calls)

    # 核验数据库中设备已恢复为 AVAILABLE
    engine_test_db.refresh(a)
    assert a.borrow_status == "AVAILABLE"
    assert a.borrower is None


# ---------------------------------------------------------
# 5. 最大步数防护机制测试 (max_steps 保护)
# ---------------------------------------------------------
def test_engine_max_steps_protection(engine_test_db):
    """测试当步数达到上限时，状态机安全截断，防止死循环"""
    engine = ReActEngine()
    # 强制将最大步数设置为 1，由于超温排查至少需要 2 步，步数上限将在此生效
    res = engine.run(
        user_prompt="查询 DEV-SRV-201 监控指标并自动提单",
        session_id="sess-limit-001",
        db=engine_test_db,
        max_steps=1,
    )
    assert res.steps == 1
    # 验证产生安全截断或步骤保护提示
    assert "最大推理步数上限" in res.content or "DEV-SRV-201" in res.content


# ---------------------------------------------------------
# 6. 台账检索与工单查询意图驱动测试
# ---------------------------------------------------------
def test_engine_query_assets_intent(engine_test_db):
    """测试用户发起资产台账查询意图驱动 query_assets 工具"""
    engine = ReActEngine()
    res = engine.run(
        user_prompt="请帮我查询资产台账列表，看有哪些设备",
        session_id="sess-query-asset-001",
        db=engine_test_db,
    )
    assert any(tc["name"] == "query_assets" for tc in res.tool_calls)
    assert "资产台账查询结果" in res.content


def test_engine_query_tickets_intent(engine_test_db):
    """测试用户发起工单列表查询意图驱动 query_tickets 工具"""
    engine = ReActEngine()
    res = engine.run(
        user_prompt="查询工单列表，查看目前机房待办工单",
        session_id="sess-query-ticket-001",
        db=engine_test_db,
    )
    assert any(tc["name"] == "query_tickets" for tc in res.tool_calls)
    assert "工单列表检索结果" in res.content


def test_engine_sse_event_serialization_contract(engine_test_db):
    """验证流式输出的每个事件完全符合 JSON 序列化规范 (为阶段 4 SSE 接口做准备)"""
    import json

    engine = ReActEngine()
    events = list(engine.stream_run(
        user_prompt="查询 DEV-SRV-202 的运行指标",
        session_id="sess-sse-test-001",
        db=engine_test_db,
    ))
    assert len(events) >= 4
    for event in events:
        assert isinstance(event, dict)
        assert "type" in event
        # 确保所有事件字典均可无损 JSON 序列化
        serialized = json.dumps(event, ensure_ascii=False)
        assert len(serialized) > 0


def test_engine_db_none_standalone():
    """验证无 DB 会话注入时，ReAct 引擎与独立 Mock 大脑依然可正常执行并返回"""
    engine = ReActEngine()
    res = engine.run(
        user_prompt="查询 DEV-SRV-201 的监控指标",
        session_id="sess-nodb-001",
        db=None,
    )
    assert res.steps >= 1
    assert "DEV-SRV-201" in res.content


def test_engine_api_error_fallback_to_mock(monkeypatch, engine_test_db):
    """验证配置为真实 API 模式但远程接口异常时，引擎自动安全降级至本地确定性 Mock 大脑"""
    from app.config import settings

    # 强制将模式设为 real 并配置假 Key
    monkeypatch.setattr(settings, "AGENT_MOCK_MODE", "real")
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "fake_sk_test_123456")

    # Mock OpenAI client 抛出网络或认证异常
    class MockFailingCompletions:
        def create(self, *args, **kwargs):
            raise ConnectionError("Simulated OpenAI upstream network timeout")

    class MockFailingChat:
        completions = MockFailingCompletions()

    class MockFailingOpenAI:
        def __init__(self, *args, **kwargs):
            self.chat = MockFailingChat()

    monkeypatch.setattr("openai.OpenAI", MockFailingOpenAI)

    engine = ReActEngine()
    res = engine.run(
        user_prompt="查询 DEV-SRV-202 的运行指标",
        session_id="sess-fallback-001",
        db=engine_test_db,
    )
    # 验证降级后仍可返回正确分析结果，未抛出致命异常
    assert res.steps >= 1
    assert "DEV-SRV-202" in res.content


def test_engine_borrow_conflict_feedback(engine_test_db):
    """验证资产已被占用时，引擎执行借用工具后能向管理员反馈冲突提示"""
    engine = ReActEngine()
    # 先借出 DEV-SRV-202
    engine.run(
        user_prompt="帮张三老师借用 DEV-SRV-202",
        session_id="sess-borrow-first",
        db=engine_test_db,
    )

    # 再次尝试借出
    res = engine.run(
        user_prompt="帮李四同学借用 DEV-SRV-202",
        session_id="sess-borrow-second",
        db=engine_test_db,
    )
    assert "无法重复借出" in res.content or "IN_USE" in res.content


def test_engine_non_existent_device_truthful_report(engine_test_db):
    """验证查询不存在设备时，引擎诚实返回未找到提示，而不虚构指标"""
    engine = ReActEngine()
    res = engine.run(
        user_prompt="查询 DEV-SRV-999 的监控指标",
        session_id="sess-ghost-001",
        db=engine_test_db,
    )
    assert res.steps >= 1
    assert "未在机房资产台账中找到" in res.content or "排查异常" in res.content
    assert "HEALTHY" not in res.content


def test_engine_update_ticket_status_flow(engine_test_db):
    """验证引擎准确识别工单推进意图并调用 update_ticket_status 工具"""
    engine = ReActEngine()
    # 获取一条工单
    t = engine_test_db.query(Ticket).first()
    target_no = t.ticket_no

    res = engine.run(
        user_prompt=f"帮我将工单 {target_no} 状态更新为 RESOLVED，说明：已更换散热硅脂",
        session_id="sess-tk-update-001",
        db=engine_test_db,
    )
    assert any(tc["name"] == "update_ticket_status" for tc in res.tool_calls)
    assert "RESOLVED" in res.content or "已更新" in res.content

    # 验证 SQLite 数据库中状态确实更新
    engine_test_db.refresh(t)
    assert t.status == "RESOLVED"


def test_engine_update_asset_health_flow(engine_test_db):
    """验证引擎准确识别设备健康变更意图并调用 update_asset_health 工具"""
    engine = ReActEngine()
    res = engine.run(
        user_prompt="将设备 DEV-SRV-201 健康状态更新为 HEALTHY",
        session_id="sess-asset-health-001",
        db=engine_test_db,
    )
    assert any(tc["name"] == "update_asset_health" for tc in res.tool_calls)
    assert "HEALTHY" in res.content or "更新" in res.content

    a = engine_test_db.query(Asset).filter(Asset.asset_no == "DEV-SRV-201").first()
    assert a.health_status == "HEALTHY"


def test_engine_direct_create_ticket_flow(engine_test_db):
    """验证引擎支持管理员主动直接创建工单"""
    engine = ReActEngine()
    res = engine.run(
        user_prompt="创建工单：机房201空调突发冷媒泄漏紧急处置",
        session_id="sess-direct-tk-001",
        db=engine_test_db,
    )
    assert any(tc["name"] == "create_ticket" for tc in res.tool_calls)
    assert "工单创建成功" in res.content or "TK-" in res.content


def test_engine_query_assets_with_health_filter(engine_test_db):
    """验证资产检索时准确传递过滤参数"""
    engine = ReActEngine()
    res = engine.run(
        user_prompt="查询当前健康状态为 OVERHEAT 的设备资产",
        session_id="sess-filter-asset-001",
        db=engine_test_db,
    )
    assert any(tc["name"] == "query_assets" for tc in res.tool_calls)
    assert "资产台账查询结果" in res.content


def test_engine_query_tickets_with_status_filter(engine_test_db):
    """验证工单查询时准确传递 status 状态参数"""
    engine = ReActEngine()
    res = engine.run(
        user_prompt="查询待办工单列表",
        session_id="sess-filter-ticket-001",
        db=engine_test_db,
    )
    assert any(tc["name"] == "query_tickets" for tc in res.tool_calls)
    assert "工单列表检索结果" in res.content


def test_engine_offline_device_diagnosis_report(engine_test_db):
    """验证 ReAct 调度引擎对 OFFLINE 设备进行指标排查时，客观如实汇报离线失联预警，杜绝误报为 HEALTHY"""
    engine = ReActEngine()
    res = engine.run(
        user_prompt="查询 DEV-SRV-205 的监控指标",
        session_id="sess-offline-diag-001",
        db=engine_test_db,
    )
    assert any(tc["name"] == "get_server_metrics" for tc in res.tool_calls)
    assert "DEV-SRV-205" in res.content
    assert "OFFLINE" in res.content
    assert "离线" in res.content
    assert "HEALTHY" not in res.content
    assert "运行良好" not in res.content


def test_engine_warning_device_diagnosis_report(engine_test_db):
    """验证 ReAct 调度引擎对 WARNING 预警设备进行指标排查时，客观汇报 WARNING 状态，杜绝误报为 HEALTHY"""
    engine = ReActEngine()
    res = engine.run(
        user_prompt="查询 DEV-UPS-201 的监控指标",
        session_id="sess-warning-diag-001",
        db=engine_test_db,
    )
    assert any(tc["name"] == "get_server_metrics" for tc in res.tool_calls)
    assert "DEV-UPS-201" in res.content
    assert "WARNING" in res.content
    assert "HEALTHY" not in res.content


# ---------------------------------------------------------
# RBAC 角色权限硬防御与防越权测试套件
# ---------------------------------------------------------
def test_engine_student_borrow_asset_intercepted(engine_test_db):
    """验证学生角色 (STUDENT) 发起借用指令时被坚决拦截，不调用 borrow_asset 工具"""
    engine = ReActEngine()
    res = engine.run(
        user_prompt="借用 DEV-SRV-202 服务器开展课程实验",
        session_id="sess-student-borrow-001",
        db=engine_test_db,
        user_role="STUDENT",
        user_name="张同学",
        user_department="计算机科学与技术2201班",
    )
    # 坚决不调用 borrow_asset 工具
    assert not any(tc["name"] == "borrow_asset" for tc in res.tool_calls)
    assert len(res.tool_calls) == 0
    assert "权限拦截警报" in res.content
    assert "张同学" in res.content
    assert "学生" in res.content
    assert "在读学生无权直接办理" in res.content or "需指导教师办理" in res.content

    # 验证数据库中设备仍为 AVAILABLE，未被篡改
    asset = engine_test_db.query(Asset).filter(Asset.asset_no == "DEV-SRV-202").first()
    assert asset.borrow_status == "AVAILABLE"


def test_engine_student_update_ticket_intercepted(engine_test_db):
    """验证学生角色更新或办结工单时被直接拦截并提示只读"""
    engine = ReActEngine()
    res = engine.run(
        user_prompt="更新工单 TK-20260901-001 为已解决",
        session_id="sess-student-tk-001",
        db=engine_test_db,
        user_role="STUDENT",
        user_name="李同学",
    )
    assert not any(tc["name"] == "update_ticket_status" for tc in res.tool_calls)
    assert len(res.tool_calls) == 0
    assert "权限拦截警报" in res.content
    assert "只读" in res.content


def test_engine_student_update_health_intercepted(engine_test_db):
    """验证学生角色修改硬件健康度时被直接拦截"""
    engine = ReActEngine()
    res = engine.run(
        user_prompt="将 DEV-SRV-201 的健康状态更新为 HEALTHY",
        session_id="sess-student-health-001",
        db=engine_test_db,
        user_role="STUDENT",
        user_name="李同学",
    )
    assert not any(tc["name"] == "update_asset_health" for tc in res.tool_calls)
    assert len(res.tool_calls) == 0
    assert "权限拦截警报" in res.content


def test_engine_teacher_borrow_asset_locked_borrower(engine_test_db):
    """验证教师角色借调设备时，借用人强制锁定为当前教师本人，杜绝冒名代借"""
    engine = ReActEngine()
    res = engine.run(
        user_prompt="帮王同学办理 DEV-SRV-202 借用登记",
        session_id="sess-teacher-borrow-001",
        db=engine_test_db,
        user_role="TEACHER",
        user_name="李老师",
        user_department="计算机科学与技术学院",
    )
    # 调用了 borrow_asset 工具
    assert any(tc["name"] == "borrow_asset" for tc in res.tool_calls)
    borrow_call = next(tc for tc in res.tool_calls if tc["name"] == "borrow_asset")
    # 强制锁定为李老师本人，而非输入的王同学
    assert borrow_call["args"]["borrower"] == "李老师"

    # 验证数据库中设备真实记录借用人为李老师
    asset = engine_test_db.query(Asset).filter(Asset.asset_no == "DEV-SRV-202").first()
    assert asset.borrow_status == "IN_USE"
    assert asset.borrower == "李老师"


def test_engine_teacher_close_ticket_intercepted(engine_test_db):
    """验证教师角色请求办结/关闭工单时被拦截，提示需主管核验闭环"""
    engine = ReActEngine()
    res = engine.run(
        user_prompt="办结工单 TK-20260901-001",
        session_id="sess-teacher-close-001",
        db=engine_test_db,
        user_role="TEACHER",
        user_name="李老师",
    )
    assert not any(tc["name"] == "update_ticket_status" for tc in res.tool_calls)
    assert len(res.tool_calls) == 0
    assert "权限拦截警报" in res.content
    assert "需机房专职主管验收核验闭环" in res.content or "主管" in res.content


def test_engine_teacher_update_health_intercepted(engine_test_db):
    """验证教师角色修改硬件健康度时被直接拦截"""
    engine = ReActEngine()
    res = engine.run(
        user_prompt="将 DEV-SRV-201 的健康状态更新为 HEALTHY",
        session_id="sess-teacher-health-001",
        db=engine_test_db,
        user_role="TEACHER",
        user_name="李老师",
    )
    assert not any(tc["name"] == "update_asset_health" for tc in res.tool_calls)
    assert len(res.tool_calls) == 0
    assert "权限拦截警报" in res.content


def test_engine_rule_inquiry_does_not_falsely_intercept_or_borrow(engine_test_db):
    """验证用户咨询借用规则时准确检索规约，学生不被误报越权，管理员不被误触发设备借出"""
    engine = ReActEngine()

    # 1. 学生咨询借用规则：调用 query_regulations，不得返回权限拦截警报
    res_student = engine.run(
        user_prompt="请问机房设备的借用规则是什么？",
        session_id="sess-rule-inquiry-student",
        db=engine_test_db,
        user_role="STUDENT",
        user_name="陈同学",
    )
    assert any(tc["name"] == "query_regulations" for tc in res_student.tool_calls)
    assert "权限拦截警报" not in res_student.content

    # 2. 管理员咨询借用规则：调用 query_regulations，坚决不触发 borrow_asset 工具
    res_admin = engine.run(
        user_prompt="请问机房设备的借用规则是什么？",
        session_id="sess-rule-inquiry-admin",
        db=engine_test_db,
        user_role="ADMIN",
        user_name="王主管",
    )
    assert any(tc["name"] == "query_regulations" for tc in res_admin.tool_calls)
    assert not any(tc["name"] == "borrow_asset" for tc in res_admin.tool_calls)


def test_engine_ticket_workflow_inquiry_does_not_mutate_ticket(engine_test_db):
    """验证咨询工单办结流程时准确查询规约，管理员不误操作办结工单，学生不被误报拦截"""
    engine = ReActEngine()
    t = engine_test_db.query(Ticket).first()
    init_status = t.status

    res = engine.run(
        user_prompt="请问工单办结流程是什么？",
        session_id="sess-ticket-workflow-inquiry",
        db=engine_test_db,
        user_role="ADMIN",
        user_name="王主管",
    )
    assert any(tc["name"] == "query_regulations" for tc in res.tool_calls)
    assert not any(tc["name"] == "update_ticket_status" for tc in res.tool_calls)

    # 确保数据库中的工单未被擅自流转
    engine_test_db.refresh(t)
    assert t.status == init_status


def test_engine_student_can_query_ticket_status_read_only(engine_test_db):
    """验证学生角色查询具体工单当前状态时属于只读权限，不被越权拦截，准确调用 query_tickets"""
    engine = ReActEngine()
    t = engine_test_db.query(Ticket).first()
    t_no = t.ticket_no

    res = engine.run(
        user_prompt=f"查询工单 {t_no} 的当前状态",
        session_id="sess-student-query-tk-status",
        db=engine_test_db,
        user_role="STUDENT",
        user_name="陈同学",
    )
    assert any(tc["name"] == "query_tickets" for tc in res.tool_calls)
    assert not any(tc["name"] == "update_ticket_status" for tc in res.tool_calls)
    assert "权限拦截警报" not in res.content
    assert t_no in res.content or "工单列表" in res.content


def test_engine_admin_ui_borrow_with_department(engine_test_db):
    """验证管理员从看板发起借用登记并附带教研室时，准确将借调人提取为王主管而非科研教师兜底"""
    engine = ReActEngine()
    res = engine.run(
        user_prompt="帮 王主管 (网络中心运维部) 办理设备 DEV-SRV-201 的借用登记",
        session_id="sess-admin-ui-borrow",
        db=engine_test_db,
        user_role="ADMIN",
        user_name="王主管",
        user_department="网络中心运维部",
    )
    assert any(tc["name"] == "borrow_asset" for tc in res.tool_calls)
    borrow_call = next(tc for tc in res.tool_calls if tc["name"] == "borrow_asset")
    assert borrow_call["args"]["borrower"] == "王主管"


def test_engine_student_natural_phrasing_borrow_intercepted(engine_test_db):
    """验证学生角色采用自然口语表达借调指令时（如我要借/申请借调）仍被严正硬拦截"""
    engine = ReActEngine()
    res = engine.run(
        user_prompt="我要借 DEV-SRV-202",
        session_id="sess-student-natural-borrow",
        db=engine_test_db,
        user_role="STUDENT",
        user_name="陈同学",
    )
    assert not any(tc["name"] == "borrow_asset" for tc in res.tool_calls)
    assert "权限拦截警报" in res.content


def test_engine_natural_health_update_rbac(engine_test_db):
    """验证自然口语修改设备健康状态（如改为良好）时的精确分权：学生拦截，管理员成功执行"""
    engine = ReActEngine()

    # 1. 学生修改健康度：拦截
    res_student = engine.run(
        user_prompt="把 DEV-SRV-201 改为良好",
        session_id="sess-student-health-natural",
        db=engine_test_db,
        user_role="STUDENT",
        user_name="陈同学",
    )
    assert not any(tc["name"] == "update_asset_health" for tc in res_student.tool_calls)
    assert "权限拦截警报" in res_student.content

    # 2. 管理员修改健康度：成功执行 update_asset_health
    res_admin = engine.run(
        user_prompt="把 DEV-SRV-201 改为良好",
        session_id="sess-admin-health-natural",
        db=engine_test_db,
        user_role="ADMIN",
        user_name="王主管",
    )
    assert any(tc["name"] == "update_asset_health" for tc in res_admin.tool_calls)
    health_call = next(tc for tc in res_admin.tool_calls if tc["name"] == "update_asset_health")
    assert health_call["args"]["health_status"] == "HEALTHY"




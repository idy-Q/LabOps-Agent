"""阶段 1 自动化验证测试套件 (增强版与深度测试)

测试项覆盖：
1. 健康检查与根重定向
2. 机房资产数据底座及完整 CRUD（查询、编号过滤、关键词与多条件过滤、新增、查重、局部修改、删除）
3. 运维工单数据底座及完整 CRUD（查询、工单号精确过滤、标题/描述关键词模糊搜索、自动编号生成、重复编号拦截、状态流转、异常分支）
4. 审计日志表 (AuditLog) 与对话持久化表 (ChatHistory) ORM 模型及 Pydantic Schema 完整性
5. 边界与异常测试（枚举非法、首尾空格剥离与空白字符拦截、未定义字段 extra='forbid' 拦截、分页越界、404 处理）
6. 数据库幂等性与 IntegrityError 事务回滚安全性
7. 全局配置解析鲁棒性（CORS 字符串/列表兼容性）
"""

import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.config import Settings
from app.db.session import Base, get_db
from app.db.models import (
    Ticket,
    Asset,
    AuditLog,
    ChatHistory,
    User,
    ServerRoom,
    ServerRack,
    AssetBorrowLog,
    TicketWorkflow,
    KnowledgeDocument,
    KnowledgeChunk,
)
from app.db.init_db import init_db
from app.schemas.audit import AuditLogCreate, AuditLogResponse
from app.schemas.chat import ChatHistoryCreate, ChatHistoryResponse


@pytest.fixture(scope="module")
def test_db_env():
    """创建临时测试数据库，实现测试数据库与开发生产数据库完全物理隔离"""
    temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_file.close()
    test_db_url = f"sqlite:///{temp_file.name}"

    engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # 初始化测试库与预置种子数据
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

    # 测试结束后清理
    app.dependency_overrides.clear()
    engine.dispose()
    if os.path.exists(temp_file.name):
        try:
            os.remove(temp_file.name)
        except Exception:
            pass


@pytest.fixture(scope="module")
def client(test_db_env):
    """测试 HTTP 客户端"""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def db_session(test_db_env):
    """单独的测试数据库会话"""
    session = test_db_env["session_factory"]()
    try:
        yield session
    finally:
        session.close()


# ==================== 1. 基础服务接口测试 ====================


def test_health_check(client):
    """测试系统健康检查端点"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "LabOps-Agent"
    assert data["version"] == "1.0.0"


def test_root_redirect(client):
    """测试根路径重定向至文档"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/docs"


# ==================== 2. 机房资产管理接口测试 ====================


def test_get_assets_seed_data(client):
    """测试获取预置的机房资产种子数据"""
    response = client.get("/api/assets/")
    assert response.status_code == 200
    assets = response.json()
    assert len(assets) >= 5

    nos = [a["asset_no"] for a in assets]
    assert "DEV-SRV-201" in nos
    assert "DEV-NET-301" in nos


def test_get_assets_with_filter(client):
    """测试机房资产多维度条件过滤与精确编号查询"""
    # 1. 按健康状态过滤 (OVERHEAT)
    response = client.get("/api/assets/?health_status=OVERHEAT")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["asset_no"] == "DEV-SRV-201"
    assert data[0]["health_status"] == "OVERHEAT"

    # 2. 按关键词模糊过滤
    response = client.get("/api/assets/?keyword=交换机")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert "交换机" in data[0]["name"]

    # 3. 按资产编号精确过滤
    response_no = client.get("/api/assets/?asset_no=DEV-SRV-202")
    assert response_no.status_code == 200
    data_no = response_no.json()
    assert len(data_no) == 1
    assert data_no[0]["name"] == "2号机房-CPU计算节点02"


def test_get_asset_by_id(client):
    """测试获取单个资产详情"""
    list_res = client.get("/api/assets/")
    first_asset = list_res.json()[0]
    asset_id = first_asset["id"]

    res = client.get(f"/api/assets/{asset_id}")
    assert res.status_code == 200
    assert res.json()["asset_no"] == first_asset["asset_no"]

    # 不存在的资产应返回 404
    res_not_found = client.get("/api/assets/999999")
    assert res_not_found.status_code == 404


def test_create_and_update_asset(client):
    """测试新增资产、重复编号冲突拦截与状态更新"""
    new_asset = {
        "asset_no": "DEV-TEST-001",
        "name": "测试节点-高密计算板",
        "category": "服务器",
        "location": "实训楼201-机柜C05",
        "health_status": "HEALTHY",
        "borrow_status": "AVAILABLE",
        "borrower": None,
        "specs": "128核 256GB 闪存",
    }
    # 1. 成功创建
    create_res = client.post("/api/assets/", json=new_asset)
    assert create_res.status_code == 201
    created_id = create_res.json()["id"]

    # 2. 重复编号拦截 (400)
    dup_res = client.post("/api/assets/", json=new_asset)
    assert dup_res.status_code == 400
    assert "已存在" in dup_res.json()["detail"]

    # 3. 更新资产借用状态
    update_data = {
        "borrow_status": "IN_USE",
        "borrower": "测试借用人",
    }
    patch_res = client.patch(f"/api/assets/{created_id}", json=update_data)
    assert patch_res.status_code == 200
    assert patch_res.json()["borrow_status"] == "IN_USE"
    assert patch_res.json()["borrower"] == "测试借用人"

    # 4. 删除测试资产 (HTTP 204 无内容)
    del_res = client.delete(f"/api/assets/{created_id}")
    assert del_res.status_code == 204
    assert del_res.content == b""

    # 5. 确认已删除
    get_res = client.get(f"/api/assets/{created_id}")
    assert get_res.status_code == 404


# ==================== 3. 运维工单管理接口测试 ====================


def test_get_tickets_seed_data(client):
    """测试获取预置运维工单数据"""
    response = client.get("/api/tickets/")
    assert response.status_code == 200
    tickets = response.json()
    assert len(tickets) >= 2

    ticket_nos = [t["ticket_no"] for t in tickets]
    assert "TK-20260901-001" in ticket_nos
    assert "TK-20260901-002" in ticket_nos


def test_get_tickets_with_filter(client):
    """测试工单条件过滤与关键词搜索"""
    # 1. 按优先级过滤
    res = client.get("/api/tickets/?priority=HIGH")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert all(t["priority"] == "HIGH" for t in data)

    # 2. 按关联设备过滤
    res = client.get("/api/tickets/?device_id=DEV-SRV-201")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert data[0]["device_id"] == "DEV-SRV-201"

    # 3. 按工单编号精确过滤
    res_no = client.get("/api/tickets/?ticket_no=TK-20260901-001")
    assert res_no.status_code == 200
    data_no = res_no.json()
    assert len(data_no) == 1
    assert data_no[0]["ticket_no"] == "TK-20260901-001"

    # 4. 按关键词模糊搜索 (匹配标题或描述)
    res_kw = client.get("/api/tickets/?keyword=温度过热")
    assert res_kw.status_code == 200
    data_kw = res_kw.json()
    assert len(data_kw) >= 1
    assert "温度过热" in data_kw[0]["title"]


def test_create_and_update_ticket(client):
    """测试创建工单（自动编号生成）、重复工单号拦截、状态流转与异常处理"""
    new_ticket = {
        "title": "机房精密空调排水管冷凝水溢出告警",
        "description": "巡检发现3号空调机组下托盘传感器触水，疑似排水软管老化脱落，需立即疏通更换。",
        "priority": "CRITICAL",
        "creator": "李巡检员",
        "device_id": "DEV-UPS-201",
    }
    # 1. 自动生成工单号并创建成功
    create_res = client.post("/api/tickets/", json=new_ticket)
    assert create_res.status_code == 201
    ticket_data = create_res.json()
    created_id = ticket_data["id"]
    generated_ticket_no = ticket_data["ticket_no"]
    assert generated_ticket_no.startswith("TK-")
    assert ticket_data["status"] == "PENDING"

    # 2. 尝试显式传入已存在的工单号，验证重复拦截 (HTTP 400)
    dup_ticket = dict(new_ticket)
    dup_ticket["ticket_no"] = generated_ticket_no
    dup_res = client.post("/api/tickets/", json=dup_ticket)
    assert dup_res.status_code == 400
    assert "已存在" in dup_res.json()["detail"]

    # 3. 获取详情
    detail_res = client.get(f"/api/tickets/{created_id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["title"] == new_ticket["title"]

    # 4. 状态更新为 PROCESSING，并更新描述与提单人
    patch_res = client.patch(
        f"/api/tickets/{created_id}",
        json={
            "status": "PROCESSING",
            "description": "运维人员已到场处理排水接头",
            "creator": "张值班员",
        },
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "PROCESSING"
    assert "运维人员已到场" in patch_res.json()["description"]
    assert patch_res.json()["creator"] == "张值班员"

    # 5. 再次更新为 RESOLVED
    resolve_res = client.patch(
        f"/api/tickets/{created_id}",
        json={"status": "RESOLVED"},
    )
    assert resolve_res.status_code == 200
    assert resolve_res.json()["status"] == "RESOLVED"

    # 6. 删除工单 (204)
    del_res = client.delete(f"/api/tickets/{created_id}")
    assert del_res.status_code == 204
    assert del_res.content == b""

    # 7. 确认已删除
    assert client.get(f"/api/tickets/{created_id}").status_code == 404


# ==================== 4. 审计日志与会话模型表结构及 Schema 验证 ====================


def test_audit_log_and_chat_history_models(db_session):
    """测试底层 AuditLog 与 ChatHistory 表在隔离库中的读写可用性"""
    # 1. 写入一条审计记录
    audit = AuditLog(
        trace_id="trace-test-123456",
        tool_name="get_server_metrics",
        tool_args='{"server_id": "DEV-SRV-201"}',
        tool_result='{"cpu_usage": "78%", "temp": "85C"}',
        status="SUCCESS",
    )
    db_session.add(audit)
    db_session.commit()
    db_session.refresh(audit)
    assert audit.id is not None
    assert audit.tool_name == "get_server_metrics"

    # 2. 写入一条会话记录
    chat = ChatHistory(
        session_id="session-test-888",
        role="assistant",
        content="正在为您排查服务器指标...",
        thought="检测到用户意图为服务器状态排查，决定调用 get_server_metrics 工具",
    )
    db_session.add(chat)
    db_session.commit()
    db_session.refresh(chat)
    assert chat.id is not None
    assert chat.role == "assistant"

    # 3. 清理测试数据
    db_session.delete(audit)
    db_session.delete(chat)
    db_session.commit()


def test_audit_and_chat_pydantic_schemas():
    """测试 AuditLog 与 ChatHistory 的 Pydantic Schemas 校验与类型转换"""
    # 校验 AuditLogCreate
    audit_data = {
        "trace_id": "trace-pydantic-1",
        "tool_name": "create_ticket",
        "tool_args": '{"title": "测试"}',
        "tool_result": '{"ticket_id": "TK-1"}',
        "status": "SUCCESS",
    }
    audit_schema = AuditLogCreate(**audit_data)
    assert audit_schema.tool_name == "create_ticket"

    # 校验 ChatHistoryCreate
    chat_data = {
        "session_id": "sess-001",
        "role": "user",
        "content": "机房温度现在是多少？",
    }
    chat_schema = ChatHistoryCreate(**chat_data)
    assert chat_schema.role == "user"
    assert chat_schema.thought is None


# ==================== 5. 边界、异常与严格校验测试 ====================


def test_validation_errors(client):
    """测试非法入参、非法未定义字段与首尾空白触发表单校验 422 错误"""
    # 1. 工单非法优先级
    res = client.post(
        "/api/tickets/",
        json={"title": "测试", "description": "测试", "priority": "UNKNOWN"},
    )
    assert res.status_code == 422

    # 2. 工单空标题
    res_empty = client.post("/api/tickets/", json={"title": "", "description": "测试"})
    assert res_empty.status_code == 422

    # 3. 纯空白字符标题（验证 str_strip_whitespace=True 拦截）
    res_whitespace = client.post(
        "/api/tickets/", json={"title": "   ", "description": "测试"}
    )
    assert res_whitespace.status_code == 422

    # 4. 资产非法健康状态
    res_health = client.post(
        "/api/assets/",
        json={
            "asset_no": "DEV-TEST-ERR",
            "name": "测试设备",
            "category": "服务器",
            "location": "机房",
            "health_status": "BROKEN_INVALID",
        },
    )
    assert res_health.status_code == 422

    # 5. PATCH 传入未定义的非法字段（验证 extra='forbid' 拦截，防止拼写错误静默丢弃）
    patch_illegal = client.patch(
        "/api/assets/1",
        json={"statuss_misspelled": "ONLINE"},
    )
    assert patch_illegal.status_code == 422


def test_pagination_and_not_found(client):
    """测试分页参数与不存在资源的 404 处理"""
    # 限制单页 1 条记录
    res = client.get("/api/assets/?limit=1")
    assert res.status_code == 200
    assert len(res.json()) == 1

    # 删除不存在的资源
    assert client.delete("/api/tickets/99999").status_code == 404
    assert client.delete("/api/assets/99999").status_code == 404

    # 更新不存在的资源
    assert (
        client.patch("/api/tickets/99999", json={"status": "RESOLVED"}).status_code
        == 404
    )
    assert (
        client.patch("/api/assets/99999", json={"borrow_status": "IN_USE"}).status_code
        == 404
    )


# ==================== 6. 数据库幂等性与配置解析鲁棒性 ====================


def test_init_db_idempotency(test_db_env):
    """测试多次调用 init_db 具备绝对幂等性，不产生数据重复与主键异常"""
    engine = test_db_env["engine"]
    session_factory = test_db_env["session_factory"]

    # 连续执行 2 次初始化写入
    init_db(seed=True, custom_engine=engine, custom_session_factory=session_factory)
    init_db(seed=True, custom_engine=engine, custom_session_factory=session_factory)

    session = session_factory()
    try:
        assert session.query(Asset).count() == 15
        assert session.query(Ticket).count() == 9
        assert session.query(ChatHistory).count() == 4
        assert session.query(User).count() == 4
        assert session.query(ServerRoom).count() == 3
        assert session.query(ServerRack).count() == 3
        assert session.query(AssetBorrowLog).count() == 3
        assert session.query(TicketWorkflow).count() == 4
        assert session.query(KnowledgeDocument).count() == 3
        assert session.query(KnowledgeChunk).count() == 22

        # 验证 ORM 关系与双向访问
        doc = session.query(KnowledgeDocument).filter(KnowledgeDocument.doc_id == "DOC-RAG-001").first()
        assert doc is not None
        assert len(doc.chunks) > 0
        assert doc.chunks[0].document == doc
    finally:
        session.close()


def test_cors_config_parsing():
    """测试 Settings 对 CORS_ORIGINS 的多格式鲁棒性解析"""
    # 1. 逗号分隔字符串解析
    s1 = Settings(CORS_ORIGINS="http://localhost:5173,http://127.0.0.1:5173")
    assert s1.CORS_ORIGINS == ["http://localhost:5173", "http://127.0.0.1:5173"]

    # 2. 列表直接传入
    s2 = Settings(CORS_ORIGINS=["*"])
    assert s2.CORS_ORIGINS == ["*"]

    # 3. JSON 格式字符串解析
    s3 = Settings(CORS_ORIGINS='["http://localhost:3000"]')
    assert s3.CORS_ORIGINS == ["http://localhost:3000"]


def test_preseeded_chat_sessions_and_drawer_api(client):
    """验证预置的 2 组历史会话可通过 /api/chat/sessions 和 /api/chat/history 完整回放"""
    # 1. 查询会话摘要列表
    res_sess = client.get("/api/chat/sessions")
    assert res_sess.status_code == 200
    sess_body = res_sess.json()
    assert sess_body["status"] == "success"
    session_ids = [s["session_id"] for s in sess_body["data"]]
    assert "sess_temp_emergency_01" in session_ids
    assert "sess_auto_inspection_02" in session_ids

    # 2. 调取超温应急会话详情
    res_hist = client.get("/api/chat/history?session_id=sess_temp_emergency_01")
    assert res_hist.status_code == 200
    msgs = res_hist.json()
    assert len(msgs) == 2
    assert msgs[0]["role"] == "user"
    assert "2号机房GPU计算节点01温度过高" in msgs[0]["content"]
    assert msgs[1]["role"] == "assistant"
    assert "TK-20260901-001" in msgs[1]["content"]
    assert msgs[1]["thought"] is not None
    assert "get_server_metrics" in msgs[1]["thought"]


def test_offline_assets_and_metrics_summary_api(client):
    """验证综合指标大盘及资产工单分类接口对扩充数据的聚合计算"""
    # 1. 查询离线状态资产
    res_offline = client.get("/api/assets/?health_status=OFFLINE")
    assert res_offline.status_code == 200
    data_off = res_offline.json()
    assert len(data_off) >= 2
    assert any(a["asset_no"] == "DEV-SRV-205" for a in data_off)
    assert any(a["asset_no"] == "DEV-NET-304" for a in data_off)

    # 2. 查询已解决与已关闭工单
    res_res = client.get("/api/tickets/?status=RESOLVED")
    assert res_res.status_code == 200
    assert len(res_res.json()) >= 2

    res_clo = client.get("/api/tickets/?status=CLOSED")
    assert res_clo.status_code == 200
    assert len(res_clo.json()) >= 2

    # 3. 验证综合监控大盘聚合度
    res_sum = client.get("/api/metrics/summary")
    assert res_sum.status_code == 200
    sum_data = res_sum.json()["data"]
    assert sum_data["assets"]["total"] == 15
    assert sum_data["assets"]["offline"] >= 2
    assert sum_data["tickets"]["total"] == 9
    assert sum_data["tickets"]["resolved"] >= 2
    assert sum_data["tickets"]["closed"] >= 2
    assert sum_data["overview"]["active_alerts_count"] >= 3


def test_asset_detail_crud(client):
    """测试设备硬件物理参数表的创建、级联读取、原子更新与级联清理"""
    new_device = {
        "asset_no": "DEV-TEST-GPU99",
        "name": "测试-超算训练节点99",
        "category": "服务器",
        "location": "实训楼201-测试机柜A",
        "health_status": "HEALTHY",
        "borrow_status": "AVAILABLE",
        "specs": "2x Xeon, 512GB RAM, 8x RTX 4090",
        "detail": {
            "serial_number": "SN-TEST-2026-GPU99",
            "brand": "Dell",
            "model_name": "PowerEdge XE8545",
            "os_firmware": "Ubuntu 22.04 LTS",
            "mac_address": "00:50:56:AA:BB:CC",
            "management_ip": "192.168.10.99",
            "cpu_info": "2x AMD EPYC 7763 128核",
            "memory_info": "512GB DDR4 3200 ECC",
            "storage_info": "4x 3.84TB NVMe SSD",
            "gpu_info": "4x NVIDIA A100 80GB SXM4",
            "network_interfaces": "4x 100GE QSFP28 + 2x 10GE",
            "power_supply": "双路冗余 3000W",
            "purchase_date": "2026-05-01",
            "warranty_period": "2029-05-01",
            "supplier": "戴尔科技企业方案部",
            "extra_params": '{"cluster_role": "compute_worker"}',
        },
    }

    # 1. 创建包含完整硬件参数的设备
    create_res = client.post("/api/assets/", json=new_device)
    assert create_res.status_code == 201
    created = create_res.json()
    asset_id = created["id"]
    assert created["asset_no"] == "DEV-TEST-GPU99"
    assert created["detail"] is not None
    assert created["detail"]["serial_number"] == "SN-TEST-2026-GPU99"
    assert created["detail"]["management_ip"] == "192.168.10.99"
    assert created["detail"]["gpu_info"] == "4x NVIDIA A100 80GB SXM4"

    # 2. 单台详情获取与级联验证
    get_res = client.get(f"/api/assets/{asset_id}")
    assert get_res.status_code == 200
    got = get_res.json()
    assert got["detail"]["cpu_info"] == "2x AMD EPYC 7763 128核"
    assert got["detail"]["brand"] == "Dell"

    # 3. 更新主表与硬件参数
    patch_payload = {
        "name": "测试-超算训练节点99-已升配",
        "detail": {
            "memory_info": "1TB DDR4 3200 ECC",
            "management_ip": "192.168.10.199",
        },
    }
    patch_res = client.patch(f"/api/assets/{asset_id}", json=patch_payload)
    assert patch_res.status_code == 200
    patched = patch_res.json()
    assert patched["name"] == "测试-超算训练节点99-已升配"
    assert patched["detail"]["memory_info"] == "1TB DDR4 3200 ECC"
    assert patched["detail"]["management_ip"] == "192.168.10.199"
    # 原先的未修改字段保持完好
    assert patched["detail"]["serial_number"] == "SN-TEST-2026-GPU99"

    # 4. 删除设备并验证级联清理
    del_res = client.delete(f"/api/assets/{asset_id}")
    assert del_res.status_code == 204

    # 再次查询应返回 404
    get_after_del = client.get(f"/api/assets/{asset_id}")
    assert get_after_del.status_code == 404


def test_asset_tools_detail_and_add():
    """测试 Agent 工具库中的设备详情查询与新增设备工具"""
    from app.tools.asset_tools import get_asset_detail, add_asset, query_assets
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        # 1. 详情查询工具
        detail_res = get_asset_detail("DEV-SRV-201", db=db)
        assert detail_res["status"] == "success"
        assert detail_res["asset"]["asset_no"] == "DEV-SRV-201"
        assert detail_res["asset"]["detail"]["brand"] == "Dell"
        assert "RTX 4090" in detail_res["asset"]["detail"]["gpu_info"]

        # 2. 新增设备工具
        add_res = add_asset(
            asset_no="DEV-NET-999",
            name="测试核心万兆交换机99",
            category="网络设备",
            location="实训楼201-测试机柜B",
            specs="48口全光",
            brand="Huawei",
            model_name="CE6800-Test",
            management_ip="192.168.1.99",
            serial_number="SN-HW-TEST-999",
            db=db,
        )
        assert add_res["status"] == "success"
        assert add_res["asset"]["asset_no"] == "DEV-NET-999"

        # 3. 再次通过详情查询核验
        check_res = get_asset_detail("DEV-NET-999", db=db)
        assert check_res["status"] == "success"
        assert check_res["asset"]["detail"]["management_ip"] == "192.168.1.99"

        # 4. 清理测试添加的数据
        from app.db.models import Asset
        created_asset = db.query(Asset).filter(Asset.asset_no == "DEV-NET-999").first()
        if created_asset:
            db.delete(created_asset)
            db.commit()
    finally:
        db.close()


def test_asset_temperature_setting_and_health_linkage_api(client):
    """测试通过 REST API 录入与修改设定核心温度，验证动环探针遥测注入与健康状态智能联动"""
    # 1. 录入新设备并设定温度为 42.5℃ -> 自动联动判定为 OVERHEAT 状态
    create_payload = {
        "asset_no": "DEV-TEST-TEMP-88",
        "name": "高热AI训练卡集群88",
        "category": "服务器",
        "location": "实训楼201-机柜A01",
        "health_status": "HEALTHY",  # 即使初始选择 HEALTHY，设定 42.5℃ 亦自动联动修正为 OVERHEAT
        "custom_temperature": 42.5,
        "detail": {
            "model_name": "DGX-A100-Test",
            "custom_temperature": 42.5,
        },
    }
    create_res = client.post("/api/assets/", json=create_payload)
    assert create_res.status_code == 201
    created_data = create_res.json()
    asset_id = created_data["id"]
    assert created_data["health_status"] == "OVERHEAT"
    assert created_data["custom_temperature"] == 42.5
    assert created_data["telemetry_temperature"] == 42.5
    assert created_data["detail"]["custom_temperature"] == 42.5

    # 2. 修改设定温度至 38.6℃ -> 自动联动为 WARNING 状态
    patch_warn = client.patch(
        f"/api/assets/{asset_id}",
        json={"custom_temperature": 38.6},
    )
    assert patch_warn.status_code == 200
    warn_data = patch_warn.json()
    assert warn_data["health_status"] == "WARNING"
    assert warn_data["custom_temperature"] == 38.6
    assert warn_data["telemetry_temperature"] == 38.6

    # 3. 修改设定温度至 32.0℃ -> 自动联动为 HEALTHY 状态
    patch_healthy = client.patch(
        f"/api/assets/{asset_id}",
        json={"custom_temperature": 32.0},
    )
    assert patch_healthy.status_code == 200
    healthy_data = patch_healthy.json()
    assert healthy_data["health_status"] == "HEALTHY"
    assert healthy_data["custom_temperature"] == 32.0
    assert healthy_data["telemetry_temperature"] == 32.0

    # 4. 显式修改健康状态为 OFFLINE，温度保持环境室温且离线状态不被温度冲刷
    patch_offline = client.patch(
        f"/api/assets/{asset_id}",
        json={"health_status": "OFFLINE", "custom_temperature": 45.0},
    )
    assert patch_offline.status_code == 200
    offline_data = patch_offline.json()
    assert offline_data["health_status"] == "OFFLINE"
    assert offline_data["telemetry_temperature"] == 22.0

    # 5. 测试通过顶层 custom_temperature: None 显式清除自定义注入温度
    patch_clear = client.patch(
        f"/api/assets/{asset_id}",
        json={"custom_temperature": None, "health_status": "HEALTHY"},
    )
    assert patch_clear.status_code == 200
    cleared_data = patch_clear.json()
    assert cleared_data["custom_temperature"] is None
    assert cleared_data["health_status"] == "HEALTHY"
    assert cleared_data["telemetry_temperature"] == 31.5

    # 6. 测试使用 temperature 别名提交更新并自动联动 OVERHEAT
    patch_alias = client.patch(
        f"/api/assets/{asset_id}",
        json={"temperature": 41.8},
    )
    assert patch_alias.status_code == 200
    alias_data = patch_alias.json()
    assert alias_data["health_status"] == "OVERHEAT"
    assert alias_data["custom_temperature"] == 41.8
    assert alias_data["temperature"] == 41.8

    # 7. 测试直接更新 health_status 为 HEALTHY，验证设定温度与遥测自洽回落至 31.5℃
    patch_rollback = client.patch(
        f"/api/assets/{asset_id}",
        json={"health_status": "HEALTHY"},
    )
    assert patch_rollback.status_code == 200
    rollback_data = patch_rollback.json()
    assert rollback_data["health_status"] == "HEALTHY"
    assert rollback_data["custom_temperature"] == 31.5
    assert rollback_data["telemetry_temperature"] == 31.5

    # 8. 核验拓扑大盘接口数据准确映射
    topo_res = client.get("/api/assets/topology?room_code=ROOM-201")
    assert topo_res.status_code == 200
    topo_body = topo_res.json()
    # 验证大盘能正常聚合
    assert "summary" in topo_body

    # 9. 清理测试资源
    del_res = client.delete(f"/api/assets/{asset_id}")
    assert del_res.status_code == 204


def test_asset_temperature_boundaries_and_alias_api(client):
    """测试边界温度跃迁精度 (37.99/38.00/39.99/40.00) 与 temperature 别名创建"""
    # 1. 使用 temperature 别名字段在创建时指定边界温度 37.99℃ -> 判定为 HEALTHY
    create_payload = {
        "asset_no": "DEV-TEST-BOUND-99",
        "name": "边界温度测试节点99",
        "category": "服务器",
        "location": "实训楼201-机柜A01",
        "temperature": 37.99,
    }
    res1 = client.post("/api/assets/", json=create_payload)
    assert res1.status_code == 201
    d1 = res1.json()
    asset_id = d1["id"]
    assert d1["health_status"] == "HEALTHY"
    assert d1["custom_temperature"] == 38.0 or d1["custom_temperature"] == 37.99

    # 2. 调至临界点 38.00℃ -> 判定为 WARNING
    res2 = client.patch(f"/api/assets/{asset_id}", json={"custom_temperature": 38.00})
    assert res2.status_code == 200
    assert res2.json()["health_status"] == "WARNING"

    # 3. 调至临界点 39.99℃ -> 判定为 WARNING
    res3 = client.patch(f"/api/assets/{asset_id}", json={"custom_temperature": 39.99})
    assert res3.status_code == 200
    assert res3.json()["health_status"] == "WARNING"

    # 4. 调至超温红线 40.00℃ -> 判定为 OVERHEAT
    res4 = client.patch(f"/api/assets/{asset_id}", json={"custom_temperature": 40.00})
    assert res4.status_code == 200
    assert res4.json()["health_status"] == "OVERHEAT"

    # 5. 清理测试资源
    client.delete(f"/api/assets/{asset_id}")




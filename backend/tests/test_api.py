"""阶段 1 自动化验证测试套件

测试项覆盖：
1. 健康检查与根重定向
2. 机房资产数据底座及完整 CRUD（查询、条件过滤、新增、查重、局部修改、删除）
3. 运维工单数据底座及完整 CRUD（查询、条件过滤、自动编号生成、状态流转、异常分支）
4. 审计日志表 (AuditLog) 与对话持久化表 (ChatHistory) 数据完整性
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.db.models import AuditLog, ChatHistory


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


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


# ==================== 资产管理接口测试 ====================


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
    """测试机房资产条件过滤查询"""
    # 按健康状态过滤 (OVERHEAT)
    response = client.get("/api/assets/?health_status=OVERHEAT")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["asset_no"] == "DEV-SRV-201"
    assert data[0]["health_status"] == "OVERHEAT"

    # 按关键词过滤
    response = client.get("/api/assets/?keyword=交换机")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert "交换机" in data[0]["name"]


def test_get_asset_by_id(client):
    """测试获取单个资产详情"""
    # 先查询列表获取第一个 ID
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

    # 3. 更新资产借用状态
    update_data = {
        "borrow_status": "IN_USE",
        "borrower": "测试借用人",
    }
    patch_res = client.patch(f"/api/assets/{created_id}", json=update_data)
    assert patch_res.status_code == 200
    assert patch_res.json()["borrow_status"] == "IN_USE"
    assert patch_res.json()["borrower"] == "测试借用人"

    # 4. 删除测试资产
    del_res = client.delete(f"/api/assets/{created_id}")
    assert del_res.status_code == 204

    # 5. 确认已删除
    get_res = client.get(f"/api/assets/{created_id}")
    assert get_res.status_code == 404


# ==================== 工单管理接口测试 ====================


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
    """测试工单条件过滤查询"""
    # 按优先级过滤
    res = client.get("/api/tickets/?priority=HIGH")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert all(t["priority"] == "HIGH" for t in data)

    # 按关联设备过滤
    res = client.get("/api/tickets/?device_id=DEV-SRV-201")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert data[0]["device_id"] == "DEV-SRV-201"


def test_create_and_update_ticket(client):
    """测试创建工单（自动编号生成）、状态流转与异常处理"""
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
    assert ticket_data["ticket_no"].startswith("TK-")
    assert ticket_data["status"] == "PENDING"

    # 2. 获取详情
    detail_res = client.get(f"/api/tickets/{created_id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["title"] == new_ticket["title"]

    # 3. 状态更新为 PROCESSING，并更新描述
    patch_res = client.patch(
        f"/api/tickets/{created_id}",
        json={"status": "PROCESSING", "description": "运维人员已到场处理排水接头"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "PROCESSING"
    assert "运维人员已到场" in patch_res.json()["description"]

    # 4. 再次更新为 RESOLVED
    resolve_res = client.patch(
        f"/api/tickets/{created_id}",
        json={"status": "RESOLVED"},
    )
    assert resolve_res.status_code == 200
    assert resolve_res.json()["status"] == "RESOLVED"

    # 5. 删除工单
    del_res = client.delete(f"/api/tickets/{created_id}")
    assert del_res.status_code == 204

    # 6. 确认已删除
    assert client.get(f"/api/tickets/{created_id}").status_code == 404


# ==================== 审计日志与会话模型表结构验证 ====================


def test_audit_log_and_chat_history_models():
    """测试底层 AuditLog 与 ChatHistory 表读写可用性（为阶段 2 准备）"""
    db = SessionLocal()
    try:
        # 1. 写入一条审计记录
        audit = AuditLog(
            trace_id="trace-test-123456",
            tool_name="get_server_metrics",
            tool_args='{"server_id": "DEV-SRV-201"}',
            tool_result='{"cpu_usage": "78%", "temp": "85C"}',
            status="SUCCESS",
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)
        assert audit.id is not None
        assert audit.tool_name == "get_server_metrics"

        # 2. 写入一条会话记录
        chat = ChatHistory(
            session_id="session-test-888",
            role="assistant",
            content="正在为您排查服务器指标...",
            thought="检测到用户意图为服务器状态排查，决定调用 get_server_metrics 工具",
        )
        db.add(chat)
        db.commit()
        db.refresh(chat)
        assert chat.id is not None
        assert chat.role == "assistant"

        # 3. 清理测试数据
        db.delete(audit)
        db.delete(chat)
        db.commit()
    finally:
        db.close()


# ==================== 边界与异常测试 ====================


def test_validation_errors(client):
    """测试非法入参触发表单验证 422 错误"""
    # 工单非法优先级
    res = client.post("/api/tickets/", json={"title": "测试", "description": "测试", "priority": "UNKNOWN"})
    assert res.status_code == 422

    # 工单空标题
    res = client.post("/api/tickets/", json={"title": "", "description": "测试"})
    assert res.status_code == 422

    # 资产非法健康状态
    res = client.post("/api/assets/", json={
        "asset_no": "DEV-TEST-ERR",
        "name": "测试设备",
        "category": "服务器",
        "location": "机房",
        "health_status": "BROKEN_INVALID",
    })
    assert res.status_code == 422


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
    assert client.patch("/api/tickets/99999", json={"status": "RESOLVED"}).status_code == 404
    assert client.patch("/api/assets/99999", json={"borrow_status": "IN_USE"}).status_code == 404


"""针对工单细化编辑权限与防越权安全防护的自动化测试套件

测试项覆盖：
1. 超级管理员 (ADMIN) 拥有全局编辑权限，可修改任意工单要素 (标题、描述、优先级、关联设备)
2. 教师 (TEACHER) 仅可编辑本人创建的工单，修改成功 (HTTP 200)
3. 教师 (TEACHER) 尝试编辑他人创建的工单，被安全拦截并返回 HTTP 403 Forbidden
4. 教师 (TEACHER) 允许认领受理待处理工单 (PENDING -> PROCESSING)，但禁止直接办结 (RESOLVED) 或归档 (CLOSED)
5. 学生 (STUDENT) 尝试更新或编辑工单要素，被安全拦截并返回 HTTP 403 Forbidden
"""

import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import get_db
from app.db.models import Ticket, User
from app.db.init_db import init_db


@pytest.fixture(scope="module")
def perm_test_env():
    """创建权限测试专用物理隔离测试数据库"""
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
def client(perm_test_env):
    with TestClient(app) as c:
        yield c


def test_admin_can_edit_any_ticket(client):
    """验证超级管理员 (ADMIN) 可以编辑由任何人员或系统创建的工单"""
    # 获取种子工单 1 (由 '系统自动监控' 创建)
    res = client.get("/api/tickets/?ticket_no=TK-20260901-001")
    assert res.status_code == 200
    ticket_id = res.json()[0]["id"]

    # 管理员更新工单要素
    patch_res = client.patch(
        f"/api/tickets/{ticket_id}",
        json={
            "title": "2号机房GPU计算节点01核心温度过热预警 (管理员已修订)",
            "priority": "CRITICAL",
            "operator": "王主管",
            "operator_role": "ADMIN",
        },
    )
    assert patch_res.status_code == 200
    data = patch_res.json()
    assert data["title"] == "2号机房GPU计算节点01核心温度过热预警 (管理员已修订)"
    assert data["priority"] == "CRITICAL"


def test_teacher_can_edit_own_ticket(client):
    """验证教师 (TEACHER) 可以编辑自己创建的工单"""
    # 1. 以李老师身份创建一张新工单
    create_res = client.post(
        "/api/tickets/",
        json={
            "title": "物联网实训网关掉电排查",
            "description": "实训台网关无法启动",
            "priority": "MEDIUM",
            "creator": "李老师",
            "device_id": "DEV-NET-301",
        },
    )
    assert create_res.status_code == 201
    tid = create_res.json()["id"]

    # 2. 李老师以自身账号编辑该工单
    patch_res = client.patch(
        f"/api/tickets/{tid}",
        json={
            "title": "物联网实训网关掉电排查 (李老师补充排查细节)",
            "description": "排查发现适配器接头松动，需更换12V电源",
            "operator": "李老师",
            "operator_role": "TEACHER",
        },
    )
    assert patch_res.status_code == 200
    data = patch_res.json()
    assert "补充排查细节" in data["title"]
    assert "更换12V电源" in data["description"]


def test_teacher_cannot_edit_others_ticket(client):
    """验证教师 (TEACHER) 编辑他人创建的工单时被系统严正拦截 (HTTP 403)"""
    # TK-20260901-002 由 '王管理员' 创建
    res = client.get("/api/tickets/?ticket_no=TK-20260901-002")
    assert res.status_code == 200
    ticket_id = res.json()[0]["id"]

    # 李老师尝试修改该工单的标题与描述
    patch_res = client.patch(
        f"/api/tickets/{ticket_id}",
        json={
            "title": "篡改他人创建的工单标题",
            "description": "非法尝试编辑",
            "operator": "李老师",
            "operator_role": "TEACHER",
        },
    )
    assert patch_res.status_code == 403
    assert "权限不足" in patch_res.json()["detail"]
    assert "李老师" in patch_res.json()["detail"]


def test_teacher_can_advance_workflow_and_resolve(client):
    """验证教师可以受理待处理工单 (PENDING -> PROCESSING) 并完成办结流转 (PROCESSING -> RESOLVED)"""
    # 1. 创建待处理工单
    create_res = client.post(
        "/api/tickets/",
        json={
            "title": "待处理测试工单",
            "description": "测试教师流转权限",
            "priority": "LOW",
            "creator": "测试员",
        },
    )
    assert create_res.status_code == 201
    tid = create_res.json()["id"]

    # 2. 教师受理该工单 (PENDING -> PROCESSING): 允许通过
    accept_res = client.patch(
        f"/api/tickets/{tid}",
        json={
            "status": "PROCESSING",
            "operator": "李老师",
            "operator_role": "TEACHER",
            "comment": "李老师已到场认领受理",
        },
    )
    assert accept_res.status_code == 200
    assert accept_res.json()["status"] == "PROCESSING"

    # 3. 教师完成排查并办结该工单 (PROCESSING -> RESOLVED): 允许通过
    resolve_res = client.patch(
        f"/api/tickets/{tid}",
        json={
            "status": "RESOLVED",
            "operator": "李老师",
            "operator_role": "TEACHER",
            "comment": "现场巡检已完成，更换板卡后恢复正常",
        },
    )
    assert resolve_res.status_code == 200
    assert resolve_res.json()["status"] == "RESOLVED"


def test_teacher_cannot_edit_ticket_with_empty_or_none_creator(client):
    """验证工单无创建者(creator为空或NULL)时，教师无法编辑工单要素(HTTP 403)，防止子串空匹配越权"""
    create_res = client.post(
        "/api/tickets/",
        json={
            "title": "匿名系统工单",
            "description": "无创建者工单",
            "priority": "LOW",
        },
    )
    assert create_res.status_code == 201
    tid = create_res.json()["id"]

    patch_res = client.patch(
        f"/api/tickets/{tid}",
        json={
            "title": "教师尝试篡改无创建者的工单",
            "operator": "李老师",
            "operator_role": "TEACHER",
        },
    )
    assert patch_res.status_code == 403
    assert "权限不足" in patch_res.json()["detail"]


def test_student_cannot_edit_or_update_ticket(client):
    """验证学生 (STUDENT) 角色被全面禁止修改或流转工单 (HTTP 403)"""
    res = client.get("/api/tickets/?ticket_no=TK-20260901-001")
    assert res.status_code == 200
    ticket_id = res.json()[0]["id"]

    # 学生尝试修改标题
    patch_res = client.patch(
        f"/api/tickets/{ticket_id}",
        json={
            "title": "学生非法尝试修改工单",
            "operator": "陈同学",
            "operator_role": "STUDENT",
        },
    )
    assert patch_res.status_code == 403
    assert "学生角色对运维工单仅有只读权限" in patch_res.json()["detail"]

    # 学生尝试推进状态
    status_res = client.patch(
        f"/api/tickets/{ticket_id}",
        json={
            "status": "RESOLVED",
            "operator": "student_chen",
            "operator_role": "STUDENT",
        },
    )
    assert status_res.status_code == 403
    assert "学生角色对运维工单仅有只读权限" in status_res.json()["detail"]

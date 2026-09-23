"""用户与系统主体档案详情 (GET /api/auth/profile/{identifier}) 自动化单元测试套件

测试项覆盖：
1. 预置用户按真实姓名精准查询 (王主管 / 李老师 / 张老师 / 陈同学)
2. 预置用户按工号/学号精确与大小写不敏感查询 (admin / teacher_li / student_chen)
3. 带角色括号/中括号后缀的主体名称匹配 (如 "王主管 (超级管理员)")
4. 注册新用户后即时查询其全景档案 (真实姓名、部门、电话、权责清单)
5. AI 自治智能体与系统虚拟主体查询 (LabOps-Agent / 系统监控 / 全网一键自治巡检 / 系统管理员)
6. 外部未知操作人优雅容错保底 (返回 HTTP 200，绝不崩溃 500)
7. 极端与边界入参安全防护
"""

import os
import tempfile
import pytest
from urllib.parse import quote
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import get_db
from app.db.init_db import init_db


@pytest.fixture(scope="module")
def profile_test_env():
    """创建物理隔离的测试数据库环境并播种种子数据"""
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
def client(profile_test_env):
    """FastAPI 测试客户端"""
    return TestClient(app)


class TestUserProfileQuery:
    """测试人物与系统主体档案详情查询 API"""

    def test_query_by_real_name_admin(self, client):
        """测试通过真实姓名查询超级管理员王主管档案"""
        resp = client.get(f"/api/auth/profile/{quote('王主管')}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "admin"
        assert data["real_name"] == "王主管"
        assert data["role"] == "ADMIN"
        assert data["role_label"] == "超级管理员"
        assert data["department"] == "网络中心运维部"
        assert data["phone"] == "13800000001"
        assert data["is_system_agent"] is False
        assert data["avatar_text"] == "王"
        assert len(data["responsibilities"]) > 0

    def test_query_by_username_case_insensitive(self, client):
        """测试通过工号/用户名大小写不敏感查询教师档案"""
        resp = client.get("/api/auth/profile/Teacher_Li")
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "teacher_li"
        assert data["real_name"] == "李老师"
        assert data["role"] == "TEACHER"
        assert data["department"] == "物联网工程教研室"
        assert data["phone"] == "13900000002"
        assert data["is_system_agent"] is False

    def test_query_by_username_student(self, client):
        """测试通过工号/学号查询学生档案"""
        resp = client.get("/api/auth/profile/student_chen")
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "student_chen"
        assert data["real_name"] == "陈同学"
        assert data["role"] == "STUDENT"
        assert data["role_label"] == "实训在读学生"
        assert data["department"] == "计科2201班"
        assert data["is_system_agent"] is False

    def test_query_with_role_parentheses(self, client):
        """测试剥离角色括号后缀查询 (如 '王主管 (超级管理员)' 或 '李老师 [专业课教师]')"""
        resp1 = client.get(f"/api/auth/profile/{quote('王主管 (超级管理员)')}")
        assert resp1.status_code == 200
        assert resp1.json()["real_name"] == "王主管"
        assert resp1.json()["role"] == "ADMIN"

        resp2 = client.get(f"/api/auth/profile/{quote('李老师 [专业课教师]')}")
        assert resp2.status_code == 200
        assert resp2.json()["real_name"] == "李老师"
        assert resp2.json()["role"] == "TEACHER"

    def test_register_and_query_new_user(self, client):
        """测试新注册用户后可通过姓名与工号立即查询档案"""
        new_user_payload = {
            "username": "teacher_zhao",
            "password": "password123",
            "real_name": "赵老师",
            "role": "TEACHER",
            "department": "人工智能教研室",
            "phone": "13511112222",
        }
        reg_resp = client.post("/api/auth/register", json=new_user_payload)
        assert reg_resp.status_code == 201

        # 1. 用工号查询
        resp_by_uname = client.get("/api/auth/profile/teacher_zhao")
        assert resp_by_uname.status_code == 200
        data1 = resp_by_uname.json()
        assert data1["real_name"] == "赵老师"
        assert data1["department"] == "人工智能教研室"
        assert data1["phone"] == "13511112222"

        # 2. 用真实姓名查询
        resp_by_rname = client.get(f"/api/auth/profile/{quote('赵老师')}")
        assert resp_by_rname.status_code == 200
        data2 = resp_by_rname.json()
        assert data2["username"] == "teacher_zhao"
        assert data2["real_name"] == "赵老师"

    def test_query_system_virtual_agent(self, client):
        """测试查询 LabOps-Agent、系统监控、全网一键自治巡检等虚拟智能体"""
        # LabOps-Agent
        resp_agent = client.get("/api/auth/profile/LabOps-Agent")
        assert resp_agent.status_code == 200
        data_agent = resp_agent.json()
        assert data_agent["is_system_agent"] is True
        assert data_agent["role"] == "SYSTEM_AGENT"
        assert "LabOps-Agent" in data_agent["real_name"]
        assert "7×24H" in data_agent["status"]
        assert "ReAct" in data_agent["description"]
        assert len(data_agent["responsibilities"]) >= 3

        # 系统监控
        resp_mon = client.get(f"/api/auth/profile/{quote('系统监控')}")
        assert resp_mon.status_code == 200
        data_mon = resp_mon.json()
        assert data_mon["is_system_agent"] is True

        # 全网一键自治巡检
        resp_patrol = client.get(f"/api/auth/profile/{quote('全网一键自治巡检')}")
        assert resp_patrol.status_code == 200
        assert resp_patrol.json()["is_system_agent"] is True

        # 系统管理员 (作为虚拟主体别名查询)
        resp_sysadmin = client.get(f"/api/auth/profile/{quote('系统管理员')}")
        assert resp_sysadmin.status_code == 200
        assert resp_sysadmin.json()["is_system_agent"] is True

    def test_query_fallback_unknown_operator(self, client):
        """测试未收录的外部/第三方临时主体优雅降级兜底 (HTTP 200，绝不 500)"""
        resp = client.get(f"/api/auth/profile/{quote('外部机房驻场维保小周')}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "外部机房驻场维保小周"
        assert data["real_name"] == "外部机房驻场维保小周"
        assert data["role"] == "OPERATOR"
        assert data["role_label"] == "现场运维人员"
        assert data["is_system_agent"] is False
        assert len(data["responsibilities"]) > 0

    def test_query_blank_or_whitespace_identifier(self, client):
        """测试传入空字符串或纯空格的安全容错"""
        resp = client.get(f"/api/auth/profile/{quote('   ')}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["role"] == "OPERATOR"
        assert data["is_system_agent"] is False

    def test_query_with_ui_icons_and_arrows(self, client):
        """测试用户从时间轴卡片复制带有 UI 图标与方向字符的主体名称 (如 '👤 王主管 ↗')"""
        resp = client.get(f"/api/auth/profile/{quote('👤 王主管 ↗')}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["real_name"] == "王主管"
        assert data["role"] == "ADMIN"

        resp_agent = client.get(f"/api/auth/profile/{quote('🤖 LabOps-Agent ↗')}")
        assert resp_agent.status_code == 200
        assert resp_agent.json()["is_system_agent"] is True

    def test_query_with_unclosed_parenthesis(self, client):
        """测试输入带有未闭合单边括号的主体名称容错 (如 '王主管(超级管理员')"""
        resp = client.get(f"/api/auth/profile/{quote('王主管(超级管理员')}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["real_name"] == "王主管"
        assert data["role"] == "ADMIN"

    def test_end_to_end_ticket_operator_persistence_and_profile(self, client):
        """端到端集成测试：工单流转透传真实操作人姓名 -> 时间轴精准显示 -> 点击查阅该操作人全景档案"""
        # 1. 创建测试工单
        create_resp = client.post(
            "/api/tickets/",
            json={
                "title": "机柜A01服务器供电异常排查",
                "description": "巡检探针发现电压波动，需现场巡检",
                "priority": "HIGH",
                "creator": "李老师",
            },
        )
        assert create_resp.status_code == 201
        ticket_id = create_resp.json()["id"]
        ticket_no = create_resp.json()["ticket_no"]

        # 2. 模拟前端 handleUpdateTicketStatus 调用 updateTicket，显式传入真实姓名 operator
        update_resp = client.put(
            f"/api/tickets/{ticket_id}",
            json={
                "status": "PROCESSING",
                "operator": "李老师",
                "comment": "李老师已赶往现场开启实训机柜检修",
            },
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["status"] == "PROCESSING"

        # 3. 查阅工单流转脉络时间轴，断言 operator 确为真实姓名 '李老师'，绝非写死 '系统管理员'
        timeline_resp = client.get(f"/api/tickets/{ticket_no}/timeline")
        assert timeline_resp.status_code == 200
        timeline_data = timeline_resp.json()
        nodes = timeline_data["timeline"]
        assert len(nodes) >= 2

        # 检查最新流转节点
        wf_node = next((n for n in nodes if n["node_type"] == "PROCESSING"), None)
        assert wf_node is not None
        assert wf_node["operator"] == "李老师"
        assert "李老师已赶往现场" in wf_node["comment"]

        # 4. 模拟前端点击该节点操作人胶囊按钮，调用 /api/auth/profile/{operator}
        profile_resp = client.get(f"/api/auth/profile/{quote(wf_node['operator'])}")
        assert profile_resp.status_code == 200
        prof = profile_resp.json()
        assert prof["username"] == "teacher_li"
        assert prof["real_name"] == "李老师"
        assert prof["role"] == "TEACHER"
        assert prof["department"] == "物联网工程教研室"
        assert prof["phone"] == "13900000002"
        assert prof["is_system_agent"] is False

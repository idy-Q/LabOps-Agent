"""用户认证与权限控制自动化测试套件

测试项覆盖：
1. SHA-256 加盐密码哈希计算与比对有效性
2. 数据库种子用户（4位典型用户）初始化完整性与凭证校验
3. 典型用户展示端点 (GET /api/auth/demo-users) 数据契约
4. 教师与学生免口令正常注册 (POST /api/auth/register)
5. 用户名/工号重复注册安全拦截 (HTTP 400)
6. 管理员注册未填激活码拦截 (HTTP 400)
7. 管理员注册错误激活码拦截 (HTTP 400)
8. 管理员注册正确激活码 (admin666) 成功放行 (HTTP 201)
9. 正确凭证登录成功 (POST /api/auth/login)
10. 错误密码登录拦截 (HTTP 401)
11. 不存在用户登录拦截 (HTTP 401)
12. 请求体验证规则拦截（密码过短、工号过短、非法字段）
"""

import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import Base, get_db
from app.db.models import User, hash_password, verify_password
from app.db.init_db import init_db


@pytest.fixture(scope="module")
def auth_test_env():
    """创建物理隔离的测试数据库环境"""
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
def client(auth_test_env):
    """FastAPI 测试客户端"""
    return TestClient(app)


class TestPasswordSecurity:
    """密码安全与哈希算法测试"""

    def test_password_hash_and_verify(self):
        pwd = "admin666"
        hashed = hash_password(pwd)

        assert isinstance(hashed, str)
        assert len(hashed) == 64  # SHA-256 十六进制输出为 64 个字符

        # 确定性验证
        assert hash_password(pwd) == hashed

        # 正确与错误密码比对
        assert verify_password("admin666", hashed) is True
        assert verify_password("wrong_password", hashed) is False
        assert verify_password("admin888", hashed) is False


class TestSeedUsers:
    """初始种子用户测试"""

    def test_seed_users_presence(self, auth_test_env):
        session_factory = auth_test_env["session_factory"]
        db = session_factory()
        try:
            users = db.query(User).all()
            user_map = {u.username: u for u in users}

            # 验证 4 位典型用户必须存在
            assert "admin" in user_map
            assert "teacher_li" in user_map
            assert "teacher_zhang" in user_map
            assert "student_chen" in user_map

            # 验证管理员角色与初始密码
            admin_user = user_map["admin"]
            assert admin_user.role == "ADMIN"
            assert admin_user.real_name == "王主管"
            assert admin_user.department == "网络中心运维部"
            assert verify_password("admin666", admin_user.password_hash) is True

            # 验证教师与学生初始密码
            assert verify_password("123456", user_map["teacher_li"].password_hash) is True
            assert verify_password("123456", user_map["student_chen"].password_hash) is True
            assert user_map["student_chen"].role == "STUDENT"
        finally:
            db.close()


class TestAuthAPI:
    """认证 API 端点集成测试"""

    def test_get_demo_users(self, client):
        resp = client.get("/api/auth/demo-users")
        assert resp.status_code == 200
        data = resp.json()

        assert isinstance(data, list)
        assert len(data) == 4

        usernames = [u["username"] for u in data]
        assert "admin" in usernames
        assert "teacher_li" in usernames
        assert "teacher_zhang" in usernames
        assert "student_chen" in usernames

        # 验证包含快捷演示凭证与角色标签
        admin_item = next(u for u in data if u["username"] == "admin")
        assert admin_item["default_password"] == "admin666"
        assert admin_item["role_label"] == "超级管理员"

    def test_register_teacher_success(self, client):
        payload = {
            "username": "teacher_wang",
            "password": "password123",
            "real_name": "王老师",
            "role": "TEACHER",
            "department": "软件工程教研室",
            "phone": "13912345678",
        }
        resp = client.post("/api/auth/register", json=payload)
        assert resp.status_code == 201
        data = resp.json()

        assert data["username"] == "teacher_wang"
        assert data["real_name"] == "王老师"
        assert data["role"] == "TEACHER"
        assert data["department"] == "软件工程教研室"
        assert "password" not in data
        assert "password_hash" not in data

        # 注册后立即登录校验
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "teacher_wang", "password": "password123"},
        )
        assert login_resp.status_code == 200
        assert login_resp.json()["username"] == "teacher_wang"

    def test_register_student_success(self, client):
        payload = {
            "username": "student_liu",
            "password": "password123",
            "real_name": "刘同学",
            "role": "STUDENT",
            "department": "计科2202班",
        }
        resp = client.post("/api/auth/register", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["role"] == "STUDENT"
        assert data["real_name"] == "刘同学"

    def test_register_duplicate_username_failure(self, client):
        payload = {
            "username": "teacher_li",  # 已存在的种子工号
            "password": "password123",
            "real_name": "李老师二号",
            "role": "TEACHER",
            "department": "物联网工程教研室",
        }
        resp = client.post("/api/auth/register", json=payload)
        assert resp.status_code == 400
        assert "已经存在" in resp.json()["detail"]

    def test_register_admin_without_code_failure(self, client):
        payload = {
            "username": "fake_admin",
            "password": "password123",
            "real_name": "假管理员",
            "role": "ADMIN",
            "department": "网络中心",
            # admin_code 为空
        }
        resp = client.post("/api/auth/register", json=payload)
        assert resp.status_code == 400
        assert "激活口令" in resp.json()["detail"]

    def test_register_admin_with_wrong_code_failure(self, client):
        payload = {
            "username": "fake_admin_2",
            "password": "password123",
            "real_name": "假管理员2",
            "role": "ADMIN",
            "department": "网络中心",
            "admin_code": "admin888",  # 错误口令
        }
        resp = client.post("/api/auth/register", json=payload)
        assert resp.status_code == 400
        assert "激活口令错误" in resp.json()["detail"]

    def test_register_admin_with_correct_code_success(self, client):
        payload = {
            "username": "sec_admin",
            "password": "secpassword666",
            "real_name": "赵安全员",
            "role": "ADMIN",
            "department": "网络中心安全组",
            "admin_code": "admin666",  # 正确口令
        }
        resp = client.post("/api/auth/register", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == "sec_admin"
        assert data["role"] == "ADMIN"

        # 登录验证
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "sec_admin", "password": "secpassword666"},
        )
        assert login_resp.status_code == 200

    def test_login_success(self, client):
        # 使用种子管理员测试
        resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin666"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "admin"
        assert data["role"] == "ADMIN"
        assert data["real_name"] == "王主管"

    def test_login_wrong_password_failure(self, client):
        resp = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "wrongpassword"},
        )
        assert resp.status_code == 401
        assert "不存在或" in resp.json()["detail"]

    def test_login_nonexistent_user_failure(self, client):
        resp = client.post(
            "/api/auth/login",
            json={"username": "nobody_exists", "password": "password123"},
        )
        assert resp.status_code == 401
        assert "不存在或" in resp.json()["detail"]

    def test_register_validation_constraints(self, client):
        # 密码过短 (< 6)
        resp = client.post(
            "/api/auth/register",
            json={
                "username": "short_user",
                "password": "123",
                "real_name": "短密码用户",
                "role": "TEACHER",
                "department": "教研室",
            },
        )
        assert resp.status_code == 422

        # 工号过短 (< 2)
        resp = client.post(
            "/api/auth/register",
            json={
                "username": "x",
                "password": "password123",
                "real_name": "短工号用户",
                "role": "TEACHER",
                "department": "教研室",
            },
        )
        assert resp.status_code == 422

        # 非法外来字段 (extra='forbid')
        resp = client.post(
            "/api/auth/register",
            json={
                "username": "extra_user",
                "password": "password123",
                "real_name": "外来字段用户",
                "role": "TEACHER",
                "department": "教研室",
                "malicious_field": "hacked",
            },
        )
        assert resp.status_code == 422

    def test_register_duplicate_username_case_insensitive(self, client):
        """验证工号查重具备大小写不敏感防御，防止 ADMIN 或 Teacher_Li 恶意碰撞"""
        payload = {
            "username": "TEACHER_LI",  # 大写碰撞已有 teacher_li
            "password": "password123",
            "real_name": "李老师大写伪造",
            "role": "TEACHER",
            "department": "物联网工程教研室",
        }
        resp = client.post("/api/auth/register", json=payload)
        assert resp.status_code == 400
        assert "已经存在" in resp.json()["detail"]

    def test_login_username_case_insensitive(self, client):
        """验证用户登录支持工号大小写容错 (如 ADMIN 可正常登录 admin 账号)"""
        resp = client.post(
            "/api/auth/login",
            json={"username": "ADMIN", "password": "admin666"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "admin"
        assert data["role"] == "ADMIN"

    def test_register_phone_whitespace_normalization(self, client):
        """验证空白字符手机号自动规整为 None，杜绝数据库空字符串污染"""
        payload = {
            "username": "teacher_blankphone",
            "password": "password123",
            "real_name": "空白电话老师",
            "role": "TEACHER",
            "department": "计算机系",
            "phone": "   ",
        }
        resp = client.post("/api/auth/register", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["phone"] is None


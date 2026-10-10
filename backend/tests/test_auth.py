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
            "teacher_code": "teacher666",
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

    def test_register_teacher_without_code_failure(self, client):
        payload = {
            "username": "fake_teacher",
            "password": "password123",
            "real_name": "假教师",
            "role": "TEACHER",
            "department": "物联网教研室",
        }
        resp = client.post("/api/auth/register", json=payload)
        assert resp.status_code == 400
        assert "教师专属安全激活口令" in resp.json()["detail"]

    def test_register_teacher_with_wrong_code_failure(self, client):
        payload = {
            "username": "fake_teacher_2",
            "password": "password123",
            "real_name": "假教师2",
            "role": "TEACHER",
            "department": "物联网教研室",
            "teacher_code": "wrong_code",
        }
        resp = client.post("/api/auth/register", json=payload)
        assert resp.status_code == 400
        assert "教师专属安全激活口令" in resp.json()["detail"]

    def test_register_teacher_with_activation_code_alias_success(self, client):
        payload = {
            "username": "teacher_sun",
            "password": "password123",
            "real_name": "孙老师",
            "role": "TEACHER",
            "department": "网络工程教研室",
            "activation_code": "teacher666",
        }
        resp = client.post("/api/auth/register", json=payload)
        assert resp.status_code == 201
        assert resp.json()["role"] == "TEACHER"

    def test_register_admin_with_activation_code_alias_success(self, client):
        payload = {
            "username": "admin_zhao",
            "password": "password123",
            "real_name": "赵主管",
            "role": "ADMIN",
            "department": "实验中心主任室",
            "activation_code": "admin666",
        }
        resp = client.post("/api/auth/register", json=payload)
        assert resp.status_code == 201
        assert resp.json()["role"] == "ADMIN"

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
            "teacher_code": "teacher666",
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
            "teacher_code": "teacher666",
        }
        resp = client.post("/api/auth/register", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["phone"] is None


class TestUserProfileAndChangePassword:
    """用户资料更新与自主修改密码自动化测试"""

    def test_update_user_profile_success(self, client):
        """测试更新用户真实姓名、联系电话与所属部门"""
        payload = {
            "real_name": "陈志远同学",
            "phone": "13799998888",
            "department": "计科2201卓越工程师班",
        }
        resp = client.put("/api/auth/profile/student_chen", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "student_chen"
        assert data["real_name"] == "陈志远同学"
        assert data["phone"] == "13799998888"
        assert data["department"] == "计科2201卓越工程师班"

        # 查验 GET profile 端点同步反映最新档案
        get_resp = client.get("/api/auth/profile/student_chen")
        assert get_resp.status_code == 200
        get_data = get_resp.json()
        assert get_data["real_name"] == "陈志远同学"
        assert get_data["department"] == "计科2201卓越工程师班"

    def test_update_user_profile_not_found(self, client):
        """测试更新不存在的用户返回 HTTP 404"""
        resp = client.put(
            "/api/auth/profile/non_existent_user_404",
            json={"real_name": "虚构人物"},
        )
        assert resp.status_code == 404
        assert "不存在" in resp.json()["detail"]

    def test_change_password_lifecycle(self, client):
        """测试修改密码端点生命周期：验证旧密、更新新密、旧密失效、新密登录成功"""
        # 1. 注册测试用户
        reg_payload = {
            "username": "pwd_user_01",
            "password": "init_pwd_123",
            "real_name": "密码测试员",
            "role": "STUDENT",
            "department": "实训测试班",
        }
        reg_resp = client.post("/api/auth/register", json=reg_payload)
        assert reg_resp.status_code == 201

        # 2. 尝试使用错误旧密码修改 -> HTTP 400
        fail_resp = client.put(
            "/api/auth/change-password",
            json={
                "username": "pwd_user_01",
                "old_password": "wrong_old_pwd",
                "new_password": "brand_new_pwd_456",
            },
        )
        assert fail_resp.status_code == 400
        assert "原密码" in fail_resp.json()["detail"]

        # 3. 尝试新密码少于6位 -> HTTP 422
        short_resp = client.put(
            "/api/auth/change-password",
            json={
                "username": "pwd_user_01",
                "old_password": "init_pwd_123",
                "new_password": "123",
            },
        )
        assert short_resp.status_code == 422

        # 4. 正确修改密码 -> HTTP 200
        ok_resp = client.put(
            "/api/auth/change-password",
            json={
                "username": "pwd_user_01",
                "old_password": "init_pwd_123",
                "new_password": "brand_new_pwd_456",
            },
        )
        assert ok_resp.status_code == 200
        assert "成功" in ok_resp.json()["message"]

        # 5. 旧密码登录被拒 -> HTTP 401
        old_login = client.post(
            "/api/auth/login",
            json={"username": "pwd_user_01", "password": "init_pwd_123"},
        )
        assert old_login.status_code == 401

        # 6. 新密码登录成功 -> HTTP 200
        new_login = client.post(
            "/api/auth/login",
            json={"username": "pwd_user_01", "password": "brand_new_pwd_456"},
        )
        assert new_login.status_code == 200
        assert new_login.json()["username"] == "pwd_user_01"

    def test_change_password_not_found(self, client):
        """测试对不存在用户修改密码返回 HTTP 404"""
        resp = client.put(
            "/api/auth/change-password",
            json={
                "username": "non_existent_999",
                "old_password": "old_pass_123",
                "new_password": "new_pass_123",
            },
        )
        assert resp.status_code == 404

    def test_update_user_profile_case_insensitive_and_clear_phone(self, client):
        """测试大小写不敏感工号更新以及将电话置为空白字符串时自动清洗为 None"""
        resp = client.put(
            "/api/auth/profile/STUDENT_CHEN",
            json={
                "real_name": "陈志远(已更名)",
                "phone": "   ",
                "department": "计算机科学与技术系",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "student_chen"
        assert data["real_name"] == "陈志远(已更名)"
        assert data["phone"] == "暂未登记"

    def test_change_password_case_insensitive_username(self, client):
        """测试修改密码支持工号大小写不敏感容错"""
        # 使用大写工号 PWD_USER_01 再次修改密码
        resp = client.put(
            "/api/auth/change-password",
            json={
                "username": "PWD_USER_01",
                "old_password": "brand_new_pwd_456",
                "new_password": "another_new_pwd_789",
            },
        )
        assert resp.status_code == 200
        assert "成功" in resp.json()["message"]

        # 验证新密码登录成功
        login_resp = client.post(
            "/api/auth/login",
            json={"username": "pwd_user_01", "password": "another_new_pwd_789"},
        )
        assert login_resp.status_code == 200

    def test_update_user_profile_forbid_extra_fields(self, client):
        """测试更新用户资料接口禁止传递非定义字段 (防篡改注入)"""
        resp = client.put(
            "/api/auth/profile/student_chen",
            json={
                "real_name": "陈同学",
                "role": "ADMIN",  # 禁止越权提升角色
            },
        )
        assert resp.status_code == 422

    def test_change_password_forbid_extra_fields(self, client):
        """测试修改密码接口禁止传递非定义字段"""
        resp = client.put(
            "/api/auth/change-password",
            json={
                "username": "student_chen",
                "old_password": "any",
                "new_password": "anypassword123",
                "is_admin": True,
            },
        )
        assert resp.status_code == 422



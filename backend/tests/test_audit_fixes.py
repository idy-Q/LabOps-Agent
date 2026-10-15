"""本次审计缺陷闭环回归与保护测试套件

测试项覆盖：
1. init_db 自建机房保留与密码防覆盖保护 (P0)
2. vector_store 向量库持久化与防误清空保护 (P0)
3. assets delete_asset 资产借出中使用中删除安全拦截 (P1)
4. asset_tools 借调日志真实用户名 User 反查关联 (P1)
5. notifications 催办通知缺失借调人时合理降级回退 (P1)
"""

import os
import tempfile
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import Base, get_db
from app.db.models import ServerRoom, User, Asset, AssetBorrowLog, UserNotification
from app.db.init_db import init_db
from app.rag.vector_store import KnowledgeBase, DEFAULT_VOCAB
from app.tools.asset_tools import borrow_asset


@pytest.fixture(scope="module")
def audit_test_env():
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
def client(audit_test_env):
    return TestClient(app)


def test_init_db_preserves_custom_room_and_password(audit_test_env):
    """测试重新初始化种子时，自建机房不被静默删除且已修改的用户密码哈希不被覆盖"""
    SessionLocal = audit_test_env["session_factory"]
    engine = audit_test_env["engine"]
    db = SessionLocal()
    try:
        # 1. 插入用户自建机房
        custom_room = ServerRoom(
            room_code="ROOM-999-CUSTOM",
            room_name="999创新实验机房",
            location="实训楼999",
            power_capacity_kw=50.0,
            manager_teacher="张老师",
        )
        db.add(custom_room)

        # 2. 修改种子用户 teacher_li 的密码哈希
        user = db.query(User).filter(User.username == "teacher_li").first()
        assert user is not None
        custom_hash = "custom_modified_password_hash_12345"
        user.password_hash = custom_hash
        db.commit()
    finally:
        db.close()

    # 3. 再次执行 init_db (模拟服务重启再次填充种子)
    init_db(seed=True, reset=False, custom_engine=engine, custom_session_factory=SessionLocal)

    # 4. 验证自建机房依然完好保留，密码哈希未被原版覆盖
    verify_db = SessionLocal()
    try:
        room = verify_db.query(ServerRoom).filter(ServerRoom.room_code == "ROOM-999-CUSTOM").first()
        assert room is not None
        assert room.room_name == "999创新实验机房"

        teacher = verify_db.query(User).filter(User.username == "teacher_li").first()
        assert teacher.password_hash == custom_hash
    finally:
        verify_db.close()


def test_vector_store_does_not_delete_collection_on_dimension_change():
    """测试向量库初始化时即便词表长度发生增减，也不会强制 delete_collection 误清空已有切块"""
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        kb = KnowledgeBase(persist_directory=tmpdir)
        test_chunks = [
            {"doc_name": "sec_doc", "section": "sec1", "clause": "1.1", "content": "服务器机房温度不得高于40度"}
        ]
        kb.add_documents(test_chunks)
        assert len(kb.search("机房温度", top_k=1)) == 1

        # 模拟外部词表扩展或缩减 (DEFAULT_VOCAB 变长)
        mock_larger_vocab = DEFAULT_VOCAB + ["新", "词", "汇", "测", "试"]
        with patch("app.rag.vector_store.DEFAULT_VOCAB", mock_larger_vocab):
            # 重新实例化 KnowledgeBase，验证旧集合未被 delete_collection 删除，文档依然能够检索
            kb2 = KnowledgeBase(persist_directory=tmpdir)
            assert kb2.collection.count() == 1
            res = kb2.search("机房温度", top_k=1)
            assert len(res) == 1
            assert "40度" in res[0]["content"]


def test_borrow_asset_username_mapping(audit_test_env):
    """测试借出设备时，借调日志能精准反查真实 username 而非盲目写入带部门的长字符串"""
    SessionLocal = audit_test_env["session_factory"]
    db = SessionLocal()
    try:
        # 新增一台可用测试设备
        test_asset = Asset(
            asset_no="DEV-AUDIT-BORROW-01",
            name="审计测试刀片节点",
            category="服务器",
            location="实训楼201-机柜A01",
            health_status="HEALTHY",
            borrow_status="AVAILABLE",
        )
        db.add(test_asset)
        db.commit()

        # 调用 borrow_asset，传入常见中文全称格式 "李老师 (物联网工程教研室)"
        res = borrow_asset(
            asset_no="DEV-AUDIT-BORROW-01",
            borrower="李老师 (物联网工程教研室)",
            db=db,
        )
        assert res["status"] == "success"

        # 检查持久化的 AssetBorrowLog
        blog = (
            db.query(AssetBorrowLog)
            .filter(AssetBorrowLog.asset_id == "DEV-AUDIT-BORROW-01")
            .order_by(AssetBorrowLog.id.desc())
            .first()
        )
        assert blog is not None
        assert blog.borrower_username == "teacher_li"
        assert "李老师" in blog.borrower_name
    finally:
        db.close()


def test_delete_asset_blocked_when_in_use(client):
    """测试在用状态资产物理删除被 HTTP 400 安全联锁拦截"""
    # 1. 创建处于借出中的资产
    create_payload = {
        "asset_no": "DEV-AUDIT-INUSE-99",
        "name": "在用借出保护节点",
        "category": "服务器",
        "location": "实训楼101",
        "borrow_status": "IN_USE",
        "borrower": "王主管",
    }
    c_res = client.post("/api/assets/", json=create_payload)
    assert c_res.status_code == 201
    asset_id = c_res.json()["id"]

    # 2. 尝试直接删除，应触发 400 拦截
    del_res = client.delete(f"/api/assets/{asset_id}")
    assert del_res.status_code == 400
    assert "借出使用中" in del_res.json()["detail"]

    # 3. 归还后再次删除应正常成功 (204)
    client.patch(f"/api/assets/{asset_id}", json={"borrow_status": "AVAILABLE", "borrower": None})
    del_ok = client.delete(f"/api/assets/{asset_id}")
    assert del_ok.status_code == 204


def test_urge_notification_admin_fallback(client, audit_test_env):
    """测试对无借调人/无借调日志的设备发起催还时，不会硬编码李老师，而是平滑回退至管理员"""
    SessionLocal = audit_test_env["session_factory"]
    db = SessionLocal()
    try:
        asset = Asset(
            asset_no="DEV-AUDIT-FREE-01",
            name="无借用人设备",
            category="网络设备",
            location="实训楼201",
            borrow_status="AVAILABLE",
            borrower=None,
        )
        db.add(asset)
        db.commit()
    finally:
        db.close()

    payload = {
        "asset_no": "DEV-AUDIT-FREE-01",
        "remark": "请机房主管核实该设备去向",
    }
    resp = client.post("/api/notifications/urge", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    # 验证不包含硬编码的 teacher_li
    assert data["notification"]["username"] != "teacher_li"
    assert data["notification"]["username"] == "admin"

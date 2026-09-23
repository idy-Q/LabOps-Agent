"""超期借用智能预警与 Agent 催还督促公文服务自动化测试套件

测试项覆盖：
1. get_overdue_assets_summary 计算全机房逾期台数、最长逾期天数与明细
2. 借用记录 BORROWING 到期自动动态同步为 OVERDUE 状态
3. 非超期设备 (DEV-SRV-203) 正常借调隔离排除
4. generate_overdue_notice 生成规范红头公文字号、主送人、条例条款与 Markdown
5. REST API: GET /api/assets/overdue 端点契约
6. REST API: GET /api/assets/{asset_no}/overdue-notice 端点契约与 404 容错
7. Agent 工具 check_overdue_assets 与 draft_overdue_notice 行为
8. MockDecisionBrain 对“超期设备”、“起草催告函”、“督促催还”等意图的正确识别与工具调度
"""

import json
import os
import tempfile
from datetime import datetime, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import Base, get_db
from app.db.models import Asset, AssetBorrowLog, User
from app.db.init_db import init_db
from app.services.overdue_service import get_overdue_assets_summary, generate_overdue_notice
from app.tools.asset_tools import check_overdue_assets, draft_overdue_notice
from app.agent.react_engine import MockDecisionBrain


@pytest.fixture(scope="module")
def overdue_test_env():
    """创建物理隔离的测试数据库环境并填充标准种子数据"""
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
def client(overdue_test_env):
    return TestClient(app)


# ==================== 1. 服务层核心算法测试 ====================

def test_get_overdue_assets_summary(overdue_test_env):
    """测试逾期大盘统计与明细计算"""
    db = overdue_test_env["session_factory"]()
    try:
        summary = get_overdue_assets_summary(db)
        assert summary["status"] == "success"
        assert summary["total_overdue"] >= 1
        assert summary["max_overdue_days"] >= 18

        items = summary["items"]
        asset_nos = [it["asset_no"] for it in items]
        assert "DEV-SRV-201" in asset_nos
        # DEV-SRV-203 是未超期的正常借调，不应出现在逾期列表中
        assert "DEV-SRV-203" not in asset_nos

        srv_201_item = next(it for it in items if it["asset_no"] == "DEV-SRV-201")
        assert srv_201_item["borrower_name"] == "李老师"
        assert "物联网工程教研室" in srv_201_item["department"]
        assert srv_201_item["overdue_days"] >= 18
        assert srv_201_item["brand"] == "Dell"
    finally:
        db.close()


def test_dynamic_status_synchronization(overdue_test_env):
    """测试借调记录 BORROWING 到期后调用 summary 动态同步为 OVERDUE"""
    db = overdue_test_env["session_factory"]()
    try:
        # 新增一条已过期的 BORROWING 记录
        expired_log = AssetBorrowLog(
            log_no="BORROW-TEST-EXPIRED-999",
            asset_id="DEV-SRV-202",
            borrower_username="teacher_zhang",
            borrower_name="张老师",
            purpose="单元测试超期自动同步",
            borrow_time=datetime.now() - timedelta(days=10),
            expected_return_time=datetime.now() - timedelta(days=5),
            return_status="BORROWING",
            approver="王主管",
        )
        db.add(expired_log)
        db.commit()

        # 执行汇总计算，应动态标记为 OVERDUE
        summary = get_overdue_assets_summary(db)
        db.refresh(expired_log)
        assert expired_log.return_status == "OVERDUE"

        # 清理测试记录
        db.delete(expired_log)
        db.commit()
    finally:
        db.close()


def test_generate_overdue_notice_success(overdue_test_env):
    """测试针对 DEV-SRV-201 生成合规公文通知"""
    db = overdue_test_env["session_factory"]()
    try:
        notice = generate_overdue_notice(db, "DEV-SRV-201")
        assert notice["status"] == "success"
        assert "实管催字第" in notice["doc_code"]
        assert notice["title"] == "实验室仪器设备超期使用归还催告单"
        assert "李老师" in notice["recipient"]
        assert "物联网工程教研室" in notice["borrower"]["department"]
        assert notice["asset"]["asset_no"] == "DEV-SRV-201"
        assert notice["asset"]["brand"] == "Dell"
        assert notice["overdue_days"] >= 18
        assert len(notice["regulations"]) >= 2

        # 校验生成的 Markdown 文本
        md = notice["markdown_content"]
        assert "# 实验室仪器设备超期使用归还催告单" in md
        assert notice["doc_code"] in md
        assert "DEV-SRV-201" in md
        assert "大模型多模态推理教学实验与算力压测" in md
        assert "限期归还或续借处置" in md
    finally:
        db.close()


def test_generate_overdue_notice_not_found(overdue_test_env):
    """测试不存在的资产编号生成催告单抛出 ValueError"""
    db = overdue_test_env["session_factory"]()
    try:
        with pytest.raises(ValueError, match="不存在于机房台账中"):
            generate_overdue_notice(db, "DEV-NON-EXIST-999")
    finally:
        db.close()


# ==================== 2. REST API 契约测试 ====================

def test_api_get_overdue_assets(client):
    """测试 GET /api/assets/overdue 端点响应契约"""
    res = client.get("/api/assets/overdue")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "total_overdue" in data
    assert "max_overdue_days" in data
    assert isinstance(data["items"], list)
    assert any(it["asset_no"] == "DEV-SRV-201" for it in data["items"])


def test_api_get_overdue_notice(client):
    """测试 GET /api/assets/{asset_no}/overdue-notice 端点响应契约"""
    res = client.get("/api/assets/DEV-SRV-201/overdue-notice")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "doc_code" in data
    assert "markdown_content" in data
    assert "DEV-SRV-201" in data["markdown_content"]

    # 404 测试
    res_404 = client.get("/api/assets/DEV-NON-EXIST-999/overdue-notice")
    assert res_404.status_code == 404


# ==================== 3. Agent 工具与推理脑测试 ====================

def test_agent_tools(overdue_test_env):
    """测试 check_overdue_assets 与 draft_overdue_notice Agent 工具直接调用"""
    db = overdue_test_env["session_factory"]()
    try:
        res1 = check_overdue_assets(db=db)
        assert res1["status"] == "success"
        assert res1["total_overdue"] >= 1

        res2 = draft_overdue_notice(asset_no="DEV-SRV-201", db=db)
        assert res2["status"] == "success"
        assert "markdown_content" in res2

        res3 = draft_overdue_notice(asset_no="", db=db)
        assert res3["status"] == "error"
    finally:
        db.close()


def test_mock_decision_brain_check_overdue():
    """测试 Mock 决策脑对超期设备查询意图的识别与调用"""
    messages = [
        {"role": "user", "content": "检查当前机房所有借用超期设备清单及逾期天数"}
    ]
    step1 = MockDecisionBrain.decide(messages, user_role="ADMIN", user_name="王主管")
    assert "tool_calls" in step1
    call = step1["tool_calls"][0]
    assert call["function"]["name"] == "check_overdue_assets"

    # 模拟工具执行返回
    messages.append({
        "role": "assistant",
        "tool_calls": step1["tool_calls"],
    })
    messages.append({
        "role": "tool",
        "name": "check_overdue_assets",
        "content": json.dumps({
            "status": "success",
            "total_overdue": 1,
            "max_overdue_days": 18,
            "items": [
                {
                    "asset_no": "DEV-SRV-201",
                    "name": "2号机房-GPU计算节点01",
                    "borrower_name": "李老师",
                    "department": "物联网工程教研室",
                    "overdue_days": 18,
                    "expected_return_time": "2026-09-03 18:00:00",
                }
            ],
        }, ensure_ascii=False),
    })
    step2 = MockDecisionBrain.decide(messages, user_role="ADMIN", user_name="王主管")
    assert "content" in step2
    assert "机房资产借用超期预警汇报" in step2["content"]
    assert "DEV-SRV-201" in step2["content"]
    assert "18 天" in step2["content"]


def test_mock_decision_brain_draft_notice():
    """测试 Mock 决策脑对起草催告函与督促通知意图的识别与调用"""
    messages = [
        {"role": "user", "content": "请为设备 DEV-SRV-201 生成超期归还催告单并启动督促通知"}
    ]
    step1 = MockDecisionBrain.decide(messages, user_role="ADMIN", user_name="王主管")
    assert "tool_calls" in step1
    call = step1["tool_calls"][0]
    assert call["function"]["name"] == "draft_overdue_notice"
    args = json.loads(call["function"]["arguments"])
    assert args["asset_no"] == "DEV-SRV-201"

    # 模拟工具执行返回
    messages.append({
        "role": "assistant",
        "tool_calls": step1["tool_calls"],
    })
    messages.append({
        "role": "tool",
        "name": "draft_overdue_notice",
        "content": json.dumps({
            "status": "success",
            "doc_code": "〔2026〕实管催字第 0921 号",
            "recipient": "李老师 (物联网工程教研室)",
            "overdue_days": 18,
            "markdown_content": "# 实验室仪器设备超期使用归还催告单\n\n**公文字号**：〔2026〕实管催字第 0921 号\n\n请尽快交接归还。",
        }, ensure_ascii=False),
    })
    step2 = MockDecisionBrain.decide(messages, user_role="ADMIN", user_name="王主管")
    assert "content" in step2
    assert "实验室仪器设备超期使用归还催告单" in step2["content"]
    assert "〔2026〕实管催字第 0921 号" in step2["content"]


def test_mock_decision_brain_urge_not_confuse_with_return():
    """测试催促督促归还不被误判为办理归还资产登记"""
    messages = [
        {"role": "user", "content": "请督促李老师归还超期借用设备 DEV-SRV-201，并起草正式催告公函"}
    ]
    step = MockDecisionBrain.decide(messages, user_role="ADMIN", user_name="王主管")
    assert "tool_calls" in step
    call = step["tool_calls"][0]
    # 必须调用 draft_overdue_notice，绝不能调用 return_asset！
    assert call["function"]["name"] == "draft_overdue_notice"
    args = json.loads(call["function"]["arguments"])
    assert args["asset_no"] == "DEV-SRV-201"


# ==================== 4. 边界防御与鲁棒性深度测试 ====================

def test_generate_overdue_notice_non_overdue_rejected(overdue_test_env):
    """测试对处于正常借用期内未超期的设备 (DEV-SRV-203) 严正拦截拒签催告单"""
    db = overdue_test_env["session_factory"]()
    try:
        with pytest.raises(ValueError, match="尚未超期"):
            generate_overdue_notice(db, "DEV-SRV-203")
    finally:
        db.close()


def test_generate_overdue_notice_available_device_rejected(overdue_test_env):
    """测试对处于空闲在库状态的设备 (DEV-SRV-202) 严正拦截拒签催告单"""
    db = overdue_test_env["session_factory"]()
    try:
        with pytest.raises(ValueError, match="空闲在库状态"):
            generate_overdue_notice(db, "DEV-SRV-202")
    finally:
        db.close()


def test_generate_overdue_notice_returned_device_rejected(overdue_test_env):
    """测试对历史已结清正常归还的设备 (DEV-LAB-105) 严正拦截拒签催告单"""
    db = overdue_test_env["session_factory"]()
    try:
        with pytest.raises(ValueError, match="空闲在库状态"):
            generate_overdue_notice(db, "DEV-LAB-105")
    finally:
        db.close()


def test_api_rejection_for_non_overdue_devices(client):
    """测试 REST API 对未超期及在库设备出具催告函请求正确返回 HTTP 404"""
    # 正常借用中未超期
    res1 = client.get("/api/assets/DEV-SRV-203/overdue-notice")
    assert res1.status_code == 404
    assert "尚未超期" in res1.json()["detail"]

    # 空闲在库
    res2 = client.get("/api/assets/DEV-SRV-202/overdue-notice")
    assert res2.status_code == 404
    assert "空闲在库状态" in res2.json()["detail"]

    # 历史已结清归还
    res3 = client.get("/api/assets/DEV-LAB-105/overdue-notice")
    assert res3.status_code == 404


def test_return_device_clears_overdue_lifecycle(overdue_test_env):
    """测试设备超期借出后执行归还，超期大盘即时清零且无法再起草催告单"""
    from app.tools.asset_tools import return_asset
    db = overdue_test_env["session_factory"]()
    try:
        # 1. 归还前，DEV-SRV-201 在超期清单中
        summary_before = get_overdue_assets_summary(db)
        assert any(it["asset_no"] == "DEV-SRV-201" for it in summary_before["items"])

        # 2. 执行归还操作
        ret_res = return_asset(asset_no="DEV-SRV-201", db=db)
        assert ret_res["status"] == "success"

        # 3. 归还后，DEV-SRV-201 立即从超期清单消失
        summary_after = get_overdue_assets_summary(db)
        assert not any(it["asset_no"] == "DEV-SRV-201" for it in summary_after["items"])

        # 4. 再次请求出具催告单应被防御拦截
        with pytest.raises(ValueError, match="空闲在库状态"):
            generate_overdue_notice(db, "DEV-SRV-201")

        # 5. 恢复测试环境：将 DEV-SRV-201 恢复为借调超期状态供后续模块复用
        asset = db.query(Asset).filter(Asset.asset_no == "DEV-SRV-201").first()
        asset.borrow_status = "IN_USE"
        asset.borrower = "李老师 (物联网工程教研室)"
        blog = (
            db.query(AssetBorrowLog)
            .filter(AssetBorrowLog.asset_id == "DEV-SRV-201")
            .order_by(AssetBorrowLog.borrow_time.desc())
            .first()
        )
        if blog:
            blog.actual_return_time = None
            blog.return_status = "OVERDUE"
        db.commit()
    finally:
        db.close()


def test_services_direct_import_circular_dependency():
    """测试直接从 app.services 导入核心函数不会引发循环依赖崩溃"""
    from app.services import get_overdue_assets_summary, generate_overdue_notice, execute_autonomous_patrol
    assert callable(get_overdue_assets_summary)
    assert callable(generate_overdue_notice)
    assert callable(execute_autonomous_patrol)


def test_mock_decision_brain_extended_phrases():
    """测试扩展口语化 Prompt 识别矩阵准确调用对应工具"""
    test_cases = [
        ("查一下借用逾期", "check_overdue_assets"),
        ("查看逾期设备有哪些", "check_overdue_assets"),
        ("查查哪些设备超期了", "check_overdue_assets"),
        ("催一下李老师还设备 DEV-SRV-201", "draft_overdue_notice"),
        ("对设备 DEV-SRV-201 进行催还", "draft_overdue_notice"),
    ]
    for prompt, expected_tool in test_cases:
        res = MockDecisionBrain.decide([{"role": "user", "content": prompt}], "ADMIN", "王主管")
        assert "tool_calls" in res, f"Prompt '{prompt}' failed to trigger tool_calls"
        call = res["tool_calls"][0]
        assert call["function"]["name"] == expected_tool, f"Prompt '{prompt}' expected {expected_tool}, got {call['function']['name']}"


def test_overdue_notice_user_none_department_fallback(overdue_test_env):
    """测试当借用人用户记录的部门或手机号为 None 时，公文生成能安全降级并杜绝 'None' 字符串"""
    db = overdue_test_env["session_factory"]()
    try:
        # 创建一个 department 为 None 的测试用户与借调记录
        user = User(
            username="temp_borrower_empty_dept",
            password_hash="dummy_hash",
            real_name="临时教师",
            role="TEACHER",
            department="",
            phone="",
        )
        db.add(user)
        db.flush()

        asset = Asset(
            asset_no="DEV-TEST-NODEPT-01",
            name="测试无部门节点",
            category="服务器",
            location="实训楼201-机柜A02",
            health_status="HEALTHY",
            borrow_status="IN_USE",
            borrower="临时教师",
        )
        db.add(asset)
        db.flush()

        blog = AssetBorrowLog(
            log_no="BORROW-TEST-NODEPT-001",
            asset_id="DEV-TEST-NODEPT-01",
            borrower_username="temp_borrower_empty_dept",
            borrower_name="临时教师",
            purpose="验证部门为空时的催告单健壮性",
            borrow_time=datetime.now() - timedelta(days=10),
            expected_return_time=datetime.now() - timedelta(days=2),
            return_status="OVERDUE",
            approver="王主管",
        )
        db.add(blog)
        db.commit()

        # 生成公文
        notice = generate_overdue_notice(db, "DEV-TEST-NODEPT-01")
        assert notice["status"] == "success"
        assert "(None)" not in notice["recipient"]
        assert notice["borrower"]["department"] is not None
        assert "None" not in notice["borrower"]["department"]
        assert notice["borrower"]["phone"] is not None

        # 汇总
        summary = get_overdue_assets_summary(db)
        item = next(it for it in summary["items"] if it["asset_no"] == "DEV-TEST-NODEPT-01")
        assert item["department"] is not None
        assert "None" not in item["department"]

        # 清理
        db.delete(blog)
        db.delete(asset)
        db.delete(user)
        db.commit()
    finally:
        db.close()


"""设备口语简称、后缀编号与名称智能模糊解析全链路测试

验证用户输入口语简称（如 106、lab-106、srv-201、实验箱）时：
1. 底层 resolve_asset 能够精准匹配到目标资产实体；
2. get_server_metrics 能够支持口语简称并规范化返回真实指标；
3. ReAct 决策引擎能够精准提取口语简称实体并调用工具闭环。
"""

import pytest
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models import Asset
from app.tools.asset_tools import resolve_asset
from app.tools.metric_tools import get_server_metrics, resolve_seed_asset
from app.agent.react_engine import ReActEngine, MockDecisionBrain


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_resolve_seed_asset_shorthands():
    """测试离线 SEED 数据中的口语简称模糊匹配"""
    assert resolve_seed_asset("DEV-LAB-106")["asset_no"] == "DEV-LAB-106"
    assert resolve_seed_asset("LAB-106")["asset_no"] == "DEV-LAB-106"
    assert resolve_seed_asset("lab-106")["asset_no"] == "DEV-LAB-106"
    assert resolve_seed_asset("lab-106啊")["asset_no"] == "DEV-LAB-106"
    assert resolve_seed_asset("106")["asset_no"] == "DEV-LAB-106"
    assert resolve_seed_asset("实验箱-03号")["asset_no"] == "DEV-LAB-106"

    assert resolve_seed_asset("201")["asset_no"] == "DEV-SRV-201"
    assert resolve_seed_asset("srv-201")["asset_no"] == "DEV-SRV-201"


def test_resolve_asset_db_shorthands(db_session: Session):
    """测试数据库中对 DEV-LAB-106 的多形态模糊与口语匹配"""
    # 确保数据库中存在 DEV-LAB-106
    lab106 = db_session.query(Asset).filter(Asset.asset_no == "DEV-LAB-106").first()
    if not lab106:
        pytest.skip("数据库中未初始化 DEV-LAB-106，跳过 DB 测试")

    # 1. 编号全称
    a1 = resolve_asset("DEV-LAB-106", db=db_session)
    assert a1 is not None and a1.asset_no == "DEV-LAB-106"

    # 2. 去 DEV- 前缀大写
    a2 = resolve_asset("LAB-106", db=db_session)
    assert a2 is not None and a2.asset_no == "DEV-LAB-106"

    # 3. 小写口语
    a3 = resolve_asset("lab-106", db=db_session)
    assert a3 is not None and a3.asset_no == "DEV-LAB-106"

    # 4. 带语气助词
    a4 = resolve_asset("lab-106啊", db=db_session)
    assert a4 is not None and a4.asset_no == "DEV-LAB-106"

    # 5. 纯后缀数字
    a5 = resolve_asset("106", db=db_session)
    assert a5 is not None and a5.asset_no == "DEV-LAB-106"

    # 6. 名称片段
    a6 = resolve_asset("实验箱-03号", db=db_session)
    assert a6 is not None and a6.asset_no == "DEV-LAB-106"


def test_get_server_metrics_shorthand_support(db_session: Session):
    """测试 get_server_metrics 对简称的自动感知支持"""
    res1 = get_server_metrics(device_id="lab-106", db=db_session)
    assert res1["status"] != "error"
    assert res1["device_id"] == "DEV-LAB-106"
    assert "实验箱" in res1["device_name"]

    res2 = get_server_metrics(device_id="106", db=db_session)
    assert res2["status"] != "error"
    assert res2["device_id"] == "DEV-LAB-106"


def test_react_engine_decide_conversational_106(db_session: Session):
    """测试 Mock 决策引擎面对自然语言 '106机器好像超温了' 与 'lab-106啊' 能够精确命中 DEV-LAB-106"""
    # 1. 识别 "106机器好像超温了"
    msgs1 = [{"role": "user", "content": "106机器好像超温了"}]
    dec1 = MockDecisionBrain.decide(msgs1)
    assert "tool_calls" in dec1
    fn1 = dec1["tool_calls"][0]["function"]
    assert fn1["name"] == "get_server_metrics"
    import json
    args1 = json.loads(fn1["arguments"])
    assert args1["device_id"] == "DEV-LAB-106"

    # 2. 识别 "lab-106啊"
    msgs2 = [{"role": "user", "content": "lab-106啊"}]
    dec2 = MockDecisionBrain.decide(msgs2)
    assert "tool_calls" in dec2
    fn2 = dec2["tool_calls"][0]["function"]
    assert fn2["name"] == "get_server_metrics"
    args2 = json.loads(fn2["arguments"])
    assert args2["device_id"] == "DEV-LAB-106"

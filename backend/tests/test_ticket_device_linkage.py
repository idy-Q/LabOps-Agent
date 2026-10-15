"""工单完结设备健康闭环联动与无斜杠路由规范化回归测试套件"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import get_db
from app.db.models import Ticket, Asset, AssetDetail, ServerRoom


@pytest.fixture
def client():
    return TestClient(app)


def test_rooms_slash_and_non_slash_post(client):
    """测试 POST /api/rooms 与 POST /api/rooms/ 均不产生 307 重定向，均能正常处理创建"""
    payload_no_slash = {
        "room_code": "ROOM-402-TEST-1",
        "room_name": "实训机房402-A",
        "location": "实训楼402室",
        "manager_teacher": "王主管",
        "power_capacity_kw": 50.0,
    }
    res1 = client.post("/api/rooms", json=payload_no_slash)
    assert res1.status_code == 201, f"POST /api/rooms 应返回 201，实际: {res1.status_code}"
    assert res1.json()["room_code"] == "ROOM-402-TEST-1"

    # 清理
    client.delete("/api/rooms/ROOM-402-TEST-1")

    payload_with_slash = {
        "room_code": "ROOM-402-TEST-2",
        "room_name": "实训机房402-B",
        "location": "实训楼402室",
        "manager_teacher": "王主管",
        "power_capacity_kw": 50.0,
    }
    res2 = client.post("/api/rooms/", json=payload_with_slash)
    assert res2.status_code == 201, f"POST /api/rooms/ 应返回 201，实际: {res2.status_code}"
    assert res2.json()["room_code"] == "ROOM-402-TEST-2"

    # 清理
    client.delete("/api/rooms/ROOM-402-TEST-2")


def test_ticket_resolve_auto_recovers_asset_health_and_temperature(client):
    """测试工单流转至 RESOLVED 后，关联设备自动降温至安全基线 (31.5°C) 且健康状态恢复为 HEALTHY"""
    # 1. 创建一台超温故障设备
    asset_payload = {
        "asset_no": "DEV-TEST-OVERHEAT-99",
        "name": "测试过热GPU服务器",
        "category": "服务器",
        "location": "实训楼201-机柜A01",
        "health_status": "OVERHEAT",
        "custom_temperature": 43.5,
    }
    asset_res = client.post("/api/assets", json=asset_payload)
    assert asset_res.status_code == 201
    asset_id = asset_res.json()["id"]

    try:
        # 验证初始状态处于 OVERHEAT
        get_res = client.get(f"/api/assets/{asset_id}")
        assert get_res.json()["health_status"] == "OVERHEAT"
        assert get_res.json()["custom_temperature"] == 43.5

        # 2. 为该设备创建排障检修工单
        ticket_payload = {
            "title": "DEV-TEST-OVERHEAT-99 核心温度过热紧急排查",
            "description": "现场巡检散热情况，核验风扇转速与风道",
            "priority": "CRITICAL",
            "device_id": "DEV-TEST-OVERHEAT-99",
            "creator": "王主管",
        }
        ticket_res = client.post("/api/tickets", json=ticket_payload)
        assert ticket_res.status_code == 201
        ticket_id = ticket_res.json()["id"]

        # 3. 将工单流转推进至 PROCESSING
        p_res = client.put(
            f"/api/tickets/{ticket_id}",
            json={
                "status": "PROCESSING",
                "operator": "王主管",
                "comment": "已到达现场进行巡检与降频",
            },
        )
        assert p_res.status_code == 200
        assert p_res.json()["status"] == "PROCESSING"

        # 4. 将工单推进至 RESOLVED (已解决)
        r_res = client.put(
            f"/api/tickets/{ticket_id}",
            json={
                "status": "RESOLVED",
                "operator": "王主管",
                "comment": "现场巡检已完成并更换风扇，温度回落正常",
            },
        )
        assert r_res.status_code == 200
        assert r_res.json()["status"] == "RESOLVED"

        # 5. 核心断言：核验关联设备的健康度与温度指标是否已闭环复位
        asset_check = client.get(f"/api/assets/{asset_id}")
        asset_data = asset_check.json()
        assert asset_data["health_status"] == "HEALTHY", f"工单解决后设备健康状态应恢复为 HEALTHY，实际为: {asset_data['health_status']}"
        assert asset_data["custom_temperature"] == 31.5, f"工单解决后设定温度应回落至 31.5°C，实际为: {asset_data['custom_temperature']}"

    finally:
        # 清理测试数据
        client.delete(f"/api/assets/{asset_id}")

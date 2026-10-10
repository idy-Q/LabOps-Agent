"""机房机柜 2D 拓扑视图聚合接口自动化单元测试套件"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_get_rack_topology_structure_and_summary(client):
    """测试 GET /api/assets/topology 基础连通性、大盘总览指标与数据层级完整性"""
    resp = client.get("/api/assets/topology")
    assert resp.status_code == 200
    data = resp.json()

    # 1. 验证顶层核心字段结构
    assert "summary" in data
    assert "rooms" in data
    assert "unracked_assets" in data

    summary = data["summary"]
    # 2. 验证大盘总览指标计算精确性 (201立A01+A02空柜，101立B01柜，301纯仓储0柜)
    assert summary["total_rooms"] == 3
    assert summary["total_racks"] == 3
    assert summary["total_u"] == 126  # 3 个标准机柜 * 42U = 126U
    assert summary["used_u"] == 17  # A01 (14U) + B01 (3U) + A02 (0U) = 17U
    assert summary["usage_rate"] == 13.5  # round(17 / 126 * 100, 1) = 13.5%
    assert summary["total_assets"] == 15
    assert summary["racked_assets_count"] == 7
    assert summary["unracked_assets_count"] == 8
    assert summary["max_temperature"] >= 40.0  # DEV-SRV-201 核心超温 43.5℃
    assert summary["avg_temperature"] > 0

    # 3. 验证告警与健康态势分布
    health_dist = summary["health_distribution"]
    assert health_dist["HEALTHY"] >= 1
    assert health_dist["WARNING"] >= 1
    assert health_dist["OVERHEAT"] >= 1
    assert health_dist["OFFLINE"] >= 1


def test_rooms_and_rack_slots_aggregation(client):
    """测试机房拓扑树、42U 机柜与物理槽位切片渲染数据"""
    resp = client.get("/api/assets/topology")
    assert resp.status_code == 200
    data = resp.json()
    rooms = data["rooms"]
    assert len(rooms) == 3

    room_201 = next((r for r in rooms if r["room_code"] == "ROOM-201"), None)
    assert room_201 is not None
    assert room_201["room_name"] == "实训楼201 人工智能与高密算力实训机房"
    assert room_201["total_racks"] == 2
    assert room_201["stats"]["used_u"] == 14  # A01: 14U / 84U (A01+A02) = 16.7%
    assert room_201["stats"]["usage_rate"] == 16.7
    assert room_201["stats"]["health_status"] == "OVERHEAT"

    # 验证 机柜A01 细节
    rack_a01 = next((rk for rk in room_201["racks"] if rk["rack_id"] == "机柜A01"), None)
    assert rack_a01 is not None
    assert rack_a01["total_u"] == 42
    assert rack_a01["used_u"] == 14
    assert rack_a01["usage_rate"] == 33.3
    assert rack_a01["health_status"] == "OVERHEAT"
    assert len(rack_a01["assets"]) == 5  # 5 台在架设备全量归整至 A01

    # 验证 机柜A02 (空 42U 机柜) 细节
    rack_a02 = next((rk for rk in room_201["racks"] if rk["rack_id"] == "机柜A02"), None)
    assert rack_a02 is not None
    assert rack_a02["total_u"] == 42
    assert rack_a02["used_u"] == 0
    assert rack_a02["usage_rate"] == 0.0
    assert rack_a02["health_status"] == "HEALTHY"
    assert len(rack_a02["assets"]) == 0
    assert len(rack_a02["slots"]) == 42
    assert all(not s["occupied"] for s in rack_a02["slots"])

    # 验证在架设备的起始 U 位及高度
    asset_map = {a["asset_no"]: a for a in rack_a01["assets"]}
    assert asset_map["DEV-NET-301"]["start_u"] == 40
    assert asset_map["DEV-NET-301"]["u_height"] == 2
    assert asset_map["DEV-NET-303"]["start_u"] == 36
    assert asset_map["DEV-NET-303"]["u_height"] == 2
    assert asset_map["DEV-SRV-201"]["start_u"] == 28
    assert asset_map["DEV-SRV-201"]["u_height"] == 4
    assert asset_map["DEV-SRV-202"]["start_u"] == 24
    assert asset_map["DEV-SRV-202"]["u_height"] == 2
    assert asset_map["DEV-SRV-203"]["start_u"] == 18
    assert asset_map["DEV-SRV-203"]["u_height"] == 4

    # 验证 42U 标准槽位切片
    assert len(rack_a01["slots"]) == 42
    slot_28 = next((s for s in rack_a01["slots"] if s["u"] == 28), None)
    assert slot_28 is not None
    assert slot_28["occupied"] is True
    assert slot_28["device"]["asset_no"] == "DEV-SRV-201"
    assert slot_28["device"]["is_base"] is True

    slot_40 = next((s for s in rack_a01["slots"] if s["u"] == 40), None)
    assert slot_40 is not None
    assert slot_40["occupied"] is True
    assert slot_40["device"]["asset_no"] == "DEV-NET-301"

    # 空闲插槽验证
    slot_10 = next((s for s in rack_a01["slots"] if s["u"] == 10), None)
    assert slot_10 is not None
    assert slot_10["occupied"] is False
    assert slot_10["device"] is None


def test_unracked_peripherals_and_room_filtering(client):
    """测试非机架外设资产聚类 (100% 在册设备可视) 与单机房按需过滤"""
    # 1. 过滤 ROOM-101
    resp_101 = client.get("/api/assets/topology?room_code=ROOM-101")
    assert resp_101.status_code == 200
    data_101 = resp_101.json()
    assert data_101["filtered_room_code"] == "ROOM-101"
    assert data_101["selected_room"] is not None
    assert data_101["selected_room"]["room_code"] == "ROOM-101"
    assert data_101["selected_room"]["total_racks"] == 1
    assert data_101["selected_room"]["stats"]["in_rack_count"] == 2  # DEV-SRV-204, DEV-NET-302
    assert data_101["selected_room"]["stats"]["unracked_count"] == 5  # UPS-101, NET-304, LAB-105, 106, 107

    rack_b01 = data_101["selected_room"]["racks"][0]
    assert rack_b01["rack_id"] == "机柜B01"
    assert rack_b01["used_u"] == 3  # DEV-NET-302 (1U) + DEV-SRV-204 (2U)
    assert rack_b01["usage_rate"] == 7.1

    # 2. 过滤 ROOM-301 (备用库房与退役设备，纯仓储无机柜)
    resp_301 = client.get("/api/assets/topology?room_code=ROOM-301")
    assert resp_301.status_code == 200
    data_301 = resp_301.json()
    sel_301 = data_301["selected_room"]
    assert sel_301["total_racks"] == 0
    assert len(sel_301["racks"]) == 0
    assert sel_301["stats"]["total_u"] == 0
    assert sel_301["stats"]["used_u"] == 0
    assert len(sel_301["unracked_assets"]) == 1
    assert sel_301["unracked_assets"][0]["asset_no"] == "DEV-SRV-205"


def test_nonexistent_room_filter(client):
    """测试过滤不存在的机房编号，验证优雅返回而不是抛出 500 异常"""
    resp = client.get("/api/assets/topology?room_code=ROOM-999")
    assert resp.status_code == 200
    data = resp.json()
    assert data["filtered_room_code"] == "ROOM-999"
    assert data["selected_room"] is None
    assert len(data["rooms"]) == 3
    # 仍应展示全局非在架外设，不发生数据丢失
    assert len(data["unracked_assets"]) == 8


def test_rack_topology_metrics_resilience(client):
    """测试机房拓扑各项计算指标的自洽性与边界防护 (利用率与总U位)"""
    resp = client.get("/api/assets/topology")
    assert resp.status_code == 200
    data = resp.json()

    for room in data["rooms"]:
        stats = room["stats"]
        assert stats["total_u"] >= 0
        assert 0 <= stats["used_u"] <= stats["total_u"]
        assert 0.0 <= stats["usage_rate"] <= 100.0
        assert stats["in_rack_count"] + stats["unracked_count"] >= 0

        for rack in room["racks"]:
            assert rack["total_u"] == 42
            assert 0 <= rack["used_u"] <= 42
            assert len(rack["slots"]) == 42
            assert "has_conflict" in rack
            # 槽位倒序 U42 -> U1
            assert rack["slots"][0]["u"] == 42
            assert rack["slots"][-1]["u"] == 1


def test_room_filter_case_insensitivity_and_shorthand(client):
    """测试机房过滤对小写 room-201 与纯数字 201 简写形式的健壮支持"""
    # 1. 小写 room-201
    resp_lower = client.get("/api/assets/topology?room_code=room-201")
    assert resp_lower.status_code == 200
    data_lower = resp_lower.json()
    assert data_lower["selected_room"] is not None
    assert data_lower["selected_room"]["room_code"] == "ROOM-201"
    assert data_lower["selected_room"]["stats"]["used_u"] == 14

    # 2. 纯数字简写 101
    resp_short = client.get("/api/assets/topology?room_code=101")
    assert resp_short.status_code == 200
    data_short = resp_short.json()
    assert data_short["selected_room"] is not None
    assert data_short["selected_room"]["room_code"] == "ROOM-101"
    assert data_short["selected_room"]["stats"]["used_u"] == 3

    # 3. 纯数字简写 301 (零机柜)
    resp_301 = client.get("/api/assets/topology?room_code=301")
    assert resp_301.status_code == 200
    data_301 = resp_301.json()
    assert data_301["selected_room"] is not None
    assert data_301["selected_room"]["room_code"] == "ROOM-301"
    assert data_301["selected_room"]["stats"]["total_u"] == 0


def test_drag_and_drop_rack_allocation_and_dispatch(client):
    """测试设备录入/拖拽调拨机位在拓扑图中的动态上架、跨柜迁移与周边配套区双向流转"""
    import json

    # 1. 录入一台新服务器，预设放置于 机柜A02 的 U18~U21 (4U)
    create_payload = {
        "asset_no": "DEV-TEST-DND-99",
        "name": "自动化测试调拨GPU服务器",
        "category": "服务器",
        "location": "实训楼201-机柜A02-U18(4U)",
        "health_status": "HEALTHY",
        "borrow_status": "AVAILABLE",
        "detail": {
            "extra_params": json.dumps({"start_u": 18, "u_height": 4, "rack_units": "4U"}),
        },
    }
    resp = client.post("/api/assets/", json=create_payload)
    assert resp.status_code == 201
    asset_id = resp.json()["id"]

    try:
        # 2. 检查拓扑接口：该设备应准确上架至 ROOM-201 机柜A02
        topo_resp = client.get("/api/assets/topology")
        assert topo_resp.status_code == 200
        rooms = topo_resp.json()["rooms"]
        room_201 = next(r for r in rooms if r["room_code"] == "ROOM-201")
        rack_a02 = next(rk for rk in room_201["racks"] if rk["rack_id"] == "机柜A02")
        a02_assets = {a["asset_no"]: a for a in rack_a02["assets"]}
        assert "DEV-TEST-DND-99" in a02_assets
        assert a02_assets["DEV-TEST-DND-99"]["start_u"] == 18
        assert a02_assets["DEV-TEST-DND-99"]["u_height"] == 4

        # 3. 模拟跨柜拖拽迁移：从 机柜A02 拖至 101 机房 机柜B01 U1~U4
        update_payload = {
            "location": "实训楼101-机柜B01-U1(4U)",
            "detail": {
                "extra_params": json.dumps({"start_u": 1, "u_height": 4, "rack_units": "4U"}),
            },
        }
        patch_resp = client.patch(f"/api/assets/{asset_id}", json=update_payload)
        assert patch_resp.status_code == 200

        # 验证拓扑：A02 已无该设备，B01 成功接收
        topo_resp2 = client.get("/api/assets/topology")
        rooms2 = topo_resp2.json()["rooms"]
        room_201_new = next(r for r in rooms2 if r["room_code"] == "ROOM-201")
        rack_a02_new = next(rk for rk in room_201_new["racks"] if rk["rack_id"] == "机柜A02")
        assert "DEV-TEST-DND-99" not in [a["asset_no"] for a in rack_a02_new["assets"]]

        room_101_new = next(r for r in rooms2 if r["room_code"] == "ROOM-101")
        rack_b01_new = next(rk for rk in room_101_new["racks"] if rk["rack_id"] == "机柜B01")
        b01_assets = {a["asset_no"]: a for a in rack_b01_new["assets"]}
        assert "DEV-TEST-DND-99" in b01_assets
        assert b01_assets["DEV-TEST-DND-99"]["start_u"] == 1

        # 4. 模拟下架流转至周边配套区（修改类别为配电温控，清空 start_u）
        unrack_payload = {
            "category": "配电温控",
            "location": "实训楼101-动力配电区",
            "detail": {
                "extra_params": json.dumps({"cooling": "列间风道"}),
            },
        }
        patch_resp2 = client.patch(f"/api/assets/{asset_id}", json=unrack_payload)
        assert patch_resp2.status_code == 200

        # 验证拓扑：B01 机柜已移除，全量 unracked_assets 正确收纳
        topo_resp3 = client.get("/api/assets/topology")
        unracked = topo_resp3.json()["unracked_assets"]
        unracked_nos = [a["asset_no"] for a in unracked]
        assert "DEV-TEST-DND-99" in unracked_nos
    finally:
        # 清理测试数据，保持数据库状态无污染
        del_resp = client.delete(f"/api/assets/{asset_id}")
        assert del_resp.status_code in [200, 204]




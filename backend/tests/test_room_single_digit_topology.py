"""单数字机房(如编号'1')防机柜克隆与防幽灵资产渗透回归测试套件"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_room_1_topology_has_no_ghost_racks_or_cloned_assets(client):
    """测试新建编号为'1'且名称为'1'的机房时，绝不应克隆机柜A01/B01或误匹配任何既有资产"""
    # 1. 创建编号为 '1', 名称为 '1' 的机房
    room_payload = {
        "room_code": "1",
        "room_name": "1",
        "location": "实训楼1",
        "manager_teacher": "王主管",
        "power_capacity_kw": 50.0,
    }
    create_res = client.post("/api/rooms", json=room_payload)
    assert create_res.status_code == 201

    try:
        # 2. 查询拓扑大盘
        topo_res = client.get("/api/assets/topology?room_code=1")
        assert topo_res.status_code == 200
        data = topo_res.json()

        rooms = [r for r in data.get("rooms", []) if r["room_code"] == "1"]
        assert len(rooms) == 1, "未在拓扑大盘中找到机房 '1'"
        room_1 = rooms[0]

        # 核心断言：新建的空机房 '1' 必须是 0 机柜、0 在架资产
        assert room_1["total_racks"] == 0, f"机房1机柜数应为0，实际为: {room_1['total_racks']}"
        assert len(room_1["racks"]) == 0, f"机房1机柜列表应为空，实际含有: {[r['rack_id'] for r in room_1['racks']]}"
        assert len(room_1["unracked_assets"]) == 0, f"机房1外设列表应为空，实际含有: {len(room_1['unracked_assets'])}"

        # 3. 验证空机房能正常安全注销删除（无误判阻断）
        del_res = client.delete("/api/rooms/1")
        assert del_res.status_code == 200
        assert "已成功注销删除" in del_res.json()["message"]
    except Exception:
        client.delete("/api/rooms/1")
        raise

"""机房与机柜全生命周期动态化闭环单元测试套件

涵盖：
1. 机房 (ServerRoom) 新增、列表、详情、编辑、安全联锁删除校验
2. 机柜 (ServerRack) 新增、列表、详情、编辑、安全联锁下线删除校验
3. 拓扑接口与大盘指标动态联动 (立柜即现、下线即消)
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_rooms_crud_and_safety_interlock(client):
    """测试机房增删改查及带机柜/带资产防误删安全联锁防护"""
    # 1. 查询初始机房列表 (ROOM-201, ROOM-101, ROOM-301)
    res = client.get("/api/rooms/")
    assert res.status_code == 200
    rooms = res.json()
    codes = [r["room_code"] for r in rooms]
    assert "ROOM-201" in codes
    assert "ROOM-101" in codes
    assert "ROOM-301" in codes

    # 2. 尝试删除带有在册机柜和资产的 ROOM-201，应触发安全联锁拦截 (HTTP 400)
    del_blocked = client.delete("/api/rooms/ROOM-201")
    assert del_blocked.status_code == 400
    assert "该机房下仍有在册机柜或资产" in del_blocked.json()["detail"]

    # 3. 尝试删除带有外设资产的 ROOM-301，应触发安全联锁拦截 (HTTP 400)
    del_301_blocked = client.delete("/api/rooms/ROOM-301")
    assert del_301_blocked.status_code == 400
    assert "该机房下仍有在册机柜或资产" in del_301_blocked.json()["detail"]

    # 4. 新增无机柜且无资产的全新机房 ROOM-501
    create_payload = {
        "room_code": "ROOM-501",
        "room_name": "实训楼501 边缘智能创新实验室",
        "location": "实训楼5层东区501室",
        "manager_teacher": "张教授",
        "power_capacity_kw": 60.0,
    }
    create_res = client.post("/api/rooms/", json=create_payload)
    assert create_res.status_code == 201
    data = create_res.json()
    assert data["room_code"] == "ROOM-501"
    assert data["total_racks"] == 0

    # 5. 重复创建相同编号机房，应返回 HTTP 400
    dup_res = client.post("/api/rooms/", json=create_payload)
    assert dup_res.status_code == 400
    assert "已存在" in dup_res.json()["detail"]

    # 6. 编辑机房信息
    update_res = client.put(
        "/api/rooms/ROOM-501",
        json={"room_name": "实训楼501 人机协同实验中心", "power_capacity_kw": 75.0},
    )
    assert update_res.status_code == 200
    assert update_res.json()["room_name"] == "实训楼501 人机协同实验中心"
    assert update_res.json()["power_capacity_kw"] == 75.0

    # 7. 删除空机房，应当成功删除
    del_ok = client.delete("/api/rooms/ROOM-501")
    assert del_ok.status_code == 200
    assert "已成功注销删除" in del_ok.json()["message"]

    # 8. 再次查询机房详情，应返回 404
    get_del = client.get("/api/rooms/ROOM-501")
    assert get_del.status_code == 404


def test_racks_crud_and_safety_interlock(client):
    """测试机柜增删改查及非空机柜安全联锁阻断下线防护"""
    # 1. 查询机柜列表
    res = client.get("/api/racks/")
    assert res.status_code == 200
    racks = res.json()
    rack_ids = [r["rack_id"] for r in racks]
    assert "机柜A01" in rack_ids
    assert "机柜A02" in rack_ids
    assert "机柜B01" in rack_ids

    # 2. 按机房过滤机柜
    r_201_res = client.get("/api/racks/?room_code=ROOM-201")
    assert r_201_res.status_code == 200
    r_201_racks = [r["rack_id"] for r in r_201_res.json()]
    assert "机柜A01" in r_201_racks
    assert "机柜A02" in r_201_racks
    assert "机柜B01" not in r_201_racks

    # 3. 尝试下线含有在架设备的 机柜A01，应触发安全联锁拦截 (HTTP 400)
    del_a01 = client.delete("/api/racks/机柜A01")
    assert del_a01.status_code == 400
    assert "该机柜内尚有" in del_a01.json()["detail"]
    assert "在架设备" in del_a01.json()["detail"]

    # 4. 在不存在的机房立柜，应返回 404
    bad_room_res = client.post(
        "/api/racks/",
        json={
            "rack_id": "机柜X99",
            "rack_name": "X99 测试柜",
            "room_code": "ROOM-NONEXIST",
            "total_u": 42,
            "power_rating_w": 5000,
        },
    )
    assert bad_room_res.status_code == 404

    # 5. 在 ROOM-101 新增一个空机柜 机柜B02
    create_rack_payload = {
        "rack_id": "机柜B02",
        "rack_name": "B02 备用网络扩展汇聚柜",
        "room_code": "ROOM-101",
        "total_u": 42,
        "power_rating_w": 4000,
    }
    create_b02 = client.post("/api/racks/", json=create_rack_payload)
    assert create_b02.status_code == 201
    assert create_b02.json()["rack_id"] == "机柜B02"

    # 6. 编辑机柜信息
    update_b02 = client.put(
        "/api/racks/机柜B02",
        json={"rack_name": "B02 软件定义网络实验扩展柜", "power_rating_w": 4200},
    )
    assert update_b02.status_code == 200
    assert update_b02.json()["rack_name"] == "B02 软件定义网络实验扩展柜"
    assert update_b02.json()["power_rating_w"] == 4200

    # 7. 下线空机柜 机柜B02，应当成功
    del_b02 = client.delete("/api/racks/机柜B02")
    assert del_b02.status_code == 200
    assert "已成功下线注销" in del_b02.json()["message"]


def test_dynamic_topology_sync_on_rack_lifecycle(client):
    """测试机柜新增与下线能够实时动态反映在拓扑大盘中 (告别静态硬编码)"""
    # 1. 获取当前大盘机柜总数
    topo1 = client.get("/api/assets/topology").json()
    orig_total_racks = topo1["summary"]["total_racks"]
    orig_total_u = topo1["summary"]["total_u"]

    # 2. 为 ROOM-201 新增一个机柜 机柜A03 (42U)
    new_rack_payload = {
        "rack_id": "机柜A03",
        "rack_name": "A03 智算高通量扩展柜",
        "room_code": "ROOM-201",
        "total_u": 42,
        "power_rating_w": 6000,
    }
    c_res = client.post("/api/racks/", json=new_rack_payload)
    assert c_res.status_code == 201

    try:
        # 3. 再次请求拓扑大盘：应即时动态包含 机柜A03
        topo2 = client.get("/api/assets/topology").json()
        assert topo2["summary"]["total_racks"] == orig_total_racks + 1
        assert topo2["summary"]["total_u"] == orig_total_u + 42

        room_201 = next(r for r in topo2["rooms"] if r["room_code"] == "ROOM-201")
        rack_ids_201 = [rk["rack_id"] for rk in room_201["racks"]]
        assert "机柜A03" in rack_ids_201

        a03_rack = next(rk for rk in room_201["racks"] if rk["rack_id"] == "机柜A03")
        assert a03_rack["rack_name"] == "A03 智算高通量扩展柜"
        assert a03_rack["total_u"] == 42
        assert a03_rack["used_u"] == 0
        assert len(a03_rack["slots"]) == 42
    finally:
        # 4. 下线清理 机柜A03
        del_res = client.delete("/api/racks/机柜A03")
        assert del_res.status_code == 200

    # 5. 验证拓扑恢复原状
    topo3 = client.get("/api/assets/topology").json()
    assert topo3["summary"]["total_racks"] == orig_total_racks
    room_201_restored = next(r for r in topo3["rooms"] if r["room_code"] == "ROOM-201")
    assert "机柜A03" not in [rk["rack_id"] for rk in room_201_restored["racks"]]


def test_room_single_digit_boundary_interlock(client):
    """测试单字符/数字机房编号 (如 ROOM-2) 的删除安全联锁：不应被 201 资产误判拦截"""
    # 1. 创建编号为 ROOM-2 的空机房
    res = client.post("/api/rooms/", json={
        "room_code": "ROOM-2",
        "room_name": "实训楼2号临时设备间",
        "location": "实训楼2层西区通道",
        "manager_teacher": "张老师",
        "power_capacity_kw": 15.0,
    })
    assert res.status_code == 201

    # 2. 删除空机房 ROOM-2：由于没有机柜也没有资产，应成功删除 (此前因 '2' in '201' 会报 400 假阳性)
    del_res = client.delete("/api/rooms/ROOM-2")
    assert del_res.status_code == 200
    assert "已成功注销删除" in del_res.json()["message"]


def test_rack_prefix_boundary_interlock(client):
    """测试机柜名称前缀边界隔离：机柜A1 不应被 机柜A01 或 机柜A10 误判拦截"""
    # 1. 在 ROOM-101 新增空机柜 机柜A1
    res = client.post("/api/racks/", json={
        "rack_id": "机柜A1",
        "rack_name": "A1 边缘网络试验柜",
        "room_code": "ROOM-101",
        "total_u": 42,
        "power_rating_w": 3000,
    })
    assert res.status_code == 201

    # 2. 删除空机柜 机柜A1：应正常删除，不被其他含有 A 的机柜在架设备干扰
    del_res = client.delete("/api/racks/机柜A1")
    assert del_res.status_code == 200
    assert "已成功下线注销" in del_res.json()["message"]


def test_rack_capacity_shrink_and_migration_safety_interlock(client):
    """测试机柜容量压缩越界防护及在架设备跨机房迁移安全联锁"""
    # 1. 尝试将含有高U位设备的 机柜A01 (有设备位于 U28~U31) 的总容量压缩为 10U，应触发安全联锁拦截 (HTTP 400)
    shrink_res = client.put("/api/racks/机柜A01", json={"total_u": 10})
    assert shrink_res.status_code == 400
    assert "无法将机柜容量调整为 10U" in shrink_res.json()["detail"]
    assert "超出新容量空间" in shrink_res.json()["detail"]

    # 2. 尝试将含有在架设备的 机柜A01 跨机房直接迁移至 ROOM-101，应触发安全联锁拦截 (HTTP 400)
    migrate_res = client.put("/api/racks/机柜A01", json={"room_code": "ROOM-101"})
    assert migrate_res.status_code == 400
    assert "不可直接跨机房迁移机柜" in migrate_res.json()["detail"]


def test_full_lifecycle_new_room_rack_asset_topology(client):
    """全生命周期全链路验证：新建机房 -> 立柜 -> 资产上架 -> 拓扑动态反映 -> 级联阻断 -> 清退清理"""
    # 1. 新建机房 ROOM-601
    room_res = client.post("/api/rooms/", json={
        "room_code": "ROOM-601",
        "room_name": "实训楼601 算力仿真创新基地",
        "location": "实训楼6层601室",
        "manager_teacher": "赵教授",
        "power_capacity_kw": 88.0,
    })
    assert room_res.status_code == 201

    # 2. 新建立项 36U 机柜 机柜C01
    rack_res = client.post("/api/racks/", json={
        "rack_id": "机柜C01",
        "rack_name": "C01 智算集群柜",
        "room_code": "ROOM-601",
        "total_u": 36,
        "power_rating_w": 5500,
    })
    assert rack_res.status_code == 201

    # 3. 录入在架资产 DEV-SRV-601 放置于 U12(2U)
    asset_res = client.post("/api/assets/", json={
        "asset_no": "DEV-SRV-601",
        "name": "6号机房-高密仿真节点01",
        "category": "服务器",
        "location": "实训楼601-机柜C01-U12(2U)",
        "health_status": "HEALTHY",
        "detail": {
            "model_name": "Dell PowerEdge R750",
            "custom_temperature": 32.0,
            "extra_params": '{"start_u": 12, "u_height": 2, "rack_units": "2U"}',
        },
    })
    assert asset_res.status_code == 201
    asset_id = asset_res.json()["id"]

    try:
        # 4. 验证拓扑接口能够正确反映新机房、新机柜及在架资产
        topo = client.get("/api/assets/topology").json()
        room_601 = next((r for r in topo["rooms"] if r["room_code"] == "ROOM-601"), None)
        assert room_601 is not None
        assert room_601["room_name"] == "实训楼601 算力仿真创新基地"
        assert len(room_601["racks"]) == 1

        rack_c01 = room_601["racks"][0]
        assert rack_c01["rack_id"] == "机柜C01"
        assert rack_c01["total_u"] == 36
        assert rack_c01["used_u"] == 2
        assert len(rack_c01["slots"]) == 36
        assert len(rack_c01["assets"]) == 1
        assert rack_c01["assets"][0]["asset_no"] == "DEV-SRV-601"

        # 5. 安全联锁：尝试下线 机柜C01，应被阻断 (HTTP 400)
        del_rack_blocked = client.delete("/api/racks/机柜C01")
        assert del_rack_blocked.status_code == 400
        assert "该机柜内尚有 1 台在架设备" in del_rack_blocked.json()["detail"]

        # 6. 安全联锁：尝试注销 机房 ROOM-601，应被阻断 (HTTP 400)
        del_room_blocked = client.delete("/api/rooms/ROOM-601")
        assert del_room_blocked.status_code == 400
        assert "该机房下仍有在册机柜或资产" in del_room_blocked.json()["detail"]
    finally:
        # 7. 清理在架资产
        client.delete(f"/api/assets/{asset_id}")

        # 8. 清理下线 机柜C01
        del_rack_ok = client.delete("/api/racks/机柜C01")
        assert del_rack_ok.status_code == 200

        # 9. 清理注销 机房 ROOM-601
        del_room_ok = client.delete("/api/rooms/ROOM-601")
        assert del_room_ok.status_code == 200


def test_room_location_unique_constraint(client):
    """测试机房物理位置 (location) 在添加与修改时的排他唯一性硬拦截规则"""
    # 1. 查询现有机房 ROOM-201 的物理位置
    res_201 = client.get("/api/rooms/ROOM-201")
    assert res_201.status_code == 200
    loc_201 = res_201.json()["location"]

    # 2. 尝试新增一个编号不同但物理位置完全相同的机房，应被严格拦截 (HTTP 400)
    dup_loc_create = client.post("/api/rooms/", json={
        "room_code": "ROOM-DUP-LOC",
        "room_name": "重复物理位置测试机房",
        "location": loc_201,
        "manager_teacher": "测试员",
        "power_capacity_kw": 30.0,
    })
    assert dup_loc_create.status_code == 400
    assert "机房物理位置" in dup_loc_create.json()["detail"]
    assert "不可重复" in dup_loc_create.json()["detail"]

    # 3. 尝试编辑 ROOM-101，将其物理位置更改为已存在的 ROOM-201 位置，应被拦截 (HTTP 400)
    dup_loc_update = client.put("/api/rooms/ROOM-101", json={
        "location": loc_201,
    })
    assert dup_loc_update.status_code == 400
    assert "机房物理位置" in dup_loc_update.json()["detail"]
    assert "不可重复" in dup_loc_update.json()["detail"]

    # 4. 编辑 ROOM-101 但保持自身位置不变，应允许成功 (排除自身)
    res_101 = client.get("/api/rooms/ROOM-101")
    loc_101 = res_101.json()["location"]
    self_update = client.put("/api/rooms/ROOM-101", json={
        "location": loc_101,
        "room_name": res_101.json()["room_name"],
    })
    assert self_update.status_code == 200


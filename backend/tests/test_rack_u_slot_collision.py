"""机架物理槽位防重叠排他性碰撞校验测试 (Slot Collision Prevention Tests)

测试场景覆盖：
1. 在同一机柜上录入设备，若选择的 U 位区间与已有设备发生物理重叠，系统必须坚决拦截并返回 HTTP 400；
2. 录入设备选择空闲 U 位区间时，成功录入；
3. 修改既有设备时，排除当前设备自身所占槽位（允许只修改名称、温度、参数等而槽位不变）；
4. 修改既有设备槽位至已被其他设备占用的槽位时，坚决拦截并返回 HTTP 400；
5. 修改既有设备槽位至其他空闲槽位时，允许更新成功；
6. 起始槽位越界校验：超出机柜总容量 (如 42U 机柜 U42 放置 2U 设备) 触发 HTTP 400 拦截。
"""

import pytest
from starlette.testclient import TestClient
from app.main import app
from app.db.models import Asset, ServerRack, ServerRoom
from app.db.session import SessionLocal


@pytest.fixture
def client():
    return TestClient(app)


def test_asset_slot_collision_on_creation_and_update(client):
    """测试设备录入与修改阶段的物理机柜 U 位槽位防重叠排他性硬拦截"""
    db = SessionLocal()
    try:
        # 确保基础机房与机柜存在
        room = db.query(ServerRoom).filter(ServerRoom.room_code == "ROOM-201").first()
        if not room:
            room = ServerRoom(room_code="ROOM-201", room_name="实训楼201 人工智能实训机房")
            db.add(room)
            db.commit()

        rack = db.query(ServerRack).filter(ServerRack.rack_id == "机柜A01").first()
        if not rack:
            rack = ServerRack(rack_id="机柜A01", rack_name="A01 核心机柜", room_code="ROOM-201", total_u=42)
            db.add(rack)
            db.commit()
    finally:
        db.close()

    asset1_id = None
    asset2_id = None

    try:
        # 1. 正常录入设备 1：放置于 机柜A01 的 U10~U11 (2U)
        res1 = client.post(
            "/api/assets",
            json={
                "asset_no": "DEV-TEST-COLLISION-01",
                "name": "测试计算服务器-01",
                "category": "服务器",
                "location": "实训楼201-机柜A01-U10(2U)",
                "detail": {
                    "extra_params": '{"start_u": 10, "u_height": 2, "rack_units": "2U"}'
                },
            },
        )
        assert res1.status_code == 201
        asset1_id = res1.json()["id"]

        # 2. 尝试录入设备 2：故意选择与设备 1 重叠的槽位
        # 2.1 完全相同 U10 (2U, 占用 U10~U11) -> 必须被 400 拦截
        dup_res = client.post(
            "/api/assets",
            json={
                "asset_no": "DEV-TEST-COLLISION-02",
                "name": "冲突设备-完全相同",
                "category": "服务器",
                "location": "实训楼201-机柜A01-U10(2U)",
                "detail": {
                    "extra_params": '{"start_u": 10, "u_height": 2}'
                },
            },
        )
        assert dup_res.status_code == 400
        assert "冲突" in dup_res.json()["detail"] or "占用" in dup_res.json()["detail"]

        # 2.2 部分重叠：U9 (2U, 占用 U9~U10，与 U10 冲突) -> 必须被 400 拦截
        overlap_res_1 = client.post(
            "/api/assets",
            json={
                "asset_no": "DEV-TEST-COLLISION-02B",
                "name": "冲突设备-前向重叠",
                "category": "服务器",
                "location": "实训楼201-机柜A01-U9(2U)",
                "detail": {
                    "extra_params": '{"start_u": 9, "u_height": 2}'
                },
            },
        )
        assert overlap_res_1.status_code == 400
        assert "冲突" in overlap_res_1.json()["detail"] or "占用" in overlap_res_1.json()["detail"]

        # 2.3 部分重叠：U11 (2U, 占用 U11~U12，与 U11 冲突) -> 必须被 400 拦截
        overlap_res_2 = client.post(
            "/api/assets",
            json={
                "asset_no": "DEV-TEST-COLLISION-02C",
                "name": "冲突设备-后向重叠",
                "category": "服务器",
                "location": "实训楼201-机柜A01-U11(2U)",
                "detail": {
                    "extra_params": '{"start_u": 11, "u_height": 2}'
                },
            },
        )
        assert overlap_res_2.status_code == 400
        assert "冲突" in overlap_res_2.json()["detail"] or "占用" in overlap_res_2.json()["detail"]

        # 3. 录入设备 2 到完全空闲的槽位 U12~U13 (2U) -> 允许成功
        succ_res = client.post(
            "/api/assets",
            json={
                "asset_no": "DEV-TEST-COLLISION-02",
                "name": "测试计算服务器-02",
                "category": "服务器",
                "location": "实训楼201-机柜A01-U12(2U)",
                "detail": {
                    "extra_params": '{"start_u": 12, "u_height": 2}'
                },
            },
        )
        assert succ_res.status_code == 201
        asset2_id = succ_res.json()["id"]

        # 4. 修改设备 1：仅修改参数/名称，槽位仍保持 U10 (排除自身占用) -> 允许成功！
        update_self_res = client.patch(
            f"/api/assets/{asset1_id}",
            json={
                "name": "测试计算服务器-01-已重命名",
                "specs": "128G RAM",
            },
        )
        assert update_self_res.status_code == 200
        assert update_self_res.json()["name"] == "测试计算服务器-01-已重命名"

        # 5. 修改设备 1：试图将槽位改为已被设备 2 占用的 U12 (2U) -> 必须被 400 拦截！
        update_conflict_res = client.patch(
            f"/api/assets/{asset1_id}",
            json={
                "location": "实训楼201-机柜A01-U12(2U)",
                "detail": {
                    "extra_params": '{"start_u": 12, "u_height": 2}'
                },
            },
        )
        assert update_conflict_res.status_code == 400
        assert "冲突" in update_conflict_res.json()["detail"] or "占用" in update_conflict_res.json()["detail"]

        # 6. 修改设备 1：移动到全新的空闲槽位 U15 (2U) -> 允许成功！
        update_free_res = client.patch(
            f"/api/assets/{asset1_id}",
            json={
                "location": "实训楼201-机柜A01-U15(2U)",
                "detail": {
                    "extra_params": '{"start_u": 15, "u_height": 2}'
                },
            },
        )
        assert update_free_res.status_code == 200
        assert "U15" in update_free_res.json()["location"]

        # 7. 越界检查：42U 机柜试图在 U42 放置 2U 设备 (跨至 U43) -> 必须被 400 拦截！
        out_of_bounds_res = client.post(
            "/api/assets",
            json={
                "asset_no": "DEV-TEST-COLLISION-OUT",
                "name": "越界超载设备",
                "category": "服务器",
                "location": "实训楼201-机柜A01-U42(2U)",
                "detail": {
                    "extra_params": '{"start_u": 42, "u_height": 2}'
                },
            },
        )
        assert out_of_bounds_res.status_code == 400
        assert "超出" in out_of_bounds_res.json()["detail"] or "容量" in out_of_bounds_res.json()["detail"]

    finally:
        # 清理测试数据
        if asset1_id:
            client.delete(f"/api/assets/{asset1_id}")
        if asset2_id:
            client.delete(f"/api/assets/{asset2_id}")

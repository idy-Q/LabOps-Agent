import re
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import ServerRoom, ServerRack, Asset
from app.schemas.room import RoomCreate, RoomUpdate, RoomResponse

router = APIRouter()


def is_asset_in_room(loc: str, room_code: str, room_name: str = "") -> bool:
    """判断资产物理位置字符串是否归属于指定机房（支持严格边界匹配与单数字防穿透防护）"""
    if not loc or not room_code:
        return False

    loc_strip = loc.strip()
    r_code_strip = room_code.strip()

    # 1. 严格全字匹配标准带前缀 room_code（如 ROOM-201, ROOM-1 等）
    if r_code_strip.upper().startswith("ROOM-"):
        pattern = rf"(^|[^a-zA-Z0-9_-]){re.escape(r_code_strip)}([^a-zA-Z0-9_-]|$)"
        if re.search(pattern, loc_strip, re.IGNORECASE):
            return True

    # 2. room_name 具备足够专有区分度时的语义匹配
    # 严格排除单字符、纯数字或无特征词（如 '1', '2', '402', '机房', '实验室'），防止灾难性子串误匹配
    if room_name:
        rn_strip = room_name.strip()
        if len(rn_strip) >= 3 and not rn_strip.isdigit() and rn_strip not in ("机房", "实验室", "实训室", "办公室", "设备间"):
            if rn_strip in loc_strip:
                return True

    # 3. 提取房间数字编号 (如 ROOM-201 -> 201, 101 -> 101, 1 -> 1)
    room_num = r_code_strip.upper().replace("ROOM-", "").strip()
    if not room_num:
        return False

    # 3.1 针对 1~2 位超短房间号（如 '1', '2', '01'）：
    # 极其严格：必须带明确的房间实体后缀（'1室', '1机房', '1实验室'）或以 '1-' 作为位置开头，严格排除 '1层', '1楼', 'U1', 'A01'
    if len(room_num) <= 2:
        pattern_short = rf"(^|[^a-zA-Z0-9_\u4e00-\u9fa5]|实训楼){re.escape(room_num)}(室|机房|实验室|实训室)"
        if re.search(pattern_short, loc_strip, re.IGNORECASE):
            return True
        if re.match(rf"^{re.escape(room_num)}-(机柜|核心柜|配电柜|网络柜)", loc_strip):
            return True
        return False

    # 3.2 针对标准 3 位及以上房间号（如 101, 201, 402 等）：
    # 匹配标准前缀 '实训楼201-' 或 '实训楼201' 且尾部非数字
    if re.search(rf"实训楼{re.escape(room_num)}([^0-9]|$)", loc_strip, re.IGNORECASE):
        return True
    # 匹配 '201室'、'201机房'、'201实验室'、'201实训室'
    if re.search(rf"(^|[^0-9]){re.escape(room_num)}(室|机房|实验室|实训室)", loc_strip, re.IGNORECASE):
        return True
    # 匹配独立分段如 '201-机柜A01' 或开头 '201-'
    if re.search(rf"(^|[^0-9]){re.escape(room_num)}-", loc_strip, re.IGNORECASE):
        return True

    return False


@router.get(
    "",
    response_model=List[RoomResponse],
    include_in_schema=False,
)
@router.get(
    "/",
    response_model=List[RoomResponse],
    summary="查询全量机房列表",
    description="获取所有物理机房台账及其实时在册机柜总数",
)
def list_rooms(db: Session = Depends(get_db)) -> List[RoomResponse]:
    rooms = db.query(ServerRoom).order_by(ServerRoom.room_code).all()
    for r in rooms:
        r.total_racks = db.query(ServerRack).filter(ServerRack.room_code == r.room_code).count()
    return rooms


@router.get(
    "/{room_code}",
    response_model=RoomResponse,
    summary="获取指定机房信息",
    description="根据机房编号获取特定机房的详细台账信息",
)
def get_room(room_code: str, db: Session = Depends(get_db)) -> RoomResponse:
    room = db.query(ServerRoom).filter(ServerRoom.room_code == room_code).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"机房编号 {room_code} 不存在",
        )
    room.total_racks = db.query(ServerRack).filter(ServerRack.room_code == room.room_code).count()
    return room


@router.post(
    "",
    response_model=RoomResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
@router.post(
    "/",
    response_model=RoomResponse,
    status_code=status.HTTP_201_CREATED,
    summary="新增机房区域",
    description="录入新的机房空间，包括机房编号、名称、物理位置、责任教师与配电容量",
)
def create_room(payload: RoomCreate, db: Session = Depends(get_db)) -> RoomResponse:
    clean_code = payload.room_code.strip()
    exists = db.query(ServerRoom).filter(ServerRoom.room_code == clean_code).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"机房编号 {clean_code} 已存在，请勿重复创建",
        )

    # 物理位置全局唯一性校验
    clean_loc = payload.location.strip()
    if clean_loc:
        existing_loc = db.query(ServerRoom).filter(ServerRoom.location == clean_loc).first()
        if existing_loc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"机房物理位置 '{clean_loc}' 已被机房 [{existing_loc.room_code}] ({existing_loc.room_name}) 登记占用，物理位置不可重复！",
            )

    room = ServerRoom(
        room_code=clean_code,
        room_name=payload.room_name.strip(),
        location=clean_loc,
        manager_teacher=payload.manager_teacher.strip(),
        power_capacity_kw=payload.power_capacity_kw,
        total_racks=0,
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    room.total_racks = 0
    return room


@router.put(
    "/{room_code}",
    response_model=RoomResponse,
    summary="编辑机房信息",
    description="修改机房名称、物理位置、责任教师与额定配电容量",
)
def update_room(
    room_code: str,
    payload: RoomUpdate,
    db: Session = Depends(get_db),
) -> RoomResponse:
    room = db.query(ServerRoom).filter(ServerRoom.room_code == room_code).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"机房编号 {room_code} 不存在",
        )

    update_data = payload.model_dump(exclude_unset=True)

    # 物理位置修改唯一性排他校验 (排除当前机房自身)
    if "location" in update_data and update_data["location"]:
        clean_loc = update_data["location"].strip()
        existing_loc = (
            db.query(ServerRoom)
            .filter(ServerRoom.location == clean_loc, ServerRoom.room_code != room.room_code)
            .first()
        )
        if existing_loc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"机房物理位置 '{clean_loc}' 已被其他机房 [{existing_loc.room_code}] ({existing_loc.room_name}) 登记占用，物理位置不可重复！",
            )
        update_data["location"] = clean_loc

    for field, val in update_data.items():
        setattr(room, field, val)

    db.commit()
    db.refresh(room)
    room.total_racks = db.query(ServerRack).filter(ServerRack.room_code == room.room_code).count()
    return room


@router.delete(
    "/{room_code}",
    summary="注销删除机房",
    description="删除指定机房。若该机房下仍有在册机柜或在架/周边资产，安全联锁触发阻断注销",
)
def delete_room(room_code: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    room = db.query(ServerRoom).filter(ServerRoom.room_code == room_code).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"机房编号 {room_code} 不存在",
        )

    # 1. 安全联锁检查：是否仍有在册机柜
    racks_count = db.query(ServerRack).filter(ServerRack.room_code == room_code).count()

    # 2. 安全联锁检查：是否仍有资产归属于该机房
    all_assets = db.query(Asset).all()
    room_assets = [
        a for a in all_assets
        if is_asset_in_room(a.location, room_code, room.room_name)
    ]

    if racks_count > 0 or len(room_assets) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该机房下仍有在册机柜或资产，请先腾退清空后再注销机房",
        )

    db.delete(room)
    db.commit()
    return {"message": f"机房 {room_code} 已成功注销删除"}

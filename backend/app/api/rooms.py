import re
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import ServerRoom, ServerRack, Asset
from app.schemas.room import RoomCreate, RoomUpdate, RoomResponse

router = APIRouter()


def is_asset_in_room(loc: str, room_code: str, room_name: str = "") -> bool:
    """判断资产物理位置字符串是否归属于指定机房（支持严格边界匹配，防止 ROOM-2 误匹配 ROOM-201）"""
    if not loc:
        return False
    # 1. 严格边界匹配 room_code，防止 ROOM-2 误匹配 ROOM-201
    if re.search(rf"(^|[^a-zA-Z0-9]){re.escape(room_code)}([^a-zA-Z0-9]|$)", loc, re.IGNORECASE):
        return True
    if room_name and room_name in loc:
        return True
    room_num = room_code.replace("ROOM-", "").strip()
    if room_num:
        # 2. 匹配标准实训楼前缀：如 '实训楼201-'，要求尾部为非字母数字边界
        if re.search(rf"实训楼{re.escape(room_num)}([^a-zA-Z0-9]|$)", loc, re.IGNORECASE):
            return True
        # 3. 匹配 '201室' 或 '201机房'
        if re.search(rf"(^|[^a-zA-Z0-9]){re.escape(room_num)}(室|机房)", loc, re.IGNORECASE):
            return True
        # 4. 独立房间编号边界匹配：如 '201-机柜A01'
        if re.search(rf"(^|[^a-zA-Z0-9]){re.escape(room_num)}([^a-zA-Z0-9]|$)", loc, re.IGNORECASE):
            return True
    return False


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
    "/",
    response_model=RoomResponse,
    status_code=status.HTTP_201_CREATED,
    summary="新增机房区域",
    description="录入新的机房空间，包括机房编号、名称、物理位置、责任教师与配电容量",
)
def create_room(payload: RoomCreate, db: Session = Depends(get_db)) -> RoomResponse:
    exists = db.query(ServerRoom).filter(ServerRoom.room_code == payload.room_code).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"机房编号 {payload.room_code} 已存在，请勿重复创建",
        )

    room = ServerRoom(
        room_code=payload.room_code,
        room_name=payload.room_name,
        location=payload.location,
        manager_teacher=payload.manager_teacher,
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

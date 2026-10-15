import json
import re
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import ServerRoom, ServerRack, Asset
from app.schemas.rack import RackCreate, RackUpdate, RackResponse

router = APIRouter()


def is_asset_in_rack(loc: str, rack_id: str) -> bool:
    """判断资产物理位置字符串是否明确归属于指定机柜（严格边界匹配，防止 机柜A1 误匹配 机柜A10）"""
    if not loc or not rack_id:
        return False
    return bool(re.search(rf"(^|[-_ ]){re.escape(rack_id)}([-_ ]|$)", loc))


@router.get(
    "",
    response_model=List[RackResponse],
    include_in_schema=False,
)
@router.get(
    "/",
    response_model=List[RackResponse],
    summary="查询机柜列表",
    description="获取所有在册标准机柜，支持按机房编号进行过滤",
)
def list_racks(
    room_code: Optional[str] = Query(default=None, description="按机房编号过滤，如 ROOM-201"),
    db: Session = Depends(get_db),
) -> List[RackResponse]:
    query = db.query(ServerRack)
    if room_code:
        query = query.filter(ServerRack.room_code == room_code)
    return query.order_by(ServerRack.rack_id).all()


@router.get(
    "/{rack_id}",
    response_model=RackResponse,
    summary="获取指定机柜详情",
    description="根据机柜编号获取特定机柜的详细物理参数",
)
def get_rack(rack_id: str, db: Session = Depends(get_db)) -> RackResponse:
    rack = db.query(ServerRack).filter(ServerRack.rack_id == rack_id).first()
    if not rack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"机柜编号 {rack_id} 不存在",
        )
    return rack


@router.post(
    "",
    response_model=RackResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
@router.post(
    "/",
    response_model=RackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="新增机柜",
    description="在指定机房内立项新增标准工业机柜，包括机柜编号、名称、U位容量及额定功耗",
)
def create_rack(payload: RackCreate, db: Session = Depends(get_db)) -> RackResponse:
    # 验证所属机房是否存在
    room = db.query(ServerRoom).filter(ServerRoom.room_code == payload.room_code).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"所属机房 {payload.room_code} 不存在，无法创建机柜",
        )

    # 验证机柜编号唯一性
    exists = db.query(ServerRack).filter(ServerRack.rack_id == payload.rack_id).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"机柜编号 {payload.rack_id} 已存在，请勿重复创建",
        )

    rack = ServerRack(
        rack_id=payload.rack_id,
        rack_name=payload.rack_name,
        room_code=payload.room_code,
        total_u=payload.total_u,
        power_rating_w=payload.power_rating_w,
    )
    db.add(rack)
    db.commit()
    db.refresh(rack)

    # 联动更新所属机房 total_racks
    room.total_racks = db.query(ServerRack).filter(ServerRack.room_code == room.room_code).count()
    db.commit()

    return rack


@router.put(
    "/{rack_id}",
    response_model=RackResponse,
    summary="编辑机柜参数",
    description="修改机柜显示名称、所属机房、总U位与额定功耗",
)
def update_rack(
    rack_id: str,
    payload: RackUpdate,
    db: Session = Depends(get_db),
) -> RackResponse:
    rack = db.query(ServerRack).filter(ServerRack.rack_id == rack_id).first()
    if not rack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"机柜编号 {rack_id} 不存在",
        )

    old_room_code = rack.room_code
    update_data = payload.model_dump(exclude_unset=True)

    # 1. 跨机房迁移机柜安全校验
    if "room_code" in update_data and update_data["room_code"] != old_room_code:
        new_room = db.query(ServerRoom).filter(ServerRoom.room_code == update_data["room_code"]).first()
        if not new_room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"目标机房 {update_data['room_code']} 不存在",
            )
        # 安全联锁：若机柜内仍有在架设备，阻断跨机房直接迁移
        all_assets = db.query(Asset).all()
        assets_in_rack = [a for a in all_assets if is_asset_in_rack(a.location, rack_id)]
        if len(assets_in_rack) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该机柜内尚有 {len(assets_in_rack)} 台在架设备，不可直接跨机房迁移机柜，请先清退柜内设备或逐台调拨后再行迁移",
            )

    # 2. 槽位容量压缩边界防护校验
    if "total_u" in update_data and update_data["total_u"] is not None:
        new_total_u = update_data["total_u"]
        all_assets = db.query(Asset).all()
        assets_in_rack = [a for a in all_assets if is_asset_in_rack(a.location, rack_id)]
        for a in assets_in_rack:
            st = 1
            h = 1
            if a.detail and a.detail.extra_params:
                try:
                    ep = json.loads(a.detail.extra_params)
                    st = int(ep.get("start_u", 1))
                    h = int(ep.get("u_height", 1))
                except Exception:
                    pass
            else:
                m_u = re.search(r"-U(\d+)", a.location or "")
                if m_u:
                    st = int(m_u.group(1))
                m_h = re.search(r"\((\d+)U\)", a.location or "")
                if m_h:
                    h = int(m_h.group(1))
            top_u = st + h - 1
            if top_u > new_total_u:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"无法将机柜容量调整为 {new_total_u}U，柜内设备 {a.asset_no} (占用至 U{top_u}) 超出新容量空间，请先调整在架设备后再缩小机柜容量",
                )

    for field, val in update_data.items():
        setattr(rack, field, val)

    db.commit()
    db.refresh(rack)

    # 若所属机房变更，同步更新新旧机房 total_racks
    if rack.room_code != old_room_code:
        old_room = db.query(ServerRoom).filter(ServerRoom.room_code == old_room_code).first()
        if old_room:
            old_room.total_racks = db.query(ServerRack).filter(ServerRack.room_code == old_room_code).count()
        new_room = db.query(ServerRoom).filter(ServerRoom.room_code == rack.room_code).first()
        if new_room:
            new_room.total_racks = db.query(ServerRack).filter(ServerRack.room_code == rack.room_code).count()
        db.commit()

    return rack


@router.delete(
    "/{rack_id}",
    summary="下线删除机柜",
    description="删除指定机柜。若该机柜内仍有在架设备，安全联锁触发阻断下线",
)
def delete_rack(rack_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    rack = db.query(ServerRack).filter(ServerRack.rack_id == rack_id).first()
    if not rack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"机柜编号 {rack_id} 不存在",
        )

    # 安全联锁检查：机柜内是否仍有在架设备（采用严格边界判定）
    all_assets = db.query(Asset).all()
    assets_in_rack = [
        a for a in all_assets
        if is_asset_in_rack(a.location, rack_id)
    ]

    if len(assets_in_rack) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"该机柜内尚有 {len(assets_in_rack)} 台在架设备，请先将设备拖拽迁出至其他机柜或下架后再下线该机柜",
        )

    room_code = rack.room_code
    db.delete(rack)
    db.commit()

    # 联动更新所属机房 total_racks
    room = db.query(ServerRoom).filter(ServerRoom.room_code == room_code).first()
    if room:
        room.total_racks = db.query(ServerRack).filter(ServerRack.room_code == room_code).count()
        db.commit()

    return {"message": f"机柜 {rack_id} 已成功下线注销"}

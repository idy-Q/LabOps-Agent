"""机房资产设备 RESTful API 路由"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from app.db.session import get_db
from app.db.models import Asset
from app.schemas.asset import (
    AssetCreate,
    AssetUpdate,
    AssetResponse,
    HealthStatusType,
    BorrowStatusType,
)

router = APIRouter()


@router.get(
    "/",
    response_model=List[AssetResponse],
    summary="查询资产台账列表",
    description="支持按分类、位置、健康状态、借用状态以及关键词组合过滤。",
)
def list_assets(
    category: Optional[str] = Query(default=None, description="按设备分类过滤"),
    location: Optional[str] = Query(default=None, description="按机房位置模糊过滤"),
    health_status: Optional[HealthStatusType] = Query(default=None, description="按健康状态过滤"),
    borrow_status: Optional[BorrowStatusType] = Query(default=None, description="按借用状态过滤"),
    keyword: Optional[str] = Query(default=None, description="按编号或名称关键词搜索"),
    skip: int = Query(default=0, ge=0, description="分页起始偏移量"),
    limit: int = Query(default=50, ge=1, le=100, description="每页条目数"),
    db: Session = Depends(get_db),
):
    query = db.query(Asset)
    if category:
        query = query.filter(Asset.category == category)
    if location:
        query = query.filter(Asset.location.contains(location))
    if health_status:
        query = query.filter(Asset.health_status == health_status)
    if borrow_status:
        query = query.filter(Asset.borrow_status == borrow_status)
    if keyword:
        query = query.filter(
            or_(
                Asset.asset_no.contains(keyword),
                Asset.name.contains(keyword),
            )
        )

    assets = query.order_by(desc(Asset.created_at)).offset(skip).limit(limit).all()
    return assets


@router.post(
    "/",
    response_model=AssetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="新增机房资产设备",
    description="录入新资产设备，要求资产编号 asset_no 全局唯一。",
)
def create_asset(
    asset_in: AssetCreate,
    db: Session = Depends(get_db),
):
    # 校验编号唯一性
    existing = db.query(Asset).filter(Asset.asset_no == asset_in.asset_no).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"资产编号 '{asset_in.asset_no}' 已存在，不能重复添加",
        )

    asset = Asset(
        asset_no=asset_in.asset_no,
        name=asset_in.name,
        category=asset_in.category,
        location=asset_in.location,
        health_status=asset_in.health_status or "HEALTHY",
        borrow_status=asset_in.borrow_status or "AVAILABLE",
        borrower=asset_in.borrower,
        specs=asset_in.specs,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@router.get(
    "/{asset_id}",
    response_model=AssetResponse,
    summary="获取单个资产详情",
)
def get_asset(
    asset_id: int,
    db: Session = Depends(get_db),
):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID 为 {asset_id} 的资产不存在",
        )
    return asset


@router.patch(
    "/{asset_id}",
    response_model=AssetResponse,
    summary="更新资产状态与信息",
    description="支持更新资产借还状态、借用人、健康状态、物理位置或硬件规格等。",
)
def update_asset(
    asset_id: int,
    asset_update: AssetUpdate,
    db: Session = Depends(get_db),
):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID 为 {asset_id} 的资产不存在",
        )

    update_data = asset_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(asset, field, value)

    db.commit()
    db.refresh(asset)
    return asset


@router.delete(
    "/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除资产记录",
)
def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),
):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID 为 {asset_id} 的资产不存在",
        )
    db.delete(asset)
    db.commit()
    return None

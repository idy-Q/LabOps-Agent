"""机房资产设备与硬件详细参数 RESTful API 路由"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, or_
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.db.models import Asset, AssetDetail
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
    description="支持按资产编号、分类、位置、健康状态、借用状态以及关键词组合过滤，自动级联加载硬件物理规格参数。",
)
def list_assets(
    asset_no: Optional[str] = Query(default=None, description="按资产编号精确过滤"),
    category: Optional[str] = Query(default=None, description="按设备分类过滤"),
    location: Optional[str] = Query(default=None, description="按机房位置模糊过滤"),
    health_status: Optional[HealthStatusType] = Query(default=None, description="按健康状态过滤"),
    borrow_status: Optional[BorrowStatusType] = Query(default=None, description="按借用状态过滤"),
    keyword: Optional[str] = Query(default=None, description="按编号、名称或规格关键词搜索"),
    skip: int = Query(default=0, ge=0, description="分页起始偏移量"),
    limit: int = Query(default=50, ge=1, le=100, description="每页条目数"),
    db: Session = Depends(get_db),
):
    query = db.query(Asset).options(joinedload(Asset.detail))
    if asset_no:
        query = query.filter(Asset.asset_no == asset_no)
    if category:
        query = query.filter(Asset.category == category)
    if location:
        query = query.filter(Asset.location.contains(location))
    if health_status:
        query = query.filter(Asset.health_status == health_status)
    if borrow_status:
        query = query.filter(Asset.borrow_status == borrow_status)
    if keyword:
        kw = keyword.strip()
        query = query.filter(
            or_(
                Asset.asset_no.contains(kw),
                Asset.name.contains(kw),
            )
        )

    assets = (
        query.order_by(desc(Asset.created_at), desc(Asset.id))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return assets


@router.post(
    "/",
    response_model=AssetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="新增机房资产设备与硬件参数",
    description="录入新资产设备，要求资产编号 asset_no 全局唯一，支持同步录入硬件物理参数。",
)
def create_asset(
    asset_in: AssetCreate,
    db: Session = Depends(get_db),
):
    # 校验编号唯一性
    clean_no = asset_in.asset_no.strip()
    existing = db.query(Asset).filter(Asset.asset_no == clean_no).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"资产编号 '{clean_no}' 已存在，不能重复添加",
        )

    asset = Asset(
        asset_no=clean_no,
        name=asset_in.name.strip(),
        category=asset_in.category.strip(),
        location=asset_in.location.strip(),
        health_status=asset_in.health_status or "HEALTHY",
        borrow_status=asset_in.borrow_status or "AVAILABLE",
        borrower=asset_in.borrower,
        specs=asset_in.specs,
    )

    try:
        db.add(asset)
        db.flush()  # 生成 asset.id

        # 如果提供了硬件详细参数，创建 AssetDetail
        if asset_in.detail is not None:
            detail_data = asset_in.detail.model_dump(exclude_unset=True)
            asset_detail = AssetDetail(
                asset_id=asset.id,
                **detail_data,
            )
            db.add(asset_detail)

        db.commit()
        db.refresh(asset)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"资产编号 '{clean_no}' 已存在或数据冲突",
        )
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"录入设备失败: {str(exc)}",
        )
    return asset


@router.get(
    "/{asset_id}",
    response_model=AssetResponse,
    summary="获取单个资产全景详情",
    description="获取指定资产的基础台账与其关联的全部硬件规格参数。",
)
def get_asset(
    asset_id: int,
    db: Session = Depends(get_db),
):
    asset = (
        db.query(Asset)
        .options(joinedload(Asset.detail))
        .filter(Asset.id == asset_id)
        .first()
    )
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID 为 {asset_id} 的资产不存在",
        )
    return asset


@router.patch(
    "/{asset_id}",
    response_model=AssetResponse,
    summary="更新资产状态与硬件详细参数",
    description="支持更新资产基础属性（借还状态、健康度、位置、规格等）以及硬件参数（CPU、内存、存储、GPU、管理IP等）。",
)
def update_asset(
    asset_id: int,
    asset_update: AssetUpdate,
    db: Session = Depends(get_db),
):
    asset = (
        db.query(Asset)
        .options(joinedload(Asset.detail))
        .filter(Asset.id == asset_id)
        .first()
    )
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID 为 {asset_id} 的资产不存在",
        )

    update_data = asset_update.model_dump(exclude_unset=True)
    detail_data = update_data.pop("detail", None)

    # 1. 更新主表字段
    for field, value in update_data.items():
        setattr(asset, field, value)

    # 2. 更新或新建从表 AssetDetail 字段
    if detail_data is not None:
        if asset.detail:
            for d_field, d_value in detail_data.items():
                setattr(asset.detail, d_field, d_value)
        else:
            new_detail = AssetDetail(asset_id=asset.id, **detail_data)
            db.add(new_detail)

    try:
        db.commit()
        db.refresh(asset)
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新资产信息失败: {str(exc)}",
        )
    return asset


@router.delete(
    "/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="安全删除资产记录",
    description="删除指定资产，若设备正处于借出中 (IN_USE) 将阻断删除，并级联清理关联的硬件详细参数。",
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

    try:
        db.delete(asset)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除资产失败: {str(exc)}",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)

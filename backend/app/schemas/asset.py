"""资产设备数据模式 (Pydantic Schemas)"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field


HealthStatusType = Literal["HEALTHY", "WARNING", "OVERHEAT", "OFFLINE"]
BorrowStatusType = Literal["AVAILABLE", "IN_USE", "MAINTENANCE"]


class AssetBase(BaseModel):
    """机房资产设备基础属性"""

    asset_no: str = Field(..., description="资产唯一编号，如 DEV-SRV-201", min_length=1, max_length=64)
    name: str = Field(..., description="设备名称", min_length=1, max_length=128)
    category: str = Field(..., description="设备类别 (服务器/网络设备/实验教学/配电温控)", min_length=1, max_length=64)
    location: str = Field(..., description="机房物理位置", min_length=1, max_length=128)
    health_status: HealthStatusType = Field(default="HEALTHY", description="设备健康状态")
    borrow_status: BorrowStatusType = Field(default="AVAILABLE", description="设备借还/占用状态")
    borrower: Optional[str] = Field(default=None, description="借用人或使用部门")
    specs: Optional[str] = Field(default=None, description="硬件规格参数说明")


class AssetCreate(AssetBase):
    """资产创建请求模型"""
    pass


class AssetUpdate(BaseModel):
    """资产更新请求模型 (所有字段均可选)"""

    name: Optional[str] = Field(default=None, min_length=1, max_length=128)
    category: Optional[str] = Field(default=None, min_length=1, max_length=64)
    location: Optional[str] = Field(default=None, min_length=1, max_length=128)
    health_status: Optional[HealthStatusType] = Field(default=None)
    borrow_status: Optional[BorrowStatusType] = Field(default=None)
    borrower: Optional[str] = Field(default=None)
    specs: Optional[str] = Field(default=None)


class AssetResponse(AssetBase):
    """资产详情响应模型"""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

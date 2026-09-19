"""资产设备与硬件详细参数数据模式 (Pydantic Schemas)"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field


HealthStatusType = Literal["HEALTHY", "WARNING", "OVERHEAT", "OFFLINE"]
BorrowStatusType = Literal["AVAILABLE", "IN_USE", "MAINTENANCE"]


# =====================================================================
# 设备硬件物理规格与详细参数 Schemas
# =====================================================================

class AssetDetailBase(BaseModel):
    """设备硬件详细参数基础属性"""

    serial_number: Optional[str] = Field(default=None, description="出厂硬件序列号 (SN)", max_length=64)
    brand: Optional[str] = Field(default=None, description="厂商品牌", max_length=64)
    model_name: Optional[str] = Field(default=None, description="设备具体型号", max_length=128)
    os_firmware: Optional[str] = Field(default=None, description="操作系统或固件版本", max_length=128)
    mac_address: Optional[str] = Field(default=None, description="主网卡物理MAC地址", max_length=64)
    management_ip: Optional[str] = Field(default=None, description="带外/管理IP地址", max_length=64)

    # 核心计算与物理参数
    cpu_info: Optional[str] = Field(default=None, description="CPU处理器规格及核心数", max_length=255)
    memory_info: Optional[str] = Field(default=None, description="内存容量及类型", max_length=255)
    storage_info: Optional[str] = Field(default=None, description="磁盘存储与RAID阵列", max_length=255)
    gpu_info: Optional[str] = Field(default=None, description="GPU/加速卡配置", max_length=255)
    network_interfaces: Optional[str] = Field(default=None, description="网络端口与传输速率", max_length=255)
    power_supply: Optional[str] = Field(default=None, description="供电与功耗规格", max_length=128)

    # 维保与商务信息
    purchase_date: Optional[str] = Field(default=None, description="采购投产日期", max_length=32)
    warranty_period: Optional[str] = Field(default=None, description="维保期限与到期日", max_length=64)
    supplier: Optional[str] = Field(default=None, description="供应商与技术支持电话", max_length=128)

    # 扩展定制参数
    extra_params: Optional[str] = Field(default=None, description="各类设备定制参数(JSON格式)")

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class AssetDetailCreate(AssetDetailBase):
    """创建资产时可选附加的硬件详细参数"""
    pass


class AssetDetailUpdate(AssetDetailBase):
    """更新资产硬件详细参数 (所有字段均可选)"""
    pass


class AssetDetailResponse(AssetDetailBase):
    """资产硬件详细参数响应模型"""

    id: int
    asset_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =====================================================================
# 资产主表 Schemas
# =====================================================================

class AssetBase(BaseModel):
    """机房资产设备基础属性"""

    asset_no: str = Field(..., description="资产唯一编号，如 DEV-SRV-201", min_length=1, max_length=64)
    name: str = Field(..., description="设备名称", min_length=1, max_length=128)
    category: str = Field(..., description="设备类别 (服务器/网络设备/实验教学/配电温控)", min_length=1, max_length=64)
    location: str = Field(..., description="机房物理位置", min_length=1, max_length=128)
    health_status: HealthStatusType = Field(default="HEALTHY", description="设备健康状态")
    borrow_status: BorrowStatusType = Field(default="AVAILABLE", description="设备借还/占用状态")
    borrower: Optional[str] = Field(default=None, description="借用人或使用部门")
    specs: Optional[str] = Field(default=None, description="硬件规格参数简要说明")

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class AssetCreate(AssetBase):
    """资产创建请求模型 (支持同步附带硬件物理参数)"""

    detail: Optional[AssetDetailCreate] = Field(default=None, description="设备硬件详细参数")


class AssetUpdate(BaseModel):
    """资产更新请求模型 (所有字段均可选)"""

    name: Optional[str] = Field(default=None, min_length=1, max_length=128)
    category: Optional[str] = Field(default=None, min_length=1, max_length=64)
    location: Optional[str] = Field(default=None, min_length=1, max_length=128)
    health_status: Optional[HealthStatusType] = Field(default=None)
    borrow_status: Optional[BorrowStatusType] = Field(default=None)
    borrower: Optional[str] = Field(default=None)
    specs: Optional[str] = Field(default=None)
    detail: Optional[AssetDetailUpdate] = Field(default=None, description="设备硬件详细参数")

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class AssetResponse(AssetBase):
    """资产详情响应模型 (包含级联加载的硬件详细参数)"""

    id: int
    created_at: datetime
    updated_at: datetime
    detail: Optional[AssetDetailResponse] = Field(default=None, description="设备硬件详细参数")

    model_config = ConfigDict(from_attributes=True)

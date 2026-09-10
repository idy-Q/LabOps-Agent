"""机房运行健康监控指标大盘 API 路由"""

import logging
from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Asset, Ticket
from app.tools.metric_tools import get_server_metrics

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/summary",
    summary="获取机房运行监控综合大盘数据",
    description="聚合计算全机房资产健康率、能耗负荷、工单状态流转统计及核心服务器硬件实时探针数据",
)
def get_metrics_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """生成机房综合大盘实时感知指标"""
    # 1. 资产状态全景统计
    total_assets = db.query(Asset).count()
    healthy_assets = db.query(Asset).filter(Asset.health_status == "HEALTHY").count()
    warning_assets = db.query(Asset).filter(Asset.health_status == "WARNING").count()
    overheat_assets = db.query(Asset).filter(Asset.health_status == "OVERHEAT").count()
    offline_assets = db.query(Asset).filter(Asset.health_status == "OFFLINE").count()

    in_use_assets = db.query(Asset).filter(Asset.borrow_status == "IN_USE").count()
    available_assets = db.query(Asset).filter(Asset.borrow_status == "AVAILABLE").count()
    maintenance_assets = db.query(Asset).filter(Asset.borrow_status == "MAINTENANCE").count()

    # 2. 工单流转全景统计
    total_tickets = db.query(Ticket).count()
    pending_tickets = db.query(Ticket).filter(Ticket.status == "PENDING").count()
    processing_tickets = db.query(Ticket).filter(Ticket.status == "PROCESSING").count()
    resolved_tickets = db.query(Ticket).filter(Ticket.status == "RESOLVED").count()
    closed_tickets = db.query(Ticket).filter(Ticket.status == "CLOSED").count()

    # 3. 核心节点硬件探针实时数据
    core_devices = (
        db.query(Asset)
        .filter(Asset.category.in_(["服务器", "网络设备", "配电温控"]))
        .order_by(Asset.id.asc())
        .limit(6)
        .all()
    )

    node_metrics: List[Dict[str, Any]] = []
    temperatures: List[float] = []
    cpu_loads: List[float] = []
    total_power_watts: int = 0

    for dev in core_devices:
        metric = get_server_metrics(dev.asset_no, db=db)
        if metric.get("status") == "success":
            node_metrics.append(metric)
            temperatures.append(float(metric.get("temperature", 30.0)))
            cpu_loads.append(float(metric.get("cpu_usage", 20.0)))
            total_power_watts += int(metric.get("power_watts", 200))

    # 计算全局健康度与均值
    avg_temperature = round(sum(temperatures) / len(temperatures), 1) if temperatures else 24.5
    avg_cpu_load = round(sum(cpu_loads) / len(cpu_loads), 1) if cpu_loads else 40.0
    health_rate = round((healthy_assets / total_assets * 100) if total_assets > 0 else 100.0, 1)

    return {
        "status": "success",
        "data": {
            "overview": {
                "avg_temperature": avg_temperature,
                "avg_cpu_load": avg_cpu_load,
                "total_power_watts": total_power_watts,
                "system_health_rate": health_rate,
                "active_alerts_count": warning_assets + overheat_assets + offline_assets,
            },
            "assets": {
                "total": total_assets,
                "healthy": healthy_assets,
                "warning": warning_assets,
                "overheat": overheat_assets,
                "offline": offline_assets,
                "in_use": in_use_assets,
                "available": available_assets,
                "maintenance": maintenance_assets,
            },
            "tickets": {
                "total": total_tickets,
                "pending": pending_tickets,
                "processing": processing_tickets,
                "resolved": resolved_tickets,
                "closed": closed_tickets,
            },
            "nodes": node_metrics,
        },
    }

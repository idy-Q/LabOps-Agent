"""数据库初始化与测试种子数据填充脚本"""

import logging
from sqlalchemy import select
from app.db.session import engine, SessionLocal, Base
from app.db.models import Ticket, Asset, AuditLog, ChatHistory

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# 预置 5 条典型机房资产种子数据
SEED_ASSETS = [
    {
        "asset_no": "DEV-SRV-201",
        "name": "2号机房-GPU计算节点01",
        "category": "服务器",
        "location": "实训楼201-机柜A01",
        "health_status": "OVERHEAT",
        "borrow_status": "IN_USE",
        "borrower": "人工智能科研组",
        "specs": "2x Intel Xeon Gold 6330, 256GB RAM, 4x NVIDIA RTX 4090 24G",
    },
    {
        "asset_no": "DEV-SRV-202",
        "name": "2号机房-CPU计算节点02",
        "category": "服务器",
        "location": "实训楼201-机柜A02",
        "health_status": "HEALTHY",
        "borrow_status": "AVAILABLE",
        "borrower": None,
        "specs": "2x AMD EPYC 7763, 512GB RAM, 2TB NVMe SSD",
    },
    {
        "asset_no": "DEV-NET-301",
        "name": "核心主干路由交换机01",
        "category": "网络设备",
        "location": "实训楼201-网络核心柜",
        "health_status": "HEALTHY",
        "borrow_status": "IN_USE",
        "borrower": "网络中心",
        "specs": "48口万兆SFP+ 光纤核心交换机 Huawei CloudEngine 6800",
    },
    {
        "asset_no": "DEV-LAB-105",
        "name": "网络安全渗透实验箱-A组",
        "category": "实验教学",
        "location": "实训楼105-器材柜B",
        "health_status": "HEALTHY",
        "borrow_status": "AVAILABLE",
        "borrower": None,
        "specs": "工控靶机套件 + 工业交换机 + 无线渗透嗅探适配器",
    },
    {
        "asset_no": "DEV-UPS-201",
        "name": "机房201大功率在线式UPS",
        "category": "配电温控",
        "location": "实训楼201-配电角",
        "health_status": "WARNING",
        "borrow_status": "IN_USE",
        "borrower": "机房后勤保障组",
        "specs": "APC Smart-UPS RT 10kVA 在线双变换式",
    },
]

# 预置 2 条典型运维工单种子数据
SEED_TICKETS = [
    {
        "ticket_no": "TK-20260901-001",
        "title": "2号机房GPU计算节点01核心温度过热预警",
        "description": "监控指标显示GPU温度达88℃且排风扇转速异常，已触发安全规章超温应急预警，需现场清理散热风道并检查水冷循环。",
        "priority": "HIGH",
        "status": "PROCESSING",
        "device_id": "DEV-SRV-201",
        "creator": "系统自动监控",
    },
    {
        "ticket_no": "TK-20260901-002",
        "title": "机房201在线UPS电池组定期维护巡检",
        "description": "例行按高校机房运行规章进行电池容量与逆变器状态巡查。",
        "priority": "MEDIUM",
        "status": "PENDING",
        "device_id": "DEV-UPS-201",
        "creator": "王管理员",
    },
]


def init_db(
    seed: bool = True,
    custom_engine=None,
    custom_session_factory=None,
) -> None:
    """创建表结构并可选写入种子数据 (支持自定义 engine 和 session 用于测试隔离)"""
    target_engine = custom_engine or engine
    target_session_factory = custom_session_factory or SessionLocal

    logger.info("开始初始化数据库结构...")
    Base.metadata.create_all(bind=target_engine)
    logger.info("数据库表结构校验/创建完成 (tickets, assets, audit_logs, chat_history)")

    if not seed:
        return

    db = target_session_factory()
    try:
        # 1. 种子资产数据幂等填充 (按唯一 asset_no 判定)
        added_assets = 0
        for asset_data in SEED_ASSETS:
            exists = db.query(Asset).filter(Asset.asset_no == asset_data["asset_no"]).first()
            if not exists:
                asset = Asset(**asset_data)
                db.add(asset)
                added_assets += 1
        if added_assets > 0:
            db.commit()
            logger.info("已成功预置 %d 条典型机房资产初始数据！", added_assets)
        else:
            logger.info("所有机房资产种子数据均已存在，跳过初始数据填充。")

        # 2. 种子工单数据幂等填充 (按唯一 ticket_no 判定)
        added_tickets = 0
        for ticket_data in SEED_TICKETS:
            exists = db.query(Ticket).filter(Ticket.ticket_no == ticket_data["ticket_no"]).first()
            if not exists:
                ticket = Ticket(**ticket_data)
                db.add(ticket)
                added_tickets += 1
        if added_tickets > 0:
            db.commit()
            logger.info("已成功预置 %d 条典型机房运维工单初始数据！", added_tickets)
        else:
            logger.info("所有运维工单种子数据均已存在，跳过初始数据填充。")

    except Exception as e:
        db.rollback()
        logger.error("数据库初始化种子数据失败: %s", str(e))
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    print("LabOps-Agent 数据库结构与初始化数据准备就绪。")

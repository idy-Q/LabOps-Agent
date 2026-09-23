"""机房资产借用超期智能预警与合规催告公文服务

基于第一性原理与高校仪器设备管理条例，提供：
1. 借用超期全景研判与状态动态同步 (get_overdue_assets_summary)
2. 规范级《实验室仪器设备超期使用归还催告单》红头公文生成引擎 (generate_overdue_notice)
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, desc

from app.db.models import Asset, AssetDetail, AssetBorrowLog, User


def get_overdue_assets_summary(db: Session) -> Dict[str, Any]:
    """计算全机房资产借用逾期总台数、最长逾期天数与各设备逾期明细列表

    若发现约定归还时间已过且状态仍为 BORROWING 的借调记录，动态同步更新为 OVERDUE。
    """
    now = datetime.now()

    # 1. 检索所有处于借用中或已超期状态的借还历史记录
    candidate_logs = (
        db.query(AssetBorrowLog)
        .filter(
            AssetBorrowLog.return_status.in_(["BORROWING", "OVERDUE"]),
            AssetBorrowLog.actual_return_time.is_(None),
        )
        .order_by(desc(AssetBorrowLog.borrow_time))
        .all()
    )

    overdue_logs: List[AssetBorrowLog] = []
    need_commit = False

    # 按 asset_id 进行去重（每台设备以最新的借调记录为准）
    seen_assets = set()
    for log in candidate_logs:
        if log.asset_id in seen_assets:
            continue
        seen_assets.add(log.asset_id)

        if log.expected_return_time and log.expected_return_time < now:
            # 动态原子同步状态为 OVERDUE
            if log.return_status == "BORROWING":
                log.return_status = "OVERDUE"
                need_commit = True
            overdue_logs.append(log)

    if need_commit:
        try:
            db.commit()
        except Exception:
            db.rollback()

    # 2. 组装超期设备全景详细清单
    overdue_items: List[Dict[str, Any]] = []
    max_days = 0

    for blog in overdue_logs:
        # 查询对应资产及硬件明细
        asset = (
            db.query(Asset)
            .options(joinedload(Asset.detail))
            .filter(Asset.asset_no == blog.asset_id)
            .first()
        )
        if not asset or asset.borrow_status == "AVAILABLE":
            continue

        # 查询借用人详细档案（部门、联系电话）
        user = (
            db.query(User)
            .filter(
                or_(
                    User.username == blog.borrower_username,
                    User.real_name == blog.borrower_name,
                )
            )
            .first()
        )

        delta = now - blog.expected_return_time
        days = max(1, delta.days)
        if days > max_days:
            max_days = days

        dept = (user.department if (user and user.department) else "物联网工程教研室")
        phone = (user.phone if (user and user.phone) else "13900000002")

        item = {
            "log_no": blog.log_no,
            "asset_id": asset.id,
            "asset_no": asset.asset_no,
            "name": asset.name,
            "category": asset.category,
            "location": asset.location,
            "health_status": asset.health_status,
            "borrow_status": asset.borrow_status,
            "specs": asset.specs or "",
            "brand": asset.detail.brand if (asset.detail and asset.detail.brand) else "标准配置",
            "model_name": asset.detail.model_name if (asset.detail and asset.detail.model_name) else "通用机型",
            "serial_number": asset.detail.serial_number if (asset.detail and asset.detail.serial_number) else "",
            "management_ip": asset.detail.management_ip if (asset.detail and asset.detail.management_ip) else "",
            "borrower_name": blog.borrower_name,
            "borrower_username": blog.borrower_username,
            "department": dept,
            "phone": phone,
            "purpose": blog.purpose,
            "borrow_time": blog.borrow_time.strftime("%Y-%m-%d %H:%M:%S") if blog.borrow_time else "",
            "expected_return_time": blog.expected_return_time.strftime("%Y-%m-%d %H:%M:%S") if blog.expected_return_time else "",
            "overdue_days": days,
            "approver": blog.approver or "机房主管",
        }
        overdue_items.append(item)

    # 按超期天数从大到小降序排列
    overdue_items.sort(key=lambda x: x["overdue_days"], reverse=True)

    return {
        "status": "success",
        "total_overdue": len(overdue_items),
        "max_overdue_days": max_days,
        "items": overdue_items,
        "assets": overdue_items,
    }


def generate_overdue_notice(db: Session, asset_no: str) -> Dict[str, Any]:
    """结合借调记录、设备硬件详情与借用人信息，生成标准化《设备资产超期归还催告单》公文通知

    :param db: 数据库会话
    :param asset_no: 资产唯一编号，如 DEV-SRV-201
    :return: 规范红头公文结构体与 Markdown 全文
    """
    now = datetime.now()
    clean_no = (asset_no or "").strip().upper()

    # 1. 校验设备是否存在
    asset = (
        db.query(Asset)
        .options(joinedload(Asset.detail))
        .filter(Asset.asset_no == clean_no)
        .first()
    )
    if not asset:
        raise ValueError(f"资产编号 '{clean_no}' 不存在于机房台账中")

    # 2. 校验设备当前借用状态（在库设备不得出具催告单）
    if asset.borrow_status == "AVAILABLE":
        raise ValueError(f"设备 '{clean_no}' 当前处于空闲在库状态 (AVAILABLE)，未处于借调占用状态，无需出具催告函")

    # 3. 查询该设备当前生效的借调记录（必须为 BORROWING 或 OVERDUE 且尚未实际归还）
    borrow_log = (
        db.query(AssetBorrowLog)
        .filter(
            AssetBorrowLog.asset_id == clean_no,
            AssetBorrowLog.return_status.in_(["OVERDUE", "BORROWING"]),
            AssetBorrowLog.actual_return_time.is_(None),
        )
        .order_by(desc(AssetBorrowLog.borrow_time))
        .first()
    )
    if not borrow_log:
        raise ValueError(f"设备 '{clean_no}' 暂无生效中的借调流转记录（历史借调已结清入库）")

    # 4. 超期天数研判（正常期限借调不得出具催告单）
    if not borrow_log.expected_return_time or now <= borrow_log.expected_return_time:
        exp_str = borrow_log.expected_return_time.strftime("%Y-%m-%d %H:%M:%S") if borrow_log.expected_return_time else "未约定"
        raise ValueError(f"设备 '{clean_no}' 借用期限正常（约定归还时间：{exp_str}），当前尚未超期，无需出具催告函")

    overdue_days = max(1, (now - borrow_log.expected_return_time).days)
    if borrow_log.return_status == "BORROWING":
        borrow_log.return_status = "OVERDUE"
        try:
            db.commit()
        except Exception:
            db.rollback()

    # 4. 借用人档案检索
    user = (
        db.query(User)
        .filter(
            or_(
                User.username == borrow_log.borrower_username,
                User.real_name == borrow_log.borrower_name,
            )
        )
        .first()
    )
    borrower_name = borrow_log.borrower_name or ((user.real_name or user.username) if user else "相关借调教师")
    borrower_dept = user.department if (user and user.department) else "物联网工程教研室"
    borrower_phone = user.phone if (user and user.phone) else "13900000002"

    # 5. 设备参数
    brand = asset.detail.brand if (asset.detail and asset.detail.brand) else "标准厂商"
    model = asset.detail.model_name if (asset.detail and asset.detail.model_name) else "通用型号"
    serial_no = asset.detail.serial_number if (asset.detail and asset.detail.serial_number) else "暂无SN"
    mgmt_ip = asset.detail.management_ip if (asset.detail and asset.detail.management_ip) else "DHCP动态分配"

    # 6. 公文规范要素生成
    doc_seq = now.strftime("%m%d")
    doc_code = f"〔{now.year}〕实管催字第 {doc_seq} 号"
    doc_title = "实验室仪器设备超期使用归还催告单"
    recipient = f"{borrower_name} 老师/主管 ({borrower_dept})"
    deadline_date = (now + timedelta(days=3)).strftime("%Y-%m-%d 18:00:00")
    issuer = "高校实验室与设备管理处 / 网络中心运维部"
    issued_at = now.strftime("%Y年%m月%d日")

    regulations = [
        {
            "clause": "第4章第18条【超期督促与安全追偿规程】",
            "content": "凡借用高校实验室仪器设备超出约定归还期限且未提前办理正规延期审批者，资产管理部门将向借用人签发书面催告单，责令3个工作日内完好交接入库；逾期未交接者将暂扣后续借调资质并通报教研室。",
        },
        {
            "clause": "第2章第7条【高密算力与高价值资产监管条例】",
            "content": "GPU算力节点、核心交换机与大功率电源等重点设备在借用期间必须确保物理环境散热良好并接入监控，严禁擅自转借第三方或私自脱离机房安全管控网络。",
        },
    ]

    # 7. 生成规范 Markdown 文本
    borrow_time_str = borrow_log.borrow_time.strftime("%Y-%m-%d %H:%M:%S") if borrow_log.borrow_time else "2026-09-01 09:00:00"
    expected_return_str = borrow_log.expected_return_time.strftime("%Y-%m-%d %H:%M:%S") if borrow_log.expected_return_time else "2026-09-03 18:00:00"

    markdown_content = f"""# {doc_title}

**公文字号**：`{doc_code}`  
**主送单位/人员**：**{recipient}**  
**签发机构**：{issuer}  
**签发日期**：{issued_at}  

---

### 一、超期借用设备核验档案

| 项目 | 参数详情 |
| :--- | :--- |
| **设备编号** | `{asset.asset_no}` |
| **设备名称** | **{asset.name}** |
| **品牌型号** | {brand} {model} |
| **机房机柜** | {asset.location} |
| **出厂序列号** | `{serial_no}` |
| **带外管理IP** | `{mgmt_ip}` |
| **借调流水号** | `{borrow_log.log_no}` |
| **借用用途** | {borrow_log.purpose} |
| **借出登记时间** | {borrow_time_str} |
| **约定归还时间** | {expected_return_str} |
| **当前逾期天数** | <font color="#f43f5e">**{overdue_days} 天**</font> ⚠️ |

---

### 二、管理规章依据与处置要求

依据《高校实验室安全与仪器设备借调管理条例》有关条款要求：

1. **限期归还或续借处置**：
   请借用人于 **{deadline_date}**（自本通知签发之日起 3 个工作日内），将上述设备完好交接送还至设备归属机房；如科研教学任务确需继续借用，须于截止时间前在系统内提交加盖教研室审批公章的《设备续借延期申请书》。

2. **现场硬件健康验收**：
   归还前请配合机房专职主管（{borrow_log.approver or '王主管'}）进行外观完整性核对、风道散热清理与通电运行自检，签署入库验收单。

3. **责任追溯与安全追偿**：
   超期使用期间如因超温过载或未按规程维护导致硬件故障或损坏，将严格依据规程由使用责任人承担维保修复责任。

---

> 实验室与设备管理处（公章）  
> 联系电话：010-82600380 / 内线 8021  
> 日期：{issued_at}
"""

    return {
        "status": "success",
        "doc_code": doc_code,
        "title": doc_title,
        "recipient": recipient,
        "issuer": issuer,
        "issued_at": issued_at,
        "deadline": deadline_date,
        "overdue_days": overdue_days,
        "borrower": {
            "name": borrower_name,
            "username": borrow_log.borrower_username,
            "department": borrower_dept,
            "phone": borrower_phone,
        },
        "asset": {
            "asset_no": asset.asset_no,
            "name": asset.name,
            "category": asset.category,
            "location": asset.location,
            "brand": brand,
            "model_name": model,
            "serial_number": serial_no,
            "management_ip": mgmt_ip,
            "health_status": asset.health_status,
        },
        "borrow_log": {
            "log_no": borrow_log.log_no,
            "purpose": borrow_log.purpose,
            "borrow_time": borrow_time_str,
            "expected_return_time": expected_return_str,
            "approver": borrow_log.approver or "机房主管",
        },
        "regulations": regulations,
        "markdown_content": markdown_content.strip(),
    }

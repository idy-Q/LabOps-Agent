"""数据库初始化与测试种子数据填充脚本"""

import os
import sys
import logging

# 兼容直接通过 python app/db/init_db.py 执行脚本时的导入路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sqlalchemy import select
from app.db.session import engine, SessionLocal, Base
from app.db.models import Ticket, Asset, AuditLog, ChatHistory, User, hash_password

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# 预置 15 条典型机房资产种子数据 (覆盖服务器/网络设备/配电温控/实验教学 4大类，覆盖 HEALTHY/WARNING/OVERHEAT/OFFLINE 4种健康状态)
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
        "asset_no": "DEV-SRV-203",
        "name": "2号机房-分布式存储服务器03",
        "category": "服务器",
        "location": "实训楼201-机柜A03",
        "health_status": "HEALTHY",
        "borrow_status": "IN_USE",
        "borrower": "大数据实验室",
        "specs": "2x Intel Xeon Silver 4314, 128GB RAM, 12x 16TB SAS HDD RAID6",
    },
    {
        "asset_no": "DEV-SRV-204",
        "name": "1号机房-通用教学虚拟化节点01",
        "category": "服务器",
        "location": "实训楼101-机柜B01",
        "health_status": "WARNING",
        "borrow_status": "IN_USE",
        "borrower": "计算机教学中心",
        "specs": "2x Intel Xeon Gold 5218, 192GB RAM, VMware ESXi 宿主机",
    },
    {
        "asset_no": "DEV-SRV-205",
        "name": "3号机房-退役待报废老旧服务器",
        "category": "服务器",
        "location": "实训楼301-备用区",
        "health_status": "OFFLINE",
        "borrow_status": "AVAILABLE",
        "borrower": None,
        "specs": "已下架离线断电，封存待物理消磁处置",
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
        "asset_no": "DEV-NET-302",
        "name": "实验室千兆汇聚交换机02",
        "category": "网络设备",
        "location": "实训楼101-弱电井",
        "health_status": "HEALTHY",
        "borrow_status": "IN_USE",
        "borrower": "网络中心",
        "specs": "48口千兆 PoE+ 汇聚交换机 Cisco Catalyst 9300",
    },
    {
        "asset_no": "DEV-NET-303",
        "name": "机房边界安全防火墙01",
        "category": "网络设备",
        "location": "实训楼201-网络核心柜",
        "health_status": "HEALTHY",
        "borrow_status": "IN_USE",
        "borrower": "网络安全教研室",
        "specs": "双机热备千兆下一代防火墙 Fortinet FortiGate-200F",
    },
    {
        "asset_no": "DEV-NET-304",
        "name": "物联网无线AP控制器AC01",
        "category": "网络设备",
        "location": "实训楼105-弱电箱",
        "health_status": "OFFLINE",
        "borrow_status": "IN_USE",
        "borrower": "物联网教研室",
        "specs": "无线控制器 AC6508 (当前脱机失联告警)",
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
    {
        "asset_no": "DEV-UPS-101",
        "name": "机房101应急后备式UPS",
        "category": "配电温控",
        "location": "实训楼101-配电间",
        "health_status": "HEALTHY",
        "borrow_status": "IN_USE",
        "borrower": "机房后勤保障组",
        "specs": "山特 3C20KS 20kVA 双变换纯在线式",
    },
    {
        "asset_no": "DEV-AC-201",
        "name": "2号机房精密恒温恒湿空调01",
        "category": "配电温控",
        "location": "实训楼201-北墙",
        "health_status": "HEALTHY",
        "borrow_status": "IN_USE",
        "borrower": "后勤动力科",
        "specs": "依米康 35kW 变频风冷机房精密空调",
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
        "asset_no": "DEV-LAB-106",
        "name": "嵌入式ARM综合开发实验箱-03号",
        "category": "实验教学",
        "location": "实训楼103-器材架A",
        "health_status": "HEALTHY",
        "borrow_status": "IN_USE",
        "borrower": "物联网实验班",
        "specs": "STM32F429 + RK3568 双核边缘计算教学套件",
    },
    {
        "asset_no": "DEV-LAB-107",
        "name": "工控PLC仿真教学实训台-02号",
        "category": "实验教学",
        "location": "实训楼104-工位4",
        "health_status": "WARNING",
        "borrow_status": "AVAILABLE",
        "borrower": None,
        "specs": "西门子 S7-1200 CPU1214C + 模拟量扩展模块 (偶发信号漂移)",
    },
]

# 预置 9 条典型运维工单种子数据 (覆盖 PENDING/PROCESSING/RESOLVED/CLOSED 4种状态，覆盖 CRITICAL/HIGH/MEDIUM/LOW 4种优先级)
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
    {
        "ticket_no": "TK-20260902-001",
        "title": "物联网无线AP控制器AC01离线脱网告警排查",
        "description": "弱电箱AC控制器心跳丢失超30分钟，终端无线无法漫游接入，需现场排查供电适配器与上联光模块。",
        "priority": "CRITICAL",
        "status": "PENDING",
        "device_id": "DEV-NET-304",
        "creator": "系统自动监控",
    },
    {
        "ticket_no": "TK-20260902-002",
        "title": "工控PLC实训台模拟量模块精度偏差校准",
        "description": "学生实验反馈工位4的S7-1200模拟量输入信号存在0.5V固定漂移，需使用标准信号源重新标定量程。",
        "priority": "LOW",
        "status": "PENDING",
        "device_id": "DEV-LAB-107",
        "creator": "赵实验员",
    },
    {
        "ticket_no": "TK-20260901-003",
        "title": "1号机房通用教学虚拟化节点内存告警排查",
        "description": "ESXi宿主机虚拟化内存复用率超过92%，多个教学虚拟机触发内存交换压测告警，需平衡迁移部分负载。",
        "priority": "MEDIUM",
        "status": "PROCESSING",
        "device_id": "DEV-SRV-204",
        "creator": "李管理员",
    },
    {
        "ticket_no": "TK-20260828-001",
        "title": "核心主干路由交换机01光纤接口衰减过大检修",
        "description": "TenGigabitEthernet 1/0/24 端口光衰达-26dBm，已更换跳线与SFP+万兆光模块，光衰恢复至-12dBm，误码率归零。",
        "priority": "HIGH",
        "status": "RESOLVED",
        "device_id": "DEV-NET-301",
        "creator": "网络中心",
    },
    {
        "ticket_no": "TK-20260829-002",
        "title": "网络安全渗透实验箱-A组配件归还与清点核验",
        "description": "攻防课程实训结束，清点工业靶机套件、4口网卡及外接天线，全部功能正常、封签完好，已入库保全。",
        "priority": "LOW",
        "status": "RESOLVED",
        "device_id": "DEV-LAB-105",
        "creator": "张老师",
    },
    {
        "ticket_no": "TK-20260820-001",
        "title": "暑期高校机房精密空调防汛与冷凝排水管道疏通",
        "description": "对实训楼201空调室外冷凝排水管执行高压气体疏通并更换老化绝缘保护套，测试连续运行24小时排水通畅无滴漏，验收关闭。",
        "priority": "MEDIUM",
        "status": "CLOSED",
        "device_id": "DEV-AC-201",
        "creator": "后勤动力科",
    },
    {
        "ticket_no": "TK-20260825-003",
        "title": "3号机房退役老旧服务器下架与硬盘物理消磁审计",
        "description": "实训楼301备用区老旧刀片服务器已执行下架清退，3块系统盘完成消磁打孔与资产核销报废登记，全流程审计归档完毕。",
        "priority": "LOW",
        "status": "CLOSED",
        "device_id": "DEV-SRV-205",
        "creator": "机房资产管理员",
    },
]

# 预置 2 组典型机房运维历史会话种子数据 (彻底消除前端历史会话抽屉空状态)
SEED_CHAT_HISTORIES = [
    # 会话 1：超温紧急排查与规章提单闭环
    {
        "session_id": "sess_temp_emergency_01",
        "role": "user",
        "content": "2号机房GPU计算节点01温度过高，查一下指标并按规范提单",
        "thought": None,
    },
    {
        "session_id": "sess_temp_emergency_01",
        "role": "assistant",
        "thought": "【思考链条】\n1. 感知阶段：收到针对设备 DEV-SRV-201 的超温排查请求，首先调用 get_server_metrics 工具获取实时硬件探针数据。\n2. 研判阶段：探针返回温度为 43.5℃，超过规章规定的 40℃ 红线，风扇转速 4800 RPM，功耗 450W，触发 CRITICAL 级别告警。\n3. 规章溯源：检索《高校计算机机房运行安全与故障应急规章》，第4.2条明确规定核心设备温度连续超标须立即提单并通知现场处置。\n4. 闭环操作：调用 create_ticket 工具自动生成运维工单 TK-20260901-001，优先级标定为 HIGH。\n5. 总结汇报：汇总探针数据、规章依据与已生成的工单详情反馈用户。",
        "content": "已完成对 **2号机房-GPU计算节点01 (DEV-SRV-201)** 的硬件探针指标排查与规章研判：\n\n### 1. 实时探针遥测数据\n- **核心温度**：`43.5℃` 🔴（超过 40.0℃ 安全预警阈值）\n- **CPU 负载**：`88.5%`\n- **内存占用**：`76.2%`\n- **风扇转速**：`4800 RPM`（满负荷运转）\n- **当前功耗**：`450 W`\n\n### 2. 机房规章比对与处置\n依据《高校机房运行安全管理规程》第 4.2 款【设备过热与温控应急】：当服务器核心温度超过 40℃ 时，系统需立即建立紧急运维工单并指派现场巡检。\n\n### 3. 已自动创建运维工单\n- **工单编号**：`TK-20260901-001`\n- **工单标题**：2号机房GPU计算节点01核心温度过热预警\n- **工单状态**：`PROCESSING` (处理中)\n- **优先级**：`HIGH`\n- **提单建议**：建议运维人员携带热成像仪前往实训楼201机房，重点排查机柜A01进出风道与水冷散热模块。",
    },
    # 会话 2：机房全盘自动化健康巡检
    {
        "session_id": "sess_auto_inspection_02",
        "role": "user",
        "content": "一键巡检当前机房全部资产设备，若存在超温或警告请自动提单",
        "thought": None,
    },
    {
        "session_id": "sess_auto_inspection_02",
        "role": "assistant",
        "thought": "【自动化巡检思考链】\n1. 资产检索：调用 query_assets 获取机房全量资产台账（共15台设备）。\n2. 遍历感知：逐一比对设备健康状态，发现异常设备：\n   - DEV-SRV-201（GPU计算节点01）：健康状态 OVERHEAT，温度 43.5℃；\n   - DEV-UPS-201（机房201在线式UPS）：健康状态 WARNING，逆变器温度 38.0℃；\n   - DEV-NET-304、DEV-SRV-205（离线失联）：处于 OFFLINE 脱机状态。\n3. 工单比对：已存在 TK-20260901-001 处理 GPU 节点；针对 DEV-UPS-201 创建预防性维护工单 TK-20260901-002。\n4. 结果汇报：输出巡检大盘全景分布与异常设备处置状态报告。",
        "content": "机房全盘自动化巡检已完成，全量 15 台设备健康体检报告如下：\n\n### 📊 巡检概况\n- **受检资产总数**：`15 台`\n- **健康正常 (HEALTHY)**：`9 台`\n- **亚健康预警 (WARNING)**：`3 台`\n- **超温高危 (OVERHEAT)**：`1 台`\n- **离线脱网 (OFFLINE)**：`2 台`\n\n### ⚠️ 异常设备与闭环处置\n1. **DEV-SRV-201 (2号机房-GPU计算节点01)**\n   - **状态**：`OVERHEAT` (43.5℃)\n   - **流转**：已自动关联工单 `TK-20260901-001` (HIGH, 处理中)\n2. **DEV-UPS-201 (机房201大功率在线式UPS)**\n   - **状态**：`WARNING` (38.0℃，逆变器负载较高)\n   - **流转**：已自动创建工单 `TK-20260901-002` (MEDIUM, 待处理)\n3. **DEV-NET-304 (物联网无线AP控制器AC01)**\n   - **状态**：`OFFLINE` (失联心跳中断)\n   - **流转**：已生成脱网告警并录入待办工单 `TK-20260902-001`。\n\n全量设备监控指标已同步至全景磁贴看板，请管理员在工单流转库持续跟进。",
    },
]

# 预置 4 组典型系统用户种子数据 (涵盖管理员、专业教师、实训指导教师、在读学生四种典型角色)
SEED_USERS = [
    {
        "username": "admin",
        "raw_password": "admin666",
        "real_name": "王主管",
        "role": "ADMIN",
        "department": "网络中心运维部",
        "phone": "13800000001",
    },
    {
        "username": "teacher_li",
        "raw_password": "123456",
        "real_name": "李老师",
        "role": "TEACHER",
        "department": "物联网工程教研室",
        "phone": "13900000002",
    },
    {
        "username": "teacher_zhang",
        "raw_password": "123456",
        "real_name": "张老师",
        "role": "TEACHER",
        "department": "网络安全教研室",
        "phone": "13900000003",
    },
    {
        "username": "student_chen",
        "raw_password": "123456",
        "real_name": "陈同学",
        "role": "STUDENT",
        "department": "计科2201班",
        "phone": "13700000004",
    },
]


def init_db(
    seed: bool = True,
    reset: bool = False,
    custom_engine=None,
    custom_session_factory=None,
) -> None:
    """创建表结构并可选写入种子数据 (支持自定义 engine 和 session 用于测试隔离，支持 reset 重置现有表)"""
    target_engine = custom_engine or engine
    target_session_factory = custom_session_factory or SessionLocal

    if reset:
        logger.info("正在重置数据库已有表结构 (drop_all)...")
        Base.metadata.drop_all(bind=target_engine)

    logger.info("开始初始化数据库结构...")
    Base.metadata.create_all(bind=target_engine)
    logger.info("数据库表结构校验/创建完成 (tickets, assets, audit_logs, chat_history, users)")

    if not seed:
        return

    db = target_session_factory()
    try:
        # 1. 种子资产数据幂等填充 (按唯一 asset_no 判定并同步更新最新属性)
        added_assets = 0
        updated_assets = 0
        for asset_data in SEED_ASSETS:
            exists = db.query(Asset).filter(Asset.asset_no == asset_data["asset_no"]).first()
            if not exists:
                asset = Asset(**asset_data)
                db.add(asset)
                added_assets += 1
            else:
                for k, v in asset_data.items():
                    setattr(exists, k, v)
                updated_assets += 1
        db.commit()
        logger.info("机房资产种子数据处理完成: 新增 %d 台，同步更新 %d 台 (当前共 %d 台)。", added_assets, updated_assets, len(SEED_ASSETS))

        # 2. 种子工单数据幂等填充 (按唯一 ticket_no 判定并同步更新最新属性)
        added_tickets = 0
        updated_tickets = 0
        for ticket_data in SEED_TICKETS:
            exists = db.query(Ticket).filter(Ticket.ticket_no == ticket_data["ticket_no"]).first()
            if not exists:
                ticket = Ticket(**ticket_data)
                db.add(ticket)
                added_tickets += 1
            else:
                for k, v in ticket_data.items():
                    setattr(exists, k, v)
                updated_tickets += 1
        db.commit()
        logger.info("运维工单种子数据处理完成: 新增 %d 条，同步更新 %d 条 (当前共 %d 条)。", added_tickets, updated_tickets, len(SEED_TICKETS))

        # 3. 种子历史会话数据幂等填充 (按 session_id 与 role 判定并同步更新最新文本与思考链)
        added_histories = 0
        updated_histories = 0
        for hist_data in SEED_CHAT_HISTORIES:
            exists = (
                db.query(ChatHistory)
                .filter(
                    ChatHistory.session_id == hist_data["session_id"],
                    ChatHistory.role == hist_data["role"],
                )
                .first()
            )
            if not exists:
                history = ChatHistory(**hist_data)
                db.add(history)
                added_histories += 1
            else:
                for k, v in hist_data.items():
                    setattr(exists, k, v)
                updated_histories += 1
        db.commit()
        logger.info("历史会话种子数据处理完成: 新增 %d 条，同步更新 %d 条 (当前共 %d 条)。", added_histories, updated_histories, len(SEED_CHAT_HISTORIES))

        # 4. 系统典型用户种子数据幂等填充 (按唯一 username 判定并同步更新最新属性与加盐密码)
        added_users = 0
        updated_users = 0
        for user_data in SEED_USERS:
            exists = db.query(User).filter(User.username == user_data["username"]).first()
            pwd_hash = hash_password(user_data["raw_password"])
            if not exists:
                user = User(
                    username=user_data["username"],
                    password_hash=pwd_hash,
                    real_name=user_data["real_name"],
                    role=user_data["role"],
                    department=user_data["department"],
                    phone=user_data.get("phone"),
                )
                db.add(user)
                added_users += 1
            else:
                exists.password_hash = pwd_hash
                exists.real_name = user_data["real_name"]
                exists.role = user_data["role"]
                exists.department = user_data["department"]
                exists.phone = user_data.get("phone")
                updated_users += 1
        db.commit()
        logger.info("系统用户种子数据处理完成: 新增 %d 个，同步更新 %d 个 (当前共 %d 个)。", added_users, updated_users, len(SEED_USERS))

    except Exception as e:
        db.rollback()
        logger.error("数据库初始化种子数据失败: %s", str(e))
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    do_reset = "--no-reset" not in sys.argv
    init_db(seed=True, reset=do_reset)
    print("LabOps-Agent 数据库结构与初始化数据准备就绪。")

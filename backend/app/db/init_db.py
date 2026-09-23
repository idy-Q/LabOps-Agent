"""数据库初始化与测试种子数据填充脚本"""

import os
import sys
import logging

# 兼容直接通过 python app/db/init_db.py 执行脚本时的导入路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import hashlib
from datetime import datetime
from sqlalchemy import select
from app.db.session import engine, SessionLocal, Base
from app.db.models import (
    Ticket,
    Asset,
    AssetDetail,
    AuditLog,
    ChatHistory,
    User,
    ServerRoom,
    AssetBorrowLog,
    TicketWorkflow,
    KnowledgeDocument,
    KnowledgeChunk,
    UserNotification,
    hash_password,
)
from app.rag.chunking import MarkdownChunker

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
        "borrower": "李老师 (物联网工程教研室)",
        "specs": "2x Intel Xeon Gold 6330, 256GB RAM, 4x NVIDIA RTX 4090 24G",
        "detail": {
            "serial_number": "SN-DELL-2024-GPU01",
            "brand": "Dell",
            "model_name": "PowerEdge R750xa 4U机架式服务器",
            "os_firmware": "Ubuntu 22.04 LTS (Kernel 5.15.0-105-generic)",
            "mac_address": "A0:48:1C:82:11:01",
            "management_ip": "192.168.10.201",
            "cpu_info": "2x Intel Xeon Gold 6330 (56核/112线程 @ 2.0GHz, 2.8GHz 睿频)",
            "memory_info": "256GB (8x 32GB DDR4 3200MHz ECC RDIMM)",
            "storage_info": "2x 960GB NVMe SSD RAID1 (OS) + 4x 3.84TB U.2 NVMe SSD RAID5 (Data)",
            "gpu_info": "4x NVIDIA GeForce RTX 4090 24GB GDDR6X (CUDA 12.4)",
            "network_interfaces": "2x 25Gbps SFP28 双光口 + 2x 10Gbps RJ45 电口",
            "power_supply": "双路冗余 2400W 80Plus 钛金电源 (1+1)",
            "purchase_date": "2024-03-15",
            "warranty_period": "2027-03-14 (原厂 3年 7x24金牌服务)",
            "supplier": "戴尔科技集团企业客户部 (客服: 400-881-1852)",
            "extra_params": '{"rack_units": "4U", "start_u": 28, "u_height": 4, "cooling": "前冷后热加压风道", "cuda_version": "12.4"}',
        },
    },
    {
        "asset_no": "DEV-SRV-202",
        "name": "2号机房-CPU计算节点02",
        "category": "服务器",
        "location": "实训楼201-机柜A01",
        "health_status": "HEALTHY",
        "borrow_status": "AVAILABLE",
        "borrower": None,
        "specs": "2x AMD EPYC 7763, 512GB RAM, 2TB NVMe SSD",
        "detail": {
            "serial_number": "SN-H3C-2024-CPU02",
            "brand": "H3C",
            "model_name": "UniServer R4900 G5",
            "os_firmware": "AlmaLinux 9.3 (Kernel 5.14.0)",
            "mac_address": "B4:05:5D:31:22:02",
            "management_ip": "192.168.10.202",
            "cpu_info": "2x AMD EPYC 7763 (128核/256线程 @ 2.45GHz, 256MB L3缓存)",
            "memory_info": "512GB (16x 32GB DDR4 3200MHz ECC RDIMM)",
            "storage_info": "2x 480GB SATA SSD RAID1 + 2x 1.92TB NVMe PCIe4.0 SSD",
            "gpu_info": "板载 ASPEED AST2500 基础显示",
            "network_interfaces": "4x 10Gbps SFP+ 光口 + 2x 千兆电口",
            "power_supply": "双路 1200W 白金级电源",
            "purchase_date": "2024-04-10",
            "warranty_period": "2027-04-09 (新华三 3年联保)",
            "supplier": "新华三技术有限公司 (400-810-0504)",
            "extra_params": '{"rack_units": "2U", "start_u": 24, "u_height": 2, "purpose": "科学计算高通量仿真集群"}',
        },
    },
    {
        "asset_no": "DEV-SRV-203",
        "name": "2号机房-分布式存储服务器03",
        "category": "服务器",
        "location": "实训楼201-机柜A01",
        "health_status": "HEALTHY",
        "borrow_status": "IN_USE",
        "borrower": "王主管",
        "specs": "2x Intel Xeon Silver 4314, 128GB RAM, 12x 16TB SAS HDD RAID6",
        "detail": {
            "serial_number": "SN-INSPUR-2023-STR03",
            "brand": "Inspur (浪潮)",
            "model_name": "NF5466M6 高密存储服务器",
            "os_firmware": "Ceph Storage OS (Debian 12 base)",
            "mac_address": "70:79:90:54:33:03",
            "management_ip": "192.168.10.203",
            "cpu_info": "2x Intel Xeon Silver 4314 (32核/64线程 @ 2.40GHz)",
            "memory_info": "128GB (4x 32GB DDR4 3200MHz ECC)",
            "storage_info": "12x 16TB 3.5寸 企业级 SAS HDD (RAID6, 净可用约 160TB) + 2x 480GB 系统盘",
            "gpu_info": "无独立显卡",
            "network_interfaces": "2x 25Gbps SFP28 光纤存储网卡 + 2x 千兆管理口",
            "power_supply": "双路 1600W 80Plus 白金电源",
            "purchase_date": "2023-11-20",
            "warranty_period": "2026-11-19 (浪潮 3年原厂支持)",
            "supplier": "浪潮信息系统股份有限公司 (400-860-0011)",
            "extra_params": '{"rack_units": "4U", "start_u": 18, "u_height": 4, "raid_controller": "LSI 3108 MegaRAID 2GB Cache", "raw_capacity_tb": "192TB"}',
        },
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
        "detail": {
            "serial_number": "SN-LENOVO-2023-VM01",
            "brand": "Lenovo (联想)",
            "model_name": "ThinkSystem SR650 2U机架式",
            "os_firmware": "VMware ESXi 8.0 Update 2 (Build 22380479)",
            "mac_address": "54:AB:3A:41:44:04",
            "management_ip": "192.168.10.104",
            "cpu_info": "2x Intel Xeon Gold 5218 (32核/64线程 @ 2.30GHz)",
            "memory_info": "192GB (12x 16GB DDR4 2933MHz ECC)",
            "storage_info": "4x 1.2TB 10K SAS 2.5寸热插拔 HDD (RAID10) + 2x M.2 240GB 引导镜像",
            "gpu_info": "无",
            "network_interfaces": "4x 10Gbps SFP+ 双光双电复合板",
            "power_supply": "双路 1100W 铂金热插拔电源",
            "purchase_date": "2023-09-01",
            "warranty_period": "2026-08-31 (联想企业级 3年上门服务)",
            "supplier": "联想开天科技有限公司 (400-810-8888)",
            "extra_params": '{"rack_units": "2U", "start_u": 34, "u_height": 2, "hypervisor": "VMware vSphere ESXi 8.0u2", "vms_hosted": 18}',
        },
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
        "detail": {
            "serial_number": "SN-HP-2016-OLD05",
            "brand": "HP (惠普)",
            "model_name": "ProLiant DL380p Gen8",
            "os_firmware": "已格式化清空 (待消磁)",
            "mac_address": "00:1E:0B:AA:55:05",
            "management_ip": "192.168.10.205 (离线断开)",
            "cpu_info": "2x Intel Xeon E5-2620 v2 (12核/24线程 @ 2.10GHz)",
            "memory_info": "64GB (8x 8GB DDR3 1600MHz)",
            "storage_info": "无硬盘 (已物理拔出消磁)",
            "gpu_info": "无",
            "network_interfaces": "4x 1Gbps RJ45 板载千兆电口",
            "power_supply": "单路 750W 冗余电源",
            "purchase_date": "2016-06-15",
            "warranty_period": "已过保 (2019-06-14 到期)",
            "supplier": "惠普中国 (设备已停产退市)",
            "extra_params": '{"rack_units": "2U", "scrap_status": "已获审批待残值评估回收"}',
        },
    },
    {
        "asset_no": "DEV-NET-301",
        "name": "核心主干路由交换机01",
        "category": "网络设备",
        "location": "实训楼201-机柜A01",
        "health_status": "HEALTHY",
        "borrow_status": "IN_USE",
        "borrower": "网络中心",
        "specs": "48口万兆SFP+ 光纤核心交换机 Huawei CloudEngine 6800",
        "detail": {
            "serial_number": "SN-HW-2024-SW01",
            "brand": "Huawei (华为)",
            "model_name": "CloudEngine 6800 万兆数据中心核心交换机",
            "os_firmware": "VRP V200R019C00SPC800",
            "mac_address": "28:6E:D4:11:33:01",
            "management_ip": "192.168.1.1",
            "cpu_info": "4核 1.5GHz 工业网络专用处理器",
            "memory_info": "4GB RAM + 8GB Flash",
            "storage_info": "内置 8GB eMMC 固件系统存储",
            "gpu_info": "无",
            "network_interfaces": "48x 10GE SFP+ 光纤端口 + 6x 100GE QSFP28 上联口",
            "power_supply": "双路 600W AC 前后风道冗余电源",
            "purchase_date": "2024-01-10",
            "warranty_period": "2027-01-09 (华为原厂 3年硬件保修)",
            "supplier": "华为技术有限公司企业 BG (400-822-9999)",
            "extra_params": '{"rack_units": "2U", "start_u": 40, "u_height": 2, "switching_capacity": "2.16 Tbps", "forwarding_rate": "720 Mpps", "vlans": "1-4094"}',
        },
    },
    {
        "asset_no": "DEV-NET-302",
        "name": "实验室千兆汇聚交换机02",
        "category": "网络设备",
        "location": "实训楼101-机柜B01",
        "health_status": "HEALTHY",
        "borrow_status": "IN_USE",
        "borrower": "网络中心",
        "specs": "48口千兆 PoE+ 汇聚交换机 Cisco Catalyst 9300",
        "detail": {
            "serial_number": "SN-CS-2023-SW02",
            "brand": "Cisco (思科)",
            "model_name": "Catalyst 9300-48P PoE+ 交换机",
            "os_firmware": "Cisco IOS-XE 17.9.4a",
            "mac_address": "F8:B7:E2:44:22:02",
            "management_ip": "192.168.1.2",
            "cpu_info": "4核 x86 网络处理器 @ 1.8GHz",
            "memory_info": "16GB DRAM + 16GB Flash",
            "storage_info": "16GB 闪存存储",
            "gpu_info": "无",
            "network_interfaces": "48x 10/100/1000M PoE+ 电口 + 4x 10GE 上联模块",
            "power_supply": "715W AC PoE 供电电源",
            "purchase_date": "2023-10-18",
            "warranty_period": "2026-10-17 (思科 Smart Net Total Care)",
            "supplier": "思科系统 (中国) 网络技术有限公司 (400-810-8886)",
            "extra_params": '{"rack_units": "1U", "start_u": 40, "u_height": 1, "poe_budget": "437W", "stacking_bandwidth": "480 Gbps"}',
        },
    },
    {
        "asset_no": "DEV-NET-303",
        "name": "机房边界安全防火墙01",
        "category": "网络设备",
        "location": "实训楼201-机柜A01",
        "health_status": "HEALTHY",
        "borrow_status": "IN_USE",
        "borrower": "网络安全教研室",
        "specs": "双机热备千兆下一代防火墙 Fortinet FortiGate-200F",
        "detail": {
            "serial_number": "SN-FG-2023-FW03",
            "brand": "Fortinet (飞塔)",
            "model_name": "FortiGate-200F 下一代网络安全网关",
            "os_firmware": "FortiOS v7.2.6 build1575",
            "mac_address": "70:4C:A5:66:33:03",
            "management_ip": "192.168.1.254",
            "cpu_info": "Fortinet SPU NP6XLite + CP9 硬件加速引擎",
            "memory_info": "8GB 高速内存",
            "storage_info": "内置 64GB 固态日志存储盘",
            "gpu_info": "无",
            "network_interfaces": "16x GE RJ45 电口 + 8x 10GE SFP+ 光口",
            "power_supply": "双路 AC 100-240V 冗余供电",
            "purchase_date": "2023-08-25",
            "warranty_period": "2026-08-24 (FortiCare 24x7 维保与威胁库升级)",
            "supplier": "飞塔信息科技 (400-600-5255)",
            "extra_params": '{"rack_units": "2U", "start_u": 36, "u_height": 2, "ips_throughput": "5 Gbps", "ngfw_throughput": "3.5 Gbps", "threat_protection": "3 Gbps"}',
        },
    },
    {
        "asset_no": "DEV-NET-304",
        "name": "物联网无线AP控制器AC01",
        "category": "网络设备",
        "location": "实训楼101-弱电箱",
        "health_status": "OFFLINE",
        "borrow_status": "IN_USE",
        "borrower": "物联网教研室",
        "specs": "无线控制器 AC6508 (当前脱机失联告警)",
        "detail": {
            "serial_number": "SN-HW-2023-AC04",
            "brand": "Huawei (华为)",
            "model_name": "Access Controller AC6508",
            "os_firmware": "VRP (R) Software, Version 5.170 (V200R019C00)",
            "mac_address": "4C:1F:CC:99:44:04",
            "management_ip": "192.168.1.5",
            "cpu_info": "双核 ARM Cortex-A9 @ 1.2GHz",
            "memory_info": "2GB DDR3 RAM",
            "storage_info": "1GB NAND Flash",
            "gpu_info": "无",
            "network_interfaces": "10x 10/100/1000M RJ45 电口 + 2x 10GE SFP+ 光口",
            "power_supply": "外置 12V/3A 直流电源适配器",
            "purchase_date": "2023-05-12",
            "warranty_period": "2026-05-11 (华为 3年维保)",
            "supplier": "华为技术 (400-822-9999)",
            "extra_params": '{"max_aps_managed": 256, "max_clients": 4096}',
        },
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
        "detail": {
            "serial_number": "SN-APC-2023-UPS01",
            "brand": "APC (施耐德)",
            "model_name": "Smart-UPS RT 10kVA 在线双变换 UPS",
            "os_firmware": "Network Management Card 3 (v2.5.0.6)",
            "mac_address": "00:C0:B7:AA:66:01",
            "management_ip": "192.168.10.250",
            "cpu_info": "微处理器数字双变换控制核心 (DSP)",
            "memory_info": "512MB 监控控制器运存",
            "storage_info": "非易失性参数 EEPROM",
            "gpu_info": "无",
            "network_interfaces": "1x 10/100M SNMP/Web 网管接口 + RS-232 串口",
            "power_supply": "额定输出容量 10kVA / 10kW，单相/三相兼容输入",
            "purchase_date": "2023-07-20",
            "warranty_period": "2026-07-19 (施耐德电气原厂 3年主机 + 2年电池保修)",
            "supplier": "施耐德电气 (中国) 有限公司 (400-810-1315)",
            "extra_params": '{"battery_type": "免维护铅酸蓄电池组 192VDC", "backup_time_full_load": "12 分钟"}',
        },
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
        "detail": {
            "serial_number": "SN-ST-2022-UPS02",
            "brand": "SANTAK (山特)",
            "model_name": "3C20KS 20kVA 双变换纯在线式 UPS",
            "os_firmware": "WinPower SNMP Card II v4.1",
            "mac_address": "00:0B:AB:33:11:02",
            "management_ip": "192.168.10.251",
            "cpu_info": "双 DSP 全数字化电压电流双环控制",
            "memory_info": "256MB 控制器内存",
            "storage_info": "内置参数存储芯片",
            "gpu_info": "无",
            "network_interfaces": "1x 百兆 SNMP 网管口 + DB9 智能串口",
            "power_supply": "额定容量 20kVA / 18kW，三相输入单相输出",
            "purchase_date": "2022-12-05",
            "warranty_period": "2025-12-04 (山特原厂 3年保修)",
            "supplier": "深圳山特电子有限公司 (400-830-3938)",
            "extra_params": '{"efficiency": "94.5%", "battery_pack": "32节 12V 65Ah 电池柜"}',
        },
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
        "detail": {
            "serial_number": "SN-ENV-2023-AC01",
            "brand": "Envicool (英维克)",
            "model_name": "CyberMate V系列 变频风冷精密空调 (35kW)",
            "os_firmware": "DMC3000 智能触摸屏控制器 v3.82",
            "mac_address": "18:8E:D5:88:99:01",
            "management_ip": "192.168.10.252",
            "cpu_info": "工业级 ARM9 嵌入式温湿度控制核心",
            "memory_info": "128MB 工业运存",
            "storage_info": "内置历史温湿度运行曲线存储",
            "gpu_info": "无",
            "network_interfaces": "RS-485 Modbus-RTU + RJ45 SNMP 网管卡",
            "power_supply": "三相五线 380VAC 50Hz，最大运行电流 38A",
            "purchase_date": "2023-04-20",
            "warranty_period": "2026-04-19 (英维克 3年巡检维保)",
            "supplier": "深圳市英维克科技股份有限公司 (400-600-8898)",
            "extra_params": '{"cooling_capacity_kw": 35.0, "air_flow_m3h": 10500, "refrigerant": "R410A 环保冷媒"}',
        },
    },
    {
        "asset_no": "DEV-LAB-105",
        "name": "网络安全渗透实验箱-A组",
        "category": "实验教学",
        "location": "实训楼101-器材柜B",
        "health_status": "HEALTHY",
        "borrow_status": "AVAILABLE",
        "borrower": None,
        "specs": "工控靶机套件 + 工业交换机 + 无线渗透嗅探适配器",
        "detail": {
            "serial_number": "SN-TOP-2024-LAB05",
            "brand": "天融信 (Topsec)",
            "model_name": "网络攻防与渗透测试教学实验套件 TS-LAB-EDU",
            "os_firmware": "Kali Linux 2024.1 ARM + 嵌入式工控仿真固件",
            "mac_address": "00:50:56:C0:00:05",
            "management_ip": "172.16.105.15",
            "cpu_info": "瑞芯微 RK3588 八核 64位处理器 (4x A76 + 4x A55 @ 2.4GHz)",
            "memory_info": "16GB LPDDR4x",
            "storage_info": "128GB eMMC 5.1 + 1TB NVMe M.2 扩展盘",
            "gpu_info": "Mali-G610 MP4 GPU + 6 TOPS 算力 NPU",
            "network_interfaces": "2x 千兆 RJ45 + 1x WiFi 6 无线网络嗅探模块 + SDR 射频模块",
            "power_supply": "12V/5A 桌面直流电源",
            "purchase_date": "2024-02-28",
            "warranty_period": "2027-02-27 (教学仪器 3年联保)",
            "supplier": "北京天融信网络安全技术有限公司 (400-610-5188)",
            "extra_params": '{"target_modules": "PLC攻防仿真模块, CAN总线模拟器, WiFi钓鱼网关"}',
        },
    },
    {
        "asset_no": "DEV-LAB-106",
        "name": "嵌入式ARM综合开发实验箱-03号",
        "category": "实验教学",
        "location": "实训楼101-器材架A",
        "health_status": "HEALTHY",
        "borrow_status": "IN_USE",
        "borrower": "物联网实验班",
        "specs": "STM32F429 + RK3568 双核边缘计算教学套件",
        "detail": {
            "serial_number": "SN-HQ-2023-LAB06",
            "brand": "华清远见",
            "model_name": "FS-IoT-ARM综合物联网实训教学箱",
            "os_firmware": "Ubuntu 20.04 + RT-Thread 4.1 混合架构",
            "mac_address": "00:04:A3:12:34:56",
            "management_ip": "172.16.103.16",
            "cpu_info": "STM32F429IGT6 (180MHz Cortex-M4) + RK3568 (四核 A55 @ 2.0GHz)",
            "memory_info": "8GB LPDDR4 (核心板) + 64MB SDRAM (单片机底板)",
            "storage_info": "32GB eMMC + 128MB SPI Flash",
            "gpu_info": "Mali-G52 2EE",
            "network_interfaces": "千兆网口 + 4G 全网通 Cat.1 + Zigbee 3.0 + 蓝牙5.0",
            "power_supply": "220V AC 转 12V/10A 稳压航空插头电源",
            "purchase_date": "2023-09-15",
            "warranty_period": "2025-09-14 (厂商 2年保修)",
            "supplier": "北京华清远见科技信息有限公司 (010-82600380)",
            "extra_params": '{"sensors": "温湿度/光照/烟雾/三轴加速度/RFID读写器/7寸电容触摸屏"}',
        },
    },
    {
        "asset_no": "DEV-LAB-107",
        "name": "工控PLC仿真教学实训台-02号",
        "category": "实验教学",
        "location": "实训楼101-工位4",
        "health_status": "WARNING",
        "borrow_status": "AVAILABLE",
        "borrower": None,
        "specs": "西门子 S7-1200 CPU1214C + 模拟量扩展模块 (偶发信号漂移)",
        "detail": {
            "serial_number": "SN-SIEMENS-2023-PLC07",
            "brand": "Siemens (西门子)",
            "model_name": "SIMATIC S7-1200 自动化工程教学实验台",
            "os_firmware": "TIA Portal V18 / Firmware V4.6",
            "mac_address": "00:1C:06:55:77:07",
            "management_ip": "192.168.0.107",
            "cpu_info": "西门子专用工业控制实时微处理器 CPU 1214C DC/DC/DC",
            "memory_info": "100KB 工作存储区 + 4MB 负载存储区 + 10KB 保持性存储区",
            "storage_info": "24MB SIMATIC 工业安全存储卡 (MC)",
            "gpu_info": "无",
            "network_interfaces": "PROFINET 2端口以太网交换机接口",
            "power_supply": "西门子 PM1207 稳压电源 (24V DC / 2.5A)",
            "purchase_date": "2023-03-20",
            "warranty_period": "2026-03-19 (西门子工业自动化原厂 3年质保)",
            "supplier": "西门子 (中国) 有限公司数字化工业集团 (400-810-4288)",
            "extra_params": '{"io_points": "14点数字量输入(24V DC), 10点数字量输出, 2点模拟量输入(0-10V)", "status_notes": "模拟量通道偶发微伏级漂移，需标定"}',
        },
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

# 预置 3 个典型机房区域与机柜台账种子数据
SEED_SERVER_ROOMS = [
    {
        "room_code": "ROOM-201",
        "room_name": "实训楼201 人工智能与高密算力实训机房",
        "total_racks": 1,
        "power_capacity_kw": 80.0,
        "manager_teacher": "王主管",
        "location": "实训楼2层东侧201室",
    },
    {
        "room_code": "ROOM-101",
        "room_name": "实训楼101 综合网络与虚拟化教学机房",
        "total_racks": 1,
        "power_capacity_kw": 45.0,
        "manager_teacher": "李老师",
        "location": "实训楼1层中段101室",
    },
    {
        "room_code": "ROOM-301",
        "room_name": "实训楼301 备用与退役实验仪器库房",
        "total_racks": 0,
        "power_capacity_kw": 20.0,
        "manager_teacher": "赵实验员",
        "location": "实训楼3层西侧301室",
    },
]

# 预置 3 条典型设备借调流转历史记录种子数据 (覆盖 OVERDUE/BORROWING/RETURNED 三种状态)
SEED_BORROW_LOGS = [
    {
        "log_no": "BORROW-20260901-001",
        "asset_id": "DEV-SRV-201",
        "borrower_username": "teacher_li",
        "borrower_name": "李老师",
        "purpose": "大模型多模态推理教学实验与算力压测",
        "borrow_time": datetime(2026, 9, 1, 9, 0, 0),
        "expected_return_time": datetime(2026, 9, 3, 18, 0, 0),
        "actual_return_time": None,
        "return_status": "OVERDUE",
        "approver": "王主管",
    },
    {
        "log_no": "BORROW-20260919-002",
        "asset_id": "DEV-SRV-203",
        "borrower_username": "admin_wang",
        "borrower_name": "王主管",
        "purpose": "分布式存储性能基准调优与容灾备份演练",
        "borrow_time": datetime(2026, 9, 19, 10, 0, 0),
        "expected_return_time": datetime(2026, 10, 3, 18, 0, 0),
        "actual_return_time": None,
        "return_status": "BORROWING",
        "approver": "李老师",
    },
    {
        "log_no": "BORROW-20260825-001",
        "asset_id": "DEV-LAB-105",
        "borrower_username": "teacher_zhang",
        "borrower_name": "张老师",
        "purpose": "网络攻防演习与安全渗透实验教学",
        "borrow_time": datetime(2026, 8, 25, 8, 30, 0),
        "expected_return_time": datetime(2026, 8, 29, 17, 0, 0),
        "actual_return_time": datetime(2026, 8, 29, 16, 30, 0),
        "return_status": "RETURNED",
        "approver": "王主管",
    },
]

# 预置 4 条工单流转处置记录种子数据 (体现工单全生命周期状态机变迁)
SEED_TICKET_WORKFLOWS = [
    {
        "ticket_id": "TK-20260901-001",
        "previous_status": "PENDING",
        "next_status": "PROCESSING",
        "operator": "王主管",
        "comment": "系统自动感知GPU核心超温触发告警，已指派现场运维携带热成像仪前往实训楼201排查风道",
        "created_at": datetime(2026, 9, 1, 9, 15, 0),
    },
    {
        "ticket_id": "TK-20260828-001",
        "previous_status": "PENDING",
        "next_status": "PROCESSING",
        "operator": "李老师",
        "comment": "万兆光模块衰减检测告警，领用备件光纤跳线与SFP+模块准备更换",
        "created_at": datetime(2026, 8, 28, 10, 0, 0),
    },
    {
        "ticket_id": "TK-20260828-001",
        "previous_status": "PROCESSING",
        "next_status": "RESOLVED",
        "operator": "李老师",
        "comment": "更换跳线及模块完毕，光功率测量恢复至-12dBm，误码率归零，业务通信恢复正常",
        "created_at": datetime(2026, 8, 28, 14, 30, 0),
    },
    {
        "ticket_id": "TK-20260820-001",
        "previous_status": "RESOLVED",
        "next_status": "CLOSED",
        "operator": "王主管",
        "comment": "精密空调连续排水压测24小时无渗漏，动环温湿度回归22℃标准线，验收通过正式归档闭环",
        "created_at": datetime(2026, 8, 21, 16, 0, 0),
    },
]

# 预置 3 篇知识库规程源文档元数据定义
SEED_KNOWLEDGE_DOCS_META = [
    {
        "doc_id": "DOC-RAG-001",
        "file_name": "power_safety.md",
        "title": "用电安全与高功耗设备接入管理规范",
        "version": "2026版",
        "category": "用电规范",
        "effective_date": "2026-01-01",
    },
    {
        "doc_id": "DOC-RAG-002",
        "file_name": "overheat_emergency.md",
        "title": "空调故障与超温应急预案",
        "version": "2026版",
        "category": "应急条例",
        "effective_date": "2026-01-01",
    },
    {
        "doc_id": "DOC-RAG-003",
        "file_name": "inspection_maintenance.md",
        "title": "日常巡检维保与设备全生命周期制度",
        "version": "2026版",
        "category": "维保规程",
        "effective_date": "2026-01-01",
    },
]

# 预置用户站内待办与超期督促通知种子数据 (为李老师预置 DEV-SRV-201 借用超期督促待办)
SEED_NOTIFICATIONS = [
    {
        "username": "teacher_li",
        "title": "【超期催促】DEV-SRV-201 借用已超期 18 天，请及时办理归还或续借手续",
        "content": "尊敬的李老师：您于 2026-09-01 借调的设备「2号机房-GPU计算节点01 (DEV-SRV-201)」应还日期为 2026-09-03 18:00:00，当前已严重超期 18 天。请尽快归还设备或联系实训中心主管办理延期审批。",
        "notice_type": "OVERDUE_URGE",
        "asset_no": "DEV-SRV-201",
        "is_read": False,
        "created_at": datetime(2026, 9, 21, 9, 30, 0),
    }
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
    logger.info("数据库表结构校验/创建完成 (tickets, assets, asset_details, audit_logs, chat_history, users, server_rooms, asset_borrow_logs, ticket_workflows, knowledge_documents, knowledge_chunks, user_notifications)")

    if not seed:
        return

    db = target_session_factory()
    try:
        # 1. 种子资产与硬件详细参数数据幂等填充 (按唯一 asset_no 判定并同步更新最新属性)
        added_assets = 0
        updated_assets = 0
        for item in SEED_ASSETS:
            asset_dict = {k: v for k, v in item.items() if k != "detail"}
            detail_dict = item.get("detail")
            exists = db.query(Asset).filter(Asset.asset_no == asset_dict["asset_no"]).first()
            if not exists:
                asset = Asset(**asset_dict)
                db.add(asset)
                db.flush()
                if detail_dict:
                    detail = AssetDetail(asset_id=asset.id, **detail_dict)
                    db.add(detail)
                added_assets += 1
            else:
                for k, v in asset_dict.items():
                    setattr(exists, k, v)
                db.flush()
                if detail_dict:
                    if exists.detail:
                        for dk, dv in detail_dict.items():
                            setattr(exists.detail, dk, dv)
                    else:
                        detail = AssetDetail(asset_id=exists.id, **detail_dict)
                        db.add(detail)
                updated_assets += 1
        db.commit()
        logger.info("机房资产与硬件详细参数种子数据处理完成: 新增 %d 台，同步更新 %d 台 (当前共 %d 台)。", added_assets, updated_assets, len(SEED_ASSETS))

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

        # 5. 机房区域与机柜台账种子数据幂等填充 (按唯一 room_code 判定)
        valid_codes = [r["room_code"] for r in SEED_SERVER_ROOMS]
        db.query(ServerRoom).filter(ServerRoom.room_code.notin_(valid_codes)).delete(synchronize_session=False)
        added_rooms = 0
        updated_rooms = 0
        for room_data in SEED_SERVER_ROOMS:
            exists = db.query(ServerRoom).filter(ServerRoom.room_code == room_data["room_code"]).first()
            if not exists:
                room = ServerRoom(**room_data)
                db.add(room)
                added_rooms += 1
            else:
                for k, v in room_data.items():
                    setattr(exists, k, v)
                updated_rooms += 1
        db.commit()
        logger.info("机房区域种子数据处理完成: 新增 %d 间，同步更新 %d 间 (当前共 %d 间)。", added_rooms, updated_rooms, len(SEED_SERVER_ROOMS))

        # 6. 设备借调流转历史记录种子数据幂等填充 (按唯一 log_no 判定)
        added_borrow_logs = 0
        updated_borrow_logs = 0
        for log_data in SEED_BORROW_LOGS:
            exists = db.query(AssetBorrowLog).filter(AssetBorrowLog.log_no == log_data["log_no"]).first()
            if not exists:
                blog = AssetBorrowLog(**log_data)
                db.add(blog)
                added_borrow_logs += 1
            else:
                for k, v in log_data.items():
                    setattr(exists, k, v)
                updated_borrow_logs += 1
        db.commit()
        logger.info("设备借调历史种子数据处理完成: 新增 %d 条，同步更新 %d 条 (当前共 %d 条)。", added_borrow_logs, updated_borrow_logs, len(SEED_BORROW_LOGS))

        # 7. 工单流转处置记录种子数据幂等填充 (按 ticket_id 与 前后置状态判定)
        added_workflows = 0
        updated_workflows = 0
        for wf_data in SEED_TICKET_WORKFLOWS:
            exists = (
                db.query(TicketWorkflow)
                .filter(
                    TicketWorkflow.ticket_id == wf_data["ticket_id"],
                    TicketWorkflow.previous_status == wf_data["previous_status"],
                    TicketWorkflow.next_status == wf_data["next_status"],
                )
                .first()
            )
            if not exists:
                wf = TicketWorkflow(**wf_data)
                db.add(wf)
                added_workflows += 1
            else:
                for k, v in wf_data.items():
                    setattr(exists, k, v)
                updated_workflows += 1
        db.commit()
        logger.info("工单流转历史种子数据处理完成: 新增 %d 条，同步更新 %d 条 (当前共 %d 条)。", added_workflows, updated_workflows, len(SEED_TICKET_WORKFLOWS))

        # 8. 知识库规程源文档与切块索引台账种子数据幂等填充
        added_docs = 0
        updated_docs = 0
        added_chunks = 0
        updated_chunks = 0
        reg_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "regulations"))
        chunker = MarkdownChunker()

        for doc_meta in SEED_KNOWLEDGE_DOCS_META:
            doc_id = doc_meta["doc_id"]
            file_path = os.path.join(reg_dir, doc_meta["file_name"])
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    content_str = f.read()
                file_hash = hashlib.sha256(content_str.encode("utf-8")).hexdigest()
                char_count = len(content_str)
                try:
                    chunks = chunker.chunk_document(file_path)
                except Exception as e:
                    logger.warning("解析规程文档切块异常 %s: %s", file_path, str(e))
                    chunks = []
            else:
                file_hash = hashlib.sha256(doc_meta["title"].encode("utf-8")).hexdigest()
                char_count = len(doc_meta["title"])
                chunks = [
                    {
                        "doc_name": os.path.splitext(doc_meta["file_name"])[0],
                        "section": "第一条 规程总则",
                        "clause": "1. 规范概述",
                        "content": doc_meta["title"],
                    }
                ]

            exists_doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.doc_id == doc_id).first()
            if not exists_doc:
                doc_obj = KnowledgeDocument(
                    doc_id=doc_id,
                    title=doc_meta["title"],
                    version=doc_meta["version"],
                    category=doc_meta["category"],
                    file_hash=file_hash,
                    char_count=char_count,
                    effective_date=doc_meta["effective_date"],
                )
                db.add(doc_obj)
                added_docs += 1
            else:
                exists_doc.title = doc_meta["title"]
                exists_doc.version = doc_meta["version"]
                exists_doc.category = doc_meta["category"]
                exists_doc.file_hash = file_hash
                exists_doc.char_count = char_count
                exists_doc.effective_date = doc_meta["effective_date"]
                updated_docs += 1
            db.flush()

            # 清理该文档若超出当前切块数量的过时切块 (保障规程内容调整时的绝对幂等)
            db.query(KnowledgeChunk).filter(
                KnowledgeChunk.document_id == doc_id,
                KnowledgeChunk.chunk_index > len(chunks),
            ).delete()

            for idx, ck in enumerate(chunks):
                chunk_id = f"CHK-{doc_id[-3:]}-{idx+1:02d}"
                sec = ck.get("section", "")
                cl = ck.get("clause", "")
                section_title = f"{sec} {cl}".strip() if cl else sec
                chunk_text = ck.get("content", "")
                token_est = max(1, len(chunk_text) // 2)
                chroma_id = f"{ck.get('doc_name', '')}_{sec}_{idx}"

                exists_ck = db.query(KnowledgeChunk).filter(KnowledgeChunk.chunk_id == chunk_id).first()
                if not exists_ck:
                    chunk_obj = KnowledgeChunk(
                        chunk_id=chunk_id,
                        document_id=doc_id,
                        chunk_index=idx + 1,
                        section_title=section_title,
                        chunk_content=chunk_text,
                        token_count=token_est,
                        chroma_id=chroma_id,
                    )
                    db.add(chunk_obj)
                    added_chunks += 1
                else:
                    exists_ck.section_title = section_title
                    exists_ck.chunk_content = chunk_text
                    exists_ck.token_count = token_est
                    exists_ck.chroma_id = chroma_id
                    updated_chunks += 1

        db.commit()
        logger.info(
            "知识规程与切块种子数据处理完成: 源文档新增 %d 篇/更新 %d 篇，切块新增 %d 条/更新 %d 条。",
            added_docs,
            updated_docs,
            added_chunks,
            updated_chunks,
        )

        # 9. 用户站内待办与超期督促通知种子数据幂等填充 (按 username 与 asset_no 与 notice_type 判定)
        added_notifications = 0
        updated_notifications = 0
        for notif_data in SEED_NOTIFICATIONS:
            exists = (
                db.query(UserNotification)
                .filter(
                    UserNotification.username == notif_data["username"],
                    UserNotification.asset_no == notif_data["asset_no"],
                    UserNotification.notice_type == notif_data["notice_type"],
                )
                .first()
            )
            if not exists:
                notif = UserNotification(**notif_data)
                db.add(notif)
                added_notifications += 1
            else:
                for k, v in notif_data.items():
                    setattr(exists, k, v)
                updated_notifications += 1
        db.commit()
        logger.info(
            "用户站内待办通知种子数据处理完成: 新增 %d 条，同步更新 %d 条 (当前共 %d 条)。",
            added_notifications,
            updated_notifications,
            len(SEED_NOTIFICATIONS),
        )

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

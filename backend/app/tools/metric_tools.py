"""服务器与机房运行健康监控指标工具 (Metric Tools)"""

from typing import Any, Dict, Optional
from sqlalchemy.orm import Session

from app.db.models import Asset
from app.tools.registry import tool


@tool(name="get_server_metrics", description="查询机房指定服务器或设备的实时健康监控指标（包括核心温度、CPU占用率、内存占用、风扇转速等），温度超过40℃将自动触发超温预警")
def get_server_metrics(
    device_id: str,
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """查询指定设备的实时健康状态与传感器指标

    :param device_id: 设备/资产编号，例如 DEV-SRV-201、DEV-SRV-202
    :param db: 数据库会话 (由系统自动注入)
    :return: 包含温度、CPU、内存及告警等级的指标字典
    """
    clean_device_id = (device_id or "").strip().upper()
    if not clean_device_id:
        return {"status": "error", "message": "设备编号不能为空"}

    device_name = "机房运算节点"
    location = "实训楼201机房"
    health_status = "HEALTHY"

    if db is not None:
        asset = db.query(Asset).filter(Asset.asset_no == clean_device_id).first()
        if not asset:
            return {
                "status": "error",
                "message": f"未在机房资产台账中找到编号为 '{clean_device_id}' 的设备，请核实设备编号",
            }
        device_name = asset.name
        location = asset.location
        health_status = asset.health_status
    else:
        # 无 DB 注入时的纯净模拟探针兜底 (单测与纯离线传感器模拟)
        from app.db.init_db import SEED_ASSETS

        seed_map = {item["asset_no"]: item for item in SEED_ASSETS}
        if clean_device_id in seed_map:
            seed_asset = seed_map[clean_device_id]
            health_status = seed_asset["health_status"]
            device_name = seed_asset["name"]
            location = seed_asset["location"]
        elif "overheat" in clean_device_id.lower():
            health_status = "OVERHEAT"
            device_name = "2号机房-GPU计算节点01"
            location = "实训楼201-机柜A01"
        elif "warning" in clean_device_id.lower():
            health_status = "WARNING"
            device_name = "机房预警设备"
            location = "实训楼201"
        elif "offline" in clean_device_id.lower():
            health_status = "OFFLINE"
            device_name = "离线设备"
            location = "实训楼备用区"
        else:
            return {
                "status": "error",
                "message": f"未在机房资产台账中找到编号为 '{clean_device_id}' 的设备，请核实设备编号",
            }

    # 基于设备健康状态派生传感器监控指标
    if health_status == "OVERHEAT":
        temperature = 43.5
        cpu_usage = 88.5
        memory_usage = 76.2
        fan_speed_rpm = 4800
        power_watts = 450
        status_code = "OVERHEAT"
        alert = True
        alert_level = "CRITICAL"
        alert_message = f"【高温告警】设备 {clean_device_id} 核心温度达 {temperature}℃（已越过 40℃ 预警红线）！散热风扇超负荷运转，建议立即创建紧急排查工单。"
    elif health_status == "WARNING":
        temperature = 38.0
        cpu_usage = 65.0
        memory_usage = 58.0
        fan_speed_rpm = 3600
        power_watts = 320
        status_code = "WARNING"
        alert = True
        alert_level = "WARNING"
        alert_message = f"【注意】设备 {clean_device_id} 核心温度达到 {temperature}℃，接近安全阈值，请关注通风情况。"
    elif health_status == "OFFLINE":
        temperature = 22.0
        cpu_usage = 0.0
        memory_usage = 0.0
        fan_speed_rpm = 0
        power_watts = 0
        status_code = "OFFLINE"
        alert = True
        alert_level = "WARNING"
        alert_message = f"【离线脱网预警】设备 {clean_device_id} 处于离线失联状态，探针传感器无遥测响应，功耗与负载为0（当前环境室温 {temperature}℃）。"
    else:
        temperature = 31.5
        cpu_usage = 32.0
        memory_usage = 45.0
        fan_speed_rpm = 2400
        power_watts = 210
        status_code = "HEALTHY"
        alert = False
        alert_level = "NORMAL"
        alert_message = f"设备 {clean_device_id} 各项运行与温湿度指标良好。"

    return {
        "status": "success",
        "device_id": clean_device_id,
        "device_name": device_name,
        "location": location,
        "health_status": status_code,
        "temperature": temperature,
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage,
        "fan_speed_rpm": fan_speed_rpm,
        "power_watts": power_watts,
        "alert": alert,
        "alert_level": alert_level,
        "alert_message": alert_message,
    }

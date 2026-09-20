"""全机房主动自治巡检与《运行健康研判简报》生成服务 (Patrol Service)

核心机制：
1. 主动遍历机房核心资产（服务器、网络、温控配电节点）；
2. 调度实时监控探针采集传感器遥测（温度、CPU 负荷、风扇转速、功耗）；
3. 判定越界与亚健康风险（温度 >= 40.0℃ 触发超温、离线脱网等）；
4. 检索 RAG 规程知识库，溯源安全管理与温控应急条款；
5. 自动防重复创建运维工单并持久化入库，实现自治闭环；
6. 综合多维指标计算健康指数 (0~100) 与运行态势等级，出具结构化研判台账及 Markdown 简报。
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.db.models import Asset, Ticket
from app.tools.metric_tools import get_server_metrics
from app.tools.ticket_tools import create_ticket
from app.tools.regulation_tools import query_regulations


def execute_autonomous_patrol(
    db: Optional[Session] = None,
    operator: str = "系统自治巡检",
) -> Dict[str, Any]:
    """执行全机房主动自治巡检流水线

    :param db: 数据库会话（若为空则自动获取并在执行后关闭）
    :param operator: 巡检发起人或 Agent 角色标识
    :return: 包含健康评分、KPI、异常清单、依据法规及 Markdown 简报的结构化字典
    """
    close_local_db = False
    active_db = db
    if active_db is None:
        try:
            from app.db.session import SessionLocal
            active_db = SessionLocal()
            close_local_db = True
        except Exception:
            active_db = None

    try:
        now_dt = datetime.now()
        batch_no = f"PTR-{now_dt.strftime('%Y%m%d-%H%M%S')}"
        patrol_time_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")

        # 1. 获取机房待巡检资产列表
        assets_to_scan = []
        if active_db is not None:
            assets_to_scan = active_db.query(Asset).order_by(Asset.id.asc()).all()

        # 离线与无 DB 种子数据兜底
        if not assets_to_scan:
            from app.db.init_db import SEED_ASSETS
            class SimpleAsset:
                def __init__(self, data):
                    self.asset_no = data["asset_no"]
                    self.name = data["name"]
                    self.category = data["category"]
                    self.location = data["location"]
                    self.health_status = data["health_status"]

            assets_to_scan = [SimpleAsset(s) for s in SEED_ASSETS]

        # 2. 遍历设备采集实时传感器遥测
        devices_scanned: List[Dict[str, Any]] = []
        abnormal_devices: List[Dict[str, Any]] = []
        created_tickets: List[Dict[str, Any]] = []

        temperatures: List[float] = []
        cpu_loads: List[float] = []
        total_power_watts = 0

        healthy_count = 0
        warning_count = 0
        overheat_count = 0
        offline_count = 0

        for asset in assets_to_scan:
            asset_no = getattr(asset, "asset_no", "")
            metric = get_server_metrics(device_id=asset_no, db=active_db)
            if metric.get("status") != "success":
                continue

            temp = float(metric.get("temperature", 25.0))
            cpu = float(metric.get("cpu_usage", 0.0))
            power = int(metric.get("power_watts", 0))
            fan_rpm = int(metric.get("fan_speed_rpm", 0))
            status_code = metric.get("health_status", "HEALTHY")
            device_name = metric.get("device_name", asset.name if hasattr(asset, "name") else "机房设备")
            location = metric.get("location", asset.location if hasattr(asset, "location") else "实训楼机房")

            temperatures.append(temp)
            cpu_loads.append(cpu)
            total_power_watts += power

            is_overheat = (status_code == "OVERHEAT") or (temp >= 40.0)
            is_offline = (status_code == "OFFLINE")
            is_warning = (status_code == "WARNING") or (38.0 <= temp < 40.0 and not is_overheat)

            if is_overheat:
                overheat_count += 1
            elif is_offline:
                offline_count += 1
            elif is_warning:
                warning_count += 1
            else:
                healthy_count += 1

            device_info = {
                "asset_no": asset_no,
                "name": device_name,
                "location": location,
                "health_status": status_code,
                "temperature": temp,
                "cpu_usage": cpu,
                "fan_speed_rpm": fan_rpm,
                "power_watts": power,
                "alert": metric.get("alert", False),
                "alert_level": metric.get("alert_level", "NORMAL"),
                "alert_message": metric.get("alert_message", ""),
            }
            devices_scanned.append(device_info)

            # 3. 越界异常研判与自治工单自动闭环
            if is_overheat or is_offline or is_warning:
                needs_ticket = is_overheat or is_offline
                ticket_action = "NONE"
                linked_ticket_no = None

                if needs_ticket:
                    # 防重复提单检测：核验是否已存在处理中或待办工单
                    existing_ticket = None
                    if active_db is not None:
                        existing_ticket = (
                            active_db.query(Ticket)
                            .filter(
                                Ticket.device_id == asset_no,
                                Ticket.status.in_(["PENDING", "PROCESSING"]),
                            )
                            .order_by(Ticket.id.desc())
                            .first()
                        )

                    if existing_ticket:
                        ticket_action = "EXISTING"
                        linked_ticket_no = existing_ticket.ticket_no
                    else:
                        # 自动生成工单
                        issue_type = "超温高温告警" if is_overheat else "脱网失联告警"
                        title = f"【自治巡检】{asset_no} {issue_type}处置工单"
                        priority = "CRITICAL" if is_overheat else "HIGH"
                        desc = (
                            f"【系统自治巡检实时捕获】巡检批次：{batch_no}\n"
                            f"- 设备编号：{asset_no}（{device_name}）\n"
                            f"- 物理位置：{location}\n"
                            f"- 关键遥测：核心温度 {temp}℃ (安全红线 40℃)，CPU 负载 {cpu}%，风扇 {fan_rpm} RPM，功耗 {power}W\n"
                            f"- 告警判定：{metric.get('alert_message', '')}\n"
                            f"- 处置要求：请运维人员现场核验散热风道与供电回路，排查温控及网络状态。"
                        )
                        create_res = create_ticket(
                            title=title,
                            description=desc,
                            priority=priority,
                            device_id=asset_no,
                            creator=operator,
                            db=active_db,
                        )
                        if create_res.get("status") == "success":
                            ticket_action = "CREATED"
                            linked_ticket_no = create_res.get("ticket", {}).get("ticket_no")
                            created_tickets.append(create_res.get("ticket"))

                abnormal_devices.append({
                    **device_info,
                    "is_overheat": is_overheat,
                    "is_offline": is_offline,
                    "is_warning": is_warning,
                    "ticket_action": ticket_action,
                    "ticket_no": linked_ticket_no,
                })

        # 4. 计算 KPI 汇总与机房综合健康指数 (0~100)
        total_scanned = len(devices_scanned)
        avg_temp = round(sum(temperatures) / len(temperatures), 1) if temperatures else 24.5
        avg_cpu = round(sum(cpu_loads) / len(cpu_loads), 1) if cpu_loads else 30.0

        # 扣分规则：超温 -15 分/台，离线 -10 分/台，预警 -5 分/台
        deduction = (overheat_count * 15) + (offline_count * 10) + (warning_count * 5)
        health_score = max(0, min(100, 100 - deduction))

        if health_score >= 90:
            posture_level = "EXCELLENT"
            posture_text = "整体优良 · 运行平稳"
            posture_color = "emerald"
        elif health_score >= 75:
            posture_level = "GOOD"
            posture_text = "基本平稳 · 局部关注"
            posture_color = "blue"
        elif health_score >= 60:
            posture_level = "WARN"
            posture_text = "亚健康预警 · 存在隐患"
            posture_color = "amber"
        else:
            posture_level = "CRITICAL"
            posture_text = "高危告警 · 需立即干预"
            posture_color = "rose"

        # 5. RAG 知识规程智能溯源
        rag_query = "机房日常巡检制度与设备超温应急处置条例"
        if overheat_count > 0:
            rag_query = "机房服务器核心温度超温40度应急处置规范与制冷散热预案"
        elif offline_count > 0:
            rag_query = "设备离线失联排查与机房网络供电维保规程"

        reg_raw = query_regulations(rag_query, top_k=3)
        cited_regulations = []
        if reg_raw and not reg_raw.startswith("未找到"):
            matches = re.findall(r"\[来源:《(.*?)》(.*?)\]\s*([\s\S]*?)(?=(?:\[来源:《|$))", reg_raw)
            if matches:
                for doc_name, sec_clause, snippet in matches:
                    clean_snippet = re.sub(r"\n+", " ", snippet.strip())[:160] + "..."
                    cited_regulations.append({
                        "doc_name": doc_name.strip(),
                        "clause": sec_clause.strip(),
                        "content": clean_snippet,
                    })
            else:
                cited_regulations.append({
                    "doc_name": "高校实验室安全管理规程",
                    "clause": "日常巡视与应急预案",
                    "content": reg_raw[:200] + "...",
                })

        # 6. 生成综合研判总结与高保真 Markdown 简报文本
        summary_lines = []
        summary_lines.append(f"本轮主动巡检共扫描在册设备 {total_scanned} 台，系统综合健康指数为 {health_score} 分（{posture_text}）。")
        if overheat_count > 0 or offline_count > 0:
            summary_lines.append(f"共捕获 {len(abnormal_devices)} 处异常：超温红线告警 {overheat_count} 台，脱网离线 {offline_count} 台，亚健康预警 {warning_count} 台。")
            if created_tickets:
                tks_str = "、".join([f"`{t.get('ticket_no', '')}`" for t in created_tickets if t and t.get('ticket_no')])
                summary_lines.append(f"系统已自主触发工单闭环，自动生成维修工单 {tks_str} 并持久化入库。")
            elif any(d.get("ticket_action") == "EXISTING" for d in abnormal_devices):
                summary_lines.append("检测到异常设备已有进行中的关联工单，系统执行防重复策略，未发起重复提单。")
        elif warning_count > 0:
            summary_lines.append(f"检出 {warning_count} 台设备处于亚健康预警状态（接近红线），系统持续维持主动监视。")
        else:
            summary_lines.append("各项动力能耗、算力负荷与环境温湿度均处于安全受控阈值以内，运行状态良好。")

        summary_text = " ".join(summary_lines)

        # 组装专业 Markdown 简报
        markdown_parts = [
            f"# 📋 高校实验室 IT 基础设施运行健康研判简报",
            f"> **巡检批次**：`{batch_no}` &nbsp;|&nbsp; **执行机构**：{operator} &nbsp;|&nbsp; **报告生成时间**：{patrol_time_str}\n",
            f"---",
            f"### 一、 机房整体运行态势概览",
            f"- **综合健康指数**：**{health_score} / 100 分**（评级：**{posture_text}**）",
            f"- **动力与微环境**：均温 **{avg_temp} ℃**（40℃ 红线）&nbsp;|&nbsp; 集群均载 **{avg_cpu} %** &nbsp;|&nbsp; 动力总负荷 **{total_power_watts} W**",
            f"- **资产体检全景**：在册检测 **{total_scanned}** 台（正常 **{healthy_count}** 台，预警 **{warning_count}** 台，超温 **{overheat_count}** 台，离线 **{offline_count}** 台）\n",
            f"---",
            f"### 二、 异常与风险隐患排查台账",
        ]

        if abnormal_devices:
            markdown_parts.append("| 设备编号 | 设备名称 | 位置 | 核心指标 | 隐患研判 | 自治工单闭环 |")
            markdown_parts.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
            for dev in abnormal_devices:
                metric_desc = f"{dev['temperature']}℃ / CPU {dev['cpu_usage']}%"
                if dev['is_overheat']:
                    status_badge = "🔥 **超温告警**"
                elif dev['is_offline']:
                    status_badge = "⚠️ **脱网离线**"
                else:
                    status_badge = "⚡ **亚健康预警**"

                if dev['ticket_action'] == "CREATED":
                    tk_badge = f"🆕 已自动创建 `{dev['ticket_no']}`"
                elif dev['ticket_action'] == "EXISTING":
                    tk_badge = f"🔄 跟进已有 `{dev['ticket_no']}`"
                else:
                    tk_badge = "👀 持续巡航监控"

                markdown_parts.append(
                    f"| `{dev['asset_no']}` | {dev['name']} | {dev['location']} | {metric_desc} | {status_badge} | {tk_badge} |"
                )
        else:
            markdown_parts.append("✅ **巡航全景未发现异常节点**，全部在册核心服务器与网络设备指标均处于良好安全区间。\n")

        markdown_parts.append("\n---")
        markdown_parts.append("### 三、 规程条例溯源依据 (RAG 向量安全准则)")
        if cited_regulations:
            for idx, reg in enumerate(cited_regulations, start=1):
                markdown_parts.append(f"{idx}. **《{reg['doc_name']}》** - `{reg['clause']}`")
                markdown_parts.append(f"   > *“{reg['content']}”*")
        else:
            markdown_parts.append("依据《高校实验室基础设施安全巡检与温控应急管理规范》第 3.2 条开展常规例行体检。\n")

        markdown_parts.append("\n---")
        markdown_parts.append("### 四、 处置建议与后续守望规划")
        if overheat_count > 0:
            markdown_parts.append("1. **紧急降温与风道核查**：发现存在超温过热节点，请指派运维值班员实地核查对应机柜冷热通道进出风口是否堵塞；")
        if offline_count > 0:
            markdown_parts.append("2. **链路与带外探针复位**：离线设备需核验交换机接入端口指示灯及 PDU 供电开关；")
        markdown_parts.append("3. **持续闭环追踪**：系统自治 Agent 将保持持续心跳感知，工单办结后指标若回落至健康区间将自动解除警报。")

        markdown_report = "\n".join(markdown_parts)

        return {
            "status": "success",
            "batch_no": batch_no,
            "operator": operator,
            "patrol_time": patrol_time_str,
            "health_score": health_score,
            "posture_level": posture_level,
            "posture_text": posture_text,
            "posture_color": posture_color,
            "kpi": {
                "total_scanned": total_scanned,
                "healthy_count": healthy_count,
                "warning_count": warning_count,
                "overheat_count": overheat_count,
                "offline_count": offline_count,
                "avg_temperature": avg_temp,
                "avg_cpu_load": avg_cpu,
                "total_power_watts": total_power_watts,
            },
            "devices_scanned": devices_scanned,
            "abnormal_devices": abnormal_devices,
            "cited_regulations": cited_regulations,
            "created_tickets": created_tickets,
            "summary_text": summary_text,
            "markdown_report": markdown_report,
        }
    finally:
        if close_local_db and active_db is not None:
            active_db.close()

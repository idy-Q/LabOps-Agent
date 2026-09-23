"""机房全网主动自治巡检工具 (Patrol Tools)"""

from typing import Any, Dict, Optional
from sqlalchemy.orm import Session

from app.tools.registry import tool


@tool(
    name="run_autonomous_patrol",
    description="执行全机房主动自治巡检体检。遍历服务器、网络与配电温控设备，实时采集温度、负载与功耗，结合规程库研判超温(>=40℃)与脱网风险，自动防重复创建运维工单并生成综合健康态势研判简报。",
)
def run_autonomous_patrol(
    operator: str = "系统自治巡检",
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """执行全网主动自治体检并生成研判简报

    :param operator: 发起巡检的操作员或系统角色名称，默认为 '系统自治巡检'
    :param db: 数据库会话 (由 Agent 执行引擎自动注入)
    :return: 包含体检得分、KPI、异常清单、工单及 Markdown 简报的结构化结果
    """
    from app.services.patrol_service import execute_autonomous_patrol

    report = execute_autonomous_patrol(db=db, operator=operator)
    return {
        "status": "success",
        "message": f"全机房主动自治巡检完成，综合健康得分 {report.get('health_score')} 分（{report.get('posture_text')}）",
        "report": report,
        "created_tickets": report.get("created_tickets", []),
    }

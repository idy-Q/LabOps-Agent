"""手写轻量级 ReAct 调度引擎 (Agent Core)

基于第一性原理与原生 Python 手写，无任何第三方黑盒 Agent 框架（如 LangChain）。
具备：
1. 白盒化 ReAct (Reasoning + Acting) 状态机循环 (带 max_steps 保护)
2. 双模驱动（支持真实商业大模型 OpenAI 兼容端点 + 零依赖确定性本地 Mock 大脑）
3. 同步调用 `run()` 与流式生成器 `stream_run()`（输出标准结构化事件，供 SSE 联动）
4. 全流程自动持久化写入 AuditLog 与 ChatHistory 表
"""

import json
import logging
import re
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Generator, List, Optional
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import ChatHistory
from app.agent.prompts import SYSTEM_PROMPT
from app.tools.registry import execute_tool, get_tools_schemas

logger = logging.getLogger(__name__)


@dataclass
class AgentEvent:
    """Agent 流式事件结构 (用于阶段 4 SSE 标准契约)"""

    type: str  # think, tool_start, tool_end, content, done
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type, **self.data}


@dataclass
class AgentResult:
    """Agent 同步执行结果"""

    session_id: str
    trace_id: str
    content: str
    thought: str
    steps: int
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)


class MockDecisionBrain:
    """确定性本地规则推理大脑 (Mock Brain)

    用于无 API Key、断网离线与自动化单测兜底演示。
    具备对机房巡检、超温告警、工单创建与流转、资产台账检索与借还的确定性多步状态决策能力。
    """

    @classmethod
    def decide(
        cls,
        messages: List[Dict[str, Any]],
        user_role: Optional[str] = None,
        user_name: Optional[str] = None,
        user_department: Optional[str] = None,
    ) -> Dict[str, Any]:
        """根据当前对话历史和工具返回结果，决定下一步行为 (思考/调工具/最终回复)"""
        system_content = ""
        user_prompt = ""
        for m in messages:
            if m.get("role") == "system":
                system_content = m.get("content", "")
            elif m.get("role") == "user":
                user_prompt = m.get("content", "")

        # 若未直接传参，则从 system 提示词中回溯提取注入的身份元数据
        if not user_role or not user_name:
            id_match = re.search(r"【当前交互用户身份】：(.*?)\s*\(角色:\s*([A-Za-z_]+)(?:,\s*归属:\s*(.*?))?\)", system_content)
            if id_match:
                user_name = user_name or id_match.group(1).strip()
                user_role = user_role or id_match.group(2).strip()
                user_department = user_department or (id_match.group(3).strip() if id_match.group(3) else None)

        role = (user_role or "ADMIN").upper()
        name = user_name or "管理员"
        dept_desc = f" ({user_department})" if user_department else ""

        # 收集已执行过的工具名与结果
        executed_tools: List[str] = []
        tool_results: Dict[str, Any] = {}
        for m in messages:
            if m.get("role") == "tool":
                t_name = m.get("name", "")
                executed_tools.append(t_name)
                try:
                    tool_results[t_name] = json.loads(m.get("content", "{}"))
                except Exception:
                    tool_results[t_name] = {}

        # 提取关键实体 (当前轮次优先，若无则从多轮会话历史逆向回溯提取)
        device_match = re.search(r"(DEV[_-][A-Z0-9]+-[0-9]+|DEV-[A-Z]+-[0-9]+)", user_prompt, re.IGNORECASE)
        ticket_match = re.search(r"(TK-[0-9]{8}-[A-Za-z0-9]+)", user_prompt, re.IGNORECASE)

        # 多轮会话实体回溯溯源 (代词如“它”、“刚才的设备”、“刚才的工单”)
        if not device_match:
            for m in reversed(messages[:-1]):
                content_txt = str(m.get("content", "") or "")
                dm = re.search(r"(DEV[_-][A-Z0-9]+-[0-9]+|DEV-[A-Z]+-[0-9]+)", content_txt, re.IGNORECASE)
                if dm:
                    device_match = dm
                    break

        if not ticket_match:
            for m in reversed(messages[:-1]):
                content_txt = str(m.get("content", "") or "")
                tm = re.search(r"(TK-[0-9]{8}-[A-Za-z0-9]+)", content_txt, re.IGNORECASE)
                if tm:
                    ticket_match = tm
                    break

        device_id = device_match.group(1).upper().replace("_", "-") if device_match else "DEV-SRV-201"
        ticket_no = ticket_match.group(1).upper() if ticket_match else None

        # -------------------------------------------------------------
        # 决策逻辑 0：规章制度与应急规范问答检索 (query_regulations) 优先判断
        # 避免用户咨询规程、借用规则、办结流程、应急预案时误触发操作或权限拦截
        # -------------------------------------------------------------
        is_query_regulations = (
            any(kw in user_prompt for kw in ["规章", "制度", "规范", "用电", "应急", "PDU", "功率", "功耗", "审批流程", "上限", "维保", "预案", "滤网", "巡检要求", "巡检时间", "巡检频次", "巡检周期", "空调故障"])
            or any(kw in user_prompt for kw in ["借用规则", "借调规则", "借用流程", "借调流程", "归还规则", "归还流程", "办结流程", "关闭流程", "流转流程", "维修流程", "报修流程", "借用规程", "借用制度", "借用规定"])
            or ("巡检" in user_prompt and any(kw in user_prompt for kw in ["规定", "要求", "怎么做", "时间", "周期", "频次", "标准", "指引", "规则"]))
            or (any(kw in user_prompt for kw in ["怎么处理", "如何处理", "处置流程", "处置预案", "处理预案", "应急方案", "应急措施"]) and not device_match)
            or (any(kw in user_prompt for kw in ["规则是什么", "规定是什么", "流程是什么", "怎么借", "如何借", "怎么还", "如何还", "可以借吗", "能否借用", "借用要求", "借用标准"]))
        ) and not any(kw in user_prompt for kw in ["查询工单", "创建工单", "新建工单"])
        if is_query_regulations:
            if "query_regulations" not in executed_tools:
                return {
                    "thought": "用户询问机房管理规章制度、操作规程或应急规范，调用 query_regulations 工具进行检索。",
                    "tool_calls": [
                        {
                            "id": f"call_{uuid.uuid4().hex[:8]}",
                            "function": {
                                "name": "query_regulations",
                                "arguments": json.dumps({"query": user_prompt}, ensure_ascii=False),
                            },
                        }
                    ],
                }

            r_res = tool_results.get("query_regulations", "")
            if isinstance(r_res, dict):
                reg_text = r_res.get("data") or r_res.get("message") or str(r_res)
            else:
                reg_text = str(r_res)
            return {
                "thought": "检索到相关规章制度与应急预案，根据条款回答用户并标注来源。",
                "content": f"【规章制度查询结果】\n{reg_text}",
            }

        # -------------------------------------------------------------
        # 决策逻辑 1：工单状态推进流转 (update_ticket_status)
        # -------------------------------------------------------------
        is_ticket_inquiry = any(kw in user_prompt for kw in ["查询", "查看", "检索", "详情", "进展", "进度", "情况", "是什么", "看下", "有哪些"])
        is_ticket_update = (
            any(kw in user_prompt for kw in ["更新工单", "修改工单", "办结工单", "关闭工单", "解决工单", "处理工单", "受理工单", "认领工单", "流转工单", "推进工单", "结单"])
            or (
                ticket_no
                and any(kw in user_prompt for kw in ["更新为", "修改为", "改为", "设为", "推进为", "标记为", "变更为", "设成", "改成", "办结", "关闭", "归档", "受理", "认领"])
            )
            or (
                ticket_no
                and any(kw in user_prompt for kw in ["更新", "推进", "关闭", "办结", "解决"])
                and not is_ticket_inquiry
            )
        ) and not is_query_regulations
        if is_ticket_update:
            # RBAC 拦截 A: 学生角色对工单严格只读，无权流转或办结工单
            if role == "STUDENT":
                return {
                    "thought": f"检测到当前交互用户角色为学生（{name}），根据机房运维分权管理规程，学生对工单仅具备只读权限，无权更新或办结工单，执行权限硬拦截。",
                    "content": (
                        f"【权限拦截警报】工单流转操作已被系统拦截！\n\n"
                        f"- 当前操作用户：{name}（角色: 学生 STUDENT{dept_desc}）\n"
                        f"- 拦截原因：学生角色对机房运维工单仅具备只读查看权限，无权受理、推进、关闭或办结运维工单。\n"
                        f"- 处置指引：如需反馈设备故障或跟进维修进度，请联系机房巡视教师或专职管理员跟进处置。"
                    ),
                }

            target_status = "RESOLVED"
            if any(kw in user_prompt for kw in ["关闭", "办结", "CLOSED", "归档"]):
                target_status = "CLOSED"
            elif any(kw in user_prompt for kw in ["解决", "RESOLVED", "已解决"]):
                target_status = "RESOLVED"
            elif any(kw in user_prompt for kw in ["处理中", "进行中", "PROCESSING", "受理", "认领"]):
                target_status = "PROCESSING"
            elif any(kw in user_prompt for kw in ["待办", "PENDING"]):
                target_status = "PENDING"

            # RBAC 拦截 B: 教师角色禁止直接办结/关闭/归档工单（需机房主管实地验收核验闭环）
            if role == "TEACHER" and (target_status in ("CLOSED", "RESOLVED") or any(kw in user_prompt for kw in ["办结", "关闭", "归档", "CLOSED", "解决", "RESOLVED", "已解决"])):
                return {
                    "thought": f"检测到当前用户为教师（{name}），请求办结/关闭工单。根据机房闭环验收规范，工单办结需机房专职主管验收核验闭环，执行拦截。",
                    "content": (
                        f"【权限拦截警报】工单办结/归档操作已被系统拦截！\n\n"
                        f"- 当前操作用户：{name}（角色: 教师 TEACHER{dept_desc}）\n"
                        f"- 拦截原因：工单办结需机房专职主管验收核验闭环，教师仅可将工单认领受理推进至处理中（PROCESSING），无权直接办结或归档工单。\n"
                        f"- 处置指引：如检修维保已完成，请将工单受理状态标记为处理中，并联系机房专职主管（王主管）进行现场实地验收与终审闭环关单。"
                    ),
                }

            if "update_ticket_status" not in executed_tools:
                target_tk = ticket_no or "TK-20260901-001"
                append_match = re.search(r"(?:说明|记录|备注|处置|追加)[：:\s]*([^\n，。]+)", user_prompt)
                desc_append = append_match.group(1).strip() if append_match else f"{name}指令推进工单状态"

                return {
                    "thought": f"用户（{name}，角色: {role}）请求推进工单状态，调用 update_ticket_status 将工单 {target_tk} 更新为 {target_status}。",
                    "tool_calls": [
                        {
                            "id": f"call_{uuid.uuid4().hex[:8]}",
                            "function": {
                                "name": "update_ticket_status",
                                "arguments": json.dumps(
                                    {
                                        "ticket_no": target_tk,
                                        "status": target_status,
                                        "description_append": desc_append,
                                    },
                                    ensure_ascii=False,
                                ),
                            },
                        }
                    ],
                }

            u_res = tool_results.get("update_ticket_status", {})
            msg = u_res.get("message", "工单状态已更新")
            return {
                "thought": "已完成工单状态更新并留痕，向操作用户返回流转结果。",
                "content": f"【工单状态流转通知】\n{msg}",
            }

        # -------------------------------------------------------------
        # 决策逻辑 2：资产健康状态变更 (update_asset_health)
        # -------------------------------------------------------------
        is_health_inquiry = any(q in user_prompt for q in ["查询", "查看", "是什么", "如何", "怎样", "巡检", "排查", "监控", "指标"])
        is_asset_health_update = (
            any(kw in user_prompt for kw in [
                "更新设备健康", "变更健康", "修改健康", "恢复健康", "更新健康", "调整健康",
                "健康状态改为", "状态改为健康", "标记为健康", "标记为良好", "标记为正常", "设为正常", "设为良好",
                "标记为预警", "标记为过热", "标记为离线", "设为预警", "设为过热", "设为离线",
                "改为良好", "改为正常", "改为预警", "改为过热", "改为离线", "改为健康",
                "改成良好", "改成正常", "改成预警", "改成过热", "改成离线", "改成健康",
            ])
            or (
                (device_match or "设备" in user_prompt)
                and any(kw in user_prompt for kw in ["健康状态更新为", "健康更新为", "状态更新为", "状态改为", "健康改为", "设为", "改为", "改成", "标记为"])
                and any(h in user_prompt for h in ["HEALTHY", "WARNING", "OVERHEAT", "OFFLINE", "良好", "正常", "预警", "过热", "离线", "健康"])
            )
        ) and not is_query_regulations and not is_health_inquiry
        if is_asset_health_update:
            # RBAC 权限硬拦截: 仅专职管理员 ADMIN 可修改健康状态，STUDENT 与 TEACHER 严正拦截
            if role != "ADMIN":
                role_label = "学生 STUDENT" if role == "STUDENT" else "教师 TEACHER"
                return {
                    "thought": f"检测到当前交互用户角色为{role_label}（{name}），无权修改硬件健康度，执行权限硬拦截并驳回。",
                    "content": (
                        f"【权限拦截警报】设备健康状态变更已被系统拦截！\n\n"
                        f"- 当前操作用户：{name}（角色: {role_label}{dept_desc}）\n"
                        f"- 拦截原因：机房服务器硬件健康度标定与状态变更属于机房专职主管管理权限，非管理员用户禁止擅自篡改硬件健康台账。\n"
                        f"- 处置指引：如发现设备存在超温、脱网或硬件故障，请发起运维报修工单，由机房专职主管实地检修并统一标定状态。"
                    ),
                }

            if "update_asset_health" not in executed_tools:
                target_health = "HEALTHY"
                if any(kw in user_prompt for kw in ["HEALTHY", "良好", "正常", "健康"]):
                    target_health = "HEALTHY"
                elif any(kw in user_prompt for kw in ["WARNING", "预警"]):
                    target_health = "WARNING"
                elif any(kw in user_prompt for kw in ["OVERHEAT", "过热", "高温"]):
                    target_health = "OVERHEAT"
                elif any(kw in user_prompt for kw in ["OFFLINE", "离线", "故障"]):
                    target_health = "OFFLINE"

                return {
                    "thought": f"管理员请求更新设备健康等级，调用 update_asset_health 将设备 {device_id} 标记为 {target_health}。",
                    "tool_calls": [
                        {
                            "id": f"call_{uuid.uuid4().hex[:8]}",
                            "function": {
                                "name": "update_asset_health",
                                "arguments": json.dumps(
                                    {"asset_no": device_id, "health_status": target_health},
                                    ensure_ascii=False,
                                ),
                            },
                        }
                    ],
                }

            h_res = tool_results.get("update_asset_health", {})
            return {
                "thought": "设备健康状态更新完毕，向管理员同步台账变更。",
                "content": f"【设备健康变更通知】\n{h_res.get('message', '设备健康状态更新完成')}",
            }

        # -------------------------------------------------------------
        # 决策逻辑 3：设备资产借用登记 (borrow_asset)
        # -------------------------------------------------------------
        is_borrow = (
            any(kw in user_prompt for kw in ["借用", "借出", "借走", "借调", "借领", "租借"])
            or ("借" in user_prompt and any(w in user_prompt for w in ["我要", "我想", "申请", "帮", "给", "办理", "借一台", "借个", "借一下", "DEV-", "服务器", "设备"]))
        ) and not is_query_regulations
        if is_borrow:
            # RBAC 拦截 A: 学生坚决不调用 borrow_asset 工具，直接返回严正权限拦截通知
            if role == "STUDENT":
                return {
                    "thought": f"检测到当前交互用户角色为学生（{name}），根据机房资产管理条例，在读学生无权借调机房服务器或固定设备，坚决不调用 borrow_asset 工具，执行权限硬拦截。",
                    "content": (
                        f"【权限拦截警报】借调申请已被系统拦截！\n\n"
                        f"- 当前操作用户：{name}（角色: 学生 STUDENT{dept_desc}）\n"
                        f"- 拦截原因：根据《高校机房资产安全管理条例》，在读学生无权直接办理机房服务器及固定资产的借调出库手续。\n"
                        f"- 处置指引：如需开展课程实验或学术科研，需指导教师办理，请联系您的导师或实验课程主讲教师登录系统进行设备借调登记。"
                    ),
                }

            if "borrow_asset" not in executed_tools:
                if role == "TEACHER":
                    # RBAC 防冒名硬绑定: 教师借用设备时，borrower 自动强制锁定为教师姓名，禁止伪造他人
                    borrower = name
                else:
                    borrower = name
                    # 1. 优先提取 "帮/给/借给 X [办理/借]"（支持带教研室括号与空格）
                    alt_match = re.search(r"(?:帮|给|借给|借用人[是：:\s]*)\s*([^\s，。（）\(\)]+?)(?:\s*\(.*?\))?\s*(?:办理|借)", user_prompt)
                    if alt_match and alt_match.group(1).strip():
                        borrower = alt_match.group(1).strip()
                    else:
                        # 2. 匹配常见姓名与角色称谓
                        name_match = re.search(r"([^\s，。（）\(\)]+?(?:老师|同学|教授|工程师|主管|主任|院长|员|工)|张三|李四|王五)", user_prompt)
                        if name_match and name_match.group(1).strip():
                            borrower = name_match.group(1).strip()

                return {
                    "thought": f"用户（{name}，角色: {role}）发起资产借用申请，已锁定借调人为「{borrower}」，调用 borrow_asset 工具办理设备 {device_id} 的借用登记。",
                    "tool_calls": [
                        {
                            "id": f"call_{uuid.uuid4().hex[:8]}",
                            "function": {
                                "name": "borrow_asset",
                                "arguments": json.dumps({"asset_no": device_id, "borrower": borrower}, ensure_ascii=False),
                            },
                        }
                    ],
                }
            b_res = tool_results.get("borrow_asset", {})
            return {
                "thought": "资产借用登记操作完成，向管理员同步最新台账变动。",
                "content": f"【资产借用登记通知】\n{b_res.get('message', '借用操作已处理')}",
            }

        # -------------------------------------------------------------
        # 决策逻辑 4：设备资产归还 (return_asset)
        # -------------------------------------------------------------
        is_return = any(kw in user_prompt for kw in ["归还", "还设备", "还入库", "归还资产"]) and not is_query_regulations
        if is_return:
            # RBAC 拦截: 学生无权办理归还出入库
            if role == "STUDENT":
                return {
                    "thought": f"检测到当前交互用户角色为学生（{name}），学生无设备资产借还出入库权限，执行权限硬拦截。",
                    "content": (
                        f"【权限拦截警报】资产归还登记已被系统拦截！\n\n"
                        f"- 当前操作用户：{name}（角色: 学生 STUDENT{dept_desc}）\n"
                        f"- 拦截原因：在读学生无设备台账借还出入库权限。\n"
                        f"- 处置指引：请由借调教师本人或机房专职管理员统一办理资产归还交接入库手续。"
                    ),
                }

            if "return_asset" not in executed_tools:
                return {
                    "thought": f"用户（{name}，角色: {role}）发起设备归还申请，调用 return_asset 工具恢复设备 {device_id} 为可用状态。",
                    "tool_calls": [
                        {
                            "id": f"call_{uuid.uuid4().hex[:8]}",
                            "function": {
                                "name": "return_asset",
                                "arguments": json.dumps({"asset_no": device_id}, ensure_ascii=False),
                            },
                        }
                    ],
                }
            r_res = tool_results.get("return_asset", {})
            return {
                "thought": "资产归还已入库，向管理员同步台账状态。",
                "content": f"【资产归还登记通知】\n{r_res.get('message', '归还操作已处理')}",
            }

        # -------------------------------------------------------------
        # 决策逻辑 6：机房监控与设备健康/超温排查流程 (get_server_metrics)
        # -------------------------------------------------------------
        if any(kw in user_prompt for kw in ["指标", "监控", "温度", "巡检", "排查", "超温", "传感器", "cpu", "内存"]):
            if "get_server_metrics" not in executed_tools:
                return {
                    "thought": f"管理员指令涉及设备排查，优先感知设备 {device_id} 的实时运行指标与温度传感器数据。",
                    "tool_calls": [
                        {
                            "id": f"call_{uuid.uuid4().hex[:8]}",
                            "function": {
                                "name": "get_server_metrics",
                                "arguments": json.dumps({"device_id": device_id}, ensure_ascii=False),
                            },
                        }
                    ],
                }

            metrics = tool_results.get("get_server_metrics", {})
            # 严格校验：若工具返回错误（如设备编号不存在），如实向管理员报告，不虚构正常指标
            if metrics.get("status") == "error":
                err_msg = metrics.get("message", f"未在机房资产台账中找到编号为 '{device_id}' 的设备，请核实设备编号")
                return {
                    "thought": f"设备 {device_id} 传感器感知反馈异常或不存在，向管理员如实反馈排查结论。",
                    "content": f"【机房设备排查提示】\n排查异常：{err_msg}",
                }

            is_overheat = metrics.get("health_status") == "OVERHEAT" or metrics.get("temperature", 0) > 40.0

            if is_overheat and "create_ticket" not in executed_tools:
                temp = metrics.get("temperature", 43.5)
                return {
                    "thought": f"传感器数据表明设备 {device_id} 核心温度达到 {temp}℃（>40℃），处于 OVERHEAT 严重状态！按机房应急规程必须立即自动创建高优先级排查工单。",
                    "tool_calls": [
                        {
                            "id": f"call_{uuid.uuid4().hex[:8]}",
                            "function": {
                                "name": "create_ticket",
                                "arguments": json.dumps(
                                    {
                                        "title": f"{device_id} 核心温度过热紧急处置工单",
                                        "description": f"实时监控监测到设备核心温度达到 {temp}℃，超过安全阈值 40℃，散热负荷异常，触发 OVERHEAT 报警，需现场检修风道与制冷。",
                                        "priority": "HIGH",
                                        "device_id": device_id,
                                    },
                                    ensure_ascii=False,
                                ),
                            },
                        }
                    ],
                }

            # 工具调用全部闭环，输出最终总结
            ticket_res = tool_results.get("create_ticket", {}).get("ticket", {})
            t_no = ticket_res.get("ticket_no", "TK-待指派")
            temp = metrics.get("temperature", 31.5)
            status_code = metrics.get("health_status", "HEALTHY")

            if is_overheat:
                content = (
                    f"【机房运维排查汇报】\n"
                    f"- 目标设备：`{device_id}` ({metrics.get('device_name', '服务器')})\n"
                    f"- 物理位置：{metrics.get('location', '实训楼201')}\n"
                    f"- 核心指标：温度 **{temp}℃**（[超温告警] 超过40℃安全红线），CPU占用率 {metrics.get('cpu_usage', 88.5)}%\n"
                    f"- 研判等级：**{status_code}**（严重过热警报）\n"
                    f"- 闭环操作：系统已自动为您生成高优先级维修工单（工单号：`{t_no}`），并持久化写入数据库。\n"
                    f"- 处置建议：请通知后勤运维人员现场核验散热风扇与机房空调温控。"
                )
            elif status_code == "OFFLINE":
                content = (
                    f"【机房设备离线告警汇报】\n"
                    f"- 目标设备：`{device_id}` ({metrics.get('device_name', '设备')})\n"
                    f"- 物理位置：{metrics.get('location', '实训楼')}\n"
                    f"- 核心指标：探针失联（功耗 0W，风扇 0 RPM，环境室温 {temp}℃）\n"
                    f"- 研判等级：**OFFLINE**（离线脱网告警）\n"
                    f"- 处置建议：{metrics.get('alert_message', '设备处于离线失联状态，请现场排查网络连接与供电电源。')}"
                )
            elif status_code == "WARNING":
                content = (
                    f"【机房设备亚健康预警汇报】\n"
                    f"- 目标设备：`{device_id}` ({metrics.get('device_name', '设备')})\n"
                    f"- 物理位置：{metrics.get('location', '实训楼')}\n"
                    f"- 核心指标：温度 **{temp}℃**（接近40℃警戒线），CPU占用率 {metrics.get('cpu_usage', 65.0)}%\n"
                    f"- 研判等级：**WARNING**（亚健康预警）\n"
                    f"- 处置建议：{metrics.get('alert_message', '设备负载或温度偏高，建议持续关注运行负荷并安排巡检。')}"
                )
            else:
                content = (
                    f"【机房设备指标正常汇报】\n"
                    f"- 目标设备：`{device_id}` ({metrics.get('device_name', '服务器')})\n"
                    f"- 核心指标：温度 **{temp}℃**（正常），CPU占用率 {metrics.get('cpu_usage', 30.0)}%\n"
                    f"- 研判等级：**HEALTHY**（运行良好）\n"
                    f"- 处置结论：设备各项温湿度指标均在安全阈值以内，无需创建工单。"
                )
            return {"thought": "已完成指标采集与分析闭环，为管理员呈现清晰排查报告。", "content": content}

        # -------------------------------------------------------------
        # 决策逻辑 6：主动直接创建工单 (create_ticket)
        # -------------------------------------------------------------
        is_direct_create_ticket = any(
            kw in user_prompt for kw in ["创建工单", "新建工单", "提交工单", "提工单", "建立工单", "发起工单"]
        )
        if is_direct_create_ticket:
            if "create_ticket" not in executed_tools:
                title_match = re.search(r"(?:创建工单|新建工单|提交工单|提工单|建立工单|发起工单)[：:\s]*(.+)", user_prompt)
                raw_title = title_match.group(1).strip() if title_match else user_prompt
                priority = "HIGH" if any(kw in user_prompt for kw in ["紧急", "高", "CRITICAL", "HIGH"]) else "MEDIUM"
                target_dev = device_match.group(1).upper() if device_match else None

                return {
                    "thought": "管理员请求新建运维工单，调用 create_ticket 工具持久化入库。",
                    "tool_calls": [
                        {
                            "id": f"call_{uuid.uuid4().hex[:8]}",
                            "function": {
                                "name": "create_ticket",
                                "arguments": json.dumps(
                                    {
                                        "title": raw_title[:60],
                                        "description": f"管理员指令提单：{raw_title}",
                                        "priority": priority,
                                        "device_id": target_dev,
                                    },
                                    ensure_ascii=False,
                                ),
                            },
                        }
                    ],
                }

            t_res = tool_results.get("create_ticket", {})
            return {
                "thought": "工单创建完毕，向管理员呈现工单详情与编号。",
                "content": f"【工单创建成功】\n{t_res.get('message', '工单创建成功')}",
            }

        # -------------------------------------------------------------
        # 决策逻辑 7：查询资产台账 (query_assets)
        # -------------------------------------------------------------
        is_query_assets = (
            any(kw in user_prompt for kw in ["查询资产", "资产列表", "台账", "查设备", "查看设备", "设备台账", "搜索设备", "查询设备", "检索资产", "设备列表"])
            or ("资产" in user_prompt and any(kw in user_prompt for kw in ["查询", "查看", "检索", "列表", "搜索", "有哪些"]))
            or ("设备" in user_prompt and any(kw in user_prompt for kw in ["查询", "查看", "检索", "列表", "搜索", "有哪些"]) and not any(kw in user_prompt for kw in ["指标", "监控", "温度", "巡检", "排查", "超温", "借用", "借出", "归还"]))
        )
        if is_query_assets:
            if "query_assets" not in executed_tools:
                q_args: Dict[str, Any] = {"limit": 5}
                if "服务器" in user_prompt:
                    q_args["category"] = "服务器"
                elif "网络" in user_prompt:
                    q_args["category"] = "网络设备"
                elif any(k in user_prompt for k in ["温控", "配电", "空调", "UPS"]):
                    q_args["category"] = "配电温控"
                elif any(k in user_prompt for k in ["教学", "实验"]):
                    q_args["category"] = "实验教学"

                if any(k in user_prompt for k in ["过热", "OVERHEAT", "高温"]):
                    q_args["health_status"] = "OVERHEAT"
                elif any(k in user_prompt for k in ["预警", "WARNING"]):
                    q_args["health_status"] = "WARNING"
                elif any(k in user_prompt for k in ["正常", "良好", "HEALTHY"]):
                    q_args["health_status"] = "HEALTHY"
                elif any(k in user_prompt for k in ["离线", "OFFLINE"]):
                    q_args["health_status"] = "OFFLINE"

                if any(k in user_prompt for k in ["可借", "空闲", "AVAILABLE"]):
                    q_args["borrow_status"] = "AVAILABLE"
                elif any(k in user_prompt for k in ["已借", "使用中", "IN_USE"]):
                    q_args["borrow_status"] = "IN_USE"

                if "GPU" in user_prompt:
                    q_args["keyword"] = "GPU"

                return {
                    "thought": "管理员请求检索资产台账，调用 query_assets 工具查询机房设备记录。",
                    "tool_calls": [
                        {
                            "id": f"call_{uuid.uuid4().hex[:8]}",
                            "function": {
                                "name": "query_assets",
                                "arguments": json.dumps(q_args, ensure_ascii=False),
                            },
                        }
                    ],
                }
            q_res = tool_results.get("query_assets", {})
            count = q_res.get("count", 0)
            assets = q_res.get("assets", [])
            if count == 0:
                assets_brief = "（暂未检索到符合条件的设备资产）"
            else:
                assets_brief = "\n".join(
                    [f"- `{a.get('asset_no')}`: {a.get('name')} [{a.get('health_status')}]（位置: {a.get('location')}，借用状态: {a.get('borrow_status')}）" for a in assets[:5]]
                )
            return {
                "thought": "已检索到最新台账，向管理员汇总展示。",
                "content": f"【资产台账查询结果】\n共检索到 {count} 条相关资产记录：\n{assets_brief}",
            }

        # -------------------------------------------------------------
        # 决策逻辑 8：查询工单列表与工单状态进展 (query_tickets)
        # -------------------------------------------------------------
        if (
            any(kw in user_prompt for kw in ["查询工单", "工单列表", "待办工单", "历史工单", "所有工单", "查看工单", "检索工单", "工单进展", "工单进度", "工单详情"])
            or (ticket_no and is_ticket_inquiry)
            or (
                "工单" in user_prompt
                and any(kw in user_prompt for kw in ["查询", "查看", "检索", "列表", "有哪些", "待办", "进展", "进度", "状态", "详情"])
                and not any(kw in user_prompt for kw in ["创建", "新建", "提交", "提工单", "发起", "更新为", "修改为", "改为", "设为", "推进为", "标记为"])
            )
        ):
            if "query_tickets" not in executed_tools:
                t_args: Dict[str, Any] = {"limit": 5}
                if "待办" in user_prompt:
                    t_args["status"] = "PENDING"
                elif "处理中" in user_prompt:
                    t_args["status"] = "PROCESSING"
                elif "已解决" in user_prompt:
                    t_args["status"] = "RESOLVED"
                elif any(k in user_prompt for k in ["关闭", "办结", "已关闭"]):
                    t_args["status"] = "CLOSED"

                if any(k in user_prompt for k in ["紧急", "高优先级", "CRITICAL", "HIGH"]):
                    t_args["priority"] = "HIGH"

                if ticket_match:
                    t_args["ticket_no"] = ticket_match.group(1).upper()
                if device_match:
                    t_args["device_id"] = device_match.group(1).upper()

                return {
                    "thought": "管理员请求查询工单，调用 query_tickets 检索符合条件的运维工单。",
                    "tool_calls": [
                        {
                            "id": f"call_{uuid.uuid4().hex[:8]}",
                            "function": {
                                "name": "query_tickets",
                                "arguments": json.dumps(t_args, ensure_ascii=False),
                            },
                        }
                    ],
                }
            t_res = tool_results.get("query_tickets", {})
            count = t_res.get("count", 0)
            tickets = t_res.get("tickets", [])
            if count == 0:
                tk_brief = "（当前未检索到符合条件的工单记录）"
            else:
                tk_brief = "\n".join(
                    [f"- `{t.get('ticket_no')}`: {t.get('title')} [{t.get('status')}]（优先级: {t.get('priority')}）" for t in tickets[:5]]
                )
            return {
                "thought": "已获取工单列表，呈现给管理员。",
                "content": f"【工单列表检索结果】\n当前系统共有 {count} 条符合条件的工单记录：\n{tk_brief}",
            }

        # 原逻辑9已被移至上方

        # 默认通用回复
        return {
            "thought": "用户进行常规询问，说明管家职能并提供运维指引。",
            "content": (
                "您好！我是高校机房智能运维管家（LabOps-Agent）。\n"
                "我具备机房服务器指标感知、温度超标（>40℃）自动工单闭环、资产借还登记与台账审计能力。\n"
                "您可以对我发送指令，例如：\n"
                "- `“查询DEV-SRV-201监控指标，若异常请自动提单”`\n"
                "- `“帮张老师办理DEV-SRV-202借出登记”`\n"
                "- `“查询当前机房全部异常设备台账”`"
            ),
        }


class ReActEngine:
    """手写 ReAct 调度引擎核心类"""

    def __init__(self, max_steps: Optional[int] = None):
        self.max_steps = max_steps or settings.REACT_MAX_STEPS
        self.mock_mode = settings.AGENT_MOCK_MODE.lower()

    def _should_use_mock(self) -> bool:
        """判定当前是否应采用本地 Mock 大脑"""
        if self.mock_mode == "mock":
            return True
        if self.mock_mode == "real":
            return False
        # auto 模式下：若无 Key 则默认自动降级为 Mock 大脑
        return not bool((settings.OPENAI_API_KEY or "").strip())

    def _call_llm(
        self,
        messages: List[Dict[str, Any]],
        tools_schemas: List[Dict[str, Any]],
        user_role: str = "ADMIN",
        user_name: str = "管理员",
        user_department: Optional[str] = None,
    ) -> Dict[str, Any]:
        """统一调用决策大脑（真实 OpenAI 协议 API 或确定性 Mock 大脑）"""
        if self._should_use_mock():
            return MockDecisionBrain.decide(
                messages,
                user_role=user_role,
                user_name=user_name,
                user_department=user_department,
            )

        try:
            from openai import OpenAI

            client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL,
            )
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL_NAME,
                messages=messages,
                tools=tools_schemas if tools_schemas else None,
                tool_choice="auto" if tools_schemas else None,
                temperature=0.2,
            )
            choice = response.choices[0]
            msg = choice.message
            tool_calls = []
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    tool_calls.append(
                        {
                            "id": tc.id,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                    )
            return {
                "thought": getattr(msg, "reasoning_content", None) or "模型分析用户意图并制定执行策略。",
                "content": msg.content or "",
                "tool_calls": tool_calls,
            }
        except Exception as exc:
            logger.warning("调用远程大模型 API 失败，自动容灾回退至本地 Mock 大脑: %s", str(exc))
            return MockDecisionBrain.decide(
                messages,
                user_role=user_role,
                user_name=user_name,
                user_department=user_department,
            )

    def stream_run(
        self,
        user_prompt: str,
        session_id: Optional[str] = None,
        db: Optional[Session] = None,
        max_steps: Optional[int] = None,
        user_role: str = "ADMIN",
        user_name: str = "管理员",
        user_department: Optional[str] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """流式生成器：执行 ReAct 状态机循环并实时产出结构化事件 (供 SSE 使用)"""
        active_session_id = session_id or f"sess-{uuid.uuid4().hex[:8]}"
        trace_id = f"trace-{uuid.uuid4().hex[:8]}"
        limit_steps = max_steps or self.max_steps
        tools_schemas = get_tools_schemas()

        dept_str = user_department or "公共机房中心"
        system_content = f"{SYSTEM_PROMPT}\n\n【当前交互用户身份】：{user_name} (角色: {user_role}, 归属: {dept_str})"

        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": system_content},
        ]

        # 若属于多轮会话，加载历史上下文增强代词解析与记忆连续性
        if db is not None and session_id:
            try:
                prior_records = (
                    db.query(ChatHistory)
                    .filter(ChatHistory.session_id == active_session_id)
                    .order_by(ChatHistory.created_at.desc(), ChatHistory.id.desc())
                    .limit(10)
                    .all()
                )
                for rec in reversed(prior_records):
                    messages.append({
                        "role": rec.role,
                        "content": rec.content,
                    })
            except Exception as e:
                logger.warning("加载历史会话上下文失败: %s", str(e))

        # 持久化用户初始提问到 ChatHistory
        if db is not None:
            try:
                user_record = ChatHistory(
                    session_id=active_session_id,
                    role="user",
                    content=user_prompt,
                )
                db.add(user_record)
                db.commit()
            except Exception as e:
                db.rollback()
                logger.warning("记录用户会话历史失败: %s", str(e))

        messages.append({"role": "user", "content": user_prompt})

        step = 0
        final_content = ""
        accumulated_thought: List[str] = []

        while step < limit_steps:
            step += 1
            decision = self._call_llm(
                messages,
                tools_schemas,
                user_role=user_role,
                user_name=user_name,
                user_department=user_department,
            )

            # 1. 产生思考过程事件
            thought_text = decision.get("thought", "")
            if thought_text:
                accumulated_thought.append(thought_text)
                yield AgentEvent(type="think", data={"thought": thought_text, "step": step}).to_dict()

            tool_calls = decision.get("tool_calls", [])

            # 2. 如果决策需要调用工具 (Acting 阶段)
            if tool_calls:
                # 规范化并记录 assistant 的 tool_calls 消息
                raw_tool_calls = []
                for idx, tc in enumerate(tool_calls):
                    call_id = tc.get("id") or f"call_{step}_{idx}"
                    fn_data = tc.get("function", {})
                    fn_name = fn_data.get("name", "")
                    fn_args = fn_data.get("arguments", "{}")
                    if not isinstance(fn_args, str):
                        fn_args = json.dumps(fn_args, ensure_ascii=False)
                    raw_tool_calls.append({
                        "id": call_id,
                        "type": "function",
                        "function": {
                            "name": fn_name,
                            "arguments": fn_args,
                        },
                    })

                messages.append({
                    "role": "assistant",
                    "content": decision.get("content") or "",
                    "tool_calls": raw_tool_calls,
                })

                for idx, tc in enumerate(tool_calls):
                    call_id = raw_tool_calls[idx]["id"]
                    t_name = tc["function"]["name"]
                    raw_args = tc["function"]["arguments"]

                    try:
                        args_dict = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                    except Exception:
                        args_dict = {}

                    # 推送 tool_start 事件
                    yield AgentEvent(
                        type="tool_start",
                        data={"name": t_name, "args": args_dict, "step": step, "tool_call_id": call_id},
                    ).to_dict()

                    # 统一分发执行工具并持久化 AuditLog
                    result = execute_tool(
                        name=t_name,
                        args=args_dict,
                        db=db,
                        trace_id=trace_id,
                    )

                    # 推送 tool_end 事件
                    yield AgentEvent(
                        type="tool_end",
                        data={"name": t_name, "result": result, "step": step, "tool_call_id": call_id},
                    ).to_dict()

                    # 细粒度业务衍生事件推送 (供前端 SSE 实时联动)
                    # 1. 规章制度引用溯源事件
                    if t_name == "query_regulations":
                        content_str = ""
                        if isinstance(result, str):
                            content_str = result
                        elif isinstance(result, dict):
                            content_str = str(result.get("data", "") or result.get("message", "") or "")

                        if content_str:
                            matches = re.findall(r"\[来源:《(.*?)》(.*?)\]\s*([\s\S]*?)(?=(?:\[来源:《|$))", content_str)
                            if matches:
                                for doc_name, sec_clause, snippet in matches:
                                    yield AgentEvent(
                                        type="citation",
                                        data={
                                            "source": doc_name.strip(),
                                            "section": sec_clause.strip(),
                                            "content": snippet.strip(),
                                            "step": step,
                                        },
                                    ).to_dict()
                            elif not content_str.startswith("未找到"):
                                yield AgentEvent(
                                    type="citation",
                                    data={
                                        "source": "机房管理规章制度",
                                        "section": "",
                                        "content": content_str.strip(),
                                        "step": step,
                                    },
                                ).to_dict()

                    # 2. 工单状态突变事件 (创建或流转)
                    if t_name in ("create_ticket", "update_ticket_status") and isinstance(result, dict) and result.get("status") == "success":
                        ticket_data = result.get("ticket")
                        yield AgentEvent(
                            type="ticket_mutation",
                            data={
                                "action": "create" if t_name == "create_ticket" else "update",
                                "ticket": ticket_data,
                                "ticket_no": ticket_data.get("ticket_no") if isinstance(ticket_data, dict) else None,
                                "step": step,
                            },
                        ).to_dict()

                    # 3. 资产状态突变事件 (借还或健康变更)
                    if t_name in ("borrow_asset", "return_asset", "update_asset_health") and isinstance(result, dict) and result.get("status") in ("success", "warning"):
                        asset_data = result.get("asset")
                        yield AgentEvent(
                            type="asset_mutation",
                            data={
                                "action": t_name,
                                "asset": asset_data,
                                "asset_no": asset_data.get("asset_no") if isinstance(asset_data, dict) else None,
                                "step": step,
                            },
                        ).to_dict()

                    # 将对应工具的执行结果接入会话上下文
                    messages.append({
                        "role": "tool",
                        "name": t_name,
                        "tool_call_id": call_id,
                        "content": json.dumps(result, ensure_ascii=False, default=str),
                    })

                # 本轮工具全部执行完毕，继续进入下一轮 while 思考研判
                continue

            # 3. 如果决策直接给出回答 (Final Answer 阶段)
            content_text = decision.get("content", "")
            final_content = content_text
            yield AgentEvent(
                type="content",
                data={"text": content_text, "delta": content_text},
            ).to_dict()
            break

        # 若达到最大步数仍未结束，进行保护性截断
        if step >= limit_steps and not final_content:
            fallback = f"【系统提示】Agent 执行已达单次最大推理步数上限（max_steps={limit_steps}），已安全截断。"
            final_content = fallback
            yield AgentEvent(type="content", data={"text": fallback, "delta": fallback}).to_dict()

        # 持久化 Assistant 最终回复与推理链到 ChatHistory
        full_thought_str = "\n".join(accumulated_thought) if accumulated_thought else None
        if db is not None:
            try:
                assistant_record = ChatHistory(
                    session_id=active_session_id,
                    role="assistant",
                    content=final_content,
                    thought=full_thought_str,
                )
                db.add(assistant_record)
                db.commit()
            except Exception as e:
                db.rollback()
                logger.warning("记录 Assistant 会话历史失败: %s", str(e))

        # 产出 done 结束事件
        yield AgentEvent(
            type="done",
            data={
                "session_id": active_session_id,
                "trace_id": trace_id,
                "total_steps": step,
            },
        ).to_dict()

    def run(
        self,
        user_prompt: str,
        session_id: Optional[str] = None,
        db: Optional[Session] = None,
        max_steps: Optional[int] = None,
        user_role: str = "ADMIN",
        user_name: str = "管理员",
        user_department: Optional[str] = None,
    ) -> AgentResult:
        """同步执行入口：聚合流式事件并返回完整结果"""
        final_content = ""
        thoughts: List[str] = []
        tool_calls: List[Dict[str, Any]] = []
        active_session_id = session_id or ""
        trace_id = ""
        steps = 0

        for event in self.stream_run(
            user_prompt=user_prompt,
            session_id=session_id,
            db=db,
            max_steps=max_steps,
            user_role=user_role,
            user_name=user_name,
            user_department=user_department,
        ):
            e_type = event.get("type")
            if e_type == "think":
                thoughts.append(event.get("thought", ""))
            elif e_type == "tool_start":
                tool_calls.append({"name": event.get("name"), "args": event.get("args")})
            elif e_type == "content":
                final_content = event.get("text", "")
            elif e_type == "done":
                active_session_id = event.get("session_id", active_session_id)
                trace_id = event.get("trace_id", "")
                steps = event.get("total_steps", steps)

        return AgentResult(
            session_id=active_session_id,
            trace_id=trace_id,
            content=final_content,
            thought="\n".join(thoughts),
            steps=steps,
            tool_calls=tool_calls,
        )

"""针对 Mock 确定性规则大脑的 RBAC 角色权限与防越权拦截自动化测试套件"""

import pytest
from app.agent.react_engine import ReActEngine


def test_student_permission_inquiry_returns_guide():
    """测试学生咨询权限与操作指引时，返回专属权限清单和合法 Prompt"""
    engine = ReActEngine()
    events = list(
        engine.stream_run(
            user_prompt="我是学生，我能做什么？有什么推荐的提示词？",
            user_role="STUDENT",
            user_name="李同学",
            user_department="计算机系2023级",
        )
    )
    content_events = [e for e in events if e.get("type") == "content"]
    assert len(content_events) > 0
    reply = content_events[0].get("text", "")
    assert "【学生身份权限与操作指引】" in reply
    assert "李同学" in reply
    assert "机房感知监控" in reply
    assert "故障报修提单" in reply
    assert "禁止直接办理设备借调出库登记" in reply
    assert "推荐您可以直接发送的提示词" in reply


def test_student_borrow_intercepted():
    """测试学生尝试申请借调服务器时被严正拦截"""
    engine = ReActEngine()
    events = list(
        engine.stream_run(
            user_prompt="我想借用服务器 DEV-SRV-202 做实验",
            user_role="STUDENT",
            user_name="张小凡",
            user_department="自动化学院",
        )
    )
    content_events = [e for e in events if e.get("type") == "content"]
    assert len(content_events) > 0
    reply = content_events[0].get("text", "")
    assert "【权限拦截警报】借调申请已被系统拦截！" in reply
    assert "张小凡" in reply
    assert "学生 STUDENT" in reply
    assert "权限边界：" in reply
    assert "指导教师办理" in reply


def test_student_device_admin_action_intercepted():
    """测试学生尝试删除设备或添加设备时被严正拦截"""
    engine = ReActEngine()
    events = list(
        engine.stream_run(
            user_prompt="帮我删除设备 DEV-SRV-201，注销掉这台机器",
            user_role="STUDENT",
            user_name="王同学",
            user_department="软件学院",
        )
    )
    content_events = [e for e in events if e.get("type") == "content"]
    assert len(content_events) > 0
    reply = content_events[0].get("text", "")
    assert "【权限拦截警报】设备资产管理与底层控制操作已被系统拦截！" in reply
    assert "王同学" in reply
    assert "物理资产底账" in reply
    assert "专职主管办理" in reply


def test_student_ticket_update_intercepted():
    """测试学生尝试办结或更新工单时被严正拦截"""
    engine = ReActEngine()
    events = list(
        engine.stream_run(
            user_prompt="把工单 TK-20260901-001 标记为已解决并办结",
            user_role="STUDENT",
            user_name="赵同学",
            user_department="网安学院",
        )
    )
    content_events = [e for e in events if e.get("type") == "content"]
    assert len(content_events) > 0
    reply = content_events[0].get("text", "")
    assert "【权限拦截警报】工单流转操作已被系统拦截！" in reply
    assert "赵同学" in reply
    assert "只读查看权限" in reply


def test_student_health_update_intercepted():
    """测试学生尝试修改设备健康度时被严正拦截"""
    engine = ReActEngine()
    events = list(
        engine.stream_run(
            user_prompt="把设备 DEV-SRV-201 的健康状态改成良好",
            user_role="STUDENT",
            user_name="钱同学",
            user_department="人工智能学院",
        )
    )
    content_events = [e for e in events if e.get("type") == "content"]
    assert len(content_events) > 0
    reply = content_events[0].get("text", "")
    assert "【权限拦截警报】设备健康状态变更已被系统拦截！" in reply
    assert "钱同学" in reply
    assert "专职主管专管权限" in reply


def test_teacher_ticket_close_intercepted():
    """测试教师尝试直接办结关闭工单时被拦截"""
    engine = ReActEngine()
    events = list(
        engine.stream_run(
            user_prompt="请直接办结工单 TK-20260901-001 并归档",
            user_role="TEACHER",
            user_name="孙老师",
            user_department="计算机科学教研室",
        )
    )
    content_events = [e for e in events if e.get("type") == "content"]
    assert len(content_events) > 0
    reply = content_events[0].get("text", "")
    assert "【权限拦截警报】工单办结/归档操作已被系统拦截！" in reply
    assert "孙老师" in reply
    assert "教师 TEACHER" in reply
    assert "验收核验闭环" in reply


def test_student_urge_intercepted():
    """测试学生尝试向教师发起催还通知时被严正拦截"""
    engine = ReActEngine()
    events = list(
        engine.stream_run(
            user_prompt="催还李老师 DEV-SRV-201，下发催办通知",
            user_role="STUDENT",
            user_name="周同学",
            user_department="软件工程2023级",
        )
    )
    content_events = [e for e in events if e.get("type") == "content"]
    assert len(content_events) > 0
    reply = content_events[0].get("text", "")
    assert "【权限拦截警报】超期催办操作已被系统拦截！" in reply
    assert "周同学" in reply
    assert "学生 STUDENT" in reply
    assert "机房专职主管专属职权" in reply

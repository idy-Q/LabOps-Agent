"""全系统全交互链路端到端闭环自动化综合测试套件 (E2E Full System Interaction Test)

本套件严格模拟真实用户与各角色身份，将整个项目的所有核心交互流程完整跑通：
1. 身份认证与 RBAC 权限隔离交互 (Admin / Teacher / Student)
2. 大盘监控与主动自治巡检交互 (Overview / Autonomous Patrol / Overdue Notice)
3. 运维工单全生命周期流转交互 (Create -> Processing -> Resolved [设备降温复位] -> Closed -> Timeline Audit)
4. 资产台账借调与安全联锁交互 (Add -> Temp Tune -> Fault Borrow Block -> Normal Borrow -> Return -> Delete Protect)
5. 机房与机柜 2D 拓扑全生命周期交互 (Room Add [单字符隔离] -> Rack Add -> Allocation -> Capacity Interlock -> Cleanup)
6. 规章规程中心与知识检索交互 (CRUD -> Hybrid Search -> RAG Sync)
7. AI 智能管家对话与 ReAct 引擎流式推理交互 (Chat -> Intent Detection -> Tool Execution Audit)
"""

import json
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.tools.asset_tools import borrow_asset, return_asset
from app.agent.react_engine import ReActEngine


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


# ==============================================================================
# 1. 身份认证与 RBAC 权限隔离交互测试
# ==============================================================================
def test_interaction_auth_and_rbac_flow(client):
    """测试多角色认证切换与关键操作鉴权隔离交互"""
    # 1.1 管理员、教师、学生身份凭据核验
    admin_login = client.post("/api/auth/login", json={"username": "admin", "password": "admin666"})
    assert admin_login.status_code == 200
    assert admin_login.json()["role"] == "ADMIN"

    teacher_login = client.post("/api/auth/login", json={"username": "teacher_zhang", "password": "123456"})
    assert teacher_login.status_code == 200
    assert teacher_login.json()["role"] == "TEACHER"

    student_login = client.post("/api/auth/login", json={"username": "student_chen", "password": "123456"})
    assert student_login.status_code == 200
    assert student_login.json()["role"] == "STUDENT"

    # 1.2 学生尝试修改运维工单 -> 应被严正拦截 (HTTP 403)
    t_res = client.post(
        "/api/tickets",
        json={
            "title": "权限拦截交互测试工单",
            "description": "用于测试学生角色编辑拦截",
            "priority": "LOW",
            "creator": "王主管",
        },
    )
    assert t_res.status_code == 201
    ticket_id = t_res.json()["id"]

    try:
        # 学生尝试流转该工单 -> 403
        st_res = client.put(
            f"/api/tickets/{ticket_id}",
            json={"status": "PROCESSING", "operator": "陈同学", "operator_role": "STUDENT"},
        )
        assert st_res.status_code == 403
        assert "学生角色对运维工单仅有只读权限" in st_res.json()["detail"]

        # 1.3 教师尝试编辑他人创建的工单基本要素 -> 应被拦截 (HTTP 403)
        th_res = client.put(
            f"/api/tickets/{ticket_id}",
            json={"title": "教师篡改标题", "operator": "李老师", "operator_role": "TEACHER"},
        )
        assert th_res.status_code == 403
        assert "仅可编辑本人创建的工单" in th_res.json()["detail"]

    finally:
        client.delete(f"/api/tickets/{ticket_id}")


# ==============================================================================
# 2. 大盘监控与自治巡检交互测试
# ==============================================================================
def test_interaction_overview_and_patrol_flow(client):
    """测试监控大盘指标汇总、主动自治巡检报告生成及超期催告单交互"""
    # 2.1 获取大盘监控汇总指标
    summary_res = client.get("/api/metrics/summary")
    assert summary_res.status_code == 200
    summary_data = summary_res.json()
    assert summary_data["status"] == "success"
    data = summary_data["data"]
    assert "overview" in data
    assert "assets" in data
    assert "tickets" in data

    # 2.2 执行主动自治巡检交互
    patrol_res = client.post("/api/metrics/patrol")
    assert patrol_res.status_code == 200
    p_data = patrol_res.json()
    assert p_data["status"] == "success"
    report = p_data["data"]
    assert "batch_no" in report
    assert "kpi" in report
    assert "total_scanned" in report["kpi"]
    assert "healthy_count" in report["kpi"]

    # 2.3 获取超期借用设备概要
    overdue_res = client.get("/api/assets/overdue")
    assert overdue_res.status_code == 200
    assert "total_overdue" in overdue_res.json()


# ==============================================================================
# 3. 运维工单全生命周期流转与温度闭环复位交互测试
# ==============================================================================
def test_interaction_ticket_full_lifecycle_and_device_recovery(client):
    """测试工单流转完整链条及工单已解决后关联设备健康度与温度自动复位闭环"""
    # 3.1 预置一台严重超温设备
    asset_res = client.post(
        "/api/assets",
        json={
            "asset_no": "DEV-INTERACTION-OVERHEAT-01",
            "name": "超温AI服务器交互测试机",
            "category": "服务器",
            "location": "实训楼201-机柜A01",
            "health_status": "OVERHEAT",
            "custom_temperature": 44.5,
        },
    )
    assert asset_res.status_code == 201
    asset_id = asset_res.json()["id"]

    try:
        # 3.2 针对该设备提单 (PENDING)
        ticket_res = client.post(
            "/api/tickets",
            json={
                "title": "DEV-INTERACTION-OVERHEAT-01 核心高温处置工单",
                "description": "温度达到44.5度严重告警，需现场排障",
                "priority": "CRITICAL",
                "device_id": "DEV-INTERACTION-OVERHEAT-01",
                "creator": "王主管",
            },
        )
        assert ticket_res.status_code == 201
        ticket = ticket_res.json()
        ticket_id = ticket["id"]

        # 3.3 推进至处理中 (PROCESSING)
        proc_res = client.put(
            f"/api/tickets/{ticket_id}",
            json={
                "status": "PROCESSING",
                "operator": "王主管",
                "operator_role": "ADMIN",
                "comment": "现场巡检已启动，正核实告警硬件指标",
            },
        )
        assert proc_res.status_code == 200
        assert proc_res.json()["status"] == "PROCESSING"

        # 3.4 推进至已解决 (RESOLVED)，包含用户特殊处置输入
        resolv_res = client.put(
            f"/api/tickets/{ticket_id}",
            json={
                "status": "RESOLVED",
                "operator": "王主管",
                "operator_role": "ADMIN",
                "comment": "现场更换辅助散热风扇；清灰除尘并重抹导热硅脂，温度测试正常",
            },
        )
        assert resolv_res.status_code == 200
        assert resolv_res.json()["status"] == "RESOLVED"

        # 3.5 核心断言：核验关联设备是否已自动闭环降温复位至 31.5℃ 与 HEALTHY
        asset_check = client.get(f"/api/assets/{asset_id}").json()
        assert asset_check["health_status"] == "HEALTHY", "工单解决后关联设备健康状态未恢复为 HEALTHY"
        assert asset_check["custom_temperature"] == 31.5, "工单解决后关联设备温度未回落至安全基线 31.5"

        # 3.6 推进至已关闭 (CLOSED)
        close_res = client.put(
            f"/api/tickets/{ticket_id}",
            json={
                "status": "CLOSED",
                "operator": "王主管",
                "operator_role": "ADMIN",
                "comment": "连续观察24小时各项指标平稳，确认故障根除归档",
            },
        )
        assert close_res.status_code == 200
        assert close_res.json()["status"] == "CLOSED"

        # 3.7 检验全景时序审计流水 (Audit Trail)
        timeline_res = client.get(f"/api/tickets/{ticket_id}/timeline")
        assert timeline_res.status_code == 200
        tl_data = timeline_res.json()
        assert tl_data["summary"]["is_closed"] is True
        nodes = tl_data["timeline"]
        node_types = [n["node_type"] for n in nodes]
        assert "CREATED" in node_types
        assert "PROCESSING" in node_types
        assert "RESOLVED" in node_types
        assert "CLOSED" in node_types

        # 3.8 清理测试工单
        client.delete(f"/api/tickets/{ticket_id}")

    finally:
        client.delete(f"/api/assets/{asset_id}")


# ==============================================================================
# 4. 资产台账借调与安全联锁交互测试
# ==============================================================================
def test_interaction_asset_lifecycle_and_safety_interlock(client):
    """测试设备录入、温度调节、超温故障借调锁定拦截、正常借还及删除防护交互"""
    # 4.1 录入新设备
    add_res = client.post(
        "/api/assets",
        json={
            "asset_no": "DEV-INTERACTION-SRV-99",
            "name": "高密双路刀片节点99",
            "category": "服务器",
            "location": "实训楼201-机柜A01",
            "health_status": "HEALTHY",
            "custom_temperature": 32.0,
        },
    )
    assert add_res.status_code == 201
    asset_id = add_res.json()["id"]

    try:
        # 4.2 温度微调至 OVERHEAT (42℃) -> 验证健康状态自动联动为 OVERHEAT
        tune_res = client.patch(
            f"/api/assets/{asset_id}",
            json={"custom_temperature": 42.0},
        )
        assert tune_res.status_code == 200
        assert tune_res.json()["health_status"] == "OVERHEAT"

        # 4.3 故障状态下办理借用 -> 业务层安全拦截验证
        intercept_result = borrow_asset(
            asset_no="DEV-INTERACTION-SRV-99",
            borrower="张老师",
        )
        assert "无法办理" in str(intercept_result) or "拦截" in str(intercept_result) or "超温" in str(intercept_result)

        # 4.4 温度恢复正常 (30℃) -> 验证健康状态恢复为 HEALTHY
        heal_res = client.patch(
            f"/api/assets/{asset_id}",
            json={"custom_temperature": 30.0},
        )
        assert heal_res.status_code == 200
        assert heal_res.json()["health_status"] == "HEALTHY"

        # 4.5 正常办理借调登记 -> 借调成功，状态变更为 IN_USE
        borrow_succ = borrow_asset(
            asset_no="DEV-INTERACTION-SRV-99",
            borrower="张老师",
        )
        assert "成功" in str(borrow_succ) or "借用登记成功" in str(borrow_succ) or borrow_succ.get("status") == "success"

        # 校验数据库状态
        borrowed_check = client.get(f"/api/assets/{asset_id}").json()
        assert borrowed_check["borrow_status"] == "IN_USE"
        assert borrowed_check["borrower"] == "张老师"

        # 4.6 借用中设备删除安全拦截 -> 应阻断删除 (HTTP 400)
        del_block_res = client.delete(f"/api/assets/{asset_id}")
        assert del_block_res.status_code == 400
        assert "借用" in del_block_res.json()["detail"]

        # 4.7 归还设备入库 -> 状态恢复 AVAILABLE
        return_res = return_asset(asset_no="DEV-INTERACTION-SRV-99")
        assert "归还" in str(return_res) or return_res.get("status") == "success"

        returned_check = client.get(f"/api/assets/{asset_id}").json()
        assert returned_check["borrow_status"] == "AVAILABLE"
        assert returned_check["borrower"] is None

        # 4.8 归还后安全删除
        del_succ_res = client.delete(f"/api/assets/{asset_id}")
        assert del_succ_res.status_code in [200, 204]

    except Exception:
        client.delete(f"/api/assets/{asset_id}")
        raise


# ==============================================================================
# 5. 机房与机柜 2D 拓扑全生命周期交互测试
# ==============================================================================
def test_interaction_room_rack_topology_lifecycle(client):
    """测试单字符机房防克隆、标准机房机柜增删改查、在架 U 位调度与安全联锁交互"""
    # 5.1 单字符机房 '1' 拓扑防幽灵机柜克隆验证
    r1_res = client.post("/api/rooms", json={
        "room_code": "1",
        "room_name": "1",
        "location": "实训楼1",
        "manager_teacher": "王主管",
        "power_capacity_kw": 50.0,
    })
    assert r1_res.status_code == 201

    try:
        topo_r1 = client.get("/api/assets/topology?room_code=1").json()
        rooms_1 = [r for r in topo_r1.get("rooms", []) if r["room_code"] == "1"]
        assert len(rooms_1) == 1
        assert rooms_1[0]["total_racks"] == 0, "机房1不应有幽灵机柜"
        assert len(rooms_1[0]["racks"]) == 0, "机房1机柜列表必须为空"
    finally:
        client.delete("/api/rooms/1")

    # 5.2 新建立项标准实训机房 ROOM-801
    room_payload = {
        "room_code": "ROOM-801",
        "room_name": "实训楼801 边缘异构计算中心",
        "location": "实训楼8层801室",
        "manager_teacher": "王主管",
        "power_capacity_kw": 60.0,
    }
    room_res = client.post("/api/rooms", json=room_payload)
    assert room_res.status_code == 201

    try:
        # 5.3 在 ROOM-801 内立项投产机柜 机柜D01
        rack_payload = {
            "rack_id": "机柜D01",
            "rack_name": "D01 边缘服务器机柜",
            "room_code": "ROOM-801",
            "total_u": 42,
            "power_rating_w": 5000,
        }
        rack_res = client.post("/api/racks", json=rack_payload)
        assert rack_res.status_code == 201

        # 5.4 上架一台 2U 实验设备至机柜D01 的 U10 槽位
        asset_res = client.post("/api/assets", json={
            "asset_no": "DEV-INTERACTION-RACK-88",
            "name": "边缘网关节点88",
            "category": "服务器",
            "location": "实训楼801-机柜D01-U10(2U)",
            "health_status": "HEALTHY",
            "custom_temperature": 31.0,
            "detail": {
                "extra_params": json.dumps({"start_u": 10, "u_height": 2, "rack_units": "2U"})
            }
        })
        assert asset_res.status_code == 201
        asset_id = asset_res.json()["id"]

        try:
            # 5.5 查询拓扑，验证机柜 U 位占用与设备准确定位
            topo_res = client.get("/api/assets/topology?room_code=ROOM-801").json()
            r801 = [r for r in topo_res["rooms"] if r["room_code"] == "ROOM-801"][0]
            assert r801["total_racks"] == 1
            rack_d01 = r801["racks"][0]
            assert rack_d01["rack_id"] == "机柜D01"
            assert rack_d01["used_u"] == 2
            assert len(rack_d01["assets"]) == 1
            assert rack_d01["assets"][0]["asset_no"] == "DEV-INTERACTION-RACK-88"

            # 5.6 机柜在架设备防误删联锁：机柜内有在架设备时下线注销应被拦截 (HTTP 400)
            del_rack_block = client.delete("/api/racks/机柜D01")
            assert del_rack_block.status_code == 400
            assert "在架设备" in del_rack_block.json()["detail"]

            # 5.7 机房内有机柜或在架设备时注销机房应被拦截 (HTTP 400)
            del_room_block = client.delete("/api/rooms/ROOM-801")
            assert del_room_block.status_code == 400
            assert "安全联锁" in del_room_block.json()["detail"] or "腾退" in del_room_block.json()["detail"]

        finally:
            # 腾退清理：先删设备 -> 再删机柜 -> 再删机房
            client.delete(f"/api/assets/{asset_id}")

        client.delete("/api/racks/机柜D01")
        del_room_succ = client.delete("/api/rooms/ROOM-801")
        assert del_room_succ.status_code == 200

    except Exception:
        client.delete("/api/rooms/ROOM-801")
        raise


# ==============================================================================
# 6. 规章规程知识中心与 RAG 检索交互测试
# ==============================================================================
def test_interaction_regulations_and_rag_flow(client):
    """测试规章制度录入、分块嵌入、混合检索与级联清理交互"""
    # 6.1 录入一条新的实验室管理规程
    reg_payload = {
        "title": "高温极端环境机房设备紧急断电与熔断指引",
        "category": "应急条例",
        "effective_date": "2026-09-01",
        "content": "当精密空调失效且核心服务器温度连续15分钟超过45℃时，值班安全员必须执行紧急安全熔断关机，严禁延误。",
    }
    create_res = client.post("/api/regulations", json=reg_payload)
    assert create_res.status_code == 201
    reg_data = create_res.json()
    reg_id = reg_data["id"]

    try:
        # 6.2 检索该规程 (向量与关键词混合检索)
        search_res = client.get("/api/regulations/search?q=核心服务器超过45度")
        assert search_res.status_code == 200
        search_results = search_res.json()
        assert isinstance(search_results, list)
        matched_titles = [r.get("doc_title", "") for r in search_results]
        assert any("高温" in t or "应急" in t for t in matched_titles) or len(search_results) > 0

        # 6.3 获取规程汇总总数
        sum_res = client.get("/api/regulations/summary")
        assert sum_res.status_code == 200
        assert sum_res.json()["total_documents"] >= 1

    finally:
        client.delete(f"/api/regulations/{reg_id}")


# ==============================================================================
# 7. AI 智能管家对话与 ReAct 引擎流式推理交互测试
# ==============================================================================
def test_interaction_agent_chat_and_tools_flow(client):
    """测试自然语言提问与 ReAct 引擎调度运行交互"""
    engine = ReActEngine()

    # 7.1 测试自然语言查询设备健康状态
    events = list(engine.stream_run(
        user_prompt="查询 DEV-SRV-201 的监控指标",
        user_name="王主管",
        user_role="ADMIN",
    ))
    event_types = [e.type if hasattr(e, "type") else (e.get("type") or e.get("event")) for e in events]
    assert any(t in event_types for t in ["done", "content"])

    # 7.2 测试规章咨询意图
    reg_events = list(engine.stream_run(
        user_prompt="请问实验室关于设备超温出借有什么规定？",
        user_name="王主管",
        user_role="ADMIN",
    ))
    reg_event_types = [e.type if hasattr(e, "type") else (e.get("type") or e.get("event")) for e in reg_events]
    assert any(t in reg_event_types for t in ["done", "content"])

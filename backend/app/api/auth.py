"""系统用户认证与角色授权 API 路由"""

import re
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import User, hash_password, verify_password
from app.schemas.user import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    DemoUserResponse,
    UserProfileResponse,
    UserProfileUpdateRequest,
    ChangePasswordRequest,
)

router = APIRouter()

# 管理员与教师专属安全激活口令 (高校实验室安全分级防护体系)
TEACHER_ACTIVATION_CODE = "teacher666"
ADMIN_ACTIVATION_CODE = "admin666"

# 4 位系统典型预置用户展示卡片清单 (供登录 Tab 快速一键填入凭据或秒级切换)
DEMO_USERS_LIST = [
    DemoUserResponse(
        username="admin",
        real_name="王主管",
        role="ADMIN",
        role_label="超级管理员",
        department="网络中心运维部",
        phone="13800000001",
        default_password="admin666",
    ),
    DemoUserResponse(
        username="teacher_li",
        real_name="李老师",
        role="TEACHER",
        role_label="专业课教师",
        department="物联网工程教研室",
        phone="13900000002",
        default_password="123456",
    ),
    DemoUserResponse(
        username="teacher_zhang",
        real_name="张老师",
        role="TEACHER",
        role_label="实训指导教师",
        department="网络安全教研室",
        phone="13900000003",
        default_password="123456",
    ),
    DemoUserResponse(
        username="student_chen",
        real_name="陈同学",
        role="STUDENT",
        role_label="实训在读学生",
        department="计科2201班",
        phone="13700000004",
        default_password="123456",
    ),
]


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="新用户注册",
    description="支持学生（免密）、教师（需专属激活口令 teacher666）和管理员（需专属激活口令 admin666）注册。",
)
def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    # 1. 唯一性查重：工号/学号不可重复注册 (大小写不敏感防碰撞)
    existing_user = (
        db.query(User)
        .filter(func.lower(User.username) == request.username.lower())
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"工号/学号 [{request.username}] 已经存在，请直接登录或使用其他工号",
        )

    # 2. 权限提权防护与身份安全激活口令校验
    if request.role == "ADMIN":
        code = request.admin_code or request.activation_code
        if not code or code != ADMIN_ACTIVATION_CODE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="管理员专属安全激活口令错误或未提供，无法注册超级管理员角色",
            )
    elif request.role == "TEACHER":
        code = request.teacher_code or request.activation_code
        if not code or code != TEACHER_ACTIVATION_CODE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="教师专属安全激活口令错误或未提供，无法注册高校专业教师角色",
            )
    # 学生 (STUDENT): 最低权限，免密直接放行

    # 3. 生成加盐 SHA-256 哈希并落盘
    pwd_hash = hash_password(request.password)
    norm_phone = request.phone.strip() if request.phone and request.phone.strip() else None
    user = User(
        username=request.username,
        password_hash=pwd_hash,
        real_name=request.real_name,
        role=request.role,
        department=request.department,
        phone=norm_phone,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post(
    "/login",
    response_model=UserResponse,
    summary="用户登录认证",
    description="校验工号与密码哈希，通过后返回用户详细信息。",
)
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(func.lower(User.username) == request.username.lower())
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="工号/学号不存在或登录密码错误",
        )

    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="工号/学号不存在或登录密码错误",
        )

    return user


@router.get(
    "/demo-users",
    response_model=List[DemoUserResponse],
    summary="获取典型演示用户展示列表",
    description="返回预置的 4 位典型角色用户列表，供前端登录弹窗快捷选择填入。",
)
def get_demo_users():
    return DEMO_USERS_LIST


def build_user_profile(user: User) -> UserProfileResponse:
    """构建注册用户的标准化全景档案"""
    role = (user.role or "TEACHER").upper()
    if role == "ADMIN":
        role_label = "超级管理员"
        responsibilities = [
            "机房物理资产全生命周期审计与出入库核准",
            "工单多级流转最终办结与归档权",
            "自动化运维策略调优与高危操作一票否决权",
            "全网设备拓扑与实时监控巡检权限",
        ]
        description = f"系统最高管理权限拥有者，负责{user.department}与高校实验实训机房中枢运营保障。"
    elif role == "TEACHER":
        role_label = "专业课指导教师"
        responsibilities = [
            "教学实训设备借调预约与工单提报",
            "实验机房日常教学设备工况验收与反馈",
            "实训现场软硬件故障报修与流程跟进",
        ]
        description = f"专业课教师，负责{user.department}的课程实训教学与教学机房设备规范使用。"
    elif role == "STUDENT":
        role_label = "实训在读学生"
        responsibilities = [
            "实训工位设备规范使用与异常报修",
            "工单处理进度与设备履历查阅",
        ]
        description = f"在读学生，所属{user.department}，参与实验实训课程学习。"
    else:
        role_label = "现场运维人员"
        responsibilities = [
            "机房现场运维与设备流转协同",
            "基础巡检与工单现场执行",
        ]
        description = f"运维人员，所属{user.department}。"

    created_str = user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else "系统初始化"
    avatar_text = user.real_name[:1] if user.real_name else user.username[:1].upper()

    return UserProfileResponse(
        username=user.username,
        real_name=user.real_name,
        role=user.role,
        role_label=role_label,
        department=user.department or "实验室运维中心",
        phone=user.phone or "暂未登记",
        status="ONLINE",
        is_system_agent=False,
        avatar_text=avatar_text,
        responsibilities=responsibilities,
        description=description,
        created_at=created_str,
    )


def build_system_agent_profile(query_name: str) -> UserProfileResponse:
    """构建 LabOps-Agent 智能自治运维管家专属数字智能体档案"""
    return UserProfileResponse(
        username="LabOps-Agent",
        real_name="LabOps-Agent 智能自治运维管家",
        role="SYSTEM_AGENT",
        role_label="AI 智能自治运维管家",
        department="LabOps 智能机房中枢 / 自治调度算法引擎",
        phone="7×24H 内部总线",
        status="7×24H 实时在线",
        is_system_agent=True,
        avatar_text="AI",
        responsibilities=[
            "全网网络设备与服务器心跳的主动探针采样与阈值研判",
            "基于 ReAct 思考-行动循环的故障定位与工单自主生成",
            "融合知识库标准作业规程 (SOP) 的智能化自治排障",
            "工单全景时序变迁记录与审计溯源防抵赖存证",
        ],
        description="高校数据中心机房 AI 自治运维大脑，具备 LangChain / ReAct 循环调度机制与 RAG 知识库检索能力，全天候守护机房网络设备与服务器工况。",
        created_at="系统初始化上线",
    )


def build_fallback_profile(identifier: str) -> UserProfileResponse:
    """未收录主体的合规保底档案（确保 HTTP 200，绝不崩溃抛出 500）"""
    clean_name = identifier.strip() or "临时运维人员"
    return UserProfileResponse(
        username=clean_name,
        real_name=clean_name,
        role="OPERATOR",
        role_label="现场运维人员",
        department="高校实验实训保障组",
        phone="暂无登记",
        status="离线/临时流转",
        is_system_agent=False,
        avatar_text=clean_name[:1] if clean_name else "运",
        responsibilities=[
            "负责机房指定设备的现场巡检与流转操作",
            "配合管理员完成应急抢修与状态复核",
            "工单协同处置与现场记录同步",
        ],
        description=f"流转记录中的操作人员 [{clean_name}]，已通过系统审计留痕记入工单时间轴。",
        created_at="临时协同",
    )


@router.get(
    "/profile/{identifier}",
    response_model=UserProfileResponse,
    summary="查询人员或系统主体档案详情",
    description="支持通过工号/学号 (username)、真实姓名 (real_name) 或主体标识 (LabOps-Agent、系统监控等) 查询档案详情。",
)
def get_user_profile(identifier: str, db: Session = Depends(get_db)):
    raw_id = (identifier or "").strip()
    if not raw_id:
        return build_fallback_profile("未知主体")

    # 1. 优先从 User 表检索 (支持精确匹配、大小写不敏感匹配、剥离UI图标/箭头及角色括号)
    # 剥离可能携带的前置/后置 UI 装饰图标与方向符号 (如 "👤 王主管 ↗" -> "王主管")
    base_id = re.sub(r"^[\s👤🤖⚙️🔧\-\|\/]+|[\s↗→\-\|\/]+$", "", raw_id).strip()

    # 剥离成对的角色后缀括号 (如 "王主管 (超级管理员)" -> "王主管")
    clean_id = re.sub(r"[\(\[\（\【].*?[\)\]\）\】]", "", base_id).strip()

    # 兼容未闭合单边括号容错 (如 "王主管(管理员" -> "王主管")
    split_id = re.split(r"[\(\[\（\【]", base_id)[0].strip()

    candidate_names = []
    for cand in [raw_id, base_id, clean_id, split_id]:
        cand = cand.strip()
        if cand and cand not in candidate_names:
            candidate_names.append(cand)

    user = None
    for name in candidate_names:
        user = (
            db.query(User)
            .filter(
                or_(
                    func.lower(User.username) == name.lower(),
                    User.real_name == name,
                    func.lower(User.real_name) == name.lower(),
                )
            )
            .first()
        )
        if user:
            break

    if user:
        return build_user_profile(user)

    # 2. 检查是否属于系统内置虚拟主体、AI 智能体或自动化监控探针
    system_agent_keys = {
        "labops-agent", "labops_agent", "labopsagent", "agent",
        "系统监控", "系统监控巡检", "系统", "system",
        "全网一键自治巡检", "自治巡检", "自主巡检", "全网自治巡检",
        "系统管理员", "管理员",
    }
    norm_id = raw_id.lower().replace(" ", "").replace("-", "").replace("_", "")
    norm_clean = clean_id.lower().replace(" ", "").replace("-", "").replace("_", "") if clean_id else norm_id

    if (
        norm_id in system_agent_keys
        or norm_clean in system_agent_keys
        or "agent" in norm_id
        or "系统" in raw_id
        or "巡检" in raw_id
        or "监控" in raw_id
    ):
        return build_system_agent_profile(raw_id)

    # 3. 未收录主体优雅降级保底 (确保返回 HTTP 200，绝不崩溃抛出 500)
    return build_fallback_profile(raw_id)


@router.put(
    "/profile/{username}",
    response_model=UserProfileResponse,
    summary="更新用户个人资料",
    description="更新指定工号/学号用户的真实姓名、联系电话与所属部门，并返回最新全景档案。",
)
def update_user_profile(
    username: str,
    request: UserProfileUpdateRequest,
    db: Session = Depends(get_db),
):
    clean_username = username.strip()
    user = (
        db.query(User)
        .filter(func.lower(User.username) == clean_username.lower())
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工号/学号 [{clean_username}] 不存在，无法更新个人资料",
        )

    if request.real_name is not None:
        user.real_name = request.real_name.strip()
    if request.phone is not None:
        user.phone = request.phone.strip() if request.phone.strip() else None
    if request.department is not None:
        user.department = request.department.strip()

    db.commit()
    db.refresh(user)
    return build_user_profile(user)


@router.put(
    "/change-password",
    summary="用户自主修改密码",
    description="校验工号与原密码后，更新密码加盐哈希为新密码。",
)
def change_password(
    request: ChangePasswordRequest,
    db: Session = Depends(get_db),
):
    clean_username = request.username.strip()
    user = (
        db.query(User)
        .filter(func.lower(User.username) == clean_username.lower())
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工号/学号 [{clean_username}] 不存在",
        )

    if not verify_password(request.old_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码校验不通过，密码修改失败",
        )

    user.password_hash = hash_password(request.new_password)
    db.commit()
    return {"message": "密码修改成功", "username": user.username}



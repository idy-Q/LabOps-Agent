"""系统用户认证与角色授权 API 路由"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import User, hash_password, verify_password
from app.schemas.user import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    DemoUserResponse,
)

router = APIRouter()

# 管理员专属安全激活口令 (严格遵从 2026-09 最新安全要求与用户反馈：admin666)
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
    description="支持教师、学生和管理员注册。申请 ADMIN 角色必须提供专属安全激活口令 (admin666)。",
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

    # 2. 权限提权防护：若申请超级管理员角色，必须验证专属口令
    if request.role == "ADMIN":
        if not request.admin_code or request.admin_code != ADMIN_ACTIVATION_CODE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="管理员专属安全激活口令错误或未提供，无法注册超级管理员角色",
            )

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

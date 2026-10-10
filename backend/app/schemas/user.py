"""系统用户认证与权限数据模式 (Pydantic Schemas)"""

from datetime import datetime
from typing import Optional, Literal, List
from pydantic import BaseModel, ConfigDict, Field

UserRoleType = Literal["ADMIN", "TEACHER", "STUDENT"]


class UserRegisterRequest(BaseModel):
    """用户注册请求数据模式"""

    username: str = Field(..., min_length=2, max_length=64, description="登录工号/学号")
    password: str = Field(..., min_length=6, max_length=64, description="登录密码 (至少6位)")
    real_name: str = Field(..., min_length=1, max_length=64, description="真实姓名，如 王主管/李老师")
    role: UserRoleType = Field(default="STUDENT", description="申请角色: STUDENT (学生), TEACHER (教师), ADMIN (管理员)")
    department: str = Field(..., min_length=1, max_length=128, description="所属教研室/班级/部门")
    phone: Optional[str] = Field(default=None, max_length=32, description="联系电话")
    teacher_code: Optional[str] = Field(default=None, description="教师专属安全激活口令 (申请 TEACHER 角色时必填)")
    admin_code: Optional[str] = Field(default=None, description="管理员专属安全激活口令 (申请 ADMIN 角色时必填)")
    activation_code: Optional[str] = Field(default=None, description="通用安全激活口令 (兼容传递)")

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class UserLoginRequest(BaseModel):
    """用户登录请求数据模式"""

    username: str = Field(..., min_length=1, max_length=64, description="登录工号/学号")
    password: str = Field(..., min_length=1, max_length=64, description="登录密码")

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class UserResponse(BaseModel):
    """用户基本信息响应数据模式"""

    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="登录工号/学号")
    real_name: str = Field(..., description="真实姓名")
    role: str = Field(..., description="角色类型")
    department: str = Field(..., description="所属教研室/班级/部门")
    phone: Optional[str] = Field(default=None, description="联系电话")
    created_at: Optional[datetime] = Field(default=None, description="注册时间")

    model_config = ConfigDict(from_attributes=True)


class DemoUserResponse(BaseModel):
    """系统典型预置演示用户数据模式"""

    username: str = Field(..., description="登录工号/学号")
    real_name: str = Field(..., description="真实姓名")
    role: str = Field(..., description="角色标识 (ADMIN/TEACHER/STUDENT)")
    role_label: str = Field(..., description="角色展示标签 (如 超级管理员/专业课教师)")
    department: str = Field(..., description="所属教研室/班级/部门")
    phone: Optional[str] = Field(default=None, description="联系电话")
    default_password: str = Field(..., description="典型演示密码 (供快捷填入测试)")


class UserProfileResponse(BaseModel):
    """用户或系统主体人物详情档案数据模式"""

    username: str = Field(..., description="工号/学号或主体唯一识别号")
    real_name: str = Field(..., description="真实姓名或主体全称")
    role: str = Field(..., description="角色标识 (ADMIN/TEACHER/STUDENT/SYSTEM_AGENT/OPERATOR)")
    role_label: str = Field(..., description="角色展示标签 (如 超级管理员/专业课指导教师/AI 自治智能体)")
    department: str = Field(..., description="所属教研室/班级/部门")
    phone: Optional[str] = Field(default=None, description="联系电话")
    status: str = Field(default="ONLINE", description="在线状态 (如 ONLINE / 7×24H 实时在线)")
    is_system_agent: bool = Field(default=False, description="是否系统/AI虚拟智能体主体")
    avatar_text: str = Field(default="", description="头像缩写文字或图标标识")
    responsibilities: List[str] = Field(default_factory=list, description="职责/权责清单")
    description: Optional[str] = Field(default=None, description="主体简介或算法架构说明")
    created_at: Optional[str] = Field(default=None, description="注册或上线时间")

    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdateRequest(BaseModel):
    """用户个人资料更新请求数据模式"""

    real_name: Optional[str] = Field(default=None, min_length=1, max_length=64, description="真实姓名")
    phone: Optional[str] = Field(default=None, max_length=32, description="联系电话")
    department: Optional[str] = Field(default=None, min_length=1, max_length=128, description="所属教研室/班级/部门")

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ChangePasswordRequest(BaseModel):
    """用户修改密码请求数据模式"""

    username: str = Field(..., min_length=1, max_length=64, description="登录工号/学号")
    old_password: str = Field(..., min_length=1, max_length=64, description="原密码")
    new_password: str = Field(..., min_length=6, max_length=64, description="新密码 (至少6位)")

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)



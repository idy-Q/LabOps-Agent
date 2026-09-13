"""系统用户认证与权限数据模式 (Pydantic Schemas)"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field

UserRoleType = Literal["ADMIN", "TEACHER", "STUDENT"]


class UserRegisterRequest(BaseModel):
    """用户注册请求数据模式"""

    username: str = Field(..., min_length=2, max_length=64, description="登录工号/学号")
    password: str = Field(..., min_length=6, max_length=64, description="登录密码 (至少6位)")
    real_name: str = Field(..., min_length=1, max_length=64, description="真实姓名，如 王主管/李老师")
    role: UserRoleType = Field(default="TEACHER", description="申请角色: ADMIN, TEACHER, STUDENT")
    department: str = Field(..., min_length=1, max_length=128, description="所属教研室/班级/部门")
    phone: Optional[str] = Field(default=None, max_length=32, description="联系电话")
    admin_code: Optional[str] = Field(default=None, description="管理员专属安全激活口令 (申请 ADMIN 角色时必填)")

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

"""用户认证相关数据传输对象"""
from typing import Optional

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class RegisterRequest(BaseModel):
    """注册请求"""
    username: str


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    user_id: int
    old_password: str
    new_password: str


class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    user_id: int


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    role: str
    created_at: Optional[str]

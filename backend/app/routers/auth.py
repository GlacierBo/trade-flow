from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    ApiResponse,
    LoginRequest,
    RegisterRequest,
    ChangePasswordRequest,
    ResetPasswordRequest,
)
from app.services import auth

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    result = auth.verify_user(db, body.username, body.password)
    if not result:
        return ApiResponse(success=False, error="用户名或密码错误")
    return ApiResponse(data=result)


@router.post("/register")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    """用户注册（自动生成密码）"""
    result = auth.register_user(db, body.username)
    if "error" in result:
        return ApiResponse(success=False, error=result["error"])
    return ApiResponse(data=result)


@router.post("/change-password")
def change_password(body: ChangePasswordRequest, db: Session = Depends(get_db)):
    """修改密码"""
    success = auth.change_password(db, body.user_id, body.old_password, body.new_password)
    if not success:
        return ApiResponse(success=False, error="原密码错误")
    return ApiResponse(data={"status": "success"})


@router.post("/reset-password")
def reset_password(body: ResetPasswordRequest, db: Session = Depends(get_db)):
    """管理员重置密码"""
    new_password = auth.reset_password(db, body.user_id)
    if not new_password:
        return ApiResponse(success=False, error="用户不存在")
    return ApiResponse(data={"password": new_password})


@router.get("/users")
def get_users(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    """获取用户列表（管理员）"""
    result = auth.get_users(db, page, page_size)
    return ApiResponse(data=result)

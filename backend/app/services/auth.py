"""用户认证服务"""

import hashlib
import secrets

from sqlalchemy.orm import Session

from app.models import User


def generate_salt() -> str:
    """生成 16 位随机盐值"""
    return secrets.token_hex(16)[:16]


def hash_password(password: str, salt: str) -> str:
    """MD5(password + salt) 加密"""
    return hashlib.md5((password + salt).encode()).hexdigest()


def generate_password() -> str:
    """生成 12 位随机密码"""
    return secrets.token_hex(8)[:12]


def verify_user(db: Session, username: str, password: str) -> dict | None:
    """验证用户登录，成功返回用户信息，失败返回 None"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None

    hashed = hash_password(password, user.salt)
    if hashed != user.password:
        return None

    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
    }


def register_user(db: Session, username: str) -> dict:
    """注册用户，返回用户 ID 和生成的密码"""
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        return {"error": "用户名已被注册"}

    password = generate_password()
    salt = generate_salt()
    hashed = hash_password(password, salt)

    user = User(
        username=username,
        password=hashed,
        salt=salt,
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"id": user.id, "password": password}


def change_password(db: Session, user_id: int, old_password: str, new_password: str) -> bool:
    """修改密码，成功返回 True"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False

    old_hashed = hash_password(old_password, user.salt)
    if old_hashed != user.password:
        return False

    salt = generate_salt()
    hashed = hash_password(new_password, salt)

    user.password = hashed
    user.salt = salt
    db.commit()

    return True


def reset_password(db: Session, user_id: int) -> str:
    """管理员重置密码，默认重置为 123456，返回新密码"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return ""

    new_password = "123456"
    salt = generate_salt()
    hashed = hash_password(new_password, salt)

    user.password = hashed
    user.salt = salt
    db.commit()

    return new_password


def get_users(db: Session, page: int = 1, page_size: int = 20) -> dict:
    """分页获取用户列表"""
    total = db.query(User).count()
    offset = (page - 1) * page_size

    users = db.query(User).order_by(User.created_at.desc()).offset(offset).limit(page_size).all()

    user_list = [{
        "id": u.id,
        "username": u.username,
        "role": u.role,
        "created_at": u.created_at.isoformat() if u.created_at else None,
    } for u in users]

    return {"users": user_list, "total": total}

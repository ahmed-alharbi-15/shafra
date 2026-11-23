from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .config import get_settings
from .database import get_db
from .models import STAFF, User

settings = get_settings()
ALGORITHM = "HS256"
bearer = HTTPBearer(auto_error=False)

# نفس جدول الصلاحيات اللي في js/auth.js — السيرفر هو اللي يتحقق فعليًا
PERMS = {
    "viewPortal": ("owner", "admin", "moderator", "employee"),
    "viewAccounts": ("owner", "admin"),
    "viewAllTasks": ("owner", "admin", "moderator"),
    # المشرف يضيف المهام ويوزعها ويتابع الموظفين؛ الحذف والرتب والمال للـ Owner
    "createTask": ("owner", "admin", "moderator"),
    "assignTask": ("owner", "admin", "moderator"),
    "deleteTask": ("owner", "admin", "moderator"),
    "claimTask": ("owner", "admin", "moderator", "employee"),
    "seePhones": ("owner",),
    "manageRoles": ("owner",),
}


def can(perm: str, user: User) -> bool:
    return user.role in PERMS.get(perm, ())


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except ValueError:
        return False


def create_access_token(user_id: int, remember: bool = False) -> str:
    minutes = settings.REMEMBER_TOKEN_EXPIRE_MINUTES if remember else settings.ACCESS_TOKEN_EXPIRE_MINUTES
    expire = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    return jwt.encode({"sub": str(user_id), "exp": expire}, settings.SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="لازم تسجل دخول",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if creds is None:
        raise unauthorized
    try:
        payload = jwt.decode(creds.credentials, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise unauthorized
    user = db.get(User, user_id)
    if not user:
        raise unauthorized
    return user


def require(perm: str):
    def dep(user: User = Depends(get_current_user)) -> User:
        if not can(perm, user):
            raise HTTPException(status_code=403, detail="ما عندك صلاحية لهذا")
        return user

    return dep


def require_staff(user: User = Depends(get_current_user)) -> User:
    if user.role not in STAFF:
        raise HTTPException(status_code=403, detail="بوابة الفريق للموظفين بس")
    return user

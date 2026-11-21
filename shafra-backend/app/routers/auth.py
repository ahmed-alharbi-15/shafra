from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import LoginIn, MemberOut, MemberSelfUpdate, PasswordChange, ProfileOut, TokenOut
from ..security import create_access_token, get_current_user, hash_password, verify_password
from ..serializers import member_out, profile_out

router = APIRouter(prefix="/api/auth", tags=["Auth"])

# ما فيه تسجيل عام: البوابة «للأدمن والموظفين فقط»، والأدمن هو اللي يضيف الحسابات من /api/team


@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="الإيميل أو كلمة المرور غلط")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="الحساب موقوف، كلّم الأدمن")
    return TokenOut(access_token=create_access_token(user.id, data.remember), user=member_out(db, user))


@router.get("/me", response_model=ProfileOut)
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """ملفي الشخصي مع الإحصائيات والسجل"""
    return profile_out(db, user)


@router.patch("/me", response_model=MemberOut)
def update_me(data: MemberSelfUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return member_out(db, user)


@router.post("/change-password", status_code=204)
def change_password(data: PasswordChange, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(data.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="كلمة المرور الحالية غلط")
    user.hashed_password = hash_password(data.new_password)
    db.commit()

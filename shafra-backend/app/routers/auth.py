from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Task, User
from ..schemas import DeleteMe, EmailChange, LoginIn, MeUpdate, PasswordChange, RegisterIn, TokenOut, UserOut
from ..security import create_access_token, get_current_user, hash_password, verify_password
from ..serializers import user_out

router = APIRouter(tags=["Auth & Me"])


@router.post("/api/auth/register", response_model=TokenOut, status_code=201)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    """تسجيل عام — أي أحد يسجل يصير «عميل»، والـ Owner يغيّر رتبته بعدين"""
    email = data.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=400, detail="هذا الإيميل مسجّل من قبل.")
    user = User(name=data.name, email=email, phone=data.phone or "", hashed_password=hash_password(data.password), role="client")
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenOut(access_token=create_access_token(user.id, data.remember), user=user_out(user))


@router.post("/api/auth/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="الإيميل أو كلمة المرور غلط.")
    return TokenOut(access_token=create_access_token(user.id, data.remember), user=user_out(user))


@router.get("/api/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user_out(user)


@router.patch("/api/me", response_model=UserOut)
def update_me(data: MeUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is None:
            continue
        if field == "name":
            value = value.strip()
        if field in ("domains", "languages"):
            value = [str(x).strip() for x in value if str(x).strip()][:30]
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user_out(user)


@router.post("/api/me/email", response_model=UserOut)
def change_email(data: EmailChange, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="كلمة المرور الحالية غلط.")
    email = data.newEmail.lower()
    if db.scalar(select(User).where(User.email == email, User.id != user.id)):
        raise HTTPException(status_code=400, detail="هذا الإيميل مستخدم.")
    user.email = email
    db.commit()
    db.refresh(user)
    return user_out(user)


@router.post("/api/me/password", status_code=204)
def change_password(data: PasswordChange, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(data.oldPassword, user.hashed_password):
        raise HTTPException(status_code=400, detail="كلمة المرور الحالية غلط.")
    user.hashed_password = hash_password(data.newPassword)
    db.commit()


@router.delete("/api/me", status_code=204)
def delete_me(data: DeleteMe, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role == "owner":
        raise HTTPException(status_code=400, detail="حساب Owner ما ينحذف من الموقع.")
    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="كلمة المرور غلط.")
    # المهام اللي كانت عليه ترجع مفتوحة
    db.execute(update(Task).where(Task.assignee_id == user.id).values(assignee_id=None))
    db.delete(user)
    db.commit()

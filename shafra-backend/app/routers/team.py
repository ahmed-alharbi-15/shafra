from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import MemberCreate, MemberOut, MemberUpdate, PasswordReset, ProfileOut
from ..security import get_current_user, hash_password, require_admin
from ..serializers import member_out, profile_out

router = APIRouter(prefix="/api/team", tags=["Team"])


@router.get("", response_model=list[MemberOut])
def list_team(include_inactive: bool = False, me: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = select(User).order_by(User.is_admin.desc(), User.id)
    if not (include_inactive and me.is_admin):
        stmt = stmt.where(User.is_active.is_(True))
    return [member_out(db, u) for u in db.scalars(stmt).all()]


@router.get("/{user_id}", response_model=ProfileOut)
def get_profile(user_id: int, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="الموظف غير موجود")
    return profile_out(db, user)


@router.post("", response_model=MemberOut, status_code=201)
def create_member(data: MemberCreate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    email = data.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=400, detail="الإيميل مستخدم لحساب ثاني")
    values = data.model_dump(exclude={"password", "email"})
    user = User(**values, email=email, hashed_password=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return member_out(db, user)


@router.patch("/{user_id}", response_model=MemberOut)
def update_member(user_id: int, data: MemberUpdate, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="الموظف غير موجود")
    values = data.model_dump(exclude_unset=True)
    if user.id == admin.id and (values.get("is_admin") is False or values.get("is_active") is False):
        raise HTTPException(status_code=400, detail="ما تقدر تشيل صلاحيتك أو توقف حسابك بنفسك")
    if "email" in values and values["email"]:
        values["email"] = values["email"].lower()
        clash = db.scalar(select(User).where(User.email == values["email"], User.id != user.id))
        if clash:
            raise HTTPException(status_code=400, detail="الإيميل مستخدم لحساب ثاني")
    for field, value in values.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return member_out(db, user)


@router.post("/{user_id}/reset-password", status_code=204)
def reset_password(user_id: int, data: PasswordReset, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    """«نسيت كلمة المرور؟» — الأدمن يحط له كلمة مرور جديدة"""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="الموظف غير موجود")
    user.hashed_password = hash_password(data.new_password)
    db.commit()


@router.delete("/{user_id}", status_code=204)
def deactivate_member(user_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    """يوقف الحساب بدل ما يحذفه، عشان يبقى سجل مهامه"""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="الموظف غير موجود")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="ما تقدر توقف حسابك")
    user.is_active = False
    db.commit()

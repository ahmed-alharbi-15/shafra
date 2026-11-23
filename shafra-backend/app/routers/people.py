from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import STAFF, User
from ..schemas import MeetingsIn, PersonOut, RoleIn, UserOut
from ..security import require, require_staff
from ..serializers import person_out, user_out

router = APIRouter(tags=["People & Roles"])


@router.get("/api/people", response_model=list[PersonOut])
def people(viewer: User = Depends(require_staff), db: Session = Depends(get_db)):
    """الموظفين (كل رتبة غير عميل)، مع سجل تسليماتهم"""
    users = db.scalars(select(User).where(User.role.in_(STAFF)).order_by(User.id)).all()
    order = {r: i for i, r in enumerate(STAFF)}
    users = sorted(users, key=lambda u: (order.get(u.role, 9), u.id))
    return [person_out(db, u, viewer) for u in users]


@router.get("/api/users", response_model=list[UserOut])
def all_users(viewer: User = Depends(require("manageRoles")), db: Session = Depends(get_db)):
    """كل الحسابات حتى العملاء — لإدارة الرتب (Owner بس)"""
    return [user_out(u, viewer) for u in db.scalars(select(User).order_by(User.id)).all()]


@router.patch("/api/users/{user_id}/role", response_model=UserOut)
def set_role(user_id: int, data: RoleIn, viewer: User = Depends(require("manageRoles")), db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="الحساب غير موجود.")
    if user.role == "owner":
        raise HTTPException(status_code=400, detail="رتبة Owner ثابتة.")
    user.role = data.role
    db.commit()
    db.refresh(user)
    return user_out(user, viewer)


@router.patch("/api/users/{user_id}/meetings", response_model=UserOut)
def set_meetings(user_id: int, data: MeetingsIn, viewer: User = Depends(require("manageRoles")), db: Session = Depends(get_db)):
    """حضور الاجتماعات (Owner بس)"""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="الحساب غير موجود.")
    if data.attended > data.total:
        raise HTTPException(status_code=400, detail="الحضور أكثر من عدد الاجتماعات.")
    user.meetings_attended, user.meetings_total = data.attended, data.total
    db.commit()
    db.refresh(user)
    return user_out(user, viewer)

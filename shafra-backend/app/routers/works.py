from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Work
from ..schemas import Category, WorkCreate, WorkOut, WorksListOut, WorkUpdate
from ..security import require_admin

router = APIRouter(prefix="/api/works", tags=["Works"])


def _counts(works: list[Work]) -> dict[str, int]:
    counts = {"all": len(works), "site": 0, "app": 0, "dash": 0, "student": 0}
    for w in works:
        for c in w.cats or []:
            if c in counts:
                counts[c] += 1
    return counts


def _ordered():
    return select(Work).order_by(Work.sort_order, Work.created_at.desc())


@router.get("", response_model=WorksListOut)
def public_list(cat: Category | None = None, db: Session = Depends(get_db)):
    """للموقع العام — صفحة الأعمال مع عدد كل فلتر"""
    published = db.scalars(_ordered().where(Work.is_published.is_(True))).all()
    items = [w for w in published if cat is None or cat in (w.cats or [])]
    return WorksListOut(items=items, counts=_counts(published))


@router.get("/admin/all", response_model=list[WorkOut])
def admin_list(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    """كل الأعمال حتى غير المنشورة"""
    return db.scalars(_ordered()).all()


@router.get("/{slug}", response_model=WorkOut)
def get_work(slug: str, db: Session = Depends(get_db)):
    work = db.scalar(select(Work).where(Work.slug == slug, Work.is_published.is_(True)))
    if not work:
        raise HTTPException(status_code=404, detail="العمل غير موجود")
    return work


@router.post("", response_model=WorkOut, status_code=201)
def create_work(data: WorkCreate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    if db.scalar(select(Work.id).where(Work.slug == data.slug)):
        raise HTTPException(status_code=400, detail="الـ slug مستخدم لعمل ثاني")
    work = Work(**data.model_dump())
    db.add(work)
    db.commit()
    db.refresh(work)
    return work


@router.patch("/{work_id}", response_model=WorkOut)
def update_work(work_id: int, data: WorkUpdate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    work = db.get(Work, work_id)
    if not work:
        raise HTTPException(status_code=404, detail="العمل غير موجود")
    values = data.model_dump(exclude_unset=True)
    if values.get("slug") and db.scalar(select(Work.id).where(Work.slug == values["slug"], Work.id != work_id)):
        raise HTTPException(status_code=400, detail="الـ slug مستخدم لعمل ثاني")
    for field, value in values.items():
        setattr(work, field, value)
    db.commit()
    db.refresh(work)
    return work


@router.delete("/{work_id}", status_code=204)
def delete_work(work_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    work = db.get(Work, work_id)
    if not work:
        raise HTTPException(status_code=404, detail="العمل غير موجود")
    db.delete(work)
    db.commit()

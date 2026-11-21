from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Payment, User
from ..schemas import CategoryTotal, PaymentIn, PaymentOut, PaymentsMonthOut
from ..security import require_admin

router = APIRouter(prefix="/api/payments", tags=["Accounts"])

CATEGORIES = ["site", "app", "dash", "student"]


@router.get("", response_model=PaymentsMonthOut)
def month_view(
    month: str | None = Query(default=None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$", description="مثل 2026-11، الافتراضي الشهر الحالي"),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    month = month or date.today().strftime("%Y-%m")
    items = db.scalars(select(Payment).where(Payment.month == month).order_by(Payment.created_at.desc())).all()
    by_cat = [
        CategoryTotal(
            category=c,
            count=sum(1 for p in items if p.category == c),
            total=sum(p.amount for p in items if p.category == c),
        )
        for c in CATEGORIES
    ]
    months = db.scalars(select(Payment.month).distinct().order_by(Payment.month)).all()
    return PaymentsMonthOut(
        month=month,
        items=[PaymentOut.model_validate(p) for p in items],
        count=len(items),
        month_total=sum(p.amount for p in items),
        all_total=db.scalar(select(func.coalesce(func.sum(Payment.amount), 0))) or 0,
        by_category=by_cat,
        months=list(months),
    )


@router.post("", response_model=PaymentOut, status_code=201)
def add_payment(data: PaymentIn, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    payment = Payment(**data.model_dump())
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


@router.delete("/{payment_id}", status_code=204)
def delete_payment(payment_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    payment = db.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="الدفعة غير موجودة")
    db.delete(payment)
    db.commit()

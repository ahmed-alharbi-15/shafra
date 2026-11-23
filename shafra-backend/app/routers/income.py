from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Income, User
from ..schemas import IncomeIn, IncomeOut
from ..security import require

router = APIRouter(prefix="/api/income", tags=["Income"])


@router.get("", response_model=list[IncomeOut])
def list_income(month: str | None = None, _: User = Depends(require("viewAccounts")), db: Session = Depends(get_db)):
    stmt = select(Income).order_by(Income.created_at, Income.id)
    if month:
        stmt = stmt.where(Income.month == month)
    return db.scalars(stmt).all()


@router.post("", response_model=IncomeOut, status_code=201)
def add_income(data: IncomeIn, _: User = Depends(require("viewAccounts")), db: Session = Depends(get_db)):
    entry = Income(name=data.name.strip(), cat=data.cat, amount=data.amount, month=data.month)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=204)
def delete_income(entry_id: int, _: User = Depends(require("viewAccounts")), db: Session = Depends(get_db)):
    entry = db.get(Income, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="الدفعة غير موجودة.")
    db.delete(entry)
    db.commit()

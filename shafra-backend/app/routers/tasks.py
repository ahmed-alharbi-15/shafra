from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..models import STAFF, Task, TaskItem, User
from ..schemas import ItemIn, ItemPatch, TaskCreate, TaskOut, TaskPatch
from ..security import can, require, require_staff
from ..serializers import refresh_completion, task_out

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


def _load(task_id: int, db: Session) -> Task:
    task = db.scalar(select(Task).options(selectinload(Task.items)).where(Task.id == task_id))
    if not task:
        raise HTTPException(status_code=404, detail="المهمة غير موجودة.")
    return task


def _check_assignee(assignee_id: int | None, db: Session) -> None:
    if assignee_id is None:
        return
    u = db.get(User, assignee_id)
    if not u or u.role not in STAFF:
        raise HTTPException(status_code=400, detail="الموظف المحدد غير موجود.")


def _can_work(task: Task, user: User) -> None:
    # المسؤول عن المهمة أو الـ Owner
    if not (task.assignee_id == user.id or can("assignTask", user)):
        raise HTTPException(status_code=403, detail="هذي المهمة مو لك.")


def _visible(task: Task, user: User) -> bool:
    return can("viewAllTasks", user) or task.assignee_id is None or task.assignee_id == user.id


@router.get("", response_model=list[TaskOut])
def list_tasks(user: User = Depends(require_staff), db: Session = Depends(get_db)):
    """owner/admin/moderator: الكل — الموظف: مهامه + المفتوحة"""
    stmt = select(Task).options(selectinload(Task.items)).order_by(Task.created_at.desc(), Task.id.desc())
    if not can("viewAllTasks", user):
        stmt = stmt.where(or_(Task.assignee_id.is_(None), Task.assignee_id == user.id))
    return [task_out(t) for t in db.scalars(stmt).all()]


@router.post("", response_model=TaskOut, status_code=201)
def create_task(data: TaskCreate, _: User = Depends(require("createTask")), db: Session = Depends(get_db)):
    _check_assignee(data.assignee, db)
    task = Task(
        title=data.title.strip(),
        project=(data.project or "").strip() or "عام",
        due=data.due,
        priority=data.priority,
        assignee_id=data.assignee,
    )
    for it in data.items:
        text = (it if isinstance(it, str) else it.text).strip()
        if text:
            task.items.append(TaskItem(text=text[:300], done=False if isinstance(it, str) else it.done))
    refresh_completion(task)
    db.add(task)
    db.commit()
    return task_out(_load(task.id, db))


@router.patch("/{task_id}", response_model=TaskOut)
def patch_task(task_id: int, data: TaskPatch, _: User = Depends(require("assignTask")), db: Session = Depends(get_db)):
    task = _load(task_id, db)
    values = data.model_dump(exclude_unset=True)
    if "assignee" in values:
        _check_assignee(values["assignee"], db)
        task.assignee_id = values.pop("assignee")
    for field, value in values.items():
        if value is not None:
            setattr(task, field, value)
    db.commit()
    return task_out(_load(task_id, db))


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, _: User = Depends(require("deleteTask")), db: Session = Depends(get_db)):
    db.delete(_load(task_id, db))
    db.commit()


@router.post("/{task_id}/claim", response_model=TaskOut)
def claim(task_id: int, user: User = Depends(require("claimTask")), db: Session = Depends(get_db)):
    task = _load(task_id, db)
    if task.assignee_id is not None:
        raise HTTPException(status_code=400, detail="المهمة مأخوذة من قبل.")
    task.assignee_id = user.id
    db.commit()
    return task_out(_load(task_id, db))


@router.post("/{task_id}/items", response_model=TaskOut, status_code=201)
def add_item(task_id: int, data: ItemIn, user: User = Depends(require_staff), db: Session = Depends(get_db)):
    task = _load(task_id, db)
    _can_work(task, user)
    task.items.append(TaskItem(text=data.text.strip()))
    refresh_completion(task)
    db.commit()
    return task_out(_load(task_id, db))


@router.patch("/{task_id}/items/{index}", response_model=TaskOut)
def patch_item(task_id: int, index: int, data: ItemPatch, user: User = Depends(require_staff), db: Session = Depends(get_db)):
    """index = ترتيب العمل في القائمة (يبدأ من 0)"""
    task = _load(task_id, db)
    _can_work(task, user)
    if not 0 <= index < len(task.items):
        raise HTTPException(status_code=404, detail="العمل غير موجود.")
    item = task.items[index]
    if data.done is not None:
        item.done = data.done
    if data.text is not None:
        item.text = data.text.strip()
    refresh_completion(task)
    db.commit()
    return task_out(_load(task_id, db))


@router.delete("/{task_id}/items/{index}", response_model=TaskOut)
def delete_item(task_id: int, index: int, user: User = Depends(require_staff), db: Session = Depends(get_db)):
    task = _load(task_id, db)
    _can_work(task, user)
    if not 0 <= index < len(task.items):
        raise HTTPException(status_code=404, detail="العمل غير موجود.")
    task.items.pop(index)
    refresh_completion(task)
    db.commit()
    return task_out(_load(task_id, db))

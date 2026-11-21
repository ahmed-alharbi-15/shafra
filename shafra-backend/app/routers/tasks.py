from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..models import Task, TaskItem, User
from ..schemas import ItemIn, ItemUpdate, TaskCreate, TaskOut, TaskStats, TaskStatus, TaskUpdate
from ..security import get_current_user, require_admin
from ..serializers import items_totals, refresh_completion, task_out, task_status

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


def _load(task_id: int, db: Session) -> Task:
    task = db.scalar(select(Task).options(selectinload(Task.items)).where(Task.id == task_id))
    if not task:
        raise HTTPException(status_code=404, detail="المهمة غير موجودة")
    return task


def _can_work_on(task: Task, user: User) -> None:
    # الأدمن يعدل أي مهمة، والموظف يعدل أعمال مهامه هو بس
    if not user.is_admin and task.assignee_id != user.id:
        raise HTTPException(status_code=403, detail="هذي المهمة مو لك")


def _check_assignee(assignee_id: int | None, db: Session) -> None:
    if assignee_id is not None:
        u = db.get(User, assignee_id)
        if not u or not u.is_active:
            raise HTTPException(status_code=400, detail="الموظف المحدد غير موجود")


@router.get("", response_model=list[TaskOut])
def list_tasks(
    assignee_id: int | None = None,
    status: TaskStatus | None = None,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = select(Task).options(selectinload(Task.items), selectinload(Task.assignee))
    if assignee_id is not None:
        stmt = stmt.where(Task.assignee_id == assignee_id)
    stmt = stmt.order_by(Task.due.is_(None), Task.due, Task.id)
    tasks = db.scalars(stmt).all()
    if status:
        tasks = [t for t in tasks if task_status(t) == status]
    return [task_out(t) for t in tasks]


@router.get("/stats", response_model=TaskStats)
def stats(assignee_id: int | None = None, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = select(Task).options(selectinload(Task.items))
    if assignee_id is not None:
        stmt = stmt.where(Task.assignee_id == assignee_id)
    tasks = db.scalars(stmt).all()
    by_status = {"new": 0, "doing": 0, "done": 0}
    for t in tasks:
        by_status[task_status(t)] += 1
    if assignee_id is None:
        done_items, all_items = items_totals(db)
    else:
        all_items = sum(len(t.items) for t in tasks)
        done_items = sum(1 for t in tasks for i in t.items if i.done)
    people = db.scalar(select(func.count()).select_from(User).where(User.is_active.is_(True))) or 0
    return TaskStats(
        open=by_status["new"] + by_status["doing"],
        done_items=done_items,
        all_items=all_items,
        complete=by_status["done"],
        people=people,
        by_status=by_status,
    )


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return task_out(_load(task_id, db))


@router.post("", response_model=TaskOut, status_code=201)
def create_task(data: TaskCreate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    _check_assignee(data.assignee_id, db)
    task = Task(**data.model_dump(exclude={"items"}))
    task.items = [TaskItem(text=t.strip()) for t in data.items if t.strip()]
    db.add(task)
    db.commit()
    return task_out(_load(task.id, db))


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, data: TaskUpdate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    task = _load(task_id, db)
    values = data.model_dump(exclude_unset=True)
    if "assignee_id" in values:
        _check_assignee(values["assignee_id"], db)
    for field, value in values.items():
        setattr(task, field, value)
    db.commit()
    return task_out(_load(task_id, db))


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    db.delete(_load(task_id, db))
    db.commit()


# ----- قائمة الأعمال تحت المهمة -----
@router.post("/{task_id}/items", response_model=TaskOut, status_code=201)
def add_item(task_id: int, data: ItemIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = _load(task_id, db)
    _can_work_on(task, user)
    task.items.append(TaskItem(text=data.text.strip()))
    refresh_completion(task)
    db.commit()
    return task_out(_load(task_id, db))


@router.patch("/{task_id}/items/{item_id}", response_model=TaskOut)
def update_item(
    task_id: int, item_id: int, data: ItemUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    task = _load(task_id, db)
    _can_work_on(task, user)
    item = next((i for i in task.items if i.id == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="العمل غير موجود")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    refresh_completion(task)
    db.commit()
    return task_out(_load(task_id, db))


@router.delete("/{task_id}/items/{item_id}", response_model=TaskOut)
def delete_item(task_id: int, item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = _load(task_id, db)
    _can_work_on(task, user)
    item = next((i for i in task.items if i.id == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="العمل غير موجود")
    task.items.remove(item)
    refresh_completion(task)
    db.commit()
    return task_out(_load(task_id, db))

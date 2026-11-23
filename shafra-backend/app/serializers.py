from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Task, User
from .schemas import HistoryRow, ItemOut, Meetings, PersonOut, TaskOut, UserOut
from .security import can


def task_status(task: Task) -> str:
    total = len(task.items)
    done = sum(1 for i in task.items if i.done)
    if total and done == total:
        return "done"
    if done > 0:
        return "doing"
    return "new"


def refresh_completion(task: Task) -> None:
    """يسجل تاريخ التسليم أول ما تكتمل كل الأعمال، ويشيله لو رجع شي مفتوح"""
    if task_status(task) == "done":
        if task.completed_at is None:
            task.completed_at = date.today()
    else:
        task.completed_at = None


def task_out(task: Task) -> TaskOut:
    return TaskOut(
        id=task.id,
        title=task.title,
        project=task.project,
        due=task.due,
        priority=task.priority,
        assignee=task.assignee_id,
        items=[ItemOut.model_validate(i) for i in task.items],
        completed_at=task.completed_at,
        created_at=task.created_at,
    )


def user_out(user: User, viewer: User | None = None) -> UserOut:
    # الجوال ما يرجع إلا للـ Owner ولصاحب الحساب
    show_phone = viewer is None or viewer.id == user.id or can("seePhones", viewer)
    return UserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        phone=user.phone if show_phone else None,
        role=user.role,
        domains=user.domains or [],
        languages=user.languages or [],
        status=user.status,
        meetings=Meetings(attended=user.meetings_attended, total=user.meetings_total),
        created_at=user.created_at,
    )


def person_out(db: Session, user: User, viewer: User) -> PersonOut:
    done = db.scalars(
        select(Task)
        .where(Task.assignee_id == user.id, Task.completed_at.is_not(None))
        .order_by(Task.completed_at.desc())
    ).all()
    history = [HistoryRow(title=t.title, project=t.project, due=t.due, done=t.completed_at) for t in done]
    return PersonOut(**user_out(user, viewer).model_dump(), history=history)

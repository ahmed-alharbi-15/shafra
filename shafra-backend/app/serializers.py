"""تحويل الموديلات لشكل الـ JSON اللي يحتاجه الفرونت اند"""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .config import get_settings
from .models import Task, TaskItem, User
from .schemas import HistoryRow, ItemOut, MemberOut, OpenTaskRow, ProfileOut, TaskOut


def initial_of(name: str) -> str:
    return name.strip()[:1] if name and name.strip() else "؟"


def task_status(task: Task) -> str:
    total = len(task.items)
    done = sum(1 for i in task.items if i.done)
    if total and done == total:
        return "done"
    if done > 0:
        return "doing"
    return "new"


def refresh_completion(task: Task) -> None:
    """يسجل تاريخ التسليم أول ما تكتمل كل الأعمال، ويشيله لو رجع شي منها مفتوح"""
    if task_status(task) == "done":
        if task.completed_at is None:
            task.completed_at = date.today()
    else:
        task.completed_at = None


def task_out(task: Task) -> TaskOut:
    owner = task.assignee
    return TaskOut(
        id=task.id,
        title=task.title,
        project=task.project,
        priority=task.priority,
        due=task.due,
        status=task_status(task),
        done_count=sum(1 for i in task.items if i.done),
        total=len(task.items),
        assignee_id=task.assignee_id,
        assignee_name=owner.name if owner else None,
        assignee_initial=initial_of(owner.name) if owner else None,
        completed_at=task.completed_at,
        items=[ItemOut.model_validate(i) for i in task.items],
        created_at=task.created_at,
    )


def open_task_count(db: Session, user_id: int) -> int:
    # مهمة مفتوحة = فيها عمل واحد على الأقل مو منجز، أو ما فيها أعمال أصلًا
    tasks = db.scalars(select(Task).where(Task.assignee_id == user_id)).all()
    return sum(1 for t in tasks if task_status(t) != "done")


def member_out(db: Session, user: User) -> MemberOut:
    return MemberOut(
        id=user.id,
        name=user.name,
        initial=initial_of(user.name),
        email=user.email,
        is_admin=user.is_admin,
        is_owner=get_settings().is_owner_email(user.email),
        is_active=user.is_active,
        role=user.role,
        title=user.title,
        status=user.status,
        skills=user.skills or [],
        duties=user.duties or [],
        joined=user.joined,
        avatar_url=user.avatar_url,
        meetings_attended=user.meetings_attended,
        meetings_total=user.meetings_total,
        open_task_count=open_task_count(db, user.id),
    )


def grade_for(pct: int, has_history: bool) -> str:
    if not has_history:
        return "—"
    if pct >= 90:
        return "ممتاز"
    if pct >= 75:
        return "جيد جدًا"
    if pct >= 60:
        return "جيد"
    return "يحتاج تحسين"


def profile_out(db: Session, user: User) -> ProfileOut:
    tasks = db.scalars(select(Task).where(Task.assignee_id == user.id).order_by(Task.due)).all()
    open_tasks = [t for t in tasks if task_status(t) != "done"]
    done_tasks = sorted(
        (t for t in tasks if t.completed_at is not None), key=lambda t: t.completed_at, reverse=True
    )

    history: list[HistoryRow] = []
    for t in done_tasks:
        late = max(0, (t.completed_at - t.due).days) if t.due else 0
        history.append(
            HistoryRow(
                task_id=t.id, title=t.title, project=t.project, due=t.due,
                done=t.completed_at, on_time=late == 0, days_late=late,
            )
        )

    on_time = sum(1 for h in history if h.on_time)
    late_rows = [h.days_late for h in history if not h.on_time]
    on_time_pct = round(on_time * 100 / len(history)) if history else 0
    meet_pct = round(user.meetings_attended * 100 / user.meetings_total) if user.meetings_total else 0

    base = member_out(db, user).model_dump()
    base["open_task_count"] = len(open_tasks)
    return ProfileOut(
        **base,
        open_tasks=[OpenTaskRow(id=t.id, title=t.title, project=t.project, due=t.due) for t in open_tasks],
        done_count=len(history),
        on_time_pct=on_time_pct,
        avg_late_days=round(sum(late_rows) / len(late_rows), 1) if late_rows else 0,
        grade=grade_for(on_time_pct, bool(history)),
        meet_pct=meet_pct,
        history=history,
    )


def items_totals(db: Session) -> tuple[int, int]:
    total = db.scalar(select(func.count()).select_from(TaskItem)) or 0
    done = db.scalar(select(func.count()).select_from(TaskItem).where(TaskItem.done.is_(True))) or 0
    return done, total

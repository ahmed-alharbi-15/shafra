from datetime import date, datetime, timezone

from sqlalchemy import JSON, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

SCHEMA_VERSION = "2"

ROLES = ("owner", "admin", "moderator", "employee", "client")
STAFF = ("owner", "admin", "moderator", "employee")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AppMeta(Base):
    __tablename__ = "app_meta"

    key: Mapped[str] = mapped_column(String(50), primary_key=True)
    value: Mapped[str] = mapped_column(String(200))


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(30), default="")
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="client", index=True)
    domains: Mapped[list] = mapped_column(JSON, default=list)  # مجالات العمل
    languages: Mapped[list] = mapped_column(JSON, default=list)  # لغات البرمجة
    status: Mapped[str] = mapped_column(String(20), default="متاح")  # متاح | مشغول | إجازة
    meetings_attended: Mapped[int] = mapped_column(Integer, default=0)
    meetings_total: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    tasks: Mapped[list["Task"]] = relationship(back_populates="assignee")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    project: Mapped[str] = mapped_column(String(150), default="عام")
    priority: Mapped[str] = mapped_column(String(20), default="متوسطة")  # عالية | متوسطة | منخفضة
    due: Mapped[date | None] = mapped_column(Date, nullable=True)
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    completed_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    assignee: Mapped[User | None] = relationship(back_populates="tasks")
    items: Mapped[list["TaskItem"]] = relationship(
        back_populates="task", cascade="all, delete-orphan", order_by="TaskItem.id"
    )


class TaskItem(Base):
    __tablename__ = "task_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"))
    text: Mapped[str] = mapped_column(String(300))
    done: Mapped[bool] = mapped_column(Boolean, default=False)

    task: Mapped[Task] = relationship(back_populates="items")


class Income(Base):
    """دفعة دخل في صفحة الحسابات"""

    __tablename__ = "income"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    cat: Mapped[str] = mapped_column(String(20))  # site | app | dash | student
    amount: Mapped[float] = mapped_column(Float)
    month: Mapped[str] = mapped_column(String(7), index=True)  # 2026-11
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Work(Base):
    """عمل معروض في صفحة الأعمال (اختياري — الموقع حاليًا يقرأ من projects-data.js)"""

    __tablename__ = "works"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    desc: Mapped[str] = mapped_column(Text, default="")
    cats: Mapped[list] = mapped_column(JSON, default=list)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    stack: Mapped[str] = mapped_column(String(300), default="")
    kind: Mapped[str] = mapped_column(String(30), default="site")
    href: Mapped[str | None] = mapped_column(String(500), nullable=True)
    live_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_personal: Mapped[bool] = mapped_column(Boolean, default=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

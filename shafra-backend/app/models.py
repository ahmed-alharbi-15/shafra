from datetime import date, datetime, timezone

from sqlalchemy import JSON, Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    """موظف أو أدمن في بوابة الفريق"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    role: Mapped[str] = mapped_column(String(100), default="")  # مثل: Frontend Developer
    title: Mapped[str] = mapped_column(String(150), default="")  # مثل: شريك مؤسس — مطوّر واجهات
    status: Mapped[str] = mapped_column(String(20), default="متاح")  # متاح | مشغول | إجازة
    skills: Mapped[list] = mapped_column(JSON, default=list)
    duties: Mapped[list] = mapped_column(JSON, default=list)
    joined: Mapped[date | None] = mapped_column(Date, nullable=True)
    meetings_attended: Mapped[int] = mapped_column(Integer, default=0)
    meetings_total: Mapped[int] = mapped_column(Integer, default=0)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    tasks: Mapped[list["Task"]] = relationship(back_populates="assignee")


class Task(Base):
    """مهمة، وتحتها قائمة أعمال (items)"""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    project: Mapped[str] = mapped_column(String(150), default="")
    priority: Mapped[str] = mapped_column(String(20), default="متوسطة")  # عالية | متوسطة | منخفضة
    due: Mapped[date | None] = mapped_column(Date, nullable=True)
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    completed_at: Mapped[date | None] = mapped_column(Date, nullable=True)  # تنحسب تلقائي لما تكتمل كل الأعمال
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


class Payment(Base):
    """دفعة دخل في صفحة الحسابات"""

    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))  # اسم المشروع
    category: Mapped[str] = mapped_column(String(20))  # site | app | dash | student
    amount: Mapped[int] = mapped_column(Integer)  # بالريال
    month: Mapped[str] = mapped_column(String(7), index=True)  # 2026-11
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Work(Base):
    """عمل معروض في صفحة الأعمال بالموقع العام"""

    __tablename__ = "works"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)  # مثل: sofrah
    title: Mapped[str] = mapped_column(String(200))
    desc: Mapped[str] = mapped_column(Text, default="")
    cats: Mapped[list] = mapped_column(JSON, default=list)  # ["site", "app"]
    tags: Mapped[list] = mapped_column(JSON, default=list)  # ["موقع", "تطبيق"]
    stack: Mapped[str] = mapped_column(String(300), default="")
    kind: Mapped[str] = mapped_column(String(30), default="site")  # شكل الكرت في التصميم
    href: Mapped[str | None] = mapped_column(String(500), nullable=True)  # صفحة المشروع
    live_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)  # Cloudinary
    is_personal: Mapped[bool] = mapped_column(Boolean, default=False)  # شارة «مشروع شخصي»
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

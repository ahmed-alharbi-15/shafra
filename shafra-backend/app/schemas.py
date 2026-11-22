from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

Category = Literal["site", "app", "dash", "student"]
Status = Literal["متاح", "مشغول", "إجازة"]
Priority = Literal["عالية", "متوسطة", "منخفضة"]
TaskStatus = Literal["new", "doing", "done"]


# ---------- Auth ----------
class LoginIn(BaseModel):
    email: EmailStr
    password: str
    remember: bool = False  # «تذكرني»: توكن يعيش 30 يوم بدل يوم


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=72)


class PasswordReset(BaseModel):
    new_password: str = Field(min_length=8, max_length=72)


# ---------- Team ----------
class MemberBase(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    role: str = ""
    title: str = ""
    status: Status = "متاح"
    skills: list[str] = []
    duties: list[str] = []
    joined: date | None = None
    avatar_url: str | None = None


class MemberCreate(MemberBase):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    is_admin: bool = False


class MemberUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
    role: str | None = None
    title: str | None = None
    status: Status | None = None
    skills: list[str] | None = None
    duties: list[str] | None = None
    joined: date | None = None
    avatar_url: str | None = None
    is_admin: bool | None = None
    is_active: bool | None = None
    meetings_attended: int | None = Field(default=None, ge=0)
    meetings_total: int | None = Field(default=None, ge=0)


class MemberSelfUpdate(BaseModel):
    """اللي يقدر الموظف يعدله في ملفه بنفسه"""

    status: Status | None = None
    skills: list[str] | None = None
    avatar_url: str | None = None


class MemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    initial: str
    email: str
    is_admin: bool
    is_owner: bool = False
    is_active: bool
    role: str
    title: str
    status: str
    skills: list[str]
    duties: list[str]
    joined: date | None
    avatar_url: str | None
    meetings_attended: int
    meetings_total: int
    open_task_count: int = 0


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: MemberOut


class HistoryRow(BaseModel):
    task_id: int
    title: str
    project: str
    due: date | None
    done: date
    on_time: bool
    days_late: int


class OpenTaskRow(BaseModel):
    id: int
    title: str
    project: str
    due: date | None


class ProfileOut(MemberOut):
    open_tasks: list[OpenTaskRow]
    done_count: int
    on_time_pct: int  # الالتزام بمواعيد التسليم
    avg_late_days: float  # متوسط التأخير للمتأخر
    grade: str  # التقييم
    meet_pct: int  # حضور الاجتماعات
    history: list[HistoryRow]  # سجل التسليمات


# ---------- Tasks ----------
class ItemIn(BaseModel):
    text: str = Field(min_length=1, max_length=300)


class ItemUpdate(BaseModel):
    text: str | None = Field(default=None, min_length=1, max_length=300)
    done: bool | None = None


class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    done: bool


class TaskCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    project: str = ""
    priority: Priority = "متوسطة"
    due: date | None = None
    assignee_id: int | None = None
    items: list[str] = []


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    project: str | None = None
    priority: Priority | None = None
    due: date | None = None
    assignee_id: int | None = None


class TaskOut(BaseModel):
    id: int
    title: str
    project: str
    priority: str
    due: date | None
    status: TaskStatus
    done_count: int
    total: int
    assignee_id: int | None
    assignee_name: str | None
    assignee_initial: str | None
    completed_at: date | None
    items: list[ItemOut]
    created_at: datetime


class TaskStats(BaseModel):
    open: int  # المهام المفتوحة
    done_items: int  # الأعمال المنجزة
    all_items: int
    complete: int  # المهام المكتملة
    people: int  # الموظفين
    by_status: dict[str, int]


# ---------- Payments ----------
class PaymentIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    category: Category
    amount: int = Field(gt=0)
    month: str = Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$", examples=["2026-11"])


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    amount: int
    month: str
    created_at: datetime


class CategoryTotal(BaseModel):
    category: str
    count: int
    total: int


class PaymentsMonthOut(BaseModel):
    month: str
    items: list[PaymentOut]
    count: int
    month_total: int
    all_total: int
    by_category: list[CategoryTotal]
    months: list[str]  # الشهور اللي فيها دفعات


# ---------- Works ----------
class WorkBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    desc: str = ""
    cats: list[Category] = Field(min_length=1)
    tags: list[str] = []
    stack: str = ""
    kind: str = "site"
    href: str | None = None
    live_url: str | None = None
    image_url: str | None = None
    is_personal: bool = False
    is_published: bool = True
    sort_order: int = 0


class WorkCreate(WorkBase):
    slug: str = Field(min_length=1, max_length=120, pattern=r"^[a-z0-9-]+$")


class WorkUpdate(BaseModel):
    slug: str | None = Field(default=None, min_length=1, max_length=120, pattern=r"^[a-z0-9-]+$")
    title: str | None = None
    desc: str | None = None
    cats: list[Category] | None = None
    tags: list[str] | None = None
    stack: str | None = None
    kind: str | None = None
    href: str | None = None
    live_url: str | None = None
    image_url: str | None = None
    is_personal: bool | None = None
    is_published: bool | None = None
    sort_order: int | None = None


class WorkOut(WorkBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    created_at: datetime


class WorksListOut(BaseModel):
    items: list[WorkOut]
    counts: dict[str, int]  # all, site, app, dash, student

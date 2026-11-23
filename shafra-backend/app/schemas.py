from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

Category = Literal["site", "app", "dash", "student"]
AssignableRole = Literal["admin", "moderator", "employee", "client"]
Priority = Literal["عالية", "متوسطة", "منخفضة"]
Status = Literal["متاح", "مشغول", "إجازة"]

PHONE_PATTERN = r"^\+?[0-9\s-]{8,16}$"


def _clean_phone(v: str | None) -> str:
    return (v or "").strip()


# ---------- Auth ----------
class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str | None = None
    password: str = Field(min_length=8, max_length=72)
    remember: bool = False

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("اكتب اسمك.")
        return v

    @field_validator("phone")
    @classmethod
    def check_phone(cls, v):
        import re

        v = _clean_phone(v)
        if v and not re.match(PHONE_PATTERN, v):
            raise ValueError("رقم الجوال مو صحيح.")
        return v


class LoginIn(BaseModel):
    email: EmailStr
    password: str
    remember: bool = False


class MeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    phone: str | None = None
    domains: list[str] | None = None
    languages: list[str] | None = None
    status: Status | None = None

    @field_validator("phone")
    @classmethod
    def check_phone(cls, v):
        import re

        if v is None:
            return v
        v = _clean_phone(v)
        if v and not re.match(PHONE_PATTERN, v):
            raise ValueError("رقم الجوال مو صحيح.")
        return v


class EmailChange(BaseModel):
    newEmail: EmailStr
    password: str


class PasswordChange(BaseModel):
    oldPassword: str
    newPassword: str = Field(min_length=8, max_length=72)


class DeleteMe(BaseModel):
    password: str


class RoleIn(BaseModel):
    role: AssignableRole


class MeetingsIn(BaseModel):
    attended: int = Field(ge=0)
    total: int = Field(ge=0)


# ---------- Users out ----------
class HistoryRow(BaseModel):
    title: str
    project: str
    due: date | None
    done: date


class Meetings(BaseModel):
    attended: int
    total: int


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    phone: str | None  # None = مخفي عنك
    role: str
    domains: list[str]
    languages: list[str]
    status: str
    meetings: Meetings
    created_at: datetime
    last_login_at: datetime | None = None  # للـ Owner بس


class PersonOut(UserOut):
    history: list[HistoryRow]  # سجل التسليمات


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Tasks ----------
class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    text: str
    done: bool


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    project: str = Field(default="عام", max_length=150)
    due: date | None = None
    priority: Priority = "متوسطة"
    assignee: int | None = None
    items: list[str | ItemOut] = []


class TaskPatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    project: str | None = None
    due: date | None = None
    priority: Priority | None = None
    assignee: int | None = None


class ItemIn(BaseModel):
    text: str = Field(min_length=1, max_length=300)


class ItemPatch(BaseModel):
    done: bool | None = None
    text: str | None = Field(default=None, min_length=1, max_length=300)


class TaskOut(BaseModel):
    id: int
    title: str
    project: str
    due: date | None
    priority: str
    assignee: int | None
    items: list[ItemOut]
    completed_at: date | None
    created_at: datetime


# ---------- Income ----------
class IncomeIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    cat: Category
    amount: float = Field(gt=0)
    month: str = Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$", examples=["2026-11"])


class IncomeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    cat: str
    amount: float
    month: str
    created_at: datetime


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
    counts: dict[str, int]

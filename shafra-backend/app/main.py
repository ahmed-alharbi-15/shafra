from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import inspect, select, text

from .config import get_settings
from .database import Base, SessionLocal, engine
from .models import SCHEMA_VERSION, AppMeta, User
from .routers import auth, income, people, tasks, works
from .security import hash_password

settings = get_settings()

OLD_TABLES = ["task_items", "tasks", "payments", "income", "works", "users", "app_meta"]


def migrate_schema() -> None:
    """لو قاعدة البيانات فيها جداول من نسخة قديمة، يمسحها وينشئها من جديد (مرة وحدة بس)"""
    insp = inspect(engine)
    tables = set(insp.get_table_names())
    current = None
    if "app_meta" in tables:
        with engine.connect() as conn:
            current = conn.execute(text("SELECT value FROM app_meta WHERE key = 'schema_version'")).scalar()
    if tables & set(OLD_TABLES) and current != SCHEMA_VERSION:
        with engine.begin() as conn:
            for t in OLD_TABLES:
                if t in tables:
                    conn.execute(text(f'DROP TABLE IF EXISTS "{t}" CASCADE' if engine.dialect.name == "postgresql" else f'DROP TABLE IF EXISTS "{t}"'))
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        row = db.get(AppMeta, "schema_version")
        if row is None:
            db.add(AppMeta(key="schema_version", value=SCHEMA_VERSION))
        else:
            row.value = SCHEMA_VERSION
        db.commit()


def seed_owners() -> None:
    """ينشئ حسابات الـ Owner من متغيرات البيئة، ويتأكد إن رتبتهم Owner"""
    with SessionLocal() as db:
        for email, password, name in settings.owners:
            user = db.scalar(select(User).where(User.email == email))
            if user is None:
                db.add(User(name=name, email=email, hashed_password=hash_password(password), role="owner"))
            elif user.role != "owner":
                user.role = "owner"
        db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    migrate_schema()
    seed_owners()
    yield


app = FastAPI(title=settings.APP_NAME, version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_error(_: Request, exc: RequestValidationError):
    """يرجع أول خطأ كرسالة عربية واضحة بدل قائمة إنجليزي"""
    first = exc.errors()[0] if exc.errors() else {}
    field = str(first.get("loc", ["", ""])[-1])
    msg = str(first.get("msg", ""))
    if msg.startswith("Value error, "):
        detail = msg.replace("Value error, ", "")
    else:
        detail = {
            "email": "الإيميل مو صحيح.",
            "newEmail": "الإيميل مو صحيح.",
            "password": "كلمة المرور لازم 8 خانات أو أكثر.",
            "newPassword": "كلمة المرور الجديدة لازم 8 خانات أو أكثر.",
            "name": "اكتب اسمك.",
            "amount": "اكتب مبلغ أكبر من صفر.",
            "title": "اكتب عنوان المهمة.",
        }.get(field, "البيانات المرسلة مو صحيحة.")
    return JSONResponse(status_code=422, content={"detail": detail, "field": field})


app.include_router(auth.router)
app.include_router(people.router)
app.include_router(tasks.router)
app.include_router(income.router)
app.include_router(works.router)


@app.get("/", tags=["Health"])
def root():
    return {"name": settings.APP_NAME, "status": "ok", "version": "2", "docs": "/docs"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from .config import get_settings
from .database import Base, SessionLocal, engine
from .models import User
from .routers import auth, payments, tasks, team, works
from .security import hash_password

settings = get_settings()


def create_first_admin() -> None:
    """ينشئ أول أدمن من متغيرات البيئة إذا ما كان موجود"""
    if not (settings.ADMIN_EMAIL and settings.ADMIN_PASSWORD):
        return
    email = settings.ADMIN_EMAIL.lower()
    with SessionLocal() as db:
        if db.scalar(select(User).where(User.email == email)):
            return
        db.add(
            User(
                name=settings.ADMIN_NAME,
                email=email,
                hashed_password=hash_password(settings.ADMIN_PASSWORD),
                is_admin=True,
                role="Frontend Developer",
                title="شريك مؤسس — مطوّر واجهات",
            )
        )
        db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ينشئ الجداول تلقائيًا أول ما يشتغل السيرفر
    Base.metadata.create_all(bind=engine)
    create_first_admin()
    yield


app = FastAPI(title=settings.APP_NAME, version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(team.router)
app.include_router(tasks.router)
app.include_router(payments.router)
app.include_router(works.router)


@app.get("/", tags=["Health"])
def root():
    return {"name": settings.APP_NAME, "status": "ok", "docs": "/docs"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}

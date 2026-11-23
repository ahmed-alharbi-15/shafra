import json
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "Shafra API"
    # Render يعطيك DATABASE_URL لما تربط قاعدة البيانات
    DATABASE_URL: str = "sqlite:///./shafra.db"
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # يوم
    REMEMBER_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # «تذكرني»: 30 يوم
    # روابط الموقع المسموح لها، مفصولة بفاصلة
    CORS_ORIGINS: str = "http://localhost:5500,http://127.0.0.1:5500"

    # الـ Owner الأول (أحمد) — ينشأ تلقائي أول ما يشتغل السيرفر
    ADMIN_EMAIL: str = ""
    ADMIN_PASSWORD: str = ""
    ADMIN_NAME: str = "أحمد الحربي"

    # الـ Owner الثاني (نايف) — اختياري
    OWNER2_EMAIL: str = ""
    OWNER2_PASSWORD: str = ""
    OWNER2_NAME: str = "نايف الحربي"

    @property
    def database_url(self) -> str:
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip().rstrip("/") for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def owner_profiles(self) -> dict[str, dict]:
        """الـ Owners المعروفين (owners.json): الإيميل والاسم بدون باسورد. الباسورد ينحط بسكربت set_owner_password."""
        try:
            data = json.loads((Path(__file__).resolve().parent.parent / "owners.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}
        return {str(o["email"]).strip().lower(): o for o in data if isinstance(o, dict) and o.get("email")}

    def is_owner_email(self, email: str) -> bool:
        e = email.strip().lower()
        return e in self.owner_profiles or e in {x[0] for x in self.owners}

    @property
    def owners(self) -> list[tuple[str, str, str]]:
        out = []
        for email, pw, name in (
            (self.ADMIN_EMAIL, self.ADMIN_PASSWORD, self.ADMIN_NAME),
            (self.OWNER2_EMAIL, self.OWNER2_PASSWORD, self.OWNER2_NAME),
        ):
            if email.strip() and pw:
                out.append((email.strip().lower(), pw, name.strip() or email))
        return out


@lru_cache
def get_settings() -> Settings:
    return Settings()

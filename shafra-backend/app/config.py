from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "Shafra API"
    # Render يعطيك DATABASE_URL تلقائيًا لما تربط قاعدة البيانات
    DATABASE_URL: str = "sqlite:///./shafra.db"
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # يوم
    REMEMBER_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # «تذكرني»: 30 يوم
    # روابط الفرونت اند المسموح لها، مفصولة بفاصلة
    CORS_ORIGINS: str = "http://localhost:5500,http://127.0.0.1:5500,http://localhost:3000"

    # أول أدمن: ينشأ تلقائيًا أول ما يشتغل السيرفر إذا ما كان موجود
    ADMIN_EMAIL: str = ""
    ADMIN_PASSWORD: str = ""
    ADMIN_NAME: str = "أحمد الحربي"

    @property
    def database_url(self) -> str:
        url = self.DATABASE_URL
        # Render يعطي postgres:// أو postgresql:// ، نحوله لدرايفر psycopg 3
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip().rstrip("/") for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    # ... các dòng đang có ...
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = "admin123"

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./data.db"
    JWT_SECRET: str = "change_me"  # change in production
    SESSION_TTL_MINUTES: int = 120
    HEARTBEAT_TIMEOUT_SEC: int = 120
    TEMP_LOCK_MINUTES: int = 30
    OFFLINE_TTL_MINUTES: int = 0  # 0 disables offline tokens

settings = Settings()

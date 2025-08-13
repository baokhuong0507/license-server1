# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Đọc DATABASE_URL do Render cung cấp
    DATABASE_URL: str
    
    # Các biến khác giữ nguyên
    ADMIN_SECRET_KEY: str = "default_secret_key"

    class Config:
        env_file = ".env"

settings = Settings()

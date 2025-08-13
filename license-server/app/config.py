# app/config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Đường dẫn đến tệp CSDL. Render sẽ cung cấp thư mục /app/data
    DATABASE_URL: str = "sqlite:///./data/database.db"
    
    # Secret key để bảo vệ các API quản lý. Hãy đổi nó trên Render.
    ADMIN_SECRET_KEY: str = os.getenv("ADMIN_SECRET_KEY", "CHANGE_THIS_SECRET_KEY")

    class Config:
        env_file = ".env" # Cho phép dùng file .env khi chạy ở local

settings = Settings()

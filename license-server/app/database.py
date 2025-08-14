# app/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Tải biến môi trường từ file .env (dành cho lập trình ở máy cá nhân)
load_dotenv()

# Lấy chuỗi kết nối từ biến môi trường của Render
DATABASE_URL = os.getenv("DATABASE_URL")

# Kiểm tra nếu DATABASE_URL không được thiết lập
if not DATABASE_URL:
    raise ValueError("No DATABASE_URL environment variable set. Please configure it on Render.")

# Tạo engine kết nối với database
# connect_args chỉ cần thiết cho SQLite, chúng ta có thể bỏ nó đi khi dùng PostgreSQL
engine = create_engine(DATABASE_URL)

# Tạo một lớp Session để tương tác với DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class cho các lớp model
Base = declarative_base()

def get_db():
    """
    Hàm dependency của FastAPI để cung cấp một session database cho mỗi request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
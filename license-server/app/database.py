# app/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Lấy chuỗi kết nối từ biến môi trường của Render
# Đây là cách làm đúng và an toàn
DATABASE_URL = os.getenv("DATABASE_URL")

# Nếu biến môi trường không được thiết lập, ứng dụng sẽ không thể chạy
if not DATABASE_URL:
    raise ValueError("FATAL: DATABASE_URL environment variable is not set.")

# Tạo engine kết nối
engine = create_engine(DATABASE_URL)

# Tạo một lớp Session để tương tác với DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class cho các lớp model
Base = declarative_base()

def get_db():
    """
    Hàm dependency của FastAPI để cung cấp một session database cho mỗi request.
    Đảm bảo session luôn được đóng sau khi request hoàn tất.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
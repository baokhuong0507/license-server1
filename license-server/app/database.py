# app/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Lấy chuỗi kết nối từ biến môi trường của Render
DATABASE_URL = os.getenv("DATABASE_URL")

# Nếu biến này không tồn tại, in ra lỗi và dừng lại
if not DATABASE_URL:
    print("="*80)
    print("FATAL ERROR: Environment variable 'DATABASE_URL' is not set.")
    print("Please go to your service's 'Environment' tab on Render and add it.")
    print("="*80)
    # Dừng chương trình ở đây để tránh các lỗi không mong muốn
    # raise ValueError("DATABASE_URL is not set") # Dùng print thay vì raise để đảm bảo log được ghi lại
    engine = None
else:
    # Nếu biến tồn tại, tạo engine
    engine = create_engine(DATABASE_URL)

# Tạo một lớp Session để tương tác với DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class cho các lớp model
Base = declarative_base()

def get_db():
    """Hàm dependency của FastAPI để cung cấp một session database."""
    if engine is None:
        raise Exception("Database engine is not initialized due to missing DATABASE_URL.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_database_connection():
    """
    Hàm này sẽ cố gắng kết nối tới DB và báo cáo kết quả.
    Đây là hàm quan trọng nhất để gỡ lỗi.
    """
    if engine is None:
        return False # Đã báo lỗi ở trên
    try:
        print("STEP 1: Attempting to connect to the database...")
        connection = engine.connect()
        print("STEP 1: SUCCESS - Database connection established.")
        connection.close()
        print("STEP 1: SUCCESS - Database connection closed.")
        return True
    except Exception as e:
        print("="*80)
        print("STEP 1: FATAL ERROR - DATABASE CONNECTION FAILED.")
        print(f"Error details: {e}")
        print("This is likely due to an incorrect DATABASE_URL value in your Environment Variables.")
        print("="*80)
        return False
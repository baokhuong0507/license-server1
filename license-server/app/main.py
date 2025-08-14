# app/main.py

import sys
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from sqlalchemy import text

# Import các thành phần cần thiết
from .database import engine, get_db
from . import models
from .routers import admin_web, admin_api, client_api

# --- PHẦN MÃ TẠM THỜI ĐỂ XÓA BẢNG ---
# Mã này sẽ chạy một lần duy nhất trong lần deploy này.
print("="*80)
print("RUNNING ONE-TIME DATABASE CLEANUP SCRIPT...")
try:
    with engine.connect() as connection:
        print("Connecting to the database to drop the old 'keys' table...")
        # Dùng `IF EXISTS` để lệnh không báo lỗi nếu bảng đã bị xóa
        connection.execute(text("DROP TABLE IF EXISTS keys;"))
        # Quan trọng: commit thay đổi
        connection.commit()
        print("SUCCESS: Old 'keys' table has been dropped.")
except Exception as e:
    print(f"ERROR: Could not drop the table. Reason: {e}")
    # Nếu không xóa được thì dừng lại để tránh lỗi
    sys.exit(1)
print("="*80)
# --- KẾT THÚC PHẦN MÃ TẠM THỜI ---


# Lệnh này sẽ tạo lại bảng mới với cấu trúc chính xác
try:
    print("Creating new 'keys' table with the correct schema...")
    models.Base.metadata.create_all(bind=engine)
    print("SUCCESS: New 'keys' table created.")
except Exception as e:
    print(f"FATAL: Could not create new tables. Error: {e}")
    sys.exit(1)


# Khởi tạo ứng dụng FastAPI như bình thường
app = FastAPI(title="License Server")
app.include_router(admin_web.router)
app.include_router(admin_api.router)
app.include_router(client_api.router)

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/admin/keys")

print("Application startup complete.")
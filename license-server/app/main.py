# app/main.py

import sys
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

# Import các thành phần cần thiết
from .database import check_database_connection, engine
from . import models
from .routers import admin_web, admin_api, client_api


# --- KIỂM TRA KẾT NỐI DATABASE ---
# Đây là việc đầu tiên ứng dụng làm. Nếu thất bại, nó sẽ dừng lại.
if not check_database_connection():
    sys.exit(1) # Lệnh này sẽ dừng ứng dụng một cách an toàn


# --- TẠO BẢNG DATABASE ---
# Chỉ chạy sau khi kết nối thành công
try:
    print("STEP 2: Attempting to create database tables...")
    models.Base.metadata.create_all(bind=engine)
    print("STEP 2: SUCCESS - Database tables are ready.")
except Exception as e:
    print("="*80)
    print(f"STEP 2: FATAL ERROR - Could not create database tables.")
    print(f"Error details: {e}")
    print("="*80)
    sys.exit(1)


# Khởi tạo ứng dụng FastAPI
print("STEP 3: Initializing FastAPI application...")
app = FastAPI(title="License Server")

# Gắn các router vào ứng dụng
app.include_router(admin_web.router)
app.include_router(admin_api.router)
app.include_router(client_api.router)
print("STEP 3: SUCCESS - FastAPI routers included.")


@app.get("/", include_in_schema=False)
async def root():
    """Khi truy cập trang chủ, chuyển hướng đến trang quản lý key."""
    return RedirectResponse(url="/admin/keys")

print("STEP 4: Application startup complete. Server is ready.")
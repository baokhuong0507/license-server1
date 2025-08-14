# app/main.py

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from . import models
from .database import engine
from .routers import admin_web, admin_api, client_api

# Cố gắng tạo các bảng trong database khi ứng dụng khởi động
# Nếu có lỗi (ví dụ: không kết nối được DB), ứng dụng sẽ báo lỗi rõ ràng
try:
    models.Base.metadata.create_all(bind=engine)
    print("Database tables created or already exist.")
except Exception as e:
    # In ra lỗi nếu không thể tạo bảng để dễ gỡ lỗi trên Render
    print(f"FATAL: Could not connect to the database and create tables. Error: {e}")

# Khởi tạo ứng dụng FastAPI
app = FastAPI(title="License Server")

# Gắn các router (bộ định tuyến) vào ứng dụng chính
app.include_router(admin_web.router)
app.include_router(admin_api.router)
app.include_router(client_api.router)


@app.get("/", include_in_schema=False)
async def root():
    # Khi người dùng truy cập vào trang chủ, tự động chuyển hướng họ đến /admin/keys.
    # Lỗi cú pháp nằm ở docstring của hàm này trong phiên bản trước.
    return RedirectResponse(url="/admin/keys")
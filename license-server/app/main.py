# app/main.py

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from . import models
from .database import engine
from .routers import admin_web, admin_api, client_api

# Lệnh này sẽ tạo các bảng trong database dựa trên models.py
# Nó chỉ chạy một lần khi ứng dụng khởi động.
models.Base.metadata.create_all(bind=engine)

# Khởi tạo ứng dụng FastAPI
app = FastAPI(title="License Server")

# Gắn các router từ các tệp khác vào ứng dụng chính
app.include_router(admin_web.router)
app.include_router(admin_api.router)
app.include_router(client_api.router)

# Gắn thư mục static để phục vụ các file CSS, JS (nếu có)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", include_in_schema=False)
async def root():
    """
    Khi người dùng truy cập vào trang chủ (ví dụ: https://license-server-ef3k.onrender.com/),
    tự động chuyển hướng họ đến trang quản lý key.
    """
    return RedirectResponse(url="/admin/keys")
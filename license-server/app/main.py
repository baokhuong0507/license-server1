# app/main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.routers import client_api, admin_api, admin_web # THÊM admin_web
from app.services import keys as key_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Khởi tạo cơ sở dữ liệu...")
    key_service.init_db()
    yield
    print("Server shutting down.")

app = FastAPI(title="License Server", lifespan=lifespan)

# THÊM DÒNG NÀY ĐỂ DÙNG CSS (NẾU CÓ)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Thêm các router vào ứng dụng
app.include_router(client_api.router, prefix="/api/client", tags=["Client API"])
app.include_router(admin_api.router, prefix="/api/admin", tags=["Admin API"])
app.include_router(admin_web.router, tags=["Admin Web Interface"]) # THÊM DÒNG NÀY

@app.get("/", tags=["Root"])
def read_root():
    return RedirectResponse(url="/admin/dashboard")

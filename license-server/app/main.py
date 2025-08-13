# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import client_api, admin_api # Import cả hai router
from app.services import keys as key_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Chạy một lần khi server khởi động
    print("Khởi tạo cơ sở dữ liệu...")
    key_service.init_db()
    yield
    # Chạy khi server tắt (không quan trọng lắm trên Render)
    print("Server shutting down.")

app = FastAPI(title="License Server", lifespan=lifespan)

# Thêm các router vào ứng dụng
app.include_router(client_api.router, prefix="/api/client", tags=["Client Activation"])
app.include_router(admin_api.router, prefix="/api/admin", tags=["Admin Management"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "License Server is running."}

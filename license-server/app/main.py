# app/main.py
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.routers import client_api, admin_api, admin_web
from app.database import engine
from app import models

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Ứng dụng khởi động. Tạo các bảng CSDL...")
    # Lệnh này sẽ tạo bảng 'keys' nếu nó chưa tồn tại
    models.Base.metadata.create_all(bind=engine)
    yield
    print("Ứng dụng kết thúc.")

app = FastAPI(title="License Server", lifespan=lifespan)

# Phần còn lại của tệp giữ nguyên...
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(client_api.router, prefix="/api/client", tags=["Client API"])
app.include_router(admin_api.router, prefix="/api/admin", tags=["Admin API"])
app.include_router(admin_web.router, tags=["Admin Web Interface"])

@app.get("/", include_in_schema=False)
def read_root():
    return Response(status_code=302, headers={"Location": "/admin/dashboard"})

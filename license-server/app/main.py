from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.routers import client_api, admin_api, admin_web
from app.database import engine
from app import models

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Ứng dụng khởi động. Tạo các bảng CSDL...")
    # Chỉ tạo bảng nếu chưa tồn tại.
    models.Base.metadata.create_all(bind=engine)
    models.Base.metadata.drop_all(bind=engine)
    yield
    print("Ứng dụng kết thúc.")
    
app = FastAPI(title="License Server", lifespan=lifespan)

# Mount thư mục static để phục vụ các tệp CSS, JS (nếu có)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Bao gồm các router vào ứng dụng chính
app.include_router(client_api.router, prefix="/api/client", tags=["Client API"])
app.include_router(admin_api.router, prefix="/api/admin", tags=["Admin API"])
app.include_router(admin_web.router, tags=["Admin Web Interface"])

# Chuyển hướng trang gốc đến trang dashboard
@app.get("/", include_in_schema=False)
def read_root():
    return Response(status_code=302, headers={"Location": "/admin/dashboard"})

# app/main.py

from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler

from app.routers import client_api, admin_api, admin_web
from app.database import engine, SessionLocal
from app import models
from app.services import keys as key_service

# --- KHỞI TẠO TÁC VỤ NỀN ---
scheduler = BackgroundScheduler()

def expire_keys_job():
    """Công việc được scheduler gọi định kỳ."""
    print("Bắt đầu tác vụ nền: Quét key hết hạn...")
    # Tạo một phiên CSDL riêng cho tác vụ nền
    db = SessionLocal()
    try:
        # Gọi hàm service để thực hiện công việc
        count = key_service.sweep_expired_keys(db)
        print(f"Tác vụ nền hoàn tất: {count} key được cập nhật.")
    finally:
        # Luôn đóng phiên CSDL sau khi hoàn thành
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Ứng dụng khởi động...")
    # Đảm bảo các bảng CSDL tồn tại
    models.Base.metadata.create_all(bind=engine)
    
    # Thêm công việc vào scheduler và khởi động nó
    # Chạy mỗi giờ một lần (bạn có thể thay đổi 'hours=1' thành 'minutes=30' nếu muốn)
    scheduler.add_job(expire_keys_job, 'interval', hours=1)
    scheduler.start()
    
    yield
    
    print("Ứng dụng kết thúc. Dừng scheduler...")
    scheduler.shutdown()

app = FastAPI(title="License Server", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(client_api.router, prefix="/api/client", tags=["Client API"])
app.include_router(admin_api.router, prefix="/api/admin", tags=["Admin API"])
app.include_router(admin_web.router, tags=["Admin Web Interface"])

@app.get("/", include_in_schema=False)
def read_root():
    return Response(status_code=302, headers={"Location": "/admin/dashboard"})
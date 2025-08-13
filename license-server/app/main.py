# app/main.py (chỉ trích các phần cần thêm)

from .routers.admin_api import router as admin_api_router  # <--- THÊM DÒNG NÀY

app = FastAPI(title="License Server")

# ... (các cấu hình/mount static cũ của bạn)

app.include_router(admin_api_router)  # <--- THÊM DÒNG NÀY

# (khuyến nghị) route gốc để health check:
@app.get("/")
def root():
    return {"ok": True, "service": "license-server"}

# app/main.py
# BẢN TỐI GIẢN, AN TOÀN KHI DEPLOY TRÊN RENDER

import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from .routers.client_api import router as client_api_router
from .routers.admin_api import router as admin_api_router
app = FastAPI(title="License Server")

# Mount static nếu thư mục tồn tại (tránh lỗi Directory does not exist)
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Bật CORS cho frontend/admin gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(client_api_router)
app.include_router(admin_api_router)
# Include các router (có gì include cái đó, thiếu cũng không làm crash)
try:
    from .routers.client_api import router as client_api_router
    app.include_router(client_api_router)
except Exception:
    pass

try:
    from .routers.admin_web import router as admin_web_router
    app.include_router(admin_web_router)
except Exception:
    pass

try:
    from .routers.admin_api import router as admin_api_router  # file bạn sẽ thêm ở bước 2
    app.include_router(admin_api_router)
except Exception:
    pass

# Health check
@app.get("/")
def root():
    return {"ok": True, "service": "license-server"}

# app/main.py

import sys
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from sqlalchemy import text

# Import các thành phần cần thiết
from .database import engine
from . import models
from .routers import admin_web, admin_api, client_api

# --- PHẦN MÃ DỌN DẸP DATABASE TRIỆT ĐỂ ---
print("="*80)
print("RUNNING FINAL DATABASE CLEANUP SCRIPT...")
try:
    with engine.connect() as connection:
        print("Connecting to the database to drop old types and tables...")
        # Lệnh này sẽ xóa kiểu dữ liệu 'keystatus' và BẤT KỲ THỨ GÌ phụ thuộc vào nó (như bảng 'keys')
        # Đây là cách làm triệt để nhất.
        connection.execute(text("DROP TYPE IF EXISTS keystatus CASCADE;"))
        connection.commit()
        print("SUCCESS: Old 'keystatus' type and dependent objects (like 'keys' table) have been dropped.")
except Exception as e:
    print(f"ERROR: Could not perform cleanup. Reason: {e}")
    sys.exit(1)
print("="*80)
# --- KẾT THÚC PHẦN MÃ DỌN DẸP ---


# Lệnh này sẽ tạo lại TẤT CẢ MỌI THỨ từ đầu một cách sạch sẽ
try:
    print("Re-creating all tables and types from scratch with the correct schema...")
    models.Base.metadata.create_all(bind=engine)
    print("SUCCESS: All tables and types have been recreated correctly.")
except Exception as e:
    print(f"FATAL: Could not create new tables. Error: {e}")
    sys.exit(1)


# Khởi tạo ứng dụng FastAPI như bình thường
app = FastAPI(title="License Server")
app.include_router(admin_web.router)
app.include_router(admin_api.router)
app.include_router(client_api.router)

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/admin/keys")

print("Application startup complete.")
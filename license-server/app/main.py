# app/main.py

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from . import models
from .database import engine
from .routers import admin_web, admin_api, client_api

# Lệnh này sẽ tạo các bảng trong database nếu chúng chưa tồn tại
# Đây là một bước quan trọng để đảm bảo DB luôn sẵn sàng
try:
    models.Base.metadata.create_all(bind=engine)
except Exception as e:
    # In ra lỗi nếu không thể tạo bảng để dễ gỡ lỗi trên Render
    print(f"Error creating database tables: {e}")

# Khởi tạo ứng dụng
app = FastAPI(title="License Server")

# Gắn các router vào ứng dụng
app.include_router(admin_web.router)
app.include_router(admin_api.router)
app.include_router(client_api.router)

@app.get("/", include_in_schema=False)
async def root_redirect():
    """
    Khi truy cập trang gốc, tự động chuyển hướng đến trang quản lý.
    """
    return RedirectResponse(url="/admin/keys")```

##### **3. Tệp `app/routers/admin_web.py`**

Tệp router cho giao diện web.

**Đường dẫn:** `app/routers/admin_web.py`
**Nội dung mới:**
```python
# app/routers/admin_web.py

from __future__ import annotations
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..database import get_db
from ..services import keys as keys_service

router = APIRouter(prefix="/admin", tags=["Admin Web Interface"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/keys", response_class=HTMLResponse)
async def keys_page(request: Request, db: Session = Depends(get_db)):
    """Trang chính hiển thị bảng quản lý key."""
    try:
        all_keys = keys_service.get_all_keys(db)
        return templates.TemplateResponse("keys.html", {"request": request, "keys": all_keys})
    except Exception as e:
        # Nếu có lỗi xảy ra, trả về một trang báo lỗi rõ ràng
        print(f"An error occurred in keys_page: {e}")
        return templates.TemplateResponse("error.html", {"request": request, "detail": str(e)}, status_code=500)

@router.post("/keys/create", response_class=HTMLResponse)
async def htmx_create_key(request: Request, days_valid: int = Form(None), db: Session = Depends(get_db)):
    new_key = keys_service.create_new_key(db, days_valid)
    return templates.TemplateResponse("partials/keys_table_rows.html", {"request": request, "key": new_key})

@router.post("/keys/{key_id}/activate", response_class=HTMLResponse)
async def htmx_activate_key(request: Request, key_id: int, db: Session = Depends(get_db)):
    updated_key = keys_service.activate_key_by_id(db, key_id=key_id)
    if not updated_key:
        raise HTTPException(status_code=400, detail="Key cannot be activated.")
    return templates.TemplateResponse("partials/keys_table_rows.html", {"request": request, "key": updated_key})

@router.delete("/keys/{key_id}", response_class=HTMLResponse)
async def htmx_delete_key(key_id: int, db: Session = Depends(get_db)):
    success = keys_service.delete_key_by_id(db, key_id=key_id)
    if not success:
        raise HTTPException(status_code=404, detail="Key not found.")
    return HTMLResponse(content="", status_code=200)
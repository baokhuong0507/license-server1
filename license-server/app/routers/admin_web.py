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
        # Nếu có lỗi ở tầng service hoặc DB, hiển thị lỗi rõ ràng
        print(f"An error occurred in keys_page: {e}")
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")

@router.post("/keys/create", response_class=HTMLResponse)
async def htmx_create_key(request: Request, days_valid: int = Form(None), db: Session = Depends(get_db)):
    """Tạo key mới và trả về HTML cho một hàng mới."""
    new_key = keys_service.create_new_key(db, days_valid)
    return templates.TemplateResponse("partials/keys_table_rows.html", {"request": request, "key": new_key})

@router.post("/keys/{key_id}/activate", response_class=HTMLResponse)
async def htmx_activate_key(request: Request, key_id: int, db: Session = Depends(get_db)):
    """Kích hoạt key và trả về HTML của hàng đã được cập nhật."""
    updated_key = keys_service.activate_key_by_id(db, key_id=key_id)
    if not updated_key:
        # Nếu key đã được dùng hoặc không tồn tại, không thể kích hoạt
        raise HTTPException(status_code=400, detail="Key already used or not found.")
    return templates.TemplateResponse("partials/keys_table_rows.html", {"request": request, "key": updated_key})

@router.delete("/keys/{key_id}", response_class=HTMLResponse)
async def htmx_delete_key(key_id: int, db: Session = Depends(get_db)):
    """Xóa một key và trả về response trống để HTMX xóa hàng."""
    success = keys_service.delete_key_by_id(db, key_id=key_id)
    if not success:
        raise HTTPException(status_code=404, detail="Key not found to delete.")
    # Lỗi cú pháp nằm ở đây trong phiên bản trước. Phiên bản này đã đúng.
    return HTMLResponse(content="", status_code=200)
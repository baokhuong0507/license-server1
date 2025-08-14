# app/routers/admin_web.py

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..database import get_db
from ..services import keys as keys_service

router = APIRouter(
    prefix="/admin",
    tags=["Admin Web Interface"]
)
templates = Jinja2Templates(directory="app/templates")

@router.get("/keys", response_class=HTMLResponse)
async def keys_page(request: Request, db: Session = Depends(get_db)):
    """
    Route để hiển thị trang quản lý key.
    """
    # Sử dụng hàm service đã sửa để đảm bảo trạng thái key luôn đúng
    all_keys = keys_service.get_all_keys(db)
    return templates.TemplateResponse("keys.html", {"request": request, "keys": all_keys})

@router.post("/keys/create", response_class=HTMLResponse)
async def htmx_create_key(request: Request, days_valid: int = Form(None), db: Session = Depends(get_db)):
    """
    Route để tạo key mới và trả về HTML cho hàng mới (HTMX)
    """
    new_key = keys_service.create_new_key(db, days_valid)
    return templates.TemplateResponse("partials/keys_table_rows.html", {"request": request, "key": new_key})

@router.post("/keys/{key_id}/activate", response_class=HTMLResponse)
async def htmx_activate_key(request: Request, key_id: int, db: Session = Depends(get_db)):
    """
    Route để kích hoạt key và trả về HTML của hàng đã được cập nhật.
    --> Đây là giải pháp cho vấn đề #2.
    """
    # Gọi service để kích hoạt key
    updated_key = keys_service.activate_key_by_id(db, key_id=key_id)

    # Render và trả về HTML của chỉ MỘT hàng trong bảng
    return templates.TemplateResponse(
        "partials/keys_table_rows.html", 
        {"request": request, "key": updated_key}
    )

@router.delete("/keys/{key_id}", response_class=HTMLResponse)
async def htmx_delete_key(request: Request, key_id: int, db: Session = Depends(get_db)):
    """
    Route để xóa key và trả về một response trống để HTMX xóa hàng khỏi giao diện.
    """
    key_to_delete = db.query(keys_service.models.Key).filter(keys_service.models.Key.id == key_id).first()
    if key_to_delete:
        db.delete(key_to_delete)
        db.commit()
    # Trả về chuỗi rỗng để HTMX loại bỏ thẻ <tr>
    return HTMLResponse("")
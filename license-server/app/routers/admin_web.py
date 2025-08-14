# app/routers/admin_web.py

from __future__ import annotations
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..database import get_db
from ..services import keys as keys_service
from .. import models

router = APIRouter(prefix="/admin", tags=["Admin Web Interface"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/keys", response_class=HTMLResponse)
async def keys_page(request: Request, db: Session = Depends(get_db)):
    all_keys = keys_service.get_all_keys(db)
    return templates.TemplateResponse("keys.html", {"request": request, "keys": all_keys})

# --- ROUTE TÌM KIẾM MỚI ---
@router.post("/keys/search", response_class=HTMLResponse)
async def htmx_search_keys(request: Request, search: str = Form(""), db: Session = Depends(get_db)):
    """
    Xử lý yêu cầu tìm kiếm từ HTMX và trả về các hàng của bảng.
    """
    # Lấy danh sách key đầy đủ để render partial
    # (Vì partial keys_table_rows.html yêu cầu vòng lặp)
    if not search.strip():
        # Nếu ô tìm kiếm trống, trả về tất cả key
        keys = keys_service.get_all_keys(db)
    else:
        search_term = f"%{search.strip()}%"
        query = db.query(models.Key).filter(
            or_(
                models.Key.key.ilike(search_term),
                # Chuyển đổi Enum sang text để so sánh
                models.Key.status.as_string().ilike(search_term)
            )
        ).order_by(models.Key.id.desc())
        keys = query.all()

    # Tạo một list rỗng để chứa HTML của từng hàng
    html_rows = []
    for key in keys:
        # Render tệp partial cho mỗi key và thêm vào list
        html_rows.append(templates.get_template("partials/keys_table_rows.html").render({"request": request, "key": key}))
    
    # Nối tất cả các hàng HTML lại và trả về
    return HTMLResponse(content="".join(html_rows))


@router.post("/keys/create", response_class=HTMLResponse)
async def htmx_create_key(request: Request, days_valid: int = Form(None), db: Session = Depends(get_db)):
    new_key = keys_service.create_new_key(db, days_valid)
    # Trả về HTML cho chỉ một hàng mới
    return templates.TemplateResponse("partials/keys_table_rows.html", {"request": request, "key": new_key})


@router.post("/keys/{key_id}/activate", response_class=HTMLResponse)
async def htmx_activate_key(request: Request, key_id: int, db: Session = Depends(get_db)):
    updated_key = keys_service.activate_key_by_id(db, key_id=key_id)
    if not updated_key:
        raise HTTPException(status_code=400, detail="Key already used or not found.")
    return templates.TemplateResponse("partials/keys_table_rows.html", {"request": request, "key": updated_key})

@router.delete("/keys/{key_id}", response_class=HTMLResponse)
async def htmx_delete_key(key_id: int, db: Session = Depends(get_db)):
    success = keys_service.delete_key_by_id(db, key_id=key_id)
    if not success:
        raise HTTPException(status_code=404, detail="Key not found to delete.")
    return HTMLResponse(content="", status_code=200)
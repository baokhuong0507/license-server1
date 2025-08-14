# app/routers/admin_web.py

from __future__ import annotations # <--- Thêm dòng này vào đầu
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
    all_keys = keys_service.get_all_keys(db)
    return templates.TemplateResponse("keys.html", {"request": request, "keys": all_keys})

@router.post("/keys/create", response_class=HTMLResponse)
async def htmx_create_key(request: Request, days_valid: int = Form(None), db: Session = Depends(get_db)):
    new_key = keys_service.create_new_key(db, days_valid)
    return templates.TemplateResponse("partials/keys_table_rows.html", {"request": request, "key": new_key})

@router.post("/keys/{key_id}/activate", response_class=HTMLResponse)
async def htmx_activate_key(request: Request, key_id: int, db: Session = Depends(get_db)):
    updated_key = keys_service.activate_key_by_id(db, key_id=key_id)
    return templates.TemplateResponse("partials/keys_table_rows.html", {"request": request, "key": updated_key})

@router.delete("/keys/{key_id}", response_class=HTMLResponse)
async def htmx_delete_key(request: Request, key_id: int, db: Session = Depends(get_db)):
    key_to_delete = db.query(keys_service.models.Key).filter(keys_service.models.Key.id == key_id).first()
    if key_to_delete:
        db.delete(key_to_delete)
        db.commit()
    return HTMLResponse("")
# app/routers/admin_api.py

from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.services import keys as key_service
from app.database import get_db
from app.auth import get_current_user

router = APIRouter()

# --- Pydantic Models ---
class KeyActionRequest(BaseModel):
    key_value: str

class AddKeyRequest(BaseModel):
    key_value: str
    program_name: str = "Default"
    expiration_date_str: Optional[str] = None

class BulkAddRequest(BaseModel):
    quantity: int = 10
    length: int = 20
    program_name: str = "Default"
    expiration_date_str: Optional[str] = None

# --- Admin API Endpoints ---
@router.get("/keys/all", summary="Lấy danh sách tất cả keys (JSON)")
async def get_all_keys_json(user_logged_in: bool = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user_logged_in:
        raise HTTPException(status_code=401, detail="Unauthorized")
    all_keys = key_service.get_all_keys(db, filters={})
    return all_keys

@router.post("/keys/add", summary="Thêm một key mới (API)")
async def add_new_key_api(request: AddKeyRequest, user_logged_in: bool = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user_logged_in:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if key_service.get_key_by_value(db, request.key_value):
        raise HTTPException(status_code=409, detail=f"Key '{request.key_value}' đã tồn tại.")
    exp_date_obj = date.fromisoformat(request.expiration_date_str) if request.expiration_date_str else None
    key_service.create_key(db, request.key_value, request.program_name, exp_date_obj)
    return {"status": "success"}

@router.post("/keys/bulk-add", summary="Tạo key hàng loạt (API)")
async def bulk_add_keys_api(request: BulkAddRequest, user_logged_in: bool = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user_logged_in:
        raise HTTPException(status_code=401, detail="Unauthorized")
    exp_date_obj = date.fromisoformat(request.expiration_date_str) if request.expiration_date_str else None
    key_service.bulk_create_keys(db, request.quantity, request.length, request.program_name, exp_date_obj)
    return {"status": "success"}

@router.post("/keys/delete", summary="Xóa một key (API)")
async def delete_key_api(request: KeyActionRequest, user_logged_in: bool = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user_logged_in:
        raise HTTPException(status_code=401, detail="Unauthorized")
    success = key_service.delete_key(db, request.key_value)
    if not success:
        raise HTTPException(status_code=404, detail="Key không tìm thấy để xóa.")
    return {"status": "success"}

@router.post("/keys/lock", summary="Khóa một key (API)")
async def lock_key_api(request: KeyActionRequest, user_logged_in: bool = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user_logged_in:
        raise HTTPException(status_code=401, detail="Unauthorized")
    key_service.update_key_status(db, request.key_value, "revoked")
    return {"status": "success"}

@router.post("/keys/unlock", summary="Mở khóa một key (API)")
async def unlock_key_api(request: KeyActionRequest, user_logged_in: bool = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user_logged_in:
        raise HTTPException(status_code=401, detail="Unauthorized")
    key_service.update_key_status(db, request.key_value, "active")
    return {"status": "success"}
# app/routers/admin_api.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.services import keys as key_service
from app.database import get_db
from app.auth import get_current_user

router = APIRouter()

# --- Pydantic Models ---
class KeyRequest(BaseModel):
    key: str

# --- Admin Endpoints ---
@router.post("/keys/add", summary="Thêm một key mới (API)")
async def add_new_key_api(
    request: KeyRequest, 
    user_logged_in: bool = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    if not user_logged_in:
        raise HTTPException(status_code=401, detail="Unauthorized")

    key_object = key_service.get_key_by_value(db, request.key)
    if key_object:
        raise HTTPException(status_code=409, detail=f"Key '{request.key}' đã tồn tại.")
    
    key_service.create_key(db, request.key, "Default", None)
    return {"status": "success", "message": f"Key '{request.key}' đã được thêm."}

@router.post("/keys/delete", summary="Xóa một key (API)")
async def delete_existing_key_api(
    request: KeyRequest, 
    user_logged_in: bool = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    if not user_logged_in:
        raise HTTPException(status_code=401, detail="Unauthorized")

    success = key_service.delete_key(db, request.key)
    if not success:
        raise HTTPException(status_code=404, detail=f"Key '{request.key}' không tìm thấy để xóa.")
    return {"status": "success", "message": f"Key '{request.key}' đã được xóa."}

@router.get("/keys/status/{key_value}", summary="Kiểm tra trạng thái một key (API)")
async def check_key_status_api(
    key_value: str, 
    user_logged_in: bool = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    if not user_logged_in:
        raise HTTPException(status_code=401, detail="Unauthorized")

    key_object = key_service.get_key_by_value(db, key_value)
    if not key_object:
        raise HTTPException(status_code=404, detail="Key không tìm thấy.")
    return {"key": key_object.key_value, "status": key_object.status}

@router.get("/keys/all", summary="Lấy danh sách tất cả keys (JSON cho giao diện web)")
async def get_all_keys_json(
    user_logged_in: bool = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    if not user_logged_in:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    all_keys = key_service.get_all_keys(db, filters={})
    return all_keys
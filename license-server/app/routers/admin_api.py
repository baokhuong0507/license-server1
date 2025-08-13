# app/routers/admin_api.py
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import Annotated

from app.config import settings
from app.services import keys as key_service
# Thêm 2 dòng này vào đầu tệp app/routers/admin_api.py
import os
from app.services.keys import get_db_path
router = APIRouter()

# --- Security Dependency ---
async def verify_admin(x_admin_secret: Annotated[str, Header()]):
    """Một dependency để kiểm tra secret key trong header."""
    if x_admin_secret != settings.ADMIN_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

# --- Pydantic Models ---
class KeyRequest(BaseModel):
    key: str

# --- Admin Endpoints ---
@router.post("/keys/add", summary="Thêm một key mới", dependencies=[Depends(verify_admin)])
async def add_new_key(request: KeyRequest):
    success = key_service.add_key(request.key)
    if not success:
        raise HTTPException(status_code=409, detail=f"Key '{request.key}' đã tồn tại.")
    return {"status": "success", "message": f"Key '{request.key}' đã được thêm."}

@router.post("/keys/delete", summary="Xóa một key", dependencies=[Depends(verify_admin)])
async def delete_existing_key(request: KeyRequest):
    key_service.delete_key(request.key)
    return {"status": "success", "message": f"Key '{request.key}' đã được xóa."}

@router.get("/keys/status/{key_value}", summary="Kiểm tra trạng thái một key", dependencies=[Depends(verify_admin)])
async def check_key_status(key_value: str):
    status = key_service.get_key_status(key_value)
    if not status:
        raise HTTPException(status_code=404, detail="Key không tìm thấy.")
    return {"key": key_value, "status": status}
# Dán đoạn này vào cuối tệp app/routers/admin_api.py

import os
from app.services.keys import get_db_path

@router.post("/system/reset-database", 
             summary="[NGUY HIỂM] Xóa và khởi tạo lại toàn bộ CSDL", 
             dependencies=[Depends(verify_admin)])
async def reset_the_database():
    """
    Endpoint này sẽ xóa tệp CSDL hiện tại.
    Sau khi chạy, bạn PHẢI khởi động lại service trên Render để nó tạo lại CSDL mới.
    """
    db_path = get_db_path()
    try:
        os.remove(db_path)
        return {"status": "success", 
                "message": f"Tệp CSDL tại '{db_path}' đã được xóa. Vui lòng khởi động lại service."}
    except FileNotFoundError:
        return {"status": "warning", 
                "message": f"Không tìm thấy tệp CSDL tại '{db_path}'. Không có gì để xóa."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi không xác định khi xóa CSDL: {e}")

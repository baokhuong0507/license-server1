# app/routers/client_api.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import date

from app.services import keys as key_service
from app.database import get_db

router = APIRouter()

class KeyActivationRequest(BaseModel):
    key: str
    machine_id: str
    username: str

# Trong tệp app/routers/client_api.py

@router.post("/activate", summary="Kích hoạt một key bản quyền")
async def activate_license_key(request: KeyActivationRequest, db: Session = Depends(get_db)):
    key_object = key_service.get_key_by_value(db, request.key)

    if not key_object:
        raise HTTPException(status_code=404, detail="Key không hợp lệ hoặc không tồn tại.")

    if key_object.expiration_date and key_object.expiration_date < date.today():
        if key_object.status != "expired":
            key_service.update_key_status(db, request.key, "expired")
        raise HTTPException(status_code=403, detail="Key này đã hết hạn sử dụng.")

    if key_object.status == 'revoked':
        key_service.increment_failed_attempts(db, request.key)
        raise HTTPException(status_code=403, detail="Key này đã bị quản trị viên tạm khóa.")

    if key_object.status == 'used':
        if key_object.machine_id == request.machine_id:
            # GỌI HÀM CẬP NHẬT MỚI
            key_service.update_last_activated_time(db, request.key)
            return {"status": "success", "message": "Key đã được xác thực lại trên máy này."}
        else:
            key_service.increment_failed_attempts(db, request.key)
            raise HTTPException(status_code=403, detail="Key này đã được sử dụng trên một máy tính khác.")
    
    if key_object.status == 'expired':
        raise HTTPException(status_code=403, detail="Key này đã hết hạn sử dụng.")

    if key_object.status == 'active':
        key_service.set_activation_details(
            db, 
            key_value=request.key, 
            machine_id=request.machine_id, 
            username=request.username
        )
        return {"status": "success", "message": "Kích hoạt thành công!"}

    raise HTTPException(status_code=400, detail=f"Không thể kích hoạt key với trạng thái '{key_object.status}'.")
    
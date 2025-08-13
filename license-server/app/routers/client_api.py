# app/routers/client_api.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.services import keys as key_service
from app.database import get_db

router = APIRouter()

# --- Sửa Pydantic Model để nhận thêm thông tin ---
class KeyActivationRequest(BaseModel):
    key: str
    machine_id: str
    username: str

@router.post("/activate", summary="Kích hoạt một key bản quyền")
async def activate_license_key(request: KeyActivationRequest, db: Session = Depends(get_db)):
    key_object = key_service.get_key_by_value(db, request.key)

    # Trường hợp 1: Key không tồn tại
    if not key_object:
        raise HTTPException(status_code=404, detail="Key không hợp lệ hoặc không tồn tại.")

    # Trường hợp 2: Key đã bị khóa
    if key_object.status == 'revoked':
        key_service.increment_failed_attempts(db, request.key)
        raise HTTPException(status_code=403, detail="Key này đã bị quản trị viên tạm khóa.")

    # Trường hợp 3: Key đã được sử dụng
    if key_object.status == 'used':
        # Kiểm tra xem có phải cùng một máy đang kích hoạt lại không
        if key_object.machine_id == request.machine_id:
            # Nếu đúng là máy cũ, cho phép và coi như thành công
            return {"status": "success", "message": "Key đã được xác thực lại trên máy này."}
        else:
            # Nếu là máy khác -> Cảnh báo chia sẻ key
            key_service.increment_failed_attempts(db, request.key)
            raise HTTPException(status_code=403, detail="Key này đã được sử dụng trên một máy tính khác.")

    # Trường hợp 4: Key hợp lệ và sẵn sàng để kích hoạt
    if key_object.status == 'active':
        key_service.set_activation_details(
            db, 
            key_value=request.key, 
            machine_id=request.machine_id, 
            username=request.username
        )
        return {"status": "success", "message": "Kích hoạt thành công!"}

    # Các trường hợp khác
    raise HTTPException(status_code=400, detail=f"Không thể kích hoạt key với trạng thái '{key_object.status}'.")

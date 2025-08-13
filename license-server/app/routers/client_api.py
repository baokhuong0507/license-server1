# app/routers/client_api.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services import keys as key_service

router = APIRouter()

class KeyActivationRequest(BaseModel):
    key: str

@router.post("/activate", summary="Kích hoạt một key bản quyền")
async def activate_license_key(request: KeyActivationRequest):
    status = key_service.get_key_status(request.key)

    if not status:
        raise HTTPException(status_code=404, detail="Key không hợp lệ hoặc không tồn tại.")
    
    if status == 'active':
        key_service.update_key_status(request.key, 'used')
        return {"status": "success", "message": "Kích hoạt thành công!"}
    
    if status == 'used':
        raise HTTPException(status_code=403, detail="Key này đã được sử dụng.")
        
    raise HTTPException(status_code=403, detail=f"Key không thể kích hoạt (trạng thái: {status}).")

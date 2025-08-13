# app/routers/client_api.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services import keys as key_service
from sqlalchemy.orm import Session
from app.database import get_db
router = APIRouter()

class KeyActivationRequest(BaseModel):
    key: str

@router.post("/activate", summary="Kích hoạt một key bản quyền")
async def activate_license_key(request: KeyActivationRequest, db: Session = Depends(get_db)):
    key_object = key_service.get_key_by_value(db, request.key)

    if not key_object:
        raise HTTPException(status_code=404, detail="Key không hợp lệ hoặc không tồn tại.")
    
    if key_object.status == 'active':
        key_service.update_key_status(db, request.key, 'used')
        return {"status": "success", "message": "Kích hoạt thành công!"}
    
    if key_object.status == 'used':
        raise HTTPException(status_code=403, detail="Key này đã được sử dụng.")
        
    raise HTTPException(status_code=403, detail=f"Key không thể kích hoạt (trạng thái: {key_object.status}).")

# app/routers/admin_api.py

from __future__ import annotations # <--- Thêm dòng này vào đầu
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..services import keys as key_service
from .. import schemas

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin API"]
)

@router.get("/keys", response_model=list[schemas.Key])
def get_all_keys(db: Session = Depends(get_db)):
    """
    API endpoint to get all keys.
    """
    return key_service.get_all_keys(db)
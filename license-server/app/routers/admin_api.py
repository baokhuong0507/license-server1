# app/routers/admin_api.py
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from ..deps import get_db
from ..services import keys as key_service

router = APIRouter(prefix="/admin/api", tags=["admin-api"])

@router.get("/keys")
def get_all_keys_json(
    status: str | None = None,
    q: str | None = None,
    db: Session = Depends(get_db),
):
    filters = {}
    if status: filters["status"] = status
    if q: filters["q"] = q
    return {"items": key_service.get_all_keys(db, filters=filters)}

@router.post("/keys")
def create_key_api(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
):
    try:
        key_value = (payload.get("key") or "").strip()
        note = payload.get("note") or ""
        offline_ttl = int(payload.get("offline_ttl_minutes") or 0)
        return key_service.create_key(
            db,
            key_value=key_value,
            note=note,
            offline_ttl_minutes=offline_ttl,
        )
    except ValueError as e:
        # Các mã: EMPTY_KEY, DUPLICATE_KEY
        raise HTTPException(status_code=400, detail=str(e))

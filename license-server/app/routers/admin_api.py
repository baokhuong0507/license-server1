# app/routers/admin_api.py
# Router JSON cho admin + alias tương thích với UI đang gọi (/api/admin/keys/*)

from fastapi import APIRouter, Depends, HTTPException, Body, Form, Request
from sqlalchemy.orm import Session

from ..deps import get_db
from ..services import keys as key_service

router = APIRouter(tags=["admin-api"])

# -----------------------------
# LIST KEYS
# -----------------------------
@router.get("/admin/api/keys")
@router.get("/api/admin/keys/all")  # <--- alias cho UI hiện có
def list_keys(
    status: str | None = None,
    q: str | None = None,
    db: Session = Depends(get_db),
):
    filters = {}
    if status: filters["status"] = status
    if q: filters["q"] = q
    return {"items": key_service.get_all_keys(db, filters=filters)}


# -----------------------------
# CREATE KEY (JSON)
# -----------------------------
@router.post("/admin/api/keys")
def create_key_json(
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
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------
# CREATE KEY (FORM) – alias cho UI: /api/admin/keys/add
# Hỗ trợ cả form-urlencoded lẫn JSON để chắc ăn.
# -----------------------------
@router.post("/api/admin/keys/add")  # <--- alias cho UI hiện có
async def create_key_legacy(
    request: Request,
    db: Session = Depends(get_db),
    # nếu UI gửi form
    key: str | None = Form(default=None),
    note: str | None = Form(default=None),
    offline_ttl_minutes: int | None = Form(default=None),
):
    try:
        # Nếu là JSON, đọc từ body
        if request.headers.get("content-type", "").startswith("application/json"):
            data = await request.json()
            key_value = (data.get("key") or "").strip()
            note_value = data.get("note") or ""
            offline_ttl = int(data.get("offline_ttl_minutes") or 0)
        else:
            # Form
            key_value = (key or "").strip()
            note_value = note or ""
            offline_ttl = int(offline_ttl_minutes or 0)

        result = key_service.create_key(
            db,
            key_value=key_value,
            note=note_value,
            offline_ttl_minutes=offline_ttl,
        )
        # Một số UI cũ chỉ cần {"success": true}
        return {"success": True, **result}
    except ValueError as e:
        # EMPTY_KEY, DUPLICATE_KEY ...
        raise HTTPException(status_code=400, detail=str(e))

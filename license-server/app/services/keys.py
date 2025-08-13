# app/services/keys.py
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
# import "lười" để tránh ImportError do thứ tự nạp module
from .. import models

# ===== HÀM SẴN CÓ (điều chỉnh import) =====

def get_key_by_value(db: Session, key_value: str):
    return db.query(models.LicenseKey).filter_by(key=key_value).first()

def set_key_status(db: Session, key, status):
    if status == models.KeyStatus.TEMP_LOCKED:
        key.status = models.KeyStatus.TEMP_LOCKED
    else:
        key.status = status
    db.add(key)
    db.commit()
    db.refresh(key)
    return key

# ===== HÀM BỔ SUNG CHO DASHBOARD =====

def get_all_keys(db: Session, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    q = db.query(models.LicenseKey)
    if filters:
        if filters.get("status"):
            try:
                q = q.filter(models.LicenseKey.status == models.KeyStatus(filters["status"]))
            except Exception:
                pass
        if filters.get("q"):
            like = f"%{filters['q']}%"
            q = q.filter(
                (models.LicenseKey.key.ilike(like)) |
                (models.LicenseKey.note.ilike(like))
            )
    items = q.order_by(models.LicenseKey.created_at.desc()).all()
    return [{
        "id": k.id,
        "key": k.key,
        "status": k.status.value if hasattr(k.status, "value") else str(k.status),
        "note": k.note,
        "offline_ttl_minutes": k.offline_ttl_minutes,
        "created_at": getattr(k, "created_at", None).isoformat() if getattr(k, "created_at", None) else None,
        "updated_at": getattr(k, "updated_at", None).isoformat() if getattr(k, "updated_at", None) else None,
    } for k in items]

def create_key(db: Session, key_value: str, *, note: str = "", offline_ttl_minutes: int = 0) -> Dict[str, Any]:
    if not key_value or not key_value.strip():
        raise ValueError("EMPTY_KEY")
    exists = db.query(models.LicenseKey).filter_by(key=key_value).first()
    if exists:
        raise ValueError("DUPLICATE_KEY")
    k = models.LicenseKey(
        key=key_value.strip(),
        note=note or "",
        offline_ttl_minutes=int(offline_ttl_minutes or 0),
        status=models.KeyStatus.ACTIVE,
    )
    db.add(k)
    db.commit()
    db.refresh(k)
    return {"id": k.id, "key": k.key}

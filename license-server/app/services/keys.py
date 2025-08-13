# app/services/keys.py
from datetime import datetime
from sqlalchemy.orm import Session
from ..models import LicenseKey, KeyStatus

def get_all_keys(db: Session, filters: dict | None = None):
    q = db.query(LicenseKey)
    if filters:
        if s := filters.get("status"):
            try:
                q = q.filter(LicenseKey.status == KeyStatus(s))
            except ValueError:
                pass
        if term := filters.get("q"):
            like = f"%{term}%"
            q = q.filter(
                (LicenseKey.key.ilike(like)) |
                (LicenseKey.note.ilike(like))
            )
    items = q.order_by(LicenseKey.created_at.desc()).all()
    return [{
        "id": k.id,
        "key": k.key,
        "status": k.status.value,
        "note": k.note,
        "offline_ttl_minutes": k.offline_ttl_minutes,
        "created_at": k.created_at.isoformat(),
        "updated_at": k.updated_at.isoformat() if k.updated_at else None
    } for k in items]

def create_key(db: Session, key_value: str, note: str = "", offline_ttl_minutes: int = 0):
    if not key_value:
        raise ValueError("EMPTY_KEY")
    exists = db.query(LicenseKey).filter_by(key=key_value).first()
    if exists:
        raise ValueError("DUPLICATE_KEY")
    k = LicenseKey(
        key=key_value,
        note=note,
        offline_ttl_minutes=offline_ttl_minutes,
        status=KeyStatus.ACTIVE,
    )
    db.add(k)
    db.commit()
    db.refresh(k)
    return {"id": k.id, "key": k.key}

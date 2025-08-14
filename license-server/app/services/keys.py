# app/services/keys.py
# Bản an toàn: import các lớp từ models NGAY BÊN TRONG HÀM
# để tránh tình huống module app.models chưa khởi tạo xong.

from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session


# ========= CÁC HÀM GỐC (điều chỉnh import) =========

def get_key_by_value(db: Session, key_value: str):
    # Import cục bộ để tránh lỗi khi khởi tạo module
    from ..models import LicenseKey
    return db.query(LicenseKey).filter_by(key=key_value).first()


def set_key_status(db: Session, key, status):
    from ..models import KeyStatus
    key.status = status
    if status == KeyStatus.TEMP_LOCKED:
        from datetime import datetime
        # last_violation_at có trong schema
        key.last_violation_at = datetime.utcnow()
    db.commit()
    return key


# ========= HÀM CHO DASHBOARD (list + create) =========

def get_all_keys(db: Session, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    from ..models import LicenseKey, KeyStatus
    q = db.query(LicenseKey)

    if filters:
        if filters.get("status"):
            try:
                q = q.filter(LicenseKey.status == KeyStatus(filters["status"]))
            except Exception:
                pass
        if filters.get("q"):
            like = f"%{filters['q']}%"
            q = q.filter(
                (LicenseKey.key.ilike(like)) |
                (LicenseKey.note.ilike(like))
            )

    items = q.order_by(LicenseKey.created_at.desc()).all()
    out: List[Dict[str, Any]] = []
    for k in items:
        out.append({
            "id": k.id,
            "key": k.key,
            "status": k.status.value if hasattr(k.status, "value") else str(k.status),
            "note": k.note,
            "offline_ttl_minutes": k.offline_ttl_minutes,
            "created_at": getattr(k, "created_at", None).isoformat() if getattr(k, "created_at", None) else None,
            "updated_at": getattr(k, "updated_at", None).isoformat() if getattr(k, "updated_at", None) else None,
        })
    return out


def create_key(db: Session, key_value: str, *, note: str = "", offline_ttl_minutes: int = 0) -> Dict[str, Any]:
    from ..models import LicenseKey, KeyStatus
    if not key_value or not key_value.strip():
        raise ValueError("EMPTY_KEY")

    exists = db.query(LicenseKey).filter_by(key=key_value).first()
    if exists:
        raise ValueError("DUPLICATE_KEY")

    k = LicenseKey(
        key=key_value.strip(),
        note=note or "",
        offline_ttl_minutes=int(offline_ttl_minutes or 0),
        status=KeyStatus.ACTIVE,
    )
    db.add(k)
    db.commit()
    db.refresh(k)
    return {"id": k.id, "key": k.key}

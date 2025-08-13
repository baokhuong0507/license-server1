# app/services/keys.py
# LƯU Ý: đây là file đầy đủ, thay thế toàn bộ file cũ.

from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

# Dùng import "lười" để tránh ImportError khi thứ tự nạp module thay đổi.
# Ta sẽ truy cập models.LicenseKey / models.KeyStatus ở bên trong hàm.
from .. import models


# ========= CÁC HÀM CŨ (giữ nguyên chức năng, đổi cách import) =========

def get_key_by_value(db: Session, key_value: str):
    """Trả về 1 LicenseKey theo giá trị key (hoặc None nếu không có)."""
    return db.query(models.LicenseKey).filter_by(key=key_value).first()


def set_key_status(db: Session, key, status):
    """
    Cập nhật trạng thái key. Hỗ trợ các giá trị trong models.KeyStatus.
    """
    # Nếu repo của bạn có logic đặc biệt cho TEMP_LOCKED thì vẫn dùng như cũ.
    if status == models.KeyStatus.TEMP_LOCKED:
        key.status = models.KeyStatus.TEMP_LOCKED
    else:
        key.status = status
    db.add(key)
    db.commit()
    db.refresh(key)
    return key


# ========= CÁC HÀM BỔ SUNG (dashboard đang gọi tới) =========

def get_all_keys(db: Session, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Trả về danh sách key theo JSON cho dashboard.
    Hỗ trợ lọc đơn giản theo 'status' và tìm kiếm 'q'.
    """
    q = db.query(models.LicenseKey)

    if filters:
        # Lọc theo status (chuỗi tên enum), ví dụ: "ACTIVE", "BLOCKED"...
        s = filters.get("status")
        if s:
            try:
                q = q.filter(models.LicenseKey.status == models.KeyStatus(s))
            except Exception:
                pass

        # Tìm kiếm theo key hoặc note
        term = filters.get("q")
        if term:
            like = f"%{term}%"
            q = q.filter(
                (models.LicenseKey.key.ilike(like)) |
                (models.LicenseKey.note.ilike(like))
            )

    items = q.order_by(models.LicenseKey.created_at.desc()).all()

    # Chuẩn hóa JSON để frontend dễ dùng
    return [{
        "id": k.id,
        "key": k.key,
        "status": k.status.value if hasattr(k.status, "value") else str(k.status),
        "note": k.note,
        "offline_ttl_minutes": k.offline_ttl_minutes,
        "created_at": k.created_at.isoformat() if getattr(k, "created_at", None) else None,
        "updated_at": k.updated_at.isoformat() if getattr(k, "updated_at", None) else None,
    } for k in items]


def create_key(
    db: Session,
    key_value: str,
    *,
    note: str = "",
    offline_ttl_minutes: int = 0,
) -> Dict[str, Any]:
    """
    Tạo 1 key mới với trạng thái ACTIVE.
    - Không đụng tới 'program' hay 'expiry' vì lược đồ mặc định không có.
    """
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

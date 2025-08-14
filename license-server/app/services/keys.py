# app/services/keys.py

from __future__ import annotations
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from .. import models
import random
import string

def _generate_key_string() -> str:
    """Hàm nội bộ để tạo chuỗi key ngẫu nhiên."""
    chars = string.ascii_uppercase + string.digits
    return '-'.join(''.join(random.choice(chars) for _ in range(5)) for _ in range(5))

def check_and_update_all_keys_status(db: Session):
    """Kiểm tra và cập nhật trạng thái của tất cả các key đã hết hạn."""
    now = datetime.now(timezone.utc)
    keys_to_check = db.query(models.Key).filter(models.Key.status != 'expired').all()
    needs_commit = False
    for key in keys_to_check:
        if key.expiry_date and key.expiry_date < now:
            key.status = 'expired'
            needs_commit = True
    if needs_commit:
        db.commit()

def get_all_keys(db: Session) -> list[models.Key]:
    """Lấy tất cả các key, luôn kiểm tra trạng thái trước."""
    check_and_update_all_keys_status(db)
    return db.query(models.Key).order_by(models.Key.id.desc()).all()

def activate_key_by_id(db: Session, key_id: int) -> models.Key | None:
    """Kích hoạt một key cụ thể."""
    key = db.query(models.Key).filter(models.Key.id == key_id).first()
    if key and key.status == 'unused':
        key.status = 'active'
        if not key.expiry_date:
            key.expiry_date = datetime.now(timezone.utc) + timedelta(days=30)
        db.commit()
        db.refresh(key)
        return key
    return None

def create_new_key(db: Session, days_valid: int | None = None) -> models.Key:
    """Tạo một key mới trong database."""
    new_key_data = models.Key(
        key=_generate_key_string(),
        status='unused'
    )
    if days_valid and days_valid > 0:
        new_key_data.expiry_date = datetime.now(timezone.utc) + timedelta(days=days_valid)
    
    db.add(new_key_data)
    db.commit()
    db.refresh(new_key_data)
    return new_key_data

def delete_key_by_id(db: Session, key_id: int) -> bool:
    """Xóa một key khỏi database."""
    key_to_delete = db.query(models.Key).filter(models.Key.id == key_id).first()
    if key_to_delete:
        db.delete(key_to_delete)
        db.commit()
        return True
    return False
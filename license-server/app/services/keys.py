# app/services/keys.py

from __future__ import annotations # <--- Thêm dòng này vào đầu
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from .. import models

def check_and_update_all_keys_status(db: Session):
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
    check_and_update_all_keys_status(db)
    return db.query(models.Key).order_by(models.Key.id.desc()).all()

def activate_key_by_id(db: Session, key_id: int) -> models.Key | None:
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
    import random
    import string

    def generate_key_string():
        chars = string.ascii_uppercase + string.digits
        return '-'.join(''.join(random.choice(chars) for _ in range(5)) for _ in range(5))

    new_key_data = models.Key(
        key=generate_key_string(),
        status='unused'
    )
    if days_valid:
        new_key_data.expiry_date = datetime.now(timezone.utc) + timedelta(days=days_valid)
    db.add(new_key_data)
    db.commit()
    db.refresh(new_key_data)
    return new_key_data
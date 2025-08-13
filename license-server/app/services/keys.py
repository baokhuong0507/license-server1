# app/services/keys.py

import string
import random
from sqlalchemy.orm import Session
from sqlalchemy import update
from app import models
from datetime import date, datetime, timezone
from datetime import datetime
# --- Các hàm khác giữ nguyên, chỉ sửa lại hàm sweep_expired_keys ---

def get_key_by_value(db: Session, key_value: str):
    return db.query(models.Key).filter(models.Key.key_value == key_value).first()

def get_all_keys(db: Session, filters: dict):
    query = db.query(models.Key)
    if filters.get("status"):
        query = query.filter(models.Key.status == filters["status"])
    if filters.get("program_name"):
        query = query.filter(models.Key.program_name.ilike(f'%{filters["program_name"]}%'))
    if filters.get("search_key"):
        query = query.filter(models.Key.key_value.ilike(f'%{filters["search_key"]}%'))
    return query.order_by(models.Key.created_at.desc()).all()

def create_key(db: Session, key_value: str, program_name: str, expiration_date: datetime | None):
    db_key = models.Key(
        key_value=key_value, 
        program_name=program_name, 
        expiration_date=expiration_date
    )
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    return db_key

def bulk_create_keys(db: Session, quantity: int, length: int, program_name: str, expiration_date: datetime | None):
    generated_keys = []
    for _ in range(quantity):
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        db_key = models.Key(
            key_value=random_str,
            program_name=program_name,
            expiration_date=expiration_date
        )
        db.add(db_key)
    db.commit()
    return generated_keys

def delete_key(db: Session, key_value: str):
    db_key = get_key_by_value(db, key_value)
    if db_key:
        db.delete(db_key)
        db.commit()
        return True
    return False

def update_key_status(db: Session, key_value: str, new_status: str):
    db_key = get_key_by_value(db, key_value)
    if db_key:
        db_key.status = new_status
        db.commit()
        db.refresh(db_key)
    return db_key

def set_activation_details(db: Session, key_value: str, machine_id: str, username: str):
    db_key = get_key_by_value(db, key_value)
    if db_key:
        db_key.status = "used"
        db_key.machine_id = machine_id
        db_key.activated_by_user = username
        db_key.last_activated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(db_key)
    return db_key

def update_last_activated_time(db: Session, key_value: str):
    db_key = get_key_by_value(db, key_value)
    if db_key:
        db_key.last_activated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(db_key)
    return db_key

def increment_failed_attempts(db: Session, key_value: str):
    db_key = get_key_by_value(db, key_value)
    if db_key:
        current_attempts = getattr(db_key, 'failed_attempts', 0)
        db_key.failed_attempts = (current_attempts or 0) + 1
        db.commit()

# --- HÀM QUAN TRỌNG ĐÃ ĐƯỢC SỬA LẠI HOÀN TOÀN ---
def sweep_expired_keys(db: Session):
    """
    Quét và cập nhật trạng thái cho tất cả các key đã hết hạn.
    Đây là cách làm hiệu quả với SQLAlchemy, chỉ thực hiện một câu lệnh UPDATE.
    """
    today = date.today()
    
    # Tạo một câu lệnh UPDATE
    stmt = (
        update(models.Key)
        .where(
            models.Key.status.in_(['active', 'used']),
            models.Key.expiration_date < today
        )
        .values(status="expired")
    )
    
    # Thực thi câu lệnh và lấy số dòng đã bị ảnh hưởng
    result = db.execute(stmt)
    db.commit()
    
    count = result.rowcount
    print(f"Đã quét và cập nhật {count} key thành 'expired'.")
    return count
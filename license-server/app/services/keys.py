# app/services/keys.py
import string
import random
from sqlalchemy.orm import Session
from app import models
from datetime import date

def get_key_by_value(db: Session, key_value: str):
    return db.query(models.Key).filter(models.Key.key_value == key_value).first()

def get_all_keys(db: Session, filters: dict):
    """Lấy danh sách keys với bộ lọc động."""
    query = db.query(models.Key)
    
    # Lọc theo trạng thái
    if filters.get("status"):
        query = query.filter(models.Key.status == filters["status"])
        
    # Lọc theo tên chương trình
    if filters.get("program_name"):
        query = query.filter(models.Key.program_name.ilike(f'%{filters["program_name"]}%'))
        
    # Tìm kiếm theo key
    if filters.get("search_key"):
        query = query.filter(models.Key.key_value.ilike(f'%{filters["search_key"]}%'))
        
    return query.order_by(models.Key.created_at.desc()).all()

def create_key(db: Session, key_value: str, program_name: str, expiration_date: date | None):
    db_key = models.Key(
        key_value=key_value, 
        program_name=program_name, 
        expiration_date=expiration_date
    )
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    return db_key

def bulk_create_keys(db: Session, quantity: int, length: int, program_name: str, expiration_date: date | None):
    """Tạo key hàng loạt."""
    generated_keys = []
    for _ in range(quantity):
        # Tạo chuỗi key ngẫu nhiên
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        
        # Thêm vào CSDL
        db_key = models.Key(
            key_value=random_str,
            program_name=program_name,
            expiration_date=expiration_date
        )
        db.add(db_key)
        generated_keys.append(db_key)
        
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
    return None

def set_activation_details(db: Session, key_value: str, machine_id: str, username: str):
    db_key = get_key_by_value(db, key_value)
    if db_key:
        db_key.status = "used"
        db_key.machine_id = machine_id
        db_key.activated_by_user = username
        db.commit()
        db.refresh(db_key)
        return db_key
    return None

def increment_failed_attempts(db: Session, key_value: str):
    db_key = get_key_by_value(db, key_value)
    if db_key:
        # Dùng getattr để tránh lỗi nếu cột không tồn tại ở phiên bản CSDL cũ
        current_attempts = getattr(db_key, 'failed_attempts', 0)
        db_key.failed_attempts = (current_attempts or 0) + 1
        db.commit()
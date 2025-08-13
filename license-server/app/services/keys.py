# app/services/keys.py
from sqlalchemy.orm import Session
from app import models

def get_key_by_value(db: Session, key_value: str):
    return db.query(models.Key).filter(models.Key.key_value == key_value).first()

def get_all_keys(db: Session):
    return db.query(models.Key).order_by(models.Key.created_at.desc()).all()

def create_key(db: Session, key_value: str):
    db_key = models.Key(key_value=key_value, status="active")
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    return db_key

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

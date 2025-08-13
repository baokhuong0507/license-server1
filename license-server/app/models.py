# app/models.py
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.sql import func
from app.database import Base

class Key(Base):
    __tablename__ = "keys"

    key_value = Column(String, primary_key=True, index=True)
    status = Column(String, default="active", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # Đã là DateTime
    machine_id = Column(String, nullable=True)
    activated_by_user = Column(String, nullable=True)
    failed_attempts = Column(Integer, default=0)
    program_name = Column(String, nullable=True, index=True, default="Default")
    
    # --- THAY ĐỔI QUAN TRỌNG ---
    # Chuyển từ Date sang DateTime để lưu cả giờ
    expiration_date = Column(DateTime(timezone=True), nullable=True)
    
    last_activated_at = Column(DateTime(timezone=True), nullable=True)
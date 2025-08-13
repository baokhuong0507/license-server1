# app/models.py
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.sql import func
from app.database import Base

class Key(Base):
    __tablename__ = "keys"

    # Các cột cũ
    key_value = Column(String, primary_key=True, index=True)
    status = Column(String, default="active", index=True) # active, used, revoked
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # --- CÁC CỘT MỚI ---
    # ID của máy tính đã kích hoạt key
    machine_id = Column(String, nullable=True)
    
    # Tên người dùng trên máy tính đã kích hoạt
    activated_by_user = Column(String, nullable=True)
    
    # Đếm số lần kích hoạt thất bại (khi key đã used hoặc không tồn tại)
    failed_attempts = Column(Integer, default=0)

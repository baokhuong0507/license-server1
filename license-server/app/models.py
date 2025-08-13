# app/models.py
from sqlalchemy import Column, String, DateTime, Integer, Date
from sqlalchemy.sql import func
from app.database import Base

class Key(Base):
    __tablename__ = "keys"

    # Các cột cũ
    key_value = Column(String, primary_key=True, index=True)
    status = Column(String, default="active", index=True) # active, used, revoked, expired
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    machine_id = Column(String, nullable=True)
    activated_by_user = Column(String, nullable=True)
    failed_attempts = Column(Integer, default=0)

    # --- CÁC CỘT MỚI ---
    # Tên chương trình mà key này thuộc về
    program_name = Column(String, nullable=True, index=True, default="Default")
    
    # Hạn sử dụng của key. Nếu là NULL, có nghĩa là vĩnh viễn.
    expiration_date = Column(Date, nullable=True)
# app/models.py
from sqlalchemy import Column, String, DateTime, Integer, Date
from sqlalchemy.sql import func
from app.database import Base

class Key(Base):
    __tablename__ = "keys"

    key_value = Column(String, primary_key=True, index=True)
    status = Column(String, default="active", index=True)
    # Cột này đã có sẵn, sẽ tự động thêm ngày giờ khi tạo mới
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    machine_id = Column(String, nullable=True)
    activated_by_user = Column(String, nullable=True)
    failed_attempts = Column(Integer, default=0)
    program_name = Column(String, nullable=True, index=True, default="Default")
    expiration_date = Column(Date, nullable=True)
    # Cột này cũng đã có sẵn
    last_activated_at = Column(DateTime(timezone=True), nullable=True)
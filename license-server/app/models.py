# app/models.py

from __future__ import annotations
from sqlalchemy import Column, Integer, String, DateTime, Enum
from .database import Base
import enum

class KeyStatus(str, enum.Enum):
    unused = "unused"
    active = "active"
    expired = "expired"

class Key(Base):
    # ĐÂY LÀ THAY ĐỔI DUY NHẤT VÀ QUAN TRỌNG NHẤT.
    # Chúng ta sẽ sử dụng một tên bảng mới, sạch sẽ, và đúng cấu trúc,
    # bỏ qua hoàn toàn bảng "keys" cũ đã bị lỗi.
    __tablename__ = "license_keys_final"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    status = Column(Enum(KeyStatus), default=KeyStatus.unused, nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)
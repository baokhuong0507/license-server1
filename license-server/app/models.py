# app/models.py

from __future__ import annotations # <--- DÒNG QUAN TRỌNG NHẤT ĐỂ SỬA LỖI
from sqlalchemy import Column, Integer, String, DateTime, Enum
from .database import Base
import enum

class KeyStatus(str, enum.Enum):
    unused = "unused"
    active = "active"
    expired = "expired"

class Key(Base):
    __tablename__ = "keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    status = Column(Enum(KeyStatus), default=KeyStatus.unused, nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)
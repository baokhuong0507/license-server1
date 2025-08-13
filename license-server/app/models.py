# app/models.py
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Key(Base):
    __tablename__ = "keys"

    key_value = Column(String, primary_key=True, index=True)
    status = Column(String, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

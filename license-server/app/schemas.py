# app/schemas.py

from __future__ import annotations
from pydantic import BaseModel
from datetime import datetime

# Import Enum từ tệp models để dùng chung
from .models import KeyStatus

# Đây là Schema cơ bản, chứa các trường chung
class KeyBase(BaseModel):
    key: str
    status: KeyStatus

# Đây là Schema chính, dùng để trả về dữ liệu từ API.
# Nó kế thừa từ KeyBase và thêm các trường khác từ database.
class Key(KeyBase):
    id: int
    expiry_date: datetime | None = None
    created_at: datetime

    # Cấu hình này cho phép Pydantic làm việc với các đối tượng SQLAlchemy
    class Config:
        orm_mode = True
# app/auth.py

from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status, Request
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# --- Cấu hình ---
SECRET_KEY = settings.ADMIN_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Hàm tiện ích ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- HÀM XÁC THỰC ĐÃ ĐƯỢC SỬA LẠI ---
async def get_current_user(request: Request):
    """
    Dependency này đọc token từ cookie (cho web) hoặc từ Header (cho API).
    """
    token = request.cookies.get("access_token")

    if not token:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

    if not token:
        return None 
    
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return True 
    except JWTError:
        return None
# app/auth.py

from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# --- Cấu hình ---
SECRET_KEY = settings.ADMIN_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # Token hết hạn sau 1 ngày

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Dòng oauth2_scheme không được dùng trực tiếp cho web nhưng cần cho cấu trúc
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") 

# --- Hàm tiện ích ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiểm tra mật khẩu nhập vào với mật khẩu đã mã hóa."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Mã hóa mật khẩu."""
    return pwd_context.hash(password)

def create_access_token(data: dict):
    """Tạo một JSON Web Token (JWT) mới."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- HÀM BỊ THIẾU ĐÃ ĐƯỢC THÊM VÀO ĐÂY ---
async def get_current_user(request: Request):
    """
    Dependency này đọc token từ cookie, giải mã nó để xác thực người dùng.
    Dùng cho giao diện web.
    """
    token = request.cookies.get("access_token")
    if not token:
        return None  # Không có token, coi như chưa đăng nhập
    try:
        # Chỉ cần giải mã để xác thực, không cần dùng payload
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return True # Token hợp lệ, đã đăng nhập
    except JWTError:
        return None # Token không hợp lệ, coi như chưa đăng nhập```

from datetime import datetime, timedelta
from jose import jwt
from .config import settings

ALGO = "HS256"

def create_token(subject: str, minutes: int) -> str:
    now = datetime.utcnow()
    payload = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGO)

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGO])

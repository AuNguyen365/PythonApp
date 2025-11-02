import hashlib, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
from typing import Optional, Tuple
from app.config import settings


# ==== crypto / jwt ====


def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def verify_password(pw: str, hashed: str) -> bool:
    return hash_password(pw) == hashed


def create_token(user_id: int) -> str:
    payload = {
    "sub": str(user_id),
    "exp": datetime.utcnow() + timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])


# ==== response envelope ====


def response(status: str, message: str, data=None, meta: Optional[dict] = None):
    return {"status": status, "message": message, "data": data, "meta": meta}


# ==== helpers ====


def parse_bearer(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Thiếu header Authorization")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Header Authorization không hợp lệ")
    return parts[1]


def clamp_pagination(offset: Optional[int], limit: Optional[int]) -> Tuple[int, int]:
    if offset is None or offset < 0:
        offset = 0
    if limit is None or limit <= 0:
        limit = settings.DEFAULT_LIMIT
    limit = min(limit, settings.MAX_LIMIT)
    return offset, limit
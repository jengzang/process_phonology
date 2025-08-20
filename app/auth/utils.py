from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Request

# === 安全配置（建議改為環境變量/配置） ===
SECRET_KEY = "super-secret-key-change-me"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ISSUER = "your-app"      # 可自定義
AUDIENCE = "your-client" # 可自定義

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- 時間工具：UTC 時間 ---
def now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)  # 入庫用 naive UTC

# 如果要存北京時區，可改為：
# from datetime import timedelta
# CST = timezone(timedelta(hours=8))
# def now_cst() -> datetime:
#     return datetime.now(CST).replace(tzinfo=None)

# --- 密碼雜湊 ---
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# --- JWT ---
def create_access_token(subject: str, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    now = now_utc()
    to_encode = {
        "sub": subject,
        "iss": ISSUER,
        "aud": AUDIENCE,
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
        # 也可以加 jti/設備信息等
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], audience=AUDIENCE, issuer=ISSUER)

# --- 取客戶端 IP（考慮反代） ---
def extract_client_ip(request: Request) -> str:
    # 優先取 X-Forwarded-For (第一個為客戶端)
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    xri = request.headers.get("x-real-ip")
    if xri:
        return xri.strip()
    return request.client.host if request.client else "0.0.0.0"

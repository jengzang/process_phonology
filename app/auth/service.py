from sqlalchemy.orm import Session
from datetime import timedelta
from app.auth import models, utils
from app.schemas import auth as schemas
from common.config import REQUIRE_EMAIL_VERIFICATION

# --- 註冊 ---
def register_user(db: Session, user: schemas.UserCreate, register_ip: str) -> models.User:
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise ValueError("Username already exists")
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise ValueError("Email already exists")

    db_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        hashed_password=utils.get_password_hash(user.password),
        register_ip=register_ip,
        is_verified=not REQUIRE_EMAIL_VERIFICATION,  # 如果不需要驗證 -> 直接設 True
        # created_at 走 DB 默認
        login_count=0,
        failed_attempts=0,
        total_online_seconds=0,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- 認證（成功/失敗計數，會話開始） ---
def authenticate_user(db: Session, username: str, password: str, login_ip: str) -> models.User | None:
    user = db.query(models.User).filter(models.User.username == username).first()
    if REQUIRE_EMAIL_VERIFICATION and not user.is_verified:
        return None  # 或 raise HTTPException(status_code=403, detail="Email not verified")
    if not user:
        return None
    if not utils.verify_password(password, user.hashed_password):
        # 密碼錯誤 → 計數 + 記錄時間
        user.failed_attempts = (user.failed_attempts or 0) + 1
        user.last_failed_login = utils.now_utc()
        db.commit()
        return None

    # 成功登入
    user.failed_attempts = 0
    user.last_login = utils.now_utc()
    user.last_login_ip = login_ip
    user.login_count = (user.login_count or 0) + 1
    user.current_session_started_at = user.last_login
    user.last_seen = user.last_login
    db.commit()
    return user

# --- 心跳 / 訪問受保護接口時更新 last_seen ---
def touch_activity(db: Session, user: models.User) -> None:
    user.last_seen = utils.now_utc()
    db.commit()

# --- 登出：累加本次會話在線時長 ---
def logout_user(db: Session, user: models.User) -> int:
    """
    返回本次會話時長（秒）
    """
    now = utils.now_utc()
    session_secs = 0
    if user.current_session_started_at:
        delta = now - user.current_session_started_at
        session_secs = int(delta.total_seconds())
        user.total_online_seconds = (user.total_online_seconds or 0) + session_secs
        user.current_session_started_at = None
    user.last_seen = now
    db.commit()
    return session_secs

# --- 簽發 token ---
def issue_token_for_user(user: models.User, minutes: int = utils.ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    return utils.create_access_token(subject=user.username, expires_minutes=minutes)

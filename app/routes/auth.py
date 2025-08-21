from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from sqlalchemy.orm import Session

from app.schemas import auth as schemas
from app.auth import service, utils, models
from app.auth.database import get_db
from common.config import REQUIRE_EMAIL_VERIFICATION

router = APIRouter()
# Swagger 的 "Authorize" 按钮会用到这个 tokenUrl
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# 注册：根据开关决定是否要求邮箱验证；生成验证链接并发送
@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, request: Request, db: Session = Depends(get_db)):
    client_ip = utils.extract_client_ip(request)
    try:
        created = service.register_user(db, user, register_ip=client_ip)

        if REQUIRE_EMAIL_VERIFICATION:
            # 以 email 做 subject，设置 24h 过期
            token = utils.create_access_token(subject=created.email, expires_minutes=60 * 24)
            # 使用 url_for 生成你的后端地址（避免硬编码域名）
            verify_url = str(request.url_for("verify_email")) + f"?token={token}"
            utils.send_email(
                email=created.email,
                subject="Verify your email",
                body=f"Hello {created.username},\n\nPlease verify your email by clicking the link below:\n{verify_url}\n\nThis link expires in 24 hours.",
            )

        return created
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# 登录：未验证时返回 403；其它无效凭证返回 401
@router.post("/login", response_model=schemas.Token)
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    client_ip = utils.extract_client_ip(request)
    try:
        user = service.authenticate_user(db, form_data.username, form_data.password, login_ip=client_ip)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = utils.create_access_token(subject=user.username, expires_minutes=utils.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {"access_token": token, "token_type": "bearer"}

# 邮箱验证：点击邮件中的链接来到这里
@router.get("/verify-email", name="verify_email")
def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        payload = utils.decode_access_token(token)
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=400, detail="Invalid token payload")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        return {"message": "Email already verified"}

    user.is_verified = True
    db.commit()
    return {"message": "Email verified successfully"}


# ========== Me（恢复 & 最小化改动）==========
@router.get("/me", response_model=schemas.UserResponse)
def me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # 这里必须用“登录生成的 access token”，其 sub=username
    try:
        payload = utils.decode_access_token(token)
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token (no subject)")
    except JWTError as e:
        print("JWTError:", e)  # 临时日志
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 刷新活跃时间（统计在线时长时有用）
    service.touch_activity(db, user)
    return user


# ========== Logout ==========
@router.post("/logout", response_model=schemas.LogoutResponse)
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # 同样要求使用“登录 access token”（sub=username）
    try:
        payload = utils.decode_access_token(token)
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token (no subject)")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session_secs = service.logout_user(db, user)
    return {"session_seconds": session_secs, "total_online_seconds": user.total_online_seconds}
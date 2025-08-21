from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, Request
from jose import JWTError, jwt
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.auth import models
from app.auth.database import get_db
from app.auth.models import User, ApiUsageLog
from common.config import SECRET_KEY, ALGORITHM, MAX_USAGE_SECONDS_PER_HOUR  # 根據你的設定實際調整

def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    require_admin: bool = False  # ✅ 預設不要求管理員
) -> models.User:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None  # 匿名使用者

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Token 無效")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token 解碼失敗")

    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="用戶不存在")

    if require_admin and user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理員權限")

    return user


def check_api_usage_limit(
    db: Session,
    user: Optional[User],
    require_login: bool = False  # 如果这个接口必须登录，设为 True
) -> None:
    """
    - 未登录: 默认放行（可选登录）；如需强制登录，传 require_login=True。
    - 管理员: 不限流。
    - 普通用户: 最近 1 小时内 duration 累积不得超过 1800 秒。
    """
    # 1) 可选登录场景处理
    if user is None:
        if require_login:
            raise HTTPException(status_code=401, detail="💡 請先登入")
        # 匿名用户：无法按用户做配额，这里选择放行（如需限制可改为 raise 或基于 IP 做限流）
        return

    # 管理員不受限制
    if user.role == "admin":
        return

    one_hour_ago = datetime.utcnow() - timedelta(hours=1)

    total_duration = db.execute(
        select(func.coalesce(func.sum(ApiUsageLog.duration), 0))
        .where(ApiUsageLog.user_id == user.id)
        .where(ApiUsageLog.called_at >= one_hour_ago)
    ).scalar()

    if total_duration >= MAX_USAGE_SECONDS_PER_HOUR:
        raise HTTPException(status_code=429, detail="API使用已達每小時上限，請稍後再試")

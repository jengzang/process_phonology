from sqlalchemy import Column, Integer, String, DateTime, Boolean, func, ForeignKey, Float, Text
from sqlalchemy.orm import relationship

from sqlalchemy.orm import declarative_base
Base = declarative_base()
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # 基本資料
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    # full_name = Column(String(100), nullable=True)  # 可為空
    # phone = Column(String(20), nullable=True)  # 可為空

    # 角色/狀態
    role = Column(String(20), default="user")           # user/admin
    status = Column(String(20), default="active")       # active/disabled/banned
    is_verified = Column(Boolean, default=False)

    # 審計 & 行為
    # 下面時間默認存 UTC；如果要北京時區，改成 server_default=func.timezone('Asia/Shanghai', func.now()) (PostgreSQL)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    register_ip = Column(String(45), nullable=True)     # IPv4/IPv6
    last_login = Column(DateTime, nullable=True)
    last_login_ip = Column(String(45), nullable=True)

    login_count = Column(Integer, default=0)
    failed_attempts = Column(Integer, default=0)
    last_failed_login = Column(DateTime, nullable=True)

    # 在線時長（秒）
    total_online_seconds = Column(Integer, default=0)
    current_session_started_at = Column(DateTime, nullable=True)  # 登入成功時設置；登出時計入時長並清空
    last_seen = Column(DateTime, nullable=True)                   # 最近一次有有效 token 的請求時間

    profile_picture = Column(String(255), nullable=True)

    # informations = relationship("Information", back_populates="user")

class ApiUsageLog(Base):
    __tablename__ = "api_usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # optional: 若有 user 模型
    path = Column(String(255), nullable=False)
    duration = Column(Float, nullable=False)
    status_code = Column(Integer, nullable=False)
    ip = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    referer = Column(String(255), nullable=True)
    called_at = Column(DateTime, server_default=func.now())

    user = relationship("User", backref="api_logs")



from typing import List

from fastapi import APIRouter, HTTPException

from app.auth.models import User
from app.custom.database import SessionLocal as SessionLocal_info
from app.auth.database import SessionLocal as SessionLocal_user
from app.custom.models import Information
from app.schemas.admin import InformationBase

router = APIRouter()
@router.get("/all", response_model=List[InformationBase])
async def get_informations():
    # 使用兩個不同的 session
    session_info = SessionLocal_info()
    session_user = SessionLocal_user()

    try:
        informations = session_info.query(Information).all()
        result = []

        # 遍歷資料，根據 user_id 查找對應的 username
        for info in informations:
            user = session_user.query(User).filter(User.id == info.user_id).first()
            if user:
                result.append({
                    "簡稱": info.簡稱,
                    "音典分區": info.音典分區,
                    "經緯度": info.經緯度,
                    "特徵": info.特徵,
                    "值": info.值,
                    "說明": info.說明,
                    "username": user.username  # 加上對應的用戶名稱
                })
            else:
                result.append({
                    "id": info.id,
                    "error": "未找到對應的用戶"
                })

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    finally:
        # 關閉 session
        session_info.close()
        session_user.close()

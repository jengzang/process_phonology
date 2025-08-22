# routes/form_submit.py
"""
📦 路由模塊：處理 /api/submit_form 提交用戶填寫的語音資料。
"""

from fastapi import APIRouter, Request, HTTPException, Depends


from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.custom.database import get_db
from app.custom.delete import handle_form_deletion
from app.schemas import FormData
from app.custom.write_submit import handle_form_submission
import time
from app.service.api_logger import *

router = APIRouter()

@router.post("/submit_form")
async def submit_form(
    request: Request,
    payload: FormData,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    update_count(request.url.path)
    log_all_fields(request.url.path, payload.dict())
    start = time.time()

    try:
        result = handle_form_submission(payload.dict(), user, db)
        if not result.get("success"):
            raise HTTPException(status_code=422, detail=result.get("message"))
        return result
    except HTTPException:
        raise  # ✅ 让 HTTPException 保持原样传递
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="伺服器錯誤")
    finally:
        duration = time.time() - start
        log_detailed_api(
            request.url.path, duration, 200,
            request.client.host,
            request.headers.get("user-agent", ""),
            request.headers.get("referer", "")
        )

@router.post("/delete_form")
async def delete_form(
    request: Request,
    payload: FormData,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    update_count(request.url.path)
    log_all_fields(request.url.path, payload.dict())
    start = time.time()

    try:
        result = handle_form_deletion(payload.dict(), user, db)
        if not result.get("success"):
            raise HTTPException(status_code=422, detail=result.get("message"))
        return result
    except HTTPException:
        raise  # ✅ 让 HTTPException 保持原样传递
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="伺服器錯誤")
    finally:
        duration = time.time() - start
        log_detailed_api(
            request.url.path, duration, 200,
            request.client.host,
            request.headers.get("user-agent", ""),
            request.headers.get("referer", "")
        )
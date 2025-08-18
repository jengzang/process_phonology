# routes/form_submit.py
"""
📦 路由模塊：處理 /api/submit_form 提交用戶填寫的語音資料。
"""

from fastapi import APIRouter, Request, HTTPException
from app.schemas import FormData
from app.service.write_read_submit import handle_form_submission
import time
from app.service.api_logger import *

router = APIRouter()

@router.post("/api/submit_form")
async def submit_form(request: Request, payload: FormData):
    update_count(request.url.path)
    log_all_fields(request.url.path, payload.dict())
    start = time.time()
    try:
        print(payload.dict())
        handle_form_submission(payload.dict())
        return {"success": True, "message": "数据提交成功！"}
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=422, detail="数据格式错误")
    finally:
        duration = time.time() - start
        log_detailed_api(request.url.path, duration, 200, request.client.host, request.headers.get("user-agent", ""),
                         request.headers.get("referer", ""))

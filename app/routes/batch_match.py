# routes/batch_match.py
"""
📦 路由模塊：處理 /api/batch_match 地點名稱匹配。
"""

from fastapi import APIRouter, Request
from app.schemas import MatchRequest
from app.service.match_input_tip import match_locations_batch
import time
from app.service.api_logger import *

router = APIRouter()

@router.post("/api/batch_match")
async def batch_match(request: Request, data: MatchRequest):
    update_count(request.url.path)
    log_all_fields(request.url.path, data.dict())
    start = time.time()
    try:
        input_string = data.input_string.strip()
        if not input_string:
            return []
        results = match_locations_batch(input_string, data.filter_valid_abbrs_only)
        responses = []
        for idx, res in enumerate(results):
            part = re.split(r"[ ,;/，；、]+", input_string)[idx].strip()
            success = bool(res[1])
            if success:
                responses.append({
                    "success": True,
                    "message": f"“{part}”匹配成功",
                    "items": res[0]
                })
            else:
                merged, seen = [], set()
                for i in [0, 3, 5, 7]:
                    val = res[i]
                    if isinstance(val, list):
                        for item in val:
                            if item not in seen:
                                merged.append(item)
                                seen.add(item)
                    elif val not in seen:
                        merged.append(val)
                        seen.add(val)
                responses.append({
                    "success": False,
                    "message": f"第{idx + 1}個“{part}”未匹配",
                    "items": merged
                })
        return responses
    finally:
        duration = time.time() - start
        log_detailed_api(request.url.path, duration, 200, request.client.host, request.headers.get("user-agent", ""),
                         request.headers.get("referer", ""))

"""
📦 路由模塊：處理 /api/search_chars 與 /api/search_tones 查詢音節與聲調。
"""

from fastapi import APIRouter, Request, Query
from typing import List, Optional
from app.service.match_input_tip import match_locations_batch
from app.service.search_chars import search_characters
from common.search_tones import search_tones
import time
from app.service.api_logger import *

router = APIRouter()

@router.get("/api/search_chars/")
async def search_chars(
        request: Request,
        chars: List[str] = Query(..., description="要查的漢字序列"),
        locations: Optional[List[str]] = Query(None, description="要查的地點，可多個"),
        regions: Optional[List[str]] = Query(None, description="要查的音典分區，可多個（輸入某一級的音典分區）")
):
    """
    - 用于 /api/search_chars 查字，返回中古地位、對應地點的讀音及注釋。
    - chars-要查的漢字序列
    - locations-要查的地點，可多個
    - region-要查的音典分區，可多個（輸入某一級的音典分區）
    """
    update_count(request.url.path)
    log_all_fields(request.url.path, {"chars": chars, "locations": locations, "regions": regions})
    start = time.time()
    try:
        locations_processed = []
        for location in locations or []:
            matched = match_locations_batch(location)
            extracted = [res[0][0] for res in matched if res[0]]
            locations_processed.extend(extracted)
        result = search_characters(chars=chars, locations=locations_processed, regions=regions)
        return {"result": result}
    finally:
        duration = time.time() - start
        log_detailed_api(request.url.path, duration, 200,
                         request.client.host,
                         request.headers.get("user-agent", ""),
                         request.headers.get("referer", ""))


@router.get("/api/search_tones/")
async def search_tones_o(
        request: Request,
        locations: Optional[List[str]] = Query(None, description="要查的地點，可多個"),
        regions: Optional[List[str]] = Query(None, description="要查的音典分區，可多個（輸入某一級的音典分區）")
):
    """
    - 用于 /api/search_tones 查調，返回調值、調類。
    - locations-要查的地點，可多個
    - region-要查的音典分區，可多個（輸入某一級的音典分區）
    """
    update_count(request.url.path)
    log_all_fields(request.url.path, {"locations": locations, "regions": regions})
    start = time.time()
    try:
        locations_processed = []
        for location in locations or []:
            matched = match_locations_batch(location)
            extracted = [res[0][0] for res in matched if res[0]]
            locations_processed.extend(extracted)
        result = search_tones(locations=locations_processed, regions=regions)
        return {"tones_result": result}
    finally:
        duration = time.time() - start
        log_detailed_api(request.url.path, duration, 200,
                         request.client.host,
                         request.headers.get("user-agent", ""),
                         request.headers.get("referer", ""))

# routes/search.py
"""
📦 路由模塊：處理 /api/search_chars 與 /api/search_tones 查詢音節與聲調。
"""

from fastapi import APIRouter, Request
from app.schemas import SearchRequest, SearchRequest2
from app.service.match_input_tip import match_locations_batch
from app.service.search_chars import search_characters
from common.search_tones import search_tones
import time
from app.service.api_logger import *

router = APIRouter()

@router.post("/api/search_chars/")
async def search_chars(request: Request, data: SearchRequest):
    update_count(request.url.path)
    log_all_fields(request.url.path, data.dict())
    start = time.time()
    try:
        locations_processed = []
        for location in data.locations or []:
            matched = match_locations_batch(location)
            extracted = [res[0][0] for res in matched if res[0]]
            locations_processed.extend(extracted)
        result = search_characters(chars=data.chars, locations=locations_processed, regions=data.regions)
        return {"result": result}
    finally:
        duration = time.time() - start
        log_detailed_api(request.url.path, duration, 200, request.client.host, request.headers.get("user-agent", ""),
                         request.headers.get("referer", ""))


@router.post("/api/search_tones/")
async def search_tones_o(request: Request, data: SearchRequest2):
    update_count(request.url.path)
    log_all_fields(request.url.path, data.dict())
    start = time.time()
    try:
        locations_processed = []
        for location in data.locations or []:
            matched = match_locations_batch(location)
            extracted = [res[0][0] for res in matched if res[0]]
            locations_processed.extend(extracted)
        result = search_tones(locations=locations_processed, regions=data.regions)
        return {"tones_result": result}
    finally:
        duration = time.time() - start
        log_detailed_api(request.url.path, duration, 200, request.client.host, request.headers.get("user-agent", ""),
                         request.headers.get("referer", ""))


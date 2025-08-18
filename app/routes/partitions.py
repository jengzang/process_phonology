# routes/partitions.py
"""
📦 路由模塊：處理 /api/partitions 調用分區階層。
"""
import time
from typing import Optional

from fastapi import APIRouter, Request, Query
from app.service.match_input_tip import read_partition_hierarchy
from app.service.api_logger import *

router = APIRouter()

@router.get("/api/partitions")
async def api_get_partitions(request: Request, parent: Optional[str] = Query(None)):
    update_count(request.url.path)
    log_all_fields(request.url.path, {"parent": parent})
    start = time.time()
    try:
        result = read_partition_hierarchy(parent)
        return result
    finally:
        duration = time.time() - start
        log_detailed_api(request.url.path, duration, 200, request.client.host, request.headers.get("user-agent", ""),
                         request.headers.get("referer", ""))

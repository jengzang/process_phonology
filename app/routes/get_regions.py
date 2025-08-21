# app/routes/get_regions.py

from fastapi import APIRouter, Request, Query
from typing import List, Union

from app.service.locs_regions import fetch_dialect_region
from app.service.api_logger import update_count, log_all_fields, log_detailed_api
import time

router = APIRouter()

@router.get("/get_regions")
async def get_regions(
    request: Request,
    input_data: Union[str, List[str]] = Query(..., alias="input_data")
):
    """
    - :param request:地點簡稱
    - :return: 對應的音典分區
    """
    update_count(request.url.path)
    log_all_fields(request.url.path, {"input_data": input_data})
    start = time.time()
    try:
        return fetch_dialect_region(input_data)
    finally:
        duration = time.time() - start
        log_detailed_api(
            request.url.path,
            duration,
            200,
            request.client.host,
            request.headers.get("user-agent", ""),
            request.headers.get("referer", "")
        )

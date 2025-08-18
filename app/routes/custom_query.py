# routes/custom_query.py
"""
📦 路由模塊：處理 /api/get_custom 及 /api/get_custom_feature 查詢提交資料。
"""

from fastapi import APIRouter, Request, HTTPException
from app.schemas import QueryParams, FeatureQueryParams
from app.service.write_read_submit import get_from_submission
from app.service.match_input_tip import match_custom_feature
import time
from app.service.api_logger import *

router = APIRouter()


@router.post("/api/get_custom")
async def query_location_data(request: Request, query_params: QueryParams):
    update_count(request.url.path)
    log_all_fields(request.url.path, query_params.dict())
    start = time.time()
    try:
        result = get_from_submission(query_params.locations, query_params.regions, query_params.need_features)
        if not result:
            raise HTTPException(status_code=404, detail="No matching data found")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        duration = time.time() - start
        log_detailed_api(request.url.path, duration, 200, request.client.host, request.headers.get("user-agent", ""),
                         request.headers.get("referer", ""))


@router.post("/api/get_custom_feature")
async def get_custom_feature(request: Request, query_params: FeatureQueryParams):
    update_count(request.url.path)
    log_all_fields(request.url.path, query_params.dict())
    start = time.time()
    try:
        result = match_custom_feature(
            query_params.locations,
            query_params.regions,
            query_params.word
        )
        if not result:
            raise HTTPException(status_code=404, detail="No matching features found")
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        duration = time.time() - start
        log_detailed_api(request.url.path, duration, 200, request.client.host, request.headers.get("user-agent", ""),
                         request.headers.get("referer", ""))

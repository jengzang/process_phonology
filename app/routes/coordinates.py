# routes/coordinates.py
"""
📦 路由模塊：處理 /api/get_coordinates 查詢地點座標資料。
"""

from fastapi import APIRouter, Request, Query, HTTPException
from app.service.locs_regions import get_coordinates_from_db
from common.getloc_by_name_region import query_dialect_abbreviations
from app.service.match_input_tip import match_locations_batch
from common.config import SUPPLE_DB_PATH
import time
from app.service.api_logger import *

router = APIRouter()

@router.get("/api/get_coordinates")
async def get_coordinates(
        request: Request,
        regions: str = Query(...),
        locations: str = Query(...),
        iscustom: bool = None,
        flag: bool = True
):
    update_count(request.url.path)
    log_all_fields(request.url.path, {
        "regions": regions,
        "locations": locations,
        "iscustom": iscustom,
        "flag": flag
    })
    start = time.time()
    try:
        if not regions.strip() and not locations.strip():
            raise HTTPException(status_code=400, detail="請輸入地點或簡稱！")

        locations_list = locations.split(',')
        regions_list = regions.split(',')
        locations_processed = []
        for location in locations_list:
            matched = match_locations_batch(location)
            extracted = [res[0][0] for res in matched if res[0]]
            locations_processed.extend(extracted)

        if iscustom:
            abbr1 = query_dialect_abbreviations(regions_list, locations_list, db_path=SUPPLE_DB_PATH,
                                                tables="informations")
            abbr2 = query_dialect_abbreviations(regions_list, locations_processed, need_storage_flag=flag)
            result = get_coordinates_from_db(abbr2, abbr1, use_supplementary_db=True)
        else:
            abbrs = query_dialect_abbreviations(regions_list, locations_processed)
            result = get_coordinates_from_db(abbrs)

        return result
    finally:
        duration = time.time() - start
        log_detailed_api(request.url.path, duration, 200, request.client.host, request.headers.get("user-agent", ""),
                         request.headers.get("referer", ""))

# routes/get_coordinates.py
"""
📦 路由模塊：處理 /api/get_coordinates 查詢地點座標資料。
"""

from fastapi import APIRouter, Request, Query, HTTPException, Depends
from app.schemas import CoordinatesQuery
from app.service.locs_regions import get_coordinates_from_db
from common.getloc_by_name_region import query_dialect_abbreviations
from app.service.match_input_tip import match_locations_batch
from common.config import SUPPLE_DB_PATH
import time
from app.service.api_logger import *

router = APIRouter()

@router.get("/get_coordinates")
async def get_coordinates(
        request: Request,
        query: CoordinatesQuery = Depends()
):
    """
    獲取坐標
    :return: {"coordinates_locations": List of (簡稱, (緯度, 經度)),
             "region_mappings": Dict of {簡稱: 音典分區},
             "center_coordinate": [中心緯度, 中心經度] or None,
             "max_distances": {
                  "lat_km": 最大緯度距離 (float),
                  "lon_km": 最大經度距離 (float)
             },
             "zoom_level": 建議地圖縮放層級 (int) or None
            }

            說明:
            - coordinates_locations : [(str, (float, float))]，每個簡稱及其經緯度
            - region_mappings       : {str: str}，每個簡稱對應的音典分區
            - center_coordinate     : [float, float]，所有地點的中心座標點（若無資料則為 None）
            - max_distances         : 緯度與經度方向的最大距離，單位為公里
            - zoom_level            : 根據距離推算的地圖縮放層級，數字越大放大越多（2–20）
    """
    update_count(request.url.path)
    log_all_fields(request.url.path, query.dict())
    start = time.time()
    try:
        if not query.regions.strip() and not query.locations.strip():
            raise HTTPException(status_code=400, detail="請輸入地點或簡稱！")

        locations_list = query.locations.split(',')
        regions_list = query.regions.split(',')
        locations_processed = []

        for location in locations_list:
            matched = match_locations_batch(location)
            extracted = [res[0][0] for res in matched if res[0]]
            locations_processed.extend(extracted)

        if query.iscustom:
            abbr1 = query_dialect_abbreviations(regions_list, locations_list, db_path=SUPPLE_DB_PATH,
                                                tables="informations")
            abbr2 = query_dialect_abbreviations(regions_list, locations_processed, need_storage_flag=query.flag)
            result = get_coordinates_from_db(abbr2, abbr1, use_supplementary_db=True)
        else:
            abbrs = query_dialect_abbreviations(regions_list, locations_processed)
            result = get_coordinates_from_db(abbrs)

        return result

    except HTTPException as e:
        # 如果捕捉到 HTTPException 类型的错误，则返回它本身的错误信息
        raise HTTPException(status_code=e.status_code, detail=f"錯誤信息: {e.detail}")

    except Exception as e:
        # 其他异常类型，返回详细错误信息
        raise HTTPException(status_code=500, detail=f"處理過程中出現錯誤: {str(e)}")

    finally:
        duration = time.time() - start
        log_detailed_api(request.url.path, duration, 200, request.client.host, request.headers.get("user-agent", ""),
                         request.headers.get("referer", ""))

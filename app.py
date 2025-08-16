import os
import sys
import threading
import time
import webbrowser
import asyncio
import re
import pandas as pd
from typing import List, Optional, Union

import uvicorn
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from main import run_phonology_analysis
from source.Extras_addplaces_searchchars import fetch_dialect_region, handle_form_submission, get_from_submission, \
    search_characters, search_tones, match_custom_feature
from source.config import SUPPLE_DB_PATH
from source.process_input import read_partition_hierarchy, match_locations_batch, query_dialect_abbreviations, \
    get_coordinates_from_db

# 引入日志统计模块
from logs.api_logger  import update_count, log_detailed_api, log_all_fields

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# 静态资源

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)


app.mount("/css", StaticFiles(directory=get_resource_path("css")), name="css")
app.mount("/js", StaticFiles(directory=get_resource_path("js")), name="js")
app.mount("/source", StaticFiles(directory=get_resource_path("source")), name="source")
app.mount("/data", StaticFiles(directory=get_resource_path("data")), name="data")


@app.get("/", response_class=HTMLResponse)
async def index():
    index_path = get_resource_path("index.html")
    with open(index_path, encoding="utf-8") as f:
        content = f.read()
    headers = {"Cache-Control": "no-cache, must-revalidate"}
    return HTMLResponse(content=content, headers=headers)


# === API Models ===
class AnalysisPayload(BaseModel):
    mode: str
    locations: List[str] = Field(default_factory=list)
    regions: List[str] = Field(default_factory=list)
    features: List[str] = Field(default_factory=list)
    status_inputs: Union[str, List[str], None] = None
    group_inputs: Union[str, List[str], None] = None
    pho_values: Union[str, List[str], None] = None


@app.post("/api/phonology")
async def api_run_phonology_analysis(request: Request, payload: AnalysisPayload):
    update_count(request.url.path)
    log_all_fields(request.url.path, payload.dict())
    start = time.time()
    try:
        result = await asyncio.to_thread(run_phonology_analysis, **payload.dict())
        status = 200
        if isinstance(result, pd.DataFrame):
            return {"success": True, "results": result.to_dict(orient="records")}
        if isinstance(result, list) and all(isinstance(df, pd.DataFrame) for df in result):
            merged = pd.concat(result, ignore_index=True)
            return {"success": True, "results": merged.to_dict(orient="records")}
        return {"success": False, "error": "未識別的分析結果格式"}
    except Exception as e:
        status = 500
        return {"success": False, "error": str(e)}
    finally:
        duration = time.time() - start
        log_detailed_api(request.url.path, duration, status, request.client.host, request.headers.get("user-agent", ""),
                         request.headers.get("referer", ""))


@app.get("/api/partitions")
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


class MatchRequest(BaseModel):
    input_string: str
    filter_valid_abbrs_only: bool = True  # 默认值为 True


@app.post("/api/batch_match")
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


@app.get("/api/get_regions")
async def get_regions(request: Request, input_data: Union[str, List[str]] = Query(..., alias="input_data")):
    update_count(request.url.path)
    log_all_fields(request.url.path, {"input_data": input_data})
    start = time.time()
    try:
        return fetch_dialect_region(input_data)
    finally:
        duration = time.time() - start
        log_detailed_api(request.url.path, duration, 200, request.client.host, request.headers.get("user-agent", ""),
                         request.headers.get("referer", ""))


@app.get("/api/get_coordinates")
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


class FormData(BaseModel):
    location: str
    region: str
    coordinates: str
    feature: str
    value: str
    description: Optional[str] = None


@app.post("/api/submit_form")
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


class QueryParams(BaseModel):
    locations: List[str]
    regions: List[str]
    need_features: List[str]


@app.post("/api/get_custom")
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


class FeatureQueryParams(BaseModel):
    locations: List[str]
    regions: List[str]
    word: str


@app.post("/api/get_custom_feature")
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


class SearchRequest(BaseModel):
    chars: List[str]
    locations: List[str] = None
    regions: List[str] = None


@app.post("/api/search_chars/")
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


class SearchRequest2(BaseModel):
    locations: List[str] = None
    regions: List[str] = None


@app.post("/api/search_tones/")
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


# 启动服务并自动打开浏览器
if __name__ == "__main__":
    def open_browser():
        time.sleep(1)
        webbrowser.open("http://10.250.101.238:5000")


    threading.Thread(target=open_browser).start()
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)

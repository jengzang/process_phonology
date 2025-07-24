from typing import List, Optional, Union

import httpx
import uvicorn
from pydantic import BaseModel, Field
import asyncio
import pandas as pd
import re

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from main import run_phonology_analysis
from source.Extras_addplaces_searchchars import fetch_dialect_region, handle_form_submission, get_from_submission, \
    search_characters, search_tones
from source.config import SUPPLE_DB_PATH
from source.process_input import read_partition_hierarchy, match_locations_batch, query_dialect_abbreviations, \
    get_coordinates_from_db

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class AnalysisPayload(BaseModel):
    mode: str
    locations: List[str] = Field(default_factory=list)
    regions: List[str] = Field(default_factory=list)
    features: List[str] = Field(default_factory=list)
    status_inputs: Union[str, List[str], None] = None
    group_inputs: Union[str, List[str], None] = None
    pho_values: Union[str, List[str], None] = None


@app.post("/api/phonology")
async def api_run_phonology_analysis(payload: AnalysisPayload):
    try:
        analysis_result = await asyncio.to_thread(
            run_phonology_analysis,
            mode=payload.mode,
            locations=payload.locations,
            regions=payload.regions,
            features=payload.features,
            status_inputs=payload.status_inputs,
            group_inputs=payload.group_inputs,
            pho_values=payload.pho_values
        )

        # 假設只回傳一個 DataFrame
        if isinstance(analysis_result, pd.DataFrame):
            return {
                "success": True,
                "results": analysis_result.to_dict(orient="records")
            }

        # 若是清單，合併所有 DataFrame
        if isinstance(analysis_result, list) and all(isinstance(df, pd.DataFrame) for df in analysis_result):
            merged_df = pd.concat(analysis_result, ignore_index=True)
            return {
                "success": True,
                "results": merged_df.to_dict(orient="records")
            }

        return {
            "success": False,
            "error": "未識別的分析結果格式"
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/partitions")
async def api_get_partitions(parent: Optional[str] = Query(None)):
    try:
        result = read_partition_hierarchy(parent)
        return result
    except Exception as e:
        return {"error": str(e)}


class MatchRequest(BaseModel):
    input_string: str
    filter_valid_abbrs_only: bool = True  # 默认值为 True


@app.post("/api/batch_match")
async def batch_match(data: MatchRequest):
    input_string = data.input_string.strip()
    filter_valid_abbrs_only = data.filter_valid_abbrs_only  # 从请求体获取这个值
    if not input_string:
        return []

    results = match_locations_batch(input_string, filter_valid_abbrs_only)
    responses = []

    for idx, res in enumerate(results):
        part = re.split(r"[ ,;/，；、]+", input_string)[idx].strip()
        success = bool(res[1])
        if success:
            responses.append({
                "success": True,
                "message": f"第{idx + 1}個“{part}”匹配成功",
                "items": res[0]
            })
        else:
            merged = []
            seen = set()  # 用來跟踪已經加入 merged 的元素
            for i in [0, 3, 5, 7]:
                val = res[i]
                if isinstance(val, list):
                    for item in val:
                        if item not in seen:  # 確保只加入未添加過的元素
                            merged.append(item)
                            seen.add(item)
                else:
                    if val not in seen:  # 確保只加入未添加過的元素
                        merged.append(val)
                        seen.add(val)

            responses.append({
                "success": False,
                "message": f"第{idx + 1}個“{part}”未匹配",
                "items": merged  # 保留順序，並確保不重複
            })

    return responses


@app.get("/api/get_regions")
async def get_regions(input_data: Union[str, List[str]] = Query(..., alias="input_data")):
    # 调用重构后的函数
    return fetch_dialect_region(input_data)


@app.get("/api/get_coordinates")
async def get_coordinates(
        regions: str = Query(...),
        locations: str = Query(...),
        iscustom: bool = None  # 默认值为 None
):
    # 处理传入的字符串，转化为列表
    locations_list = locations.split(',')  # 用逗号分隔字符串，转换为列表
    regions_list = regions.split(',')  # 同样处理 regions

    # Step 2: 如果 iscustom 为 True，则进行特殊处理
    if iscustom:  # 如果 iscustom 被设置为 True
        # 在这里添加自定义处理逻辑
        abbreviations_list1 = query_dialect_abbreviations(regions_list, locations_list,
                                                          db_path=SUPPLE_DB_PATH, tables="informations")
        abbreviations_list2 = query_dialect_abbreviations(regions_list, locations_list)
        result = get_coordinates_from_db(abbreviations_list2, abbreviations_list1,
                                         use_supplementary_db=True)

    else:
        # 默认行为，调用数据库获取坐标
        # Step 1: 查询方言缩写列表，基于 regions 和 locations
        abbreviations_list = query_dialect_abbreviations(regions_list, locations_list)
        result = get_coordinates_from_db(abbreviations_list)

    return result


class FormData(BaseModel):
    location: str
    region: str
    coordinates: str
    feature: str
    value: str
    description: Optional[str] = None  # 允许为空


@app.post("/api/submit_form")
async def submit_form(payload: FormData):
    try:
        # 打印接收到的数据
        print(payload.dict())
        # 调用处理表单数据的函数
        handle_form_submission(payload.dict())
        return {"success": True, "message": "数据提交成功！"}
    except Exception as e:
        # 捕获并打印异常，方便调试
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=422, detail="数据格式错误")


# 定义输入数据模型
class QueryParams(BaseModel):
    locations: List[str]
    regions: List[str]
    need_features: List[str]


@app.post("/api/get_custom")
async def query_location_data(query_params: QueryParams):
    try:
        print("嘗試自用數據庫")
        # 调用数据库查询函数
        result = get_from_submission(query_params.locations, query_params.regions, query_params.need_features)
        print("自用數據庫讀取成功！")
        # 如果结果为空，返回404
        if not result:
            raise HTTPException(status_code=404, detail="No matching data found")

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class SearchRequest(BaseModel):
    chars: List[str]  # List of characters to search for
    locations: List[str] = None  # List of locations (optional)
    regions: List[str]= None  # List of regions (optional)


@app.post("/api/search_chars/")
async def search_chars(request: SearchRequest):
    # print(request.chars)
    # print(request.locations)
    # print(request.regions)
    # print("开始运行")
    try:
        # Call the search_characters function with the provided parameters
        result = search_characters(chars=request.chars, locations=request.locations, regions=request.regions)

        # Return the result
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SearchRequest2(BaseModel):
    locations: List[str] = None  # List of locations (optional)
    regions: List[str]= None  # List of regions (optional)
@app.post("/api/search_tones/")
async def search_tones_o(request: SearchRequest2):
    try:
        # Call the search_characters function with the provided parameters
        result = search_tones(locations=request.locations, regions=request.regions)

        # Return the result
        return {"tones_result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @app.get("/proxy")
# async def proxy(url: str):
#     # 使用 httpx 获取目标 URL 的响应
#     async with httpx.AsyncClient() as client:
#         response = await client.get(url)
#
#     # 返回目标 URL 的响应内容
#     return JSONResponse(content=response.json(), status_code=response.status_code)

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)

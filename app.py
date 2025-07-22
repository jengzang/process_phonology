from typing import List, Optional, Union

import httpx
import uvicorn
from pydantic import BaseModel, Field
import asyncio
import pandas as pd
import re

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from main import run_phonology_analysis
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


# @app.get("/proxy")
# async def proxy(url: str):
#     # 使用 httpx 获取目标 URL 的响应
#     async with httpx.AsyncClient() as client:
#         response = await client.get(url)
#
#     # 返回目标 URL 的响应内容
#     return JSONResponse(content=response.json(), status_code=response.status_code)


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


@app.post("/batch_match")
async def batch_match(data: MatchRequest):
    input_string = data.input_string.strip()
    if not input_string:
        return []

    results = match_locations_batch(input_string)
    responses = []

    for idx, res in enumerate(results):
        part = re.split(r"[ ,;/，；、]+", input_string)[idx].strip()
        success = bool(res[1])
        if success:
            responses.append({
                "success": True,
                "message": f"✅ 第{idx + 1}個“{part}”匹配成功",
                "items": []
            })
        else:
            merged = set()
            for i in [0, 3, 5, 7]:
                val = res[i]
                if isinstance(val, list):
                    merged.update(val)
                else:
                    merged.add(val)
            responses.append({
                "success": False,
                "message": f"第{idx + 1}個“{part}”未匹配",
                "items": list(merged)
            })

    return responses

@app.get("/get_coordinates")
async def get_coordinates(regions: str = Query(...), locations: str = Query(...)):
    # 处理传入的字符串，转化为列表
    locations_list = locations.split(',')  # 用逗号分隔字符串，转换为列表
    regions_list = regions.split(',')  # 同样处理 regions

    # Step 1: Query the dialect abbreviations based on regions and locations
    abbreviations_list = query_dialect_abbreviations(regions_list, locations_list)

    # Step 2: Get the coordinates and other information from the database
    result = get_coordinates_from_db(abbreviations_list)

    return result


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)

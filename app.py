from typing import List, Optional, Union

import uvicorn
from pydantic import BaseModel, Field
import asyncio
import pandas as pd
import re

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from main import run_phonology_analysis
from source.process_input import read_partition_hierarchy, match_locations_batch

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


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)

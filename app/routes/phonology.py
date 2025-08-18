# routes/phonology.py
"""
📦 路由模塊：處理 /api/phonology 音韻分析請求。
不改動原邏輯，將原來 app.py 中對應接口移出。
"""

import asyncio
import time

import pandas as pd
from fastapi import APIRouter, Request

from app.schemas import AnalysisPayload
from app.service.phonology2status import pho2sta
from app.service.status_arrange_pho import sta2pho
from app.service.api_logger import update_count, log_all_fields, log_detailed_api


router = APIRouter()

@router.post("/api/phonology")
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


def run_phonology_analysis(
        mode: str,
        locations: list,
        regions: list,
        features: list,
        status_inputs: list = None,
        group_inputs: list = None,
        pho_values: list = None
):
    """
    統一介面函數：根據 mode ('s2p' 或 'p2s') 執行 sta2pho 或 pho2sta。

    參數：
        mode: 's2p' = 語音條件 ➝ 統計；'p2s' = 特徵值 ➝ 統計
        locations: 方言點名稱
        features: 語音特徵欄位
        status_inputs: 語音條件字串（如 '知組三'），僅限 's2p'
        group_inputs: 要分組的欄位（如 '組聲'），僅限 'p2s'
        pho_values: 音值條件（如 ['l', 'm', 'an']），僅限 'p2s'

    回傳：
        List[pd.DataFrame]
    """

    if mode == 's2p':
        # if not status_inputs:
        #     raise ValueError("🔴 mode='s2p' 時，請提供 status_inputs。")
        return sta2pho(locations, regions, features, status_inputs)

    elif mode == 'p2s':
        # if not group_inputs :
        #     raise ValueError("🔴 mode='p2s' 時，請提供 group_inputs ")
        return pho2sta(locations, regions, features, group_inputs, pho_values)


    else:
        raise ValueError("🔴 mode 必須為 's2p' 或 'p2s'")

# schemas/query.py

from pydantic import BaseModel
from typing import List

class QueryParams(BaseModel):
    """
    用于 /api/get_custom 查詢某些地點的語音特徵。
    """
    locations: List[str]
    regions: List[str]
    need_features: List[str]

class FeatureQueryParams(BaseModel):
    """
    用于 /api/get_custom_feature 查詢特定詞的語音特徵。
    """
    locations: List[str]
    regions: List[str]
    word: str

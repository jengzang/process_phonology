# schemas/search.py

from pydantic import BaseModel
from typing import List, Optional

class SearchRequest(BaseModel):
    """
    用于 /api/search_chars 查字，返回中古地位、對應地點的讀音及注釋。
    chars-要查的漢字序列
    locations-要查的地點，可多個
    region-要查的音典分區，可多個（輸入某一級的音典分區）
    """
    chars: List[str]
    locations: Optional[List[str]] = None
    regions: Optional[List[str]] = None

class SearchRequest2(BaseModel):
    """
    用于 /api/search_tones 查調，返回調值、調類。
    locations-要查的地點，可多個
    region-要查的音典分區，可多個（輸入某一級的音典分區）
    """
    locations: Optional[List[str]] = None
    regions: Optional[List[str]] = None

# schemas/search.py

from pydantic import BaseModel
from typing import List, Optional

class SearchRequest(BaseModel):
    """
    用于 /api/search_chars 的字符查詢模型。
    """
    chars: List[str]
    locations: Optional[List[str]] = None
    regions: Optional[List[str]] = None

class SearchRequest2(BaseModel):
    """
    用于 /api/search_tones 的語調查詢模型。
    """
    locations: Optional[List[str]] = None
    regions: Optional[List[str]] = None

# schemas/match.py

from pydantic import BaseModel

class MatchRequest(BaseModel):
    """
    用于 /api/batch_match 路由的地點匹配請求模型。
    """
    input_string: str
    filter_valid_abbrs_only: bool = True

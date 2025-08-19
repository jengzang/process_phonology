# schemas/match.py

from pydantic import BaseModel

class MatchRequest(BaseModel):
    """
    用于 /api/batch_match 路由，匹配用戶輸入的地點，並提示正確的地點。
    - input_string-用戶輸入的字符串，用於後端匹配正確的地點
    - filter_valid_abbrs_only-是否過濾沒有字表的簡稱（若為真則過濾）
    - 返回值：
        "success": bool,代表是否找到完全相同的
        "message": 提示信息,
        "items": 所有匹配的地點序列
    """
    input_string: str
    filter_valid_abbrs_only: bool = True

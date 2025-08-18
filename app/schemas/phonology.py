# schemas/phonology.py

from pydantic import BaseModel, Field
from typing import List, Union, Optional

class AnalysisPayload(BaseModel):
    """
    用于 /api/phonology 路由的分析请求模型。
    """
    mode: str
    locations: List[str] = Field(default_factory=list)
    regions: List[str] = Field(default_factory=list)
    features: List[str] = Field(default_factory=list)
    status_inputs: Union[str, List[str], None] = None
    group_inputs: Union[str, List[str], None] = None
    pho_values: Union[str, List[str], None] = None

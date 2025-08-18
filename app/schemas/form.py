# schemas/form.py

from pydantic import BaseModel
from typing import Optional

class FormData(BaseModel):
    """
    用于 /api/submit_form 的表單提交模型。
    """
    location: str
    region: str
    coordinates: str
    feature: str
    value: str
    description: Optional[str] = None

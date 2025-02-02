from pydantic import BaseModel
from typing import Optional, List, Dict


class CodeAnalysisRequest(BaseModel):
    code: str
    context: Optional[str] = None
    user_prompt: Optional[str] = None

from pydantic import BaseModel
from typing import Optional, List, Dict


class LogAnalysisRequest(BaseModel):
    code: str
    logs: str
    context: Optional[str] = ""
    type: str = "terminal_logs"
    format: str = "text"
    user_prompt: Optional[str] = None

from pydantic import BaseModel
from typing import Optional, List, Dict


class RefactorRequest(BaseModel):
    code: str
    file_type: str
    context: list | None
    user_prompt: Optional[str] = None
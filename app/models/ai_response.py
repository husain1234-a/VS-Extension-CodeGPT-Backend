from pydantic import BaseModel
from typing import Optional, List, Dict


class AIResponse(BaseModel):
    content: str
    suggestions: Optional[List[str]] = None
    code_snippets: Optional[List[Dict[str, str]]] = None

from pydantic import BaseModel
from typing import Optional, List, Dict


class CodeAnalysisRequest(BaseModel):
    code: str
    context: Optional[str] = None


class LogAnalysisRequest(BaseModel):
    logs: str
    context: Optional[str] = ""
    type: str = "terminal_logs"
    format: str = "text"


class RefactorRequest(BaseModel):
    code: str
    file_type: str
    context: list | None


class AIResponse(BaseModel):
    content: str
    suggestions: Optional[List[str]] = None
    code_snippets: Optional[List[Dict[str, str]]] = None


class ErrorDetail(BaseModel):
    error_type: str
    message: str
    line_number: Optional[int]
    suggestion: str

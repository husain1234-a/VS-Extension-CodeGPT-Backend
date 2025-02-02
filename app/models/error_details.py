from pydantic import BaseModel
from typing import Optional, List, Dict


class ErrorDetail(BaseModel):
    error_type: str
    message: str
    line_number: Optional[int]
    suggestion: str

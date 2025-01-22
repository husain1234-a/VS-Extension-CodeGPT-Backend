from fastapi import APIRouter, HTTPException
from app.models.schemas import CodeAnalysisRequest, AIResponse, LogAnalysisRequest
from app.services.ai_service import AIService

router = APIRouter()
ai_service = AIService()


@router.post("/analyze", response_model=AIResponse)
async def analyze_code(request: CodeAnalysisRequest):
    try:
        return await ai_service.analyze_code(request.code, request.context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



from fastapi import APIRouter, HTTPException
from app.models.schemas import CodeAnalysisRequest, AIResponse, LogAnalysisRequest
from app.services.ai_service import AIService

router = APIRouter()
ai_service = AIService()


@router.post("/debug", response_model=AIResponse)
async def debug_logs(request: LogAnalysisRequest):
    try:
        return await ai_service.analyze_logs(request.logs, request.context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, HTTPException
from app.models.schemas import CodeAnalysisRequest, AIResponse
from app.services.ai_service import AIService
from app.services.code_service import CodeService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
ai_service = AIService()

@router.post("/analyze", response_model=AIResponse)
async def analyze_code(request: CodeAnalysisRequest):
    try:
        logger.info(f"Received code analysis request: {request.code} with context: {request.context}")
        
        response = await ai_service.analyze_code(request.code, request.context)
        
        logger.info(f"Code analysis response: {response}")
        
        return response
    
    except Exception as e:
        logger.error(f"Error analyzing code: {str(e)}")
        
        raise HTTPException(status_code=500, detail=str(e))
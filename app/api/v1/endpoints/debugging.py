from fastapi import APIRouter, HTTPException
from app.models.schemas import LogAnalysisRequest, AIResponse
from app.services.ai_service import AIService
from app.services.log_service import LogService
from typing import Optional
import os

router = APIRouter()
ai_service = AIService()
log_service = LogService()


async def read_log_file(file_path: str) -> Optional[str]:
    """Safely read log file contents."""
    try:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        return None
    except Exception as e:
        print(f"Error reading log file: {str(e)}")
        return None


@router.post("/debug", response_model=AIResponse)
async def debug_logs(request: LogAnalysisRequest):
    try:
        # Handle log input (string or file path)
        logs = request.logs
        if isinstance(logs, str) and os.path.exists(logs):
            file_content = await read_log_file(logs)
            if file_content:
                logs = file_content
            else:
                raise HTTPException(
                    status_code=400, detail="Unable to read log file or file is empty"
                )

        if not logs or not logs.strip():
            raise HTTPException(status_code=400, detail="No logs provided for analysis")

        # Use LogService to analyze logs first
        try:
            log_analysis = log_service.analyze_logs(logs)

            # Enhance the context with LogService analysis
            enhanced_context = {
                "user_context": request.context,
                "log_analysis": {
                    "total_entries": log_analysis["total_entries"],
                    "error_count": log_analysis["error_count"],
                    "error_rate": log_analysis["summary"]["error_rate"],
                    "level_distribution": log_analysis["summary"]["level_distribution"],
                    "detected_errors": [
                        {
                            "type": error.error_type,
                            "message": error.message,
                            "line_number": error.line_number,
                            "suggestion": error.suggestion,
                        }
                        for error in log_analysis["errors"]
                    ],
                },
            }

            # Send enhanced analysis to AI service
            response = await ai_service.analyze_logs(
                logs=logs, context=enhanced_context
            )

            if not response or not response.content:
                raise HTTPException(
                    status_code=500, detail="AI service returned empty response"
                )

            return response

        except Exception as log_error:
            print(f"LogService analysis failed: {str(log_error)}")
            # Fall back to basic AI analysis if LogService fails
            response = await ai_service.analyze_logs(logs=logs, context=request.context)
            return response

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error analyzing logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze logs: {str(e)}")

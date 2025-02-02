import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from app.models.ai_response import AIResponse
from app.services.ai_service import AIService
from app.services.code_service import CodeService
from app.models.code_analysis_request import CodeAnalysisRequest

logger = logging.getLogger(__name__)
router = APIRouter()
ai_service = AIService()
code_service = CodeService()


@router.post("/analyze", response_model=AIResponse)
async def analyze_code(request: CodeAnalysisRequest):
    try:
        logger.info("Starting code analysis")

        if not request.code or not request.code.strip():
            raise HTTPException(status_code=400, detail="No code provided for analysis")

        try:
            ast_tree = code_service.parse_code(request.code)
            code_analysis = code_service.analyze_structure(ast_tree)

            optimized_code = code_service.refactor_code(
                request.code, "optimize_imports"
            )
            formatted_code = code_service.refactor_code(optimized_code, "format")

            enhanced_context = {
                "user_context": request.context,
                "code_analysis": {
                    "structure": code_analysis,
                    "metrics": {
                        "total_imports": len(code_analysis["imports"]),
                        "total_functions": len(code_analysis["functions"]),
                        "total_classes": len(code_analysis["classes"]),
                        "complexity": code_analysis["complexity"],
                    },
                    "improvements": {
                        "optimized_imports": optimized_code != request.code,
                        "formatting_changes": formatted_code != request.code,
                    },
                },
            }

            if code_analysis["functions"]:
                enhanced_context["code_analysis"]["function_details"] = {
                    func["name"]: {
                        "argument_count": func["args"],
                        "line_number": func["line_number"],
                    }
                    for func in code_analysis["functions"]
                }

            if code_analysis["classes"]:
                enhanced_context["code_analysis"]["class_details"] = {
                    cls["name"]: {
                        "method_count": cls["methods"],
                        "line_number": cls["line_number"],
                    }
                    for cls in code_analysis["classes"]
                }

            response = await ai_service.analyze_code(
                code=request.code,
                context=enhanced_context,
                user_prompt=request.user_prompt,
            )

            if not response or not response.content:
                raise HTTPException(
                    status_code=500, detail="AI service returned empty response"
                )

            return response

        except Exception as code_error:
            logger.error(f"Code analysis failed: {str(code_error)}")
            response = await ai_service.analyze_code(
                code=request.code,
                context=request.context,
                user_prompt=request.user_prompt,
            )
            return response

    except HTTPException as he:
        raise he
    except Exception as e:
        error_msg = f"Error analyzing code: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

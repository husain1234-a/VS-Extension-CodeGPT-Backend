from fastapi import APIRouter
from app.api.v1.endpoints import code_analysis, debugging, refactoring

api_router = APIRouter()

api_router.include_router(code_analysis.router)
api_router.include_router(debugging.router)
api_router.include_router(refactoring.router)

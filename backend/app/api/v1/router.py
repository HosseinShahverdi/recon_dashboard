from fastapi import APIRouter
from app.api.v1 import domains, tools

api_router = APIRouter()
api_router.include_router(domains.router, prefix="/domains", tags=["domains"])
api_router.include_router(tools.router, prefix="/tools", tags=["tools"])
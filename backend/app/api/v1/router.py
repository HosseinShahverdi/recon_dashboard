from fastapi import APIRouter
from app.api.v1 import domains, tools, scans, assets, stats

api_router = APIRouter()
api_router.include_router(domains.router, prefix="/domains", tags=["domains"])
api_router.include_router(tools.router, prefix="/tools", tags=["tools"])
api_router.include_router(scans.router, prefix="/scans", tags=["scans"])
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
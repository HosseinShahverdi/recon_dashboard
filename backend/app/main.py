from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.db.session import engine, Base
from app.api.v1.router import api_router
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Ensure the data directory exists
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    
    # 2. Create all database tables automatically on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    yield
    # (Cleanup logic goes here on shutdown if needed)

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# Allow the React frontend (Vite runs on 5173) to talk to the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Recon Dashboard API is running. Ready for Phase 3."}
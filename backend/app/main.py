from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.database.init_db import init_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("taskflow")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing TaskFlow AI Database on startup...")
    init_db()
    logger.info("TaskFlow AI Backend started successfully.")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Intelligent Project Management and Real-Time Collaboration Platform API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "ai_demo_mode": settings.AI_DEMO_MODE,
        "openai_configured": bool(settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith("sk-placeholder"))
    }

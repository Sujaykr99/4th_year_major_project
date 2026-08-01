"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime

from app.core.database import connect_to_mongo, close_mongo_connection
from app.core.config import settings
from app.ml.service import ml_service
from app.api.v1.endpoints import auth, profile, prediction, roadmap


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    # Load ML model
    if not ml_service.load():
        print("Warning: ML model failed to load. Predictions will not be available.")
    yield
    # Shutdown
    await close_mongo_connection()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Career Matrix API - AI-powered career prediction and guidance system",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    lifespan=lifespan,
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["auth"])
app.include_router(profile.router, prefix=f"{settings.API_V1_PREFIX}/profile", tags=["profile"])
app.include_router(prediction.router, prefix=f"{settings.API_V1_PREFIX}/predict", tags=["prediction"])
app.include_router(roadmap.router, prefix=f"{settings.API_V1_PREFIX}/roadmap", tags=["roadmap"])


@app.get("/", tags=["root"])
async def root():
    return {
        "message": "Welcome to Career Matrix API",
        "version": settings.APP_VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs",
    }


@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "model_loaded": ml_service.is_loaded,
    }

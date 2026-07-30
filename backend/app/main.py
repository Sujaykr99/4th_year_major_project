"""Main FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection, get_database
from app.core.security import get_current_user_id
from app.ml.service import ml_service

# Import routers
from app.api import auth, profile, predict, roadmap


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Career Matrix API...")
    await connect_to_mongo()

    # Load ML model
    ml_service.load_artifacts()

    yield

    # Shutdown
    print("Shutting down Career Matrix API...")
    await close_mongo_connection()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Career Prediction & Guidance System",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(predict.router)
app.include_router(roadmap.router)


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    db = get_database()
    try:
        # Ping database
        await db.command("ping")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": "healthy",
        "database": db_status,
        "ml_model": "loaded" if ml_service.is_loaded else "not loaded"
    }


@app.get("/api/v1/model/info")
async def model_info():
    """Get ML model information."""
    return ml_service.get_model_info()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
"""Application configuration using Pydantic Settings."""
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Career Matrix API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    MONGODB_URI: str = Field(default="mongodb://localhost:27017", env="MONGODB_URI")
    MONGODB_DB_NAME: str = Field(default="career_matrix", env="MONGODB_DB_NAME")

    # Security
    SECRET_KEY: str = Field(default="your-super-secret-key-change-in-production", env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 60  # 30 days

    # ML Model
    MODEL_PATH: str = Field(default="models/career_model.pkl", env="MODEL_PATH")
    SCALER_PATH: str = Field(default="models/scaler.pkl", env="SCALER_PATH")
    ENCODERS_PATH: str = Field(default="models/encoders.pkl", env="ENCODERS_PATH")
    SHAP_EXPLAINER_PATH: str = Field(default="models/shap_explainer.pkl", env="SHAP_EXPLAINER_PATH")

    # Dataset
    DATASET_PATH: str = Field(default="data/career_dataset.csv", env="DATASET_PATH")

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
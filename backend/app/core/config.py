from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "AIGC Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/aigc_db")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Storage
    UPLOAD_DIR: str = "uploads"
    GALLERY_DIR: str = "gallery"
    
    # Model Settings
    MODEL_PATH: str = os.getenv("MODEL_PATH", "runwayml/stable-diffusion-v1-5")
    DEVICE: str = "cuda" if os.getenv("USE_GPU", "1") == "1" else "cpu"
    
    # OpenAI配置
    OPENAI_API_KEY: str = ""
    
    # CORS配置
    CORS_ORIGINS: list = ["*"]
    
    class Config:
        case_sensitive = True

settings = Settings() 
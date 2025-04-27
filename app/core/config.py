from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 基础配置
    PROJECT_NAME: str = "AIGC图像生成平台"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # 路径配置
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    GALLERY_DIR: Path = BASE_DIR / "gallery"
    TEMPLATES_DIR: Path = BASE_DIR / "templates"
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./aimg.db"
    
    # AI引擎配置
    DEFAULT_AI_ENGINE: str = "stable_diffusion"
    AI_ENGINES: dict = {
        "stable_diffusion": {
            "name": "Stable Diffusion",
            "enabled": True,
            "api_key": "",
            "api_base": "http://localhost:7860"
        },
        "midjourney": {
            "name": "Midjourney",
            "enabled": False,
            "api_key": "",
            "api_base": ""
        }
    }
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # UI配置
    UI_THEME: str = "light"
    UI_LANGUAGE: str = "zh_CN"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

# 确保必要的目录存在
settings.GALLERY_DIR.mkdir(parents=True, exist_ok=True)
settings.TEMPLATES_DIR.mkdir(parents=True, exist_ok=True) 
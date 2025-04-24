from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="AI Image Generator API",
    description="Backend API for AI Image Generation",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 导入路由
from .routers import auth, images, users

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(images.router, prefix="/api/images", tags=["图片"])
app.include_router(users.router, prefix="/api/users", tags=["用户"]) 
from fastapi import APIRouter
from .routes import image_generation, models, users

router = APIRouter()
 
# 包含各个路由模块
router.include_router(image_generation.router, prefix="/images", tags=["images"])
router.include_router(models.router, prefix="/models", tags=["models"])
router.include_router(users.router, prefix="/users", tags=["users"]) 
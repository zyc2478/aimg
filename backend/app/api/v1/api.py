from fastapi import APIRouter
from app.api.v1.endpoints import images

api_router = APIRouter()
api_router.include_router(images.router, prefix="/images", tags=["images"]) 
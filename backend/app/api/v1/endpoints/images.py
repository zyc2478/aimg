from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.services.image_generation import ImageGenerationService
from app.schemas.image import ImageCreate, ImageResponse
from app.models.image import Image

router = APIRouter()
image_service = ImageGenerationService()

@router.post("/generate", response_model=ImageResponse)
async def generate_image(
    image_data: ImageCreate,
    db: Session = Depends(get_db)
):
    try:
        image = await image_service.generate_image(
            db=db,
            prompt=image_data.prompt,
            negative_prompt=image_data.negative_prompt,
            num_inference_steps=image_data.num_inference_steps,
            guidance_scale=image_data.guidance_scale,
            width=image_data.width,
            height=image_data.height
        )
        return image
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{image_id}", response_model=ImageResponse)
async def get_image(image_id: int, db: Session = Depends(get_db)):
    image = await image_service.get_image(db, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image

@router.get("/", response_model=List[ImageResponse])
async def list_images(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    images = await image_service.list_images(db, skip=skip, limit=limit)
    return images 
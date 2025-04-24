from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core import security
from ..schemas import image as image_schemas
from ..crud import image as image_crud
from ..database import get_db
from typing import List

router = APIRouter()

@router.post("/text-to-image", response_model=image_schemas.ImageResponse)
async def generate_text_to_image(
    prompt: image_schemas.ImagePrompt,
    current_user = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """文生图接口"""
    try:
        # 生成图片
        image_url = await image_crud.generate_text_to_image(prompt.prompt)
        # 保存到数据库
        image_crud.create_image(db, current_user.id, prompt.prompt, image_url)
        return {"url": image_url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/image-to-image", response_model=image_schemas.ImageResponse)
async def generate_image_to_image(
    prompt: image_schemas.ImageToImagePrompt,
    current_user = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """图生图接口"""
    try:
        # 生成图片
        image_url = await image_crud.generate_image_to_image(prompt.prompt, prompt.image_data)
        # 保存到数据库
        image_crud.create_image(db, current_user.id, prompt.prompt, image_url, is_variation=True)
        return {"url": image_url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/history", response_model=List[image_schemas.ImageHistory])
async def get_image_history(
    current_user = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """获取图片历史记录"""
    return image_crud.get_user_images(db, current_user.id) 
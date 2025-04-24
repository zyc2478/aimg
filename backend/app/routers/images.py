from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core import security
from ..schemas import image as image_schemas
from ..crud import image as image_crud
from ..database import get_db
from typing import List
from ..schemas.user import User

router = APIRouter()

@router.post("/text-to-image", response_model=image_schemas.ImageResponse)
async def text_to_image(
    prompt: image_schemas.ImagePrompt,
    current_user: User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """文生图接口"""
    try:
        # 生成图片
        image_url = await image_crud.generate_text_to_image(
            prompt=prompt.prompt,
            model=prompt.model
        )
        
        # 保存到数据库
        image = image_crud.create_image(
            db=db,
            user_id=current_user.id,
            prompt=prompt.prompt,
            image_url=image_url
        )
        
        return image_schemas.ImageResponse(
            success=True,
            message="图片生成成功",
            image_url=image_url
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/image-to-image", response_model=image_schemas.ImageResponse)
async def image_to_image(
    prompt: image_schemas.ImageToImagePrompt,
    current_user: User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """图生图接口"""
    try:
        # 生成图片
        image_url = await image_crud.generate_image_to_image(
            prompt=prompt.prompt,
            image_data=prompt.image_data,
            model=prompt.model
        )
        
        # 保存到数据库
        image = image_crud.create_image(
            db=db,
            user_id=current_user.id,
            prompt=prompt.prompt,
            image_url=image_url,
            is_variation=True
        )
        
        return image_schemas.ImageResponse(
            success=True,
            message="图片生成成功",
            image_url=image_url
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/my-images", response_model=List[image_schemas.ImageResponse])
async def get_my_images(
    current_user: User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的图片列表"""
    images = image_crud.get_user_images(db=db, user_id=current_user.id)
    return [
        image_schemas.ImageResponse(
            success=True,
            message="获取成功",
            image_url=image.image_url
        )
        for image in images
    ] 
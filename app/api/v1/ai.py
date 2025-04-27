from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pathlib import Path

from app.core.deps import get_current_active_user, get_db
from app.core.ai_engine import get_ai_engine
from app.models.user import User
from app.schemas.ai import (
    TextToImageRequest,
    ImageToImageRequest,
    ImageResponse,
    ModelList
)

router = APIRouter()

@router.post("/text-to-image", response_model=ImageResponse)
async def text_to_image(
    *,
    request: TextToImageRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """文生图"""
    try:
        engine = get_ai_engine(request.engine or "stable_diffusion")
        image_path = await engine.text_to_image(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            **request.parameters
        )
        return {"image_path": str(image_path)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/image-to-image", response_model=ImageResponse)
async def image_to_image(
    *,
    image: UploadFile = File(...),
    request: ImageToImageRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """图生图"""
    try:
        # 保存上传的图片
        temp_path = Path("temp") / image.filename
        temp_path.parent.mkdir(exist_ok=True)
        with temp_path.open("wb") as f:
            f.write(await image.read())
        
        engine = get_ai_engine(request.engine or "stable_diffusion")
        output_path = await engine.image_to_image(
            image_path=temp_path,
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            **request.parameters
        )
        
        # 清理临时文件
        temp_path.unlink()
        return {"image_path": str(output_path)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/models/{engine}", response_model=ModelList)
async def get_models(
    engine: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取可用模型列表"""
    try:
        ai_engine = get_ai_engine(engine)
        models = await ai_engine.get_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class ImageBase(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    num_inference_steps: int = 50
    guidance_scale: float = 7.5
    width: int = 512
    height: int = 512

class ImageCreate(ImageBase):
    pass

class ImageResponse(ImageBase):
    id: int
    filename: str
    parameters: Dict
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ImagePrompt(BaseModel):
    prompt: str
    model: str = "dall-e"  # 默认使用 DALL-E 模型

class ImageToImagePrompt(BaseModel):
    prompt: str
    image_data: str  # base64编码的图片数据
    model: str = "dall-e"  # 默认使用 DALL-E 模型

class ImageHistory(BaseModel):
    id: int
    user_id: int
    prompt: str
    image_url: str
    is_variation: bool
    created_at: datetime

    class Config:
        from_attributes = True 
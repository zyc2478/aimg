from pydantic import BaseModel
from datetime import datetime

class ImagePrompt(BaseModel):
    prompt: str

class ImageToImagePrompt(BaseModel):
    prompt: str
    image_data: str  # base64编码的图片数据

class ImageResponse(BaseModel):
    url: str

class ImageHistory(BaseModel):
    id: int
    user_id: int
    prompt: str
    image_url: str
    is_variation: bool
    created_at: datetime

    class Config:
        from_attributes = True 
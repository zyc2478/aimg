from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class TextToImageRequest(BaseModel):
    """文生图请求"""
    prompt: str
    negative_prompt: Optional[str] = None
    engine: Optional[str] = None
    parameters: Dict[str, Any] = {}

class ImageToImageRequest(BaseModel):
    """图生图请求"""
    prompt: str
    negative_prompt: Optional[str] = None
    engine: Optional[str] = None
    parameters: Dict[str, Any] = {}

class ImageResponse(BaseModel):
    """图片响应"""
    image_path: str

class ModelList(BaseModel):
    """模型列表响应"""
    models: List[Dict[str, Any]] 
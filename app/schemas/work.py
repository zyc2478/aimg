from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel

class WorkBase(BaseModel):
    """作品基础模型"""
    title: str
    description: Optional[str] = None
    prompt: str
    negative_prompt: Optional[str] = None
    parameters: Dict[str, Any] = {}
    ai_engine: str

class WorkCreate(WorkBase):
    """创建作品请求"""
    image_path: str

class WorkUpdate(BaseModel):
    """更新作品请求"""
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None

class WorkShare(BaseModel):
    """分享作品请求"""
    is_public: bool = False
    expires_in_hours: Optional[int] = None  # 分享链接有效期（小时）

class WorkResponse(WorkBase):
    """作品响应"""
    id: int
    image_path: str
    owner_id: int
    is_public: bool
    share_code: Optional[str] = None
    share_expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    tags: List[str] = []
    
    class Config:
        from_attributes = True

class WorkList(BaseModel):
    """作品列表响应"""
    total: int
    items: List[WorkResponse]

class SharedWorkResponse(WorkResponse):
    """分享作品响应"""
    owner_name: str 
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from ..database import Base

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    prompt = Column(String)
    image_url = Column(String)
    is_variation = Column(Boolean, default=False)  # 是否是图生图生成的图片
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 
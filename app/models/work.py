from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database.base_class import Base

class Work(Base):
    """作品模型"""
    __tablename__ = "works"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    image_path = Column(String(255), nullable=False)
    prompt = Column(Text, nullable=False)
    negative_prompt = Column(Text, nullable=True)
    parameters = Column(JSON, nullable=True)
    ai_engine = Column(String(50), nullable=False)
    
    # 分享相关字段
    is_public = Column(Boolean, default=False)
    share_code = Column(String(10), unique=True, nullable=True)
    share_expires_at = Column(DateTime, nullable=True)
    
    # 关联字段
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="works")
    tags = relationship("Tag", secondary="work_tags", back_populates="works")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 
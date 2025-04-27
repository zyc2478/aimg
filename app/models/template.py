from sqlalchemy import Column, String, Integer, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from .base import Base

class Template(Base):
    name = Column(String, index=True)
    description = Column(String)
    prompt_template = Column(String)  # 提示词模板
    negative_prompt_template = Column(String)  # 反向提示词模板
    parameters = Column(JSON)  # 默认参数
    is_public = Column(Boolean, default=False)  # 是否公开
    
    # 外键
    owner_id = Column(Integer, ForeignKey("user.id"))
    
    # 关联
    owner = relationship("User", back_populates="templates")
    category = relationship("Category", back_populates="templates")
    category_id = Column(Integer, ForeignKey("category.id")) 
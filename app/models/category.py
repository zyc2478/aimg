from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from .base import Base

class Category(Base):
    name = Column(String, unique=True, index=True)
    description = Column(String)
    
    # 关联
    templates = relationship("Template", back_populates="category") 
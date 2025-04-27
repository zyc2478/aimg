from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship
from .base import Base

class User(Base):
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # 关联
    works = relationship("Work", back_populates="owner")
    templates = relationship("Template", back_populates="owner") 
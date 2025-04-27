from sqlalchemy import Column, String, Table, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

# 作品-标签关联表
work_tags = Table(
    "work_tags",
    Base.metadata,
    Column("work_id", Integer, ForeignKey("work.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tag.id"), primary_key=True)
)

class Tag(Base):
    name = Column(String, unique=True, index=True)
    description = Column(String)
    
    # 关联
    works = relationship("Work", secondary=work_tags, back_populates="tags") 
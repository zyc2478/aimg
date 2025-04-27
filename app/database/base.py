from app.models.base import Base
from app.database.session import engine

# 创建所有表
def init_db():
    Base.metadata.create_all(bind=engine) 
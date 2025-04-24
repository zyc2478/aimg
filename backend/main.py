import uvicorn
from app import app
from app.database import engine
from app.models import user, image

# 创建数据库表
user.Base.metadata.create_all(bind=engine)
image.Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 
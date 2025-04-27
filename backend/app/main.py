import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
from app.core.config import settings
from app.api.v1.api import api_router
from app.database import Base, engine
import threading
from app.ui import run_ui

# 加载环境变量
load_dotenv()

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含API路由
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to AIGC Platform API"}

# 启动UI线程
def start_ui():
    run_ui()

if __name__ == "__main__":
    # 在新线程中启动UI
    ui_thread = threading.Thread(target=start_ui)
    ui_thread.daemon = True
    ui_thread.start()
    
    # 启动FastAPI
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

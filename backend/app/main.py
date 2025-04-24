import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = FastAPI(
    title="AI Image Generation API",
    description="基于 Stable Diffusion 的 AI 图像生成 API",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 导入路由
from app.api import router as api_router
app.include_router(api_router, prefix="/api")

# 导入 Gradio 界面
from app.gradio_app import create_gradio_app
gradio_app = create_gradio_app()
app.mount("/gradio", gradio_app)

@app.get("/")
async def root():
    return {
        "message": "Welcome to AI Image Generation API",
        "docs_url": "/docs",
        "gradio_url": "/gradio"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

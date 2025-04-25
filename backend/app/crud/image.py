from sqlalchemy.orm import Session
from ..models.image import Image
from ..schemas.image import ImagePrompt, ImageToImagePrompt
from ..core.config import get_settings
import openai
import base64
import os
import json
import requests
from io import BytesIO
from PIL import Image as PILImage
import logging
import uuid
import time
import asyncio
from pathlib import Path
from ..services.image_generator import ImageGenerator

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
openai.api_key = settings.OPENAI_API_KEY

# ComfyUI API 地址
COMFYUI_API_URL = "http://101.126.152.137:8188"

async def generate_text_to_image(prompt: str, model: str = "flux-t2v") -> str:
    """文生图功能，支持多种模型"""
    try:
        # 验证提示词不为空
        if not prompt or prompt.strip() == "":
            raise Exception("提示词不能为空")
            
        logger.info(f"开始生成图片，提示词: {prompt}，模型: {model}")
        
        if model.lower() == "flux-t2v":
            # 使用新的图像生成服务
            generator = ImageGenerator(host="101.126.152.137", port=8188)
            
            # 创建临时文件路径
            temp_dir = Path("temp")
            temp_dir.mkdir(exist_ok=True)
            output_path = temp_dir / f"{uuid.uuid4()}.png"
            
            # 生成图像
            await generator.generate_image(prompt, output_path)
            
            # 将图像转换为base64
            with open(output_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()
            
            # 删除临时文件
            os.remove(output_path)
            
            # 返回base64编码的图像数据
            return f"data:image/png;base64,{image_data}"
        else:
            raise Exception(f"不支持的模型: {model}")
            
    except Exception as e:
        logger.error(f"生成图片失败: {str(e)}")
        raise Exception(f"生成图片失败: {str(e)}")

async def generate_image_to_image(prompt: str, image_data: str, model: str = "flux-t2v") -> str:
    """图生图功能，支持多种模型"""
    try:
        # 验证提示词不为空
        if not prompt or prompt.strip() == "":
            raise Exception("提示词不能为空")
            
        # 验证图像数据不为空
        if not image_data or image_data.strip() == "":
            raise Exception("图像数据不能为空")
            
        logger.info(f"开始生成图片变体，提示词: {prompt}，模型: {model}")
        
        if model.lower() == "flux-t2v":
            # 使用新的图像生成服务
            generator = ImageGenerator(host="101.126.152.137", port=8188)
            
            # 创建临时文件路径
            temp_dir = Path("temp")
            temp_dir.mkdir(exist_ok=True)
            input_path = temp_dir / f"input_{uuid.uuid4()}.png"
            output_path = temp_dir / f"output_{uuid.uuid4()}.png"
            
            # 保存上传的图像
            image_bytes = base64.b64decode(image_data)
            with open(input_path, "wb") as f:
                f.write(image_bytes)
            
            # 生成图像变体
            # 注意：目前我们的图像生成服务不支持图生图，这里只是模拟
            # 实际应用中需要扩展图像生成服务以支持图生图
            await generator.generate_image(prompt, output_path)
            
            # 将图像转换为base64
            with open(output_path, "rb") as f:
                result_image_data = base64.b64encode(f.read()).decode()
            
            # 删除临时文件
            os.remove(input_path)
            os.remove(output_path)
            
            # 返回base64编码的图像数据
            return f"data:image/png;base64,{result_image_data}"
        else:
            raise Exception(f"不支持的模型: {model}")
            
    except Exception as e:
        logger.error(f"生成图片变体失败: {str(e)}")
        raise Exception(f"生成图片变体失败: {str(e)}")

def create_image(db: Session, user_id: int, prompt: str, image_url: str, is_variation: bool = False):
    """创建图像记录"""
    db_image = Image(
        user_id=user_id,
        prompt=prompt,
        image_url=image_url,
        is_variation=is_variation
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

def get_user_images(db: Session, user_id: int):
    """获取用户的图像列表"""
    return db.query(Image).filter(Image.user_id == user_id).all() 
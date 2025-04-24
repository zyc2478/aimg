from sqlalchemy.orm import Session
from ..models.image import Image
from ..schemas.image import ImagePrompt, ImageToImagePrompt
from ..core.config import get_settings
import openai
import base64
import os
from io import BytesIO
from PIL import Image as PILImage
import logging
import requests
import json

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
openai.api_key = settings.OPENAI_API_KEY

async def generate_text_to_image(prompt: str) -> str:
    """文生图功能"""
    try:
        logger.info(f"开始生成图片，提示词: {prompt}")
        logger.info(f"使用的API密钥: {openai.api_key[:8]}...")
        
        # 首先验证API密钥
        try:
            # 尝试获取账户信息
            response = requests.get(
                "https://api.openai.com/v1/dashboard/billing/usage",
                headers={"Authorization": f"Bearer {openai.api_key}"}
            )
            if response.status_code == 401:
                logger.error("API密钥无效")
                raise Exception("API密钥无效，请检查您的API密钥是否正确")
            elif response.status_code == 403:
                logger.error("API密钥权限不足")
                raise Exception("API密钥权限不足，请检查您的账户权限")
            elif response.status_code != 200:
                logger.error(f"API请求失败: {response.status_code} - {response.text}")
                raise Exception(f"API请求失败: {response.status_code} - {response.text}")
            
            # 检查配额
            usage_data = response.json()
            logger.info(f"API使用情况: {json.dumps(usage_data, indent=2)}")
            
            # 使用 DALL-E 2 模型
            response = await openai.Image.acreate(
                model="dall-e-2",  # 使用 DALL-E 2 模型
                prompt=prompt,
                n=1,
                size="1024x1024"
            )
            
            logger.info("图片生成成功")
            return response.data[0].url
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求异常: {str(e)}")
            raise Exception(f"API请求异常: {str(e)}")
    except Exception as e:
        logger.error(f"生成图片失败: {str(e)}")
        raise Exception(f"生成图片失败: {str(e)}")

async def generate_image_to_image(prompt: str, image_data: str) -> str:
    """图生图功能"""
    try:
        logger.info(f"开始生成图片变体，提示词: {prompt}")
        
        # 将base64图片数据转换为PIL Image对象
        image = PILImage.open(BytesIO(base64.b64decode(image_data)))
        
        # 调整图片大小为1024x1024
        image = image.resize((1024, 1024))
        
        # 将图片转换回base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        response = await openai.Image.acreate_variation(
            image=img_str,
            n=1,
            size="1024x1024"
        )
        
        logger.info("图片变体生成成功")
        return response.data[0].url
    except Exception as e:
        logger.error(f"生成图片变体失败: {str(e)}")
        raise Exception(f"生成图片失败: {str(e)}")

def create_image(db: Session, user_id: int, prompt: str, image_url: str, is_variation: bool = False):
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
    return db.query(Image).filter(Image.user_id == user_id).all() 
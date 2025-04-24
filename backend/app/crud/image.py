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

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
openai.api_key = settings.OPENAI_API_KEY

# ComfyUI API 地址
COMFYUI_API_URL = "http://223.104.3.2:8188"

async def generate_text_to_image(prompt: str, model: str = "flux-t2v") -> str:
    """文生图功能，支持多种模型"""
    try:
        # 验证提示词不为空
        if not prompt or prompt.strip() == "":
            raise Exception("提示词不能为空")
            
        logger.info(f"开始生成图片，提示词: {prompt}，模型: {model}")
        
        if model.lower() == "flux-t2v":
            return await _generate_with_comfyui(prompt)
        else:
            raise Exception(f"不支持的模型: {model}")
            
    except Exception as e:
        logger.error(f"生成图片失败: {str(e)}")
        raise Exception(f"生成图片失败: {str(e)}")

async def _generate_with_dalle(prompt: str) -> str:
    """使用DALL-E生成图片"""
    try:
        logger.info(f"使用DALL-E生成图片，提示词: {prompt}")
        logger.info(f"使用的API密钥: {openai.api_key[:8]}...")
        
        # 使用 DALL-E 2 模型
        response = await openai.Image.acreate(
            model="dall-e-2",  # 使用 DALL-E 2 模型
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        
        logger.info("DALL-E图片生成成功")
        return response.data[0].url
    except Exception as e:
        logger.error(f"DALL-E生成图片失败: {str(e)}")
        raise Exception(f"DALL-E生成图片失败: {str(e)}")

async def _generate_with_sd(prompt: str) -> str:
    """使用Stable Diffusion生成图片"""
    try:
        logger.info(f"使用Stable Diffusion生成图片，提示词: {prompt}")
        
        # 这里使用ComfyUI的API来调用SD模型
        # 实际上SD和ComfyUI使用相同的API，只是工作流不同
        return await _generate_with_comfyui(prompt, workflow="sd")
    except Exception as e:
        logger.error(f"Stable Diffusion生成图片失败: {str(e)}")
        raise Exception(f"Stable Diffusion生成图片失败: {str(e)}")

async def _generate_with_comfyui(prompt: str, workflow: str = "default") -> str:
    """使用ComfyUI生成图片"""
    try:
        logger.info(f"使用ComfyUI生成图片，提示词: {prompt}，工作流: {workflow}")
        
        # 使用完整的FLUX工作流配置
        workflow_data = {
            "last_node_id": 25,
            "last_link_id": 40,
            "nodes": [
                {
                    "id": 5,
                    "type": "EmptyLatentImage",
                    "pos": [473, 450],
                    "size": [315, 106],
                    "flags": {},
                    "order": 0,
                    "mode": 0,
                    "inputs": [],
                    "outputs": [{"name": "LATENT", "type": "LATENT", "links": [23], "slot_index": 0}],
                    "properties": {"Node name for S&R": "EmptyLatentImage"},
                    "widgets_values": [1024, 1024, 1]
                },
                {
                    "id": 22,
                    "type": "BasicGuider",
                    "pos": [559, 125],
                    "size": [241.79998779296875, 46],
                    "flags": {},
                    "order": 8,
                    "mode": 0,
                    "inputs": [
                        {"name": "model", "type": "MODEL", "link": 39},
                        {"name": "conditioning", "type": "CONDITIONING", "link": 40}
                    ],
                    "outputs": [{"name": "GUIDER", "type": "GUIDER", "links": [30], "slot_index": 0}],
                    "properties": {"Node name for S&R": "BasicGuider"}
                },
                {
                    "id": 8,
                    "type": "VAEDecode",
                    "pos": [1248, 192],
                    "size": [210, 46],
                    "flags": {},
                    "order": 10,
                    "mode": 0,
                    "inputs": [
                        {"name": "samples", "type": "LATENT", "link": 24},
                        {"name": "vae", "type": "VAE", "link": 12}
                    ],
                    "outputs": [{"name": "IMAGE", "type": "IMAGE", "links": [9], "slot_index": 0}],
                    "properties": {"Node name for S&R": "VAEDecode"}
                },
                {
                    "id": 25,
                    "type": "RandomNoise",
                    "pos": [470, 611],
                    "size": [315, 82],
                    "flags": {},
                    "order": 1,
                    "mode": 0,
                    "inputs": [],
                    "outputs": [{"name": "NOISE", "type": "NOISE", "links": [37]}],
                    "properties": {"Node name for S&R": "RandomNoise"},
                    "widgets_values": [int(time.time()) % 1000000000000000, "randomize"]
                },
                {
                    "id": 11,
                    "type": "DualCLIPLoader",
                    "pos": [-254, 279],
                    "size": [465.2893371582031, 106],
                    "flags": {},
                    "order": 2,
                    "mode": 0,
                    "inputs": [],
                    "outputs": [{"name": "CLIP", "type": "CLIP", "links": [10], "slot_index": 0}],
                    "properties": {"Node name for S&R": "DualCLIPLoader"},
                    "widgets_values": ["t5xxl_fp16.safetensors", "clip_l.safetensors", "flux", "default"]
                },
                {
                    "id": 10,
                    "type": "VAELoader",
                    "pos": [890, 670],
                    "size": [315, 58],
                    "flags": {},
                    "order": 3,
                    "mode": 0,
                    "inputs": [],
                    "outputs": [{"name": "VAE", "type": "VAE", "links": [12], "slot_index": 0}],
                    "properties": {"Node name for S&R": "VAELoader"},
                    "widgets_values": ["ae.sft"]
                },
                {
                    "id": 9,
                    "type": "SaveImage",
                    "pos": [1490, 190],
                    "size": [210, 46],
                    "flags": {},
                    "order": 11,
                    "mode": 0,
                    "inputs": [{"name": "images", "type": "IMAGE", "link": 9}],
                    "outputs": [],
                    "properties": {"Node name for S&R": "SaveImage"},
                    "widgets_values": ["ComfyUI"]
                },
                {
                    "id": 17,
                    "type": "BasicScheduler",
                    "pos": [468, 867],
                    "size": [315, 106],
                    "flags": {},
                    "order": 7,
                    "mode": 0,
                    "inputs": [{"name": "model", "type": "MODEL", "link": 38}],
                    "outputs": [{"name": "SIGMAS", "type": "SIGMAS", "links": [20]}],
                    "properties": {"Node name for S&R": "BasicScheduler"},
                    "widgets_values": ["normal", 20, 1]
                },
                {
                    "id": 16,
                    "type": "KSamplerSelect",
                    "pos": [470, 749],
                    "size": [315, 58],
                    "flags": {},
                    "order": 4,
                    "mode": 0,
                    "inputs": [],
                    "outputs": [{"name": "SAMPLER", "type": "SAMPLER", "links": [19]}],
                    "properties": {"Node name for S&R": "KSamplerSelect"},
                    "widgets_values": ["euler"]
                },
                {
                    "id": 13,
                    "type": "SamplerCustomAdvanced",
                    "pos": [840, 220],
                    "size": [360, 330],
                    "flags": {},
                    "order": 9,
                    "mode": 0,
                    "inputs": [
                        {"name": "noise", "type": "NOISE", "link": 37},
                        {"name": "guider", "type": "GUIDER", "link": 30},
                        {"name": "sampler", "type": "SAMPLER", "link": 19},
                        {"name": "sigmas", "type": "SIGMAS", "link": 20},
                        {"name": "latent_image", "type": "LATENT", "link": 23}
                    ],
                    "outputs": [{"name": "output", "type": "LATENT", "links": [24]}],
                    "properties": {"Node name for S&R": "SamplerCustomAdvanced"}
                },
                {
                    "id": 6,
                    "type": "CLIPTextEncode",
                    "pos": [-107, 576],
                    "size": [422.84503173828125, 164.31304931640625],
                    "flags": {},
                    "order": 6,
                    "mode": 0,
                    "inputs": [{"name": "clip", "type": "CLIP", "link": 10}],
                    "outputs": [{"name": "CONDITIONING", "type": "CONDITIONING", "links": [40]}],
                    "properties": {"Node name for S&R": "CLIPTextEncode"},
                    "widgets_values": [prompt]
                },
                {
                    "id": 12,
                    "type": "UNETLoader",
                    "pos": [-96.75000762939453, 82.47762298583984],
                    "size": [315, 82],
                    "flags": {},
                    "order": 5,
                    "mode": 0,
                    "inputs": [],
                    "outputs": [{"name": "MODEL", "type": "MODEL", "links": [38, 39]}],
                    "properties": {"Node name for S&R": "UNETLoader"},
                    "widgets_values": ["FLUX\\flux1-dev.sft", "fp8_e4m3fn"]
                }
            ],
            "links": [
                [9, 8, 0, 9, 0, "IMAGE"],
                [10, 11, 0, 6, 0, "CLIP"],
                [12, 10, 0, 8, 1, "VAE"],
                [19, 16, 0, 13, 2, "SAMPLER"],
                [20, 17, 0, 13, 3, "SIGMAS"],
                [23, 5, 0, 13, 4, "LATENT"],
                [24, 13, 0, 8, 0, "LATENT"],
                [30, 22, 0, 13, 1, "GUIDER"],
                [37, 25, 0, 13, 0, "NOISE"],
                [38, 12, 0, 17, 0, "MODEL"],
                [39, 12, 0, 22, 0, "MODEL"],
                [40, 6, 0, 22, 1, "CONDITIONING"]
            ],
            "groups": [],
            "config": {},
            "extra": {
                "node_versions": {"comfy-core": "0.3.12"}
            },
            "version": 0.4
        }
        
        # 发送请求到ComfyUI API
        response = requests.post(
            f"{COMFYUI_API_URL}/prompt",
            json={"prompt": workflow_data},
            timeout=30
        )
        response.raise_for_status()
        prompt_id = response.json()["prompt_id"]
        
        # 等待生成完成
        while True:
            response = requests.get(f"{COMFYUI_API_URL}/history/{prompt_id}")
            if response.status_code == 200:
                history = response.json()
                if prompt_id in history:
                    # 获取生成的图片
                    outputs = history[prompt_id]["outputs"]
                    if "9" in outputs and "images" in outputs["9"]:
                        image_data = outputs["9"]["images"][0]
                        image_name = image_data["filename"]
                        
                        # 获取图片
                        image_response = requests.get(f"{COMFYUI_API_URL}/view?filename={image_name}")
                        if image_response.status_code == 200:
                            # 将图片保存到本地
                            image_dir = "static/images"
                            os.makedirs(image_dir, exist_ok=True)
                            image_path = os.path.join(image_dir, f"{uuid.uuid4()}.png")
                            
                            with open(image_path, "wb") as f:
                                f.write(image_response.content)
                            
                            # 返回图片URL
                            return f"/static/images/{os.path.basename(image_path)}"
            
            # 等待一段时间再检查
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"ComfyUI生成图片失败: {str(e)}")
        raise Exception(f"ComfyUI生成图片失败: {str(e)}")

async def generate_image_to_image(prompt: str, image_data: str, model: str = "flux-t2v") -> str:
    """图生图功能，支持多种模型"""
    try:
        logger.info(f"开始生成图片变体，提示词: {prompt}，模型: {model}")
        
        if model.lower() == "flux-t2v":
            return await _generate_variation_with_comfyui(prompt, image_data)
        else:
            raise Exception(f"不支持的模型: {model}")
            
    except Exception as e:
        logger.error(f"生成图片变体失败: {str(e)}")
        raise Exception(f"生成图片失败: {str(e)}")

async def _generate_variation_with_dalle(image_data: str) -> str:
    """使用DALL-E生成图片变体"""
    try:
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
        
        logger.info("DALL-E图片变体生成成功")
        return response.data[0].url
    except Exception as e:
        logger.error(f"DALL-E生成图片变体失败: {str(e)}")
        raise Exception(f"DALL-E生成图片变体失败: {str(e)}")

async def _generate_variation_with_sd(prompt: str, image_data: str) -> str:
    """使用Stable Diffusion生成图片变体"""
    try:
        # 这里使用ComfyUI的API来调用SD模型
        return await _generate_variation_with_comfyui(prompt, image_data, workflow="sd")
    except Exception as e:
        logger.error(f"Stable Diffusion生成图片变体失败: {str(e)}")
        raise Exception(f"Stable Diffusion生成图片变体失败: {str(e)}")

async def _generate_variation_with_comfyui(prompt: str, image_data: str, workflow: str = "default") -> str:
    """使用ComfyUI生成图片变体"""
    try:
        # 将base64图片数据转换为PIL Image对象
        image = PILImage.open(BytesIO(base64.b64decode(image_data)))
        
        # 调整图片大小为1024x1024
        image = image.resize((1024, 1024))
        
        # 将图片保存到临时文件
        temp_dir = "static/temp"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, f"{uuid.uuid4()}.png")
        image.save(temp_path)
        
        # 根据不同的工作流选择不同的配置
        if workflow == "sd":
            # 使用SD工作流
            workflow_data = {
                "3": {
                    "inputs": {
                        "text": prompt,
                        "clip": ["4", 0]
                    },
                    "class_type": "CLIPTextEncode"
                },
                "4": {
                    "inputs": {
                        "ckpt_name": "sd_xl_base_1.0.safetensors"
                    },
                    "class_type": "CheckpointLoaderSimple"
                },
                "5": {
                    "inputs": {
                        "text": "ugly, blurry, low quality, distorted",
                        "clip": ["4", 0]
                    },
                    "class_type": "CLIPTextEncode"
                },
                "6": {
                    "inputs": {
                        "samples": ["8", 0],
                        "vae": ["8", 2],
                        "positive": ["3", 0],
                        "negative": ["5", 0],
                        "latent_image": ["7", 0]
                    },
                    "class_type": "KSampler"
                },
                "7": {
                    "inputs": {
                        "image": temp_path
                    },
                    "class_type": "LoadImage"
                },
                "8": {
                    "inputs": {
                        "filename_prefix": "ComfyUI",
                        "images": ["6", 0]
                    },
                    "class_type": "SaveImage"
                }
            }
        else:
            # 使用默认工作流
            workflow_data = {
                "3": {
                    "inputs": {
                        "text": prompt,
                        "clip": ["4", 0]
                    },
                    "class_type": "CLIPTextEncode"
                },
                "4": {
                    "inputs": {
                        "ckpt_name": "sd_xl_base_1.0.safetensors"
                    },
                    "class_type": "CheckpointLoaderSimple"
                },
                "5": {
                    "inputs": {
                        "text": "ugly, blurry, low quality, distorted",
                        "clip": ["4", 0]
                    },
                    "class_type": "CLIPTextEncode"
                },
                "6": {
                    "inputs": {
                        "samples": ["8", 0],
                        "vae": ["8", 2],
                        "positive": ["3", 0],
                        "negative": ["5", 0],
                        "latent_image": ["7", 0]
                    },
                    "class_type": "KSampler"
                },
                "7": {
                    "inputs": {
                        "image": temp_path
                    },
                    "class_type": "LoadImage"
                },
                "8": {
                    "inputs": {
                        "filename_prefix": "ComfyUI",
                        "images": ["6", 0]
                    },
                    "class_type": "SaveImage"
                }
            }
        
        # 发送请求到ComfyUI API
        response = requests.post(
            f"{COMFYUI_API_URL}/prompt",
            json={"prompt": workflow_data},  # 将workflow_data包装在prompt对象中
            timeout=30
        )
        response.raise_for_status()
        prompt_id = response.json()["prompt_id"]
        
        # 等待生成完成
        while True:
            response = requests.get(f"{COMFYUI_API_URL}/history/{prompt_id}")
            if response.status_code == 200:
                history = response.json()
                if prompt_id in history:
                    # 获取生成的图片
                    outputs = history[prompt_id]["outputs"]
                    if "8" in outputs and "images" in outputs["8"]:
                        image_data = outputs["8"]["images"][0]
                        image_name = image_data["filename"]
                        
                        # 获取图片
                        image_response = requests.get(f"{COMFYUI_API_URL}/view?filename={image_name}")
                        if image_response.status_code == 200:
                            # 将图片保存到本地
                            image_dir = "static/images"
                            os.makedirs(image_dir, exist_ok=True)
                            image_path = os.path.join(image_dir, f"{uuid.uuid4()}.png")
                            
                            with open(image_path, "wb") as f:
                                f.write(image_response.content)
                            
                            # 返回图片URL
                            return f"/static/images/{os.path.basename(image_path)}"
            
            # 等待一段时间再检查
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"ComfyUI生成图片变体失败: {str(e)}")
        raise Exception(f"ComfyUI生成图片变体失败: {str(e)}")

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
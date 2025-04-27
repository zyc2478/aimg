import gradio as gr
import asyncio
import base64
from PIL import Image
import io
import json
import sys
from pathlib import Path
import logging
import tempfile
import os
import shutil
import glob

# 设置日志级别
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.append(str(Path(__file__).parent))
from app.utils.comfyui_client import ComfyUIClient
import time

# 获取当前文件所在目录
CURRENT_DIR = Path(__file__).parent
STATIC_DIR = CURRENT_DIR / "static"

# 加载logo并转换为base64
def get_logo_base64():
    logo_path = STATIC_DIR / "pegasus_logo.png"  # 修改为.png文件
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    return "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA0MCA0MCI+PHJlY3Qgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiBmaWxsPSIjMWY2ZmViIi8+PHRleHQgeD0iMjAiIHk9IjIwIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMjQiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+UDwvdGV4dD48L3N2Zz4="

LOGO_BASE64 = get_logo_base64()

def translate_and_expand_prompt(prompt: str) -> str:
    """将提示词扩写成标准格式"""
    # 扩写成标准格式
    expanded_prompt = f"""Main Theme:
{prompt}

Style Specifications:
- High quality, masterpiece
- Highly detailed
- Best quality
- Ultra realistic
- Professional photography
- Dramatic lighting
- Sharp focus
- High resolution

Additional Details:
- Rich color palette
- Intricate details
- Perfect composition
- Cinematic atmosphere
- Professional lighting setup
- 8k resolution
- Photorealistic rendering
- Masterful technique"""
    
    return expanded_prompt

def translate_negative_prompt(negative_prompt: str) -> str:
    """将反向提示词扩写成标准格式"""
    # 添加标准的负面提示词
    expanded_negative = f"""{negative_prompt}, text, watermark, signature, logo, username, artist name, (worst quality:1.4), (low quality:1.4), (normal quality:1.4), lowres, bad anatomy, bad hands, error, missing fingers, extra digit, fewer digits, cropped, jpeg artifacts, signature, watermark, username, blurry, bad feet, poorly drawn hands, poorly drawn face, mutation, deformed, extra fingers, extra limbs, extra arms, extra legs, malformed limbs, fused fingers, too many fingers, long neck, cross-eyed, mutated hands, polar lowres, bad body, bad proportions, gross proportions, missing arms, missing legs, extra digit, extra arms, extra leg, extra foot, ((repeating hair))"""
    
    return expanded_negative

# 确保作品库目录存在
gallery_dir = Path(__file__).parent / "gallery"
gallery_dir.mkdir(exist_ok=True)

async def generate_image(prompt, negative_prompt, steps, guidance):
    try:
        logger.info("开始生成图像...")
        yield None, 0, "正在初始化..."
        
        # 翻译并扩写提示词
        translated_prompt = translate_and_expand_prompt(prompt)
        translated_negative_prompt = translate_negative_prompt(negative_prompt)
        logger.info(f"处理后的提示词: {translated_prompt[:100]}...")
        yield None, 0.1, "正在处理提示词..."
        
        # 生成简短的文件名
        timestamp = int(time.time())
        short_id = str(timestamp)[-6:]
        
        # 创建工作流
        workflow = {
            "5": {
                "class_type": "EmptyLatentImage",
                "inputs": {
                    "width": 1024,
                    "height": 1024,
                    "batch_size": 1
                }
            },
            "22": {
                "class_type": "BasicGuider",
                "inputs": {
                    "model": ["12", 0],
                    "conditioning": ["6", 0],
                    "guidance_scale": guidance  # 使用传入的guidance参数
                }
            },
            "8": {
                "class_type": "VAEDecode",
                "inputs": {
                    "samples": ["13", 0],
                    "vae": ["10", 0]
                }
            },
            "25": {
                "class_type": "RandomNoise",
                "inputs": {
                    "noise_seed": timestamp  # 使用相同的时间戳作为随机种子
                }
            },
            "11": {
                "class_type": "DualCLIPLoader",
                "inputs": {
                    "clip_name1": "t5xxl_fp16.safetensors",
                    "clip_name2": "clip_l.safetensors",
                    "type": "flux"
                }
            },
            "10": {
                "class_type": "VAELoader",
                "inputs": {
                    "vae_name": "ae.sft"
                }
            },
            "9": {
                "class_type": "SaveImage",
                "inputs": {
                    "images": ["8", 0],
                    "filename_prefix": f"img_{short_id}"  # 使用简短的文件名前缀
                }
            },
            "17": {
                "class_type": "BasicScheduler",
                "inputs": {
                    "model": ["12", 0],
                    "steps": steps,  # 使用传入的steps参数
                    "scheduler": "normal",
                    "denoise": 1
                }
            },
            "16": {
                "class_type": "KSamplerSelect",
                "inputs": {
                    "sampler_name": "euler"
                }
            },
            "13": {
                "class_type": "SamplerCustomAdvanced",
                "inputs": {
                    "noise": ["25", 0],
                    "guider": ["22", 0],
                    "sampler": ["16", 0],
                    "sigmas": ["17", 0],
                    "latent_image": ["5", 0]
                }
            },
            "6": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "clip": ["11", 0],
                    "text": translated_prompt
                }
            },
            "12": {
                "class_type": "UNETLoader",
                "inputs": {
                    "unet_name": "FLUX\\flux1-dev.sft",
                    "weight_dtype": "fp8_e4m3fn"
                }
            }
        }
        
        # 创建ComfyUI客户端
        client = ComfyUIClient(host="101.126.152.137", port=8188)
        yield None, 0.2, "正在连接ComfyUI服务器..."
        
        # 检查连接
        if not await client.check_connection():
            yield None, 0, "连接服务器失败，请重试"
            return
            
        yield None, 0.3, "正在准备生成参数..."
        
        # 执行工作流
        try:
            client_id = f"p_{short_id}"
            
            # 提交工作流
            prompt_id = await client.submit_prompt(workflow, client_id)
            if not prompt_id:
                yield None, 0, "提交工作流失败，请重试"
                return
                
            yield None, 0.4, "正在生成图像..."
            
            # 连接WebSocket
            if not await client.connect_websocket(client_id):
                yield None, 0, "连接WebSocket失败，请重试"
                return
                
            # 等待执行完成
            last_status_time = time.time()
            last_progress = 0
            current_progress = 0.4
            
            while True:
                result = await client.listen_websocket()
                current_time = time.time()
                
                if isinstance(result, dict):
                    if result.get("type") == "progress":
                        progress = result.get("data", {})
                        current_step = progress.get("value", 0)
                        total_steps = progress.get("max", 0)
                        if total_steps > 0:
                            percentage = (current_step / total_steps) * 100
                            current_progress = 0.4 + (percentage / 100 * 0.5)
                            if percentage > last_progress:
                                yield None, current_progress, f"正在生成图像... {percentage:.1f}% ({current_step}/{total_steps})"
                                last_progress = percentage
                            last_status_time = current_time
                            
                    elif result.get("type") == "executing":
                        node_id = result.get("data", {}).get("node")
                        if node_id:
                            node_name = workflow.get(node_id, {}).get("class_type", "未知节点")
                            yield None, current_progress, f"正在执行: {node_name}"
                        elif result.get("data", {}).get("node") is None:
                            yield None, 0.9, "正在保存图像..."
                            await asyncio.sleep(1)
                            image_url = await client.get_latest_image()
                            if image_url:
                                async with client.session.get(image_url) as response:
                                    if response.status == 200:
                                        image_data = await response.read()
                                        temp_dir = tempfile.gettempdir()
                                        temp_file = os.path.join(temp_dir, f"img_{short_id}.png")
                                        with open(temp_file, "wb") as f:
                                            f.write(image_data)
                                        # 保存到作品库
                                        gallery_path = gallery_dir / f"{int(time.time())}.png"
                                        shutil.copy(temp_file, gallery_path)
                                        logger.info(f"[文生图] 已保存到作品库: {gallery_path}")
                                        yield temp_file, 1.0, "生成完成！"
                                        return
                                    else:
                                        yield None, 0, "保存图像失败，请重试"
                            else:
                                yield None, 0, "获取图像失败，请重试"
                                return
                
                # 超时检查
                if current_time - last_status_time > 30:
                    yield None, 0, "生成超时，请重试"
                    return
                    
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"工作流执行错误: {str(e)}")
            yield None, 0, f"生成失败：{str(e)}"
            
    except Exception as e:
        logger.error(f"生成图像时发生错误: {str(e)}")
        yield None, 0, f"生成失败：{str(e)}"

async def get_latest_image(client):
    """获取最新生成的图像"""
    try:
        async with client.session.get(f"{client.base_url}/history") as response:
            if response.status == 200:
                history = await response.json()
                if history:
                    latest_output = list(history.values())[-1]["outputs"]
                    if latest_output:
                        node_id = list(latest_output.keys())[0]
                        image_data = latest_output[node_id]["images"][0]
                        return f"{client.base_url}/view?filename={image_data['filename']}"
                else:
                    logger.warning("未找到图像输出")
            else:
                logger.warning("历史记录为空")
    except Exception as e:
        logger.error(f"获取图像时出错: {str(e)}")
    return None

async def generate_variation(image, prompt, negative_prompt, strength, steps, guidance):
    try:
        logger.info("[图生图] 开始执行 generate_variation")
        if image is None:
            logger.warning("[图生图] 未上传图片，直接返回")
            yield None, 0, "请先上传图片！"
            return
        
        # 翻译并扩写提示词
        translated_prompt = translate_and_expand_prompt(prompt)
        translated_negative_prompt = translate_negative_prompt(negative_prompt)
        logger.info(f"[图生图] 翻译后的提示词: {translated_prompt}")
        logger.info(f"[图生图] 翻译后的反向提示词: {translated_negative_prompt}")
        yield None, 0.1, "正在处理提示词..."
        
        # 将图片转换为base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        logger.info("[图生图] 图片已转换为base64")
        
        # 生成简短的文件名
        timestamp = int(time.time())
        short_id = str(timestamp)[-6:]
        logger.info(f"[图生图] short_id: {short_id}")
        
        # 创建工作流
        workflow = {
            "5": {
                "class_type": "EmptyLatentImage",
                "inputs": {
                    "width": 1024,
                    "height": 1024,
                    "batch_size": 1
                }
            },
            "22": {
                "class_type": "BasicGuider",
                "inputs": {
                    "model": ["12", 0],
                    "conditioning": ["6", 0]
                }
            },
            "8": {
                "class_type": "VAEDecode",
                "inputs": {
                    "samples": ["13", 0],
                    "vae": ["10", 0]
                }
            },
            "25": {
                "class_type": "RandomNoise",
                "inputs": {
                    "noise_seed": 782619153058034
                }
            },
            "11": {
                "class_type": "DualCLIPLoader",
                "inputs": {
                    "clip_name1": "t5xxl_fp16.safetensors",
                    "clip_name2": "clip_l.safetensors",
                    "type": "flux"
                }
            },
            "10": {
                "class_type": "VAELoader",
                "inputs": {
                    "vae_name": "ae.sft"
                }
            },
            "9": {
                "class_type": "SaveImage",
                "inputs": {
                    "images": ["8", 0],
                    "filename_prefix": f"img_{short_id}"  # 使用简短的文件名前缀
                }
            },
            "17": {
                "class_type": "BasicScheduler",
                "inputs": {
                    "model": ["12", 0],
                    "steps": 20,
                    "scheduler": "normal",
                    "denoise": 1
                }
            },
            "16": {
                "class_type": "KSamplerSelect",
                "inputs": {
                    "sampler_name": "euler"
                }
            },
            "13": {
                "class_type": "SamplerCustomAdvanced",
                "inputs": {
                    "noise": ["25", 0],
                    "guider": ["22", 0],
                    "sampler": ["16", 0],
                    "sigmas": ["17", 0],
                    "latent_image": ["5", 0]
                }
            },
            "6": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "clip": ["11", 0],
                    "text": translated_prompt
                }
            },
            "12": {
                "class_type": "UNETLoader",
                "inputs": {
                    "unet_name": "FLUX\\flux1-dev.sft",
                    "weight_dtype": "fp8_e4m3fn"
                }
            }
        }
        
        logger.info("[图生图] 正在连接ComfyUI服务器...")
        yield None, 0.2, "正在连接ComfyUI服务器..."
        
        async with ComfyUIClient(host="101.126.152.137", port=8188) as client:
            logger.info("[图生图] 提交工作流...")
            prompt_id = await client.submit_prompt(workflow)
            logger.info(f"[图生图] 工作流已提交，ID: {prompt_id}")
            yield None, 0.3, "工作流已提交，正在生成图像..."
            
            logger.info("[图生图] 连接WebSocket...")
            await client.connect_websocket()
            
            last_status_time = time.time()
            last_progress = 0
            current_progress = 0.3
            
            while True:
                result = await client.listen_websocket()
                logger.info(f"[图生图] WebSocket返回: {result}")
                current_time = time.time()
                
                if isinstance(result, dict):
                    if result.get("type") == "progress":
                        progress = result.get("data", {})
                        current_step = progress.get("value", 0)
                        total_steps = progress.get("max", 0)
                        if total_steps > 0:
                            percentage = (current_step / total_steps) * 100
                            current_progress = 0.3 + (percentage / 100 * 0.6)
                            if percentage > last_progress:
                                logger.info(f"[图生图] 生成进度: {percentage:.1f}%")
                                yield None, current_progress, f"正在生成图像... {percentage:.1f}% ({current_step}/{total_steps})"
                                last_progress = percentage
                            last_status_time = current_time
                    
                    elif result.get("type") == "executing":
                        node_id = result.get("data", {}).get("node")
                        logger.info(f"[图生图] executing node_id: {node_id}")
                        if node_id:
                            node_name = workflow.get(node_id, {}).get("class_type", "未知节点")
                            yield None, current_progress, f"正在执行: {node_name}"
                        elif result.get("data", {}).get("node") is None:
                            logger.info("[图生图] 执行完成，等待1秒后获取图像...")
                            yield None, 0.9, "执行完成，正在获取图像..."
                            await asyncio.sleep(1)
                            image_url = await get_latest_image(client)
                            logger.info(f"[图生图] 获取到的image_url: {image_url}")
                            if image_url:
                                # 获取图像数据
                                async with client.session.get(image_url) as response:
                                    logger.info(f"[图生图] 拉取图片状态码: {response.status}")
                                    if response.status == 200:
                                        image_data = await response.read()
                                        # 将图片保存到系统临时目录
                                        temp_dir = tempfile.gettempdir()
                                        temp_file = os.path.join(temp_dir, f"img_{short_id}.png")
                                        with open(temp_file, "wb") as f:
                                            f.write(image_data)
                                        # 保存到作品库
                                        gallery_path = gallery_dir / f"{int(time.time())}.png"
                                        shutil.copy(temp_file, gallery_path)
                                        logger.info(f"[图生图] 已保存到作品库: {gallery_path}")
                                        yield temp_file, 1.0, "生成完成！"
                                        return
                                    else:
                                        logger.error(f"[图生图] 获取图像失败，状态码: {response.status}")
                                        yield None, 0, f"获取图像失败，状态码: {response.status}"
                            else:
                                logger.warning("[图生图] 未能获取到图像，继续等待...")
                
                    # 新增：处理 status 队列清空
                    elif result.get("type") == "status":
                        exec_info = result.get("data", {}).get("status", {}).get("exec_info", {})
                        if exec_info.get("queue_remaining", 1) == 0:
                            logger.info("[图生图] 队列已清空，尝试获取图片")
                            yield None, 0.95, "队列已清空，正在获取图像..."
                            await asyncio.sleep(1)
                            image_url = await get_latest_image(client)
                            logger.info(f"[图生图] 队列清空后获取到的image_url: {image_url}")
                            if image_url:
                                async with client.session.get(image_url) as response:
                                    logger.info(f"[图生图] 队列清空后拉取图片状态码: {response.status}")
                                    if response.status == 200:
                                        image_data = await response.read()
                                        temp_dir = tempfile.gettempdir()
                                        temp_file = os.path.join(temp_dir, f"img_{short_id}.png")
                                        with open(temp_file, "wb") as f:
                                            f.write(image_data)
                                        # 保存到作品库
                                        gallery_path = gallery_dir / f"{int(time.time())}.png"
                                        shutil.copy(temp_file, gallery_path)
                                        logger.info(f"[图生图] 已保存到作品库: {gallery_path}")
                                        yield temp_file, 1.0, "生成完成！"
                                        return
                                    else:
                                        logger.error(f"[图生图] 队列清空后获取图像失败，状态码: {response.status}")
                                        yield None, 0, f"获取图像失败，状态码: {response.status}"
                            else:
                                logger.error("[图生图] 队列清空后未能获取到图片")
                                yield None, 0, "未能获取到图片"
                            return
                
                # 超时检查
                if current_time - last_status_time > 30:
                    logger.warning("[图生图] 等待超时，尝试最后一次获取结果...")
                    image_url = await get_latest_image(client)
                    logger.info(f"[图生图] 超时后获取到的image_url: {image_url}")
                    if image_url:
                        # 获取图像数据
                        async with client.session.get(image_url) as response:
                            logger.info(f"[图生图] 超时拉取图片状态码: {response.status}")
                            if response.status == 200:
                                image_data = await response.read()
                                # 将图片保存到系统临时目录
                                temp_dir = tempfile.gettempdir()
                                temp_file = os.path.join(temp_dir, f"img_{short_id}.png")
                                with open(temp_file, "wb") as f:
                                    f.write(image_data)
                                # 保存到作品库
                                gallery_path = gallery_dir / f"{int(time.time())}.png"
                                shutil.copy(temp_file, gallery_path)
                                logger.info(f"[图生图] 已保存到作品库: {gallery_path}")
                                yield temp_file, 1.0, "生成完成！"
                            else:
                                logger.error(f"[图生图] 超时后获取图像失败，状态码: {response.status}")
                                yield None, 0, f"获取图像失败，状态码: {response.status}"
                    else:
                        logger.error("[图生图] 生成超时，未能获取到图片")
                        yield None, 0, "生成超时，请重试"
                    return
                
                await asyncio.sleep(0.1)
                
    except Exception as e:
        logger.error(f"[图生图] 发生错误: {str(e)}")
        yield None, 0, f"生成失败：{str(e)}"

def get_gallery_images():
    # 获取gallery目录下所有png/jpg图片路径，按时间倒序
    image_files = sorted(gallery_dir.glob("*.png"), reverse=True)
    return [str(p) for p in image_files]

with gr.Blocks(title="PegaAI", css="""
    footer {display: none}
    .author-info {
        position: fixed;
        bottom: 10px;
        right: 20px;
        font-size: 14px;
        color: #1f6feb;
        font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        z-index: 1000;
    }
    .logo-container {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .logo-container img {
        width: 40px;
        height: 40px;
    }
    .logo-container h1 {
        margin: 0;
    }
    /* 自定义进度条样式 */
    .progress-container {
        margin: 10px 0;
    }
    .progress-container .slider-container {
        margin: 0;
    }
    .progress-container .slider-container input[type="range"] {
        height: 6px;
        background: #f0f0f0;
        border-radius: 3px;
    }
    .progress-container .slider-container input[type="range"]::-webkit-slider-thumb {
        display: none;
    }
    .progress-container .slider-container input[type="range"]::-moz-range-thumb {
        display: none;
    }
    .progress-container .slider-container input[type="range"]::-ms-thumb {
        display: none;
    }
    .progress-container .slider-container input[type="range"]::-webkit-slider-runnable-track {
        background: linear-gradient(90deg, #ff6b00 var(--value-percent), #f0f0f0 var(--value-percent));
        border-radius: 3px;
    }
    .progress-container .slider-container input[type="range"]::-moz-range-track {
        background: linear-gradient(90deg, #ff6b00 var(--value-percent), #f0f0f0 var(--value-percent));
        border-radius: 3px;
    }
    .progress-container .slider-container input[type="range"]::-ms-track {
        background: linear-gradient(90deg, #ff6b00 var(--value-percent), #f0f0f0 var(--value-percent));
        border-radius: 3px;
    }
    .progress-container .slider-container button {
        display: none !important;
    }
    .progress-container .slider-container input[type="number"] {
        width: 60px !important;
        text-align: right !important;
    }
    .progress-container .slider-container label {
        display: none !important;
    }
    /* 状态文本样式 */
    .status-text {
        font-size: 14px;
        color: #666;
        margin-top: 5px;
        min-height: 20px;
    }
""") as demo:
    with gr.Row():
        with gr.Column(scale=1):
            gr.HTML(f"""
                <div class="logo-container">
                    <img src="{get_logo_base64()}" width="40" height="40" alt="PegaAI Logo">
                    <h1>PegaAI</h1>
                </div>
            """)
    
    gr.Markdown("<hr style='margin-top: 0; margin-bottom: 20px;'>")
    
    with gr.Tabs() as tabs:
        with gr.TabItem("文生图"):
            with gr.Row():
                with gr.Column():
                    prompt = gr.Textbox(
                        label="提示词",
                        placeholder="请输入您的提示词",
                        lines=2,
                        max_lines=20,
                        autoscroll=False,
                        show_copy_button=True
                    )
                    negative_prompt = gr.Textbox(
                        label="反向提示词",
                        placeholder="low quality, blurry, bad anatomy, bad hands, cropped, worst quality",
                        lines=2,
                        max_lines=20,
                        autoscroll=False,
                        show_copy_button=True
                    )
                    with gr.Row():
                        steps = gr.Slider(minimum=1, maximum=100, value=20, step=1, label="推理步数")
                        guidance = gr.Slider(minimum=1, maximum=20, value=7, step=0.1, label="提示词引导系数")
                    with gr.Row():
                        with gr.Column(scale=3):
                            gen_button = gr.Button("生成", variant="primary")
                        with gr.Column(scale=1):
                            clear_button = gr.Button("清除")
                    gen_progress = gr.Slider(
                        minimum=0,
                        maximum=1,
                        value=0,
                        label="",
                        interactive=False,
                        elem_classes="progress-container"
                    )
                    gen_status = gr.Textbox(
                        label="",
                        value="",
                        interactive=False,
                        elem_classes="status-text"
                    )
                with gr.Column():
                    output_image = gr.Image(label="生成结果")
        
        with gr.TabItem("图生图"):
            with gr.Row():
                with gr.Column():
                    input_image = gr.Image(label="上传图片", type="pil")
                    var_prompt = gr.Textbox(
                        label="提示词",
                        lines=2,
                        max_lines=20,
                        autoscroll=False,
                        show_copy_button=True
                    )
                    var_negative_prompt = gr.Textbox(
                        label="反向提示词",
                        placeholder="low quality, blurry, bad anatomy, bad hands, cropped, worst quality",
                        lines=2,
                        max_lines=20,
                        autoscroll=False,
                        show_copy_button=True
                    )
                    with gr.Row():
                        var_strength = gr.Slider(minimum=0, maximum=1, value=0.75, step=0.01, label="转换强度")
                        var_steps = gr.Slider(minimum=1, maximum=100, value=20, step=1, label="推理步数")
                        var_guidance = gr.Slider(minimum=1, maximum=20, value=7, step=0.1, label="提示词引导系数")
                    var_button = gr.Button("生成变体", variant="primary")
                    var_progress = gr.Slider(
                        minimum=0,
                        maximum=1,
                        value=0,
                        label="",
                        interactive=False,
                        elem_classes="progress-container"
                    )
                    var_status = gr.Textbox(
                        label="",
                        value="",
                        interactive=False,
                        elem_classes="status-text"
                    )
                with gr.Column():
                    var_image = gr.Image(label="生成结果")
        
        with gr.TabItem("作品库"):
            gallery_imgs = gr.Gallery(label="作品库", value=get_gallery_images(), elem_id="gallery-view", show_label=False, columns=4, height=400)
            refresh_btn = gr.Button("刷新")
            refresh_btn.click(fn=lambda: get_gallery_images(), inputs=[], outputs=gallery_imgs)
    
    # 添加JavaScript代码来更新进度条样式
    demo.load(js="""
        function updateProgressStyle(slider) {
            const value = parseFloat(slider.value);
            const percentage = Math.round(value * 100);
            slider.style.setProperty('--value-percent', percentage + '%');
            
            const numberInput = slider.parentElement.querySelector('input[type="number"]');
            if (numberInput) {
                numberInput.value = percentage + '%';
            }
        }
        
        // 监听进度条值的变化
        document.querySelectorAll('.progress-container input[type="range"]').forEach(slider => {
            slider.addEventListener('input', (e) => {
                updateProgressStyle(e.target);
            });
            
            // 初始化进度条样式
            updateProgressStyle(slider);
        });
    """)

    # 修改事件绑定
    gen_button.click(
        fn=generate_image,
        inputs=[prompt, negative_prompt, steps, guidance],
        outputs=[output_image, gen_progress, gen_status],
        api_name="generate"
    )
    var_button.click(
        fn=generate_variation,
        inputs=[input_image, var_prompt, var_negative_prompt, var_strength, var_steps, var_guidance],
        outputs=[var_image, var_progress, var_status],
        api_name="variation"
    )
    clear_button.click(
        fn=lambda: (None, 0, ""),
        inputs=[],
        outputs=[output_image, gen_progress, gen_status],
        api_name="clear"
    )

    # 只保留右下角的作者信息
    gr.HTML('<div class="author-info">author by：pegasus studio @2025</div>')

if __name__ == "__main__":
    demo.queue()  # 启用队列
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        show_error=True,  # 显示详细错误信息
        debug=True  # 启用调试模式
    ) 
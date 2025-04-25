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

# 设置日志级别
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.append(str(Path(__file__).parent))
from app.utils.comfyui_client import ComfyUIClient
import time

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

async def generate_image(prompt, negative_prompt, steps, guidance):
    try:
        logger.info("开始生成图像...")
        yield None, "开始生成图像..."
        
        # 翻译并扩写提示词
        translated_prompt = translate_and_expand_prompt(prompt)
        translated_negative_prompt = translate_negative_prompt(negative_prompt)
        logger.info(f"处理后的提示词: {translated_prompt[:100]}...")
        yield None, "提示词处理完成，准备生成..."
        
        # 生成简短的文件名
        timestamp = int(time.time())
        short_id = str(timestamp)[-6:]  # 只使用时间戳的后6位
        
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
        
        # 创建ComfyUI客户端，使用正确的服务器地址
        client = ComfyUIClient(host="101.126.152.137", port=8188)
        yield None, "正在连接ComfyUI服务器..."
        
        # 检查连接
        if not await client.check_connection():
            yield None, "无法连接到ComfyUI服务器，请确保服务器已启动"
            return
            
        yield None, "连接成功，开始执行工作流..."
        
        # 执行工作流
        try:
            # 生成唯一的client_id
            client_id = f"p_{short_id}"  # 使用简短 client_id
            
            # 提交工作流
            prompt_id = await client.submit_prompt(workflow, client_id)
            if not prompt_id:
                yield None, "提交工作流失败"
                return
                
            yield None, "工作流已提交，等待执行..."
            
            # 连接WebSocket
            if not await client.connect_websocket(client_id):
                yield None, "WebSocket连接失败"
                return
                
            # 等待执行完成
            last_status_time = time.time()
            last_progress = 0
            
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
                            if percentage > last_progress:
                                yield None, f"生成进度: {percentage:.1f}% ({current_step}/{total_steps})"
                                last_progress = percentage
                            last_status_time = current_time
                            
                    elif result.get("type") == "executing" and result.get("data", {}).get("node") is None:
                        yield None, "执行完成，正在获取图像..."
                        await asyncio.sleep(1)
                        image_url = await client.get_latest_image()
                        if image_url:
                            # 获取图像数据
                            async with client.session.get(image_url) as response:
                                if response.status == 200:
                                    image_data = await response.read()
                                    # 将图片保存到系统临时目录
                                    temp_dir = tempfile.gettempdir()
                                    temp_file = os.path.join(temp_dir, f"img_{short_id}.png")
                                    with open(temp_file, "wb") as f:
                                        f.write(image_data)
                                    # 返回临时文件路径
                                    yield temp_file, "生成完成！"
                                    return
                                else:
                                    yield None, f"获取图像失败，状态码: {response.status}"
                        else:
                            yield None, "未能获取到生成的图像"
                            return
                            
                # 超时检查
                if current_time - last_status_time > 30:
                    yield None, "生成超时，请重试"
                    return
                    
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"工作流执行错误: {str(e)}")
            yield None, f"生成图像失败: {str(e)}"
            
    except Exception as e:
        logger.error(f"生成图像时发生错误: {str(e)}")
        yield None, f"生成图像失败: {str(e)}"

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
                        async with client.session.get(f"{client.base_url}/view?filename={image_data['filename']}") as img_response:
                            if img_response.status == 200:
                                image_bytes = await img_response.read()
                                return f"data:image/png;base64,{base64.b64encode(image_bytes).decode()}"
                            else:
                                logger.warning(f"获取图像失败，状态码: {img_response.status}")
                else:
                    logger.warning("未找到图像输出")
            else:
                logger.warning("历史记录为空")
    except Exception as e:
        logger.error(f"获取图像时出错: {str(e)}")
    return None

async def generate_variation(image, prompt, negative_prompt, strength, steps, guidance):
    try:
        if image is None:
            yield None, "请先上传图片！"
            return
        
        # 翻译并扩写提示词
        translated_prompt = translate_and_expand_prompt(prompt)
        translated_negative_prompt = translate_negative_prompt(negative_prompt)
        logger.info(f"翻译后的提示词: {translated_prompt}")
        logger.info(f"翻译后的反向提示词: {translated_negative_prompt}")
        
        # 将图片转换为base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
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
                    "filename_prefix": "ComfyUI"
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
        
        logger.info("正在连接ComfyUI服务器...")
        async with ComfyUIClient(host="101.126.152.137", port=8188) as client:
            logger.info("提交工作流...")
            prompt_id = await client.submit_prompt(workflow)
            logger.info(f"工作流已提交，ID: {prompt_id}")
            yield None, "工作流已提交，正在生成图像..."
            
            logger.info("连接WebSocket...")
            await client.connect_websocket()
            
            last_status_time = time.time()
            last_progress = 0
            
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
                            if percentage > last_progress:
                                logger.info(f"生成进度: {percentage:.1f}%")
                                yield None, f"生成进度: {percentage:.1f}% ({current_step}/{total_steps})"
                                last_progress = percentage
                            last_status_time = current_time
                    
                    elif result.get("type") == "executing":
                        if result.get("data", {}).get("node") is None:
                            logger.info("执行完成，等待1秒后获取图像...")
                            await asyncio.sleep(1)
                            image_url = await get_latest_image(client)
                            if image_url:
                                yield image_url, "生成完成！"
                                return
                            else:
                                logger.warning("未能获取到图像，继续等待...")
                    
                    elif result.get("type") == "status":
                        status = result.get("data", {}).get("status", {})
                        queue_remaining = status.get("exec_info", {}).get("queue_remaining", 1)
                        if queue_remaining == 0:
                            logger.info("队列为空，检查结果...")
                            image_url = await get_latest_image(client)
                            if image_url:
                                yield image_url, "生成完成！"
                                return
                
                # 超时检查
                if current_time - last_status_time > 30:
                    logger.warning("等待超时，尝试最后一次获取结果...")
                    image_url = await get_latest_image(client)
                    if image_url:
                        yield image_url, "生成完成！"
                    else:
                        yield None, "生成超时，请重试"
                    return
                
                await asyncio.sleep(0.1)
                
    except Exception as e:
        logger.error(f"发生错误: {str(e)}")
        yield None, f"生成失败：{str(e)}"

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
""") as demo:
    with gr.Row():
        with gr.Column(scale=1):
            gr.HTML("""
                <div class="logo-container">
                    <img src="/file/static/logo.jpg" width="40" height="40" alt="PegaAI Logo">
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
                    gen_output = gr.Textbox(label="生成状态")
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
                    var_output = gr.Textbox(label="生成状态")
                with gr.Column():
                    var_image = gr.Image(label="生成结果")
    
    # 绑定事件
    gen_button.click(
        fn=generate_image,
        inputs=[prompt, negative_prompt, steps, guidance],
        outputs=[output_image, gen_output],
        api_name="generate"
    )
    var_button.click(
        fn=generate_variation,
        inputs=[input_image, var_prompt, var_negative_prompt, var_strength, var_steps, var_guidance],
        outputs=[var_image, var_output],
        api_name="variation"
    )
    clear_button.click(
        fn=lambda: (None, ""),
        inputs=[],
        outputs=[output_image, gen_output],
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
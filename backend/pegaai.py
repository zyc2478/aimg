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

# 导入各个功能模块
from modules.text2img import generate_image
from modules.img2img import generate_variation
from modules.text2video import generate_video
from modules.img2video import generate_video_from_image
from modules.video_clip import clip_video

# 设置日志级别
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 获取当前文件所在目录
CURRENT_DIR = Path(__file__).parent
STATIC_DIR = CURRENT_DIR / "static"

# 加载logo并转换为base64
def get_logo_base64():
    logo_path = STATIC_DIR / "pegasus_logo.png"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    return "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA0MCA0MCI+PHJlY3Qgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiBmaWxsPSIjMWY2ZmViIi8+PHRleHQgeD0iMjAiIHk9IjIwIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMjQiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+UDwvdGV4dD48L3N2Zz4="

LOGO_BASE64 = get_logo_base64()

# 创建主界面
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
    /* 工具箱图标样式 */
    .toolbox-icon {
        position: fixed;
        top: 20px;
        right: 20px;
        width: 40px;
        height: 40px;
        background: #1f6feb;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        cursor: pointer;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .toolbox-icon:hover {
        transform: scale(1.1);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
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
        # 导入各个标签页的UI组件
        from ui.text2img_ui import create_text2img_ui
        from ui.img2img_ui import create_img2img_ui
        from ui.text2video_ui import create_text2video_ui
        from ui.img2video_ui import create_img2video_ui
        from ui.video_clip_ui import create_video_clip_ui
        
        # 创建各个标签页
        with gr.TabItem("文生图"):
            create_text2img_ui()
        
        with gr.TabItem("图生图"):
            create_img2img_ui()
            
        with gr.TabItem("文生视频"):
            create_text2video_ui()
        
        with gr.TabItem("图生视频"):
            create_img2video_ui()
        
        with gr.TabItem("一键剪辑"):
            create_video_clip_ui()

    # 添加工具箱图标
    gr.HTML("""
        <div class="toolbox-icon" title="工具箱">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M22 7H2V11H22V7Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M22 17H2V21H22V17Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M6 7V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M18 7V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
    """)

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
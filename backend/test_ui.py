import gradio as gr
import requests
import base64
from PIL import Image
import io

# API配置
API_BASE_URL = "http://localhost:8000"
API_TOKEN = None  # 将在登录后设置

def register(username, password, email):
    """注册新用户"""
    response = requests.post(
        f"{API_BASE_URL}/api/users/register",
        json={
            "username": username,
            "password": password,
            "email": email
        }
    )
    if response.status_code == 200:
        return "注册成功！请使用新账号登录。"
    return f"注册失败：{response.text}"

def login(username, password):
    global API_TOKEN
    response = requests.post(
        f"{API_BASE_URL}/api/auth/token",
        data={"username": username, "password": password}
    )
    if response.status_code == 200:
        API_TOKEN = response.json()["access_token"]
        return "登录成功！"
    return "登录失败，请检查用户名和密码。"

def text_to_image(prompt):
    if not API_TOKEN:
        return "请先登录！", None
    
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    response = requests.post(
        f"{API_BASE_URL}/api/images/text-to-image",
        json={"prompt": prompt},
        headers=headers
    )
    
    if response.status_code == 200:
        image_url = response.json()["url"]
        return "生成成功！", image_url
    return f"生成失败：{response.text}", None

def image_to_image(prompt, image):
    if not API_TOKEN:
        return "请先登录！", None
    
    # 将图片转换为base64
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    response = requests.post(
        f"{API_BASE_URL}/api/images/image-to-image",
        json={"prompt": prompt, "image_data": img_str},
        headers=headers
    )
    
    if response.status_code == 200:
        image_url = response.json()["url"]
        return "生成成功！", image_url
    return f"生成失败：{response.text}", None

# 创建界面
with gr.Blocks() as demo:
    gr.Markdown("# AI 图片生成器")
    
    with gr.Tab("注册/登录"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 注册新用户")
                reg_username = gr.Textbox(label="用户名")
                reg_password = gr.Textbox(label="密码", type="password")
                reg_email = gr.Textbox(label="邮箱")
                register_btn = gr.Button("注册")
                register_output = gr.Textbox(label="注册状态")
            
            with gr.Column():
                gr.Markdown("### 登录")
                username = gr.Textbox(label="用户名")
                password = gr.Textbox(label="密码", type="password")
                login_btn = gr.Button("登录")
                login_output = gr.Textbox(label="登录状态")
    
    with gr.Tab("文生图"):
        with gr.Row():
            prompt = gr.Textbox(label="描述文字")
            text_to_image_btn = gr.Button("生成图片")
        text_to_image_output = gr.Textbox(label="生成状态")
        text_to_image_result = gr.Image(label="生成的图片")
    
    with gr.Tab("图生图"):
        with gr.Row():
            prompt = gr.Textbox(label="描述文字")
            input_image = gr.Image(label="输入图片")
            image_to_image_btn = gr.Button("生成图片")
        image_to_image_output = gr.Textbox(label="生成状态")
        image_to_image_result = gr.Image(label="生成的图片")
    
    # 绑定事件
    register_btn.click(
        register,
        inputs=[reg_username, reg_password, reg_email],
        outputs=[register_output]
    )
    
    login_btn.click(
        login,
        inputs=[username, password],
        outputs=[login_output]
    )
    
    text_to_image_btn.click(
        text_to_image,
        inputs=[prompt],
        outputs=[text_to_image_output, text_to_image_result]
    )
    
    image_to_image_btn.click(
        image_to_image,
        inputs=[prompt, input_image],
        outputs=[image_to_image_output, image_to_image_result]
    )

if __name__ == "__main__":
    demo.launch() 
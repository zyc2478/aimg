import gradio as gr
import requests
import base64
from PIL import Image
import io
import json

API_URL = "http://localhost:8000"
token = None

def login(username, password):
    global token
    response = requests.post(
        f"{API_URL}/api/auth/token",
        data={"username": username, "password": password}
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        return "登录成功！", gr.update(visible=True, selected=0), gr.update(visible=False)
    return "登录失败：" + str(response.json().get("detail", "未知错误")), gr.update(visible=False), gr.update(visible=True)

def register(username, password, email):
    response = requests.post(
        f"{API_URL}/api/users/register",
        json={
            "username": username,
            "password": password,
            "email": email,
            "full_name": username
        }
    )
    if response.status_code == 200:
        return "注册成功！请登录。"
    
    error_detail = response.json().get("detail", "未知错误")
    
    if isinstance(error_detail, list):
        error_messages = []
        for item in error_detail:
            if isinstance(item, dict):
                for key, value in item.items():
                    error_messages.append(f"{key}: {value}")
            else:
                error_messages.append(str(item))
        error_detail = ", ".join(error_messages)
    elif isinstance(error_detail, dict):
        error_detail = json.dumps(error_detail, ensure_ascii=False)
    
    return "注册失败：" + str(error_detail)

def generate_image(prompt, model):
    if not token:
        return None, "请先登录！"
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_URL}/api/images/text-to-image",
        headers=headers,
        json={"prompt": prompt, "model": model}
    )
    
    if response.status_code == 200:
        result = response.json()
        return result["image_url"], "生成成功！"
    return None, f"生成失败：{response.json().get('detail', '未知错误')}"

def generate_variation(image, prompt, model):
    if not token:
        return None, "请先登录！"
    
    if image is None:
        return None, "请先上传图片！"
    
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_URL}/api/images/image-to-image",
        headers=headers,
        json={
            "prompt": prompt,
            "image_data": img_str,
            "model": model
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        return result["image_url"], "生成成功！"
    return None, f"生成失败：{response.json().get('detail', '未知错误')}"

def get_my_images():
    if not token:
        return [], "请先登录！"
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{API_URL}/api/images/my-images",
        headers=headers
    )
    
    if response.status_code == 200:
        images = response.json()
        return [img["image_url"] for img in images], "获取成功！"
    return [], f"获取失败：{response.json().get('detail', '未知错误')}"

with gr.Blocks(title="PegaAI") as demo:
    gr.Markdown("# PegaAI")
    gr.Markdown("Author：风天行")
    
    with gr.Tab("用户", visible=True) as user_tab:
        with gr.Row():
            with gr.Column():
                gr.Markdown("## 注册")
                reg_username = gr.Textbox(label="用户名")
                reg_password = gr.Textbox(label="密码", type="password")
                reg_email = gr.Textbox(label="邮箱")
                reg_button = gr.Button("注册")
                reg_output = gr.Textbox(label="注册状态")
            
            with gr.Column():
                gr.Markdown("## 登录")
                login_username = gr.Textbox(label="用户名")
                login_password = gr.Textbox(label="密码", type="password")
                login_button = gr.Button("登录")
                login_output = gr.Textbox(label="登录状态")
    
    with gr.Tabs(visible=False) as func_tabs:
        with gr.TabItem("文生图"):
            with gr.Row():
                with gr.Column():
                    prompt = gr.Textbox(
                        label="提示词",
                        placeholder="一位年轻的龙骑士少女，身着精致的银色铠甲，骑在一头威武的红色巨龙背上，在火山喷发的背景下与一群奇幻生物战斗。画面风格偏向史诗奇幻，细节丰富，光影对比强烈。",
                        lines=2,
                        max_lines=20,
                        autoscroll=False,
                        show_copy_button=True
                    )
                    model = gr.Dropdown(
                        choices=["flux-t2v"],
                        value="flux-t2v",
                        label="选择模型"
                    )
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
                    var_model = gr.Dropdown(
                        choices=["flux-t2v"],
                        value="flux-t2v",
                        label="选择模型"
                    )
                    var_button = gr.Button("生成变体", variant="primary")
                    var_output = gr.Textbox(label="生成状态")
                with gr.Column():
                    var_image = gr.Image(label="生成结果")
        
        with gr.TabItem("我的图片"):
            refresh_button = gr.Button("刷新")
            gallery = gr.Gallery(label="我的图片")
            gallery_output = gr.Textbox(label="状态")
    
    # 绑定事件
    reg_button.click(register, [reg_username, reg_password, reg_email], reg_output)
    login_button.click(
        login, 
        [login_username, login_password], 
        [login_output, func_tabs, user_tab]
    )
    gen_button.click(generate_image, [prompt, model], [output_image, gen_output])
    var_button.click(generate_variation, [input_image, var_prompt, var_model], [var_image, var_output])
    refresh_button.click(get_my_images, [], [gallery, gallery_output])

if __name__ == "__main__":
    demo.launch() 
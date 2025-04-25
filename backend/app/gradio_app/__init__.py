import gradio as gr
from ..comfy.client import ComfyUIClient

# 创建 ComfyUI 客户端实例
client = ComfyUIClient()

def create_gradio_app():
    def text_to_image(prompt, negative_prompt, steps, guidance_scale, progress=gr.Progress()):
        progress(0, desc="正在连接到 ComfyUI 服务器...")
        progress(0.2, desc="正在处理提示词...")
        progress(0.4, desc="正在生成图像...")
        image = client.text_to_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            steps=steps,
            cfg=guidance_scale
        )
        progress(1.0, desc="生成完成！")
        return image

    def image_to_image(image, prompt, strength, progress=gr.Progress()):
        progress(0, desc="正在连接到 ComfyUI 服务器...")
        progress(0.2, desc="正在处理输入图像...")
        progress(0.4, desc="正在生成新图像...")
        result = client.image_to_image(
            image=image,
            prompt=prompt,
            strength=strength
        )
        progress(1.0, desc="生成完成！")
        return result

    with gr.Blocks(
        title="AI Image Generation",
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="blue",
            neutral_hue="slate",
            spacing_size="sm",
            radius_size="sm",
            font=["Source Sans Pro", "ui-sans-serif", "system-ui", "sans-serif"],
        ),
        analytics_enabled=False,
        show_error=True,
        cache_examples=False,
        show_api=False,
    ) as demo:
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("# AI 图像生成")
            with gr.Column(scale=1):
                gr.Markdown("### Author by 风天行", elem_classes=["author-text"])
        
        with gr.Tab("文本生成图像"):
            with gr.Row():
                with gr.Column():
                    prompt = gr.Textbox(label="提示词", placeholder="请输入提示词...", lines=3)
                    negative_prompt = gr.Textbox(label="反向提示词", placeholder="请输入反向提示词...", lines=3)
                    steps = gr.Slider(minimum=1, maximum=100, value=20, step=1, label="推理步数")
                    guidance_scale = gr.Slider(minimum=1, maximum=20, value=7, step=0.1, label="引导系数")
                    generate_btn = gr.Button("生成图像", variant="primary")
                with gr.Column():
                    output_image = gr.Image(label="生成的图像", type="pil")
            
            generate_btn.click(
                fn=text_to_image,
                inputs=[prompt, negative_prompt, steps, guidance_scale],
                outputs=output_image
            )
        
        with gr.Tab("图像转换"):
            with gr.Row():
                with gr.Column():
                    input_image = gr.Image(label="输入图像", type="pil")
                    prompt = gr.Textbox(label="提示词", placeholder="请输入提示词...", lines=3)
                    strength = gr.Slider(minimum=0, maximum=1, value=0.75, step=0.01, label="转换强度")
                    convert_btn = gr.Button("转换图像", variant="primary")
                with gr.Column():
                    output_image = gr.Image(label="转换后的图像", type="pil")
            
            convert_btn.click(
                fn=image_to_image,
                inputs=[input_image, prompt, strength],
                outputs=output_image
            )

    # 添加自定义 CSS
    demo.load(None, None, _js="""
        function() {
            const style = document.createElement('style');
            style.textContent = `
                .author-text {
                    text-align: right;
                    margin-top: 0;
                    color: #666;
                }
                .gradio-container {
                    max-width: 1200px;
                    margin: 0 auto;
                }
                .gradio-box {
                    padding: 1rem;
                }
                button.primary {
                    background-color: #2196F3;
                    color: white;
                }
                button.primary:hover {
                    background-color: #1976D2;
                }
            `;
            document.head.appendChild(style);
            return [];
        }
    """)

    return demo 
import gradio as gr
from modules.text2img import generate_image

def create_text2img_ui():
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
    
    # 绑定事件
    gen_button.click(
        fn=generate_image,
        inputs=[prompt, negative_prompt, steps, guidance],
        outputs=[output_image, gen_progress, gen_status],
        api_name="generate"
    )
    
    clear_button.click(
        fn=lambda: (None, 0, ""),
        inputs=[],
        outputs=[output_image, gen_progress, gen_status],
        api_name="clear"
    ) 
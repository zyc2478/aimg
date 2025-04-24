import gradio as gr
from ..api.routes.image_generation import pipe

def create_gradio_app():
    def text_to_image(prompt, negative_prompt, steps, guidance_scale):
        image = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=steps,
            guidance_scale=guidance_scale
        ).images[0]
        return image

    def image_to_image(image, prompt, strength):
        result = pipe(
            prompt=prompt,
            image=image,
            strength=strength
        ).images[0]
        return result

    with gr.Blocks(title="AI Image Generation") as demo:
        gr.Markdown("# AI 图像生成")
        
        with gr.Tab("文本生成图像"):
            with gr.Row():
                with gr.Column():
                    prompt = gr.Textbox(label="提示词")
                    negative_prompt = gr.Textbox(label="反向提示词")
                    steps = gr.Slider(minimum=1, maximum=100, value=50, step=1, label="推理步数")
                    guidance_scale = gr.Slider(minimum=1, maximum=20, value=7.5, step=0.1, label="引导系数")
                    generate_btn = gr.Button("生成图像")
                with gr.Column():
                    output_image = gr.Image(label="生成的图像")
            
            generate_btn.click(
                fn=text_to_image,
                inputs=[prompt, negative_prompt, steps, guidance_scale],
                outputs=output_image
            )
        
        with gr.Tab("图像转换"):
            with gr.Row():
                with gr.Column():
                    input_image = gr.Image(label="输入图像")
                    prompt = gr.Textbox(label="提示词")
                    strength = gr.Slider(minimum=0, maximum=1, value=0.75, step=0.01, label="转换强度")
                    convert_btn = gr.Button("转换图像")
                with gr.Column():
                    output_image = gr.Image(label="转换后的图像")
            
            convert_btn.click(
                fn=image_to_image,
                inputs=[input_image, prompt, strength],
                outputs=output_image
            )

    return demo 
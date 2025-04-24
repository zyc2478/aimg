from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional
from pydantic import BaseModel
import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import io

router = APIRouter()

# 加载模型
model_id = "runwayml/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    device_map="auto"
)

class TextToImageRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    num_inference_steps: Optional[int] = 50
    guidance_scale: Optional[float] = 7.5

@router.post("/text-to-image")
async def text_to_image(request: TextToImageRequest):
    try:
        image = pipe(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            num_inference_steps=request.num_inference_steps,
            guidance_scale=request.guidance_scale
        ).images[0]
        
        # 将图像转换为字节
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        return {"image": img_byte_arr}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/image-to-image")
async def image_to_image(
    file: UploadFile = File(...),
    prompt: Optional[str] = None,
    strength: Optional[float] = 0.75
):
    try:
        # 读取上传的图像
        image = Image.open(io.BytesIO(await file.read()))
        
        # 生成新图像
        result = pipe(
            prompt=prompt,
            image=image,
            strength=strength
        ).images[0]
        
        # 将图像转换为字节
        img_byte_arr = io.BytesIO()
        result.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        return {"image": img_byte_arr}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
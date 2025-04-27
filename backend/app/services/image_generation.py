import os
from typing import Optional
import torch
from diffusers import StableDiffusionPipeline
from app.core.config import settings
from app.models.image import Image
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

class ImageGenerationService:
    def __init__(self):
        self.device = settings.DEVICE
        self.model_path = settings.MODEL_PATH
        self.pipe = None
        self._load_model()

    def _load_model(self):
        if self.pipe is None:
            self.pipe = StableDiffusionPipeline.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            self.pipe = self.pipe.to(self.device)

    async def generate_image(
        self,
        db: Session,
        prompt: str,
        negative_prompt: Optional[str] = None,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
        width: int = 512,
        height: int = 512
    ) -> Image:
        # 生成图片
        image = self.pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            width=width,
            height=height
        ).images[0]

        # 保存图片
        filename = f"{uuid.uuid4()}.png"
        save_path = os.path.join(settings.GALLERY_DIR, filename)
        os.makedirs(settings.GALLERY_DIR, exist_ok=True)
        image.save(save_path)

        # 创建数据库记录
        db_image = Image(
            filename=filename,
            prompt=prompt,
            negative_prompt=negative_prompt,
            parameters={
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale,
                "width": width,
                "height": height
            }
        )
        db.add(db_image)
        db.commit()
        db.refresh(db_image)

        return db_image

    async def get_image(self, db: Session, image_id: int) -> Optional[Image]:
        return db.query(Image).filter(Image.id == image_id).first()

    async def list_images(self, db: Session, skip: int = 0, limit: int = 10):
        return db.query(Image).order_by(Image.created_at.desc()).offset(skip).limit(limit).all() 
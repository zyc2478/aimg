from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pathlib import Path
import httpx
from app.core.config import settings

class AIEngine(ABC):
    """AI引擎基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get("api_key", "")
        self.api_base = config.get("api_base", "")
        self.enabled = config.get("enabled", False)
    
    @abstractmethod
    async def text_to_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        **kwargs
    ) -> Path:
        """文生图"""
        pass
    
    @abstractmethod
    async def image_to_image(
        self,
        image_path: Path,
        prompt: str,
        negative_prompt: Optional[str] = None,
        **kwargs
    ) -> Path:
        """图生图"""
        pass
    
    @abstractmethod
    async def get_models(self) -> list:
        """获取可用模型列表"""
        pass

class StableDiffusionEngine(AIEngine):
    """Stable Diffusion引擎实现"""
    
    async def text_to_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        **kwargs
    ) -> Path:
        """文生图实现"""
        if not self.enabled:
            raise ValueError("Stable Diffusion引擎未启用")
        
        # 默认参数
        params = {
            "prompt": prompt,
            "negative_prompt": negative_prompt or "",
            "steps": kwargs.get("steps", 20),
            "width": kwargs.get("width", 512),
            "height": kwargs.get("height", 512),
            "cfg_scale": kwargs.get("cfg_scale", 7),
            "sampler_name": kwargs.get("sampler_name", "Euler a"),
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_base}/sdapi/v1/txt2img",
                json=params,
                headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
            )
            response.raise_for_status()
            result = response.json()
            
            # 保存图片
            import base64
            image_data = base64.b64decode(result["images"][0])
            output_path = settings.GALLERY_DIR / f"{result['info']['seed']}.png"
            output_path.write_bytes(image_data)
            return output_path
    
    async def image_to_image(
        self,
        image_path: Path,
        prompt: str,
        negative_prompt: Optional[str] = None,
        **kwargs
    ) -> Path:
        """图生图实现"""
        if not self.enabled:
            raise ValueError("Stable Diffusion引擎未启用")
        
        # 读取图片并转换为base64
        import base64
        image_data = base64.b64encode(image_path.read_bytes()).decode()
        
        # 默认参数
        params = {
            "init_images": [image_data],
            "prompt": prompt,
            "negative_prompt": negative_prompt or "",
            "steps": kwargs.get("steps", 20),
            "denoising_strength": kwargs.get("denoising_strength", 0.75),
            "cfg_scale": kwargs.get("cfg_scale", 7),
            "sampler_name": kwargs.get("sampler_name", "Euler a"),
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_base}/sdapi/v1/img2img",
                json=params,
                headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
            )
            response.raise_for_status()
            result = response.json()
            
            # 保存图片
            image_data = base64.b64decode(result["images"][0])
            output_path = settings.GALLERY_DIR / f"{result['info']['seed']}.png"
            output_path.write_bytes(image_data)
            return output_path
    
    async def get_models(self) -> list:
        """获取可用模型列表"""
        if not self.enabled:
            return []
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_base}/sdapi/v1/sd-models",
                headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
            )
            response.raise_for_status()
            return response.json()

class MidjourneyEngine(AIEngine):
    """Midjourney引擎实现"""
    
    async def text_to_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        **kwargs
    ) -> Path:
        """文生图实现"""
        if not self.enabled:
            raise ValueError("Midjourney引擎未启用")
        # TODO: 实现Midjourney API调用
        raise NotImplementedError("Midjourney引擎尚未实现")
    
    async def image_to_image(
        self,
        image_path: Path,
        prompt: str,
        negative_prompt: Optional[str] = None,
        **kwargs
    ) -> Path:
        """图生图实现"""
        if not self.enabled:
            raise ValueError("Midjourney引擎未启用")
        # TODO: 实现Midjourney API调用
        raise NotImplementedError("Midjourney引擎尚未实现")
    
    async def get_models(self) -> list:
        """获取可用模型列表"""
        if not self.enabled:
            return []
        # TODO: 实现Midjourney模型列表获取
        return []

# AI引擎工厂
def get_ai_engine(engine_name: str) -> AIEngine:
    """获取AI引擎实例"""
    engine_config = settings.AI_ENGINES.get(engine_name)
    if not engine_config:
        raise ValueError(f"未知的AI引擎: {engine_name}")
    
    if engine_name == "stable_diffusion":
        return StableDiffusionEngine(engine_config)
    elif engine_name == "midjourney":
        return MidjourneyEngine(engine_config)
    else:
        raise ValueError(f"不支持的AI引擎: {engine_name}") 
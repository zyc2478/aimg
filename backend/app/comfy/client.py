import requests
import json
import base64
from io import BytesIO
from PIL import Image
import time

class ComfyUIClient:
    def __init__(self, base_url="http://223.104.3.2:8188"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.timeout = 30  # 设置超时时间为30秒

    def _encode_image(self, image):
        if isinstance(image, str):
            with open(image, "rb") as f:
                return base64.b64encode(f.read()).decode()
        elif isinstance(image, Image.Image):
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode()
        else:
            raise ValueError("不支持的图像格式")

    def _make_request(self, method, url, **kwargs):
        try:
            kwargs['timeout'] = self.timeout
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.Timeout:
            raise Exception("请求超时，请检查服务器连接")
        except requests.exceptions.ConnectionError:
            raise Exception("无法连接到服务器，请检查网络连接")
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求失败: {str(e)}")

    def text_to_image(self, prompt, negative_prompt=None, steps=20, cfg=7):
        workflow = {
            "3": {
                "inputs": {
                    "text": prompt,
                    "clip": ["4", 0]
                },
                "class_type": "CLIPTextEncode"
            },
            "4": {
                "inputs": {
                    "ckpt_name": "sd_xl_base_1.0.safetensors"
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "5": {
                "inputs": {
                    "text": negative_prompt or "",
                    "clip": ["4", 0]
                },
                "class_type": "CLIPTextEncode"
            },
            "6": {
                "inputs": {
                    "samples": ["8", 0],
                    "vae": ["4", 2],
                    "positive": ["3", 0],
                    "negative": ["5", 0],
                    "latent_image": ["7", 0],
                    "model": ["4", 0],
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "seed": 8569857,
                    "steps": steps,
                    "cfg": cfg
                },
                "class_type": "KSampler"
            },
            "7": {
                "inputs": {
                    "width": 512,
                    "height": 512,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "8": {
                "inputs": {
                    "samples": ["6", 0],
                    "vae": ["4", 2]
                },
                "class_type": "VAEDecode"
            },
            "9": {
                "inputs": {
                    "filename_prefix": "ComfyUI",
                    "images": ["8", 0]
                },
                "class_type": "SaveImage"
            }
        }

        # 发送工作流到 ComfyUI
        response = self._make_request("POST", f"{self.api_url}/queue", json={"prompt": workflow})
        prompt_id = response.json()["prompt_id"]
        
        # 等待生成完成
        start_time = time.time()
        while True:
            if time.time() - start_time > self.timeout:
                raise Exception("生成超时，请重试")
                
            response = self._make_request("GET", f"{self.api_url}/history/{prompt_id}")
            history = response.json()
            
            if prompt_id in history:
                if "outputs" in history[prompt_id]:
                    # 获取生成的图像
                    image_data = history[prompt_id]["outputs"]["9"]["images"][0]
                    image_response = self._make_request("GET", f"{self.base_url}/view?filename={image_data['filename']}")
                    return Image.open(BytesIO(image_response.content))
                break
            
            time.sleep(0.5)

    def image_to_image(self, image, prompt, negative_prompt=None, strength=0.75, steps=20, cfg=7):
        # 编码输入图像
        encoded_image = self._encode_image(image)
        
        workflow = {
            "3": {
                "inputs": {
                    "text": prompt,
                    "clip": ["4", 0]
                },
                "class_type": "CLIPTextEncode"
            },
            "4": {
                "inputs": {
                    "ckpt_name": "sd_xl_base_1.0.safetensors"
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "5": {
                "inputs": {
                    "text": negative_prompt or "",
                    "clip": ["4", 0]
                },
                "class_type": "CLIPTextEncode"
            },
            "6": {
                "inputs": {
                    "samples": ["8", 0],
                    "vae": ["4", 2],
                    "positive": ["3", 0],
                    "negative": ["5", 0],
                    "latent_image": ["7", 0],
                    "model": ["4", 0],
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "seed": 8569857,
                    "steps": steps,
                    "cfg": cfg
                },
                "class_type": "KSampler"
            },
            "7": {
                "inputs": {
                    "image": encoded_image,
                    "vae": ["4", 2],
                    "strength": strength
                },
                "class_type": "VAEEncode"
            },
            "8": {
                "inputs": {
                    "samples": ["6", 0],
                    "vae": ["4", 2]
                },
                "class_type": "VAEDecode"
            },
            "9": {
                "inputs": {
                    "filename_prefix": "ComfyUI",
                    "images": ["8", 0]
                },
                "class_type": "SaveImage"
            }
        }

        # 发送工作流到 ComfyUI
        response = self._make_request("POST", f"{self.api_url}/queue", json={"prompt": workflow})
        prompt_id = response.json()["prompt_id"]
        
        # 等待生成完成
        start_time = time.time()
        while True:
            if time.time() - start_time > self.timeout:
                raise Exception("生成超时，请重试")
                
            response = self._make_request("GET", f"{self.api_url}/history/{prompt_id}")
            history = response.json()
            
            if prompt_id in history:
                if "outputs" in history[prompt_id]:
                    # 获取生成的图像
                    image_data = history[prompt_id]["outputs"]["9"]["images"][0]
                    image_response = self._make_request("GET", f"{self.base_url}/view?filename={image_data['filename']}")
                    return Image.open(BytesIO(image_response.content))
                break
            
            time.sleep(0.5) 
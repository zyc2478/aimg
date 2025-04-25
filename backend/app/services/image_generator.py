import json
from pathlib import Path
from typing import Optional, Dict, Any
from app.utils.comfyui_client import ComfyUIClient

class ImageGenerator:
    """图像生成服务类"""
    
    def __init__(self, host: str = "223.104.3.2", port: int = 8188):
        """
        初始化图像生成器
        
        Args:
            host: ComfyUI服务器地址
            port: ComfyUI服务器端口
        """
        self.host = host
        self.port = port
        self.workflow_path = Path(__file__).parent.parent / "config" / "workflows" / "txt2img.json"
        
    async def generate_image(self, prompt: str, output_path: Optional[Path] = None) -> Path:
        """
        生成图像
        
        Args:
            prompt: 图像生成提示词
            output_path: 输出路径，如果为None则使用默认路径
            
        Returns:
            Path: 生成的图像路径
        """
        # 加载工作流配置
        with open(self.workflow_path) as f:
            workflow = json.load(f)
            
        # 设置提示词
        inputs = {
            "6": {  # CLIPTextEncode节点
                "inputs": {
                    "text": prompt
                }
            }
        }
        
        print(f"开始生成图像，提示词: {prompt}")
        
        # 使用异步上下文管理器
        async with ComfyUIClient(host=self.host, port=self.port) as client:
            try:
                # 提交工作流
                prompt_id = await client.submit_prompt(workflow, inputs)
                print(f"工作流已提交，ID: {prompt_id}")
                
                # 连接WebSocket并等待结果
                await client.connect_websocket()
                result = await client.listen_websocket()
                
                if "image" in result:
                    # 保存生成的图像
                    if output_path is None:
                        output_path = Path("output.png")
                    with open(output_path, "wb") as f:
                        f.write(result["image"])
                    print(f"图像已保存到: {output_path}")
                    return output_path
                else:
                    raise Exception("生成图像失败")
                    
            except Exception as e:
                print(f"发生错误: {str(e)}")
                raise
                
    async def generate_image_with_params(self, 
                                       prompt: str,
                                       width: int = 1024,
                                       height: int = 1024,
                                       seed: int = 782619153058034,
                                       steps: int = 20,
                                       output_path: Optional[Path] = None) -> Path:
        """
        使用自定义参数生成图像
        
        Args:
            prompt: 图像生成提示词
            width: 图像宽度
            height: 图像高度
            seed: 随机种子
            steps: 生成步数
            output_path: 输出路径
            
        Returns:
            Path: 生成的图像路径
        """
        # 加载工作流配置
        with open(self.workflow_path) as f:
            workflow = json.load(f)
            
        # 设置自定义参数
        inputs = {
            "5": {  # EmptyLatentImage节点
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": 1
                }
            },
            "6": {  # CLIPTextEncode节点
                "inputs": {
                    "text": prompt
                }
            },
            "17": {  # BasicScheduler节点
                "inputs": {
                    "steps": steps
                }
            },
            "25": {  # RandomNoise节点
                "inputs": {
                    "noise_seed": seed
                }
            }
        }
        
        print(f"开始生成图像，提示词: {prompt}")
        print(f"参数: 宽度={width}, 高度={height}, 步数={steps}, 种子={seed}")
        
        # 使用异步上下文管理器
        async with ComfyUIClient(host=self.host, port=self.port) as client:
            try:
                # 提交工作流
                prompt_id = await client.submit_prompt(workflow, inputs)
                print(f"工作流已提交，ID: {prompt_id}")
                
                # 连接WebSocket并等待结果
                await client.connect_websocket()
                result = await client.listen_websocket()
                
                if "image" in result:
                    # 保存生成的图像
                    if output_path is None:
                        output_path = Path("output.png")
                    with open(output_path, "wb") as f:
                        f.write(result["image"])
                    print(f"图像已保存到: {output_path}")
                    return output_path
                else:
                    raise Exception("生成图像失败")
                    
            except Exception as e:
                print(f"发生错误: {str(e)}")
                raise 
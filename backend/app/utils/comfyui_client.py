import aiohttp
import asyncio
import json
import urllib.request
from typing import Dict, Any, Optional
import logging
import time

# 设置日志级别
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComfyUIClient:
    """ComfyUI API客户端"""
    
    def __init__(self, host="127.0.0.1", port=8188):
        """
        初始化ComfyUI客户端
        
        Args:
            host: ComfyUI服务器地址
            port: 服务器端口
        """
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.ws_url = f"ws://{host}:{port}/ws"
        self.session = None
        self.ws = None
        self.client_id = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.ws:
            await self.ws.close()
        if self.session:
            await self.session.close()
            
    async def check_connection(self) -> bool:
        """检查与ComfyUI服务器的连接"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            async with self.session.get(f"{self.base_url}/system_stats") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"检查连接失败: {str(e)}")
            return False
            
    async def execute_workflow(self, workflow: Dict[str, Any]) -> Optional[str]:
        """执行工作流并返回生成的图像URL"""
        try:
            # 生成唯一的client_id
            self.client_id = f"pegaai_{int(time.time())}"
            
            # 提交工作流
            prompt_id = await self.submit_prompt(workflow, self.client_id)
            if not prompt_id:
                raise Exception("提交工作流失败")
                
            # 连接WebSocket
            if not await self.connect_websocket(self.client_id):
                raise Exception("WebSocket连接失败")
                
            # 等待执行完成
            last_status_time = time.time()
            while True:
                result = await self.listen_websocket()
                current_time = time.time()
                
                if isinstance(result, dict):
                    if result.get("type") == "executing" and result.get("data", {}).get("node") is None:
                        # 执行完成，等待1秒后获取图像
                        await asyncio.sleep(1)
                        return await self.get_latest_image()
                        
                # 超时检查
                if current_time - last_status_time > 30:
                    raise Exception("执行超时")
                    
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"执行工作流失败: {str(e)}")
            return None
            
    async def get_latest_image(self) -> Optional[str]:
        """获取最新生成的图像URL"""
        try:
            async with self.session.get(f"{self.base_url}/history") as response:
                if response.status == 200:
                    history = await response.json()
                    if history:
                        latest_output = list(history.values())[-1]["outputs"]
                        if latest_output:
                            node_id = list(latest_output.keys())[0]
                            image_data = latest_output[node_id]["images"][0]
                            return f"{self.base_url}/view?filename={image_data['filename']}"
                return None
        except Exception as e:
            logger.error(f"获取最新图像失败: {str(e)}")
            return None
            
    async def connect_websocket(self, client_id=None):
        """连接到WebSocket服务器"""
        if client_id:
            self.client_id = client_id
            ws_url = f"{self.ws_url}?clientId={client_id}"
        else:
            ws_url = self.ws_url
        
        if self.ws:
            await self.ws.close()
        
        try:
            self.ws = await self.session.ws_connect(ws_url)
            return True
        except Exception as e:
            logger.error(f"WebSocket连接失败: {str(e)}")
            return False
            
    async def submit_prompt(self, workflow, client_id=None):
        """提交工作流到服务器"""
        if client_id:
            self.client_id = client_id
        
        try:
            data = {
                "prompt": workflow,
                "client_id": self.client_id
            }
            async with self.session.post(f"{self.base_url}/prompt", json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("prompt_id")
                else:
                    logger.error(f"提交工作流失败，状态码: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"提交工作流时出错: {str(e)}")
            return None
            
    async def listen_websocket(self):
        """监听WebSocket消息"""
        if not self.ws:
            logger.error("WebSocket未连接")
            return None
        
        try:
            msg = await self.ws.receive()
            if msg.type == aiohttp.WSMsgType.TEXT:
                return json.loads(msg.data)
            elif msg.type == aiohttp.WSMsgType.CLOSED:
                return {"type": "error", "error": "WebSocket closed"}
            elif msg.type == aiohttp.WSMsgType.ERROR:
                return {"type": "error", "error": str(msg.data)}
        except Exception as e:
            logger.error(f"接收WebSocket消息时出错: {str(e)}")
            return {"type": "error", "error": str(e)}
        
        return None
            
    async def get_image(self, filename: str) -> bytes:
        """
        获取生成的图片
        
        Args:
            filename: 图片文件名
            
        Returns:
            bytes: 图片二进制数据
        """
        try:
            async with self.session.get(f"{self.base_url}/view?filename={filename}") as response:
                if response.status == 200:
                    return await response.read()
                else:
                    raise Exception(f"获取图片失败，状态码: {response.status}")
        except Exception as e:
            logger.error(f"获取图片失败: {str(e)}")
            raise
            
    async def get_history(self) -> Dict[str, Any]:
        """
        获取历史记录
        
        Returns:
            Dict: 历史记录数据
        """
        try:
            async with self.session.get(f"{self.base_url}/history") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"获取历史记录失败，状态码: {response.status}")
        except Exception as e:
            logger.error(f"获取历史记录失败: {str(e)}")
            raise 
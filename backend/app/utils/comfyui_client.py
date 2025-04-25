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
            logger.info(f"WebSocket连接成功: {ws_url}")
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
                logger.error("WebSocket连接已关闭")
                return {"type": "error", "error": "WebSocket closed"}
            elif msg.type == aiohttp.WSMsgType.ERROR:
                logger.error("WebSocket错误")
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
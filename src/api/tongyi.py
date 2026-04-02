"""通义万相 API 客户端模块"""
import os
import dashscope
from dashscope.aigc.image_generation import ImageGeneration
from dashscope.api_entities.dashscope_response import Message
from typing import List


class TongyiClient:
    """通义万相 API 客户端"""
    
    def __init__(self, api_key: str, model: str = "wan2.7-image"):
        self.api_key = api_key
        self.model = model
        # 设置API基础URL
        dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'
    
    def generate_image(self, prompt: str, n: int = 1, size: str = "1024*1024") -> List[str]:
        """
        生成图片
        
        Args:
            prompt: 图片描述提示词
            n: 生成数量
            size: 图片尺寸
        
        Returns:
            图片URL列表
        """
        message = Message(
            role="user",
            content=[
                {"text": prompt}
            ]
        )
        
        rsp = ImageGeneration.call(
            model=self.model,
            api_key=self.api_key,
            messages=[message],
            n=n,
            size=size
        )
        
        if rsp.status_code != 200:
            raise Exception(f"API调用失败: {rsp.message}")
        
        # 解析返回的URL
        image_urls = []
        if hasattr(rsp, 'output') and hasattr(rsp.output, 'images'):
            image_urls = rsp.output.images
        
        return image_urls
    
    def generate_images_with_callback(self, prompt: str, n: int = 1, size: str = "1024*1024", 
                                     callback=None) -> List[str]:
        """
        带回调的图片生成（用于进度跟踪）
        
        Args:
            prompt: 图片描述提示词
            n: 生成数量
            size: 图片尺寸
            callback: 进度回调函数
        
        Returns:
            图片URL列表
        """
        message = Message(
            role="user",
            content=[
                {"text": prompt}
            ]
        )
        
        rsp = ImageGeneration.call(
            model=self.model,
            api_key=self.api_key,
            messages=[message],
            n=n,
            size=size
        )
        
        if rsp.status_code != 200:
            raise Exception(f"API调用失败: {rsp.message}")
        
        image_urls = []
        if hasattr(rsp, 'output') and hasattr(rsp.output, 'images'):
            image_urls = rsp.output.images
        
        return image_urls

"""通义万相 API 封装模块"""
import os
import time
from typing import List, Optional
from dashscope import MultiModalConversation
import dashscope


class TongyiClient:
    """通义万相 API 客户端"""
    
    def __init__(self, api_key: str, model: str = "qwen-image-2.0"):
        self.api_key = api_key
        self.model = model
        # 设置 API 基础 URL
        dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'
    
    def generate_image(self, prompt: str, image_urls: List[str] = None) -> Optional[str]:
        """调用通义万相 API 生成图片（文+图生图）"""
        try:
            # 构建消息内容
            content = []
            
            # 如果有商品图片，添加到消息中
            if image_urls:
                for img_url in image_urls:
                    content.append({"image": img_url})
            
            # 添加文本提示词
            content.append({"text": prompt})
            
            messages = [
                {
                    "role": "user",
                    "content": content
                }
            ]
            
            # 调用 API
            response = MultiModalConversation.call(
                api_key=self.api_key,
                model=self.model,
                messages=messages,
                result_format='message',
                stream=False,
                n=1,
                watermark=False,
                negative_prompt=""
            )
            
            # 解析响应
            if response.status_code == 200:
                result = response.output.choices[0].message.content
                if result and len(result) > 0:
                    # 获取生成的图片 URL
                    for item in result:
                        if 'image' in item:
                            return item['image']
                return None
            else:
                print(f"通义 API 调用失败: {response.code} - {response.message}")
                return None
                
        except Exception as e:
            print(f"通义 API 调用异常: {e}")
            return None
    
    def generate_buyer_show_image(self, prompt: str, image_urls: List[str] = None) -> Optional[str]:
        """生成买家秀图片"""
        return self.generate_image(prompt, image_urls)
    
    def generate_multiple_images(self, prompts: List[str], 
                                  image_urls: List[str] = None) -> List[Optional[str]]:
        """生成多张买家秀图片"""
        results = []
        
        for i, prompt in enumerate(prompts):
            print(f"生成第 {i+1} 张图片...")
            result = self.generate_image(prompt, image_urls)
            results.append(result)
            
            # 延迟等待，避免 API 限流
            if i < len(prompts) - 1:
                time.sleep(2)
        
        return results
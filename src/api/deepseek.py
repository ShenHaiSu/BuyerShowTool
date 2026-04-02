"""DeepSeek API 客户端模块"""
import requests
from typing import Optional, List, Dict, Any


class DeepSeekClient:
    """DeepSeek API 客户端"""
    
    def __init__(self, api_key: str, model: str = "deepseek-chat", base_url: str = "https://api.deepseek.com/v1/chat/completions"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """
        发送聊天请求
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            temperature: 温度参数
            max_tokens: 最大token数
        
        Returns:
            API返回的文本内容
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(self.base_url, headers=self.headers, json=payload, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    def chat_with_system(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """
        带系统提示词的聊天请求
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户输入
            temperature: 温度参数
        
        Returns:
            API返回的文本内容
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        return self.chat(messages, temperature)

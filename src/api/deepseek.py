"""DeepSeek API 封装模块"""
import requests
from typing import List, Dict, Optional
import time


class DeepSeekClient:
    """DeepSeek API 客户端"""
    
    def __init__(self, api_key: str, model: str = "deepseek-chat", 
                 base_url: str = "https://api.deepseek.com/v1/chat/completions"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def chat(self, messages: List[Dict[str, str]], 
             temperature: float = 0.7, 
             max_tokens: int = 1000) -> Optional[str]:
        """调用 DeepSeek Chat API 生成文本"""
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(self.base_url, json=payload, headers=self.headers, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                return data['choices'][0]['message']['content']
            return None
        except requests.exceptions.RequestException as e:
            print(f"DeepSeek API 调用失败: {e}")
            return None
        except KeyError as e:
            print(f"DeepSeek API 响应格式错误: {e}")
            return None
        except Exception as e:
            print(f"DeepSeek API 调用异常: {e}")
            return None
    
    def generate_review(self, system_prompt: str, goods_info: str, 
                        temperature: float = 0.7) -> Optional[str]:
        """生成好评文案"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": goods_info + "\n\n请生成80字左右的买家好评文案。"}
        ]
        
        return self.chat(messages, temperature=temperature)
    
    def generate_multiple_reviews(self, system_prompt: str, goods_info: str, 
                                   count: int = 4, min_temp: float = 0.7, 
                                   max_temp: float = 1.0) -> List[str]:
        """生成多条好评文案"""
        reviews = []
        
        for i in range(count):
            # 每次使用不同的 temperature 值
            temp = min_temp + (max_temp - min_temp) * (i / max(count - 1, 1))
            
            review = self.generate_review(system_prompt, goods_info, temperature=temp)
            if review:
                reviews.append(review)
            
            # 延迟等待，避免 API 限流
            if i < count - 1:
                time.sleep(1)
        
        return reviews
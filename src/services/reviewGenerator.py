"""好评文案生成服务模块"""
import os
import sys
import time
from typing import List
from src.api.deepseek import DeepSeekClient
from src.config.types import Config, GoodsData
from src.services.goodsParser import GoodsParser
from src.utils.file import save_text_file


class ReviewGenerator:
    """好评文案生成服务"""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = DeepSeekClient(
            api_key=config.deepseek.apiKey,
            model=config.deepseek.model,
            base_url=config.deepseek.url
        )
        self.parser = GoodsParser()
    
    def generate_reviews(self, goods_data: GoodsData, target_dir: str) -> List[str]:
        """生成好评文案并保存到文件"""
        # 构建商品信息字符串
        goods_info_str = self.parser.parse_goods_info(goods_data.goods)
        
        # 获取系统提示词
        system_prompt = self.config.deepseek.systemPrompt
        
        # 获取生成次数
        review_count = self.config.deepseek.reviewCount
        
        print(f"\n📝 开始生成好评文案: 共 {review_count} 条")
        print("-" * 50)
        
        # 生成多条好评文案（带进度展示）
        reviews = self._generate_reviews_with_progress(
            system_prompt=system_prompt,
            goods_info=goods_info_str,
            count=review_count
        )
        
        if not reviews:
            print("\n⚠️ 未能生成任何好评文案")
            return []
        
        print(f"\n✅ 好评文案生成完成: 成功 {len(reviews)}/{review_count} 条")
        
        # 保存到文件
        self._save_reviews(reviews, target_dir)
        
        return reviews
    
    def _generate_reviews_with_progress(self, system_prompt: str, goods_info: str, count: int) -> List[str]:
        """生成多条好评文案并显示进度"""
        reviews = []
        start_time = time.time()
        
        for i in range(count):
            # 每次使用不同的 temperature 值
            temp = 0.7 + (1.0 - 0.7) * (i / max(count - 1, 1))
            
            # 显示当前进度
            elapsed = time.time() - start_time
            percent = int(((i + 1) / count) * 100)
            bar_length = 20
            filled = int((i + 1) / count * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            print(f"\r  📝 好评文案进度: [{bar}] {percent}% ({i+1}/{count})", end="")
            sys.stdout.flush()
            
            # 生成单条好评文案
            review = self.client.generate_review(system_prompt, goods_info, temperature=temp)
            if review:
                reviews.append(review)
                print(f"\r  ✅ 第 {i+1} 条好评文案生成成功")
            else:
                print(f"\r  ❌ 第 {i+1} 条好评文案生成失败")
            
            # 延迟等待，避免 API 限流
            if i < count - 1:
                time.sleep(1)
        
        print()  # 换行
        return reviews
    
    def _save_reviews(self, reviews: List[str], target_dir: str) -> None:
        """保存好评文案到文件"""
        content_lines = []
        
        for i, review in enumerate(reviews, 1):
            content_lines.append(f"=== 第{i}条 ===")
            content_lines.append(review.strip())
            content_lines.append("")  # 空行
        
        content = "\n".join(content_lines)
        
        output_path = os.path.join(target_dir, "review.txt")
        save_text_file(output_path, content)
        
        print(f"好评文案已保存到: {output_path}")
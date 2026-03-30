"""好评文案生成服务模块"""
import os
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
        
        print(f"开始生成 {review_count} 条好评文案...")
        
        # 生成多条好评文案
        reviews = self.client.generate_multiple_reviews(
            system_prompt=system_prompt,
            goods_info=goods_info_str,
            count=review_count,
            min_temp=0.7,
            max_temp=1.0
        )
        
        if not reviews:
            print("未能生成任何好评文案")
            return []
        
        print(f"成功生成 {len(reviews)} 条好评文案")
        
        # 保存到文件
        self._save_reviews(reviews, target_dir)
        
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
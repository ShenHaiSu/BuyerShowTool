"""买家秀图片生成服务模块"""
import os
import random
import sys
import time
from typing import List, Optional
from src.api.tongyi import TongyiClient
from src.config.types import Config, GoodsData
from src.services.goodsParser import GoodsParser
from src.utils.file import download_image


class ImageGenerator:
    """买家秀图片生成服务"""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = TongyiClient(
            api_key=config.tongyi.apiKey,
            model=config.tongyi.model
        )
        self.parser = GoodsParser()
    
    def generate_buyer_show_images(self, goods_data: GoodsData, target_dir: str) -> List[str]:
        """生成买家秀图片"""
        # 获取图片生成数量
        image_count = self.config.tongyi.imageCount
        
        print(f"\n🖼️ 开始生成买家秀图片: 共 {image_count} 张")
        print("-" * 50)
        
        # 获取商品图片路径
        image_urls = self._get_image_paths(goods_data.images, target_dir)
        
        if not image_urls:
            print("⚠️ 警告: 未找到商品图片，可能影响生成效果")
        
        # 生成多张图片（带进度展示）
        saved_paths = self._generate_images_with_progress(
            goods_data=goods_data,
            target_dir=target_dir,
            image_urls=image_urls,
            image_count=image_count
        )
        
        print(f"\n✅ 买家秀图片生成完成: 成功 {len(saved_paths)}/{image_count} 张")
        return saved_paths
    
    def _generate_images_with_progress(self, goods_data: GoodsData, target_dir: str,
                                        image_urls: List[str], image_count: int) -> List[str]:
        """生成多张图片并显示进度"""
        saved_paths = []
        start_time = time.time()
        
        for i in range(image_count):
            # 显示当前进度
            elapsed = time.time() - start_time
            percent = int(((i + 1) / image_count) * 100)
            bar_length = 20
            filled = int((i + 1) / image_count * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            print(f"\r  🖼️ 买家秀进度: [{bar}] {percent}% ({i+1}/{image_count})", end="")
            sys.stdout.flush()
            
            # 构建提示词
            prompt = self._build_prompt(goods_data)
            
            # 调用 API 生成图片
            image_url = self.client.generate_buyer_show_image(prompt, image_urls)
            
            if image_url:
                # 下载并保存图片
                save_path = os.path.join(target_dir, f"buyer_show_{i+1}.jpg")
                if download_image(image_url, save_path):
                    saved_paths.append(save_path)
                    print(f"\r  ✅ 第 {i+1} 张图片生成并保存成功")
                else:
                    print(f"\r  ❌ 第 {i+1} 张图片下载失败")
            else:
                print(f"\r  ❌ 第 {i+1} 张图片生成失败")
            
            # 延迟等待，避免 API 限流
            if i < image_count - 1:
                time.sleep(2)
        
        print()  # 换行
        return saved_paths
    
    def _get_image_paths(self, images: List[str], target_dir: str) -> List[str]:
        """获取商品图片的本地路径"""
        image_paths = []
        
        for img in images:
            img_path = os.path.join(target_dir, img)
            if os.path.exists(img_path):
                # 转换为 file:// URL 格式
                img_path = img_path.replace('\\', '/')
                image_paths.append(f"file://{img_path}")
            else:
                print(f"图片文件不存在: {img}")
        
        return image_paths
    
    def _build_prompt(self, goods_data: GoodsData) -> str:
        """构建图片生成提示词"""
        # 随机选择背景
        backgrounds = ["家居室内客厅环境", "户外草地环境"]
        background = random.choice(backgrounds)
        
        # 随机选择姿势
        poses = ["站立", "坐着", "行走", "转身", "侧面展示"]
        pose = random.choice(poses)
        
        # 获取系统提示词
        system_prompt = self.config.tongyi.systemPrompt
        
        # 构建商品信息
        goods_info = goods_data.goods
        
        prompt_parts = [system_prompt]
        prompt_parts.append("")
        prompt_parts.append(f"商品名称: {goods_info.name}")
        prompt_parts.append(f"品类: {goods_info.category}")
        prompt_parts.append(f"适用性别: {goods_info.gender}")
        prompt_parts.append(f"适用年龄: {goods_info.ageGroup}")
        prompt_parts.append(f"年份: {goods_info.year}")
        prompt_parts.append(f"季节: {goods_info.season}")
        prompt_parts.append(f"袖长: {goods_info.sleeveLength}")
        prompt_parts.append(f"领型: {goods_info.collarType}")
        
        if goods_info.features:
            features_str = ", ".join(goods_info.features)
            prompt_parts.append(f"特殊卖点: {features_str}")
        
        prompt_parts.append("")
        prompt_parts.append(f"请生成一张买家秀模特图，背景为{background}，模特姿势{pose}，图片主体为商品本身，不显示模特面部和头部，模特为亚洲中国中年男士，画面真实自然，符合真实买家秀风格。")
        
        return "\n".join(prompt_parts)
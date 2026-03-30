"""商品信息解析器模块"""
from typing import Dict, Any
from src.config.types import GoodsInfo, GoodsData


class GoodsParser:
    """商品信息解析器"""
    
    @staticmethod
    def parse_goods_info(goods_info: GoodsInfo) -> str:
        """将商品信息转换为适合 API 调用的字符串格式"""
        info_parts = []
        
        info_parts.append(f"商品名称: {goods_info.name}")
        info_parts.append(f"品类: {goods_info.category}")
        info_parts.append(f"适用性别: {goods_info.gender}")
        info_parts.append(f"适用年龄: {goods_info.ageGroup}")
        info_parts.append(f"年份: {goods_info.year}")
        info_parts.append(f"季节: {goods_info.season}")
        
        if goods_info.pantsLength:
            info_parts.append(f"裤长: {goods_info.pantsLength}")
        
        info_parts.append(f"袖长: {goods_info.sleeveLength}")
        info_parts.append(f"领型: {goods_info.collarType}")
        info_parts.append(f"穿戴方式: {goods_info.wearType}")
        
        if goods_info.features:
            features_str = ", ".join(goods_info.features)
            info_parts.append(f"特殊卖点: {features_str}")
        
        return "\n".join(info_parts)
    
    @staticmethod
    def build_image_prompt(goods_info: GoodsInfo) -> str:
        """构建图片生成的提示词"""
        # 随机选择背景
        import random
        backgrounds = ["家居室内客厅环境", "户外草地环境"]
        background = random.choice(backgrounds)
        
        # 随机选择姿势
        poses = ["站立", "坐着", "行走", "转身"]
        pose = random.choice(poses)
        
        prompt_parts = []
        
        prompt_parts.append(f"商品名称: {goods_info.name}")
        prompt_parts.append(f"品类: {goods_info.category}")
        prompt_parts.append(f"适用性别: {goods_info.gender}")
        prompt_parts.append(f"年龄: {goods_info.ageGroup}")
        prompt_parts.append(f"年份: {goods_info.year}")
        prompt_parts.append(f"季节: {goods_info.season}")
        prompt_parts.append(f"袖长: {goods_info.sleeveLength}")
        prompt_parts.append(f"领型: {goods_info.collarType}")
        
        if goods_info.features:
            features_str = ", ".join(goods_info.features)
            prompt_parts.append(f"特殊卖点: {features_str}")
        
        prompt_parts.append(f"请生成一张买家秀模特图，背景为{background}，模特姿势{pose}，图片主体为商品本身，不显示模特面部和头部")
        
        return "\n".join(prompt_parts)
    
    @staticmethod
    def validate_images(images: list, target_dir: str) -> list:
        """验证商品图片是否存在"""
        import os
        valid_images = []
        
        for img in images:
            img_path = os.path.join(target_dir, img)
            if os.path.exists(img_path):
                valid_images.append(img)
            else:
                print(f"图片文件不存在: {img}")
        
        return valid_images
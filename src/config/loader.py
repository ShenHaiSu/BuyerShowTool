"""配置加载器模块"""
import os
import yaml
from typing import Tuple
from src.config.types import Config, DeepSeekConfig, TongyiConfig, GoodsData, GoodsInfo


def load_config(config_path: str = "config.yaml") -> Config:
    """加载项目根目录的 config.yaml 配置文件"""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}，请创建配置文件")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    if not data:
        raise ValueError("配置文件为空")
    
    # 验证必要字段
    if 'deepseek' not in data:
        raise ValueError("配置文件缺少 deepseek 配置")
    if 'tongyi' not in data:
        raise ValueError("配置文件缺少 tongyi 配置")
    
    deepseek_data = data['deepseek']
    tongyi_data = data['tongyi']
    
    # 验证 DeepSeek 配置
    required_deepseek_fields = ['url', 'apiKey', 'model', 'systemPrompt', 'reviewCount']
    for field in required_deepseek_fields:
        if field not in deepseek_data:
            raise ValueError(f"DeepSeek 配置缺少必要字段: {field}")
    
    # 验证通义配置
    required_tongyi_fields = ['url', 'apiKey', 'model', 'systemPrompt', 'imageCount']
    for field in required_tongyi_fields:
        if field not in tongyi_data:
            raise ValueError(f"通义配置缺少必要字段: {field}")
    
    deepseek_config = DeepSeekConfig(
        url=deepseek_data['url'],
        apiKey=deepseek_data['apiKey'],
        model=deepseek_data['model'],
        systemPrompt=deepseek_data['systemPrompt'],
        reviewCount=deepseek_data['reviewCount']
    )
    
    tongyi_config = TongyiConfig(
        url=tongyi_data['url'],
        apiKey=tongyi_data['apiKey'],
        model=tongyi_data['model'],
        systemPrompt=tongyi_data['systemPrompt'],
        imageCount=tongyi_data['imageCount']
    )
    
    return Config(deepseek=deepseek_config, tongyi=tongyi_config)


def load_goods_data(target_dir: str) -> GoodsData:
    """加载目标路径下的 goods.yaml 商品信息"""
    goods_yaml_path = os.path.join(target_dir, "goods.yaml")
    
    if not os.path.exists(goods_yaml_path):
        raise FileNotFoundError(f"商品配置文件不存在: {goods_yaml_path}，请在目标路径下创建 goods.yaml")
    
    with open(goods_yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    if not data:
        raise ValueError("商品配置文件为空")
    
    if 'goods' not in data:
        raise ValueError("商品配置文件缺少 goods 字段")
    
    goods_data = data['goods']
    images = data.get('images', [])
    
    # 验证商品必要字段
    required_goods_fields = ['name', 'category', 'gender', 'ageGroup', 'year', 
                             'season', 'sleeveLength', 'collarType', 'wearType', 'features']
    for field in required_goods_fields:
        if field not in goods_data:
            raise ValueError(f"商品信息缺少必要字段: {field}")
    
    goods_info = GoodsInfo(
        name=goods_data['name'],
        category=goods_data['category'],
        gender=goods_data['gender'],
        ageGroup=goods_data['ageGroup'],
        year=goods_data['year'],
        season=goods_data['season'],
        pantsLength=goods_data.get('pantsLength', ''),
        sleeveLength=goods_data['sleeveLength'],
        collarType=goods_data['collarType'],
        wearType=goods_data['wearType'],
        features=goods_data['features']
    )
    
    return GoodsData(goods=goods_info, images=images)


def load_all_config(target_dir: str) -> Tuple[Config, GoodsData]:
    """加载所有配置"""
    config = load_config()
    goods_data = load_goods_data(target_dir)
    return config, goods_data
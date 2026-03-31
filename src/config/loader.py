"""配置加载器模块"""
import os
import yaml
from typing import Tuple
from src.config.types import Config, DeepSeekConfig, TongyiConfig, GoodsData, GoodsInfo


# 内置 config.example.yaml 模板内容
CONFIG_EXAMPLE_TEMPLATE = """# DeepSeek API 配置（用于生成好评文案）
deepseek:
  # API 请求地址
  url: "https://api.deepseek.com/v1/chat/completions"
  # API 密钥
  apiKey: "your-deepseek-api-key-here"
  # 模型名称（如 deepseek-chat）
  model: "deepseek-chat"
  # 前调提示词（后续会拼接目标路径下的 goods.yaml 作为完整提示词）
  systemPrompt: |
    你是一位专业的电商运营专家，擅长撰写真实、客观的买家好评文案。
    请根据提供的商品信息生成买家好评文案。
    要求：
    - 字数80字左右
    - 使用较为中肯的语气
    - 禁止使用感叹号
    - 禁止使用夸张的语态
    - 禁止使用"太棒了"、"超级推荐"等夸张词汇
  # 好评文案生成次数（3-5次，提升可用率的命中）
  # 每次生成会基于相同的商品信息但可能产生不同的文案
  # 最终会保存所有生成的文案供用户选择
  reviewCount: 4

# 通义万相 API 配置（用于生成买家秀图片）
tongyi:
  # API 请求地址
  url: "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/generation"
  # API 密钥
  apiKey: "your-tongyi-api-key-here"
  # 模型名称（如 wanx-v1 或 qwen3.5-flash）
  model: "wanx-v1"
  # 前调提示词（后续会拼接商品信息作为完整提示词）
  systemPrompt: |
    请生成一张电商买家秀模特图。
    要求：
    - 模特不出现面部和头部
    - 背景为家居室内客厅环境或户外草地环境
    - 随机生成合适的姿势
    - 图片主体为商品本身
    - 画面真实自然，符合真实买家秀风格
  # 输出图片数量（3-5张）
  imageCount: 4
"""

# 内置 goods.yaml 模板内容
GOODS_TEMPLATE = """# 商品基本信息
goods:
  # 商品名称
  name: "商品名称"
  # 品类
  category: "品类"
  # 适用性别
  gender: "男"
  # 适用年龄
  ageGroup: "青年"
  # 年份
  year: "2024"
  # 季节
  season: "春夏季"
  # 裤长（如果是裤子）
  pantsLength: ""
  # 袖长
  sleeveLength: "短袖"
  # 领型
  collarType: "圆领"
  # 穿戴方式
  wearType: "套头"
  # 特殊卖点或功能
  features:
    - "卖点1"
    - "卖点2"

# 商品图片文件列表（支持 jpg/jpeg/png）
images:
  - "front.jpg"
  - "back.jpg"
"""


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


def check_and_generate_config() -> bool:
    """
    检查并生成配置文件
    
    Returns:
        bool: config.yaml 是否已存在
    """
    config_path = "config.yaml"
    example_path = "config.example.yaml"
    
    if os.path.exists(config_path):
        return True
    
    # 检查 config.example.yaml 是否存在
    if not os.path.exists(example_path):
        # 生成模板文件
        with open(example_path, 'w', encoding='utf-8') as f:
            f.write(CONFIG_EXAMPLE_TEMPLATE)
    
    return False


def generate_goods_yaml_template(target_dir: str) -> str:
    """
    生成 goods.yaml 模板到目标目录
    
    Args:
        target_dir: 目标目录路径
    
    Returns:
        str: 生成的模板文件路径
    """
    goods_yaml_path = os.path.join(target_dir, "goods.yaml")
    
    # 如果已存在则不覆盖
    if os.path.exists(goods_yaml_path):
        return goods_yaml_path
    
    with open(goods_yaml_path, 'w', encoding='utf-8') as f:
        f.write(GOODS_TEMPLATE)
    
    return goods_yaml_path
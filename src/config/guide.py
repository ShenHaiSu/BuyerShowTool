"""用户引导模块"""
import os
import shutil


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


def ensure_config_exists() -> bool:
    """
    确保 config.yaml 存在，如果不存在则生成 config.example.yaml
    
    Returns:
        bool: config.yaml 是否已存在
    """
    config_path = "config.yaml"
    example_path = "config.example.yaml"
    
    # 检查 config.yaml 是否存在
    if os.path.exists(config_path):
        return True
    
    # 检查 config.example.yaml 是否存在
    if not os.path.exists(example_path):
        # 生成模板文件
        generate_config_example()
    
    return False


def generate_config_example() -> str:
    """
    生成 config.example.yaml 模板文件
    
    Returns:
        str: 生成的模板文件路径
    """
    example_path = "config.example.yaml"
    
    with open(example_path, 'w', encoding='utf-8') as f:
        f.write(CONFIG_EXAMPLE_TEMPLATE)
    
    return example_path


def generate_goods_template(target_dir: str) -> str:
    """
    生成 goods.yaml 模板文件到目标目录
    
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


def print_guide_message(config_exists: bool, goods_exists: bool):
    """
    打印用户引导提示信息
    
    Args:
        config_exists: config.yaml 是否存在
        goods_exists: goods.yaml 是否存在
    """
    print()
    print("=" * 50)
    print("配置引导")
    print("=" * 50)
    
    if not config_exists:
        print("错误: 配置文件不存在")
        print()
        print("请先配置项目:")
        print("1. 复制 config.example.yaml 为 config.yaml")
        print("2. 修改 config.yaml 中的 API 密钥配置")
        print("3. 重新运行程序")
        print()
        print("配置文件已生成: config.example.yaml")
    elif not goods_exists:
        print("错误: 商品配置文件不存在")
        print()
        print("请先配置商品信息:")
        print("1. 编辑 goods.yaml 文件")
        print("2. 配置商品名称、图片等信息")
        print("3. 重新运行程序")
        print()
        print("商品配置模板已生成: goods.yaml")
    
    print("=" * 50)
"""类型定义模块"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class DeepSeekConfig:
    """DeepSeek API 配置"""
    url: str
    apiKey: str
    model: str
    systemPrompt: str
    reviewCount: int


@dataclass
class TongyiConfig:
    """通义万相 API 配置"""
    url: str
    apiKey: str
    model: str
    systemPrompt: str
    imageCount: int


@dataclass
class Config:
    """项目配置"""
    deepseek: DeepSeekConfig
    tongyi: TongyiConfig


@dataclass
class GoodsInfo:
    """商品信息"""
    name: str
    category: str
    gender: str
    ageGroup: str
    year: str
    season: str
    pantsLength: Optional[str]
    sleeveLength: str
    collarType: str
    wearType: str
    features: List[str]


@dataclass
class GoodsData:
    """商品数据"""
    goods: GoodsInfo
    images: List[str]
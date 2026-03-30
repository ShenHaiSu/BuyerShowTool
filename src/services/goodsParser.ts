/**
 * 商品信息解析器
 * 负责解析和转换商品信息为适合 API 调用的格式
 */

import type { GoodsInfo, GoodsBasicInfo } from "../config/types";

/**
 * 错误类：商品信息解析相关错误
 */
export class GoodsParserError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "GoodsParserError";
  }
}

/**
 * 商品信息解析器
 */
export class GoodsParser {
  /**
   * 解析商品信息
   * @param goodsInfo - 原始商品信息
   * @returns 解析后的商品信息
   */
  public parse(goodsInfo: GoodsInfo): ParsedGoodsInfo {
    this.validate(goodsInfo);

    return {
      name: goodsInfo.goods.name,
      category: goodsInfo.goods.category,
      gender: goodsInfo.goods.gender,
      ageGroup: goodsInfo.goods.ageGroup,
      year: goodsInfo.goods.year,
      season: goodsInfo.goods.season,
      pantsLength: goodsInfo.goods.pantsLength || "",
      sleeveLength: goodsInfo.goods.sleeveLength,
      collarType: goodsInfo.goods.collarType,
      wearType: goodsInfo.goods.wearType,
      features: goodsInfo.goods.features,
      images: goodsInfo.images,
    };
  }

  /**
   * 验证商品信息完整性
   * @param goodsInfo - 商品信息
   */
  private validate(goodsInfo: GoodsInfo): void {
    if (!goodsInfo.goods) {
      throw new GoodsParserError("商品信息不能为空");
    }

    const requiredFields: (keyof GoodsBasicInfo)[] = [
      "name",
      "category",
      "gender",
      "ageGroup",
      "year",
      "season",
      "sleeveLength",
      "collarType",
      "wearType",
      "features",
    ];

    for (const field of requiredFields) {
      if (!goodsInfo.goods[field]) {
        throw new GoodsParserError(`商品信息缺少必要字段: ${field}`);
      }
    }

    if (!goodsInfo.images || goodsInfo.images.length === 0) {
      throw new GoodsParserError("商品图片列表不能为空");
    }
  }

  /**
   * 将商品信息转换为 DeepSeek 提示词格式
   * @param goodsInfo - 解析后的商品信息
   * @returns 格式化的商品信息文本
   */
  public toReviewPrompt(goodsInfo: ParsedGoodsInfo): string {
    const lines: string[] = [
      `商品名称: ${goodsInfo.name}`,
      `品类: ${goodsInfo.category}`,
      `适用性别: ${goodsInfo.gender}`,
      `适用年龄: ${goodsInfo.ageGroup}`,
      `年份: ${goodsInfo.year}`,
      `季节: ${goodsInfo.season}`,
    ];

    if (goodsInfo.pantsLength) {
      lines.push(`裤长: ${goodsInfo.pantsLength}`);
    }

    lines.push(`袖长: ${goodsInfo.sleeveLength}`);
    lines.push(`领型: ${goodsInfo.collarType}`);
    lines.push(`穿戴方式: ${goodsInfo.wearType}`);
    lines.push(`特殊卖点: ${goodsInfo.features.join("、")}`);

    return lines.join("\n");
  }

  /**
   * 将商品信息转换为通义万相提示词格式
   * @param goodsInfo - 解析后的商品信息
   * @returns 格式化的商品信息文本
   */
  public toImagePrompt(goodsInfo: ParsedGoodsInfo): string {
    const backgrounds = ["家居室内客厅环境", "户外草地环境"];
    const randomBackground = backgrounds[Math.floor(Math.random() * backgrounds.length)];

    const lines: string[] = [
      `商品名称: ${goodsInfo.name}`,
      `商品品类: ${goodsInfo.category}`,
      `适用性别: ${goodsInfo.gender}`,
      `年龄: ${goodsInfo.ageGroup}`,
      `年份: ${goodsInfo.year}`,
      `季节: ${goodsInfo.season}`,
      `袖长: ${goodsInfo.sleeveLength}`,
      `领型: ${goodsInfo.collarType}`,
      `特殊卖点: ${goodsInfo.features.join("、")}`,
      `请生成一张买家秀模特图，背景为${randomBackground}，模特姿势自然，图片主体为商品本身，不显示模特面部和头部`,
    ];

    return lines.join("\n");
  }
}

/**
 * 解析后的商品信息
 */
export interface ParsedGoodsInfo {
  name: string;
  category: string;
  gender: string;
  ageGroup: string;
  year: string;
  season: string;
  pantsLength: string;
  sleeveLength: string;
  collarType: string;
  wearType: string;
  features: string[];
  images: string[];
}

/**
 * 创建商品信息解析器的工厂函数
 * @returns GoodsParser 实例
 */
export function createGoodsParser(): GoodsParser {
  return new GoodsParser();
}
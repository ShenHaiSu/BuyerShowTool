/**
 * 好评文案生成服务
 * 负责调用 DeepSeek API 生成买家好评文案
 */

import type { DeepSeekMessage, DeepSeekConfig } from "../config/types";
import type { ParsedGoodsInfo } from "./goodsParser";
import { DeepSeekClient, createDeepSeekClient } from "../api/deepseek";
import { Logger } from "../utils/logger";
import { saveTextFile, getReviewFilePath, formatReviewContent } from "../utils/file";

/**
 * 错误类：好评文案生成相关错误
 */
export class ReviewGeneratorError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ReviewGeneratorError";
  }
}

/**
 * 好评文案生成服务
 */
export class ReviewGenerator {
  private client: DeepSeekClient;
  private config: DeepSeekConfig;
  private logger: Logger;

  /**
   * 创建好评文案生成服务
   * @param config - DeepSeek 配置
   * @param logger - 日志工具
   */
  constructor(config: DeepSeekConfig, logger: Logger) {
    this.client = createDeepSeekClient({
      url: config.url,
      apiKey: config.apiKey,
    });
    this.config = config;
    this.logger = logger;
  }

  /**
   * 生成好评文案
   * @param goodsInfo - 解析后的商品信息
   * @param targetDir - 目标目录
   * @returns 生成的好评文案数组
   */
  public async generate(goodsInfo: ParsedGoodsInfo, targetDir: string): Promise<string[]> {
    const reviews: string[] = [];
    const reviewCount = this.config.reviewCount;

    this.logger.info(`开始生成好评文案，共 ${reviewCount} 条`);

    for (let i = 0; i < reviewCount; i++) {
      this.logger.info(`生成第 ${i + 1} 条好评文案...`);

      try {
        const review = await this.generateSingleReview(goodsInfo, i);
        reviews.push(review);
        this.logger.info(`第 ${i + 1} 条好评文案生成成功`);
      } catch (error) {
        this.logger.error(`第 ${i + 1} 条好评文案生成失败`, error as Error);
        // 继续生成下一条，不中断流程
      }

      // 每次生成之间添加延迟，避免 API 限流
      if (i < reviewCount - 1) {
        await this.delay(1000);
      }
    }

    if (reviews.length === 0) {
      throw new ReviewGeneratorError("所有好评文案生成失败");
    }

    // 保存到文件
    const reviewFilePath = getReviewFilePath(targetDir);
    const content = formatReviewContent(reviews);
    saveTextFile(reviewFilePath, content);

    this.logger.info(`好评文案已保存到: ${reviewFilePath}`);

    return reviews;
  }

  /**
   * 生成单条好评文案
   * @param goodsInfo - 解析后的商品信息
   * @param index - 当前生成索引
   * @returns 生成的好评文案
   */
  private async generateSingleReview(goodsInfo: ParsedGoodsInfo, _index: number): Promise<string> {
    // 构建提示词
    const messages = this.buildPrompt(goodsInfo);

    // 使用不同的 temperature 增加多样性
    const temperature = 0.7 + Math.random() * 0.3; // 0.7 - 1.0 之间随机

    const content = await this.client.chat(messages, {
      temperature,
      maxTokens: 500,
    });

    return this.cleanReviewContent(content);
  }

  /**
   * 构建提示词
   * @param goodsInfo - 解析后的商品信息
   * @returns 消息列表
   */
  private buildPrompt(goodsInfo: ParsedGoodsInfo): DeepSeekMessage[] {
    const userContent = [
      this.config.systemPrompt,
      "",
      "商品信息：",
      this.formatGoodsInfo(goodsInfo),
      "",
      "请生成80字左右的买家好评文案",
    ].join("\n");

    return [
      { role: "system", content: this.config.systemPrompt },
      { role: "user", content: userContent },
    ];
  }

  /**
   * 格式化商品信息
   * @param goodsInfo - 解析后的商品信息
   * @returns 格式化的商品信息文本
   */
  private formatGoodsInfo(goodsInfo: ParsedGoodsInfo): string {
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
   * 清理好评文案内容
   * @param content - 原始内容
   * @returns 清理后的内容
   */
  private cleanReviewContent(content: string): string {
    // 移除可能的引号
    let cleaned = content.replace(/^["']|["']$/g, "");

    // 移除可能的序号标记
    cleaned = cleaned.replace(/^\d+[\.\、]\s*/gm, "");

    return cleaned.trim();
  }

  /**
   * 延迟函数
   * @param ms - 延迟毫秒数
   */
  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

/**
 * 创建好评文案生成服务的工厂函数
 * @param config - DeepSeek 配置
 * @param logger - 日志工具
 * @returns ReviewGenerator 实例
 */
export function createReviewGenerator(config: DeepSeekConfig, logger: Logger): ReviewGenerator {
  return new ReviewGenerator(config, logger);
}
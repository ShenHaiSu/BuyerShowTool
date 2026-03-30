/**
 * 买家秀图片生成服务
 * 负责调用通义万相 API 生成买家秀模特图
 */

import type { TongyiConfig } from "../config/types";
import type { ParsedGoodsInfo } from "./goodsParser";
import { TongyiClient, createTongyiClient } from "../api/tongyi";
import { Logger } from "../utils/logger";
import { downloadFile, getBuyerShowFilePath } from "../utils/file";

/**
 * 错误类：买家秀图片生成相关错误
 */
export class ImageGeneratorError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ImageGeneratorError";
  }
}

/**
 * 买家秀图片生成服务
 */
export class ImageGenerator {
  private client: TongyiClient;
  private config: TongyiConfig;
  private logger: Logger;

  /**
   * 创建买家秀图片生成服务
   * @param config - 通义万相配置
   * @param logger - 日志工具
   */
  constructor(config: TongyiConfig, logger: Logger) {
    this.client = createTongyiClient({
      url: config.url,
      apiKey: config.apiKey,
    });
    this.config = config;
    this.logger = logger;
  }

  /**
   * 生成买家秀图片
   * @param goodsInfo - 解析后的商品信息
   * @param targetDir - 目标目录
   * @returns 生成图片的文件路径数组
   */
  public async generate(goodsInfo: ParsedGoodsInfo, targetDir: string): Promise<string[]> {
    const imageCount = this.config.imageCount;
    const generatedPaths: string[] = [];

    this.logger.info(`开始生成买家秀图片，共 ${imageCount} 张`);

    for (let i = 0; i < imageCount; i++) {
      this.logger.info(`生成第 ${i + 1} 张买家秀图片...`);

      try {
        // 为每张图片构建不同的提示词（不同的背景）
        const prompt = this.buildPrompt(goodsInfo, i);

        // 生成单张图片
        const imageUrls = await this.client.generateImage(prompt, {
          size: "1024x1024",
          imageCount: 1,
        });

        if (imageUrls.length === 0) {
          throw new ImageGeneratorError("图片生成失败，未返回图片 URL");
        }

        // 下载并保存图片
        const imageUrl = imageUrls[0];
        const filePath = getBuyerShowFilePath(targetDir, i + 1);

        this.logger.info(`下载图片: ${imageUrl}`);
        await downloadFile(imageUrl, filePath);

        generatedPaths.push(filePath);
        this.logger.info(`第 ${i + 1} 张买家秀图片已保存到: ${filePath}`);
      } catch (error) {
        this.logger.error(`第 ${i + 1} 张买家秀图片生成失败`, error as Error);
        // 继续生成下一张，不中断流程
      }

      // 每次生成之间添加延迟，避免 API 限流
      if (i < imageCount - 1) {
        await this.delay(2000);
      }
    }

    if (generatedPaths.length === 0) {
      throw new ImageGeneratorError("所有买家秀图片生成失败");
    }

    this.logger.info(`买家秀图片生成完成，成功生成 ${generatedPaths.length} 张`);

    return generatedPaths;
  }

  /**
   * 构建图片生成提示词
   * @param goodsInfo - 解析后的商品信息
   * @param index - 当前生成索引
   * @returns 完整的提示词
   */
  private buildPrompt(goodsInfo: ParsedGoodsInfo, index: number): string {
    // 交替使用不同的背景
    const backgrounds = ["家居室内客厅环境", "户外草地环境"];
    const background = backgrounds[index % backgrounds.length];

    // 为每次生成添加一些随机性
    const poses = [
      "站立姿势",
      "坐姿",
      "侧面展示",
      "背面展示",
    ];
    const randomPose = poses[Math.floor(Math.random() * poses.length)];

    const promptParts = [
      this.config.systemPrompt,
      "",
      `商品名称：${goodsInfo.name}`,
      `商品品类：${goodsInfo.category}`,
      `适用性别：${goodsInfo.gender}`,
      `年龄：${goodsInfo.ageGroup}`,
      `年份：${goodsInfo.year}`,
      `季节：${goodsInfo.season}`,
      `袖长：${goodsInfo.sleeveLength}`,
      `领型：${goodsInfo.collarType}`,
      `特殊卖点：${goodsInfo.features.join("、")}`,
      "",
      `请生成一张买家秀模特图，背景为${background}，模特姿势为${randomPose}，图片主体为商品本身，不显示模特面部和头部，画面真实自然，符合真实买家秀风格`,
    ];

    return promptParts.join("\n");
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
 * 创建买家秀图片生成服务的工厂函数
 * @param config - 通义万相配置
 * @param logger - 日志工具
 * @returns ImageGenerator 实例
 */
export function createImageGenerator(config: TongyiConfig, logger: Logger): ImageGenerator {
  return new ImageGenerator(config, logger);
}
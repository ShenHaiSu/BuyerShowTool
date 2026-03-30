/**
 * 配置文件加载器
 * 负责加载和解析项目根目录的 config.yaml 和目标路径下的 goods.yaml
 */

import { readFileSync, existsSync } from "fs";
import { resolve, join } from "path";
import YAML from "yaml";
import type { Config, GoodsInfo } from "./types";

/**
 * 错误类：配置文件相关错误
 */
export class ConfigError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ConfigError";
  }
}

/**
 * 加载项目根目录的 config.yaml
 * @param projectRoot - 项目根目录路径
 * @returns 解析后的配置对象
 */
export function loadConfig(projectRoot: string): Config {
  const configPath = resolve(projectRoot, "config.yaml");

  if (!existsSync(configPath)) {
    throw new ConfigError(
      `配置文件不存在: ${configPath}\n请在项目根目录创建 config.yaml 文件`
    );
  }

  try {
    const configContent = readFileSync(configPath, "utf-8");
    const config = YAML.parse(configContent) as Config;

    // 验证配置完整性
    validateConfig(config);

    return config;
  } catch (error) {
    if (error instanceof ConfigError) {
      throw error;
    }
    throw new ConfigError(
      `配置文件解析失败: ${(error as Error).message}`
    );
  }
}

/**
 * 加载目标路径下的 goods.yaml
 * @param targetDir - 目标目录路径
 * @returns 解析后的商品信息对象
 */
export function loadGoodsInfo(targetDir: string): GoodsInfo {
  const goodsPath = join(targetDir, "goods.yaml");

  if (!existsSync(goodsPath)) {
    throw new ConfigError(
      `商品配置文件不存在: ${goodsPath}\n请在目标路径下创建 goods.yaml 文件`
    );
  }

  try {
    const goodsContent = readFileSync(goodsPath, "utf-8");
    const goodsInfo = YAML.parse(goodsContent) as GoodsInfo;

    // 验证商品信息完整性
    validateGoodsInfo(goodsInfo);

    return goodsInfo;
  } catch (error) {
    if (error instanceof ConfigError) {
      throw error;
    }
    throw new ConfigError(
      `商品配置文件解析失败: ${(error as Error).message}`
    );
  }
}

/**
 * 验证配置文件的必要字段
 * @param config - 配置对象
 */
function validateConfig(config: Config): void {
  // 验证 DeepSeek 配置
  if (!config.deepseek) {
    throw new ConfigError("配置文件中缺少 deepseek 配置");
  }
  if (!config.deepseek.url) {
    throw new ConfigError("deepseek.url 不能为空");
  }
  if (!config.deepseek.apiKey) {
    throw new ConfigError("deepseek.apiKey 不能为空");
  }
  if (!config.deepseek.systemPrompt) {
    throw new ConfigError("deepseek.systemPrompt 不能为空");
  }
  if (typeof config.deepseek.reviewCount !== "number" || config.deepseek.reviewCount < 1) {
    throw new ConfigError("deepseek.reviewCount 必须是大于0的数字");
  }

  // 验证通义万相配置
  if (!config.tongyi) {
    throw new ConfigError("配置文件中缺少 tongyi 配置");
  }
  if (!config.tongyi.url) {
    throw new ConfigError("tongyi.url 不能为空");
  }
  if (!config.tongyi.apiKey) {
    throw new ConfigError("tongyi.apiKey 不能为空");
  }
  if (!config.tongyi.systemPrompt) {
    throw new ConfigError("tongyi.systemPrompt 不能为空");
  }
  if (typeof config.tongyi.imageCount !== "number" || config.tongyi.imageCount < 1) {
    throw new ConfigError("tongyi.imageCount 必须是大于0的数字");
  }
}

/**
 * 验证商品信息的必要字段
 * @param goodsInfo - 商品信息对象
 */
function validateGoodsInfo(goodsInfo: GoodsInfo): void {
  if (!goodsInfo.goods) {
    throw new ConfigError("商品配置文件中缺少 goods 字段");
  }

  const { goods } = goodsInfo;

  // 验证商品基本信息
  if (!goods.name) {
    throw new ConfigError("商品名称 (goods.name) 不能为空");
  }
  if (!goods.category) {
    throw new ConfigError("商品品类 (goods.category) 不能为空");
  }
  if (!goods.gender) {
    throw new ConfigError("适用性别 (goods.gender) 不能为空");
  }
  if (!goods.ageGroup) {
    throw new ConfigError("适用年龄 (goods.ageGroup) 不能为空");
  }
  if (!goods.year) {
    throw new ConfigError("年份 (goods.year) 不能为空");
  }
  if (!goods.season) {
    throw new ConfigError("季节 (goods.season) 不能为空");
  }
  if (!goods.sleeveLength) {
    throw new ConfigError("袖长 (goods.sleeveLength) 不能为空");
  }
  if (!goods.collarType) {
    throw new ConfigError("领型 (goods.collarType) 不能为空");
  }
  if (!goods.wearType) {
    throw new ConfigError("穿戴方式 (goods.wearType) 不能为空");
  }
  if (!goods.features || !Array.isArray(goods.features) || goods.features.length === 0) {
    throw new ConfigError("商品卖点 (goods.features) 不能为空");
  }

  // 验证图片列表
  if (!goodsInfo.images || !Array.isArray(goodsInfo.images) || goodsInfo.images.length === 0) {
    throw new ConfigError("商品图片列表 (images) 不能为空");
  }
}
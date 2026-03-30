/**
 * BuyerShowTool 入口文件
 * 解析命令行参数并调度任务
 */

import { resolve } from "path";
import { loadConfig, loadGoodsInfo, ConfigError } from "./config/loader";
import { createLogger } from "./utils/logger";
import { createGoodsParser } from "./services/goodsParser";
import { createReviewGenerator } from "./services/reviewGenerator";
import { createImageGenerator } from "./services/imageGenerator";

/**
 * 主函数
 */
async function main(): Promise<void> {
  // 解析命令行参数
  const targetDir = parseCommandLineArgs();

  // 获取项目根目录（当前工作目录）
  const projectRoot = process.cwd();

  // 创建日志工具
  const logger = createLogger(targetDir);

  logger.info("========================================");
  logger.info("BuyerShowTool 开始执行");
  logger.info(`目标路径: ${targetDir}`);
  logger.info("========================================");

  try {
    // 1. 加载配置文件
    logger.info("加载配置文件...");
    const config = loadConfig(projectRoot);
    logger.info("配置文件加载成功");

    // 2. 加载商品信息
    logger.info("加载商品信息...");
    const goodsInfo = loadGoodsInfo(targetDir);
    logger.info("商品信息加载成功");

    // 3. 解析商品信息
    logger.info("解析商品信息...");
    const parser = createGoodsParser();
    const parsedGoodsInfo = parser.parse(goodsInfo);
    logger.info(`商品名称: ${parsedGoodsInfo.name}`);

    // 4. 生成好评文案
    logger.info("开始生成好评文案...");
    const reviewGenerator = createReviewGenerator(config.deepseek, logger);
    const reviews = await reviewGenerator.generate(parsedGoodsInfo, targetDir);
    logger.info(`好评文案生成完成，共 ${reviews.length} 条`);

    // 5. 生成买家秀图片
    logger.info("开始生成买家秀图片...");
    const imageGenerator = createImageGenerator(config.tongyi, logger);
    const imagePaths = await imageGenerator.generate(parsedGoodsInfo, targetDir);
    logger.info(`买家秀图片生成完成，共 ${imagePaths.length} 张`);

    // 完成
    logger.info("========================================");
    logger.info("BuyerShowTool 执行完成");
    logger.info("========================================");
  } catch (error) {
    if (error instanceof ConfigError) {
      logger.error(`配置错误: ${error.message}`);
    } else {
      logger.error("执行失败", error as Error);
    }
    process.exit(1);
  }
}

/**
 * 解析命令行参数
 * @returns 目标目录路径
 */
function parseCommandLineArgs(): string {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.error("用法: bun run src/index.ts <目标路径>");
    console.error("示例: bun run src/index.ts C:\\example\\dir");
    process.exit(1);
  }

  const targetDir = resolve(args[0]);

  return targetDir;
}

// 执行主函数
main().catch((error) => {
  console.error("未捕获的错误:", error);
  process.exit(1);
});
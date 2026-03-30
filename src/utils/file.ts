/**
 * 文件操作工具
 * 提供文件读写、下载等常用操作
 */

import { writeFileSync, existsSync, readFileSync } from "fs";
import { join } from "path";

/**
 * 错误类：文件操作相关错误
 */
export class FileError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "FileError";
  }
}

/**
 * 保存文本内容到文件
 * @param filePath - 文件完整路径
 * @param content - 文件内容
 */
export function saveTextFile(filePath: string, content: string): void {
  try {
    writeFileSync(filePath, content, "utf-8");
  } catch (error) {
    throw new FileError(`写入文件失败: ${filePath}, 错误: ${(error as Error).message}`);
  }
}

/**
 * 保存二进制内容到文件
 * @param filePath - 文件完整路径
 * @param content - 二进制内容
 */
export function saveBinaryFile(filePath: string, content: Buffer): void {
  try {
    writeFileSync(filePath, content);
  } catch (error) {
    throw new FileError(`写入文件失败: ${filePath}, 错误: ${(error as Error).message}`);
  }
}

/**
 * 读取文件内容
 * @param filePath - 文件完整路径
 * @returns 文件内容
 */
export function readTextFile(filePath: string): string {
  if (!existsSync(filePath)) {
    throw new FileError(`文件不存在: ${filePath}`);
  }

  try {
    return readFileSync(filePath, "utf-8");
  } catch (error) {
    throw new FileError(`读取文件失败: ${filePath}, 错误: ${(error as Error).message}`);
  }
}

/**
 * 检查文件是否存在
 * @param filePath - 文件完整路径
 * @returns 是否存在
 */
export function fileExists(filePath: string): boolean {
  return existsSync(filePath);
}

/**
 * 从 URL 下载文件
 * @param url - 文件 URL
 * @param filePath - 保存路径
 */
export async function downloadFile(url: string, filePath: string): Promise<void> {
  try {
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const arrayBuffer = await response.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);

    saveBinaryFile(filePath, buffer);
  } catch (error) {
    throw new FileError(`下载文件失败: ${url}, 错误: ${(error as Error).message}`);
  }
}

/**
 * 生成买家秀图片文件名
 * @param index - 图片序号
 * @returns 文件名
 */
export function generateBuyerShowFileName(index: number): string {
  return `buyer_show_${index}.jpg`;
}

/**
 * 获取买家秀图片的完整路径
 * @param targetDir - 目标目录
 * @param index - 图片序号
 * @returns 完整文件路径
 */
export function getBuyerShowFilePath(targetDir: string, index: number): string {
  return join(targetDir, generateBuyerShowFileName(index));
}

/**
 * 获取好评文案文件的完整路径
 * @param targetDir - 目标目录
 * @returns 完整文件路径
 */
export function getReviewFilePath(targetDir: string): string {
  return join(targetDir, "review.txt");
}

/**
 * 格式化好评文案内容
 * @param reviews - 好评文案数组
 * @returns 格式化后的文本内容
 */
export function formatReviewContent(reviews: string[]): string {
  return reviews
    .map((review, index) => `=== 第${index + 1}条 ===\n${review}`)
    .join("\n\n");
}
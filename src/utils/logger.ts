/**
 * 日志工具
 * 提供统一的日志输出和错误日志记录功能
 */

import { appendFileSync, existsSync, mkdirSync } from "fs";
import { dirname, join } from "path";

/**
 * 日志级别
 */
export type LogLevel = "info" | "warn" | "error" | "debug";

/**
 * 日志工具类
 */
export class Logger {
  private errorLogPath: string;

  /**
   * 创建日志工具实例
   * @param targetDir - 目标目录路径，用于存储错误日志
   */
  constructor(targetDir: string) {
    this.errorLogPath = join(targetDir, "error.log");
  }

  /**
   * 输出信息日志
   * @param message - 日志消息
   */
  public info(message: string): void {
    this.log("info", message);
  }

  /**
   * 输出警告日志
   * @param message - 日志消息
   */
  public warn(message: string): void {
    this.log("warn", message);
  }

  /**
   * 输出错误日志
   * @param message - 日志消息
   * @param error - 错误对象（可选）
   */
  public error(message: string, error?: Error): void {
    const fullMessage = error ? `${message}: ${error.message}` : message;
    this.log("error", fullMessage);
    this.writeErrorLog(fullMessage, error);
  }

  /**
   * 输出调试日志
   * @param message - 日志消息
   */
  public debug(message: string): void {
    this.log("debug", message);
  }

  /**
   * 内部日志输出方法
   * @param level - 日志级别
   * @param message - 日志消息
   */
  private log(level: LogLevel, message: string): void {
    const timestamp = this.getTimestamp();
    const prefix = this.getPrefix(level);
    console.log(`[${timestamp}] ${prefix} ${message}`);
  }

  /**
   * 获取时间戳
   * @returns 格式化的时间戳字符串
   */
  private getTimestamp(): string {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, "0");
    const day = String(now.getDate()).padStart(2, "0");
    const hours = String(now.getHours()).padStart(2, "0");
    const minutes = String(now.getMinutes()).padStart(2, "0");
    const seconds = String(now.getSeconds()).padStart(2, "0");
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  }

  /**
   * 获取日志级别前缀
   * @param level - 日志级别
   * @returns 带颜色的前缀字符串
   */
  private getPrefix(level: LogLevel): string {
    const prefixes: Record<LogLevel, string> = {
      info: "\x1b[32mINFO\x1b[0m",
      warn: "\x1b[33mWARN\x1b[0m",
      error: "\x1b[31mERROR\x1b[0m",
      debug: "\x1b[36mDEBUG\x1b[0m",
    };
    return prefixes[level];
  }

  /**
   * 写入错误日志到文件
   * @param message - 错误消息
   * @param error - 错误对象（可选）
   */
  private writeErrorLog(message: string, error?: Error): void {
    try {
      const timestamp = this.getTimestamp();
      let logContent = `[${timestamp}] ${message}`;

      if (error?.stack) {
        logContent += `\n${error.stack}`;
      }

      logContent += "\n\n";

      // 确保目标目录存在
      const dir = dirname(this.errorLogPath);
      if (!existsSync(dir)) {
        mkdirSync(dir, { recursive: true });
      }

      appendFileSync(this.errorLogPath, logContent, "utf-8");
    } catch (writeError) {
      console.error("写入错误日志失败:", (writeError as Error).message);
    }
  }
}

/**
 * 创建日志工具实例的工厂函数
 * @param targetDir - 目标目录路径
 * @returns Logger 实例
 */
export function createLogger(targetDir: string): Logger {
  return new Logger(targetDir);
}
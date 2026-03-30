/**
 * DeepSeek API 封装
 * 提供 DeepSeek Chat API 的调用功能
 */

import type { DeepSeekRequest, DeepSeekResponse, DeepSeekMessage } from "../config/types";

/**
 * 错误类：DeepSeek API 相关错误
 */
export class DeepSeekError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "DeepSeekError";
  }
}

/**
 * DeepSeek API 客户端
 */
export class DeepSeekClient {
  private url: string;
  private apiKey: string;
  private model: string;
  private maxRetries: number;
  private retryDelay: number;

  /**
   * 创建 DeepSeek API 客户端
   * @param config - API 配置
   */
  constructor(config: { url: string; apiKey: string }) {
    this.url = config.url;
    this.apiKey = config.apiKey;
    this.model = "deepseek-chat";
    this.maxRetries = 3;
    this.retryDelay = 1000;
  }

  /**
   * 发送聊天请求
   * @param messages - 消息列表
   * @param options - 可选参数
   * @returns 生成的文本内容
   */
  public async chat(
    messages: DeepSeekMessage[],
    options?: { temperature?: number; maxTokens?: number }
  ): Promise<string> {
    const request: DeepSeekRequest = {
      model: this.model,
      messages,
      temperature: options?.temperature ?? 0.8,
      max_tokens: options?.maxTokens ?? 500,
    };

    let lastError: Error | null = null;

    for (let attempt = 0; attempt < this.maxRetries; attempt++) {
      try {
        const response = await this.sendRequest(request);
        return this.extractContent(response);
      } catch (error) {
        lastError = error as Error;

        // 如果是客户端错误（4xx），不重试
        if (this.isClientError(error)) {
          throw error;
        }

        // 否则等待后重试
        if (attempt < this.maxRetries - 1) {
          await this.delay(this.retryDelay * (attempt + 1));
        }
      }
    }

    throw new DeepSeekError(
      `DeepSeek API 调用失败，已重试 ${this.maxRetries} 次: ${lastError?.message}`
    );
  }

  /**
   * 发送 API 请求
   * @param request - 请求体
   * @returns API 响应
   */
  private async sendRequest(request: DeepSeekRequest): Promise<DeepSeekResponse> {
    const response = await fetch(this.url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorBody = await response.text();
      throw new DeepSeekError(
        `API 请求失败 (HTTP ${response.status}): ${errorBody}`
      );
    }

    const data = await response.json() as DeepSeekResponse;
    return data;
  }

  /**
   * 从响应中提取内容
   * @param response - API 响应
   * @returns 生成的文本内容
   */
  private extractContent(response: DeepSeekResponse): string {
    if (!response.choices || response.choices.length === 0) {
      throw new DeepSeekError("API 响应中没有有效的选择");
    }

    const content = response.choices[0]?.message?.content;
    if (!content) {
      throw new DeepSeekError("API 响应中没有内容");
    }

    return content.trim();
  }

  /**
   * 判断是否为客户端错误
   * @param error - 错误对象
   * @returns 是否为客户端错误
   */
  private isClientError(error: unknown): boolean {
    if (error instanceof DeepSeekError) {
      const message = error.message;
      // 4xx 错误码表示客户端错误
      return /HTTP [4]\d{2}/.test(message);
    }
    return false;
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
 * 创建 DeepSeek API 客户端的工厂函数
 * @param config - API 配置
 * @returns DeepSeekClient 实例
 */
export function createDeepSeekClient(config: { url: string; apiKey: string }): DeepSeekClient {
  return new DeepSeekClient(config);
}
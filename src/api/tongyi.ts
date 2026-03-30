/**
 * 通义万相 API 封装
 * 提供通义万相文生图 API 的调用功能
 */

import type { TongyiRequest, TongyiResponse, TongyiTaskStatusResponse } from "../config/types";

/**
 * 错误类：通义万相 API 相关错误
 */
export class TongyiError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "TongyiError";
  }
}

/**
 * 通义万相 API 客户端
 */
export class TongyiClient {
  private url: string;
  private apiKey: string;
  private model: string;
  private maxRetries: number;
  private retryDelay: number;
  private pollInterval: number;
  private maxPollAttempts: number;

  /**
   * 创建通义万相 API 客户端
   * @param config - API 配置
   */
  constructor(config: { url: string; apiKey: string }) {
    this.url = config.url;
    this.apiKey = config.apiKey;
    this.model = "wanx-v1";
    this.maxRetries = 3;
    this.retryDelay = 1000;
    this.pollInterval = 2000;
    this.maxPollAttempts = 60;
  }

  /**
   * 生成图片
   * @param prompt - 图片生成提示词
   * @param options - 可选参数
   * @returns 生成图片的 URL 列表
   */
  public async generateImage(
    prompt: string,
    options?: { size?: string; imageCount?: number }
  ): Promise<string[]> {
    const request: TongyiRequest = {
      model: this.model,
      input: { prompt },
      parameters: {
        size: options?.size ?? "1024x1024",
        n: options?.imageCount ?? 1,
      },
    };

    // 提交生成任务
    const taskId = await this.submitTask(request);

    // 轮询任务状态
    const imageUrls = await this.pollTaskStatus(taskId);

    return imageUrls;
  }

  /**
   * 提交图片生成任务
   * @param request - 请求体
   * @returns 任务 ID
   */
  private async submitTask(request: TongyiRequest): Promise<string> {
    let lastError: Error | null = null;

    for (let attempt = 0; attempt < this.maxRetries; attempt++) {
      try {
        const response = await this.sendRequest(request);
        return this.extractTaskId(response);
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

    throw new TongyiError(
      `通义万相 API 调用失败，已重试 ${this.maxRetries} 次: ${lastError?.message}`
    );
  }

  /**
   * 轮询任务状态
   * @param taskId - 任务 ID
   * @returns 生成图片的 URL 列表
   */
  private async pollTaskStatus(taskId: string): Promise<string[]> {
    const statusUrl = `${this.url.replace("/generation", "")}/tasks/${taskId}`;

    for (let attempt = 0; attempt < this.maxPollAttempts; attempt++) {
      const response = await this.fetchTaskStatus(statusUrl);
      const status = response.output.task_status;

      if (status === "SUCCEEDED") {
        if (!response.output.results || response.output.results.length === 0) {
          throw new TongyiError("图片生成成功但没有返回结果");
        }
        return response.output.results.map((result) => result.url);
      }

      if (status === "FAILED") {
        const errorMessage = response.output.message || "图片生成失败";
        throw new TongyiError(`图片生成任务失败: ${errorMessage}`);
      }

      // PENDING 或 RUNNING，继续轮询
      await this.delay(this.pollInterval);
    }

    throw new TongyiError(
      `图片生成任务超时，已等待 ${(this.pollInterval * this.maxPollAttempts) / 1000} 秒`
    );
  }

  /**
   * 获取任务状态
   * @param statusUrl - 状态查询 URL
   * @returns 任务状态响应
   */
  private async fetchTaskStatus(statusUrl: string): Promise<TongyiTaskStatusResponse> {
    const response = await fetch(statusUrl, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.apiKey}`,
      },
    });

    if (!response.ok) {
      const errorBody = await response.text();
      throw new TongyiError(
        `任务状态查询失败 (HTTP ${response.status}): ${errorBody}`
      );
    }

    return await response.json() as TongyiTaskStatusResponse;
  }

  /**
   * 发送 API 请求
   * @param request - 请求体
   * @returns API 响应
   */
  private async sendRequest(request: TongyiRequest): Promise<TongyiResponse> {
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
      throw new TongyiError(
        `API 请求失败 (HTTP ${response.status}): ${errorBody}`
      );
    }

    return await response.json() as TongyiResponse;
  }

  /**
   * 从响应中提取任务 ID
   * @param response - API 响应
   * @returns 任务 ID
   */
  private extractTaskId(response: TongyiResponse): string {
    if (!response.output?.task_id) {
      throw new TongyiError("API 响应中没有有效的任务 ID");
    }
    return response.output.task_id;
  }

  /**
   * 判断是否为客户端错误
   * @param error - 错误对象
   * @returns 是否为客户端错误
   */
  private isClientError(error: unknown): boolean {
    if (error instanceof TongyiError) {
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
 * 创建通义万相 API 客户端的工厂函数
 * @param config - API 配置
 * @returns TongyiClient 实例
 */
export function createTongyiClient(config: { url: string; apiKey: string }): TongyiClient {
  return new TongyiClient(config);
}
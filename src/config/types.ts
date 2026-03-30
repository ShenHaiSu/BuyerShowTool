/**
 * 项目配置类型定义
 */

/**
 * DeepSeek API 配置
 */
export interface DeepSeekConfig {
  url: string;
  apiKey: string;
  systemPrompt: string;
  reviewCount: number;
}

/**
 * 通义万相 API 配置
 */
export interface TongyiConfig {
  url: string;
  apiKey: string;
  systemPrompt: string;
  imageCount: number;
}

/**
 * 项目根目录配置文件
 */
export interface Config {
  deepseek: DeepSeekConfig;
  tongyi: TongyiConfig;
}

/**
 * 商品基本信息
 */
export interface GoodsBasicInfo {
  name: string;
  category: string;
  gender: string;
  ageGroup: string;
  year: string;
  season: string;
  pantsLength?: string;
  sleeveLength: string;
  collarType: string;
  wearType: string;
  features: string[];
}

/**
 * 商品信息
 */
export interface GoodsInfo {
  goods: GoodsBasicInfo;
  images: string[];
}

/**
 * DeepSeek API 请求消息
 */
export interface DeepSeekMessage {
  role: "system" | "user";
  content: string;
}

/**
 * DeepSeek API 请求体
 */
export interface DeepSeekRequest {
  model: string;
  messages: DeepSeekMessage[];
  temperature?: number;
  max_tokens?: number;
}

/**
 * DeepSeek API 响应体
 */
export interface DeepSeekResponse {
  choices: Array<{
    message: {
      content: string;
    };
  }>;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

/**
 * 通义万相 API 请求体
 */
export interface TongyiRequest {
  model: string;
  input: {
    prompt: string;
  };
  parameters: {
    size?: string;
    n?: number;
  };
}

/**
 * 通义万相 API 响应体
 */
export interface TongyiResponse {
  output: {
    task_id: string;
  };
  request_id: string;
}

/**
 * 通义万相任务状态查询响应
 */
export interface TongyiTaskStatusResponse {
  output: {
    task_status: "PENDING" | "RUNNING" | "SUCCEEDED" | "FAILED";
    results?: Array<{
      url: string;
    }>;
    message?: string;
  };
  request_id: string;
}
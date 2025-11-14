/**
 * @purpose: LLM Provider 相关的 TypeScript 类型定义
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */

export type ProviderType = 'qwen' | 'gemini' | 'ollama';

export interface ModelConfig {
  model_name: string;
  display_name: string;
  max_tokens: number;
  temperature: number;
  enabled: boolean;
  priority: number;
  description?: string;
}

export interface LLMProvider {
  provider_type: ProviderType;
  models: ModelConfig[];
  status: 'active' | 'inactive' | 'error';
}

export interface ModelConfigUpdate {
  max_tokens?: number;
  temperature?: number;
  enabled?: boolean;
  priority?: number;
  description?: string;
}

export interface ProviderTestResponse {
  success: boolean;
  message: string;
  response_time_ms?: number;
}


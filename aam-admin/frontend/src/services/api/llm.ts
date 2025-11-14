/**
 * @purpose: LLM Provider API 服务
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import apiClient from './client';
import { API_ENDPOINTS } from '@/config/api';
import type {
  LLMProvider,
  ModelConfig,
  ModelConfigUpdate,
  ProviderTestResponse,
} from '@/types/llm';

export const llmApi = {
  /**
   * 获取所有 Provider 列表
   */
  getProviders: async (): Promise<LLMProvider[]> => {
    const response = await apiClient.get<{ providers: LLMProvider[] }>(
      API_ENDPOINTS.llm.providers
    );
    return response.data.providers;
  },

  /**
   * 获取指定 Provider 的配置
   */
  getProvider: async (providerType: string): Promise<LLMProvider> => {
    const response = await apiClient.get<LLMProvider>(
      `/llm-providers/${providerType}`
    );
    return response.data;
  },

  /**
   * 获取指定 Provider 的模型列表
   */
  getModels: async (providerType: string): Promise<ModelConfig[]> => {
    const response = await apiClient.get<ModelConfig[]>(
      `/llm-providers/${providerType}/models`
    );
    return response.data;
  },

  /**
   * 更新模型配置
   */
  updateModel: async (
    providerType: string,
    modelName: string,
    updates: ModelConfigUpdate
  ): Promise<ModelConfig> => {
    const response = await apiClient.put<ModelConfig>(
      `/llm-providers/${providerType}/models/${modelName}`,
      updates
    );
    return response.data;
  },

  /**
   * 启用/禁用模型
   */
  toggleModel: async (
    providerType: string,
    modelName: string,
    enabled: boolean
  ): Promise<ModelConfig> => {
    const response = await apiClient.post<ModelConfig>(
      `/llm-providers/${providerType}/models/${modelName}/toggle`,
      null,
      {
        params: { enabled },
      }
    );
    return response.data;
  },

  /**
   * 测试 Provider 连接
   */
  testProvider: async (providerType: string): Promise<ProviderTestResponse> => {
    const response = await apiClient.post<ProviderTestResponse>(
      `/llm-providers/${providerType}/test`
    );
    return response.data;
  },
};


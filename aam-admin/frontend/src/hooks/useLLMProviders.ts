/**
 * @purpose: LLM Provider 数据管理 Hook
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import { useState, useEffect, useCallback } from 'react';
import { llmApi } from '@/services/api/llm';
import type { LLMProvider, ModelConfig, ModelConfigUpdate } from '@/types/llm';

export const useLLMProviders = () => {
  const [providers, setProviders] = useState<LLMProvider[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchProviders = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await llmApi.getProviders();
      setProviders(data);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProviders();
  }, [fetchProviders]);

  return { providers, loading, error, refresh: fetchProviders };
};

export const useLLMProvider = (providerType: string) => {
  const [provider, setProvider] = useState<LLMProvider | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchProvider = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await llmApi.getProvider(providerType);
      setProvider(data);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [providerType]);

  useEffect(() => {
    if (providerType) {
      fetchProvider();
    }
  }, [providerType, fetchProvider]);

  const updateModel = useCallback(
    async (modelName: string, updates: ModelConfigUpdate) => {
      try {
        const updatedModel = await llmApi.updateModel(providerType, modelName, updates);
        // 更新本地状态
        if (provider) {
          setProvider({
            ...provider,
            models: provider.models.map((m) =>
              m.model_name === modelName ? updatedModel : m
            ),
          });
        }
        return updatedModel;
      } catch (err) {
        setError(err as Error);
        throw err;
      }
    },
    [providerType, provider]
  );

  const toggleModel = useCallback(
    async (modelName: string, enabled: boolean) => {
      try {
        const updatedModel = await llmApi.toggleModel(providerType, modelName, enabled);
        // 更新本地状态
        if (provider) {
          setProvider({
            ...provider,
            models: provider.models.map((m) =>
              m.model_name === modelName ? updatedModel : m
            ),
            status: updatedModel.enabled ? 'active' : 'inactive',
          });
        }
        return updatedModel;
      } catch (err) {
        setError(err as Error);
        throw err;
      }
    },
    [providerType, provider]
  );

  const testProvider = useCallback(async () => {
    try {
      return await llmApi.testProvider(providerType);
    } catch (err) {
      setError(err as Error);
      throw err;
    }
  }, [providerType]);

  return {
    provider,
    loading,
    error,
    refresh: fetchProvider,
    updateModel,
    toggleModel,
    testProvider,
  };
};


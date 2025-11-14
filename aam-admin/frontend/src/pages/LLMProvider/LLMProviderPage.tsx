/**
 * @purpose: LLM Provider 管理页面
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React, { useState } from 'react';
import { Box, Typography, Grid, CircularProgress, Alert } from '@mui/joy';
import { useLLMProviders, useLLMProvider } from '@/hooks/useLLMProviders';
import { ProviderList } from '@/components/llm/ProviderList';
import { ProviderConfigForm } from '@/components/llm/ProviderConfigForm';
import type { ProviderType, ModelConfigUpdate } from '@/types/llm';

export const LLMProviderPage: React.FC = () => {
  const [selectedProviderType, setSelectedProviderType] = useState<ProviderType | undefined>();
  const { providers, loading, error, refresh } = useLLMProviders();
  const {
    provider,
    loading: providerLoading,
    error: providerError,
    updateModel,
    toggleModel,
    testProvider,
  } = useLLMProvider(selectedProviderType || '');

  const handleSelectProvider = (providerType: ProviderType) => {
    setSelectedProviderType(providerType);
  };

  const handleUpdateModel = async (modelName: string, updates: ModelConfigUpdate) => {
    if (!selectedProviderType) return;
    await updateModel(modelName, updates);
    // 刷新 Provider 列表
    await refresh();
  };

  const handleToggleModel = async (modelName: string, enabled: boolean) => {
    if (!selectedProviderType) return;
    await toggleModel(modelName, enabled);
    // 刷新 Provider 列表
    await refresh();
  };

  const handleTestProvider = async () => {
    if (!selectedProviderType) return;
    await testProvider();
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography level="h2" sx={{ mb: 3 }}>
        LLM Provider 管理
      </Typography>

      {/* 错误提示 */}
      {(error || providerError) && (
        <Alert color="danger" sx={{ mb: 2 }}>
          {error?.message || providerError?.message || '数据加载失败，请刷新页面重试'}
        </Alert>
      )}

      {/* 主内容区域 */}
      <Grid container spacing={2} sx={{ height: 'calc(100vh - 200px)' }}>
        {/* 左侧：Provider 列表 (30%) */}
        <Grid xs={12} md={3.6}>
          <Box sx={{ height: '100%' }}>
            <ProviderList
              providers={providers}
              selectedProvider={selectedProviderType}
              onSelectProvider={handleSelectProvider}
              loading={loading}
            />
          </Box>
        </Grid>

        {/* 右侧：配置详情 (70%) */}
        <Grid xs={12} md={8.4}>
          <Box sx={{ height: '100%', overflow: 'auto' }}>
            {providerLoading ? (
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  height: '100%',
                }}
              >
                <CircularProgress />
              </Box>
            ) : (
              <ProviderConfigForm
                provider={provider || null}
                loading={providerLoading}
                onUpdateModel={handleUpdateModel}
                onToggleModel={handleToggleModel}
                onTestProvider={handleTestProvider}
              />
            )}
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default LLMProviderPage;


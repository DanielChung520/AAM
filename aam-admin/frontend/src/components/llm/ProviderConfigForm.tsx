/**
 * @purpose: LLM Provider 配置表单组件（右侧面板）
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  Sheet,
  Table,
  Button,
  Input,
  Switch,
  FormControl,
  FormLabel,
  Chip,
  Alert,
  CircularProgress,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import type { LLMProvider, ModelConfig, ModelConfigUpdate } from '@/types/llm';

export interface ProviderConfigFormProps {
  provider: LLMProvider | null;
  loading?: boolean;
  onUpdateModel: (modelName: string, updates: ModelConfigUpdate) => Promise<void>;
  onToggleModel: (modelName: string, enabled: boolean) => Promise<void>;
  onTestProvider: () => Promise<void>;
}

export const ProviderConfigForm: React.FC<ProviderConfigFormProps> = ({
  provider,
  loading = false,
  onUpdateModel,
  onToggleModel,
  onTestProvider,
}) => {
  const { mode } = useColorScheme();
  const [selectedModel, setSelectedModel] = useState<ModelConfig | null>(null);
  const [editingModel, setEditingModel] = useState<ModelConfigUpdate>({});
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  if (!provider) {
    return (
      <Box
        sx={{
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          bgcolor: 'background.surface',
          borderRadius: 'sm',
        }}
      >
        <Typography level="body-lg" sx={{ color: 'text.secondary' }}>
          请选择一个 Provider
        </Typography>
      </Box>
    );
  }

  const handleModelSelect = (model: ModelConfig) => {
    setSelectedModel(model);
    setEditingModel({
      max_tokens: model.max_tokens,
      temperature: model.temperature,
      priority: model.priority,
      description: model.description,
    });
    setError(null);
    setSuccess(null);
  };

  const handleSave = async () => {
    if (!selectedModel) return;

    try {
      setSaving(true);
      setError(null);
      await onUpdateModel(selectedModel.model_name, editingModel);
      setSuccess('模型配置已保存');
      // 重新选择模型以刷新数据
      const updatedModel = provider.models.find(
        (m) => m.model_name === selectedModel.model_name
      );
      if (updatedModel) {
        setSelectedModel(updatedModel);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '保存失败');
    } finally {
      setSaving(false);
    }
  };

  const handleToggle = async (modelName: string, enabled: boolean) => {
    try {
      await onToggleModel(modelName, enabled);
      setSuccess(`模型已${enabled ? '启用' : '禁用'}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : '操作失败');
    }
  };

  const handleTest = async () => {
    try {
      setTesting(true);
      setError(null);
      await onTestProvider();
      setSuccess('Provider 连接测试成功');
    } catch (err) {
      setError(err instanceof Error ? err.message : '测试失败');
    } finally {
      setTesting(false);
    }
  };

  return (
    <Box
      sx={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        gap: 2,
        overflow: 'auto',
      }}
    >
      {/* Provider 基本信息 */}
      <Card>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Box>
            <Typography level="title-lg">
              {provider.provider_type.toUpperCase()} Provider
            </Typography>
            <Typography level="body-sm" sx={{ color: 'text.secondary', mt: 0.5 }}>
              状态: {provider.status === 'active' ? '活跃' : provider.status === 'inactive' ? '未激活' : '错误'}
            </Typography>
          </Box>
          <Button
            variant="outlined"
            color="primary"
            onClick={handleTest}
            loading={testing}
          >
            测试连接
          </Button>
        </Box>
      </Card>

      {/* 消息提示 */}
      {error && (
        <Alert color="danger" onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert color="success" onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* 模型列表表格 */}
      <Card>
        <Typography level="title-md" sx={{ mb: 2 }}>
          模型列表
        </Typography>
        <Sheet variant="outlined" sx={{ borderRadius: 'sm', overflow: 'auto' }}>
          <Table>
            <thead>
              <tr>
                <th>模型名称</th>
                <th>显示名称</th>
                <th>状态</th>
                <th>优先级</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {provider.models.map((model) => (
                <tr
                  key={model.model_name}
                  style={{
                    backgroundColor:
                      selectedModel?.model_name === model.model_name
                        ? 'var(--joy-palette-primary-50)'
                        : 'transparent',
                    cursor: 'pointer',
                  }}
                  onClick={() => handleModelSelect(model)}
                >
                  <td>
                    <Typography level="body-sm">{model.model_name}</Typography>
                  </td>
                  <td>
                    <Typography level="body-sm">{model.display_name}</Typography>
                  </td>
                  <td>
                    <Chip
                      color={model.enabled ? 'success' : 'neutral'}
                      size="sm"
                      variant="soft"
                    >
                      {model.enabled ? '启用' : '禁用'}
                    </Chip>
                  </td>
                  <td>
                    <Typography level="body-sm">{model.priority}</Typography>
                  </td>
                  <td>
                    <Switch
                      checked={model.enabled}
                      onChange={(e) => handleToggle(model.model_name, e.target.checked)}
                      size="sm"
                      onClick={(e) => e.stopPropagation()}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Sheet>
      </Card>

      {/* 模型配置表单 */}
      {selectedModel && (
        <Card>
          <Typography level="title-md" sx={{ mb: 2 }}>
            模型配置: {selectedModel.display_name}
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <FormControl>
              <FormLabel>最大 Token 数</FormLabel>
              <Input
                type="number"
                value={editingModel.max_tokens ?? selectedModel.max_tokens}
                onChange={(e) =>
                  setEditingModel({
                    ...editingModel,
                    max_tokens: parseInt(e.target.value) || undefined,
                  })
                }
              />
            </FormControl>
            <FormControl>
              <FormLabel>温度参数 (0-1)</FormLabel>
              <Input
                type="number"
                step="0.1"
                min="0"
                max="1"
                value={editingModel.temperature ?? selectedModel.temperature}
                onChange={(e) =>
                  setEditingModel({
                    ...editingModel,
                    temperature: parseFloat(e.target.value) || undefined,
                  })
                }
              />
            </FormControl>
            <FormControl>
              <FormLabel>优先级（数字越小优先级越高）</FormLabel>
              <Input
                type="number"
                value={editingModel.priority ?? selectedModel.priority}
                onChange={(e) =>
                  setEditingModel({
                    ...editingModel,
                    priority: parseInt(e.target.value) || undefined,
                  })
                }
              />
            </FormControl>
            <FormControl>
              <FormLabel>描述</FormLabel>
              <Input
                value={editingModel.description ?? selectedModel.description ?? ''}
                onChange={(e) =>
                  setEditingModel({
                    ...editingModel,
                    description: e.target.value || undefined,
                  })
                }
                multiline
                minRows={2}
              />
            </FormControl>
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
              <Button variant="outlined" onClick={() => setSelectedModel(null)}>
                取消
              </Button>
              <Button variant="solid" onClick={handleSave} loading={saving}>
                保存
              </Button>
            </Box>
          </Box>
        </Card>
      )}
    </Box>
  );
};

export default ProviderConfigForm;


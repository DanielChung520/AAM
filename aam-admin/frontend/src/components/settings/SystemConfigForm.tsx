/**
 * @purpose: 系统配置表单组件
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Sheet,
  Typography,
  FormControl,
  FormLabel,
  Input,
  Select,
  Option,
  Button,
  Alert,
  Stack,
  Chip,
  Divider,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import SaveIcon from '@mui/icons-material/Save';
import type { SystemSettings, SystemSettingsUpdate } from '@/types/settings';

export interface SystemConfigFormProps {
  settings: SystemSettings | null;
  loading?: boolean;
  onSave: (updates: SystemSettingsUpdate) => Promise<void>;
}

export const SystemConfigForm: React.FC<SystemConfigFormProps> = ({
  settings,
  loading = false,
  onSave,
}) => {
  const { mode } = useColorScheme();
  const [formData, setFormData] = useState<SystemSettingsUpdate>({});
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (settings) {
      setFormData({
        app_name: settings.app_name,
        app_version: settings.app_version,
        debug: settings.debug,
        log_level: settings.log_level as 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR',
        api_host: settings.api_host,
        api_port: settings.api_port,
        api_prefix: settings.api_prefix,
        cors_origins: settings.cors_origins,
      });
    }
  }, [settings]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    try {
      await onSave(formData);
      setSuccess('系统配置已更新（需要重启应用才能生效）');
    } catch (err) {
      setError(err instanceof Error ? err.message : '更新系统配置失败');
    }
  };

  if (!settings) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography level="body-sm" color="neutral">
          加载中...
        </Typography>
      </Box>
    );
  }

  return (
    <Sheet variant="outlined" sx={{ p: 3, borderRadius: 'sm' }}>
      <Typography level="title-lg" sx={{ mb: 2 }}>
        系统配置
      </Typography>

      {success && (
        <Alert color="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      {error && (
        <Alert color="danger" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Box component="form" onSubmit={handleSubmit}>
        <Stack spacing={3}>
          {/* 应用配置 */}
          <Box>
            <Typography level="title-md" sx={{ mb: 2 }}>
              应用配置
            </Typography>
            <Stack spacing={2}>
              <FormControl>
                <FormLabel>应用名称</FormLabel>
                <Input
                  value={formData.app_name || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, app_name: e.target.value })
                  }
                  placeholder="应用名称"
                />
              </FormControl>

              <FormControl>
                <FormLabel>应用版本</FormLabel>
                <Input
                  value={formData.app_version || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, app_version: e.target.value })
                  }
                  placeholder="应用版本"
                />
              </FormControl>

              <FormControl>
                <FormLabel>调试模式</FormLabel>
                <Select
                  value={formData.debug !== undefined ? String(formData.debug) : ''}
                  onChange={(_, value) =>
                    setFormData({ ...formData, debug: value === 'true' })
                  }
                >
                  <Option value="true">启用</Option>
                  <Option value="false">禁用</Option>
                </Select>
              </FormControl>

              <FormControl>
                <FormLabel>日志级别</FormLabel>
                <Select
                  value={formData.log_level || ''}
                  onChange={(_, value) =>
                    setFormData({
                      ...formData,
                      log_level: value as 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR',
                    })
                  }
                >
                  <Option value="DEBUG">DEBUG</Option>
                  <Option value="INFO">INFO</Option>
                  <Option value="WARNING">WARNING</Option>
                  <Option value="ERROR">ERROR</Option>
                </Select>
              </FormControl>
            </Stack>
          </Box>

          <Divider />

          {/* API 配置 */}
          <Box>
            <Typography level="title-md" sx={{ mb: 2 }}>
              API 配置
            </Typography>
            <Stack spacing={2}>
              <FormControl>
                <FormLabel>API 主机</FormLabel>
                <Input
                  value={formData.api_host || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, api_host: e.target.value })
                  }
                  placeholder="API 主机"
                />
              </FormControl>

              <FormControl>
                <FormLabel>API 端口</FormLabel>
                <Input
                  type="number"
                  value={formData.api_port || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      api_port: parseInt(e.target.value, 10),
                    })
                  }
                  placeholder="API 端口"
                />
              </FormControl>

              <FormControl>
                <FormLabel>API 前缀</FormLabel>
                <Input
                  value={formData.api_prefix || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, api_prefix: e.target.value })
                  }
                  placeholder="API 前缀"
                />
              </FormControl>

              <FormControl>
                <FormLabel>CORS 允许的来源（每行一个）</FormLabel>
                <Input
                  value={(formData.cors_origins || []).join('\n')}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      cors_origins: e.target.value
                        .split('\n')
                        .map((s) => s.trim())
                        .filter((s) => s.length > 0),
                    })
                  }
                  placeholder="http://localhost:3000"
                  multiline
                  minRows={3}
                />
              </FormControl>
            </Stack>
          </Box>

          <Divider />

          {/* 只读配置 */}
          <Box>
            <Typography level="title-md" sx={{ mb: 2 }}>
              只读配置
            </Typography>
            <Stack spacing={2}>
              <FormControl>
                <FormLabel>数据库 URL</FormLabel>
                <Input
                  value={settings.database_url}
                  disabled
                  sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}
                />
              </FormControl>

              {settings.docker_host && (
                <FormControl>
                  <FormLabel>Docker 主机</FormLabel>
                  <Input value={settings.docker_host} disabled />
                </FormControl>
              )}

              {settings.docker_base_url && (
                <FormControl>
                  <FormLabel>Docker Base URL</FormLabel>
                  <Input value={settings.docker_base_url} disabled />
                </FormControl>
              )}
            </Stack>
          </Box>

          <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
            <Button
              type="submit"
              startDecorator={<SaveIcon />}
              loading={loading}
              sx={{ minWidth: 120 }}
            >
              保存配置
            </Button>
          </Box>
        </Stack>
      </Box>
    </Sheet>
  );
};

export default SystemConfigForm;


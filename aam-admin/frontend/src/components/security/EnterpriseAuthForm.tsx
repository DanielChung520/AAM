/**
 * @purpose: 企业认证配置表单组件
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React, { useState } from 'react';
import {
  Box,
  Sheet,
  FormControl,
  FormLabel,
  Input,
  Button,
  Typography,
  Switch,
  Alert,
  Divider,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import type { EnterpriseAuthConfig, EnterpriseAuthConfigUpdate } from '@/types/security';

export interface EnterpriseAuthFormProps {
  config: EnterpriseAuthConfig;
  loading?: boolean;
  onUpdate: (config: EnterpriseAuthConfigUpdate) => Promise<void>;
  onTest?: (userId: string, token?: string) => Promise<void>;
}

export const EnterpriseAuthForm: React.FC<EnterpriseAuthFormProps> = ({
  config,
  loading = false,
  onUpdate,
  onTest,
}) => {
  const { mode } = useColorScheme();
  const [enabled, setEnabled] = useState(config.enabled);
  const [secretKey, setSecretKey] = useState('');
  const [testUserId, setTestUserId] = useState('');
  const [testToken, setTestToken] = useState('');
  const [testResult, setTestResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      await onUpdate({
        enabled,
        secret_key: secretKey || undefined,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : '更新配置失败');
    }
  };

  const handleTest = async () => {
    if (!onTest) return;
    setTestResult(null);
    setError(null);

    try {
      await onTest(testUserId, testToken || undefined);
      setTestResult('测试成功');
    } catch (err) {
      setError(err instanceof Error ? err.message : '测试失败');
    }
  };

  return (
    <Sheet variant="outlined" sx={{ p: 3, borderRadius: 'sm' }}>
      <Typography level="h4" sx={{ mb: 2 }}>
        企业认证配置
      </Typography>

      {error && (
        <Alert color="danger" variant="soft" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <form onSubmit={handleSubmit}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          <FormControl>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <FormLabel>启用企业级认证</FormLabel>
                <Typography level="body-sm" color="neutral">
                  启用后，将使用企业 Secret Key 进行服务间相互认证
                </Typography>
              </Box>
              <Switch checked={enabled} onChange={(e) => setEnabled(e.target.checked)} />
            </Box>
          </FormControl>

          <FormControl>
            <FormLabel>企业 Secret Key</FormLabel>
            <Input
              type="password"
              value={secretKey}
              onChange={(e) => setSecretKey(e.target.value)}
              placeholder={config.secret_key_set ? '输入新密钥以更新' : '请输入企业 Secret Key'}
              disabled={loading}
            />
            {config.secret_key_set && (
              <Typography level="body-sm" color="neutral" sx={{ mt: 1 }}>
                当前密钥：{config.secret_key || '已设置'}
              </Typography>
            )}
          </FormControl>

          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button type="submit" loading={loading}>
              保存配置
            </Button>
          </Box>
        </Box>
      </form>

      <Divider sx={{ my: 3 }} />

      <Box>
        <Typography level="h4" sx={{ mb: 2 }}>
          测试企业认证签名
        </Typography>

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <FormControl>
            <FormLabel>用户 ID</FormLabel>
            <Input
              value={testUserId}
              onChange={(e) => setTestUserId(e.target.value)}
              placeholder="输入用户 ID"
            />
          </FormControl>

          <FormControl>
            <FormLabel>Token（可选）</FormLabel>
            <Input
              value={testToken}
              onChange={(e) => setTestToken(e.target.value)}
              placeholder="输入 JWT Token（可选）"
            />
          </FormControl>

          {testResult && (
            <Alert color="success" variant="soft">
              {testResult}
            </Alert>
          )}

          <Button onClick={handleTest} disabled={!testUserId || loading}>
            测试签名生成
          </Button>
        </Box>
      </Box>
    </Sheet>
  );
};


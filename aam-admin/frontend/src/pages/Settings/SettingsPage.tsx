/**
 * @purpose: 系统设置页面，包含用户信息、密码修改、系统配置、环境变量、健康检查、备份管理等功能
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Divider,
  Button,
  Input,
  FormControl,
  FormLabel,
  Alert,
  Sheet,
  Tabs,
  TabList,
  Tab,
  TabPanel,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import { useAuthStore } from '@/stores/authStore';
import { authApi } from '@/services/api/auth';
import { SystemConfigForm } from '@/components/settings/SystemConfigForm';
import { EnvironmentVariables } from '@/components/settings/EnvironmentVariables';
import { SystemHealth } from '@/components/settings/SystemHealth';
import { BackupManagement } from '@/components/settings/BackupManagement';
import {
  useSettings,
  useEnvironmentVariables,
  useSystemHealth,
  useBackups,
} from '@/hooks/useSettings';
import LockIcon from '@mui/icons-material/Lock';
import PersonIcon from '@mui/icons-material/Person';
import SettingsIcon from '@mui/icons-material/Settings';
import EnvironmentIcon from '@mui/icons-material/Environment';
import HealthIcon from '@mui/icons-material/HealthAndSafety';
import BackupIcon from '@mui/icons-material/Backup';

export const SettingsPage: React.FC = () => {
  const { mode } = useColorScheme();
  const { user } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  
  // 密码修改表单
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // 用户信息
  const [userInfo, setUserInfo] = useState<{
    id: number;
    username: string;
    email: string;
    role: string;
    is_active: boolean;
  } | null>(null);

  // 系统设置 Hooks
  const {
    settings,
    loading: settingsLoading,
    error: settingsError,
    updateSettings,
  } = useSettings();

  const {
    envVars,
    loading: envVarsLoading,
    error: envVarsError,
    updateEnvVar,
  } = useEnvironmentVariables();

  const {
    health,
    loading: healthLoading,
    error: healthError,
    fetchHealth,
  } = useSystemHealth();

  const {
    backups,
    loading: backupsLoading,
    error: backupsError,
    createBackup,
    restoreBackup,
    downloadBackup,
  } = useBackups();

  useEffect(() => {
    // 获取用户信息
    const fetchUserInfo = async () => {
      try {
        const info = await authApi.getCurrentUser();
        setUserInfo(info);
      } catch (err) {
        console.error('获取用户信息失败:', err);
      }
    };
    fetchUserInfo();
  }, []);

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    // 验证新密码
    if (newPassword.length < 6) {
      setError('新密码长度至少为6个字符');
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('两次输入的密码不一致');
      return;
    }

    if (oldPassword === newPassword) {
      setError('新密码不能与旧密码相同');
      return;
    }

    setLoading(true);

    try {
      await authApi.changePassword(oldPassword, newPassword);
      setSuccess('密码修改成功！');
      setOldPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: unknown) {
      const axiosError = err as {
        response?: {
          status?: number;
          data?: { detail?: string; message?: string };
        };
        message?: string;
      };

      let errorMessage = '密码修改失败';
      if (axiosError.response?.data?.detail) {
        errorMessage = axiosError.response.data.detail;
      } else if (axiosError.message) {
        errorMessage = `错误: ${axiosError.message}`;
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography level="h2" sx={{ mb: 3 }}>
        系统设置
      </Typography>

      <Tabs value={activeTab} onChange={(_, value) => setActiveTab(value as number)} sx={{ mt: 2 }}>
        <TabList>
          <Tab>
            <PersonIcon sx={{ mr: 1 }} />
            个人信息
          </Tab>
          <Tab>
            <LockIcon sx={{ mr: 1 }} />
            修改密码
          </Tab>
          <Tab>
            <SettingsIcon sx={{ mr: 1 }} />
            系统配置
          </Tab>
          <Tab>
            <EnvironmentIcon sx={{ mr: 1 }} />
            环境变量
          </Tab>
          <Tab>
            <HealthIcon sx={{ mr: 1 }} />
            系统健康
          </Tab>
          <Tab>
            <BackupIcon sx={{ mr: 1 }} />
            备份与恢复
          </Tab>
        </TabList>

        <TabPanel value={0}>
          <Card sx={{ mt: 2 }}>
            <CardContent>
              <Typography level="h4" sx={{ mb: 2 }}>
                个人信息
              </Typography>
              <Divider sx={{ my: 2 }} />
              {userInfo ? (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Box>
                    <Typography level="body-sm" sx={{ color: 'text.secondary', mb: 0.5 }}>
                      用户名
                    </Typography>
                    <Typography level="body-md">{userInfo.username}</Typography>
                  </Box>
                  <Box>
                    <Typography level="body-sm" sx={{ color: 'text.secondary', mb: 0.5 }}>
                      邮箱
                    </Typography>
                    <Typography level="body-md">{userInfo.email}</Typography>
                  </Box>
                  <Box>
                    <Typography level="body-sm" sx={{ color: 'text.secondary', mb: 0.5 }}>
                      角色
                    </Typography>
                    <Typography level="body-md">{userInfo.role}</Typography>
                  </Box>
                  <Box>
                    <Typography level="body-sm" sx={{ color: 'text.secondary', mb: 0.5 }}>
                      状态
                    </Typography>
                    <Typography level="body-md">
                      {userInfo.is_active ? '已激活' : '已禁用'}
                    </Typography>
                  </Box>
                </Box>
              ) : (
                <Typography level="body-md" sx={{ color: 'text.secondary' }}>
                  加载中...
                </Typography>
              )}
            </CardContent>
          </Card>
        </TabPanel>

        <TabPanel value={1}>
          <Card sx={{ mt: 2 }}>
            <CardContent>
              <Typography level="h4" sx={{ mb: 2 }}>
                修改密码
              </Typography>
              <Divider sx={{ my: 2 }} />

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

              <Box component="form" onSubmit={handleChangePassword}>
                <FormControl sx={{ mb: 2 }}>
                  <FormLabel>当前密码</FormLabel>
                  <Input
                    type="password"
                    placeholder="请输入当前密码"
                    value={oldPassword}
                    onChange={(e) => setOldPassword(e.target.value)}
                    required
                  />
                </FormControl>

                <FormControl sx={{ mb: 2 }}>
                  <FormLabel>新密码</FormLabel>
                  <Input
                    type="password"
                    placeholder="请输入新密码（至少6个字符）"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    required
                    minLength={6}
                  />
                </FormControl>

                <FormControl sx={{ mb: 3 }}>
                  <FormLabel>确认新密码</FormLabel>
                  <Input
                    type="password"
                    placeholder="请再次输入新密码"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    minLength={6}
                  />
                </FormControl>

                <Button
                  type="submit"
                  loading={loading}
                  disabled={!oldPassword || !newPassword || !confirmPassword}
                  sx={{ minWidth: 120 }}
                >
                  修改密码
                </Button>
              </Box>
            </CardContent>
          </Card>
        </TabPanel>

        {/* 系统配置 Tab */}
        <TabPanel value={2}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {settingsError && (
              <Alert color="danger" variant="soft">
                {settingsError.message}
              </Alert>
            )}
            <SystemConfigForm
              settings={settings}
              loading={settingsLoading}
              onSave={updateSettings}
            />
          </Box>
        </TabPanel>

        {/* 环境变量 Tab */}
        <TabPanel value={3}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {envVarsError && (
              <Alert color="danger" variant="soft">
                {envVarsError.message}
              </Alert>
            )}
            <EnvironmentVariables
              envVars={envVars?.items || []}
              loading={envVarsLoading}
              onUpdate={updateEnvVar}
            />
          </Box>
        </TabPanel>

        {/* 系统健康 Tab */}
        <TabPanel value={4}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {healthError && (
              <Alert color="danger" variant="soft">
                {healthError.message}
              </Alert>
            )}
            <SystemHealth
              health={health}
              loading={healthLoading}
              onRefresh={fetchHealth}
            />
          </Box>
        </TabPanel>

        {/* 备份与恢复 Tab */}
        <TabPanel value={5}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {backupsError && (
              <Alert color="danger" variant="soft">
                {backupsError.message}
              </Alert>
            )}
            <BackupManagement
              backups={backups?.items || []}
              loading={backupsLoading}
              onCreateBackup={createBackup}
              onRestoreBackup={restoreBackup}
              onDownloadBackup={downloadBackup}
            />
          </Box>
        </TabPanel>
      </Tabs>
    </Box>
  );
};

export default SettingsPage;


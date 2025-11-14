/**
 * @purpose: 系统设置页面，包含系统配置、环境变量、健康检查、备份管理等功能
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-15
 */
import React, { useState } from 'react';
import {
  Box,
  Typography,
  Alert,
  Tabs,
  TabList,
  Tab,
  TabPanel,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
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
import SettingsIcon from '@mui/icons-material/Settings';
import CodeIcon from '@mui/icons-material/Code';
import HealthIcon from '@mui/icons-material/HealthAndSafety';
import BackupIcon from '@mui/icons-material/Backup';

export const SettingsPage: React.FC = () => {
  const { mode } = useColorScheme();
  const [activeTab, setActiveTab] = useState(0);

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

  return (
    <Box sx={{ p: 3 }}>
      <Typography level="h2" sx={{ mb: 3 }}>
        系统设置
      </Typography>

      <Tabs value={activeTab} onChange={(_, value) => setActiveTab(value as number)} sx={{ mt: 2 }}>
        <TabList>
          <Tab>
            <SettingsIcon sx={{ mr: 1 }} />
            系统配置
          </Tab>
          <Tab>
            <CodeIcon sx={{ mr: 1 }} />
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

        {/* 系统配置 Tab */}
        <TabPanel value={0}>
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
        <TabPanel value={1}>
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
        <TabPanel value={2}>
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
        <TabPanel value={3}>
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

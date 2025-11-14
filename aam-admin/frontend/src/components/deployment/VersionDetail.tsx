/**
 * @purpose: 版本详情组件
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Divider,
  Tabs,
  TabList,
  Tab,
  TabPanel,
  Sheet,
  Code,
  IconButton,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import type { VersionDetail as VersionDetailType } from '@/types/version';

export interface VersionDetailProps {
  version: VersionDetailType | null;
  loading?: boolean;
}

export const VersionDetail: React.FC<VersionDetailProps> = ({
  version,
  loading = false,
}) => {
  const { mode } = useColorScheme();
  const [activeTab, setActiveTab] = useState(0);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'available':
        return 'primary';
      case 'deprecated':
        return 'neutral';
      default:
        return 'neutral';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active':
        return '活动';
      case 'available':
        return '可用';
      case 'deprecated':
        return '已废弃';
      default:
        return '未知';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const formatJSON = (obj: unknown): string => {
    if (!obj) return '';
    try {
      return JSON.stringify(obj, null, 2);
    } catch {
      return String(obj);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
            加载中...
          </Typography>
        </CardContent>
      </Card>
    );
  }

  if (!version) {
    return (
      <Card>
        <CardContent>
          <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
            请选择一个版本查看详情
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Box sx={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* 基本信息 */}
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Box>
              <Typography level="h4" sx={{ mb: 1 }}>
                {version.version}
              </Typography>
              <Chip
                color={getStatusColor(version.status)}
                size="md"
                variant="soft"
                sx={{ mr: 1 }}
              >
                {getStatusText(version.status)}
              </Chip>
            </Box>
          </Box>

          {version.description && (
            <Typography level="body-md" sx={{ mb: 2, color: 'text.secondary' }}>
              {version.description}
            </Typography>
          )}

          <Divider sx={{ my: 2 }} />

          {/* Git 信息 */}
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            {version.git_tag && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography level="body-sm" sx={{ minWidth: 100, color: 'text.secondary' }}>
                  Git Tag:
                </Typography>
                <Code sx={{ flex: 1 }}>{version.git_tag}</Code>
                <IconButton
                  size="sm"
                  variant="plain"
                  onClick={() => copyToClipboard(version.git_tag!)}
                >
                  <ContentCopyIcon fontSize="small" />
                </IconButton>
              </Box>
            )}
            {version.git_branch && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography level="body-sm" sx={{ minWidth: 100, color: 'text.secondary' }}>
                  Git Branch:
                </Typography>
                <Code sx={{ flex: 1 }}>{version.git_branch}</Code>
                <IconButton
                  size="sm"
                  variant="plain"
                  onClick={() => copyToClipboard(version.git_branch!)}
                >
                  <ContentCopyIcon fontSize="small" />
                </IconButton>
              </Box>
            )}
            {version.git_commit && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography level="body-sm" sx={{ minWidth: 100, color: 'text.secondary' }}>
                  Git Commit:
                </Typography>
                <Code sx={{ flex: 1 }}>{version.git_commit}</Code>
                <IconButton
                  size="sm"
                  variant="plain"
                  onClick={() => copyToClipboard(version.git_commit!)}
                >
                  <ContentCopyIcon fontSize="small" />
                </IconButton>
              </Box>
            )}
            {version.image_tag && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography level="body-sm" sx={{ minWidth: 100, color: 'text.secondary' }}>
                  Image Tag:
                </Typography>
                <Code sx={{ flex: 1 }}>{version.image_tag}</Code>
                <IconButton
                  size="sm"
                  variant="plain"
                  onClick={() => copyToClipboard(version.image_tag!)}
                >
                  <ContentCopyIcon fontSize="small" />
                </IconButton>
              </Box>
            )}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography level="body-sm" sx={{ minWidth: 100, color: 'text.secondary' }}>
                创建时间:
              </Typography>
              <Typography level="body-sm">{formatDate(version.created_at)}</Typography>
            </Box>
            {version.created_by && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography level="body-sm" sx={{ minWidth: 100, color: 'text.secondary' }}>
                  创建者:
                </Typography>
                <Typography level="body-sm">{version.created_by}</Typography>
              </Box>
            )}
          </Box>
        </CardContent>
      </Card>

      {/* 配置信息 */}
      {(version.config_snapshot ||
        version.docker_compose_config ||
        version.environment_variables ||
        version.service_config) && (
        <Card sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <CardContent sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <Tabs
              value={activeTab}
              onChange={(_, value) => setActiveTab(value as number)}
              sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}
            >
              <TabList>
                {version.docker_compose_config && <Tab>Docker Compose</Tab>}
                {version.environment_variables && <Tab>环境变量</Tab>}
                {version.service_config && <Tab>服务配置</Tab>}
                {version.config_snapshot && <Tab>配置快照</Tab>}
              </TabList>

              {version.docker_compose_config && (
                <TabPanel value={0} sx={{ flex: 1, overflow: 'auto' }}>
                  <Sheet
                    sx={{
                      p: 2,
                      bgcolor: 'background.level1',
                      borderRadius: 'sm',
                      overflow: 'auto',
                    }}
                  >
                    <Code sx={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>
                      {formatJSON(version.docker_compose_config)}
                    </Code>
                  </Sheet>
                </TabPanel>
              )}

              {version.environment_variables && (
                <TabPanel value={version.docker_compose_config ? 1 : 0} sx={{ flex: 1, overflow: 'auto' }}>
                  <Sheet
                    sx={{
                      p: 2,
                      bgcolor: 'background.level1',
                      borderRadius: 'sm',
                      overflow: 'auto',
                    }}
                  >
                    <Code sx={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>
                      {formatJSON(version.environment_variables)}
                    </Code>
                  </Sheet>
                </TabPanel>
              )}

              {version.service_config && (
                <TabPanel
                  value={
                    (version.docker_compose_config ? 1 : 0) +
                    (version.environment_variables ? 1 : 0)
                  }
                  sx={{ flex: 1, overflow: 'auto' }}
                >
                  <Sheet
                    sx={{
                      p: 2,
                      bgcolor: 'background.level1',
                      borderRadius: 'sm',
                      overflow: 'auto',
                    }}
                  >
                    <Code sx={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>
                      {formatJSON(version.service_config)}
                    </Code>
                  </Sheet>
                </TabPanel>
              )}

              {version.config_snapshot && (
                <TabPanel
                  value={
                    (version.docker_compose_config ? 1 : 0) +
                    (version.environment_variables ? 1 : 0) +
                    (version.service_config ? 1 : 0)
                  }
                  sx={{ flex: 1, overflow: 'auto' }}
                >
                  <Sheet
                    sx={{
                      p: 2,
                      bgcolor: 'background.level1',
                      borderRadius: 'sm',
                      overflow: 'auto',
                    }}
                  >
                    <Code sx={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>
                      {formatJSON(version.config_snapshot)}
                    </Code>
                  </Sheet>
                </TabPanel>
              )}
            </Tabs>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default VersionDetail;


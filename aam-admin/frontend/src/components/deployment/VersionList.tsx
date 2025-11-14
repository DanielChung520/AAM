/**
 * @purpose: 版本列表组件（左侧面板，40%宽度）
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React from 'react';
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  Chip,
  Typography,
  Button,
  Card,
  CardContent,
  IconButton,
  Select,
  Option,
  Input,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import AddIcon from '@mui/icons-material/Add';
import type { Version, VersionStatus } from '@/types/version';

export interface VersionListProps {
  versions: Version[];
  selectedVersion?: string;
  activeVersion?: string | null;
  onSelectVersion: (version: string) => void;
  onCreateVersion?: () => void;
  onDeleteVersion?: (version: string) => void;
  loading?: boolean;
  statusFilter?: VersionStatus | null;
  onStatusFilterChange?: (status: VersionStatus | null) => void;
  searchQuery?: string;
  onSearchChange?: (query: string) => void;
}

export const VersionList: React.FC<VersionListProps> = ({
  versions,
  selectedVersion,
  activeVersion,
  onSelectVersion,
  onCreateVersion,
  onDeleteVersion,
  loading = false,
  statusFilter = null,
  onStatusFilterChange,
  searchQuery = '',
  onSearchChange,
}) => {
  const { mode } = useColorScheme();

  const getStatusColor = (status: VersionStatus) => {
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

  const getStatusText = (status: VersionStatus) => {
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
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <Box
      sx={{
        width: '100%',
        height: '100%',
        bgcolor: 'background.surface',
        borderRadius: 'sm',
        border: '1px solid',
        borderColor: 'divider',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* 头部 */}
      <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography level="title-md">版本列表</Typography>
          {onCreateVersion && (
            <IconButton
              size="sm"
              variant="outlined"
              color="primary"
              onClick={onCreateVersion}
            >
              <AddIcon />
            </IconButton>
          )}
        </Box>

        {/* 搜索框 */}
        {onSearchChange && (
          <Box sx={{ mb: 2 }}>
            <Input
              placeholder="搜索版本号..."
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              size="sm"
              fullWidth
            />
          </Box>
        )}

        {/* 状态筛选 */}
        {onStatusFilterChange && (
          <Select
            size="sm"
            value={statusFilter || 'all'}
            onChange={(_, value) => {
              onStatusFilterChange(value === 'all' ? null : (value as VersionStatus));
            }}
            sx={{ width: '100%' }}
          >
            <Option value="all">全部状态</Option>
            <Option value="active">活动</Option>
            <Option value="available">可用</Option>
            <Option value="deprecated">已废弃</Option>
          </Select>
        )}
      </Box>

      {/* 版本列表 */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        {loading ? (
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
              加载中...
            </Typography>
          </Box>
        ) : versions.length === 0 ? (
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
              暂无版本
            </Typography>
          </Box>
        ) : (
          <List>
            {versions.map((version) => {
              const isSelected = selectedVersion === version.version;
              const isActive = activeVersion === version.version;

              return (
                <ListItem key={version.version} sx={{ p: 0 }}>
                  <Card
                    sx={{
                      width: '100%',
                      m: 1,
                      border: isSelected ? '2px solid' : '1px solid',
                      borderColor: isSelected
                        ? 'primary.500'
                        : isActive
                        ? 'success.500'
                        : 'divider',
                      bgcolor: isSelected
                        ? 'primary.50'
                        : isActive
                        ? 'success.50'
                        : 'background.surface',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      '&:hover': {
                        borderColor: 'primary.500',
                        transform: 'translateY(-2px)',
                        boxShadow: 'sm',
                      },
                    }}
                    onClick={() => onSelectVersion(version.version)}
                  >
                    <CardContent>
                      <Box
                        sx={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'flex-start',
                          mb: 1,
                        }}
                      >
                        <Box sx={{ flex: 1 }}>
                          <Typography level="title-sm" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                            {version.version}
                          </Typography>
                          {isActive && (
                            <Chip
                              color="success"
                              size="sm"
                              variant="soft"
                              sx={{ mb: 0.5 }}
                            >
                              当前活动版本
                            </Chip>
                          )}
                          <Chip
                            color={getStatusColor(version.status)}
                            size="sm"
                            variant="soft"
                            sx={{ mb: 1 }}
                          >
                            {getStatusText(version.status)}
                          </Chip>
                        </Box>
                      </Box>

                      {version.description && (
                        <Typography
                          level="body-xs"
                          sx={{ color: 'text.secondary', mb: 1 }}
                        >
                          {version.description}
                        </Typography>
                      )}

                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                        {version.git_tag && (
                          <Typography level="body-xs" sx={{ color: 'text.tertiary' }}>
                            标签: {version.git_tag}
                          </Typography>
                        )}
                        {version.git_commit && (
                          <Typography level="body-xs" sx={{ color: 'text.tertiary' }}>
                            提交: {version.git_commit.substring(0, 7)}
                          </Typography>
                        )}
                        <Typography level="body-xs" sx={{ color: 'text.tertiary' }}>
                          创建: {formatDate(version.created_at)}
                        </Typography>
                        {version.created_by && (
                          <Typography level="body-xs" sx={{ color: 'text.tertiary' }}>
                            创建者: {version.created_by}
                          </Typography>
                        )}
                      </Box>
                    </CardContent>
                  </Card>
                </ListItem>
              );
            })}
          </List>
        )}
      </Box>
    </Box>
  );
};

export default VersionList;


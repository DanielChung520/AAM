/**
 * @purpose: 部署历史页面 - 显示所有部署历史记录
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React, { useState } from 'react';
import {
  Box,
  Typography,
  Sheet,
  Alert,
  Select,
  Option,
  Input,
  IconButton,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import SearchIcon from '@mui/icons-material/Search';
import { DeploymentHistory } from '@/components/deployment/DeploymentHistory';
import { useDeployments } from '@/hooks/useDeployments';
import type { DeploymentStatus } from '@/types/deployment';

export const DeploymentHistoryPage: React.FC = () => {
  const { mode } = useColorScheme();
  const [statusFilter, setStatusFilter] = useState<DeploymentStatus | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');

  // 获取部署历史
  const {
    deployments,
    total,
    page,
    pageSize,
    totalPages,
    loading,
    error,
    refresh,
    setPage,
    setPageSize,
  } = useDeployments(
    {
      status: statusFilter || undefined,
      search: searchQuery || undefined,
    },
    true
  );

  return (
    <Box
      sx={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        gap: 2,
        p: 2,
      }}
    >
      {/* 页面标题 */}
      <Box>
        <Typography level="h2" sx={{ mb: 1 }}>
          部署历史
        </Typography>
        <Typography level="body-md" sx={{ color: 'text.secondary' }}>
          查看所有部署记录和操作历史
        </Typography>
      </Box>

      {/* 错误提示 */}
      {error && (
        <Alert color="danger" sx={{ mb: 2 }}>
          {error.message}
        </Alert>
      )}

      {/* 筛选工具栏 */}
      <Sheet
        variant="outlined"
        sx={{
          p: 2,
          borderRadius: 'sm',
          display: 'flex',
          gap: 2,
          alignItems: 'center',
          flexWrap: 'wrap',
        }}
      >
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', flex: 1, minWidth: 200 }}>
          <Input
            placeholder="搜索版本号、操作者..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            startDecorator={<SearchIcon />}
            sx={{ flex: 1 }}
          />
        </Box>

        <Select
          placeholder="状态筛选"
          value={statusFilter || 'all'}
          onChange={(_, value) => {
            setStatusFilter(value === 'all' ? null : (value as DeploymentStatus));
          }}
          sx={{ minWidth: 150 }}
        >
          <Option value="all">全部状态</Option>
          <Option value="pending">待处理</Option>
          <Option value="deploying">部署中</Option>
          <Option value="active">已激活</Option>
          <Option value="failed">失败</Option>
          <Option value="rolled_back">已回滚</Option>
        </Select>

        <IconButton
          variant="outlined"
          color="primary"
          onClick={() => refresh()}
          sx={{ ml: 'auto' }}
        >
          刷新
        </IconButton>
      </Sheet>

      {/* 部署历史表格 */}
      <Sheet
        variant="outlined"
        sx={{
          flex: 1,
          borderRadius: 'sm',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <DeploymentHistory
          deployments={deployments}
          total={total}
          page={page}
          pageSize={pageSize}
          totalPages={totalPages}
          loading={loading}
          onPageChange={setPage}
          onPageSizeChange={setPageSize}
        />
      </Sheet>
    </Box>
  );
};

export default DeploymentHistoryPage;


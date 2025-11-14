/**
 * @purpose: 部署历史表格组件
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React, { useState } from 'react';
import {
  Box,
  Table,
  Sheet,
  Chip,
  Typography,
  IconButton,
  Button,
  Modal,
  ModalDialog,
  ModalClose,
  DialogTitle,
  DialogContent,
  Drawer,
  Divider,
  Code,
  Pagination,
  Select,
  Option,
  Input,
  Alert,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import VisibilityIcon from '@mui/icons-material/Visibility';
import DescriptionIcon from '@mui/icons-material/Description';
import type { DeploymentRecord, DeploymentStatus } from '@/types/deployment';

export interface DeploymentHistoryProps {
  deployments: DeploymentRecord[];
  loading?: boolean;
  page?: number;
  pageSize?: number;
  total?: number;
  totalPages?: number;
  onPageChange?: (page: number) => void;
  onPageSizeChange?: (pageSize: number) => void;
  onViewDetail?: (deployment: DeploymentRecord) => void;
  onViewLogs?: (deploymentId: number) => void;
}

export const DeploymentHistory: React.FC<DeploymentHistoryProps> = ({
  deployments,
  loading = false,
  page = 1,
  pageSize = 20,
  total = 0,
  totalPages = 1,
  onPageChange,
  onPageSizeChange,
  onViewDetail,
  onViewLogs,
}) => {
  const { mode } = useColorScheme();
  const [selectedDeployment, setSelectedDeployment] = useState<DeploymentRecord | null>(null);
  const [detailOpen, setDetailOpen] = useState(false);
  const [logsOpen, setLogsOpen] = useState(false);
  const [logs, setLogs] = useState<string>('');

  const getStatusColor = (status: DeploymentStatus) => {
    switch (status) {
      case 'success':
        return 'success';
      case 'failed':
        return 'danger';
      case 'in_progress':
        return 'primary';
      case 'pending':
        return 'neutral';
      case 'rolled_back':
        return 'warning';
      default:
        return 'neutral';
    }
  };

  const getStatusText = (status: DeploymentStatus) => {
    switch (status) {
      case 'success':
        return '成功';
      case 'failed':
        return '失败';
      case 'in_progress':
        return '进行中';
      case 'pending':
        return '等待中';
      case 'rolled_back':
        return '已回滚';
      default:
        return '未知';
    }
  };

  const getStrategyText = (strategy?: string) => {
    switch (strategy) {
      case 'blue_green':
        return '蓝绿部署';
      case 'rolling':
        return '滚动更新';
      case 'canary':
        return '金丝雀部署';
      default:
        return '-';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const handleViewDetail = (deployment: DeploymentRecord) => {
    setSelectedDeployment(deployment);
    setDetailOpen(true);
    if (onViewDetail) {
      onViewDetail(deployment);
    }
  };

  const handleViewLogs = async (deploymentId: number) => {
    setLogsOpen(true);
    if (onViewLogs) {
      onViewLogs(deploymentId);
    }
    // 这里应该通过 props 或 hook 获取日志
    // 暂时显示占位符
    setLogs('加载日志中...');
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Sheet
        variant="outlined"
        sx={{
          borderRadius: 'sm',
          overflow: 'auto',
          bgcolor: 'background.surface',
        }}
      >
        <Table aria-label="部署历史表格" stickyHeader>
          <thead>
            <tr>
              <th style={{ width: 80 }}>ID</th>
              <th style={{ width: 120 }}>版本号</th>
              <th style={{ width: 100 }}>状态</th>
              <th style={{ width: 120 }}>策略</th>
              <th style={{ width: 150 }}>部署时间</th>
              <th style={{ width: 150 }}>完成时间</th>
              <th style={{ width: 100 }}>操作者</th>
              <th style={{ width: 120 }}>操作</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={8} style={{ textAlign: 'center', padding: '2rem' }}>
                  <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
                    加载中...
                  </Typography>
                </td>
              </tr>
            ) : deployments.length === 0 ? (
              <tr>
                <td colSpan={8} style={{ textAlign: 'center', padding: '2rem' }}>
                  <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
                    暂无部署记录
                  </Typography>
                </td>
              </tr>
            ) : (
              deployments.map((deployment) => (
                <tr key={deployment.id}>
                  <td>
                    <Typography level="body-sm">{deployment.id}</Typography>
                  </td>
                  <td>
                    <Typography level="body-sm" sx={{ fontFamily: 'monospace' }}>
                      {deployment.version}
                    </Typography>
                  </td>
                  <td>
                    <Chip
                      color={getStatusColor(deployment.status)}
                      size="sm"
                      variant="soft"
                    >
                      {getStatusText(deployment.status)}
                    </Chip>
                  </td>
                  <td>
                    <Typography level="body-sm">
                      {getStrategyText(deployment.deployment_strategy)}
                    </Typography>
                  </td>
                  <td>
                    <Typography level="body-sm">
                      {formatDate(deployment.deployment_time)}
                    </Typography>
                  </td>
                  <td>
                    <Typography level="body-sm">
                      {deployment.completed_time
                        ? formatDate(deployment.completed_time)
                        : '-'}
                    </Typography>
                  </td>
                  <td>
                    <Typography level="body-sm">
                      {deployment.operator_name || `ID: ${deployment.operator_id}`}
                    </Typography>
                  </td>
                  <td>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <IconButton
                        size="sm"
                        variant="plain"
                        color="primary"
                        onClick={() => handleViewDetail(deployment)}
                      >
                        <VisibilityIcon fontSize="small" />
                      </IconButton>
                      <IconButton
                        size="sm"
                        variant="plain"
                        color="neutral"
                        onClick={() => handleViewLogs(deployment.id)}
                      >
                        <DescriptionIcon fontSize="small" />
                      </IconButton>
                    </Box>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </Table>
      </Sheet>

      {/* 分页 */}
      {totalPages > 1 && (
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mt: 2,
            gap: 2,
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
              每页显示:
            </Typography>
            <Select
              value={pageSize}
              onChange={(_, value) => onPageSizeChange?.(value as number)}
              size="sm"
              sx={{ minWidth: 80 }}
            >
              <Option value={10}>10</Option>
              <Option value={20}>20</Option>
              <Option value={50}>50</Option>
              <Option value={100}>100</Option>
            </Select>
          </Box>
          <Pagination
            count={totalPages}
            page={page}
            onChange={(_, value) => onPageChange?.(value)}
            size="sm"
          />
          <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
            共 {total} 条记录
          </Typography>
        </Box>
      )}

      {/* 部署详情对话框 */}
      <Modal open={detailOpen} onClose={() => setDetailOpen(false)}>
        <ModalDialog sx={{ maxWidth: 600, width: '100%' }}>
          <ModalClose />
          <DialogTitle>部署详情</DialogTitle>
          <DialogContent>
            {selectedDeployment && (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box>
                  <Typography level="body-xs" sx={{ color: 'text.secondary', mb: 0.5 }}>
                    部署 ID
                  </Typography>
                  <Typography level="body-md">{selectedDeployment.id}</Typography>
                </Box>
                <Box>
                  <Typography level="body-xs" sx={{ color: 'text.secondary', mb: 0.5 }}>
                    版本号
                  </Typography>
                  <Typography level="body-md" sx={{ fontFamily: 'monospace' }}>
                    {selectedDeployment.version}
                  </Typography>
                </Box>
                <Box>
                  <Typography level="body-xs" sx={{ color: 'text.secondary', mb: 0.5 }}>
                    状态
                  </Typography>
                  <Chip
                    color={getStatusColor(selectedDeployment.status)}
                    size="sm"
                    variant="soft"
                  >
                    {getStatusText(selectedDeployment.status)}
                  </Chip>
                </Box>
                {selectedDeployment.deployment_strategy && (
                  <Box>
                    <Typography level="body-xs" sx={{ color: 'text.secondary', mb: 0.5 }}>
                      部署策略
                    </Typography>
                    <Typography level="body-md">
                      {getStrategyText(selectedDeployment.deployment_strategy)}
                    </Typography>
                  </Box>
                )}
                {selectedDeployment.error_message && (
                  <Box>
                    <Typography level="body-xs" sx={{ color: 'text.secondary', mb: 0.5 }}>
                      错误信息
                    </Typography>
                    <Alert color="danger" variant="soft">
                      {selectedDeployment.error_message}
                    </Alert>
                  </Box>
                )}
              </Box>
            )}
          </DialogContent>
        </ModalDialog>
      </Modal>

      {/* 部署日志抽屉 */}
      <Drawer open={logsOpen} onClose={() => setLogsOpen(false)} anchor="right" size="lg">
        <Box sx={{ p: 2 }}>
          <Typography level="h4" sx={{ mb: 2 }}>
            部署日志
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Sheet
            sx={{
              p: 2,
              bgcolor: 'background.level1',
              borderRadius: 'sm',
              maxHeight: '70vh',
              overflow: 'auto',
            }}
          >
            <Code sx={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '0.875rem' }}>
              {logs || '暂无日志'}
            </Code>
          </Sheet>
        </Box>
      </Drawer>
    </Box>
  );
};

export default DeploymentHistory;


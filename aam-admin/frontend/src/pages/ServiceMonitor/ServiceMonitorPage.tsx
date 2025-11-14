/**
 * @purpose: 服务管理页面
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React, { useState } from 'react';
import {
  Box,
  Typography,
  Sheet,
  Table,
  Chip,
  Button,
  IconButton,
  CircularProgress,
  Alert,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';
import RefreshIcon from '@mui/icons-material/Refresh';
import InfoIcon from '@mui/icons-material/Info';
import { useServices, useService, useServiceStats, useServiceOperation } from '@/hooks/useServices';
import { ServiceDetailDrawer } from '@/components/service/ServiceDetailDrawer';
import { ServiceOperationDialog } from '@/components/service/ServiceOperationDialog';
import type { ServiceName, ServiceOperationType } from '@/types/service';

export const ServiceMonitorPage: React.FC = () => {
  const { mode } = useColorScheme();
  const { services, loading, error, refresh } = useServices();
  const { operateService, loading: operationLoading } = useServiceOperation();

  const [selectedService, setSelectedService] = useState<ServiceName | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogOperation, setDialogOperation] = useState<ServiceOperationType>('start');
  const [operationService, setOperationService] = useState<ServiceName | null>(null);

  const { service: serviceDetail, loading: detailLoading } = useService(
    selectedService,
    drawerOpen
  );
  const { stats: serviceStats } = useServiceStats(selectedService, drawerOpen);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'success';
      case 'stopped':
        return 'neutral';
      case 'error':
        return 'danger';
      default:
        return 'neutral';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'running':
        return '运行中';
      case 'stopped':
        return '已停止';
      case 'error':
        return '错误';
      default:
        return '未知';
    }
  };

  const formatUptime = (seconds?: number) => {
    if (!seconds) return '-';
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (days > 0) return `${days}天 ${hours}小时`;
    if (hours > 0) return `${hours}小时 ${minutes}分钟`;
    return `${minutes}分钟`;
  };

  const formatMemory = (percent: number) => {
    return `${percent.toFixed(2)}%`;
  };

  const handleViewDetail = (serviceName: ServiceName) => {
    setSelectedService(serviceName);
    setDrawerOpen(true);
  };

  const handleCloseDrawer = () => {
    setDrawerOpen(false);
    setSelectedService(null);
  };

  const handleOpenDialog = (serviceName: ServiceName, operation: ServiceOperationType) => {
    setOperationService(serviceName);
    setDialogOperation(operation);
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setOperationService(null);
  };

  const handleConfirmOperation = async (reason?: string) => {
    if (!operationService) return;

    const result = await operateService(operationService, dialogOperation, {
      confirm: true,
      reason,
    });

    if (result?.success) {
      handleCloseDialog();
      // 刷新服务列表
      await refresh();
      // 如果操作的是当前查看的服务，刷新详情
      if (operationService === selectedService) {
        // 详情会自动刷新
      }
    } else {
      throw new Error(result?.message || '操作失败');
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography level="h2">服务管理</Typography>
        <Button
          variant="outlined"
          startDecorator={<RefreshIcon />}
          onClick={() => refresh()}
          loading={loading}
        >
          刷新
        </Button>
      </Box>

      {/* 错误提示 */}
      {error && (
        <Alert color="danger" sx={{ mb: 2 }}>
          {error.message || '数据加载失败，请刷新页面重试'}
        </Alert>
      )}

      {/* 服务列表表格 */}
      <Sheet
        variant="outlined"
        sx={{
          borderRadius: 'sm',
          overflow: 'auto',
          bgcolor: 'background.surface',
        }}
      >
        {loading ? (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <CircularProgress />
            <Typography level="body-sm" sx={{ mt: 2, color: 'text.secondary' }}>
              加载中...
            </Typography>
          </Box>
        ) : services.length === 0 ? (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
              暂无服务数据
            </Typography>
          </Box>
        ) : (
          <Table sx={{ '--TableCell-headBackground': 'transparent' }}>
            <thead>
              <tr>
                <th style={{ width: '15%' }}>服务名称</th>
                <th style={{ width: '10%' }}>状态</th>
                <th style={{ width: '10%' }}>版本</th>
                <th style={{ width: '10%' }}>CPU</th>
                <th style={{ width: '10%' }}>内存</th>
                <th style={{ width: '10%' }}>运行时间</th>
                <th style={{ width: '35%' }}>操作</th>
              </tr>
            </thead>
            <tbody>
              {services.map((service) => (
                <tr key={service.name}>
                  <td>
                    <Typography level="body-sm" sx={{ fontWeight: 'md' }}>
                      {service.name}
                    </Typography>
                  </td>
                  <td>
                    <Chip
                      color={getStatusColor(service.status)}
                      size="sm"
                      variant="soft"
                    >
                      {getStatusText(service.status)}
                    </Chip>
                  </td>
                  <td>
                    <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
                      {service.version || '-'}
                    </Typography>
                  </td>
                  <td>
                    <Typography level="body-sm">
                      {service.cpu_usage.toFixed(2)}%
                    </Typography>
                  </td>
                  <td>
                    <Typography level="body-sm">
                      {formatMemory(service.memory_usage)}
                    </Typography>
                  </td>
                  <td>
                    <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
                      {formatUptime(service.uptime)}
                    </Typography>
                  </td>
                  <td>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <IconButton
                        size="sm"
                        variant="plain"
                        color="primary"
                        onClick={() => handleViewDetail(service.name)}
                      >
                        <InfoIcon />
                      </IconButton>
                      {service.status === 'running' ? (
                        <>
                          <IconButton
                            size="sm"
                            variant="plain"
                            color="warning"
                            onClick={() => handleOpenDialog(service.name, 'restart')}
                            disabled={operationLoading}
                          >
                            <RefreshIcon />
                          </IconButton>
                          <IconButton
                            size="sm"
                            variant="plain"
                            color="danger"
                            onClick={() => handleOpenDialog(service.name, 'stop')}
                            disabled={operationLoading}
                          >
                            <StopIcon />
                          </IconButton>
                        </>
                      ) : (
                        <IconButton
                          size="sm"
                          variant="plain"
                          color="success"
                          onClick={() => handleOpenDialog(service.name, 'start')}
                          disabled={operationLoading}
                        >
                          <PlayArrowIcon />
                        </IconButton>
                      )}
                    </Box>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        )}
      </Sheet>

      {/* 服务详情抽屉 */}
      <ServiceDetailDrawer
        open={drawerOpen}
        service={serviceDetail}
        stats={serviceStats}
        onClose={handleCloseDrawer}
        loading={detailLoading}
      />

      {/* 操作确认对话框 */}
      {operationService && (
        <ServiceOperationDialog
          open={dialogOpen}
          serviceName={operationService}
          operation={dialogOperation}
          onConfirm={handleConfirmOperation}
          onCancel={handleCloseDialog}
          loading={operationLoading}
        />
      )}
    </Box>
  );
};

export default ServiceMonitorPage;


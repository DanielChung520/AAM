/**
 * @purpose: 仪表盘页面
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React from 'react';
import {
  Box,
  Typography,
  Card,
  Grid,
  Sheet,
  Table,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import {
  useDashboardStats,
  useServiceStatus,
  useSystemMetrics,
  useRecentOperations,
} from '@/hooks/useDashboard';
import { ResourceChart } from '@/components/charts/ResourceChart';
// 格式化相对时间
const formatRelativeTime = (date: string): string => {
  const now = new Date();
  const target = new Date(date);
  const diffMs = now.getTime() - target.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return '刚刚';
  if (diffMins < 60) return `${diffMins}分钟前`;
  if (diffHours < 24) return `${diffHours}小时前`;
  if (diffDays < 7) return `${diffDays}天前`;
  return target.toLocaleDateString('zh-CN');
};

export const DashboardPage: React.FC = () => {
  const { mode } = useColorScheme();
  const { stats, loading: statsLoading, error: statsError } = useDashboardStats();
  const { services, loading: servicesLoading, error: servicesError } = useServiceStatus();
  const { metrics, loading: metricsLoading, error: metricsError } = useSystemMetrics();
  const { operations, loading: operationsLoading, error: operationsError } =
    useRecentOperations(10, 24);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'success';
      case 'stopped':
        return 'danger';
      case 'error':
        return 'warning';
      default:
        return 'neutral';
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

  return (
    <Box sx={{ p: 3 }}>
      <Typography level="h2" sx={{ mb: 3 }}>
        仪表盘
      </Typography>

      {/* 错误提示 */}
      {(statsError || servicesError || metricsError || operationsError) && (
        <Alert color="danger" sx={{ mb: 2 }}>
          数据加载失败，请刷新页面重试
        </Alert>
      )}

      {/* 顶部统计卡片 */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid xs={12} sm={6} md={3}>
          <Card sx={{ p: 2 }}>
            <Typography level="body-sm" sx={{ color: 'text.secondary', mb: 1 }}>
              运行服务数
            </Typography>
            {statsLoading ? (
              <CircularProgress size="sm" />
            ) : (
              <Typography level="h3">
                {stats?.running_services || 0}/{stats?.total_services || 0}
              </Typography>
            )}
          </Card>
        </Grid>
        <Grid xs={12} sm={6} md={3}>
          <Card sx={{ p: 2 }}>
            <Typography level="body-sm" sx={{ color: 'text.secondary', mb: 1 }}>
              LLM Provider
            </Typography>
            {statsLoading ? (
              <CircularProgress size="sm" />
            ) : (
              <Typography level="h3">
                {stats?.active_providers || 0} Active
              </Typography>
            )}
          </Card>
        </Grid>
        <Grid xs={12} sm={6} md={3}>
          <Card sx={{ p: 2 }}>
            <Typography level="body-sm" sx={{ color: 'text.secondary', mb: 1 }}>
              当前版本
            </Typography>
            {statsLoading ? (
              <CircularProgress size="sm" />
            ) : (
              <Typography level="h3">
                {stats?.current_version || 'N/A'}
              </Typography>
            )}
          </Card>
        </Grid>
        <Grid xs={12} sm={6} md={3}>
          <Card sx={{ p: 2 }}>
            <Typography level="body-sm" sx={{ color: 'text.secondary', mb: 1 }}>
              系统负载
            </Typography>
            {statsLoading ? (
              <CircularProgress size="sm" />
            ) : (
              <Typography level="h3">
                {stats?.system_load.toFixed(1) || 0}%
              </Typography>
            )}
          </Card>
        </Grid>
      </Grid>

      {/* 中部：服务状态监控 + 资源使用图表 */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid xs={12} md={6}>
          <Card>
            <Typography level="title-md" sx={{ mb: 2 }}>
              服务状态监控
            </Typography>
            {servicesLoading ? (
              <Box sx={{ p: 3, textAlign: 'center' }}>
                <CircularProgress />
              </Box>
            ) : (
              <Sheet variant="outlined" sx={{ borderRadius: 'sm', overflow: 'auto' }}>
                <Table>
                  <thead>
                    <tr>
                      <th>服务名称</th>
                      <th>状态</th>
                      <th>版本</th>
                      <th>CPU</th>
                      <th>内存</th>
                      <th>运行时间</th>
                    </tr>
                  </thead>
                  <tbody>
                    {services.length === 0 ? (
                      <tr>
                        <td colSpan={6} style={{ textAlign: 'center', padding: '20px' }}>
                          <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
                            暂无服务数据
                          </Typography>
                        </td>
                      </tr>
                    ) : (
                      services.map((service) => (
                        <tr key={service.name}>
                          <td>
                            <Typography level="body-sm">{service.name}</Typography>
                          </td>
                          <td>
                            <Chip
                              color={getStatusColor(service.status)}
                              size="sm"
                              variant="soft"
                            >
                              {service.status === 'running' ? '运行中' : service.status === 'stopped' ? '已停止' : '错误'}
                            </Chip>
                          </td>
                          <td>
                            <Typography level="body-sm">
                              {service.version || '-'}
                            </Typography>
                          </td>
                          <td>
                            <Typography level="body-sm">
                              {service.cpu_usage.toFixed(1)}%
                            </Typography>
                          </td>
                          <td>
                            <Typography level="body-sm">
                              {service.memory_usage.toFixed(1)}%
                            </Typography>
                          </td>
                          <td>
                            <Typography level="body-sm">
                              {formatUptime(service.uptime)}
                            </Typography>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </Table>
              </Sheet>
            )}
          </Card>
        </Grid>
        <Grid xs={12} md={6}>
          <Card>
            <Typography level="title-md" sx={{ mb: 2 }}>
              资源使用图表
            </Typography>
            <ResourceChart metrics={metrics} loading={metricsLoading} height={300} />
          </Card>
        </Grid>
      </Grid>

      {/* 底部：最近操作记录 + 系统健康状态 */}
      <Grid container spacing={2}>
        <Grid xs={12} md={6}>
          <Card>
            <Typography level="title-md" sx={{ mb: 2 }}>
              最近操作记录
            </Typography>
            {operationsLoading ? (
              <Box sx={{ p: 3, textAlign: 'center' }}>
                <CircularProgress />
              </Box>
            ) : (
              <Sheet variant="outlined" sx={{ borderRadius: 'sm', overflow: 'auto' }}>
                <Table>
                  <thead>
                    <tr>
                      <th>操作</th>
                      <th>资源</th>
                      <th>操作者</th>
                      <th>时间</th>
                    </tr>
                  </thead>
                  <tbody>
                    {operations.length === 0 ? (
                      <tr>
                        <td colSpan={4} style={{ textAlign: 'center', padding: '20px' }}>
                          <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
                            暂无操作记录
                          </Typography>
                        </td>
                      </tr>
                    ) : (
                      operations.map((op) => (
                        <tr key={op.id}>
                          <td>
                            <Typography level="body-sm">{op.action}</Typography>
                          </td>
                          <td>
                            <Typography level="body-sm">
                              {op.resource_type}
                              {op.resource_id && ` (${op.resource_id})`}
                            </Typography>
                          </td>
                          <td>
                            <Typography level="body-sm">{op.operator}</Typography>
                          </td>
                          <td>
                            <Typography level="body-sm">
                              {formatRelativeTime(op.created_at)}
                            </Typography>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </Table>
              </Sheet>
            )}
          </Card>
        </Grid>
        <Grid xs={12} md={6}>
          <Card>
            <Typography level="title-md" sx={{ mb: 2 }}>
              系统健康状态
            </Typography>
            {metricsLoading ? (
              <Box sx={{ p: 3, textAlign: 'center' }}>
                <CircularProgress />
              </Box>
            ) : metrics ? (
              <Box>
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography level="body-sm">CPU 使用率</Typography>
                    <Typography level="body-sm" fontWeight="bold">
                      {metrics.cpu_usage.toFixed(1)}%
                    </Typography>
                  </Box>
                  <Box
                    sx={{
                      width: '100%',
                      height: 8,
                      bgcolor: 'background.level1',
                      borderRadius: 'sm',
                      overflow: 'hidden',
                    }}
                  >
                    <Box
                      sx={{
                        width: `${metrics.cpu_usage}%`,
                        height: '100%',
                        bgcolor: metrics.cpu_usage > 80 ? 'danger.500' : 'primary.500',
                      }}
                    />
                  </Box>
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography level="body-sm">内存使用率</Typography>
                    <Typography level="body-sm" fontWeight="bold">
                      {metrics.memory_usage.toFixed(1)}%
                    </Typography>
                  </Box>
                  <Box
                    sx={{
                      width: '100%',
                      height: 8,
                      bgcolor: 'background.level1',
                      borderRadius: 'sm',
                      overflow: 'hidden',
                    }}
                  >
                    <Box
                      sx={{
                        width: `${metrics.memory_usage}%`,
                        height: '100%',
                        bgcolor: metrics.memory_usage > 80 ? 'danger.500' : 'success.500',
                      }}
                    />
                  </Box>
                  <Typography level="body-xs" sx={{ mt: 0.5, color: 'text.secondary' }}>
                    {metrics.memory_used.toFixed(0)} MB / {metrics.memory_total.toFixed(0)} MB
                  </Typography>
                </Box>
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography level="body-sm">磁盘使用率</Typography>
                    <Typography level="body-sm" fontWeight="bold">
                      {metrics.disk_usage.toFixed(1)}%
                    </Typography>
                  </Box>
                  <Box
                    sx={{
                      width: '100%',
                      height: 8,
                      bgcolor: 'background.level1',
                      borderRadius: 'sm',
                      overflow: 'hidden',
                    }}
                  >
                    <Box
                      sx={{
                        width: `${metrics.disk_usage}%`,
                        height: '100%',
                        bgcolor: metrics.disk_usage > 80 ? 'danger.500' : 'warning.500',
                      }}
                    />
                  </Box>
                  <Typography level="body-xs" sx={{ mt: 0.5, color: 'text.secondary' }}>
                    {metrics.disk_used.toFixed(1)} GB / {metrics.disk_total.toFixed(1)} GB
        </Typography>
                </Box>
              </Box>
            ) : (
              <Box sx={{ p: 3, textAlign: 'center' }}>
                <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
                  暂无数据
        </Typography>
              </Box>
            )}
      </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage;

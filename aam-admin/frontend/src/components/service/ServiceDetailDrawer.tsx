/**
 * @purpose: 服务详情抽屉组件，从右侧滑出显示服务详细信息
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React, { useMemo } from 'react';
import {
  Box,
  Drawer,
  Typography,
  Divider,
  Chip,
  LinearProgress,
  Sheet,
  List,
  ListItem,
  ListItemContent,
  IconButton,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import CloseIcon from '@mui/icons-material/Close';
import ReactECharts from 'echarts-for-react';
import type { ServiceDetail, ServiceStats } from '@/types/service';

export interface ServiceDetailDrawerProps {
  open: boolean;
  service: ServiceDetail | null;
  stats: ServiceStats | null;
  onClose: () => void;
  loading?: boolean;
}

export const ServiceDetailDrawer: React.FC<ServiceDetailDrawerProps> = ({
  open,
  service,
  stats,
  onClose,
  loading = false,
}) => {
  const { mode } = useColorScheme();
  const isDark = mode === 'dark';

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

  const formatMemory = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
  };

  const chartOption = useMemo(() => {
    if (!stats) {
      return {
        title: {
          text: '暂无数据',
          left: 'center',
          top: 'middle',
          textStyle: {
            color: isDark ? '#fff' : '#000',
          },
        },
      };
    }

    return {
      tooltip: {
        trigger: 'axis',
        backgroundColor: isDark ? 'rgba(0, 0, 0, 0.8)' : 'rgba(255, 255, 255, 0.9)',
        borderColor: isDark ? '#333' : '#ddd',
        textStyle: {
          color: isDark ? '#fff' : '#000',
        },
      },
      legend: {
        data: ['CPU 使用率', '内存使用率'],
        textStyle: {
          color: isDark ? '#fff' : '#000',
        },
      },
      xAxis: {
        type: 'category',
        data: ['当前'],
        axisLabel: {
          color: isDark ? '#fff' : '#000',
        },
      },
      yAxis: {
        type: 'value',
        max: 100,
        axisLabel: {
          color: isDark ? '#fff' : '#000',
          formatter: '{value}%',
        },
      },
      series: [
        {
          name: 'CPU 使用率',
          type: 'bar',
          data: [stats.cpu_usage.toFixed(2)],
          itemStyle: {
            color: '#1976d2',
          },
        },
        {
          name: '内存使用率',
          type: 'bar',
          data: [stats.memory_usage.percent.toFixed(2)],
          itemStyle: {
            color: '#388e3c',
          },
        },
      ],
      backgroundColor: 'transparent',
    };
  }, [stats, isDark]);

  if (!service) {
    return null;
  }

  return (
    <Drawer
      open={open}
      onClose={onClose}
      anchor="right"
      size="md"
      sx={{
        '--Drawer-horizontalSize': '600px',
      }}
    >
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          height: '100%',
          bgcolor: 'background.surface',
        }}
      >
        {/* 头部 */}
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            p: 2,
            borderBottom: '1px solid',
            borderColor: 'divider',
          }}
        >
          <Typography level="title-lg">服务详情</Typography>
          <IconButton variant="plain" size="sm" onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>

        {/* 内容区域 */}
        <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
          {loading ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
                加载中...
              </Typography>
            </Box>
          ) : (
            <>
              {/* 基本信息 */}
              <Sheet
                variant="outlined"
                sx={{
                  p: 2,
                  mb: 2,
                  borderRadius: 'sm',
                  bgcolor: 'background.level1',
                }}
              >
                <Typography level="title-md" sx={{ mb: 2 }}>
                  基本信息
                </Typography>
                <List size="sm">
                  <ListItem>
                    <ListItemContent>
                      <Typography level="body-xs" sx={{ color: 'text.secondary' }}>
                        服务名称
                      </Typography>
                      <Typography level="body-sm">{service.name}</Typography>
                    </ListItemContent>
                  </ListItem>
                  <ListItem>
                    <ListItemContent>
                      <Typography level="body-xs" sx={{ color: 'text.secondary' }}>
                        状态
                      </Typography>
                      <Chip
                        color={getStatusColor(service.status)}
                        size="sm"
                        sx={{ mt: 0.5 }}
                      >
                        {getStatusText(service.status)}
                      </Chip>
                    </ListItemContent>
                  </ListItem>
                  {service.version && (
                    <ListItem>
                      <ListItemContent>
                        <Typography level="body-xs" sx={{ color: 'text.secondary' }}>
                          版本
                        </Typography>
                        <Typography level="body-sm">{service.version}</Typography>
                      </ListItemContent>
                    </ListItem>
                  )}
                  {service.container_id && (
                    <ListItem>
                      <ListItemContent>
                        <Typography level="body-xs" sx={{ color: 'text.secondary' }}>
                          容器 ID
                        </Typography>
                        <Typography level="body-sm" sx={{ fontFamily: 'monospace' }}>
                          {service.container_id}
                        </Typography>
                      </ListItemContent>
                    </ListItem>
                  )}
                  {service.image && (
                    <ListItem>
                      <ListItemContent>
                        <Typography level="body-xs" sx={{ color: 'text.secondary' }}>
                          镜像
                        </Typography>
                        <Typography level="body-sm">{service.image}</Typography>
                      </ListItemContent>
                    </ListItem>
                  )}
                  {service.uptime !== undefined && (
                    <ListItem>
                      <ListItemContent>
                        <Typography level="body-xs" sx={{ color: 'text.secondary' }}>
                          运行时间
                        </Typography>
                        <Typography level="body-sm">{formatUptime(service.uptime)}</Typography>
                      </ListItemContent>
                    </ListItem>
                  )}
                </List>
              </Sheet>

              {/* 端口映射 */}
              {service.ports.length > 0 && (
                <Sheet
                  variant="outlined"
                  sx={{
                    p: 2,
                    mb: 2,
                    borderRadius: 'sm',
                    bgcolor: 'background.level1',
                  }}
                >
                  <Typography level="title-md" sx={{ mb: 2 }}>
                    端口映射
                  </Typography>
                  <List size="sm">
                    {service.ports.map((port, index) => (
                      <ListItem key={index}>
                        <Typography level="body-sm" sx={{ fontFamily: 'monospace' }}>
                          {port}
                        </Typography>
                      </ListItem>
                    ))}
                  </List>
                </Sheet>
              )}

              {/* 资源使用 */}
              <Sheet
                variant="outlined"
                sx={{
                  p: 2,
                  mb: 2,
                  borderRadius: 'sm',
                  bgcolor: 'background.level1',
                }}
              >
                <Typography level="title-md" sx={{ mb: 2 }}>
                  资源使用
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography level="body-sm">CPU 使用率</Typography>
                    <Typography level="body-sm">{service.cpu_usage.toFixed(2)}%</Typography>
                  </Box>
                  <LinearProgress
                    value={service.cpu_usage}
                    determinate
                    color={service.cpu_usage > 80 ? 'danger' : 'primary'}
                    sx={{ height: 8, borderRadius: 'sm' }}
                  />
                </Box>
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography level="body-sm">内存使用率</Typography>
                    <Typography level="body-sm">
                      {service.memory_usage.percent.toFixed(2)}% (
                      {formatMemory(service.memory_usage.used)} /{' '}
                      {formatMemory(service.memory_usage.limit)})
                    </Typography>
                  </Box>
                  <LinearProgress
                    value={service.memory_usage.percent}
                    determinate
                    color={service.memory_usage.percent > 80 ? 'danger' : 'success'}
                    sx={{ height: 8, borderRadius: 'sm' }}
                  />
                </Box>
              </Sheet>

              {/* 资源使用图表 */}
              {stats && (
                <Sheet
                  variant="outlined"
                  sx={{
                    p: 2,
                    mb: 2,
                    borderRadius: 'sm',
                    bgcolor: 'background.level1',
                  }}
                >
                  <Typography level="title-md" sx={{ mb: 2 }}>
                    资源使用图表
                  </Typography>
                  <ReactECharts
                    option={chartOption}
                    style={{ height: '300px', width: '100%' }}
                    opts={{ renderer: 'svg' }}
                  />
                </Sheet>
              )}
            </>
          )}
        </Box>
      </Box>
    </Drawer>
  );
};

export default ServiceDetailDrawer;


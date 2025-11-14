/**
 * @purpose: 系统健康检查组件
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React from 'react';
import {
  Box,
  Sheet,
  Typography,
  Button,
  Chip,
  Stack,
  Card,
  CardContent,
  Grid,
  LinearProgress,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import RefreshIcon from '@mui/icons-material/Refresh';
import type { SystemHealthStatus } from '@/types/settings';

export interface SystemHealthProps {
  health: SystemHealthStatus | null;
  loading?: boolean;
  onRefresh: () => void;
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'healthy':
      return 'success';
    case 'warning':
      return 'warning';
    case 'unhealthy':
      return 'danger';
    default:
      return 'neutral';
  }
};

const getStatusText = (status: string) => {
  switch (status) {
    case 'healthy':
      return '健康';
    case 'warning':
      return '警告';
    case 'unhealthy':
      return '异常';
    default:
      return '未知';
  }
};

export const SystemHealth: React.FC<SystemHealthProps> = ({
  health,
  loading = false,
  onRefresh,
}) => {
  const { mode } = useColorScheme();

  if (!health) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography level="body-sm" color="neutral">
          加载中...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography level="title-lg">系统健康状态</Typography>
        <Button
          startDecorator={<RefreshIcon />}
          onClick={onRefresh}
          loading={loading}
          variant="outlined"
          size="sm"
        >
          刷新
        </Button>
      </Box>

      {/* 总体状态 */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography level="title-md">总体状态</Typography>
            <Chip color={getStatusColor(health.overall_status)} size="lg">
              {getStatusText(health.overall_status)}
            </Chip>
          </Box>
        </CardContent>
      </Card>

      {/* 各项检查 */}
      <Grid container spacing={2}>
        {Object.entries(health.checks).map(([key, check]) => (
          <Grid xs={12} sm={6} md={4} key={key}>
            <Sheet variant="outlined" sx={{ p: 2, borderRadius: 'sm' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography level="title-sm">
                  {key === 'database' ? '数据库' :
                   key === 'docker' ? 'Docker' :
                   key === 'aam_service' ? 'AAM 服务' :
                   key === 'disk' ? '磁盘空间' :
                   key === 'memory' ? '内存' : key}
                </Typography>
                <Chip size="sm" color={getStatusColor(check.status)}>
                  {getStatusText(check.status)}
                </Chip>
              </Box>
              <Typography level="body-sm" color="neutral" sx={{ mb: 1 }}>
                {check.message}
              </Typography>
              {check.details && 'percent' in check.details && (
                <Box>
                  <LinearProgress
                    determinate
                    value={check.details.percent as number}
                    color={check.status === 'healthy' ? 'success' : check.status === 'warning' ? 'warning' : 'danger'}
                    sx={{ mb: 0.5 }}
                  />
                  <Typography level="body-xs" color="neutral">
                    {check.details.percent?.toFixed(1)}% 已使用
                  </Typography>
                </Box>
              )}
            </Sheet>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default SystemHealth;


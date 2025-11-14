/**
 * @purpose: 部署状态监控组件
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  List,
  ListItem,
  Chip,
  Sheet,
  Code,
  Divider,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import type { DeploymentStatusResponse, DeploymentStatus as StatusType } from '@/types/deployment';

export interface DeploymentStatusProps {
  status: DeploymentStatusResponse | null;
  loading?: boolean;
}

export const DeploymentStatus: React.FC<DeploymentStatusProps> = ({
  status,
  loading = false,
}) => {
  const { mode } = useColorScheme();

  const getStatusColor = (status: StatusType) => {
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

  const getStatusIcon = (stepStatus: string) => {
    switch (stepStatus) {
      case 'completed':
        return <CheckCircleIcon sx={{ color: 'success.500' }} />;
      case 'failed':
        return <ErrorIcon sx={{ color: 'danger.500' }} />;
      case 'in_progress':
        return <HourglassEmptyIcon sx={{ color: 'primary.500' }} />;
      default:
        return null;
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

  if (!status) {
    return (
      <Card>
        <CardContent>
          <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
            暂无部署状态信息
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {/* 状态概览 */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography level="title-lg">部署状态</Typography>
            <Chip color={getStatusColor(status.status)} size="md" variant="soft">
              {status.status === 'success' && '成功'}
              {status.status === 'failed' && '失败'}
              {status.status === 'in_progress' && '进行中'}
              {status.status === 'pending' && '等待中'}
              {status.status === 'rolled_back' && '已回滚'}
            </Chip>
          </Box>

          {/* 进度条 */}
          {status.progress !== undefined && status.progress !== null && (
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
                  部署进度
                </Typography>
                <Typography level="body-sm" sx={{ fontWeight: 'bold' }}>
                  {status.progress.toFixed(0)}%
                </Typography>
              </Box>
              <LinearProgress
                determinate
                value={status.progress}
                sx={{
                  height: 8,
                  borderRadius: 'sm',
                }}
              />
            </Box>
          )}

          {/* 当前步骤 */}
          {status.current_step && (
            <Box>
              <Typography level="body-sm" sx={{ color: 'text.secondary', mb: 0.5 }}>
                当前步骤
              </Typography>
              <Typography level="body-md" sx={{ fontWeight: 'bold' }}>
                {status.current_step}
              </Typography>
            </Box>
          )}

          {/* 错误信息 */}
          {status.error_message && (
            <Box sx={{ mt: 2 }}>
              <Sheet
                sx={{
                  p: 2,
                  bgcolor: 'danger.50',
                  borderRadius: 'sm',
                  border: '1px solid',
                  borderColor: 'danger.200',
                }}
              >
                <Typography level="body-sm" sx={{ color: 'danger.700' }}>
                  {status.error_message}
                </Typography>
              </Sheet>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* 部署步骤 */}
      {status.steps && status.steps.length > 0 && (
        <Card>
          <CardContent>
            <Typography level="title-md" sx={{ mb: 2 }}>
              部署步骤
            </Typography>
            <List>
              {status.steps.map((step, index) => (
                <React.Fragment key={index}>
                  <ListItem>
                    <Box
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 2,
                        width: '100%',
                      }}
                    >
                      <Box sx={{ minWidth: 24 }}>
                        {getStatusIcon(step.status)}
                      </Box>
                      <Box sx={{ flex: 1 }}>
                        <Typography level="body-md">{step.name}</Typography>
                        <Typography level="body-xs" sx={{ color: 'text.secondary', mt: 0.5 }}>
                          {step.status === 'completed' && '已完成'}
                          {step.status === 'failed' && '失败'}
                          {step.status === 'in_progress' && '进行中'}
                          {step.status === 'pending' && '等待中'}
                        </Typography>
                      </Box>
                      <Chip
                        size="sm"
                        color={
                          step.status === 'completed'
                            ? 'success'
                            : step.status === 'failed'
                            ? 'danger'
                            : step.status === 'in_progress'
                            ? 'primary'
                            : 'neutral'
                        }
                        variant="soft"
                      >
                        {step.status === 'completed' && '完成'}
                        {step.status === 'failed' && '失败'}
                        {step.status === 'in_progress' && '进行中'}
                        {step.status === 'pending' && '等待'}
                      </Chip>
                    </Box>
                  </ListItem>
                  {index < status.steps.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default DeploymentStatus;


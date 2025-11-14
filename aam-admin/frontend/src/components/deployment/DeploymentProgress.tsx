/**
 * @purpose: 部署进度组件，显示部署步骤进度和实时日志
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React, { useEffect, useRef } from 'react';
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
  Divider,
  Stack,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import RadioButtonUncheckedIcon from '@mui/icons-material/RadioButtonUnchecked';
import type { DeploymentStatusResponse, DeploymentStatus as StatusType } from '@/types/deployment';

export interface DeploymentProgressProps {
  status: DeploymentStatusResponse | null;
  logs?: string[];
  loading?: boolean;
  onLogScroll?: () => void;
}

export interface DeploymentStep {
  name: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  startTime?: string;
  endTime?: string;
  duration?: number;
  details?: string;
}

export const DeploymentProgress: React.FC<DeploymentProgressProps> = ({
  status,
  logs = [],
  loading = false,
  onLogScroll,
}) => {
  const { mode } = useColorScheme();
  const logContainerRef = useRef<HTMLDivElement>(null);

  // 自动滚动到底部
  useEffect(() => {
    if (logContainerRef.current && logs.length > 0) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
      if (onLogScroll) {
        onLogScroll();
      }
    }
  }, [logs, onLogScroll]);

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

  const getStepIcon = (stepStatus: string) => {
    switch (stepStatus) {
      case 'completed':
        return <CheckCircleIcon sx={{ color: 'success.500', fontSize: 20 }} />;
      case 'failed':
        return <ErrorIcon sx={{ color: 'danger.500', fontSize: 20 }} />;
      case 'in_progress':
        return <HourglassEmptyIcon sx={{ color: 'primary.500', fontSize: 20 }} />;
      default:
        return <RadioButtonUncheckedIcon sx={{ color: 'neutral.400', fontSize: 20 }} />;
    }
  };

  const getStepColor = (stepStatus: string) => {
    switch (stepStatus) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'danger';
      case 'in_progress':
        return 'primary';
      default:
        return 'neutral';
    }
  };

  if (loading && !status) {
    return (
      <Card>
        <CardContent>
          <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
            加载部署进度...
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
            暂无部署进度信息
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const currentStepIndex = status.steps.findIndex((step) => step.status === 'in_progress');
  const completedSteps = status.steps.filter((step) => step.status === 'completed').length;
  const totalSteps = status.steps.length;
  const progress = totalSteps > 0 ? (completedSteps / totalSteps) * 100 : 0;

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {/* 进度概览 */}
      <Card>
        <CardContent>
          <Stack spacing={2}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography level="title-lg">部署进度</Typography>
              <Chip color={getStatusColor(status.status)} size="md" variant="soft">
                {status.status === 'success' && '成功'}
                {status.status === 'failed' && '失败'}
                {status.status === 'in_progress' && '进行中'}
                {status.status === 'pending' && '等待中'}
                {status.status === 'rolled_back' && '已回滚'}
              </Chip>
            </Box>

            {/* 进度条 */}
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
                  步骤进度
                </Typography>
                <Typography level="body-sm" sx={{ fontWeight: 'bold' }}>
                  {completedSteps} / {totalSteps}
                </Typography>
              </Box>
              <LinearProgress
                determinate
                value={status.progress ?? progress}
                sx={{
                  height: 8,
                  borderRadius: 'sm',
                }}
              />
            </Box>

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
            )}
          </Stack>
        </CardContent>
      </Card>

      {/* 部署步骤列表 */}
      {status.steps && status.steps.length > 0 && (
        <Card>
          <CardContent>
            <Typography level="title-md" sx={{ mb: 2 }}>
              部署步骤
            </Typography>
            <List>
              {status.steps.map((step, index) => {
                const isCurrentStep = step.status === 'in_progress';
                const isCompleted = step.status === 'completed';
                const isFailed = step.status === 'failed';

                return (
                  <React.Fragment key={index}>
                    <ListItem>
                      <Box
                        sx={{
                          display: 'flex',
                          alignItems: 'flex-start',
                          gap: 2,
                          width: '100%',
                          p: isCurrentStep ? 1.5 : 1,
                          borderRadius: 'sm',
                          bgcolor: isCurrentStep ? 'primary.50' : 'transparent',
                          border: isCurrentStep ? '1px solid' : 'none',
                          borderColor: isCurrentStep ? 'primary.200' : 'transparent',
                          transition: 'all 0.2s',
                        }}
                      >
                        <Box sx={{ minWidth: 24, pt: 0.5 }}>
                          {getStepIcon(step.status)}
                        </Box>
                        <Box sx={{ flex: 1 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                            <Typography
                              level="body-md"
                              sx={{
                                fontWeight: isCurrentStep ? 'bold' : 'normal',
                                color: isCurrentStep ? 'primary.700' : 'text.primary',
                              }}
                            >
                              {step.name}
                            </Typography>
                            {isCurrentStep && (
                              <Chip size="sm" color="primary" variant="soft">
                                进行中
                              </Chip>
                            )}
                          </Box>
                          <Typography level="body-xs" sx={{ color: 'text.secondary' }}>
                            {step.status === 'completed' && '✓ 已完成'}
                            {step.status === 'failed' && '✗ 失败'}
                            {step.status === 'in_progress' && '⟳ 进行中'}
                            {step.status === 'pending' && '○ 等待中'}
                          </Typography>
                        </Box>
                        <Chip
                          size="sm"
                          color={getStepColor(step.status)}
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
                );
              })}
            </List>
          </CardContent>
        </Card>
      )}

      {/* 实时日志 */}
      {logs.length > 0 && (
        <Card>
          <CardContent>
            <Typography level="title-md" sx={{ mb: 2 }}>
              部署日志
            </Typography>
            <Sheet
              ref={logContainerRef}
              sx={{
                p: 2,
                bgcolor: mode === 'dark' ? 'neutral.900' : 'neutral.50',
                borderRadius: 'sm',
                maxHeight: '400px',
                overflowY: 'auto',
                fontFamily: 'monospace',
                fontSize: '0.875rem',
                lineHeight: 1.6,
              }}
            >
              {logs.map((log, index) => (
                <Typography
                  key={index}
                  level="body-xs"
                  sx={{
                    color: log.includes('错误') || log.includes('失败')
                      ? 'danger.500'
                      : log.includes('成功') || log.includes('完成')
                      ? 'success.500'
                      : 'text.primary',
                    mb: 0.5,
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                  }}
                >
                  {log}
                </Typography>
              ))}
              {logs.length === 0 && (
                <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
                  暂无日志
                </Typography>
              )}
            </Sheet>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default DeploymentProgress;


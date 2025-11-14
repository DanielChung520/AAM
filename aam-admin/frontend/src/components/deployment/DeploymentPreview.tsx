/**
 * @purpose: 部署预览组件
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
  Chip,
  Alert,
  List,
  ListItem,
  Sheet,
  Code,
  Divider,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import WarningIcon from '@mui/icons-material/Warning';
import type { DeploymentPreviewResponse } from '@/types/deployment';

export interface DeploymentPreviewProps {
  preview: DeploymentPreviewResponse | null;
  loading?: boolean;
}

export const DeploymentPreview: React.FC<DeploymentPreviewProps> = ({
  preview,
  loading = false,
}) => {
  const { mode } = useColorScheme();

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
            正在预览...
          </Typography>
        </CardContent>
      </Card>
    );
  }

  if (!preview) {
    return (
      <Card>
        <CardContent>
          <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
            请先选择版本和策略进行预览
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const getStrategyText = (strategy: string) => {
    switch (strategy) {
      case 'blue_green':
        return '蓝绿部署';
      case 'rolling':
        return '滚动更新';
      case 'canary':
        return '金丝雀部署';
      default:
        return strategy;
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {/* 预览概览 */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography level="title-lg">部署预览</Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Chip size="sm" variant="soft">
                版本: {preview.version}
              </Chip>
              <Chip size="sm" variant="soft">
                {getStrategyText(preview.strategy)}
              </Chip>
            </Box>
          </Box>

          {/* 验证结果 */}
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {preview.config_valid ? (
                <CheckCircleIcon sx={{ color: 'success.500' }} />
              ) : (
                <ErrorIcon sx={{ color: 'danger.500' }} />
              )}
              <Typography level="body-md">
                配置验证: {preview.config_valid ? '通过' : '失败'}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {preview.dependencies_ok ? (
                <CheckCircleIcon sx={{ color: 'success.500' }} />
              ) : (
                <ErrorIcon sx={{ color: 'danger.500' }} />
              )}
              <Typography level="body-md">
                依赖检查: {preview.dependencies_ok ? '通过' : '失败'}
              </Typography>
            </Box>
          </Box>

          {/* 错误信息 */}
          {preview.errors && preview.errors.length > 0 && (
            <Alert color="danger" variant="soft" sx={{ mb: 2 }}>
              <Typography level="title-sm" sx={{ mb: 1 }}>
                错误信息
              </Typography>
              <List>
                {preview.errors.map((error, index) => (
                  <ListItem key={index}>
                    <Typography level="body-sm">{error}</Typography>
                  </ListItem>
                ))}
              </List>
            </Alert>
          )}

          {/* 警告信息 */}
          {preview.warnings && preview.warnings.length > 0 && (
            <Alert color="warning" variant="soft" sx={{ mb: 2 }}>
              <Typography level="title-sm" sx={{ mb: 1 }}>
                警告信息
              </Typography>
              <List>
                {preview.warnings.map((warning, index) => (
                  <ListItem key={index}>
                    <Typography level="body-sm">{warning}</Typography>
                  </ListItem>
                ))}
              </List>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* 影响分析 */}
      {preview.impact_analysis && (
        <Card>
          <CardContent>
            <Typography level="title-md" sx={{ mb: 2 }}>
              影响分析
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {preview.impact_analysis.affected_services && (
                <Box>
                  <Typography level="body-sm" sx={{ color: 'text.secondary', mb: 0.5 }}>
                    受影响服务
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {preview.impact_analysis.affected_services.map((service, index) => (
                      <Chip key={index} size="sm" variant="outlined">
                        {service}
                      </Chip>
                    ))}
                  </Box>
                </Box>
              )}
              {preview.impact_analysis.estimated_downtime !== undefined &&
                preview.impact_analysis.estimated_downtime !== null && (
                  <Box>
                    <Typography level="body-sm" sx={{ color: 'text.secondary', mb: 0.5 }}>
                      预计停机时间
                    </Typography>
                    <Typography level="body-md">
                      {preview.impact_analysis.estimated_downtime === 0
                        ? '零停机（蓝绿部署）'
                        : `${preview.impact_analysis.estimated_downtime} 秒`}
                    </Typography>
                  </Box>
                )}
              {preview.impact_analysis.rollback_available !== undefined && (
                <Box>
                  <Typography level="body-sm" sx={{ color: 'text.secondary', mb: 0.5 }}>
                    回滚可用
                  </Typography>
                  <Typography level="body-md">
                    {preview.impact_analysis.rollback_available ? '是' : '否'}
                  </Typography>
                </Box>
              )}
            </Box>
          </CardContent>
        </Card>
      )}

      {/* 配置差异 */}
      {preview.config_diff && Object.keys(preview.config_diff).length > 0 && (
        <Card>
          <CardContent>
            <Typography level="title-md" sx={{ mb: 2 }}>
              配置差异
            </Typography>
            <Sheet
              sx={{
                p: 2,
                bgcolor: 'background.level1',
                borderRadius: 'sm',
                overflow: 'auto',
              }}
            >
              <Code sx={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>
                {JSON.stringify(preview.config_diff, null, 2)}
              </Code>
            </Sheet>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default DeploymentPreview;


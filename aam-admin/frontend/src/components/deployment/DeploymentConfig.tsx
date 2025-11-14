/**
 * @purpose: 部署配置组件
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  RadioGroup,
  Radio,
  FormControl,
  FormLabel,
  Input,
  Button,
  Alert,
  Sheet,
  Divider,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import type {
  DeploymentStrategy,
  BlueGreenConfig,
  RollingUpdateConfig,
  CanaryConfig,
  DeploymentRequest,
} from '@/types/deployment';

export interface DeploymentConfigProps {
  version: string;
  onDeploy: (request: DeploymentRequest) => Promise<void>;
  onPreview?: (request: DeploymentRequest) => Promise<void>;
  loading?: boolean;
}

export const DeploymentConfig: React.FC<DeploymentConfigProps> = ({
  version,
  onDeploy,
  onPreview,
  loading = false,
}) => {
  const { mode } = useColorScheme();
  const [strategy, setStrategy] = useState<DeploymentStrategy>('blue_green');
  const [blueGreenConfig, setBlueGreenConfig] = useState<BlueGreenConfig>({
    health_check_timeout: 300,
    traffic_switch_delay: 10,
  });
  const [rollingConfig, setRollingConfig] = useState<RollingUpdateConfig>({
    max_unavailable: 1,
    max_surge: 1,
    min_ready_seconds: 30,
  });
  const [canaryConfig, setCanaryConfig] = useState<CanaryConfig>({
    initial_traffic_percent: 10,
    traffic_increment_percent: 10,
    increment_interval_seconds: 300,
    max_error_rate: 5,
    max_response_time_ms: 1000,
  });
  const [error, setError] = useState<string | null>(null);

  const handleDeploy = async () => {
    setError(null);
    try {
      const config = getConfigForStrategy();
      const request: DeploymentRequest = {
        version,
        strategy,
        config,
      };
      await onDeploy(request);
    } catch (err) {
      setError(err instanceof Error ? err.message : '部署失败');
    }
  };

  const handlePreview = async () => {
    if (!onPreview) return;
    setError(null);
    try {
      const config = getConfigForStrategy();
      const request: DeploymentRequest = {
        version,
        strategy,
        config,
        preview: true,
      };
      await onPreview(request);
    } catch (err) {
      setError(err instanceof Error ? err.message : '预览失败');
    }
  };

  const getConfigForStrategy = (): Record<string, unknown> => {
    switch (strategy) {
      case 'blue_green':
        return blueGreenConfig;
      case 'rolling':
        return rollingConfig;
      case 'canary':
        return canaryConfig;
      default:
        return {};
    }
  };

  const getStrategyDescription = (strategyType: DeploymentStrategy): string => {
    switch (strategyType) {
      case 'blue_green':
        return '创建新版本环境，健康检查通过后切换流量，零停机部署';
      case 'rolling':
        return '逐个更新实例，保持服务可用性，逐步替换旧版本';
      case 'canary':
        return '先部署少量实例，监控指标正常后逐步增加流量';
      default:
        return '';
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {error && (
        <Alert color="danger" variant="soft">
          {error}
        </Alert>
      )}

      {/* 部署策略选择 */}
      <Card>
        <CardContent>
          <Typography level="title-md" sx={{ mb: 2 }}>
            部署策略
          </Typography>
          <RadioGroup
            value={strategy}
            onChange={(e) => setStrategy(e.target.value as DeploymentStrategy)}
            orientation="vertical"
          >
            <Radio
              value="blue_green"
              label={
                <Box>
                  <Typography level="title-sm">蓝绿部署</Typography>
                  <Typography level="body-xs" sx={{ color: 'text.secondary', mt: 0.5 }}>
                    {getStrategyDescription('blue_green')}
                  </Typography>
                </Box>
              }
            />
            <Radio
              value="rolling"
              label={
                <Box>
                  <Typography level="title-sm">滚动更新</Typography>
                  <Typography level="body-xs" sx={{ color: 'text.secondary', mt: 0.5 }}>
                    {getStrategyDescription('rolling')}
                  </Typography>
                </Box>
              }
            />
            <Radio
              value="canary"
              label={
                <Box>
                  <Typography level="title-sm">金丝雀部署</Typography>
                  <Typography level="body-xs" sx={{ color: 'text.secondary', mt: 0.5 }}>
                    {getStrategyDescription('canary')}
                  </Typography>
                </Box>
              }
            />
          </RadioGroup>
        </CardContent>
      </Card>

      {/* 策略配置 */}
      <Card>
        <CardContent>
          <Typography level="title-md" sx={{ mb: 2 }}>
            策略配置
          </Typography>

          {/* 蓝绿部署配置 */}
          {strategy === 'blue_green' && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <FormControl>
                <FormLabel>健康检查超时（秒）</FormLabel>
                <Input
                  type="number"
                  value={blueGreenConfig.health_check_timeout}
                  onChange={(e) =>
                    setBlueGreenConfig({
                      ...blueGreenConfig,
                      health_check_timeout: parseInt(e.target.value, 10) || 300,
                    })
                  }
                  placeholder="300"
                />
                <Typography level="body-xs" sx={{ color: 'text.secondary', mt: 0.5 }}>
                  等待新环境健康检查通过的最大时间（10-3600秒）
                </Typography>
              </FormControl>
              <FormControl>
                <FormLabel>流量切换延迟（秒）</FormLabel>
                <Input
                  type="number"
                  value={blueGreenConfig.traffic_switch_delay}
                  onChange={(e) =>
                    setBlueGreenConfig({
                      ...blueGreenConfig,
                      traffic_switch_delay: parseInt(e.target.value, 10) || 10,
                    })
                  }
                  placeholder="10"
                />
                <Typography level="body-xs" sx={{ color: 'text.secondary', mt: 0.5 }}>
                  健康检查通过后到切换流量的延迟时间
                </Typography>
              </FormControl>
            </Box>
          )}

          {/* 滚动更新配置 */}
          {strategy === 'rolling' && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <FormControl>
                <FormLabel>最大不可用实例数</FormLabel>
                <Input
                  type="number"
                  value={rollingConfig.max_unavailable}
                  onChange={(e) =>
                    setRollingConfig({
                      ...rollingConfig,
                      max_unavailable: parseInt(e.target.value, 10) || 1,
                    })
                  }
                  placeholder="1"
                />
                <Typography level="body-xs" sx={{ color: 'text.secondary', mt: 0.5 }}>
                  更新过程中允许的最大不可用实例数量
                </Typography>
              </FormControl>
              <FormControl>
                <FormLabel>最大新增实例数</FormLabel>
                <Input
                  type="number"
                  value={rollingConfig.max_surge}
                  onChange={(e) =>
                    setRollingConfig({
                      ...rollingConfig,
                      max_surge: parseInt(e.target.value, 10) || 1,
                    })
                  }
                  placeholder="1"
                />
                <Typography level="body-xs" sx={{ color: 'text.secondary', mt: 0.5 }}>
                  更新过程中允许的最大新增实例数量
                </Typography>
              </FormControl>
              <FormControl>
                <FormLabel>最小就绪时间（秒）</FormLabel>
                <Input
                  type="number"
                  value={rollingConfig.min_ready_seconds}
                  onChange={(e) =>
                    setRollingConfig({
                      ...rollingConfig,
                      min_ready_seconds: parseInt(e.target.value, 10) || 30,
                    })
                  }
                  placeholder="30"
                />
                <Typography level="body-xs" sx={{ color: 'text.secondary', mt: 0.5 }}>
                  新实例就绪后等待的最小时间
                </Typography>
              </FormControl>
            </Box>
          )}

          {/* 金丝雀部署配置 */}
          {strategy === 'canary' && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <FormControl>
                <FormLabel>初始流量百分比</FormLabel>
                <Input
                  type="number"
                  value={canaryConfig.initial_traffic_percent}
                  onChange={(e) =>
                    setCanaryConfig({
                      ...canaryConfig,
                      initial_traffic_percent: parseInt(e.target.value, 10) || 10,
                    })
                  }
                  placeholder="10"
                />
                <Typography level="body-xs" sx={{ color: 'text.secondary', mt: 0.5 }}>
                  初始分配给新版本的流量百分比（1-50%）
                </Typography>
              </FormControl>
              <FormControl>
                <FormLabel>流量增量百分比</FormLabel>
                <Input
                  type="number"
                  value={canaryConfig.traffic_increment_percent}
                  onChange={(e) =>
                    setCanaryConfig({
                      ...canaryConfig,
                      traffic_increment_percent: parseInt(e.target.value, 10) || 10,
                    })
                  }
                  placeholder="10"
                />
                <Typography level="body-xs" sx={{ color: 'text.secondary', mt: 0.5 }}>
                  每次增加的流量百分比
                </Typography>
              </FormControl>
              <FormControl>
                <FormLabel>增量间隔时间（秒）</FormLabel>
                <Input
                  type="number"
                  value={canaryConfig.increment_interval_seconds}
                  onChange={(e) =>
                    setCanaryConfig({
                      ...canaryConfig,
                      increment_interval_seconds: parseInt(e.target.value, 10) || 300,
                    })
                  }
                  placeholder="300"
                />
                <Typography level="body-xs" sx={{ color: 'text.secondary', mt: 0.5 }}>
                  每次增加流量之间的等待时间
                </Typography>
              </FormControl>
              <FormControl>
                <FormLabel>最大错误率（%）</FormLabel>
                <Input
                  type="number"
                  value={canaryConfig.max_error_rate}
                  onChange={(e) =>
                    setCanaryConfig({
                      ...canaryConfig,
                      max_error_rate: parseFloat(e.target.value) || 5,
                    })
                  }
                  placeholder="5"
                />
                <Typography level="body-xs" sx={{ color: 'text.secondary', mt: 0.5 }}>
                  超过此错误率将自动回滚（0-100%）
                </Typography>
              </FormControl>
              <FormControl>
                <FormLabel>最大响应时间（毫秒）</FormLabel>
                <Input
                  type="number"
                  value={canaryConfig.max_response_time_ms}
                  onChange={(e) =>
                    setCanaryConfig({
                      ...canaryConfig,
                      max_response_time_ms: parseInt(e.target.value, 10) || 1000,
                    })
                  }
                  placeholder="1000"
                />
                <Typography level="body-xs" sx={{ color: 'text.secondary', mt: 0.5 }}>
                  超过此响应时间将触发警告
                </Typography>
              </FormControl>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* 操作按钮 */}
      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
        {onPreview && (
          <Button variant="outlined" onClick={handlePreview} disabled={loading}>
            预览部署
          </Button>
        )}
        <Button onClick={handleDeploy} disabled={loading}>
          {loading ? '部署中...' : '开始部署'}
        </Button>
      </Box>
    </Box>
  );
};

export default DeploymentConfig;


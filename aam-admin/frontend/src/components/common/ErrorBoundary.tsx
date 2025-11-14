/**
 * @purpose: React 错误边界组件，用于捕获子组件的错误
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Box, Typography, Button, Card } from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import RefreshIcon from '@mui/icons-material/Refresh';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  resetKeys?: Array<string | number>;
  onReset?: () => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

/**
 * 默认错误显示组件
 */
const DefaultErrorFallback: React.FC<{
  error: Error | null;
  onReset: () => void;
}> = ({ error, onReset }) => {
  const { mode } = useColorScheme();
  const isDark = mode === 'dark';

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '400px',
        p: 3,
      }}
    >
      <Card
        sx={{
          maxWidth: 600,
          width: '100%',
          bgcolor: 'background.surface',
          borderColor: 'danger.500',
          borderWidth: 2,
          borderStyle: 'solid',
        }}
      >
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 2,
            textAlign: 'center',
          }}
        >
          <ErrorOutlineIcon
            sx={{
              fontSize: 64,
              color: 'danger.500',
            }}
          />
          <Typography level="h4" sx={{ color: 'danger.500' }}>
            出现错误
          </Typography>
          <Typography level="body-md" sx={{ color: 'text.secondary' }}>
            应用程序遇到了意外错误。请尝试刷新页面或联系管理员。
          </Typography>
          {error && (
            <Box
              sx={{
                width: '100%',
                mt: 2,
                p: 2,
                bgcolor: isDark ? 'background.level1' : 'background.level2',
                borderRadius: 'sm',
                border: '1px solid',
                borderColor: 'divider',
              }}
            >
              <Typography
                level="body-sm"
                sx={{
                  fontFamily: 'monospace',
                  color: 'text.tertiary',
                  wordBreak: 'break-word',
                  whiteSpace: 'pre-wrap',
                }}
              >
                {error.message || '未知错误'}
              </Typography>
            </Box>
          )}
          <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
            <Button
              variant="solid"
              color="primary"
              startDecorator={<RefreshIcon />}
              onClick={onReset}
            >
              重试
            </Button>
            <Button
              variant="outlined"
              color="neutral"
              onClick={() => {
                window.location.reload();
              }}
            >
              刷新页面
            </Button>
          </Box>
        </Box>
      </Card>
    </Box>
  );
};

/**
 * React 错误边界类组件
 * 注意：错误边界必须是类组件，因为 React 目前不支持函数式组件的错误边界
 */
class ErrorBoundaryClass extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  private resetTimeoutId: number | null = null;

  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // 记录错误信息
    console.error('ErrorBoundary caught an error:', error, errorInfo);

    this.setState({
      errorInfo,
    });

    // 调用外部错误处理函数
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // 可以在这里发送错误报告到监控服务
    // reportErrorToService(error, errorInfo);
  }

  componentDidUpdate(prevProps: ErrorBoundaryProps) {
    const { resetKeys } = this.props;
    const { hasError } = this.state;

    // 如果 resetKeys 发生变化且当前有错误，重置错误状态
    if (hasError && resetKeys && prevProps.resetKeys) {
      const hasResetKeyChanged = resetKeys.some(
        (key, index) => key !== prevProps.resetKeys?.[index]
      );

      if (hasResetKeyChanged) {
        this.resetErrorBoundary();
      }
    }
  }

  componentWillUnmount() {
    if (this.resetTimeoutId) {
      clearTimeout(this.resetTimeoutId);
    }
  }

  resetErrorBoundary = () => {
    if (this.resetTimeoutId) {
      clearTimeout(this.resetTimeoutId);
    }

    this.resetTimeoutId = window.setTimeout(() => {
      this.setState({
        hasError: false,
        error: null,
        errorInfo: null,
      });

      if (this.props.onReset) {
        this.props.onReset();
      }
    }, 0);
  };

  render() {
    const { hasError, error } = this.state;
    const { children, fallback } = this.props;

    if (hasError) {
      if (fallback) {
        return fallback;
      }

      return (
        <DefaultErrorFallback error={error} onReset={this.resetErrorBoundary} />
      );
    }

    return children;
  }
}

/**
 * 错误边界组件（函数式组件包装器）
 */
export const ErrorBoundary: React.FC<ErrorBoundaryProps> = (props) => {
  return <ErrorBoundaryClass {...props} />;
};

export default ErrorBoundary;


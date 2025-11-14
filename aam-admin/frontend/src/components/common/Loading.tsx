/**
 * @purpose: 加载状态组件，支持全屏遮罩、局部加载和骨架屏
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React from 'react';
import { Box, CircularProgress, LinearProgress, Typography, Skeleton } from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';

export type LoadingType = 'fullscreen' | 'inline' | 'skeleton' | 'linear';

export interface LoadingProps {
  /**
   * 加载类型
   * - fullscreen: 全屏遮罩加载
   * - inline: 行内加载（适合按钮、卡片等）
   * - skeleton: 骨架屏加载
   * - linear: 线性进度条
   */
  type?: LoadingType;
  /**
   * 加载文本提示
   */
  text?: string;
  /**
   * 是否显示加载状态
   */
  loading?: boolean;
  /**
   * 骨架屏行数（仅 skeleton 类型有效）
   */
  skeletonRows?: number;
  /**
   * 自定义样式
   */
  sx?: object;
  /**
   * 子元素（用于 skeleton 类型）
   */
  children?: React.ReactNode;
}

/**
 * 全屏遮罩加载组件
 */
const FullscreenLoading: React.FC<{ text?: string }> = ({ text }) => {
  const { mode } = useColorScheme();
  const isDark = mode === 'dark';

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: isDark ? 'rgba(0, 0, 0, 0.8)' : 'rgba(255, 255, 255, 0.9)',
        zIndex: 9999,
        gap: 2,
      }}
    >
      <CircularProgress size="lg" />
      {text && (
        <Typography level="body-md" sx={{ color: 'text.primary' }}>
          {text}
        </Typography>
      )}
    </Box>
  );
};

/**
 * 行内加载组件
 */
const InlineLoading: React.FC<{ text?: string; sx?: object }> = ({ text, sx }) => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 1,
        p: 3,
        ...sx,
      }}
    >
      <CircularProgress size="md" />
      {text && (
        <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
          {text}
        </Typography>
      )}
    </Box>
  );
};

/**
 * 骨架屏加载组件
 */
const SkeletonLoading: React.FC<{
  rows?: number;
  children?: React.ReactNode;
}> = ({ rows = 3, children }) => {
  if (children) {
    return <>{children}</>;
  }

  return (
    <Box sx={{ width: '100%' }}>
      {Array.from({ length: rows }).map((_, index) => (
        <Skeleton
          key={index}
          variant="rectangular"
          height={40}
          sx={{
            mb: index < rows - 1 ? 1 : 0,
            borderRadius: 'sm',
          }}
        />
      ))}
    </Box>
  );
};

/**
 * 线性进度条加载组件
 */
const LinearLoading: React.FC<{ text?: string; sx?: object }> = ({ text, sx }) => {
  return (
    <Box sx={{ width: '100%', ...sx }}>
      {text && (
        <Typography level="body-sm" sx={{ mb: 1, color: 'text.secondary' }}>
          {text}
        </Typography>
      )}
      <LinearProgress />
    </Box>
  );
};

/**
 * 加载状态组件
 */
export const Loading: React.FC<LoadingProps> = ({
  type = 'inline',
  text,
  loading = true,
  skeletonRows = 3,
  sx,
  children,
}) => {
  if (!loading && type !== 'skeleton') {
    return null;
  }

  switch (type) {
    case 'fullscreen':
      return <FullscreenLoading text={text} />;
    case 'skeleton':
      return <SkeletonLoading rows={skeletonRows}>{children}</SkeletonLoading>;
    case 'linear':
      return <LinearLoading text={text} sx={sx} />;
    case 'inline':
    default:
      return <InlineLoading text={text} sx={sx} />;
  }
};

/**
 * 表格骨架屏组件
 */
export const TableSkeleton: React.FC<{
  rows?: number;
  columns?: number;
}> = ({ rows = 5, columns = 5 }) => {
  return (
    <Box sx={{ width: '100%' }}>
      {/* 表头骨架 */}
      <Box
        sx={{
          display: 'flex',
          gap: 2,
          mb: 2,
        }}
      >
        {Array.from({ length: columns }).map((_, index) => (
          <Skeleton
            key={index}
            variant="rectangular"
            height={40}
            sx={{
              flex: 1,
              borderRadius: 'sm',
            }}
          />
        ))}
      </Box>
      {/* 表格行骨架 */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <Box
          key={rowIndex}
          sx={{
            display: 'flex',
            gap: 2,
            mb: 1,
          }}
        >
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton
              key={colIndex}
              variant="rectangular"
              height={48}
              sx={{
                flex: 1,
                borderRadius: 'sm',
              }}
            />
          ))}
        </Box>
      ))}
    </Box>
  );
};

/**
 * 卡片骨架屏组件
 */
export const CardSkeleton: React.FC<{
  count?: number;
}> = ({ count = 1 }) => {
  return (
    <>
      {Array.from({ length: count }).map((_, index) => (
        <Box
          key={index}
          sx={{
            p: 2,
            borderRadius: 'sm',
            border: '1px solid',
            borderColor: 'divider',
            mb: index < count - 1 ? 2 : 0,
          }}
        >
          <Skeleton variant="rectangular" height={24} width="60%" sx={{ mb: 2 }} />
          <Skeleton variant="rectangular" height={16} width="100%" sx={{ mb: 1 }} />
          <Skeleton variant="rectangular" height={16} width="80%" />
        </Box>
      ))}
    </>
  );
};

export default Loading;


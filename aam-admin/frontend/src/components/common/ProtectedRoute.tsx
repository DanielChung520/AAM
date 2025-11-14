/**
 * @purpose: 路由守卫组件，保护需要认证的路由
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-15
 */
import React, { useEffect, useState, useMemo } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import { Box, CircularProgress, Typography } from '@mui/joy';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, token } = useAuthStore();
  const [isInitialized, setIsInitialized] = useState(false);

  // 初始化：等待 Zustand persist 从 localStorage 恢复状态
  useEffect(() => {
    // 立即检查 localStorage 是否有 token
    try {
      const stored = localStorage.getItem('auth-storage');
      if (stored) {
        const parsed = JSON.parse(stored);
        // 支持两种格式：{ state: { ... } } 或直接的 state 对象
        const storedToken = parsed?.state?.token || parsed?.token || null;
        const storedRefreshToken = parsed?.state?.refreshToken || parsed?.refreshToken || null;
        const storedUser = parsed?.state?.user || parsed?.user || null;
        
        // 如果 localStorage 中有 token 但 store 中没有，尝试恢复
        if (storedToken && !token) {
          console.log('🔧 ProtectedRoute: 从 localStorage 恢复 token', {
            hasToken: !!storedToken,
            hasRefreshToken: !!storedRefreshToken,
            hasUser: !!storedUser,
          });
          useAuthStore.setState({
            token: storedToken,
            isAuthenticated: true,
            refreshToken: storedRefreshToken,
            user: storedUser,
          });
        }
      }
    } catch (e) {
      console.error('❌ ProtectedRoute: 解析 localStorage 失败', e);
    }

    // 给一点时间让状态稳定
    const timer = setTimeout(() => {
      setIsInitialized(true);
    }, 50);

    return () => clearTimeout(timer);
  }, []); // 只在组件挂载时执行一次

  // 如果有 token 但 isAuthenticated 为 false，修复状态
  useEffect(() => {
    if (token && !isAuthenticated) {
      console.log('🔧 ProtectedRoute: 修复 isAuthenticated 状态');
      useAuthStore.setState({ isAuthenticated: true });
    }
  }, [token, isAuthenticated]);

  // 检查是否有有效的 token（从 store 或 localStorage）
  const hasToken = useMemo(() => {
    if (token) {
      return true;
    }

    // 如果 store 中没有，检查 localStorage
    try {
      const stored = localStorage.getItem('auth-storage');
      if (stored) {
        const parsed = JSON.parse(stored);
        // 支持两种格式：{ state: { ... } } 或直接的 state 对象
        const storedToken = parsed?.state?.token || parsed?.token || null;
        return !!storedToken;
      }
    } catch (e) {
      // 忽略解析错误
    }

    return false;
  }, [token]);

  // 记录检查结果（仅在开发环境）
  useEffect(() => {
    if (isInitialized && process.env.NODE_ENV === 'development') {
      console.log('🔍 ProtectedRoute: 认证检查', {
        token: token ? '存在' : '缺失',
        hasToken,
        isAuthenticated,
        pathname: window.location.pathname,
      });
    }
  }, [isInitialized, token, hasToken, isAuthenticated]);

  // ⚠️ 重要：所有条件返回必须在所有 hooks 之后
  // 如果还未初始化，显示加载状态
  if (!isInitialized) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
        }}
      >
        <CircularProgress />
        <Typography level="body-sm" sx={{ mt: 2, color: 'text.secondary' }}>
          正在验证身份...
        </Typography>
      </Box>
    );
  }

  // 如果没有 token，重定向到登录页
  if (!hasToken) {
    if (process.env.NODE_ENV === 'development') {
      console.warn('⚠️ ProtectedRoute: 没有找到 token，重定向到登录页', {
        pathname: window.location.pathname,
      });
    }
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;


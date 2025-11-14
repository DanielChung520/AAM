/**
 * @purpose: 登录页面
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-15
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  Typography,
  Input,
  Button,
  Alert,
  Sheet,
  FormControl,
  FormLabel,
} from '@mui/joy';
import { useAuthStore } from '@/stores/authStore';
import { authApi } from '@/services/api/auth';
import { recordLoginTime } from '@/services/api/client';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login, isAuthenticated, token } = useAuthStore();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // 如果已经登录，自动跳转到 dashboard
  useEffect(() => {
    if (isAuthenticated && token) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, token, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const response = await authApi.login({ username, password });
      console.log('登录成功，完整响应:', response);
      console.log('access_token:', response.access_token);
      console.log('refresh_token:', response.refresh_token);
      console.log('user:', response.user);
      
      // 检查响应数据是否完整
      if (!response.access_token) {
        throw new Error('登录响应中缺少 access_token');
      }
      
      if (!response.refresh_token) {
        console.warn('⚠️ 登录响应中缺少 refresh_token，这可能导致 token 刷新失败');
      }
      
      if (!response.user) {
        console.warn('⚠️ 登录响应中缺少 user 信息');
      }
      
      // 更新认证状态
      login(
        response.access_token, 
        response.refresh_token || '', 
        response.user || { 
          id: 0, 
          username: username, 
          email: '', 
          role: '' 
        }
      );
      
      // 验证状态是否已正确更新
      const store = useAuthStore.getState();
      console.log('登录后 Store 状态:', {
        token: store.token ? '存在' : '缺失',
        refreshToken: store.refreshToken ? '存在' : '缺失',
        user: store.user,
        isAuthenticated: store.isAuthenticated
      });
      
      // 记录登录时间，用于宽限期判断
      recordLoginTime();
      
      // 等待状态更新和 localStorage 持久化完成后再导航
      // 使用 Promise 确保状态已更新
      await new Promise((resolve) => {
        let attempts = 0;
        const checkState = () => {
          attempts++;
          const store = useAuthStore.getState();
          console.log(`🔄 检查状态 (尝试 ${attempts}):`, {
            token: store.token ? '存在' : '缺失',
            refreshToken: store.refreshToken ? '存在' : '缺失',
            user: store.user,
            isAuthenticated: store.isAuthenticated
          });
          
          // 检查 localStorage 是否已更新
          const stored = localStorage.getItem('auth-storage');
          if (stored) {
            try {
              const parsed = JSON.parse(stored);
              console.log('📦 localStorage 内容:', parsed);
            } catch (e) {
              console.error('解析 localStorage 失败:', e);
            }
          }
          
          if (store.token && store.isAuthenticated) {
            console.log('✅ 状态验证成功，准备导航');
            resolve(true);
          } else if (attempts < 10) {
            // 最多等待 1 秒（10次 * 100ms）
            setTimeout(checkState, 100);
          } else {
            console.warn('⚠️ 状态验证超时，但继续导航');
            resolve(true);
          }
        };
        setTimeout(checkState, 50);
      });
      
      // 最终验证
      const finalStore = useAuthStore.getState();
      if (!finalStore.token) {
        throw new Error('Token 未正确保存，请重试');
      }
      
      // 确保导航时状态已更新
      console.log('🚀 导航到 dashboard');
      navigate('/dashboard', { replace: true });
    } catch (err: unknown) {
      console.error('登录错误:', err);
      const axiosError = err as {
        response?: {
          status?: number;
          data?: { detail?: string; message?: string };
        };
        message?: string;
      };
      
      let errorMessage = '登录失败，请检查用户名和密码';
      
      if (axiosError.response) {
        if (axiosError.response.status === 401) {
          errorMessage = axiosError.response.data?.detail || '用户名或密码错误';
        } else if (axiosError.response.status === 403) {
          errorMessage = axiosError.response.data?.detail || '用户已被禁用';
        } else if (axiosError.response.status === 0 || axiosError.response.status === undefined) {
          errorMessage = '无法连接到服务器，请检查后端服务是否运行';
        } else if (axiosError.response.data?.detail) {
          errorMessage = axiosError.response.data.detail;
        } else if (axiosError.response.data?.message) {
          errorMessage = axiosError.response.data.message;
        }
      } else if (axiosError.message) {
        errorMessage = `网络错误: ${axiosError.message}`;
      }
      
      setError(errorMessage);
      setLoading(false);
    }
  };

  return (
    <Sheet
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        bgcolor: 'background.body',
      }}
    >
      <Card
        sx={{
          width: '100%',
          maxWidth: 400,
          p: 3,
        }}
      >
        <Typography level="h3" sx={{ mb: 2, textAlign: 'center' }}>
          AAM 管理系统
        </Typography>
        <Typography level="body-sm" sx={{ mb: 3, textAlign: 'center', color: 'text.secondary' }}>
          请登录以继续
        </Typography>

        {error && (
          <Alert color="danger" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit}>
          <FormControl sx={{ mb: 2 }}>
            <FormLabel>用户名</FormLabel>
            <Input
              placeholder="请输入用户名"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoFocus
              autoComplete="username"
            />
          </FormControl>
          <FormControl sx={{ mb: 3 }}>
            <FormLabel>密码</FormLabel>
            <Input
              type="password"
              placeholder="请输入密码"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </FormControl>
          <Button
            type="submit"
            fullWidth
            loading={loading}
            disabled={!username || !password}
          >
            登录
          </Button>
        </Box>
      </Card>
    </Sheet>
  );
};

export default LoginPage;


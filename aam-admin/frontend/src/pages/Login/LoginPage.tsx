/**
 * @purpose: 登录页面
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React, { useState } from 'react';
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

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuthStore();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const response = await authApi.login({ username, password });
      console.log('登录成功，响应:', response);
      
      // 更新认证状态
      login(response.access_token, response.refresh_token, response.user);
      
      // 等待状态更新后再导航
      setTimeout(() => {
        navigate('/dashboard', { replace: true });
      }, 100);
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


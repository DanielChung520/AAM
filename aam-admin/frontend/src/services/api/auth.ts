/**
 * @purpose: 认证 API 服务
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-15
 */
import apiClient from './client';
import { API_ENDPOINTS } from '@/config/api';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: {
    id: number;
    username: string;
    email: string;
    role: string;
  };
}

export interface UserInfo {
  id: number;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
}

export const authApi = {
  /**
   * 用户登录
   */
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await apiClient.post<LoginResponse>(
      API_ENDPOINTS.auth.login,
      credentials
    );
    return response.data;
  },

  /**
   * 用户登出
   */
  logout: async (): Promise<void> => {
    await apiClient.post(API_ENDPOINTS.auth.logout);
  },

  /**
   * 刷新访问令牌
   */
  refreshToken: async (refreshToken: string): Promise<{ access_token: string }> => {
    const response = await apiClient.post<{ access_token: string }>(
      API_ENDPOINTS.auth.refresh,
      { refresh_token: refreshToken }
    );
    return response.data;
  },

  /**
   * 获取当前用户信息
   */
  getCurrentUser: async (): Promise<UserInfo> => {
    const response = await apiClient.get<UserInfo>(API_ENDPOINTS.auth.me);
    return response.data;
  },

  /**
   * 修改密码
   */
  changePassword: async (oldPassword: string, newPassword: string): Promise<{ message: string }> => {
    const response = await apiClient.post<{ message: string }>(
      API_ENDPOINTS.auth.changePassword,
      {
        old_password: oldPassword,
        new_password: newPassword,
      }
    );
    return response.data;
  },

  /**
   * 更新当前用户信息
   */
  updateCurrentUser: async (updates: { email?: string }): Promise<UserInfo> => {
    const response = await apiClient.put<UserInfo>(API_ENDPOINTS.auth.me, updates);
    return response.data;
  },
};


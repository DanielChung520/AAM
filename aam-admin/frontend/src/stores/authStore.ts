/**
 * @purpose: 认证状态管理（Zustand）
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: number;
  username: string;
  email: string;
  role: string;
}

interface AuthState {
  token: string | null;
  refreshToken: string | null;
  user: User | null;
  isAuthenticated: boolean;
  login: (token: string, refreshToken: string, user: User) => void;
  logout: () => void;
  updateUser: (user: User) => void;
  updateToken: (token: string) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      refreshToken: null,
      user: null,
      isAuthenticated: false,
      login: (token, refreshToken, user) => {
        console.log('🔐 调用 login 函数，参数:', { token: token ? '存在' : '缺失', refreshToken: refreshToken ? '存在' : '缺失', user });
        set({
          token,
          refreshToken: refreshToken || null,
          user: user || null,
          isAuthenticated: !!token, // 只要有 token 就认为是已认证
        });
        // 验证设置是否成功
        setTimeout(() => {
          const currentState = useAuthStore.getState();
          console.log('✅ login 函数执行后 Store 状态:', {
            token: currentState.token ? '存在' : '缺失',
            refreshToken: currentState.refreshToken ? '存在' : '缺失',
            user: currentState.user,
            isAuthenticated: currentState.isAuthenticated
          });
        }, 0);
      },
      logout: () =>
        set({
          token: null,
          refreshToken: null,
          user: null,
          isAuthenticated: false,
        }),
      updateUser: (user) => set({ user }),
      updateToken: (token) => {
        console.log('🔄 updateToken 被调用', { token: token ? '存在' : '缺失' });
        set({ token, isAuthenticated: !!token });
      },
    }),
    {
      name: 'auth-storage',
      // 确保所有字段都被持久化
      partialize: (state) => ({
        token: state.token,
        refreshToken: state.refreshToken,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);


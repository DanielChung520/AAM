/**
 * @purpose: Axios 客户端配置
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-15
 */
import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { API_CONFIG } from '@/config/api';
import { useAuthStore } from '@/stores/authStore';

// 创建 Axios 实例
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_CONFIG.baseURL}${API_CONFIG.apiPrefix}`,
  timeout: API_CONFIG.timeout,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token 刷新锁，防止并发刷新
let isRefreshing = false;
let refreshSubscribers: Array<(token: string) => void> = [];

// 记录登录时间，用于判断是否刚登录
let loginTimestamp: number | null = null;
const LOGIN_GRACE_PERIOD = 2000; // 登录后 2 秒内的请求失败不立即跳转

// 订阅 token 刷新
const subscribeTokenRefresh = (cb: (token: string) => void) => {
  refreshSubscribers.push(cb);
};

// 通知所有订阅者 token 已刷新
const onTokenRefreshed = (token: string) => {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
};

// 导出函数供外部调用，记录登录时间
export const recordLoginTime = () => {
  loginTimestamp = Date.now();
};

// 请求拦截器
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 添加认证 token
    // 如果 config 中已经有 Authorization header，优先使用（用于刷新后的重试）
    const store = useAuthStore.getState();
    const token = store.token;
    
    // 如果 store 中没有 token，尝试从 localStorage 获取（处理 persist 恢复延迟）
    let finalToken = token;
    if (!finalToken) {
      try {
        const stored = localStorage.getItem('auth-storage');
        if (stored) {
          const parsed = JSON.parse(stored);
          // Zustand persist 的格式可能是 { state: { ... } } 或直接是状态对象
          finalToken = parsed?.state?.token || parsed?.token || null;
          const refreshToken = parsed?.state?.refreshToken || parsed?.refreshToken || null;
          const user = parsed?.state?.user || parsed?.user || null;
          
          if (finalToken && !token) {
            // 如果 localStorage 中有 token 但 store 中没有，恢复 store
            console.log('🔄 API Client: 从 localStorage 恢复 token', {
              hasToken: !!finalToken,
              hasRefreshToken: !!refreshToken,
              hasUser: !!user,
            });
            useAuthStore.setState({
              token: finalToken,
              isAuthenticated: true,
              refreshToken: refreshToken,
              user: user,
            });
            // 更新 finalToken 为恢复后的值
            finalToken = finalToken;
          }
        }
      } catch (e) {
        console.error('❌ API Client: 解析 localStorage 失败', e);
      }
    }
    
    if (finalToken && config.headers) {
      // 只有在没有设置 Authorization 时才设置，避免覆盖刷新后的新 token
      if (!config.headers.Authorization) {
        // 检查 token 是否过期（简单检查，不验证签名）
        try {
          const tokenParts = finalToken.split('.');
          if (tokenParts.length === 3) {
            const payload = JSON.parse(atob(tokenParts[1]));
            const exp = payload.exp;
            const now = Math.floor(Date.now() / 1000);
            if (exp && exp < now) {
              console.warn('⚠️ API Client: Token 已过期', {
                url: config.url,
                expiredAt: new Date(exp * 1000).toISOString(),
                now: new Date(now * 1000).toISOString(),
              });
            }
          }
        } catch (e) {
          // 忽略解析错误
        }
        
        config.headers.Authorization = `Bearer ${finalToken}`;
        // 始终输出日志，帮助调试
        console.log('✅ API Client: 添加 token 到请求', {
          url: config.url,
          method: config.method,
          hasToken: !!finalToken,
          tokenLength: finalToken.length,
          tokenPrefix: finalToken.substring(0, 30) + '...',
          headerSet: !!config.headers.Authorization,
        });
      } else {
        console.log('ℹ️ API Client: 请求已有 Authorization header，跳过设置', {
          url: config.url,
          existingHeader: config.headers.Authorization?.substring(0, 30) + '...',
        });
      }
    } else if (!finalToken && config.headers) {
      // 如果没有 token，记录警告（但不阻止请求，让后端返回 401）
      const url = config.url || '';
      // 排除登录和刷新 token 的请求
      if (!url.includes('/auth/login') && !url.includes('/auth/refresh')) {
        console.warn('⚠️ API Client: 请求缺少 token', {
          url,
          storeToken: !!token,
          localStorageToken: !!finalToken,
        });
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { 
      _retry?: boolean;
    };

    // 登录和刷新 token 的请求不应该触发 token 刷新逻辑
    const isAuthRequest = originalRequest?.url?.includes('/auth/login') || 
                          originalRequest?.url?.includes('/auth/refresh');

    // 处理 401 错误（未授权），但排除登录和刷新 token 请求
    if (
      error.response?.status === 401 && 
      !originalRequest._retry && 
      !isAuthRequest
    ) {
      const currentToken = useAuthStore.getState().token;
      const currentPath = window.location.pathname;
      
      console.warn('⚠️ API Client: 收到 401 错误', {
        url: originalRequest?.url,
        hasToken: !!currentToken,
        pathname: currentPath,
      });

      // 如果正在刷新 token，将请求加入队列等待
      if (isRefreshing) {
        console.log('🔄 API Client: Token 正在刷新，将请求加入队列');
        return new Promise((resolve) => {
          subscribeTokenRefresh((token: string) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            resolve(apiClient(originalRequest));
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      // 尝试刷新 token
      const store = useAuthStore.getState();
      let refreshToken = store.refreshToken;
      
      // 如果 store 中没有 refreshToken，尝试从 localStorage 获取
      if (!refreshToken) {
        try {
          const stored = localStorage.getItem('auth-storage');
          if (stored) {
            const parsed = JSON.parse(stored);
            refreshToken = parsed?.state?.refreshToken || null;
            if (refreshToken && !store.refreshToken) {
              console.log('🔄 API Client: 从 localStorage 恢复 refreshToken');
              useAuthStore.setState({ refreshToken });
            }
          }
        } catch (e) {
          // 忽略解析错误
        }
      }
      
      if (refreshToken) {
        try {
          // 使用独立的 axios 实例来刷新 token，避免循环拦截
          const refreshResponse = await axios.post(
            `${API_CONFIG.baseURL}${API_CONFIG.apiPrefix}/auth/refresh`,
            { refresh_token: refreshToken },
            {
              headers: {
                'Content-Type': 'application/json',
              },
            }
          );

          const { access_token } = refreshResponse.data;
          
          // 更新 store 中的 token
          useAuthStore.getState().updateToken(access_token);

          // 通知所有等待的请求
          onTokenRefreshed(access_token);

          // 确保原始请求的 headers 存在
          if (!originalRequest.headers) {
            originalRequest.headers = {} as any;
          }

          // 更新原始请求的 Authorization header
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          
          isRefreshing = false;

          // 重试原始请求（使用更新后的 headers）
          return apiClient(originalRequest);
        } catch (refreshError) {
          // 刷新失败，检查错误类型
          console.error('❌ API Client: Token 刷新失败', refreshError);
          isRefreshing = false;
          refreshSubscribers = [];
          
          const refreshAxiosError = refreshError as {
            response?: {
              status?: number;
              data?: { detail?: string; message?: string };
            };
          };
          
          // 只有在确认是认证问题时才跳转（401 或 403）
          const isAuthError = refreshAxiosError.response?.status === 401 || 
                              refreshAxiosError.response?.status === 403;
          
          // 避免在登录页面重复跳转
          if (currentPath !== '/login' && isAuthError) {
            console.warn('⚠️ API Client: Refresh token 已过期或无效，需要重新登录');
            useAuthStore.getState().logout();
            window.location.href = '/login';
          } else if (currentPath !== '/login') {
            // 如果不是认证错误（比如网络错误），不跳转，让请求失败
            console.warn('⚠️ API Client: Token 刷新失败，但可能是网络问题，不跳转');
          }
          return Promise.reject(refreshError);
        }
      } else {
        // 没有刷新 token，检查是否在登录后的宽限期内
        const isWithinGracePeriod = loginTimestamp && (Date.now() - loginTimestamp) < LOGIN_GRACE_PERIOD;
        
        // 检查当前是否有有效的 token（从 store 或 localStorage）
        let finalToken = useAuthStore.getState().token;
        if (!finalToken) {
          try {
            const stored = localStorage.getItem('auth-storage');
            if (stored) {
              const parsed = JSON.parse(stored);
              finalToken = parsed?.state?.token || null;
            }
          } catch (e) {
            // 忽略解析错误
          }
        }
        
        // 只有在确认没有 token 且不在宽限期内时才跳转
        // 如果有 token 但请求失败，可能是后端问题或网络问题，不应该立即跳转
        if (!finalToken && !isWithinGracePeriod) {
          console.warn('⚠️ API Client: 没有 token 且不在宽限期内，需要重新登录');
          isRefreshing = false;
          refreshSubscribers = [];
          // 避免在登录页面重复跳转
          if (currentPath !== '/login') {
            useAuthStore.getState().logout();
            window.location.href = '/login';
          } else {
            // 如果在登录页面，只清除状态，不跳转
            useAuthStore.getState().logout();
          }
        } else if (!finalToken && isWithinGracePeriod) {
          console.warn('⚠️ API Client: 登录后宽限期内没有 token，可能是刚登录，不跳转');
          isRefreshing = false;
          refreshSubscribers = [];
        } else {
          // 有 token 但请求失败，可能是后端问题或网络问题，不跳转
          console.warn('⚠️ API Client: 有 token 但请求返回 401，可能是后端问题或网络问题，不跳转到登录页', {
            url: originalRequest?.url,
            hasToken: !!finalToken,
          });
          isRefreshing = false;
          refreshSubscribers = [];
        }
        return Promise.reject(error);
      }
    }

    // 如果已经重试过但仍然失败，可能是真正的认证问题
    // 但不要在登录页面时自动跳转，让登录页面自己处理错误
    if (error.response?.status === 401 && originalRequest._retry) {
      const currentPath = window.location.pathname;
      // 如果不在登录页面，且错误确实是认证问题，才跳转
      if (currentPath !== '/login') {
        // 检查是否在登录后的宽限期内
        const isWithinGracePeriod = loginTimestamp && (Date.now() - loginTimestamp) < LOGIN_GRACE_PERIOD;
        
        // 检查当前是否有有效的 token
        const currentToken = useAuthStore.getState().token;
        
        // 只有在确认没有 token 或明确是认证错误时才跳转
        if (!isWithinGracePeriod && currentToken) {
          const errorDetail = (error.response?.data as any)?.detail || '';
          // 只有在明确是认证问题时才跳转（比如 token 过期、无效等）
          const isAuthError = errorDetail.includes('令牌') || 
                             errorDetail.includes('token') || 
                             errorDetail.includes('认证') || 
                             errorDetail.includes('未授权') ||
                             errorDetail.includes('expired') ||
                             errorDetail.includes('invalid');
          
          if (isAuthError) {
            console.warn('Token 刷新后仍然失败，确认是认证问题，需要重新登录');
            useAuthStore.getState().logout();
            window.location.href = '/login';
          } else {
            // 可能是其他错误（如权限问题、后端错误等），不跳转
            console.warn('Token 刷新后仍然失败，但可能是其他问题，不跳转到登录页');
          }
        } else if (!currentToken && !isWithinGracePeriod) {
          // 没有 token 且不在宽限期内，跳转
          console.warn('没有 token 且不在宽限期内，需要重新登录');
          useAuthStore.getState().logout();
          window.location.href = '/login';
        } else {
          console.warn('登录后宽限期内请求失败，可能是 token 尚未完全生效，不跳转');
        }
      }
      return Promise.reject(error);
    }

    return Promise.reject(error);
  }
);

export default apiClient;


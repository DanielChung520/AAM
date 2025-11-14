/**
 * @purpose: React 应用根组件
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React, { Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { CssVarsProvider } from '@mui/joy/styles';
import CssBaseline from '@mui/joy/CssBaseline';
import { Box, CircularProgress } from '@mui/joy';
import { theme } from './styles/theme';
import { useThemeStore } from './stores/themeStore';
import { MainLayout } from './components/layout/MainLayout';
import { ProtectedRoute } from './components/common/ProtectedRoute';
import { ErrorBoundary } from './components/common/ErrorBoundary';

// 懒加载页面组件
const LoginPage = React.lazy(() => import('./pages/Login/LoginPage'));
const DashboardPage = React.lazy(() => import('./pages/Dashboard/DashboardPage'));
const LLMProviderPage = React.lazy(() => import('./pages/LLMProvider/LLMProviderPage'));
const ServiceMonitorPage = React.lazy(() => import('./pages/ServiceMonitor/ServiceMonitorPage'));
const DeploymentPage = React.lazy(() => import('./pages/Deployment/DeploymentPage'));
const DeploymentHistoryPage = React.lazy(() => import('./pages/Deployment/DeploymentHistoryPage'));
const LogViewerPage = React.lazy(() => import('./pages/Logs/LogViewerPage'));
const SecurityPage = React.lazy(() => import('./pages/Security/SecurityPage'));
const SettingsPage = React.lazy(() => import('./pages/Settings/SettingsPage'));
const NotFoundPage = React.lazy(() => import('./pages/NotFound/NotFoundPage'));

// 加载中组件
const LoadingFallback: React.FC = () => (
  <Box
    sx={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
    }}
  >
    <CircularProgress />
  </Box>
);

const App: React.FC = () => {
  const { mode } = useThemeStore();

  // 根据 mode 确定实际的主题模式
  const actualMode = mode === 'system' 
    ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
    : mode;

  return (
    <CssVarsProvider theme={theme} defaultMode={actualMode}>
      <CssBaseline />
      <ErrorBoundary
        onError={(error, errorInfo) => {
          // 可以在这里发送错误报告到监控服务
          console.error('Application error:', error, errorInfo);
        }}
      >
        <BrowserRouter future={{ v7_relativeSplatPath: true }}>
          <Suspense fallback={<LoadingFallback />}>
            <Routes>
              {/* 登录页面 */}
              <Route path="/login" element={<LoginPage />} />
              
              {/* 受保护的路由 */}
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <MainLayout />
                  </ProtectedRoute>
                }
              >
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<DashboardPage />} />
                <Route path="llm-provider" element={<LLMProviderPage />} />
                <Route path="service-monitor" element={<ServiceMonitorPage />} />
                <Route path="deployment" element={<DeploymentPage />} />
                <Route path="deployment/history" element={<DeploymentHistoryPage />} />
                <Route path="logs" element={<LogViewerPage />} />
                <Route path="security" element={<SecurityPage />} />
                <Route path="settings" element={<SettingsPage />} />
              </Route>

              {/* 404 页面 */}
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </Suspense>
        </BrowserRouter>
      </ErrorBoundary>
    </CssVarsProvider>
  );
};

export default App;


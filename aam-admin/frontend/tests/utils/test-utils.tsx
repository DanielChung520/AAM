/**
 * @purpose: 测试工具函数
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { CssVarsProvider } from '@mui/joy/styles';
import CssBaseline from '@mui/joy/CssBaseline';
import { theme } from '@/styles/theme';

/**
 * 自定义渲染函数，包含必要的 Provider
 */
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  return (
    <CssVarsProvider theme={theme} defaultMode="light">
      <CssBaseline />
      {children}
    </CssVarsProvider>
  );
};

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options });

export * from '@testing-library/react';
export { customRender as render };


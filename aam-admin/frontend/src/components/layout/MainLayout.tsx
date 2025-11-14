/**
 * @purpose: 主布局组件，包含顶部导航栏、侧边栏和主内容区
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Box } from '@mui/joy';
import { TopNavigation } from './TopNavigation';
import { Sidebar } from './Sidebar';

export const MainLayout: React.FC = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const handleSidebarToggle = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
        bgcolor: 'background.body',
      }}
    >
      {/* 顶部导航栏 */}
      <TopNavigation />

      {/* 主体区域 */}
      <Box
        sx={{
          display: 'flex',
          flex: 1,
          mt: '64px', // 顶部导航栏高度
        }}
      >
        {/* 侧边栏 */}
        <Sidebar collapsed={sidebarCollapsed} onToggle={handleSidebarToggle} />

        {/* 主内容区 */}
        <Box
          component="main"
          sx={{
            flex: 1,
            ml: sidebarCollapsed ? '64px' : '240px', // 侧边栏宽度
            transition: 'margin-left 0.3s ease',
            p: 3,
            bgcolor: 'background.body',
            minHeight: 'calc(100vh - 64px)',
          }}
        >
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
};

export default MainLayout;


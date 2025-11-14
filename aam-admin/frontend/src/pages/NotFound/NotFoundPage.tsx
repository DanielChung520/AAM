/**
 * @purpose: 404 页面
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Typography, Button, Card } from '@mui/joy';
import HomeIcon from '@mui/icons-material/Home';

export const NotFoundPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '60vh',
        gap: 3,
      }}
    >
      <Card sx={{ p: 4, textAlign: 'center' }}>
        <Typography level="h1" sx={{ fontSize: '4rem', mb: 2 }}>
          404
        </Typography>
        <Typography level="h3" sx={{ mb: 2 }}>
          页面未找到
        </Typography>
        <Typography level="body-md" sx={{ mb: 3, color: 'text.secondary' }}>
          抱歉，您访问的页面不存在
        </Typography>
        <Button
          startDecorator={<HomeIcon />}
          onClick={() => navigate('/dashboard')}
        >
          返回首页
        </Button>
      </Card>
    </Box>
  );
};

export default NotFoundPage;


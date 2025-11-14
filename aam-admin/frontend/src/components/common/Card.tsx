/**
 * @purpose: 通用卡片组件
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React from 'react';
import { Card as JoyCard, CardProps as JoyCardProps, Box, Typography } from '@mui/joy';

export interface CardProps extends JoyCardProps {
  title?: string;
  subtitle?: string;
  actions?: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({ title, subtitle, actions, children, ...props }) => {
  return (
    <JoyCard
      {...props}
      sx={{
        bgcolor: 'background.surface',
        borderColor: 'divider',
        ...props.sx,
      }}
    >
      {(title || subtitle || actions) && (
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            mb: title || subtitle ? 2 : 0,
          }}
        >
          <Box>
            {title && (
              <Typography level="title-md" sx={{ mb: subtitle ? 0.5 : 0 }}>
                {title}
              </Typography>
            )}
            {subtitle && (
              <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
                {subtitle}
              </Typography>
            )}
          </Box>
          {actions && <Box>{actions}</Box>}
        </Box>
      )}
      {children}
    </JoyCard>
  );
};

export default Card;


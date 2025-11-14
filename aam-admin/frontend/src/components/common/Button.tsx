/**
 * @purpose: 通用按钮组件
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React from 'react';
import { Button as JoyButton, ButtonProps as JoyButtonProps } from '@mui/joy';

export interface ButtonProps extends Omit<JoyButtonProps, 'variant'> {
  variant?: 'solid' | 'outlined' | 'plain' | 'soft';
}

export const Button: React.FC<ButtonProps> = ({ variant = 'solid', ...props }) => {
  return <JoyButton variant={variant} {...props} />;
};

export default Button;


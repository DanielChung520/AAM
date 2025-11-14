/**
 * @purpose: 通用输入框组件
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React from 'react';
import { Input as JoyInput, InputProps as JoyInputProps, FormControl, FormLabel } from '@mui/joy';

export interface InputProps extends Omit<JoyInputProps, 'label'> {
  label?: string;
}

export const Input: React.FC<InputProps> = ({ label, ...props }) => {
  if (label) {
    return (
      <FormControl>
        <FormLabel>{label}</FormLabel>
        <JoyInput {...props} />
      </FormControl>
    );
  }
  return <JoyInput {...props} />;
};

export default Input;


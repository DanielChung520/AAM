/**
 * @purpose: 通用数据表格组件
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React from 'react';
import {
  Table,
  Box,
  Typography,
  Sheet,
  TableProps,
} from '@mui/joy';

export interface Column<T = Record<string, unknown>> {
  key: string;
  label: string;
  width?: string | number;
  render?: (value: unknown, row: T, index: number) => React.ReactNode;
}

export interface DataTableProps<T = Record<string, unknown>> extends Omit<TableProps, 'children'> {
  columns: Column<T>[];
  data: T[];
  loading?: boolean;
  emptyMessage?: string;
}

export const DataTable = <T extends Record<string, unknown> = Record<string, unknown>>({
  columns,
  data,
  loading = false,
  emptyMessage = '暂无数据',
  ...props
}: DataTableProps<T>) => {
  if (loading) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
          加载中...
        </Typography>
      </Box>
    );
  }

  if (data.length === 0) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
          {emptyMessage}
        </Typography>
      </Box>
    );
  }

  return (
    <Sheet
      variant="outlined"
      sx={{
        borderRadius: 'sm',
        overflow: 'auto',
        bgcolor: 'background.surface',
        borderColor: 'divider',
      }}
    >
      <Table {...props} sx={{ '--TableCell-headBackground': 'transparent', ...props.sx }}>
        <thead>
          <tr>
            {columns.map((column) => (
              <th
                key={column.key}
                style={{
                  width: column.width,
                  padding: '12px 16px',
                  textAlign: 'left',
                  fontWeight: 600,
                  fontSize: '0.875rem',
                  color: 'var(--joy-palette-text-primary)',
                  borderBottom: '1px solid var(--joy-palette-divider)',
                }}
              >
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {columns.map((column) => {
                const value = row[column.key];
                return (
                  <td
                    key={column.key}
                    style={{
                      padding: '12px 16px',
                      borderBottom: '1px solid var(--joy-palette-divider)',
                    }}
                  >
                    {column.render ? column.render(value, row, rowIndex) : value}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </Table>
    </Sheet>
  );
};

export default DataTable;


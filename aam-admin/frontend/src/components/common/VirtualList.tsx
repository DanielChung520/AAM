/**
 * @purpose: 虚拟滚动列表组件，用于优化长列表性能
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { Box } from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';

export interface VirtualListProps<T> {
  /**
   * 数据列表
   */
  items: T[];
  /**
   * 渲染每个列表项的函数
   */
  renderItem: (item: T, index: number) => React.ReactNode;
  /**
   * 每个列表项的高度（固定高度）或计算高度的函数
   */
  itemHeight: number | ((index: number) => number);
  /**
   * 容器高度
   */
  height: number;
  /**
   * 容器宽度
   */
  width?: number | string;
  /**
   * 预渲染的项目数量（在可见区域前后）
   */
  overscan?: number;
  /**
   * 自定义样式
   */
  sx?: object;
  /**
   * 滚动到指定索引的回调
   */
  onScrollToIndex?: (index: number) => void;
  /**
   * 滚动事件回调
   */
  onScroll?: (scrollTop: number) => void;
}

interface VirtualItem {
  index: number;
  top: number;
  height: number;
}

/**
 * 虚拟滚动列表组件
 */
export function VirtualList<T>({
  items,
  renderItem,
  itemHeight,
  height,
  width = '100%',
  overscan = 3,
  sx,
  onScrollToIndex,
  onScroll,
}: VirtualListProps<T>) {
  const { mode } = useColorScheme();
  const containerRef = useRef<HTMLDivElement>(null);
  const [scrollTop, setScrollTop] = useState(0);
  const [containerHeight, setContainerHeight] = useState(height);

  // 计算每个项目的位置和高度
  const virtualItems = useMemo<VirtualItem[]>(() => {
    const result: VirtualItem[] = [];
    let top = 0;

    for (let i = 0; i < items.length; i++) {
      const height = typeof itemHeight === 'function' ? itemHeight(i) : itemHeight;
      result.push({
        index: i,
        top,
        height,
      });
      top += height;
    }

    return result;
  }, [items, itemHeight]);

  // 计算总高度
  const totalHeight = useMemo(() => {
    if (virtualItems.length === 0) return 0;
    const lastItem = virtualItems[virtualItems.length - 1];
    return lastItem.top + lastItem.height;
  }, [virtualItems]);

  // 计算可见范围
  const visibleRange = useMemo(() => {
    const start = scrollTop;
    const end = scrollTop + containerHeight;

    let startIndex = 0;
    let endIndex = virtualItems.length - 1;

    // 找到第一个可见项
    for (let i = 0; i < virtualItems.length; i++) {
      const item = virtualItems[i];
      if (item.top + item.height >= start) {
        startIndex = Math.max(0, i - overscan);
        break;
      }
    }

    // 找到最后一个可见项
    for (let i = startIndex; i < virtualItems.length; i++) {
      const item = virtualItems[i];
      if (item.top >= end) {
        endIndex = Math.min(virtualItems.length - 1, i + overscan);
        break;
      }
    }

    // 如果滚动到底部，确保显示最后几项
    if (scrollTop + containerHeight >= totalHeight) {
      endIndex = virtualItems.length - 1;
      startIndex = Math.max(0, endIndex - Math.ceil(containerHeight / (typeof itemHeight === 'function' ? itemHeight(0) : itemHeight)) - overscan);
    }

    return { startIndex, endIndex };
  }, [scrollTop, containerHeight, virtualItems, totalHeight, overscan, itemHeight]);

  // 处理滚动事件
  const handleScroll = useCallback(
    (e: React.UIEvent<HTMLDivElement>) => {
      const newScrollTop = e.currentTarget.scrollTop;
      setScrollTop(newScrollTop);
      if (onScroll) {
        onScroll(newScrollTop);
      }
    },
    [onScroll]
  );

  // 监听容器高度变化
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        setContainerHeight(entry.contentRect.height);
      }
    });

    resizeObserver.observe(container);

    return () => {
      resizeObserver.disconnect();
    };
  }, []);

  // 滚动到指定索引
  const scrollToIndex = useCallback(
    (index: number) => {
      const container = containerRef.current;
      if (!container || index < 0 || index >= virtualItems.length) return;

      const item = virtualItems[index];
      container.scrollTop = item.top;

      if (onScrollToIndex) {
        onScrollToIndex(index);
      }
    },
    [virtualItems, onScrollToIndex]
  );

  // 暴露滚动方法
  useEffect(() => {
    if (containerRef.current) {
      (containerRef.current as any).scrollToIndex = scrollToIndex;
    }
  }, [scrollToIndex]);

  // 渲染可见项
  const visibleItems = useMemo(() => {
    const renderedItems: React.ReactNode[] = [];
    for (let i = visibleRange.startIndex; i <= visibleRange.endIndex; i++) {
      const item = virtualItems[i];
      renderedItems.push(
        <Box
          key={i}
          sx={{
            position: 'absolute',
            top: item.top,
            left: 0,
            right: 0,
            height: item.height,
          }}
        >
          {renderItem(items[i], i)}
        </Box>
      );
    }
    return renderedItems;
  }, [visibleRange, virtualItems, renderItem, items]);

  return (
    <Box
      ref={containerRef}
      onScroll={handleScroll}
      sx={{
        height,
        width,
        overflow: 'auto',
        position: 'relative',
        ...sx,
      }}
    >
      {/* 占位容器，用于保持总高度 */}
      <Box
        sx={{
          height: totalHeight,
          position: 'relative',
        }}
      >
        {visibleItems}
      </Box>
    </Box>
  );
}

export default VirtualList;


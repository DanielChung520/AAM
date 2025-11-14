/**
 * @purpose: WebSocket Hook，用于管理日志流连接（优化版：支持连接池、消息队列、自动重连）
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import { useEffect, useRef, useState, useCallback } from 'react';
import { API_CONFIG, API_ENDPOINTS } from '@/config/api';
import type { WebSocketLogMessage } from '@/types/logs';

export interface UseWebSocketOptions {
  containerName?: string;
  since?: string;
  until?: string;
  filterLevel?: string;
  filterText?: string;
  autoConnect?: boolean;
  onMessage?: (message: WebSocketLogMessage) => void;
  onError?: (error: Event) => void;
  onClose?: () => void;
  /**
   * 重连延迟（毫秒）
   */
  reconnectDelay?: number;
  /**
   * 最大重连次数
   */
  maxReconnectAttempts?: number;
  /**
   * 消息队列最大长度
   */
  maxQueueSize?: number;
  /**
   * 是否启用消息队列（在连接断开时缓存消息）
   */
  enableMessageQueue?: boolean;
}

// WebSocket 连接池（全局管理）
const connectionPool = new Map<string, WebSocket>();

// 默认配置
const DEFAULT_RECONNECT_DELAY = 3000; // 3 秒
const DEFAULT_MAX_RECONNECT_ATTEMPTS = 5;
const DEFAULT_MAX_QUEUE_SIZE = 1000;

export const useWebSocket = (options: UseWebSocketOptions = {}) => {
  const {
    containerName,
    since,
    until,
    filterLevel,
    filterText,
    autoConnect = false,
    onMessage,
    onError,
    onClose,
    reconnectDelay = DEFAULT_RECONNECT_DELAY,
    maxReconnectAttempts = DEFAULT_MAX_RECONNECT_ATTEMPTS,
    maxQueueSize = DEFAULT_MAX_QUEUE_SIZE,
    enableMessageQueue = true,
  } = options;

  const [connected, setConnected] = useState(false);
  const [paused, setPaused] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const messageQueueRef = useRef<WebSocketLogMessage[]>([]);
  const isReconnectingRef = useRef(false);

  // 生成连接唯一标识
  const connectionKey = useCallback(() => {
    if (!containerName) return null;
    const params = [containerName, since, until, filterLevel, filterText]
      .filter(Boolean)
      .join('|');
    return `ws:${params}`;
  }, [containerName, since, until, filterLevel, filterText]);

  const buildWebSocketUrl = useCallback(() => {
    if (!containerName) return null;

    // 构建 WebSocket URL
    let wsBaseUrl = API_CONFIG.wsURL;
    if (wsBaseUrl.startsWith('http://')) {
      wsBaseUrl = wsBaseUrl.replace('http://', 'ws://');
    } else if (wsBaseUrl.startsWith('https://')) {
      wsBaseUrl = wsBaseUrl.replace('https://', 'wss://');
    } else if (!wsBaseUrl.startsWith('ws://') && !wsBaseUrl.startsWith('wss://')) {
      // 如果没有协议，默认使用 ws://
      wsBaseUrl = `ws://${wsBaseUrl}`;
    }

    let url = `${wsBaseUrl}${API_ENDPOINTS.logs.ws(containerName)}`;

    const params = new URLSearchParams();
    if (since) params.append('since', since);
    if (until) params.append('until', until);
    if (filterLevel) params.append('filter_level', filterLevel);
    if (filterText) params.append('filter_text', filterText);

    const queryString = params.toString();
    if (queryString) {
      url += `?${queryString}`;
    }

    return url;
  }, [containerName, since, until, filterLevel, filterText]);

  // 处理消息队列
  const processMessageQueue = useCallback(() => {
    if (!onMessage || messageQueueRef.current.length === 0) return;

    const messages = [...messageQueueRef.current];
    messageQueueRef.current = [];

    messages.forEach((message) => {
      try {
        onMessage(message);
      } catch (err) {
        console.error('Error processing queued message:', err);
      }
    });
  }, [onMessage]);

  // 添加消息到队列
  const enqueueMessage = useCallback(
    (message: WebSocketLogMessage) => {
      if (!enableMessageQueue) return;

      messageQueueRef.current.push(message);

      // 限制队列大小
      if (messageQueueRef.current.length > maxQueueSize) {
        messageQueueRef.current.shift();
      }
    },
    [enableMessageQueue, maxQueueSize]
  );

  const connect = useCallback(() => {
    if (!containerName) {
      setError(new Error('容器名称未指定'));
      return;
    }

    const url = buildWebSocketUrl();
    if (!url) {
      setError(new Error('无法构建 WebSocket URL'));
      return;
    }

    const key = connectionKey();
    if (!key) return;

    // 检查连接池中是否已有连接
    const existingConnection = connectionPool.get(key);
    if (existingConnection && existingConnection.readyState === WebSocket.OPEN) {
      wsRef.current = existingConnection;
      setConnected(true);
      setError(null);
      return;
    }

    // 如果已有连接，先关闭
    if (wsRef.current) {
      wsRef.current.close();
    }

    // 如果正在重连，取消重连
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;
      connectionPool.set(key, ws);

      ws.onopen = () => {
        setConnected(true);
        setError(null);
        reconnectAttemptsRef.current = 0;
        isReconnectingRef.current = false;

        // 连接成功后处理消息队列
        if (enableMessageQueue && messageQueueRef.current.length > 0) {
          processMessageQueue();
        }
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketLogMessage = JSON.parse(event.data);
          
          if (connected && onMessage) {
            // 连接正常，直接处理消息
            onMessage(message);
          } else if (enableMessageQueue) {
            // 连接未就绪，加入消息队列
            enqueueMessage(message);
          }
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };

      ws.onerror = (event) => {
        const error = new Error('WebSocket 连接错误');
        setError(error);
        if (onError) {
          onError(event);
        }
      };

      ws.onclose = (event) => {
        setConnected(false);
        
        // 从连接池中移除
        connectionPool.delete(key);

        if (onClose) {
          onClose();
        }

        // 自动重连（仅在非正常关闭时）
        if (!event.wasClean && !isReconnectingRef.current) {
          if (reconnectAttemptsRef.current < maxReconnectAttempts) {
            isReconnectingRef.current = true;
            reconnectAttemptsRef.current += 1;
            
            reconnectTimeoutRef.current = setTimeout(() => {
              isReconnectingRef.current = false;
              connect();
            }, reconnectDelay * reconnectAttemptsRef.current); // 指数退避
          } else {
            setError(new Error('WebSocket 重连失败，已达到最大重试次数'));
            isReconnectingRef.current = false;
          }
        } else {
          isReconnectingRef.current = false;
        }
      };
    } catch (err) {
      setError(err as Error);
      isReconnectingRef.current = false;
    }
  }, [
    containerName,
    buildWebSocketUrl,
    connectionKey,
    connected,
    onMessage,
    onError,
    onClose,
    reconnectDelay,
    maxReconnectAttempts,
    enableMessageQueue,
    processMessageQueue,
    enqueueMessage,
  ]);

  const disconnect = useCallback(() => {
    const key = connectionKey();
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    if (key) {
      connectionPool.delete(key);
    }

    setConnected(false);
    reconnectAttemptsRef.current = maxReconnectAttempts; // 阻止自动重连
    isReconnectingRef.current = false;
    messageQueueRef.current = []; // 清空消息队列
  }, [connectionKey, maxReconnectAttempts]);

  const pause = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'pause' }));
      setPaused(true);
    }
  }, []);

  const resume = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'resume' }));
      setPaused(false);
    }
  }, []);

  // 清理函数：组件卸载时断开连接
  useEffect(() => {
    if (autoConnect && containerName) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, containerName, connect, disconnect]);

  return {
    connected,
    paused,
    error,
    connect,
    disconnect,
    pause,
    resume,
    /**
     * 获取消息队列长度
     */
    queueLength: messageQueueRef.current.length,
    /**
     * 清空消息队列
     */
    clearQueue: () => {
      messageQueueRef.current = [];
    },
  };
};


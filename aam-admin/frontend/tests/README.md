# 前端测试说明

## 测试框架

- **Vitest**: 快速测试框架（Vite 原生支持）
- **React Testing Library**: React 组件测试库
- **jsdom**: DOM 环境模拟

## 安装依赖

```bash
cd frontend
npm install
```

## 运行测试

### 运行所有测试

```bash
npm test
```

### 运行测试（监听模式）

```bash
npm test -- --watch
```

### 运行测试 UI

```bash
npm run test:ui
```

### 运行测试并生成覆盖率报告

```bash
npm run test:coverage
```

## 测试结构

```
tests/
├── setup.ts                # 测试环境设置
├── utils/
│   └── test-utils.tsx      # 测试工具函数
├── components/
│   └── security/
│       └── TokenList.test.tsx  # Token 列表组件测试
└── hooks/
    └── useSecurity.test.ts     # useSecurity Hook 测试
```

## 测试工具

### render

自定义的 `render` 函数，包含必要的 Provider（CssVarsProvider、CssBaseline）。

```typescript
import { render, screen } from '@/tests/utils/test-utils';

render(<MyComponent />);
```

## 注意事项

1. 所有组件测试都需要使用 `@/tests/utils/test-utils` 中的 `render` 函数
2. 测试会自动清理 DOM
3. `window.matchMedia` 和 `navigator.clipboard` 已自动 mock


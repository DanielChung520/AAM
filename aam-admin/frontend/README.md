# AAM Admin Frontend

AAM 管理系统的前端应用，基于 React + TypeScript + Joy UI 构建。

## 技术栈

- React 18+
- TypeScript 5+
- React Joy UI
- Zustand (状态管理)
- React Router 6.x
- Axios (HTTP 客户端)
- ECharts (图表)
- Vite (构建工具)

## 项目结构

```
frontend/
├── src/
│   ├── components/             # 可复用 UI 组件
│   │   ├── common/            # 通用组件
│   │   ├── layout/            # 布局组件
│   │   ├── charts/            # 图表组件
│   │   ├── forms/             # 表单组件
│   │   └── tables/            # 表格组件
│   ├── pages/                 # 页面组件
│   ├── services/              # 业务服务层
│   │   ├── api/               # API 调用封装
│   │   └── websocket.ts
│   ├── stores/                # 状态管理（Zustand）
│   ├── hooks/                 # 自定义 Hooks
│   ├── types/                 # TypeScript 类型定义
│   ├── utils/                 # 工具函数
│   ├── styles/                # 样式文件
│   ├── config/                # 配置文件
│   ├── App.tsx
│   └── main.tsx
├── public/                     # 静态资源
└── tests/                     # 测试文件
```

## 开发环境设置

1. 安装依赖：
```bash
npm install
```

2. 运行开发服务器：
```bash
npm run dev
```

3. 构建生产版本：
```bash
npm run build
```

## 开发规范

请严格遵守 `.cursor/rules/frontend-development-rule.mdc` 中的开发规范：

- 必须使用 TypeScript 严格模式
- 必须支持深色模式
- 必须使用 Joy UI 主题变量
- 所有组件必须包含文件头注释
- 文件位置必须符合规范


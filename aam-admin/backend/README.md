# AAM Admin Backend

AAM 管理系统的后端服务，基于 FastAPI 构建。

## 技术栈

- FastAPI 0.104+
- Python 3.11+
- PostgreSQL 15+
- SQLAlchemy
- Alembic
- docker-py

## 项目结构

```
backend/
├── src/
│   ├── main.py                 # FastAPI 应用入口
│   ├── core/                   # 核心功能模块
│   │   ├── config.py           # 配置管理
│   │   └── services/           # 核心服务
│   ├── api/                    # API 路由
│   │   ├── dependencies/       # 依赖注入
│   │   ├── middleware/         # 中间件
│   │   └── routers/            # 路由模块
│   ├── models/                 # 数据模型
│   └── infrastructure/         # 基础设施
├── alembic/                    # 数据库迁移
├── tests/                      # 测试文件
└── requirements.txt            # Python 依赖
```

## 开发环境设置

1. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行开发服务器：
```bash
uvicorn src.main:app --reload
```

## 数据库迁移

```bash
# 创建迁移
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head
```


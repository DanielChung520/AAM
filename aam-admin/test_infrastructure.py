#!/usr/bin/env python3
"""
@purpose: 测试基础设施脚本
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""
import os
import sys
from pathlib import Path

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✓{Colors.END} {message}")

def print_error(message):
    print(f"{Colors.RED}✗{Colors.END} {message}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠{Colors.END} {message}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ{Colors.END} {message}")

def test_backend_structure():
    """测试后端目录结构"""
    print_info("测试后端目录结构...")
    backend_path = Path("backend")
    
    required_dirs = [
        "backend/src",
        "backend/src/core",
        "backend/src/api",
        "backend/src/models",
        "backend/src/infrastructure",
        "backend/alembic",
        "backend/tests",
    ]
    
    required_files = [
        "backend/src/main.py",
        "backend/src/core/config.py",
        "backend/src/models/database.py",
        "backend/src/infrastructure/database.py",
        "backend/requirements.txt",
        "backend/alembic.ini",
        "backend/alembic/env.py",
        "backend/Dockerfile.dev",
    ]
    
    all_passed = True
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print_success(f"目录存在: {dir_path}")
        else:
            print_error(f"目录缺失: {dir_path}")
            all_passed = False
    
    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"文件存在: {file_path}")
        else:
            print_error(f"文件缺失: {file_path}")
            all_passed = False
    
    return all_passed

def test_frontend_structure():
    """测试前端目录结构"""
    print_info("测试前端目录结构...")
    frontend_path = Path("frontend")
    
    required_dirs = [
        "frontend/src",
        "frontend/src/components",
        "frontend/src/pages",
        "frontend/src/services",
        "frontend/src/stores",
        "frontend/src/hooks",
        "frontend/src/types",
        "frontend/src/utils",
        "frontend/src/styles",
        "frontend/src/config",
    ]
    
    required_files = [
        "frontend/src/main.tsx",
        "frontend/src/App.tsx",
        "frontend/src/styles/theme.ts",
        "frontend/package.json",
        "frontend/tsconfig.json",
        "frontend/vite.config.ts",
        "frontend/index.html",
    ]
    
    all_passed = True
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print_success(f"目录存在: {dir_path}")
        else:
            print_error(f"目录缺失: {dir_path}")
            all_passed = False
    
    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"文件存在: {file_path}")
        else:
            print_error(f"文件缺失: {file_path}")
            all_passed = False
    
    return all_passed

def test_backend_imports():
    """测试后端导入"""
    print_info("测试后端 Python 导入...")
    
    try:
        # 添加 backend 到路径
        sys.path.insert(0, str(Path("backend").absolute()))
        
        # 测试配置导入
        from src.core.config import get_settings
        settings = get_settings()
        print_success("配置模块导入成功")
        print_info(f"  应用名称: {settings.app.app_name}")
        print_info(f"  应用版本: {settings.app.app_version}")
        print_info(f"  API 端口: {settings.api.api_port}")
        
        # 测试数据库模型导入
        from src.models.database import Base, User, TokenRecord, AuditLog
        print_success("数据库模型导入成功")
        
        return True
    except Exception as e:
        print_error(f"后端导入失败: {e}")
        return False

def test_docker_compose():
    """测试 Docker Compose 配置"""
    print_info("测试 Docker Compose 配置...")
    
    compose_file = Path("docker-compose.dev.yml")
    if not compose_file.exists():
        print_error("docker-compose.dev.yml 不存在")
        return False
    
    print_success("docker-compose.dev.yml 存在")
    
    # 检查 YAML 语法（简单检查）
    try:
        import yaml
        with open(compose_file, 'r') as f:
            config = yaml.safe_load(f)
        
        if 'services' in config:
            print_success("Docker Compose 配置格式正确")
            services = list(config['services'].keys())
            print_info(f"  服务列表: {', '.join(services)}")
            return True
        else:
            print_error("Docker Compose 配置缺少 services 部分")
            return False
    except ImportError:
        print_warning("PyYAML 未安装，跳过 YAML 语法检查")
        return True
    except Exception as e:
        print_error(f"Docker Compose 配置解析失败: {e}")
        return False

def test_file_content():
    """测试关键文件内容"""
    print_info("测试关键文件内容...")
    
    # 检查 main.py 是否有基本结构
    main_py = Path("backend/src/main.py")
    if main_py.exists():
        content = main_py.read_text()
        if "FastAPI" in content and "app = FastAPI" in content:
            print_success("main.py 包含 FastAPI 应用")
        else:
            print_error("main.py 缺少 FastAPI 应用定义")
            return False
    
    # 检查 App.tsx 是否有基本结构
    app_tsx = Path("frontend/src/App.tsx")
    if app_tsx.exists():
        content = app_tsx.read_text()
        if "CssVarsProvider" in content and "theme" in content:
            print_success("App.tsx 包含 Joy UI 主题配置")
        else:
            print_warning("App.tsx 可能缺少 Joy UI 配置")
    
    return True

def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("AAM Admin 基础设施测试")
    print("="*60 + "\n")
    
    results = []
    
    # 测试目录结构
    results.append(("后端目录结构", test_backend_structure()))
    print()
    results.append(("前端目录结构", test_frontend_structure()))
    print()
    
    # 测试导入
    results.append(("后端导入", test_backend_imports()))
    print()
    
    # 测试 Docker Compose
    results.append(("Docker Compose 配置", test_docker_compose()))
    print()
    
    # 测试文件内容
    results.append(("文件内容检查", test_file_content()))
    print()
    
    # 总结
    print("="*60)
    print("测试结果总结")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "通过" if result else "失败"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}{'✓' if result else '✗'}{Colors.END} {name}: {status}")
    
    print()
    print(f"总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print_success("所有测试通过！基础设施配置正确。")
        return 0
    else:
        print_error(f"有 {total - passed} 项测试失败，请检查上述错误。")
        return 1

if __name__ == "__main__":
    sys.exit(main())


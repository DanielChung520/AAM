#!/usr/bin/env python3
"""
@purpose: 模型配置管理工具
@author: DanielChung and AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Optional

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config.model_config_loader import get_model_config_loader
from src.core.interfaces.i_model_provider import ModelProviderType


def list_all_models(provider_type: Optional[str] = None, enabled_only: bool = False):
    """列出所有模型"""
    loader = get_model_config_loader()
    
    if provider_type:
        try:
            provider = ModelProviderType(provider_type.lower())
            models_dict = loader.list_all_models(provider)
        except ValueError:
            print(f"❌ 无效的 Provider 类型: {provider_type}")
            print(f"支持的类型: {[t.value for t in ModelProviderType]}")
            return
    else:
        models_dict = loader.list_all_models()
    
    if not models_dict:
        print("未找到任何模型配置")
        return
    
    for provider_key, models in models_dict.items():
        print(f"\n{'=' * 60}")
        print(f"Provider: {provider_key.upper()}")
        print(f"{'=' * 60}")
        
        if enabled_only:
            models = [m for m in models if m.enabled]
            print(f"启用的模型 ({len(models)} 个):")
        else:
            print(f"所有模型 ({len(models)} 个):")
        
        if not models:
            print("  (无)")
            continue
        
        for model in models:
            status = "✅ 启用" if model.enabled else "❌ 禁用"
            print(f"\n  {status} - {model.display_name or model.model_name}")
            print(f"    模型名称: {model.model_name}")
            print(f"    优先级: {model.priority}")
            print(f"    max_tokens: {model.max_tokens}")
            print(f"    temperature: {model.temperature}")
            if model.description:
                print(f"    描述: {model.description}")


def validate_config():
    """验证配置文件"""
    loader = get_model_config_loader()
    
    print("验证模型配置文件...")
    print(f"配置文件路径: {loader.config_path}")
    
    if not loader.config_path.exists():
        print("❌ 配置文件不存在")
        return False
    
    is_valid = loader.validate_config()
    
    if is_valid:
        print("✅ 配置文件格式正确")
        
        # 统计信息
        all_models = loader.list_all_models()
        total_models = sum(len(models) for models in all_models.values())
        enabled_models = sum(
            len([m for m in models if m.enabled])
            for models in all_models.values()
        )
        
        print(f"\n统计信息:")
        print(f"  Provider 数量: {len(all_models)}")
        print(f"  总模型数: {total_models}")
        print(f"  启用模型数: {enabled_models}")
        print(f"  禁用模型数: {total_models - enabled_models}")
    else:
        print("❌ 配置文件验证失败，请检查错误信息")
    
    return is_valid


def toggle_model(provider_type: str, model_name: str, enable: bool):
    """启用/禁用模型"""
    try:
        provider = ModelProviderType(provider_type.lower())
    except ValueError:
        print(f"❌ 无效的 Provider 类型: {provider_type}")
        return False
    
    loader = get_model_config_loader()
    model_config = loader.get_model_config(provider, model_name)
    
    if not model_config:
        print(f"❌ 未找到模型: {provider_type}/{model_name}")
        return False
    
    # 读取配置文件
    config_path = loader.config_path
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 更新模型状态
    provider_key = provider.value
    if provider_key not in data:
        print(f"❌ Provider {provider_key} 不在配置文件中")
        return False
    
    for model in data[provider_key]["models"]:
        if model["model_name"] == model_name:
            model["enabled"] = enable
            break
    else:
        print(f"❌ 在配置文件中未找到模型: {model_name}")
        return False
    
    # 保存配置文件
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # 重新加载配置
    loader.reload_configs()
    
    action = "启用" if enable else "禁用"
    print(f"✅ 已{action}模型: {provider_type}/{model_name}")
    return True


def set_priority(provider_type: str, model_name: str, priority: int):
    """设置模型优先级"""
    try:
        provider = ModelProviderType(provider_type.lower())
    except ValueError:
        print(f"❌ 无效的 Provider 类型: {provider_type}")
        return False
    
    loader = get_model_config_loader()
    model_config = loader.get_model_config(provider, model_name)
    
    if not model_config:
        print(f"❌ 未找到模型: {provider_type}/{model_name}")
        return False
    
    # 读取配置文件
    config_path = loader.config_path
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 更新模型优先级
    provider_key = provider.value
    if provider_key not in data:
        print(f"❌ Provider {provider_key} 不在配置文件中")
        return False
    
    for model in data[provider_key]["models"]:
        if model["model_name"] == model_name:
            model["priority"] = priority
            break
    else:
        print(f"❌ 在配置文件中未找到模型: {model_name}")
        return False
    
    # 保存配置文件
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # 重新加载配置
    loader.reload_configs()
    
    print(f"✅ 已设置模型优先级: {provider_type}/{model_name} -> {priority}")
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="模型配置管理工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # list 命令
    list_parser = subparsers.add_parser("list", help="列出所有模型")
    list_parser.add_argument(
        "--provider",
        type=str,
        help="只列出指定 Provider 的模型"
    )
    list_parser.add_argument(
        "--enabled-only",
        action="store_true",
        help="只列出启用的模型"
    )
    
    # validate 命令
    subparsers.add_parser("validate", help="验证配置文件")
    
    # enable 命令
    enable_parser = subparsers.add_parser("enable", help="启用模型")
    enable_parser.add_argument("provider", type=str, help="Provider 类型")
    enable_parser.add_argument("model", type=str, help="模型名称")
    
    # disable 命令
    disable_parser = subparsers.add_parser("disable", help="禁用模型")
    disable_parser.add_argument("provider", type=str, help="Provider 类型")
    disable_parser.add_argument("model", type=str, help="模型名称")
    
    # priority 命令
    priority_parser = subparsers.add_parser("priority", help="设置模型优先级")
    priority_parser.add_argument("provider", type=str, help="Provider 类型")
    priority_parser.add_argument("model", type=str, help="模型名称")
    priority_parser.add_argument("priority", type=int, help="优先级（数字越小优先级越高）")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "list":
        list_all_models(args.provider, args.enabled_only)
    elif args.command == "validate":
        validate_config()
    elif args.command == "enable":
        toggle_model(args.provider, args.model, enable=True)
    elif args.command == "disable":
        toggle_model(args.provider, args.model, enable=False)
    elif args.command == "priority":
        set_priority(args.provider, args.model, args.priority)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()


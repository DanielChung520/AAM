"""
@purpose: 训练模块工具函数
@author: DanielChung
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import json
from typing import Dict, List, Optional


def parse_instruction_jsonl(file_path: str) -> List[Dict]:
    """
    解析 Instruction JSONL 文件

    Args:
        file_path: JSONL 文件路径

    Returns:
        样本列表
    """
    samples = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                sample = json.loads(line)
                samples.append(sample)
            except json.JSONDecodeError as e:
                print(f"解析 JSON 失败: {e}, 行: {line[:100]}")
                continue

    return samples


def validate_training_sample(sample: Dict) -> bool:
    """
    验证训练样本格式

    Args:
        sample: 训练样本字典

    Returns:
        是否有效
    """
    required_fields = ["instruction", "input", "output"]
    return all(field in sample for field in required_fields)


def calculate_data_stats(samples: List[Dict]) -> Dict:
    """
    计算数据统计信息

    Args:
        samples: 样本列表

    Returns:
        统计信息字典
    """
    total_samples = len(samples)
    avg_input_length = sum(len(s.get("input", "")) for s in samples) / total_samples if total_samples > 0 else 0
    avg_output_length = sum(len(s.get("output", "")) for s in samples) / total_samples if total_samples > 0 else 0

    return {
        "total_samples": total_samples,
        "avg_input_length": round(avg_input_length, 2),
        "avg_output_length": round(avg_output_length, 2),
    }


"""
@purpose: Gemini 测试专用的对话场景数据
@author: Daniel Chung + AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
from datetime import datetime
from typing import List

from src.models.domain.dialogue import DialogueArchiveMessage


# 场景一：Gemini 技术咨询对话（3轮）- 直接使用场景
GEMINI_TECHNICAL_DIALOGUES: List[dict] = [
    {
        "dialog_id": "gemini_tech_dialog_001",
        "user_id": "user_gemini_001",
        "turn": 1,
        "user_query": "什么是 Python？",
        "ai_response": "Python 是一种高级编程语言，由 Guido van Rossum 在 1991 年创建。它以其简洁的语法和强大的功能而闻名。",
    },
    {
        "dialog_id": "gemini_tech_dialog_001",
        "user_id": "user_gemini_001",
        "turn": 2,
        "user_query": "Python 可以用来做什么？",
        "ai_response": "Python 可以用于多种用途，包括 Web 开发（Django、Flask）、数据科学（Pandas、NumPy）、机器学习（TensorFlow、PyTorch）和自动化脚本。",
    },
    {
        "dialog_id": "gemini_tech_dialog_001",
        "user_id": "user_gemini_001",
        "turn": 3,
        "user_query": "我想学习 Python，有什么推荐的学习资源吗？",
        "ai_response": "推荐的学习资源包括：1) Python 官方文档 2) 《Python 编程：从入门到实践》3) Codecademy 的 Python 课程 4) Real Python 网站。",
    },
]

# 场景二：Gemini 业务咨询对话（3轮）- 降级场景
GEMINI_BUSINESS_DIALOGUES: List[dict] = [
    {
        "dialog_id": "gemini_business_dialog_001",
        "user_id": "user_gemini_business_001",
        "turn": 1,
        "user_query": "我们公司想实施 AI 项目，有什么建议吗？",
        "ai_response": "实施 AI 项目需要考虑几个关键因素：1) 明确业务目标 2) 数据准备 3) 技术选型 4) 团队建设 5) 预算规划。",
    },
    {
        "dialog_id": "gemini_business_dialog_001",
        "user_id": "user_gemini_business_001",
        "turn": 2,
        "user_query": "我们的数据量很大，担心处理速度问题。",
        "ai_response": "对于大数据量，建议考虑：1) 使用分布式计算框架（如 Spark）2) 数据预处理和清洗 3) 选择合适的存储方案（如 Hadoop HDFS）4) 优化算法和模型。",
    },
    {
        "dialog_id": "gemini_business_dialog_001",
        "user_id": "user_gemini_business_001",
        "turn": 3,
        "user_query": "预算大概需要多少？",
        "ai_response": "AI 项目预算通常包括：1) 硬件成本（GPU 服务器、存储）2) 软件许可（如需要）3) 人力成本（数据科学家、工程师）4) 云服务费用。根据项目规模，预算可能在 10 万到 100 万之间。",
    },
]

# 场景三：三元组分类测试数据
GEMINI_TRIPLE_CLASSIFICATION_TEST_DATA: List[dict] = [
    {
        "subject": "Python",
        "predicate": "是",
        "object": "编程语言",
        "expected_category": "技术类",
    },
    {
        "subject": "Python",
        "predicate": "用于",
        "object": "学习编程",
        "expected_category": "教育类",
    },
    {
        "subject": "Django",
        "predicate": "是",
        "object": "Web 框架",
        "expected_category": "工具类",
    },
    {
        "subject": "Guido van Rossum",
        "predicate": "创建",
        "object": "Python",
        "expected_category": "人物关系",
    },
    {
        "subject": "Python",
        "predicate": "支持",
        "object": "机器学习",
        "expected_category": "技术类",
    },
]


def create_gemini_dialogue_messages(dialogues: List[dict]) -> List[DialogueArchiveMessage]:
    """
    將對話字典列表轉換為 DialogueArchiveMessage 對象列表
    
    Args:
        dialogues: 對話字典列表
        
    Returns:
        DialogueArchiveMessage 對象列表
    """
    messages = []
    for dialogue in dialogues:
        message = DialogueArchiveMessage(
            dialog_id=dialogue["dialog_id"],
            user_id=dialogue["user_id"],
            timestamp=datetime.now(),
            turn=dialogue["turn"],
            user_query=dialogue["user_query"],
            ai_response=dialogue["ai_response"],
        )
        messages.append(message)
    return messages


def get_gemini_technical_dialogues() -> List[DialogueArchiveMessage]:
    """獲取 Gemini 技術諮詢對話消息"""
    return create_gemini_dialogue_messages(GEMINI_TECHNICAL_DIALOGUES)


def get_gemini_business_dialogues() -> List[DialogueArchiveMessage]:
    """獲取 Gemini 業務諮詢對話消息"""
    return create_gemini_dialogue_messages(GEMINI_BUSINESS_DIALOGUES)


def get_gemini_triple_classification_test_data() -> List[dict]:
    """獲取 Gemini 三元組分類測試數據"""
    return GEMINI_TRIPLE_CLASSIFICATION_TEST_DATA


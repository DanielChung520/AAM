"""
@purpose: 對話場景測試數據，用於端到端測試
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
from datetime import datetime
from typing import List

from src.models.domain.dialogue import DialogueArchiveMessage


# 場景一：技術諮詢對話（3輪）
TECHNICAL_CONSULTATION_DIALOGUES: List[dict] = [
    {
        "dialog_id": "tech_dialog_001",
        "user_id": "user_tech_001",
        "turn": 1,
        "user_query": "什么是 Python？",
        "ai_response": "Python 是一种高级编程语言，由 Guido van Rossum 在 1991 年创建。它以其简洁的语法和强大的功能而闻名，广泛应用于 Web 开发、数据科学、机器学习和自动化脚本等领域。",
    },
    {
        "dialog_id": "tech_dialog_001",
        "user_id": "user_tech_001",
        "turn": 2,
        "user_query": "Python 可以用来做什么？",
        "ai_response": "Python 可以用于多种用途，包括：1) Web 开发（使用 Django、Flask 等框架）2) 数据科学（使用 Pandas、NumPy 等库）3) 机器学习（使用 TensorFlow、PyTorch 等框架）4) 自动化脚本和系统管理。",
    },
    {
        "dialog_id": "tech_dialog_001",
        "user_id": "user_tech_001",
        "turn": 3,
        "user_query": "我想学习 Python，有什么推荐的学习资源吗？",
        "ai_response": "推荐的学习资源包括：1) Python 官方文档（python.org）2) 《Python 编程：从入门到实践》书籍 3) Codecademy 的 Python 课程 4) Real Python 网站 5) Coursera 的 Python 专项课程。",
    },
]

# 場景二：業務諮詢對話（4輪）
BUSINESS_CONSULTATION_DIALOGUES: List[dict] = [
    {
        "dialog_id": "business_dialog_001",
        "user_id": "user_business_001",
        "turn": 1,
        "user_query": "我们公司想实施 AI 项目，有什么建议吗？",
        "ai_response": "实施 AI 项目需要考虑几个关键因素：1) 明确业务目标（解决什么问题）2) 数据准备（数据质量、数据量）3) 技术选型（选择合适的 AI 技术和工具）4) 团队建设（数据科学家、AI 工程师）5) 预算规划（硬件、软件、人力成本）。",
    },
    {
        "dialog_id": "business_dialog_001",
        "user_id": "user_business_001",
        "turn": 2,
        "user_query": "我们的数据量很大，担心处理速度问题。",
        "ai_response": "对于大数据量，建议考虑：1) 使用分布式计算框架（如 Apache Spark）2) 数据预处理和清洗（减少无效数据）3) 选择合适的存储方案（如 Hadoop HDFS、云存储）4) 优化算法和模型（使用更高效的算法）5) 考虑使用 GPU 加速计算。",
    },
    {
        "dialog_id": "business_dialog_001",
        "user_id": "user_business_001",
        "turn": 3,
        "user_query": "预算大概需要多少？",
        "ai_response": "AI 项目预算通常包括：1) 硬件成本（GPU 服务器、存储设备，约 5-50 万）2) 软件许可（如需要商业软件，约 1-10 万）3) 人力成本（数据科学家、工程师，约 20-80 万/年）4) 云服务费用（如使用 AWS、Azure，约 1-20 万/年）。根据项目规模，总预算可能在 10 万到 100 万之间。",
    },
    {
        "dialog_id": "business_dialog_001",
        "user_id": "user_business_001",
        "turn": 4,
        "user_query": "谢谢，我们会考虑这些建议。",
        "ai_response": "不客气！如果后续有任何问题，随时可以咨询。祝您的 AI 项目顺利实施！",
    },
]

# 場景三：日常對話（2轮）
CASUAL_DIALOGUES: List[dict] = [
    {
        "dialog_id": "casual_dialog_001",
        "user_id": "user_casual_001",
        "turn": 1,
        "user_query": "今天天气真好！",
        "ai_response": "是的，今天天气确实不错！适合外出活动。您有什么计划吗？",
    },
    {
        "dialog_id": "casual_dialog_001",
        "user_id": "user_casual_001",
        "turn": 2,
        "user_query": "我想去公园走走。",
        "ai_response": "那是个不错的选择！公园里空气清新，可以放松心情。祝您玩得愉快！",
    },
]

# 場景四：教育學習諮詢對話（5輪）
EDUCATION_LEARNING_DIALOGUES: List[dict] = [
    {
        "dialog_id": "education_dialog_001",
        "user_id": "user_education_001",
        "turn": 1,
        "user_query": "我想学习机器学习，但不知道从哪里开始，有什么建议吗？",
        "ai_response": "学习机器学习是一个很好的选择！建议的学习路径包括：1) 先掌握数学基础（线性代数、概率统计、微积分）2) 学习编程语言（Python 是最常用的）3) 学习机器学习基础理论（监督学习、无监督学习、深度学习）4) 实践项目（使用 TensorFlow、PyTorch 等框架）5) 参加在线课程（如 Coursera 的 Andrew Ng 机器学习课程、fast.ai 等）。",
    },
    {
        "dialog_id": "education_dialog_001",
        "user_id": "user_education_001",
        "turn": 2,
        "user_query": "我需要多长时间才能掌握机器学习？",
        "ai_response": "学习时间因人而异，但一般建议：1) 基础阶段（3-6个月）：掌握数学和编程基础，理解基本概念 2) 进阶阶段（6-12个月）：深入学习算法和模型，完成多个实践项目 3) 高级阶段（1-2年）：深入研究特定领域（如计算机视觉、自然语言处理），参与实际项目。关键是持续学习和实践，建议每天至少投入 2-3 小时。",
    },
    {
        "dialog_id": "education_dialog_001",
        "user_id": "user_education_001",
        "turn": 3,
        "user_query": "有什么推荐的学习资源吗？",
        "ai_response": "推荐的学习资源包括：1) 在线课程：Coursera（Andrew Ng 的机器学习课程）、edX、Udacity、fast.ai 2) 书籍：《机器学习》（周志华）、《统计学习方法》（李航）、《深度学习》（Ian Goodfellow）3) 实践平台：Kaggle（数据科学竞赛）、GitHub（开源项目）4) 社区：Stack Overflow、Reddit 的 r/MachineLearning、知乎机器学习话题 5) 工具：Jupyter Notebook、Google Colab（免费 GPU）。",
    },
    {
        "dialog_id": "education_dialog_001",
        "user_id": "user_education_001",
        "turn": 4,
        "user_query": "我应该先学深度学习还是传统机器学习？",
        "ai_response": "建议的学习顺序是：1) 先学传统机器学习（线性回归、逻辑回归、决策树、随机森林、SVM 等），理解基本概念和原理 2) 再学深度学习（神经网络、CNN、RNN、Transformer 等），因为深度学习是机器学习的子集，需要传统机器学习的基础 3) 传统机器学习更容易理解，有助于建立扎实的理论基础 4) 深度学习虽然强大，但需要更多数据和计算资源。建议先用传统机器学习解决实际问题，再逐步过渡到深度学习。",
    },
    {
        "dialog_id": "education_dialog_001",
        "user_id": "user_education_001",
        "turn": 5,
        "user_query": "谢谢你的建议，我会按照这个路径学习的。",
        "ai_response": "不客气！学习机器学习是一个持续的过程，建议保持耐心和坚持。如果在学习过程中遇到问题，随时可以咨询。祝你学习顺利，早日成为机器学习专家！",
    },
]


def create_dialogue_messages(dialogues: List[dict]) -> List[DialogueArchiveMessage]:
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


def get_technical_consultation_messages() -> List[DialogueArchiveMessage]:
    """獲取技術諮詢對話消息"""
    return create_dialogue_messages(TECHNICAL_CONSULTATION_DIALOGUES)


def get_business_consultation_messages() -> List[DialogueArchiveMessage]:
    """獲取業務諮詢對話消息"""
    return create_dialogue_messages(BUSINESS_CONSULTATION_DIALOGUES)


def get_casual_dialogue_messages() -> List[DialogueArchiveMessage]:
    """獲取日常對話消息"""
    return create_dialogue_messages(CASUAL_DIALOGUES)


def get_education_learning_messages() -> List[DialogueArchiveMessage]:
    """獲取教育學習諮詢對話消息"""
    return create_dialogue_messages(EDUCATION_LEARNING_DIALOGUES)


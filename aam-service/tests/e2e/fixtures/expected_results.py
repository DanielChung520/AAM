"""
@purpose: 預期測試結果數據，用於驗證測試結果
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
from typing import Dict, List

# 場景一：技術諮詢對話的預期結果

EXPECTED_NER_TECHNICAL: List[str] = [
    "Python",
    "Guido van Rossum",
    "Django",
    "Flask",
    "Pandas",
    "NumPy",
    "TensorFlow",
    "PyTorch",
    "Codecademy",
    "Real Python",
    "Coursera",
    "1991",
]

EXPECTED_KE_TECHNICAL: List[str] = [
    "Python 是高级编程语言",
    "Python 由 Guido van Rossum 创建",
    "Python 用于 Web 开发",
    "Python 用于数据科学",
    "Python 用于机器学习",
    "Python 用于自动化脚本",
]

EXPECTED_KT_TECHNICAL: List[Dict[str, str]] = [
    {"subject": "Python", "predicate": "创建者", "object": "Guido van Rossum"},
    {"subject": "Python", "predicate": "创建时间", "object": "1991"},
    {"subject": "Python", "predicate": "用于", "object": "Web 开发"},
    {"subject": "Python", "predicate": "用于", "object": "数据科学"},
    {"subject": "Python", "predicate": "用于", "object": "机器学习"},
    {"subject": "Django", "predicate": "是", "object": "Web 框架"},
    {"subject": "Flask", "predicate": "是", "object": "Web 框架"},
    {"subject": "TensorFlow", "predicate": "是", "object": "机器学习框架"},
    {"subject": "PyTorch", "predicate": "是", "object": "机器学习框架"},
]

EXPECTED_PERSONALITY_TECHNICAL: Dict = {
    "style_tags": {"technical": 0.9, "formal": 0.8, "analytical": 0.85},
    "sentiment": "positive",
    "language_patterns": ["专业", "详细", "结构化"],
    "confidence_score": 0.85,
}

# 場景二：業務諮詢對話的預期結果

EXPECTED_NER_BUSINESS: List[str] = [
    "AI 项目",
    "Apache Spark",
    "Hadoop HDFS",
    "AWS",
    "Azure",
    "GPU",
    "数据科学家",
    "AI 工程师",
]

EXPECTED_KE_BUSINESS: List[str] = [
    "AI 项目实施需要考虑业务目标",
    "AI 项目需要数据准备",
    "大数据量需要使用分布式计算",
    "AI 项目预算包括硬件、软件、人力成本",
]

EXPECTED_KT_BUSINESS: List[Dict[str, str]] = [
    {"subject": "AI 项目", "predicate": "需要", "object": "明确业务目标"},
    {"subject": "AI 项目", "predicate": "需要", "object": "数据准备"},
    {"subject": "大数据量", "predicate": "处理方案", "object": "分布式计算"},
    {"subject": "Apache Spark", "predicate": "是", "object": "分布式计算框架"},
    {"subject": "AI 项目", "predicate": "预算范围", "object": "10-100万"},
]

EXPECTED_PERSONALITY_BUSINESS: Dict = {
    "style_tags": {"business": 0.9, "formal": 0.85, "decision_making": 0.8},
    "sentiment": "positive",
    "language_patterns": ["专业", "决策导向", "结构化"],
    "confidence_score": 0.88,
}

# 場景三：日常對話的預期結果

EXPECTED_NER_CASUAL: List[str] = [
    "今天",
    "公园",
]

EXPECTED_KE_CASUAL: List[str] = [
    "天气好",
    "去公园",
]

EXPECTED_KT_CASUAL: List[Dict[str, str]] = [
    {"subject": "用户", "predicate": "计划", "object": "去公园"},
]

EXPECTED_PERSONALITY_CASUAL: Dict = {
    "style_tags": {"casual": 0.9, "friendly": 0.85},
    "sentiment": "positive",
    "language_patterns": ["轻松", "友好"],
    "confidence_score": 0.75,
}

# 場景四：教育學習諮詢對話的預期結果

EXPECTED_NER_EDUCATION: List[str] = [
    "机器学习",
    "Python",
    "TensorFlow",
    "PyTorch",
    "Coursera",
    "Andrew Ng",
    "fast.ai",
    "Kaggle",
    "GitHub",
    "Jupyter Notebook",
    "Google Colab",
    "线性代数",
    "概率统计",
    "微积分",
    "监督学习",
    "无监督学习",
    "深度学习",
    "神经网络",
    "CNN",
    "RNN",
    "Transformer",
    "周志华",
    "李航",
    "Ian Goodfellow",
    "计算机视觉",
    "自然语言处理",
]

EXPECTED_KE_EDUCATION: List[str] = [
    "机器学习学习路径包括数学基础、编程语言、理论基础、实践项目",
    "学习机器学习需要3-6个月基础阶段",
    "推荐的学习资源包括在线课程、书籍、实践平台",
    "应该先学传统机器学习再学深度学习",
    "持续学习和实践是关键",
]

EXPECTED_KT_EDUCATION: List[Dict[str, str]] = [
    {"subject": "机器学习", "predicate": "学习路径", "object": "数学基础"},
    {"subject": "机器学习", "predicate": "需要", "object": "Python 编程语言"},
    {"subject": "机器学习", "predicate": "包括", "object": "监督学习"},
    {"subject": "机器学习", "predicate": "包括", "object": "无监督学习"},
    {"subject": "机器学习", "predicate": "包括", "object": "深度学习"},
    {"subject": "TensorFlow", "predicate": "是", "object": "机器学习框架"},
    {"subject": "PyTorch", "predicate": "是", "object": "机器学习框架"},
    {"subject": "Coursera", "predicate": "提供", "object": "Andrew Ng 机器学习课程"},
    {"subject": "Kaggle", "predicate": "是", "object": "数据科学竞赛平台"},
    {"subject": "深度学习", "predicate": "是", "object": "机器学习的子集"},
    {"subject": "传统机器学习", "predicate": "包括", "object": "线性回归"},
    {"subject": "传统机器学习", "predicate": "包括", "object": "决策树"},
    {"subject": "深度学习", "predicate": "包括", "object": "神经网络"},
    {"subject": "深度学习", "predicate": "包括", "object": "CNN"},
    {"subject": "深度学习", "predicate": "包括", "object": "RNN"},
    {"subject": "深度学习", "predicate": "包括", "object": "Transformer"},
]

# 教育學習場景的三元組分類標籤預期值
EXPECTED_KT_CATEGORIES_EDUCATION: List[str] = [
    "教育",
    "技术",
    "其他",
]

EXPECTED_PERSONALITY_EDUCATION: Dict = {
    "style_tags": {"education": 0.9, "formal": 0.8, "analytical": 0.85, "curious": 0.8},
    "sentiment": "positive",
    "language_patterns": ["专业", "详细", "结构化", "学习导向"],
    "confidence_score": 0.85,
}


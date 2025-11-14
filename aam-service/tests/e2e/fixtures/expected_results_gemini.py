"""
@purpose: Gemini 测试的预期结果数据
@author: Daniel Chung + AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""

# 场景一：技术咨询对话的预期 NER 结果
EXPECTED_NER_GEMINI_TECHNICAL = [
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
]

# 场景一：技术咨询对话的预期 KT 结果
EXPECTED_KT_GEMINI_TECHNICAL = [
    {"subject": "Python", "predicate": "创建者", "object": "Guido van Rossum"},
    {"subject": "Python", "predicate": "用于", "object": "Web 开发"},
    {"subject": "Python", "predicate": "用于", "object": "数据科学"},
    {"subject": "Django", "predicate": "是", "object": "Web 框架"},
    {"subject": "TensorFlow", "predicate": "是", "object": "机器学习库"},
]

# 场景二：业务咨询对话的预期 NER 结果
EXPECTED_NER_GEMINI_BUSINESS = [
    "AI 项目",
    "Spark",
    "Hadoop HDFS",
    "GPU",
    "数据科学家",
]

# 场景二：业务咨询对话的预期 KT 结果
EXPECTED_KT_GEMINI_BUSINESS = [
    {"subject": "AI 项目", "predicate": "需要", "object": "明确业务目标"},
    {"subject": "大数据量", "predicate": "处理方案", "object": "分布式计算"},
    {"subject": "Spark", "predicate": "是", "object": "分布式计算框架"},
    {"subject": "AI 项目", "predicate": "预算范围", "object": "10-100万"},
]

# 预期三元组分类结果
EXPECTED_TRIPLE_CLASSIFICATIONS = {
    "技术类": [
        {"subject": "Python", "predicate": "是", "object": "编程语言"},
        {"subject": "Python", "predicate": "支持", "object": "机器学习"},
    ],
    "教育类": [
        {"subject": "Python", "predicate": "用于", "object": "学习编程"},
    ],
    "工具类": [
        {"subject": "Django", "predicate": "是", "object": "Web 框架"},
    ],
    "人物关系": [
        {"subject": "Guido van Rossum", "predicate": "创建", "object": "Python"},
    ],
}


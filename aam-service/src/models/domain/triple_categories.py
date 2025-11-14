"""
@purpose: 定義三元組分類標籤的預定義分類列表和映射函數
@author: Daniel Chung + AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
from typing import Dict, List, Optional


# 預定義分類列表
PREDEFINED_CATEGORIES = {
    "technology": "技术",
    "business": "业务",
    "education": "教育",
    "medical": "医疗",
    "finance": "金融",
    "person_relation": "人物关系",
    "temporal": "时间关系",
    "other": "其他",
}

# AI 分類關鍵詞映射到預定義分類
AI_CATEGORY_KEYWORDS: Dict[str, str] = {
    # 技术相关
    "编程": "technology",
    "代码": "technology",
    "软件": "technology",
    "技术": "technology",
    "开发": "technology",
    "算法": "technology",
    "系统": "technology",
    "平台": "technology",
    "框架": "technology",
    "工具": "technology",
    "语言": "technology",
    "程序": "technology",
    "应用": "technology",
    "网络": "technology",
    "数据": "technology",
    "数据库": "technology",
    "服务器": "technology",
    "云计算": "technology",
    "人工智能": "technology",
    "机器学习": "technology",
    "深度学习": "technology",
    
    # 业务相关
    "业务": "business",
    "商业": "business",
    "公司": "business",
    "企业": "business",
    "项目": "business",
    "管理": "business",
    "战略": "business",
    "市场": "business",
    "销售": "business",
    "客户": "business",
    "产品": "business",
    "服务": "business",
    "运营": "business",
    "预算": "business",
    "成本": "business",
    "收入": "business",
    "利润": "business",
    "投资": "business",
    
    # 教育相关
    "教育": "education",
    "学习": "education",
    "教学": "education",
    "课程": "education",
    "培训": "education",
    "学校": "education",
    "大学": "education",
    "学生": "education",
    "老师": "education",
    "教材": "education",
    "资源": "education",
    "方法": "education",
    "技能": "education",
    "知识": "education",
    "考试": "education",
    "成绩": "education",
    "学位": "education",
    "专业": "education",
    
    # 医疗相关
    "医疗": "medical",
    "健康": "medical",
    "疾病": "medical",
    "治疗": "medical",
    "药物": "medical",
    "医院": "medical",
    "医生": "medical",
    "患者": "medical",
    "症状": "medical",
    "诊断": "medical",
    "手术": "medical",
    "康复": "medical",
    
    # 金融相关
    "金融": "finance",
    "银行": "finance",
    "货币": "finance",
    "股票": "finance",
    "基金": "finance",
    "保险": "finance",
    "贷款": "finance",
    "利息": "finance",
    "汇率": "finance",
    "交易": "finance",
    "账户": "finance",
    "支付": "finance",
    
    # 人物关系相关
    "人": "person_relation",
    "关系": "person_relation",
    "朋友": "person_relation",
    "家人": "person_relation",
    "同事": "person_relation",
    "领导": "person_relation",
    "下属": "person_relation",
    "合作": "person_relation",
    "团队": "person_relation",
    "组织": "person_relation",
    
    # 时间关系相关
    "时间": "temporal",
    "日期": "temporal",
    "年": "temporal",
    "月": "temporal",
    "日": "temporal",
    "小时": "temporal",
    "分钟": "temporal",
    "之前": "temporal",
    "之后": "temporal",
    "现在": "temporal",
    "未来": "temporal",
    "过去": "temporal",
    "开始": "temporal",
    "结束": "temporal",
    "持续": "temporal",
    "周期": "temporal",
}


def map_ai_category_to_predefined(ai_category: str) -> str:
    """
    將 AI 分類結果映射到預定義分類
    
    Args:
        ai_category: AI 模型返回的分類標籤
        
    Returns:
        預定義分類的英文鍵（如 "technology"）
    """
    if not ai_category:
        return "other"
    
    # 轉換為小寫以便匹配
    ai_category_lower = ai_category.lower()
    
    # 檢查關鍵詞匹配
    for keyword, category in AI_CATEGORY_KEYWORDS.items():
        if keyword in ai_category_lower:
            return category
    
    # 如果沒有匹配，返回 "other"
    return "other"


def get_category_label(category_key: str) -> str:
    """
    獲取分類的中文標籤
    
    Args:
        category_key: 預定義分類的英文鍵
        
    Returns:
        分類的中文標籤
    """
    return PREDEFINED_CATEGORIES.get(category_key, "其他")


def extract_categories_from_triples(triples: List[dict]) -> List[str]:
    """
    從三元組列表中提取所有分類標籤
    
    Args:
        triples: 三元組列表，每個三元組可能包含 "category" 字段
        
    Returns:
        去重後的分類標籤列表（中文）
    """
    categories = set()
    for triple in triples:
        if isinstance(triple, dict) and "category" in triple:
            category = triple["category"]
            if category:
                categories.add(category)
    
    return sorted(list(categories))


def get_category_summary(triples: List[dict]) -> str:
    """
    獲取三元組列表的分類摘要（用於 ChromaDB metadata）
    
    Args:
        triples: 三元組列表
        
    Returns:
        分類標籤的逗號分隔字符串（如 "技术,教育,业务"）
    """
    categories = extract_categories_from_triples(triples)
    return ",".join(categories) if categories else ""


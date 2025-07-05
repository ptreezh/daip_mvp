import hashlib
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# 标准字段定义
REQUIRED_FIELDS = {
    "id": str,
    "name": str,
    "category": str,
    "description": str,
    "skills": list,
    "languages": list,
    "availability": str,
}

OPTIONAL_FIELDS = {
    "title": str,
    "specialties": list,
    "experience_years": int,
    "reputation_score": (int, float),
    "contact_info": dict,
    "hourly_rate": (int, float, type(None)),
    "location": str,
    "education": list,
    "certifications": list,
    "projects": list,
    "bio": str,
    "source_file": str,
    "created_at": str,
    "updated_at": str,
}

CATEGORY_MAPPING = {
    "技术": ["技术", "开发", "编程", "软件", "系统", "数据", "AI", "人工智能"],
    "管理": ["管理", "项目", "团队", "领导", "运营", "战略"],
    "商业": ["商业", "市场", "营销", "财务", "投资", "经济"],
    "学术": ["学术", "研究", "教育", "理论", "论文", "科学"],
    "创意": ["创意", "设计", "艺术", "创作", "文案", "内容"],
    "咨询": ["咨询", "顾问", "服务", "建议", "指导"],
    "通用": ["通用", "多面手", "协调", "综合"],
}

SKILL_CATEGORIES = {
    "编程语言": [
        "Python",
        "Java",
        "JavaScript",
        "C++",
        "Go",
        "Rust",
        "PHP",
        "Ruby",
        "Swift",
        "Kotlin",
    ],
    "框架工具": [
        "React",
        "Vue",
        "Angular",
        "Django",
        "Flask",
        "Spring",
        "Express",
        "Laravel",
        "TensorFlow",
        "PyTorch",
    ],
    "数据库": [
        "MySQL",
        "PostgreSQL",
        "MongoDB",
        "Redis",
        "Elasticsearch",
        "Oracle",
        "SQLite",
        "Cassandra",
    ],
    "云服务": ["AWS", "Azure", "GCP", "阿里云", "腾讯云", "华为云", "百度云"],
    "分析方法": ["数据分析", "统计分析", "机器学习", "深度学习", "数据挖掘", "预测分析"],
    "管理方法": ["敏捷开发", "Scrum", "看板", "六西格玛", "精益管理", "项目管理", "团队管理"],
    "设计工具": ["Photoshop", "Illustrator", "Figma", "Sketch", "InDesign", "XD"],
    "办公软件": ["Excel", "PowerPoint", "Word", "PowerBI", "Tableau", "SPSS"],
}

STANDARD_LANGUAGES = ["中文", "英文", "日文", "韩文", "法文", "德文", "西班牙文", "俄文"]


def _get_default_value(
    field: str,
    expected_type: type,
    file_path: Optional[Path] = None,
) -> Any:
    if field == "id":
        return _generate_valid_id(file_path) if file_path else str(uuid.uuid4())
    elif field == "name":
        return file_path.stem if file_path else "未命名角色"
    elif field == "category":
        return "通用"
    elif field == "description":
        return "专业角色，具备相关领域知识和经验。"
    elif field == "skills":
        return []
    elif field == "languages":
        return ["中文"]
    elif field == "availability":
        return "可用"
    elif field == "title":
        return ""
    elif field == "specialties":
        return []
    elif field == "experience_years":
        return 0
    elif field == "reputation_score":
        return 80.0
    elif field == "contact_info":
        return {}
    elif field == "hourly_rate":
        return None
    elif field == "location":
        return ""
    elif field == "education":
        return []
    elif field == "certifications":
        return []
    elif field == "projects":
        return []
    elif field == "bio":
        return ""
    else:
        return None


def _convert_field_type(value: Any, expected_type: type) -> Any:
    if isinstance(expected_type, tuple):
        for t in expected_type:
            if isinstance(value, t):
                return value
        if expected_type == (int, float, type(None)):
            if value is None:
                return None
            try:
                return float(value)
            except:
                return None
    else:
        if isinstance(value, expected_type):
            return value
        if expected_type == str:
            return str(value) if value is not None else ""
        elif expected_type == list:
            if isinstance(value, str):
                return [value]
            elif isinstance(value, (tuple, set)):
                return list(value)
            else:
                return []
        elif expected_type == dict:
            if isinstance(value, str):
                return {"info": value}
            else:
                return {}
        elif expected_type == int:
            try:
                return int(value) if value is not None else 0
            except:
                return 0
        elif expected_type == float:
            try:
                return float(value) if value is not None else 0.0
            except:
                return 0.0
    return _get_default_value("", expected_type)


def _generate_valid_id(file_path: Optional[Path]) -> str:
    content = f"{file_path}{datetime.now().isoformat()}"
    return hashlib.md5(content.encode()).hexdigest()[:16]


def _is_valid_id(role_id: str) -> bool:
    if not role_id or not isinstance(role_id, str):
        return False
    uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    hash_pattern = r"^[0-9a-f]{8,}$"
    import re

    return bool(
        re.match(uuid_pattern, role_id.lower())
        or re.match(hash_pattern, role_id.lower()),
    )


def _is_valid_timestamp(timestamp: str) -> bool:
    try:
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return True
    except Exception:
        return False


def _standardize_category(category: str) -> str:
    category_lower = category.lower()
    for standard_cat, keywords in CATEGORY_MAPPING.items():
        for keyword in keywords:
            if keyword in category_lower:
                return standard_cat
    return "通用"


def _standardize_skills(skills: list[str]) -> list[str]:
    if not skills:
        return []
    standardized_skills = []
    all_standard_skills = set()
    for skill_list in SKILL_CATEGORIES.values():
        all_standard_skills.update(skill_list)
    for skill in skills:
        skill_clean = skill.strip()
        if skill_clean:
            matched = False
            for standard_skill in all_standard_skills:
                if skill_clean.lower() == standard_skill.lower():
                    standardized_skills.append(standard_skill)
                    matched = True
                    break
            if not matched:
                standardized_skills.append(skill_clean)
    return list(set(standardized_skills))


def _standardize_languages(languages: list[str]) -> list[str]:
    if not languages:
        return ["中文"]
    standardized_languages = []
    for lang in languages:
        lang_clean = lang.strip()
        if lang_clean:
            matched = False
            for standard_lang in STANDARD_LANGUAGES:
                if lang_clean.lower() == standard_lang.lower():
                    standardized_languages.append(standard_lang)
                    matched = True
                    break
            if not matched:
                standardized_languages.append(lang_clean)
    if "中文" not in standardized_languages:
        standardized_languages.insert(0, "中文")
    return list(set(standardized_languages))


def standardize_role_dict(
    data: dict[str, Any],
    file_path: Optional[str] = None,
) -> dict[str, Any]:
    """将任意角色字典标准化为合规JSON格式。
    file_path 可选，用于生成ID和source_file。
    """
    changes_made = []
    standardized = data.copy()
    p = Path(file_path) if file_path else None
    # 1. 必需字段
    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in standardized:
            standardized[field] = _get_default_value(field, expected_type, p)
        elif not isinstance(standardized[field], expected_type):
            standardized[field] = _convert_field_type(
                standardized[field],
                expected_type,
            )
    # 2. ID
    if not _is_valid_id(standardized["id"]):
        standardized["id"] = _generate_valid_id(p)
    # 3. 名称
    if not standardized["name"].strip():
        standardized["name"] = p.stem if p else "未命名角色"
    # 4. 分类
    standardized["category"] = _standardize_category(standardized["category"])
    # 5. 技能
    if isinstance(standardized["skills"], list):
        standardized["skills"] = _standardize_skills(standardized["skills"])
    # 6. 语言
    if isinstance(standardized["languages"], list):
        standardized["languages"] = _standardize_languages(standardized["languages"])
    # 7. 可选字段
    for field, expected_type in OPTIONAL_FIELDS.items():
        if field in standardized:
            if not isinstance(standardized[field], expected_type):
                standardized[field] = _convert_field_type(
                    standardized[field],
                    expected_type,
                )
        else:
            if field in [
                "title",
                "specialties",
                "experience_years",
                "reputation_score",
            ]:
                standardized[field] = _get_default_value(field, expected_type)
    # 8. 时间戳
    if "created_at" not in standardized or not _is_valid_timestamp(
        standardized["created_at"],
    ):
        standardized["created_at"] = datetime.now().isoformat()
    standardized["updated_at"] = datetime.now().isoformat()
    # 9. 文件路径
    if p:
        standardized["source_file"] = str(p)
    # 10. 描述
    if "description" in standardized:
        desc = standardized["description"]
        if len(desc) < 10:
            standardized["description"] = f"{desc} - 专业角色，具备相关领域知识和经验。"
    return standardized


def analyze_role_definition(role_name: str, role_definition: str) -> dict[str, Any]:
    """智能分析角色定义，自动提取专业领域、技能等信息

    Args:
    ----
        role_name: 角色名称
        role_definition: 角色定义描述

    Returns:
    -------
        包含分析结果的字典

    """
    # 预定义的专业领域关键词
    specialty_keywords = {
        "技术": [
            "技术",
            "编程",
            "开发",
            "软件",
            "硬件",
            "系统",
            "架构",
            "算法",
            "数据",
            "AI",
            "人工智能",
            "机器学习",
            "深度学习",
        ],
        "管理": ["管理", "领导", "战略", "规划", "组织", "协调", "决策", "项目", "团队", "运营"],
        "学术": ["研究", "学术", "理论", "分析", "调查", "实验", "论文", "发表", "教育", "教学"],
        "商业": ["商业", "市场", "营销", "销售", "财务", "投资", "创业", "企业", "经济", "金融"],
        "创意": ["创意", "设计", "艺术", "创作", "创新", "想象", "视觉", "媒体", "内容"],
        "法律": ["法律", "法规", "合规", "政策", "治理", "监管", "合同", "知识产权"],
        "医疗": ["医疗", "健康", "医学", "临床", "诊断", "治疗", "药物", "护理"],
        "教育": ["教育", "培训", "学习", "课程", "教学", "指导", "辅导", "知识"],
        "环境": ["环境", "生态", "可持续", "绿色", "环保", "气候", "能源"],
        "社会": ["社会", "文化", "心理", "行为", "沟通", "关系", "社区", "公益"],
    }

    # 预定义的技能关键词
    skill_keywords = {
        "编程语言": [
            "Python",
            "Java",
            "JavaScript",
            "C++",
            "C#",
            "Go",
            "Rust",
            "PHP",
            "Ruby",
            "Swift",
            "Kotlin",
        ],
        "数据分析": [
            "数据分析",
            "统计",
            "建模",
            "可视化",
            "Excel",
            "SQL",
            "R",
            "SPSS",
            "SAS",
            "Tableau",
        ],
        "机器学习": [
            "机器学习",
            "深度学习",
            "神经网络",
            "TensorFlow",
            "PyTorch",
            "Scikit-learn",
            "自然语言处理",
        ],
        "项目管理": ["项目管理", "敏捷", "Scrum", "看板", "JIRA", "Trello", "Asana", "风险管理"],
        "设计工具": [
            "Photoshop",
            "Illustrator",
            "Figma",
            "Sketch",
            "InDesign",
            "CAD",
            "3D建模",
        ],
        "办公软件": [
            "Office",
            "Word",
            "Excel",
            "PowerPoint",
            "Outlook",
            "Google Workspace",
        ],
        "沟通技能": ["沟通", "演讲", "写作", "谈判", "协调", "团队合作", "跨文化"],
        "语言能力": ["中文", "英文", "日文", "韩文", "法文", "德文", "西班牙文", "俄文"],
        "研究方法": ["研究设计", "问卷调查", "访谈", "实验", "文献综述", "统计分析"],
        "行业知识": ["行业", "领域", "专业", "经验", "实践", "案例", "最佳实践"],
    }

    # 分析专业领域
    detected_specialties = []
    specialty_scores = {}

    for category, keywords in specialty_keywords.items():
        score = 0
        for keyword in keywords:
            if (
                keyword.lower() in role_definition.lower()
                or keyword.lower() in role_name.lower()
            ):
                score += 1
        if score > 0:
            specialty_scores[category] = score

    # 选择得分最高的专业领域
    if specialty_scores:
        max_score = max(specialty_scores.values())
        for category, score in specialty_scores.items():
            if score >= max_score * 0.5:  # 选择得分不低于最高分50%的领域
                detected_specialties.append(category)

    # 分析技能
    detected_skills = []
    skill_scores = {}

    for skill_category, keywords in skill_keywords.items():
        score = 0
        for keyword in keywords:
            if keyword.lower() in role_definition.lower():
                score += 1
        if score > 0:
            skill_scores[skill_category] = score

    # 选择得分最高的技能类别
    if skill_scores:
        max_score = max(skill_scores.values())
        for skill_category, score in skill_scores.items():
            if score >= max_score * 0.5:
                detected_skills.append(skill_category)

    # 分析经验年限（基于关键词）
    experience_indicators = {
        "初级": ["初级", "新手", "入门", "学习", "实习", "助理"],
        "中级": ["中级", "熟练", "经验", "专业", "资深"],
        "高级": ["高级", "专家", "资深", "首席", "总监", "经理", "主管"],
        "顶级": ["顶级", "大师", "权威", "首席", "总监", "副总裁", "总裁"],
    }

    experience_level = "中级"  # 默认
    for level, indicators in experience_indicators.items():
        for indicator in indicators:
            if indicator in role_definition or indicator in role_name:
                experience_level = level
                break

    # 根据经验级别估算年限
    experience_years_map = {"初级": 1, "中级": 5, "高级": 10, "顶级": 15}

    estimated_years = experience_years_map.get(experience_level, 5)

    # 分析声誉评分
    reputation_indicators = {
        "权威": ["权威", "专家", "大师", "首席", "知名", "著名"],
        "专业": ["专业", "资深", "经验丰富", "熟练"],
        "新手": ["新手", "初级", "学习", "入门"],
    }

    reputation_score = 80.0  # 默认
    for level, indicators in reputation_indicators.items():
        for indicator in indicators:
            if indicator in role_definition or indicator in role_name:
                if level == "权威":
                    reputation_score = 95.0
                elif level == "专业":
                    reputation_score = 85.0
                elif level == "新手":
                    reputation_score = 70.0
                break

    # 分析语言能力
    detected_languages = ["中文"]  # 默认包含中文
    language_keywords = {
        "英文": ["英文", "英语", "English", "国际", "海外", "跨国"],
        "日文": ["日文", "日语", "日本", "Japanese"],
        "韩文": ["韩文", "韩语", "韩国", "Korean"],
        "法文": ["法文", "法语", "法国", "French"],
        "德文": ["德文", "德语", "德国", "German"],
        "西班牙文": ["西班牙文", "西班牙语", "西班牙", "Spanish"],
    }

    for lang, keywords in language_keywords.items():
        for keyword in keywords:
            if keyword in role_definition or keyword in role_name:
                if lang not in detected_languages:
                    detected_languages.append(lang)
                break

    # 如果没有检测到其他语言，默认添加英文
    if len(detected_languages) == 1:
        detected_languages.append("英文")

    return {
        "specialties": detected_specialties,
        "skills": detected_skills,
        "experience_years": estimated_years,
        "reputation_score": reputation_score,
        "languages": detected_languages,
        "experience_level": experience_level,
        "analysis_confidence": 0.8,  # 分析置信度
    }

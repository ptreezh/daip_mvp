"""能力选项管理系统
定义和管理角色能力，支持基于能力的角色筛选和匹配
"""

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class Capability:
    """能力定义"""

    id: str
    name: str
    category: str
    description: str
    level_descriptions: dict[int, str]  # 等级描述 1-5
    related_skills: list[str]
    keywords: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CapabilityProfile:
    """角色能力档案"""

    role_id: str
    capabilities: dict[str, int]  # 能力ID -> 等级
    auto_detected: dict[str, int]  # 自动检测的能力
    manually_assigned: dict[str, int]  # 手动分配的能力
    last_updated: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CapabilityManager:
    """能力管理器"""

    def __init__(self, capabilities_file: str = "data/capabilities.json"):
        self.capabilities_file = Path(capabilities_file)
        self.capabilities: dict[str, Capability] = {}
        self.capability_categories: dict[str, list[str]] = {}
        self.role_profiles: dict[str, CapabilityProfile] = {}
        self.logger = logging.getLogger(__name__)

        # 确保数据目录存在
        self.capabilities_file.parent.mkdir(exist_ok=True)

        # 加载能力定义
        self._load_capabilities()

        # 初始化默认能力体系
        if not self.capabilities:
            self._initialize_default_capabilities()

    def _load_capabilities(self):
        """加载能力定义"""
        if self.capabilities_file.exists():
            try:
                with open(self.capabilities_file, encoding="utf-8") as f:
                    data = json.load(f)

                for cap_data in data.get("capabilities", []):
                    capability = Capability(**cap_data)
                    self.capabilities[capability.id] = capability

                    # 构建分类索引
                    if capability.category not in self.capability_categories:
                        self.capability_categories[capability.category] = []
                    self.capability_categories[capability.category].append(
                        capability.id,
                    )

                self.logger.info(f"加载了 {len(self.capabilities)} 个能力定义")

            except Exception as e:
                self.logger.error(f"加载能力定义失败: {e}")

    def _save_capabilities(self):
        """保存能力定义"""
        try:
            data = {
                "capabilities": [cap.to_dict() for cap in self.capabilities.values()],
                "last_updated": str(Path(__file__).stat().st_mtime),
            }

            with open(self.capabilities_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            self.logger.error(f"保存能力定义失败: {e}")

    def _initialize_default_capabilities(self):
        """初始化默认能力体系"""
        default_capabilities = [
            # 技术能力
            {
                "id": "programming",
                "name": "编程开发",
                "category": "技术",
                "description": "软件开发和编程能力",
                "level_descriptions": {
                    1: "了解基本编程概念",
                    2: "能编写简单程序",
                    3: "熟练掌握一门编程语言",
                    4: "精通多种编程语言和框架",
                    5: "架构师级别，能设计复杂系统",
                },
                "related_skills": ["Python", "Java", "JavaScript", "C++"],
                "keywords": ["编程", "开发", "代码", "软件", "programming", "coding"],
            },
            {
                "id": "data_analysis",
                "name": "数据分析",
                "category": "技术",
                "description": "数据处理和分析能力",
                "level_descriptions": {
                    1: "了解数据分析基本概念",
                    2: "能使用基本工具进行数据处理",
                    3: "熟练使用统计方法分析数据",
                    4: "能进行复杂的数据建模",
                    5: "数据科学专家级别",
                },
                "related_skills": ["统计学", "机器学习", "SQL", "Python", "R"],
                "keywords": ["数据", "分析", "统计", "建模", "data", "analysis"],
            },
            # 管理能力
            {
                "id": "project_management",
                "name": "项目管理",
                "category": "管理",
                "description": "项目规划、执行和控制能力",
                "level_descriptions": {
                    1: "了解项目管理基本概念",
                    2: "能参与项目执行",
                    3: "能独立管理小型项目",
                    4: "能管理复杂项目",
                    5: "项目管理专家，能管理项目组合",
                },
                "related_skills": ["PMP", "敏捷", "Scrum", "风险管理"],
                "keywords": ["项目", "管理", "规划", "执行", "project", "management"],
            },
            {
                "id": "team_leadership",
                "name": "团队领导",
                "category": "管理",
                "description": "团队建设和领导能力",
                "level_descriptions": {
                    1: "了解团队合作重要性",
                    2: "能在团队中发挥积极作用",
                    3: "能领导小团队",
                    4: "能管理大型团队",
                    5: "组织级领导力",
                },
                "related_skills": ["沟通", "激励", "冲突解决", "绩效管理"],
                "keywords": ["团队", "领导", "管理", "激励", "team", "leadership"],
            },
            # 创意能力
            {
                "id": "creative_thinking",
                "name": "创意思维",
                "category": "创意",
                "description": "创新和创意产生能力",
                "level_descriptions": {
                    1: "有基本的创意意识",
                    2: "能产生一些新想法",
                    3: "经常有创新思路",
                    4: "创意思维突出",
                    5: "创意大师级别",
                },
                "related_skills": ["头脑风暴", "设计思维", "创新方法"],
                "keywords": ["创意", "创新", "想象", "设计", "creative", "innovation"],
            },
            {
                "id": "content_creation",
                "name": "内容创作",
                "category": "创意",
                "description": "文字、视觉等内容创作能力",
                "level_descriptions": {
                    1: "能创作基本内容",
                    2: "内容质量较好",
                    3: "内容有吸引力",
                    4: "内容创作专业水平",
                    5: "内容创作大师",
                },
                "related_skills": ["写作", "设计", "视频制作", "文案"],
                "keywords": ["内容", "创作", "写作", "文案", "content", "writing"],
            },
            # 沟通能力
            {
                "id": "communication",
                "name": "沟通表达",
                "category": "软技能",
                "description": "口头和书面沟通能力",
                "level_descriptions": {
                    1: "基本沟通能力",
                    2: "能清楚表达观点",
                    3: "沟通效果良好",
                    4: "沟通技巧娴熟",
                    5: "沟通大师级别",
                },
                "related_skills": ["演讲", "写作", "倾听", "谈判"],
                "keywords": ["沟通", "表达", "演讲", "交流", "communication"],
            },
            {
                "id": "problem_solving",
                "name": "问题解决",
                "category": "软技能",
                "description": "分析和解决问题的能力",
                "level_descriptions": {
                    1: "能识别基本问题",
                    2: "能解决简单问题",
                    3: "能系统性解决问题",
                    4: "解决复杂问题的专家",
                    5: "问题解决大师",
                },
                "related_skills": ["逻辑思维", "分析能力", "决策", "创新"],
                "keywords": ["问题", "解决", "分析", "逻辑", "problem", "solving"],
            },
            # 学术研究能力
            {
                "id": "academic_research",
                "name": "学术研究",
                "category": "学术",
                "description": "学术研究和论文写作能力",
                "level_descriptions": {
                    1: "了解学术研究基本方法",
                    2: "能进行基础研究",
                    3: "能独立完成研究项目",
                    4: "研究能力突出",
                    5: "学术研究专家",
                },
                "related_skills": ["文献调研", "实验设计", "论文写作", "同行评议"],
                "keywords": ["研究", "学术", "论文", "实验", "research", "academic"],
            },
        ]

        for cap_data in default_capabilities:
            capability = Capability(**cap_data)
            self.capabilities[capability.id] = capability

            # 构建分类索引
            if capability.category not in self.capability_categories:
                self.capability_categories[capability.category] = []
            self.capability_categories[capability.category].append(capability.id)

        # 保存默认能力
        self._save_capabilities()
        self.logger.info(f"初始化了 {len(self.capabilities)} 个默认能力")

    def get_capability(self, capability_id: str) -> Optional[Capability]:
        """获取能力定义"""
        return self.capabilities.get(capability_id)

    def get_capabilities_by_category(self, category: str) -> list[Capability]:
        """按分类获取能力"""
        capability_ids = self.capability_categories.get(category, [])
        return [self.capabilities[cap_id] for cap_id in capability_ids]

    def get_all_capabilities(self) -> list[Capability]:
        """获取所有能力"""
        return list(self.capabilities.values())

    def search_capabilities(self, query: str) -> list[Capability]:
        """搜索能力"""
        query_lower = query.lower()
        results = []

        for capability in self.capabilities.values():
            # 搜索名称、描述和关键词
            if (
                query_lower in capability.name.lower()
                or query_lower in capability.description.lower()
                or any(
                    query_lower in keyword.lower() for keyword in capability.keywords
                )
            ):
                results.append(capability)

        return results

    def detect_role_capabilities(self, expert_data: dict[str, Any]) -> dict[str, int]:
        """自动检测角色能力"""
        detected_capabilities = {}

        # 提取文本内容
        text_content = []
        text_content.append(expert_data.get("description", ""))
        text_content.append(expert_data.get("bio", ""))
        text_content.extend(expert_data.get("specialties", []))
        text_content.extend(expert_data.get("skills", []))

        full_text = " ".join(text_content).lower()

        # 匹配能力关键词
        for capability in self.capabilities.values():
            match_score = 0
            keyword_matches = 0

            for keyword in capability.keywords:
                if keyword.lower() in full_text:
                    keyword_matches += 1
                    match_score += 1

            # 检查相关技能
            for skill in capability.related_skills:
                if skill.lower() in full_text:
                    match_score += 2  # 相关技能权重更高

            # 根据匹配程度确定能力等级
            if match_score >= 3:
                level = min(5, 2 + match_score // 2)
                detected_capabilities[capability.id] = level
            elif keyword_matches >= 2:
                detected_capabilities[capability.id] = 2
            elif keyword_matches >= 1:
                detected_capabilities[capability.id] = 1

        return detected_capabilities

    def create_role_profile(
        self,
        role_id: str,
        expert_data: dict[str, Any],
    ) -> CapabilityProfile:
        """为角色创建能力档案"""
        auto_detected = self.detect_role_capabilities(expert_data)

        profile = CapabilityProfile(
            role_id=role_id,
            capabilities=auto_detected.copy(),
            auto_detected=auto_detected,
            manually_assigned={},
            last_updated=str(Path(__file__).stat().st_mtime),
        )

        self.role_profiles[role_id] = profile
        return profile

    def update_role_capability(
        self,
        role_id: str,
        capability_id: str,
        level: int,
        manual: bool = True,
    ):
        """更新角色能力等级"""
        if role_id not in self.role_profiles:
            return False

        profile = self.role_profiles[role_id]
        profile.capabilities[capability_id] = level

        if manual:
            profile.manually_assigned[capability_id] = level

        profile.last_updated = str(Path(__file__).stat().st_mtime)
        return True

    def get_role_capabilities(self, role_id: str) -> Optional[CapabilityProfile]:
        """获取角色能力档案"""
        return self.role_profiles.get(role_id)

    def filter_roles_by_capabilities(
        self,
        role_profiles: list[CapabilityProfile],
        required_capabilities: dict[str, int],
    ) -> list[CapabilityProfile]:
        """根据能力要求筛选角色"""
        filtered_profiles = []

        for profile in role_profiles:
            meets_requirements = True

            for cap_id, min_level in required_capabilities.items():
                role_level = profile.capabilities.get(cap_id, 0)
                if role_level < min_level:
                    meets_requirements = False
                    break

            if meets_requirements:
                filtered_profiles.append(profile)

        return filtered_profiles

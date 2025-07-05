"""动态角色加载和能力选项管理系统
根据任务情景智能加载和推荐角色，支持基于任务需求的能力匹配
"""

import logging
import re
from dataclasses import dataclass
from typing import Any

from src.chat_config import get_vectorization_config
from src.expert_library import ExpertLibrary


@dataclass
class TaskContext:
    """任务上下文"""

    task_id: str
    task_type: str  # 分析、创作、咨询、研究等
    domain: str  # 领域：技术、管理、学术等
    complexity: str  # 复杂度：简单、中等、复杂
    required_skills: list[str]  # 必需技能
    preferred_skills: list[str]  # 优选技能
    language: str = "中文"
    urgency: str = "正常"  # 紧急程度
    collaboration_type: str = "讨论"  # 协作类型：讨论、辩论、头脑风暴等
    target_audience: str = "通用"  # 目标受众
    expected_output: str = ""  # 期望输出类型
    constraints: list[str] = None  # 约束条件

    def __post_init__(self):
        if self.constraints is None:
            self.constraints = []


@dataclass
class CapabilityRequirement:
    """能力需求"""

    capability_name: str
    importance: float  # 重要性权重 0-1
    min_level: int = 1  # 最低要求等级 1-5
    preferred_level: int = 3  # 优选等级 1-5
    is_mandatory: bool = False  # 是否必需


class DynamicRoleManager:
    """动态角色管理器"""

    def __init__(self, expert_library: ExpertLibrary):
        self.expert_library = expert_library
        self.config = get_vectorization_config()
        self.logger = logging.getLogger(__name__)

        # 任务类型到能力的映射
        self.task_capability_mapping = self._initialize_task_capability_mapping()

        # 领域专业知识映射
        self.domain_expertise_mapping = self._initialize_domain_expertise_mapping()

        # 协作类型到角色特征的映射
        self.collaboration_role_mapping = self._initialize_collaboration_mapping()

    def load_roles_for_task(
        self,
        task_context: TaskContext,
        max_roles: int = 6,
    ) -> list[dict[str, Any]]:
        """根据任务上下文动态加载角色"""
        self.logger.info(f"为任务 {task_context.task_id} 加载角色")

        # 1. 分析任务需求，生成能力需求
        capability_requirements = self._analyze_task_requirements(task_context)

        # 2. 获取候选角色
        candidate_roles = self._get_candidate_roles(
            task_context,
            capability_requirements,
        )

        # 3. 评分和排序
        scored_roles = self._score_roles_for_task(
            candidate_roles,
            task_context,
            capability_requirements,
        )

        # 4. 应用多样性和协作优化
        optimized_roles = self._optimize_role_combination(
            scored_roles,
            task_context,
            max_roles,
        )

        # 5. 返回最终推荐
        return optimized_roles[:max_roles]

    def _analyze_task_requirements(
        self,
        task_context: TaskContext,
    ) -> list[CapabilityRequirement]:
        """分析任务需求，生成能力需求列表"""
        requirements = []

        # 基于任务类型的基础能力需求
        base_capabilities = self.task_capability_mapping.get(task_context.task_type, [])
        for cap_name, importance in base_capabilities:
            requirements.append(
                CapabilityRequirement(
                    capability_name=cap_name,
                    importance=importance,
                    min_level=2,
                    preferred_level=4,
                ),
            )

        # 基于领域的专业能力需求
        domain_capabilities = self.domain_expertise_mapping.get(task_context.domain, [])
        for cap_name, importance in domain_capabilities:
            requirements.append(
                CapabilityRequirement(
                    capability_name=cap_name,
                    importance=importance,
                    min_level=3,
                    preferred_level=5,
                    is_mandatory=True,
                ),
            )

        # 基于明确技能需求
        for skill in task_context.required_skills:
            requirements.append(
                CapabilityRequirement(
                    capability_name=skill,
                    importance=0.9,
                    min_level=3,
                    preferred_level=5,
                    is_mandatory=True,
                ),
            )

        for skill in task_context.preferred_skills:
            requirements.append(
                CapabilityRequirement(
                    capability_name=skill,
                    importance=0.7,
                    min_level=2,
                    preferred_level=4,
                ),
            )

        return requirements

    def _get_candidate_roles(
        self,
        task_context: TaskContext,
        capability_requirements: list[CapabilityRequirement],
    ) -> list[dict[str, Any]]:
        """获取候选角色"""
        # 获取所有专家
        all_experts = self.expert_library.get_all_experts()

        candidates = []
        for expert in all_experts:
            # 基础过滤
            if self._meets_basic_requirements(expert, task_context):
                # 计算能力匹配度
                capability_score = self._calculate_capability_match(
                    expert,
                    capability_requirements,
                )
                if capability_score > 0.3:  # 最低匹配阈值
                    expert_with_score = expert.copy()
                    expert_with_score["_capability_score"] = capability_score
                    candidates.append(expert_with_score)

        return candidates

    def _meets_basic_requirements(
        self,
        expert: dict[str, Any],
        task_context: TaskContext,
    ) -> bool:
        """检查专家是否满足基本要求"""
        # 语言要求
        expert_languages = expert.get("languages", [])
        if (
            task_context.language not in expert_languages
            and "中文" not in expert_languages
        ):
            return False

        # 可用性检查
        if expert.get("availability", "") == "不可用":
            return False

        return True

    def _calculate_capability_match(
        self,
        expert: dict[str, Any],
        requirements: list[CapabilityRequirement],
    ) -> float:
        """计算专家与能力需求的匹配度"""
        if not requirements:
            return 0.5

        expert_capabilities = self._extract_expert_capabilities(expert)
        total_score = 0.0
        total_weight = 0.0

        for req in requirements:
            weight = req.importance
            total_weight += weight

            # 检查专家是否具备该能力
            capability_level = self._assess_capability_level(
                expert_capabilities,
                req.capability_name,
            )

            if capability_level >= req.min_level:
                # 计算匹配分数
                level_score = min(capability_level / req.preferred_level, 1.0)
                total_score += weight * level_score
            elif req.is_mandatory:
                # 必需能力不满足，直接返回0
                return 0.0

        return total_score / total_weight if total_weight > 0 else 0.0

    def _extract_expert_capabilities(self, expert: dict[str, Any]) -> dict[str, int]:
        """提取专家的能力和等级"""
        capabilities = {}

        # 从专业领域提取
        for specialty in expert.get("specialties", []):
            capabilities[specialty.lower()] = 4  # 专业领域默认高等级

        # 从技能提取
        for skill in expert.get("skills", []):
            capabilities[skill.lower()] = 3  # 技能默认中等级

        # 从描述中提取关键词
        description = expert.get("description", "") + " " + expert.get("bio", "")
        keywords = self._extract_keywords_from_text(description)
        for keyword in keywords:
            if keyword not in capabilities:
                capabilities[keyword] = 2  # 描述中的关键词默认较低等级

        # 基于经验年数调整等级
        experience_years = expert.get("experience_years", 0)
        experience_multiplier = min(1.0 + experience_years * 0.1, 2.0)

        for cap in capabilities:
            capabilities[cap] = min(int(capabilities[cap] * experience_multiplier), 5)

        return capabilities

    def _assess_capability_level(
        self,
        expert_capabilities: dict[str, int],
        required_capability: str,
    ) -> int:
        """评估专家在特定能力上的等级"""
        required_cap_lower = required_capability.lower()

        # 直接匹配
        if required_cap_lower in expert_capabilities:
            return expert_capabilities[required_cap_lower]

        # 模糊匹配
        for cap, level in expert_capabilities.items():
            if required_cap_lower in cap or cap in required_cap_lower:
                return level

        # 语义相关性匹配（简化版）
        related_score = self._calculate_semantic_similarity(
            required_cap_lower,
            expert_capabilities.keys(),
        )
        if related_score > 0.7:
            return 3  # 中等相关性
        elif related_score > 0.5:
            return 2  # 低相关性

        return 0  # 无相关性

    def _calculate_semantic_similarity(
        self,
        target: str,
        candidates: list[str],
    ) -> float:
        """计算语义相似性（简化实现）"""
        target_words = set(target.split())
        max_similarity = 0.0

        for candidate in candidates:
            candidate_words = set(candidate.split())
            if target_words and candidate_words:
                intersection = len(target_words & candidate_words)
                union = len(target_words | candidate_words)
                similarity = intersection / union if union > 0 else 0.0
                max_similarity = max(max_similarity, similarity)

        return max_similarity

    def _extract_keywords_from_text(self, text: str) -> list[str]:
        """从文本中提取关键词"""
        # 简化的关键词提取
        words = re.findall(r"\w+", text.lower())
        # 过滤常见停用词
        stop_words = {
            "的",
            "是",
            "在",
            "有",
            "和",
            "与",
            "或",
            "但",
            "而",
            "了",
            "着",
            "过",
            "the",
            "is",
            "in",
            "and",
            "or",
            "but",
            "with",
            "for",
            "to",
            "of",
            "a",
            "an",
        }
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        return list(set(keywords))  # 去重

    def _score_roles_for_task(
        self,
        candidates: list[dict[str, Any]],
        task_context: TaskContext,
        capability_requirements: list[CapabilityRequirement],
    ) -> list[tuple[dict[str, Any], float]]:
        """为任务对角色进行评分"""
        scored_roles = []

        for candidate in candidates:
            total_score = 0.0

            # 能力匹配分数 (40%)
            capability_score = candidate.get("_capability_score", 0.0)
            total_score += capability_score * 0.4

            # 领域相关性分数 (30%)
            domain_score = self._calculate_domain_relevance(candidate, task_context)
            total_score += domain_score * 0.3

            # 协作适应性分数 (20%)
            collaboration_score = self._calculate_collaboration_fit(
                candidate,
                task_context,
            )
            total_score += collaboration_score * 0.2

            # 声誉和经验分数 (10%)
            reputation_score = candidate.get("reputation_score", 80) / 100.0
            experience_score = min(candidate.get("experience_years", 0) / 10.0, 1.0)
            total_score += (reputation_score * 0.6 + experience_score * 0.4) * 0.1

            scored_roles.append((candidate, total_score))

        # 按分数排序
        scored_roles.sort(key=lambda x: x[1], reverse=True)
        return scored_roles

    def _calculate_domain_relevance(
        self,
        expert: dict[str, Any],
        task_context: TaskContext,
    ) -> float:
        """计算领域相关性"""
        expert_category = expert.get("category", "").lower()
        expert_specialties = [s.lower() for s in expert.get("specialties", [])]

        task_domain = task_context.domain.lower()

        # 直接分类匹配
        if task_domain in expert_category or expert_category in task_domain:
            return 1.0

        # 专业领域匹配
        for specialty in expert_specialties:
            if task_domain in specialty or specialty in task_domain:
                return 0.8

        # 语义相关性
        all_expert_text = " ".join([expert_category] + expert_specialties)
        similarity = self._calculate_semantic_similarity(task_domain, [all_expert_text])

        return similarity

    def _calculate_collaboration_fit(
        self,
        expert: dict[str, Any],
        task_context: TaskContext,
    ) -> float:
        """计算协作适应性"""
        collaboration_type = task_context.collaboration_type.lower()

        # 基于协作类型的角色特征需求
        role_traits = self.collaboration_role_mapping.get(collaboration_type, {})

        if not role_traits:
            return 0.5  # 默认中等适应性

        expert_description = (
            expert.get("description", "") + " " + expert.get("bio", "")
        ).lower()

        fit_score = 0.0
        for trait, weight in role_traits.items():
            if trait in expert_description:
                fit_score += weight

        return min(fit_score, 1.0)

    def _optimize_role_combination(
        self,
        scored_roles: list[tuple[dict[str, Any], float]],
        task_context: TaskContext,
        max_roles: int,
    ) -> list[dict[str, Any]]:
        """优化角色组合，确保多样性和协作效果"""
        if not scored_roles:
            return []

        selected_roles = []
        remaining_roles = scored_roles.copy()

        # 选择得分最高的角色
        selected_roles.append(remaining_roles.pop(0)[0])

        while len(selected_roles) < max_roles and remaining_roles:
            best_candidate = None
            best_combined_score = -1
            best_index = -1

            for i, (candidate, base_score) in enumerate(remaining_roles):
                # 计算多样性奖励
                diversity_bonus = self._calculate_diversity_bonus(
                    candidate,
                    selected_roles,
                )

                # 计算协作兼容性
                collaboration_bonus = self._calculate_collaboration_compatibility(
                    candidate,
                    selected_roles,
                    task_context,
                )

                # 综合分数
                combined_score = (
                    base_score + diversity_bonus * 0.3 + collaboration_bonus * 0.2
                )

                if combined_score > best_combined_score:
                    best_combined_score = combined_score
                    best_candidate = candidate
                    best_index = i

            if best_candidate:
                selected_roles.append(best_candidate)
                remaining_roles.pop(best_index)

        return selected_roles

    def _calculate_diversity_bonus(
        self,
        candidate: dict[str, Any],
        selected_roles: list[dict[str, Any]],
    ) -> float:
        """计算多样性奖励"""
        if not selected_roles:
            return 0.0

        candidate_category = candidate.get("category", "")
        candidate_specialties = set(candidate.get("specialties", []))

        diversity_score = 0.0

        for selected in selected_roles:
            selected_category = selected.get("category", "")
            selected_specialties = set(selected.get("specialties", []))

            # 分类多样性
            if candidate_category != selected_category:
                diversity_score += 0.5

            # 专业领域多样性
            overlap = len(candidate_specialties & selected_specialties)
            total = len(candidate_specialties | selected_specialties)
            if total > 0:
                diversity_score += (1.0 - overlap / total) * 0.5

        return diversity_score / len(selected_roles)

    def _calculate_collaboration_compatibility(
        self,
        candidate: dict[str, Any],
        selected_roles: list[dict[str, Any]],
        task_context: TaskContext,
    ) -> float:
        """计算协作兼容性"""
        # 简化实现：基于角色类型的兼容性
        compatibility_score = 0.0

        candidate_type = self._infer_role_type(candidate)

        for selected in selected_roles:
            selected_type = self._infer_role_type(selected)
            compatibility = self._get_role_type_compatibility(
                candidate_type,
                selected_type,
            )
            compatibility_score += compatibility

        return compatibility_score / len(selected_roles) if selected_roles else 0.0

    def _infer_role_type(self, expert: dict[str, Any]) -> str:
        """推断角色类型"""
        description = (
            expert.get("description", "") + " " + expert.get("bio", "")
        ).lower()
        specialties = " ".join(expert.get("specialties", [])).lower()

        all_text = description + " " + specialties

        # 简单的角色类型推断
        if any(word in all_text for word in ["分析", "研究", "数据", "analysis", "research"]):
            return "analyst"
        elif any(word in all_text for word in ["创意", "设计", "创新", "creative", "design"]):
            return "creative"
        elif any(
            word in all_text for word in ["管理", "领导", "项目", "management", "leader"]
        ):
            return "manager"
        elif any(
            word in all_text for word in ["技术", "开发", "工程", "technical", "engineer"]
        ):
            return "technical"
        elif any(word in all_text for word in ["咨询", "顾问", "consultant", "advisor"]):
            return "consultant"
        else:
            return "generalist"

    def _get_role_type_compatibility(self, type1: str, type2: str) -> float:
        """获取角色类型兼容性"""
        # 兼容性矩阵（简化版）
        compatibility_matrix = {
            ("analyst", "creative"): 0.8,
            ("analyst", "manager"): 0.9,
            ("analyst", "technical"): 0.9,
            ("creative", "manager"): 0.7,
            ("creative", "technical"): 0.6,
            ("manager", "technical"): 0.8,
            ("consultant", "analyst"): 0.9,
            ("consultant", "manager"): 0.8,
        }

        # 对称性
        key1 = (type1, type2)
        key2 = (type2, type1)

        return compatibility_matrix.get(key1, compatibility_matrix.get(key2, 0.5))

    def _initialize_task_capability_mapping(self) -> dict[str, list[tuple[str, float]]]:
        """初始化任务类型到能力的映射"""
        return {
            "分析": [
                ("数据分析", 0.9),
                ("逻辑思维", 0.8),
                ("统计学", 0.7),
                ("研究方法", 0.8),
            ],
            "创作": [
                ("创意思维", 0.9),
                ("写作能力", 0.8),
                ("内容策划", 0.7),
                ("文案撰写", 0.8),
            ],
            "咨询": [
                ("问题诊断", 0.9),
                ("解决方案", 0.8),
                ("沟通能力", 0.8),
                ("行业经验", 0.7),
            ],
            "研究": [
                ("学术研究", 0.9),
                ("文献调研", 0.8),
                ("实验设计", 0.7),
                ("论文写作", 0.8),
            ],
            "设计": [
                ("设计思维", 0.9),
                ("用户体验", 0.8),
                ("视觉设计", 0.7),
                ("原型制作", 0.6),
            ],
        }

    def _initialize_domain_expertise_mapping(
        self,
    ) -> dict[str, list[tuple[str, float]]]:
        """初始化领域专业知识映射"""
        return {
            "技术": [
                ("编程", 0.9),
                ("系统架构", 0.8),
                ("数据库", 0.7),
                ("网络安全", 0.6),
            ],
            "管理": [
                ("项目管理", 0.9),
                ("团队领导", 0.8),
                ("战略规划", 0.8),
                ("绩效管理", 0.7),
            ],
            "学术": [
                ("理论研究", 0.9),
                ("学术写作", 0.8),
                ("同行评议", 0.7),
                ("教学能力", 0.6),
            ],
            "商业": [
                ("商业分析", 0.9),
                ("市场营销", 0.8),
                ("财务管理", 0.7),
                ("商业策略", 0.8),
            ],
        }

    def _initialize_collaboration_mapping(self) -> dict[str, dict[str, float]]:
        """初始化协作类型到角色特征的映射"""
        return {
            "讨论": {
                "沟通": 0.8,
                "倾听": 0.7,
                "表达": 0.8,
            },
            "辩论": {
                "逻辑": 0.9,
                "批判": 0.8,
                "论证": 0.9,
            },
            "头脑风暴": {
                "创意": 0.9,
                "开放": 0.8,
                "想象": 0.8,
            },
            "协作": {
                "团队": 0.9,
                "合作": 0.8,
                "协调": 0.7,
            },
        }

"""对抗生成网络(GAN)认知冲突引擎
持续制造认知冲突，促进深度思考和创新突破
"""

import hashlib
import random
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

import numpy as np


class ConflictType(Enum):
    """认知冲突类型"""

    LOGICAL_PARADOX = "logical_paradox"  # 逻辑悖论
    PERSPECTIVE_CLASH = "perspective_clash"  # 视角冲突
    VALUE_CONTRADICTION = "value_contradiction"  # 价值观矛盾
    ASSUMPTION_CHALLENGE = "assumption_challenge"  # 假设挑战
    PARADIGM_SHIFT = "paradigm_shift"  # 范式转换
    TEMPORAL_INCONSISTENCY = "temporal_inconsistency"  # 时间不一致性
    SCALE_MISMATCH = "scale_mismatch"  # 尺度错配
    CONTEXT_INVERSION = "context_inversion"  # 语境反转


class ConflictIntensity(Enum):
    """冲突强度"""

    SUBTLE = 1  # 微妙冲突
    MODERATE = 2  # 中等冲突
    STRONG = 3  # 强烈冲突
    EXTREME = 4  # 极端冲突


@dataclass
class CognitiveConflict:
    """认知冲突"""

    id: str
    conflict_type: ConflictType
    intensity: ConflictIntensity
    source_concept: str
    target_concept: str
    conflict_description: str
    resolution_hints: list[str]
    cognitive_load: float  # 认知负荷 0-1
    creativity_potential: float  # 创新潜力 0-1
    timestamp: str
    context: dict[str, Any]

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class ConflictPattern:
    """冲突模式"""

    pattern_id: str
    name: str
    description: str
    trigger_conditions: list[str]
    conflict_templates: list[dict[str, Any]]
    effectiveness_score: float
    usage_count: int = 0


class CognitiveConflictGenerator:
    """认知冲突生成器（生成器网络）"""

    def __init__(self):
        self.conflict_patterns = self._initialize_conflict_patterns()
        self.concept_embeddings = {}
        self.generation_history = []
        self.creativity_threshold = 0.7

    def _initialize_conflict_patterns(self) -> list[ConflictPattern]:
        """初始化冲突模式库"""
        patterns = [
            ConflictPattern(
                pattern_id="logical_paradox_1",
                name="自指悖论",
                description="创造自我引用的逻辑矛盾",
                trigger_conditions=["self_reference", "absolute_statement"],
                conflict_templates=[
                    {
                        "template": "如果{concept}是绝对的，那么{concept}能否质疑自己的绝对性？",
                        "variables": ["concept"],
                        "intensity": ConflictIntensity.STRONG,
                    },
                ],
                effectiveness_score=0.85,
            ),
            ConflictPattern(
                pattern_id="perspective_clash_1",
                name="多维视角冲突",
                description="从不同维度审视同一问题",
                trigger_conditions=["multiple_stakeholders", "complex_system"],
                conflict_templates=[
                    {
                        "template": "从{perspective1}角度看{concept}是{value1}，但从{perspective2}角度看却是{value2}",
                        "variables": [
                            "perspective1",
                            "perspective2",
                            "concept",
                            "value1",
                            "value2",
                        ],
                        "intensity": ConflictIntensity.MODERATE,
                    },
                ],
                effectiveness_score=0.78,
            ),
            ConflictPattern(
                pattern_id="scale_mismatch_1",
                name="尺度错配冲突",
                description="在不同尺度下的矛盾表现",
                trigger_conditions=["multi_scale_system", "emergent_properties"],
                conflict_templates=[
                    {
                        "template": "在{scale1}尺度上{concept}表现为{behavior1}，但在{scale2}尺度上却表现为{behavior2}",
                        "variables": [
                            "scale1",
                            "scale2",
                            "concept",
                            "behavior1",
                            "behavior2",
                        ],
                        "intensity": ConflictIntensity.STRONG,
                    },
                ],
                effectiveness_score=0.82,
            ),
            ConflictPattern(
                pattern_id="temporal_inconsistency_1",
                name="时间悖论",
                description="时间维度上的逻辑冲突",
                trigger_conditions=["temporal_dependency", "causality"],
                conflict_templates=[
                    {
                        "template": "如果{action}在{time1}导致{result1}，那么{result1}如何能在{time2}影响{action}？",
                        "variables": ["action", "time1", "result1", "time2"],
                        "intensity": ConflictIntensity.EXTREME,
                    },
                ],
                effectiveness_score=0.90,
            ),
            ConflictPattern(
                pattern_id="value_contradiction_1",
                name="价值观冲突",
                description="核心价值观之间的矛盾",
                trigger_conditions=["ethical_dilemma", "competing_values"],
                conflict_templates=[
                    {
                        "template": "追求{value1}必然会损害{value2}，但{value2}同样重要，如何平衡？",
                        "variables": ["value1", "value2"],
                        "intensity": ConflictIntensity.STRONG,
                    },
                ],
                effectiveness_score=0.88,
            ),
        ]
        return patterns

    def generate_conflict(
        self,
        context: dict[str, Any],
        target_intensity: ConflictIntensity = ConflictIntensity.MODERATE,
    ) -> CognitiveConflict:
        """生成认知冲突"""
        # 分析上下文，选择合适的冲突模式
        suitable_patterns = self._select_patterns(context, target_intensity)

        if not suitable_patterns:
            # 如果没有合适的模式，创建新的冲突
            return self._create_novel_conflict(context, target_intensity)

        # 选择最佳模式
        selected_pattern = self._select_best_pattern(suitable_patterns, context)

        # 基于模式生成具体冲突
        conflict = self._instantiate_conflict(
            selected_pattern,
            context,
            target_intensity,
        )

        # 记录生成历史
        self.generation_history.append(conflict)
        selected_pattern.usage_count += 1

        return conflict

    def _select_patterns(
        self,
        context: dict[str, Any],
        target_intensity: ConflictIntensity,
    ) -> list[ConflictPattern]:
        """选择合适的冲突模式"""
        suitable_patterns = []

        context_keywords = set()
        for key, value in context.items():
            if isinstance(value, str):
                context_keywords.update(value.lower().split())
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        context_keywords.update(item.lower().split())

        for pattern in self.conflict_patterns:
            # 检查触发条件
            trigger_match = any(
                trigger in context_keywords for trigger in pattern.trigger_conditions
            )

            # 检查强度匹配
            pattern_intensities = [
                template.get("intensity", ConflictIntensity.MODERATE)
                for template in pattern.conflict_templates
            ]
            intensity_match = target_intensity in pattern_intensities

            if trigger_match or intensity_match:
                suitable_patterns.append(pattern)

        return suitable_patterns

    def _select_best_pattern(
        self,
        patterns: list[ConflictPattern],
        context: dict[str, Any],
    ) -> ConflictPattern:
        """选择最佳冲突模式"""
        if len(patterns) == 1:
            return patterns[0]

        # 计算每个模式的适配分数
        scores = []
        for pattern in patterns:
            score = pattern.effectiveness_score

            # 降低过度使用的模式的分数
            usage_penalty = min(pattern.usage_count * 0.1, 0.5)
            score -= usage_penalty

            # 增加新颖性奖励
            if pattern.usage_count == 0:
                score += 0.2

            scores.append(score)

        # 选择分数最高的模式
        best_index = np.argmax(scores)
        return patterns[best_index]

    def _instantiate_conflict(
        self,
        pattern: ConflictPattern,
        context: dict[str, Any],
        target_intensity: ConflictIntensity,
    ) -> CognitiveConflict:
        """实例化冲突"""
        # 选择合适的模板
        suitable_templates = [
            template
            for template in pattern.conflict_templates
            if template.get("intensity", ConflictIntensity.MODERATE) == target_intensity
        ]

        if not suitable_templates:
            suitable_templates = pattern.conflict_templates

        template = random.choice(suitable_templates)

        # 填充模板变量
        filled_description = self._fill_template(template, context)

        # 生成冲突ID
        conflict_id = hashlib.md5(
            f"{pattern.pattern_id}_{filled_description}_{datetime.now().isoformat()}".encode(),
        ).hexdigest()[:16]

        # 计算认知负荷和创新潜力
        cognitive_load = self._calculate_cognitive_load(template, context)
        creativity_potential = self._calculate_creativity_potential(pattern, context)

        # 生成解决提示
        resolution_hints = self._generate_resolution_hints(pattern, context)

        conflict = CognitiveConflict(
            id=conflict_id,
            conflict_type=ConflictType(
                pattern.pattern_id.split("_")[0]
                + "_"
                + pattern.pattern_id.split("_")[1],
            ),
            intensity=target_intensity,
            source_concept=context.get("primary_concept", "unknown"),
            target_concept=context.get("secondary_concept", "unknown"),
            conflict_description=filled_description,
            resolution_hints=resolution_hints,
            cognitive_load=cognitive_load,
            creativity_potential=creativity_potential,
            timestamp=datetime.now().isoformat(),
            context=context,
        )

        return conflict

    def _fill_template(self, template: dict[str, Any], context: dict[str, Any]) -> str:
        """填充模板变量"""
        template_str = template["template"]
        variables = template.get("variables", [])

        # 从上下文中提取变量值
        variable_values = {}

        for var in variables:
            if var in context:
                variable_values[var] = context[var]
            else:
                # 生成默认值
                variable_values[var] = self._generate_default_value(var, context)

        # 填充模板
        try:
            filled_template = template_str.format(**variable_values)
        except KeyError:
            # 如果有缺失的变量，使用占位符
            filled_template = template_str
            for var in variables:
                placeholder = f"{{{var}}}"
                if placeholder in filled_template:
                    filled_template = filled_template.replace(
                        placeholder,
                        variable_values.get(var, f"[{var}]"),
                    )

        return filled_template

    def _generate_default_value(self, variable: str, context: dict[str, Any]) -> str:
        """生成默认变量值"""
        default_values = {
            "concept": context.get("topic", "核心概念"),
            "perspective1": "技术视角",
            "perspective2": "人文视角",
            "value1": "效率",
            "value2": "公平",
            "scale1": "微观",
            "scale2": "宏观",
            "time1": "现在",
            "time2": "未来",
            "action": "决策",
            "result1": "预期结果",
            "behavior1": "有序",
            "behavior2": "混沌",
        }

        return default_values.get(variable, f"[{variable}]")

    def _calculate_cognitive_load(
        self,
        template: dict[str, Any],
        context: dict[str, Any],
    ) -> float:
        """计算认知负荷"""
        base_load = 0.5

        # 基于模板复杂度
        template_complexity = len(template.get("variables", []))
        complexity_load = min(template_complexity * 0.1, 0.3)

        # 基于上下文复杂度
        context_complexity = len(context)
        context_load = min(context_complexity * 0.05, 0.2)

        total_load = base_load + complexity_load + context_load
        return min(total_load, 1.0)

    def _calculate_creativity_potential(
        self,
        pattern: ConflictPattern,
        context: dict[str, Any],
    ) -> float:
        """计算创新潜力"""
        base_potential = pattern.effectiveness_score

        # 新颖性奖励
        novelty_bonus = (
            0.2
            if pattern.usage_count == 0
            else max(0, 0.2 - pattern.usage_count * 0.02)
        )

        # 上下文丰富度奖励
        context_richness = min(len(context) * 0.05, 0.2)

        total_potential = base_potential + novelty_bonus + context_richness
        return min(total_potential, 1.0)

    def _generate_resolution_hints(
        self,
        pattern: ConflictPattern,
        context: dict[str, Any],
    ) -> list[str]:
        """生成解决提示"""
        hints = [
            "尝试从更高维度审视这个冲突",
            "考虑是否存在隐含的假设需要质疑",
            "探索冲突双方是否可以在新的框架下共存",
            "思考时间或空间维度是否影响了判断",
        ]

        # 基于模式类型添加特定提示
        pattern_specific_hints = {
            "logical_paradox": ["检查逻辑前提是否完备", "考虑引入新的逻辑层次"],
            "perspective_clash": ["寻找更包容的视角", "探索视角背后的价值观"],
            "scale_mismatch": ["考虑跨尺度的涌现性质", "寻找尺度间的桥接机制"],
            "temporal_inconsistency": ["重新审视因果关系", "考虑非线性时间模型"],
            "value_contradiction": ["探索价值观的层次结构", "寻找更高层次的统一原则"],
        }

        pattern_type = pattern.pattern_id.split("_")[0]
        if pattern_type in pattern_specific_hints:
            hints.extend(pattern_specific_hints[pattern_type])

        return random.sample(hints, min(3, len(hints)))

    def _create_novel_conflict(
        self,
        context: dict[str, Any],
        target_intensity: ConflictIntensity,
    ) -> CognitiveConflict:
        """创建新颖的冲突"""
        # 基于上下文创建新的冲突
        primary_concept = context.get("primary_concept", "核心概念")
        secondary_concept = context.get("secondary_concept", "相关概念")

        novel_conflicts = [
            f"{primary_concept}的存在是否否定了{secondary_concept}的必要性？",
            f"如果{primary_concept}是真理，那么{secondary_concept}还有意义吗？",
            f"{primary_concept}和{secondary_concept}能否同时为真？",
            f"追求{primary_concept}是否必然导致{secondary_concept}的消失？",
        ]

        conflict_description = random.choice(novel_conflicts)

        conflict_id = hashlib.md5(
            f"novel_{conflict_description}_{datetime.now().isoformat()}".encode(),
        ).hexdigest()[:16]

        conflict = CognitiveConflict(
            id=conflict_id,
            conflict_type=ConflictType.LOGICAL_PARADOX,
            intensity=target_intensity,
            source_concept=primary_concept,
            target_concept=secondary_concept,
            conflict_description=conflict_description,
            resolution_hints=["这是一个新颖的冲突，需要创新性思考"],
            cognitive_load=0.7,
            creativity_potential=0.9,
            timestamp=datetime.now().isoformat(),
            context=context,
        )

        return conflict


class CognitiveConflictDiscriminator:
    """认知冲突判别器（判别器网络）"""

    def __init__(self):
        self.evaluation_criteria = self._initialize_evaluation_criteria()
        self.conflict_database = []  # 真实冲突数据库
        self.evaluation_history = []
        self.learning_rate = 0.01

    def _initialize_evaluation_criteria(self) -> dict[str, float]:
        """初始化评估标准"""
        return {
            "logical_consistency": 0.25,  # 逻辑一致性
            "cognitive_challenge": 0.30,  # 认知挑战性
            "resolution_difficulty": 0.20,  # 解决难度
            "creativity_stimulus": 0.25,  # 创新刺激性
        }

    def evaluate_conflict(self, conflict: CognitiveConflict) -> dict[str, float]:
        """评估认知冲突的质量"""
        scores = {}

        # 逻辑一致性评估
        scores["logical_consistency"] = self._evaluate_logical_consistency(conflict)

        # 认知挑战性评估
        scores["cognitive_challenge"] = self._evaluate_cognitive_challenge(conflict)

        # 解决难度评估
        scores["resolution_difficulty"] = self._evaluate_resolution_difficulty(conflict)

        # 创新刺激性评估
        scores["creativity_stimulus"] = self._evaluate_creativity_stimulus(conflict)

        # 计算综合分数
        total_score = sum(
            scores[criterion] * weight
            for criterion, weight in self.evaluation_criteria.items()
        )

        scores["total_score"] = total_score
        scores["is_effective"] = total_score > 0.7  # 有效性阈值

        # 记录评估历史
        evaluation_record = {
            "conflict_id": conflict.id,
            "scores": scores,
            "timestamp": datetime.now().isoformat(),
        }
        self.evaluation_history.append(evaluation_record)

        return scores

    def _evaluate_logical_consistency(self, conflict: CognitiveConflict) -> float:
        """评估逻辑一致性"""
        description = conflict.conflict_description.lower()

        # 检查逻辑连接词
        logical_connectors = ["如果", "那么", "因为", "所以", "但是", "然而", "虽然"]
        connector_count = sum(
            1 for connector in logical_connectors if connector in description
        )

        # 检查逻辑结构
        has_premise = any(word in description for word in ["假设", "前提", "条件"])
        has_conclusion = any(word in description for word in ["结论", "结果", "导致"])
        has_contradiction = any(word in description for word in ["矛盾", "冲突", "悖论"])

        # 计算逻辑一致性分数
        structure_score = (has_premise + has_conclusion + has_contradiction) / 3
        connector_score = min(connector_count / 3, 1.0)

        return structure_score * 0.7 + connector_score * 0.3

    def _evaluate_cognitive_challenge(self, conflict: CognitiveConflict) -> float:
        """评估认知挑战性"""
        # 基于冲突强度
        intensity_score = conflict.intensity.value / 4.0

        # 基于认知负荷
        load_score = conflict.cognitive_load

        # 基于概念复杂度
        concept_complexity = self._calculate_concept_complexity(
            conflict.source_concept,
            conflict.target_concept,
        )

        # 基于描述长度和复杂度
        description_complexity = min(len(conflict.conflict_description) / 200, 1.0)

        challenge_score = (
            intensity_score * 0.3
            + load_score * 0.3
            + concept_complexity * 0.2
            + description_complexity * 0.2
        )

        return min(challenge_score, 1.0)

    def _evaluate_resolution_difficulty(self, conflict: CognitiveConflict) -> float:
        """评估解决难度"""
        # 基于提示数量（提示越少，难度越高）
        hint_factor = max(0.2, 1.0 - len(conflict.resolution_hints) * 0.2)

        # 基于冲突类型的固有难度
        type_difficulty = {
            ConflictType.LOGICAL_PARADOX: 0.9,
            ConflictType.TEMPORAL_INCONSISTENCY: 0.8,
            ConflictType.PARADIGM_SHIFT: 0.85,
            ConflictType.VALUE_CONTRADICTION: 0.7,
            ConflictType.PERSPECTIVE_CLASH: 0.6,
            ConflictType.ASSUMPTION_CHALLENGE: 0.65,
            ConflictType.SCALE_MISMATCH: 0.75,
            ConflictType.CONTEXT_INVERSION: 0.7,
        }

        type_score = type_difficulty.get(conflict.conflict_type, 0.5)

        # 基于上下文复杂度
        context_complexity = min(len(conflict.context) / 10, 1.0)

        difficulty_score = (
            hint_factor * 0.4 + type_score * 0.4 + context_complexity * 0.2
        )

        return min(difficulty_score, 1.0)

    def _evaluate_creativity_stimulus(self, conflict: CognitiveConflict) -> float:
        """评估创新刺激性"""
        # 基于创新潜力
        potential_score = conflict.creativity_potential

        # 基于新颖性（与历史冲突的相似度）
        novelty_score = self._calculate_novelty(conflict)

        # 基于跨领域性
        cross_domain_score = self._calculate_cross_domain_potential(conflict)

        # 基于开放性（是否有多种解决方案）
        openness_score = self._calculate_openness(conflict)

        creativity_score = (
            potential_score * 0.3
            + novelty_score * 0.3
            + cross_domain_score * 0.2
            + openness_score * 0.2
        )

        return min(creativity_score, 1.0)

    def _calculate_concept_complexity(self, concept1: str, concept2: str) -> float:
        """计算概念复杂度"""
        # 简化的复杂度计算
        total_length = len(concept1) + len(concept2)
        word_count = len(concept1.split()) + len(concept2.split())

        length_score = min(total_length / 50, 1.0)
        word_score = min(word_count / 10, 1.0)

        return (length_score + word_score) / 2

    def _calculate_novelty(self, conflict: CognitiveConflict) -> float:
        """计算新颖性"""
        if not self.conflict_database:
            return 1.0  # 如果没有历史数据，认为是新颖的

        # 计算与历史冲突的相似度
        similarities = []
        for historical_conflict in self.conflict_database[-50:]:  # 只比较最近50个
            similarity = self._calculate_conflict_similarity(
                conflict,
                historical_conflict,
            )
            similarities.append(similarity)

        if similarities:
            max_similarity = max(similarities)
            novelty = 1.0 - max_similarity
        else:
            novelty = 1.0

        return novelty

    def _calculate_conflict_similarity(
        self,
        conflict1: CognitiveConflict,
        conflict2: CognitiveConflict,
    ) -> float:
        """计算两个冲突的相似度"""
        # 类型相似度
        type_similarity = (
            1.0 if conflict1.conflict_type == conflict2.conflict_type else 0.0
        )

        # 描述相似度（简化的文本相似度）
        desc1_words = set(conflict1.conflict_description.lower().split())
        desc2_words = set(conflict2.conflict_description.lower().split())

        if desc1_words and desc2_words:
            intersection = desc1_words.intersection(desc2_words)
            union = desc1_words.union(desc2_words)
            desc_similarity = len(intersection) / len(union)
        else:
            desc_similarity = 0.0

        # 概念相似度
        concept_similarity = 0.0
        if (
            conflict1.source_concept == conflict2.source_concept
            or conflict1.target_concept == conflict2.target_concept
        ):
            concept_similarity = 0.5
        if (
            conflict1.source_concept == conflict2.source_concept
            and conflict1.target_concept == conflict2.target_concept
        ):
            concept_similarity = 1.0

        # 综合相似度
        total_similarity = (
            type_similarity * 0.3 + desc_similarity * 0.5 + concept_similarity * 0.2
        )

        return total_similarity

    def _calculate_cross_domain_potential(self, conflict: CognitiveConflict) -> float:
        """计算跨领域潜力"""
        # 检查是否涉及多个领域
        domains = ["技术", "伦理", "法律", "商业", "社会", "心理", "哲学", "科学"]

        description = conflict.conflict_description.lower()
        context_text = " ".join(str(v) for v in conflict.context.values()).lower()

        involved_domains = []
        for domain in domains:
            if domain.lower() in description or domain.lower() in context_text:
                involved_domains.append(domain)

        # 跨领域分数基于涉及的领域数量
        cross_domain_score = min(len(involved_domains) / 3, 1.0)

        return cross_domain_score

    def _calculate_openness(self, conflict: CognitiveConflict) -> float:
        """计算开放性（多解性）"""
        # 基于冲突描述中的开放性词汇
        open_words = ["如何", "是否", "能否", "可能", "或许", "也许", "多种", "不同"]

        description = conflict.conflict_description.lower()
        open_word_count = sum(1 for word in open_words if word in description)

        # 基于提示的多样性
        hint_diversity = len(set(conflict.resolution_hints)) / max(
            len(conflict.resolution_hints),
            1,
        )

        openness_score = min(open_word_count / 3, 1.0) * 0.6 + hint_diversity * 0.4

        return openness_score

    def add_to_database(self, conflict: CognitiveConflict):
        """添加冲突到数据库"""
        self.conflict_database.append(conflict)

        # 限制数据库大小
        if len(self.conflict_database) > 1000:
            self.conflict_database = self.conflict_database[-1000:]

    def get_evaluation_statistics(self) -> dict[str, Any]:
        """获取评估统计信息"""
        if not self.evaluation_history:
            return {"message": "No evaluation history available"}

        # 计算各项指标的平均分
        criteria_averages = {}
        for criterion in self.evaluation_criteria.keys():
            scores = [
                eval_record["scores"][criterion]
                for eval_record in self.evaluation_history
            ]
            criteria_averages[f"avg_{criterion}"] = sum(scores) / len(scores)

        # 计算有效冲突比例
        effective_conflicts = sum(
            1
            for eval_record in self.evaluation_history
            if eval_record["scores"]["is_effective"]
        )
        effectiveness_rate = effective_conflicts / len(self.evaluation_history)

        return {
            "total_evaluations": len(self.evaluation_history),
            "effectiveness_rate": effectiveness_rate,
            "database_size": len(self.conflict_database),
            **criteria_averages,
        }


class CognitiveConflictGAN:
    """认知冲突对抗生成网络主控制器"""

    def __init__(self):
        self.generator = CognitiveConflictGenerator()
        self.discriminator = CognitiveConflictDiscriminator()
        self.training_iterations = 0
        self.performance_history = []
        self.active_conflicts = []
        self.conflict_resolution_feedback = []

    def generate_continuous_conflicts(
        self,
        context: dict[str, Any],
        duration_minutes: int = 60,
        conflict_interval_minutes: int = 10,
    ) -> list[CognitiveConflict]:
        """持续生成认知冲突"""
        print(f"🔄 开始持续生成认知冲突，持续时间: {duration_minutes}分钟")

        generated_conflicts = []
        total_intervals = duration_minutes // conflict_interval_minutes

        for interval in range(total_intervals):
            print(f"📍 生成第 {interval + 1}/{total_intervals} 轮冲突")

            # 动态调整冲突强度
            target_intensity = self._calculate_adaptive_intensity(
                interval,
                total_intervals,
            )

            # 更新上下文（模拟环境变化）
            updated_context = self._evolve_context(context, interval)

            # 生成冲突
            conflict = self.generator.generate_conflict(
                updated_context,
                target_intensity,
            )

            # 评估冲突质量
            evaluation = self.discriminator.evaluate_conflict(conflict)

            # 如果冲突质量足够高，添加到活跃冲突列表
            if evaluation["is_effective"]:
                generated_conflicts.append(conflict)
                self.active_conflicts.append(conflict)
                self.discriminator.add_to_database(conflict)

                print(f"✅ 生成高质量冲突: {conflict.conflict_description[:50]}...")
                print(f"   质量分数: {evaluation['total_score']:.3f}")
            else:
                print("⚠️ 冲突质量不足，重新生成...")
                # 重新生成
                conflict = self._regenerate_improved_conflict(
                    updated_context,
                    target_intensity,
                )
                if conflict:
                    generated_conflicts.append(conflict)
                    self.active_conflicts.append(conflict)

            # 对抗训练
            self._adversarial_training_step(conflict, evaluation)

        print(f"🎉 持续生成完成，共生成 {len(generated_conflicts)} 个有效冲突")
        return generated_conflicts

    def _calculate_adaptive_intensity(
        self,
        current_interval: int,
        total_intervals: int,
    ) -> ConflictIntensity:
        """计算自适应冲突强度"""
        # 基于时间进度调整强度
        progress = current_interval / total_intervals

        # 强度变化模式：开始温和，中期激烈，后期回归
        if progress < 0.3:
            # 初期：温和冲突
            intensity_value = 1 + int(progress * 3)
        elif progress < 0.7:
            # 中期：强烈冲突
            intensity_value = 3 + int((progress - 0.3) * 2.5)
        else:
            # 后期：回归温和
            intensity_value = max(1, 4 - int((progress - 0.7) * 6))

        # 基于历史表现调整
        if self.performance_history:
            recent_performance = np.mean(
                [p["effectiveness"] for p in self.performance_history[-5:]],
            )
            if recent_performance < 0.6:
                intensity_value = max(1, intensity_value - 1)  # 降低强度
            elif recent_performance > 0.8:
                intensity_value = min(4, intensity_value + 1)  # 提高强度

        return ConflictIntensity(intensity_value)

    def _evolve_context(
        self,
        base_context: dict[str, Any],
        interval: int,
    ) -> dict[str, Any]:
        """演化上下文环境"""
        evolved_context = base_context.copy()

        # 添加时间维度
        evolved_context["time_interval"] = interval
        evolved_context["evolution_stage"] = self._get_evolution_stage(interval)

        # 引入随机变化
        if random.random() < 0.3:  # 30%概率引入新元素
            new_elements = [
                "突发事件",
                "技术突破",
                "政策变化",
                "社会趋势",
                "竞争压力",
                "资源约束",
                "用户反馈",
                "市场变化",
            ]
            evolved_context["new_factor"] = random.choice(new_elements)

        # 基于历史冲突调整上下文
        if self.active_conflicts:
            recent_conflicts = self.active_conflicts[-3:]
            common_themes = self._extract_common_themes(recent_conflicts)
            if common_themes:
                evolved_context["emerging_themes"] = common_themes

        return evolved_context

    def _get_evolution_stage(self, interval: int) -> str:
        """获取演化阶段"""
        stages = ["探索期", "发展期", "成熟期", "转型期", "创新期"]
        stage_index = interval % len(stages)
        return stages[stage_index]

    def _extract_common_themes(self, conflicts: list[CognitiveConflict]) -> list[str]:
        """提取共同主题"""
        all_words = []
        for conflict in conflicts:
            words = conflict.conflict_description.lower().split()
            all_words.extend(words)

        # 简单的词频统计
        word_freq = {}
        for word in all_words:
            if len(word) > 3:  # 过滤短词
                word_freq[word] = word_freq.get(word, 0) + 1

        # 返回高频词作为主题
        common_themes = [word for word, freq in word_freq.items() if freq >= 2]
        return common_themes[:3]  # 最多返回3个主题

    def _regenerate_improved_conflict(
        self,
        context: dict[str, Any],
        target_intensity: ConflictIntensity,
    ) -> CognitiveConflict:
        """重新生成改进的冲突"""
        # 分析之前失败的原因
        if self.discriminator.evaluation_history:
            last_evaluation = self.discriminator.evaluation_history[-1]
            weak_criteria = [
                criterion
                for criterion, score in last_evaluation["scores"].items()
                if isinstance(score, (int, float)) and score < 0.5
            ]

            # 基于弱项调整生成策略
            if "logical_consistency" in weak_criteria:
                context["focus"] = "逻辑结构"
            elif "cognitive_challenge" in weak_criteria:
                context["focus"] = "认知挑战"
            elif "creativity_stimulus" in weak_criteria:
                context["focus"] = "创新刺激"

        # 重新生成
        improved_conflict = self.generator.generate_conflict(context, target_intensity)

        # 再次评估
        evaluation = self.discriminator.evaluate_conflict(improved_conflict)

        if evaluation["is_effective"]:
            return improved_conflict
        else:
            return None

    def _adversarial_training_step(
        self,
        conflict: CognitiveConflict,
        evaluation: dict[str, float],
    ):
        """对抗训练步骤"""
        self.training_iterations += 1

        # 记录性能
        performance_record = {
            "iteration": self.training_iterations,
            "conflict_id": conflict.id,
            "effectiveness": evaluation["total_score"],
            "generator_loss": 1.0 - evaluation["total_score"],  # 生成器损失
            "discriminator_accuracy": evaluation["total_score"],  # 判别器准确度
            "timestamp": datetime.now().isoformat(),
        }

        self.performance_history.append(performance_record)

        # 更新生成器（基于判别器反馈）
        self._update_generator_weights(evaluation)

        # 更新判别器（基于新数据）
        self._update_discriminator_weights(conflict, evaluation)

        # 每10次迭代进行一次深度分析
        if self.training_iterations % 10 == 0:
            self._deep_analysis_and_adjustment()

    def _update_generator_weights(self, evaluation: dict[str, float]):
        """更新生成器权重"""
        # 基于评估结果调整生成器的模式权重
        for pattern in self.generator.conflict_patterns:
            if pattern.usage_count > 0:
                # 计算该模式的平均效果
                pattern_evaluations = [
                    eval_record
                    for eval_record in self.discriminator.evaluation_history
                    if any(
                        pattern.pattern_id in conflict.id
                        for conflict in self.active_conflicts
                    )
                ]

                if pattern_evaluations:
                    avg_effectiveness = np.mean(
                        [
                            eval_record["scores"]["total_score"]
                            for eval_record in pattern_evaluations
                        ],
                    )

                    # 调整效果分数
                    adjustment = (
                        avg_effectiveness - 0.7
                    ) * self.discriminator.learning_rate
                    pattern.effectiveness_score = max(
                        0.1,
                        min(1.0, pattern.effectiveness_score + adjustment),
                    )

    def _update_discriminator_weights(
        self,
        conflict: CognitiveConflict,
        evaluation: dict[str, float],
    ):
        """更新判别器权重"""
        # 基于用户反馈调整评估标准权重
        if self.conflict_resolution_feedback:
            recent_feedback = self.conflict_resolution_feedback[-10:]  # 最近10个反馈

            # 分析反馈模式
            feedback_analysis = self._analyze_feedback_patterns(recent_feedback)

            # 调整权重
            for criterion, adjustment in feedback_analysis.items():
                if criterion in self.discriminator.evaluation_criteria:
                    current_weight = self.discriminator.evaluation_criteria[criterion]
                    new_weight = max(0.05, min(0.5, current_weight + adjustment))
                    self.discriminator.evaluation_criteria[criterion] = new_weight

            # 重新归一化权重
            total_weight = sum(self.discriminator.evaluation_criteria.values())
            for criterion in self.discriminator.evaluation_criteria:
                self.discriminator.evaluation_criteria[criterion] /= total_weight

    def _analyze_feedback_patterns(
        self,
        feedback_list: list[dict[str, Any]],
    ) -> dict[str, float]:
        """分析反馈模式"""
        adjustments = {
            "logical_consistency": 0.0,
            "cognitive_challenge": 0.0,
            "resolution_difficulty": 0.0,
            "creativity_stimulus": 0.0,
        }

        for feedback in feedback_list:
            if feedback.get("user_satisfaction", 0) > 0.8:
                # 高满意度：增强相关标准权重
                dominant_criterion = feedback.get(
                    "dominant_criterion",
                    "cognitive_challenge",
                )
                adjustments[dominant_criterion] += 0.01
            elif feedback.get("user_satisfaction", 0) < 0.4:
                # 低满意度：降低相关标准权重
                dominant_criterion = feedback.get(
                    "dominant_criterion",
                    "cognitive_challenge",
                )
                adjustments[dominant_criterion] -= 0.01

        return adjustments

    def _deep_analysis_and_adjustment(self):
        """深度分析和调整"""
        print(f"🔍 进行第 {self.training_iterations // 10} 次深度分析...")

        # 分析生成器性能趋势
        recent_performance = self.performance_history[-10:]
        effectiveness_trend = [p["effectiveness"] for p in recent_performance]

        if len(effectiveness_trend) >= 5:
            trend_slope = np.polyfit(
                range(len(effectiveness_trend)),
                effectiveness_trend,
                1,
            )[0]

            if trend_slope < -0.01:  # 性能下降
                print("📉 检测到性能下降，调整生成策略...")
                self._adjust_generation_strategy("improve")
            elif trend_slope > 0.01:  # 性能提升
                print("📈 性能提升良好，保持当前策略...")
                self._adjust_generation_strategy("maintain")
            else:
                print("📊 性能稳定，尝试探索新策略...")
                self._adjust_generation_strategy("explore")

    def _adjust_generation_strategy(self, strategy: str):
        """调整生成策略"""
        if strategy == "improve":
            # 提高创新阈值，降低生成频率
            self.generator.creativity_threshold += 0.1

        elif strategy == "maintain":
            # 保持当前设置
            pass

        elif strategy == "explore":
            # 降低创新阈值，增加随机性
            self.generator.creativity_threshold = max(
                0.5,
                self.generator.creativity_threshold - 0.05,
            )

    def add_resolution_feedback(
        self,
        conflict_id: str,
        user_satisfaction: float,
        resolution_time: float,
        creativity_boost: float,
    ):
        """添加解决反馈"""
        feedback = {
            "conflict_id": conflict_id,
            "user_satisfaction": user_satisfaction,
            "resolution_time": resolution_time,
            "creativity_boost": creativity_boost,
            "timestamp": datetime.now().isoformat(),
        }

        self.conflict_resolution_feedback.append(feedback)

        # 限制反馈历史大小
        if len(self.conflict_resolution_feedback) > 100:
            self.conflict_resolution_feedback = self.conflict_resolution_feedback[-100:]

    def get_system_status(self) -> dict[str, Any]:
        """获取系统状态"""
        generator_stats = {
            "total_patterns": len(self.generator.conflict_patterns),
            "generation_history": len(self.generator.generation_history),
            "creativity_threshold": self.generator.creativity_threshold,
        }

        discriminator_stats = self.discriminator.get_evaluation_statistics()

        performance_stats = {}
        if self.performance_history:
            recent_performance = self.performance_history[-10:]
            performance_stats = {
                "avg_effectiveness": np.mean(
                    [p["effectiveness"] for p in recent_performance],
                ),
                "training_iterations": self.training_iterations,
                "performance_trend": "improving"
                if len(recent_performance) >= 2
                and recent_performance[-1]["effectiveness"]
                > recent_performance[0]["effectiveness"]
                else "stable",
            }

        return {
            "active_conflicts": len(self.active_conflicts),
            "total_feedback": len(self.conflict_resolution_feedback),
            "generator_stats": generator_stats,
            "discriminator_stats": discriminator_stats,
            "performance_stats": performance_stats,
            "system_health": "optimal"
            if performance_stats.get("avg_effectiveness", 0) > 0.7
            else "needs_attention",
        }

#!/usr/bin/env python3
"""论证分析和评估系统

对辩论中的论证进行深度分析、质量评估和逻辑验证。
支持多维度评估、实时反馈和智能建议。

核心功能：
- 论证结构分析
- 逻辑一致性检查
- 证据质量评估
- 论证强度计算
- 反驳关系识别
- 共识点检测
"""

import asyncio
import re
import uuid
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from .debate_flow_definition import DebateContribution, DebateSession


class ArgumentType(Enum):
    """论证类型"""

    CLAIM = "claim"  # 主张
    EVIDENCE = "evidence"  # 证据
    REASONING = "reasoning"  # 推理
    REBUTTAL = "rebuttal"  # 反驳
    SUPPORT = "support"  # 支持
    CLARIFICATION = "clarification"  # 澄清
    QUESTION = "question"  # 提问
    SUMMARY = "summary"  # 总结
    CONSENSUS = "consensus"  # 共识


class LogicalFallacy(Enum):
    """逻辑谬误类型"""

    AD_HOMINEM = "ad_hominem"  # 人身攻击
    STRAW_MAN = "straw_man"  # 稻草人谬误
    FALSE_DILEMMA = "false_dilemma"  # 虚假二分法
    CIRCULAR_REASONING = "circular_reasoning"  # 循环论证
    APPEAL_TO_AUTHORITY = "appeal_to_authority"  # 诉诸权威
    SLIPPERY_SLOPE = "slippery_slope"  # 滑坡谬误
    HASTY_GENERALIZATION = "hasty_generalization"  # 草率概括
    RED_HERRING = "red_herring"  # 转移话题
    BANDWAGON = "bandwagon"  # 从众谬误
    NONE = "none"  # 无谬误


class EvidenceType(Enum):
    """证据类型"""

    STATISTICAL = "statistical"  # 统计数据
    EXPERT_OPINION = "expert_opinion"  # 专家意见
    CASE_STUDY = "case_study"  # 案例研究
    RESEARCH_PAPER = "research_paper"  # 研究论文
    HISTORICAL = "historical"  # 历史事实
    ANECDOTAL = "anecdotal"  # 轶事证据
    LOGICAL = "logical"  # 逻辑推理
    EMPIRICAL = "empirical"  # 经验证据


@dataclass
class ArgumentComponent:
    """论证组件"""

    component_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    argument_type: ArgumentType = ArgumentType.CLAIM
    confidence: float = 0.0  # 置信度 0-1
    evidence_type: Optional[EvidenceType] = None
    source: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ArgumentStructure:
    """论证结构"""

    argument_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    main_claim: str = ""
    premises: List[ArgumentComponent] = field(default_factory=list)
    evidence: List[ArgumentComponent] = field(default_factory=list)
    reasoning: List[ArgumentComponent] = field(default_factory=list)
    rebuttals: List[ArgumentComponent] = field(default_factory=list)
    strength_score: float = 0.0  # 论证强度 0-1
    logical_consistency: float = 0.0  # 逻辑一致性 0-1
    evidence_quality: float = 0.0  # 证据质量 0-1
    fallacies: List[LogicalFallacy] = field(default_factory=list)
    participant_id: str = ""
    contribution_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ArgumentRelation:
    """论证关系"""

    relation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_argument_id: str = ""
    target_argument_id: str = ""
    relation_type: str = ""  # "supports", "opposes", "clarifies", "extends"
    strength: float = 0.0  # 关系强度 0-1
    confidence: float = 0.0  # 关系置信度 0-1
    explanation: str = ""
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class ConsensusPoint:
    """共识点"""

    consensus_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    statement: str = ""
    supporting_arguments: List[str] = field(default_factory=list)  # argument_ids
    supporting_participants: List[str] = field(default_factory=list)
    consensus_strength: float = 0.0  # 共识强度 0-1
    evidence_support: float = 0.0  # 证据支持度 0-1
    detected_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ArgumentAnalysisResult:
    """论证分析结果"""

    analysis_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    contribution_id: str = ""
    session_id: str = ""
    arguments: List[ArgumentStructure] = field(default_factory=list)
    relations: List[ArgumentRelation] = field(default_factory=list)
    consensus_points: List[ConsensusPoint] = field(default_factory=list)
    overall_quality: float = 0.0  # 整体质量 0-1
    logical_coherence: float = 0.0  # 逻辑连贯性 0-1
    evidence_coverage: float = 0.0  # 证据覆盖度 0-1
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    processing_time: float = 0.0  # 处理时间（秒）
    metadata: Dict[str, Any] = field(default_factory=dict)


class ArgumentAnalyzer(ABC):
    """论证分析器抽象基类"""

    @abstractmethod
    async def analyze_contribution(self, contribution: DebateContribution) -> ArgumentAnalysisResult:
        """分析单个贡献"""
        pass

    @abstractmethod
    async def analyze_session(self, session: DebateSession) -> Dict[str, ArgumentAnalysisResult]:
        """分析整个会话"""
        pass

    @abstractmethod
    async def detect_relations(self, arguments: List[ArgumentStructure]) -> List[ArgumentRelation]:
        """检测论证关系"""
        pass

    @abstractmethod
    async def find_consensus(self, session: DebateSession) -> List[ConsensusPoint]:
        """寻找共识点"""
        pass


class RuleBasedArgumentAnalyzer(ArgumentAnalyzer):
    """基于规则的论证分析器"""

    def __init__(self):
        # 关键词模式
        self.claim_patterns = [
            r'我认为', r'我的观点是', r'我主张', r'我相信',
            r'显然', r'毫无疑问', r'事实上', r'总之'
        ]

        self.evidence_patterns = [
            r'根据.*研究', r'数据显示', r'统计表明', r'调查发现',
            r'专家指出', r'学者认为', r'报告显示', r'实验证明'
        ]

        self.reasoning_patterns = [
            r'因为', r'由于', r'既然', r'鉴于',
            r'所以', r'因此', r'由此可见', r'这说明'
        ]

        self.rebuttal_patterns = [
            r'但是', r'然而', r'不过', r'相反',
            r'我不同意', r'我反对', r'这是错误的', r'问题在于'
        ]

        # 逻辑谬误检测模式
        self.fallacy_patterns = {
            LogicalFallacy.AD_HOMINEM: [r'你.*愚蠢', r'你.*无知', r'你.*不懂'],
            LogicalFallacy.STRAW_MAN: [r'你的意思是', r'按你的逻辑'],
            LogicalFallacy.FALSE_DILEMMA: [r'要么.*要么', r'只有.*才能'],
            LogicalFallacy.CIRCULAR_REASONING: [r'因为.*所以.*因为'],
            LogicalFallacy.APPEAL_TO_AUTHORITY: [r'权威.*说', r'专家都.*认为'],
            LogicalFallacy.SLIPPERY_SLOPE: [r'如果.*那么.*最终'],
            LogicalFallacy.HASTY_GENERALIZATION: [r'所有.*都', r'总是.*从不'],
            LogicalFallacy.RED_HERRING: [r'话说回来', r'顺便说一下'],
            LogicalFallacy.BANDWAGON: [r'大家都', r'人人都', r'众所周知']
        }

        # 证据质量评估权重
        self.evidence_weights = {
            EvidenceType.RESEARCH_PAPER: 0.9,
            EvidenceType.STATISTICAL: 0.8,
            EvidenceType.EXPERT_OPINION: 0.7,
            EvidenceType.CASE_STUDY: 0.6,
            EvidenceType.EMPIRICAL: 0.6,
            EvidenceType.HISTORICAL: 0.5,
            EvidenceType.LOGICAL: 0.4,
            EvidenceType.ANECDOTAL: 0.3
        }

    async def analyze_contribution(self, contribution: DebateContribution) -> ArgumentAnalysisResult:
        """分析单个贡献"""
        start_time = datetime.now()

        # 提取论证结构
        argument_structure = await self._extract_argument_structure(contribution)

        # 检测逻辑谬误
        fallacies = await self._detect_fallacies(contribution.content)
        argument_structure.fallacies = fallacies

        # 计算质量分数
        argument_structure.strength_score = await self._calculate_argument_strength(argument_structure)
        argument_structure.logical_consistency = await self._assess_logical_consistency(argument_structure)
        argument_structure.evidence_quality = await self._assess_evidence_quality(argument_structure)

        # 创建分析结果
        processing_time = (datetime.now() - start_time).total_seconds()

        result = ArgumentAnalysisResult(
            contribution_id=contribution.contribution_id,
            session_id=contribution.session_id,
            arguments=[argument_structure],
            overall_quality=(argument_structure.strength_score +
                           argument_structure.logical_consistency +
                           argument_structure.evidence_quality) / 3,
            logical_coherence=argument_structure.logical_consistency,
            evidence_coverage=argument_structure.evidence_quality,
            processing_time=processing_time
        )

        return result

    async def analyze_session(self, session: DebateSession) -> Dict[str, ArgumentAnalysisResult]:
        """分析整个会话"""
        results = {}

        # 分析每个贡献
        for round_obj in session.rounds:
            for contribution in round_obj.contributions:
                result = await self.analyze_contribution(contribution)
                results[contribution.contribution_id] = result

        # 检测论证关系
        all_arguments = []
        for result in results.values():
            all_arguments.extend(result.arguments)

        relations = await self.detect_relations(all_arguments)

        # 更新结果中的关系
        for result in results.values():
            result.relations = [r for r in relations
                              if any(arg.argument_id in [r.source_argument_id, r.target_argument_id]
                                   for arg in result.arguments)]

        # 寻找共识点
        consensus_points = await self.find_consensus(session)

        # 更新结果中的共识点
        for result in results.values():
            result.consensus_points = consensus_points

        return results

    async def detect_relations(self, arguments: List[ArgumentStructure]) -> List[ArgumentRelation]:
        """检测论证关系"""
        relations = []

        for i, arg1 in enumerate(arguments):
            for j, arg2 in enumerate(arguments[i+1:], i+1):
                relation = await self._detect_argument_relation(arg1, arg2)
                if relation:
                    relations.append(relation)

        return relations

    async def find_consensus(self, session: DebateSession) -> List[ConsensusPoint]:
        """寻找共识点"""
        consensus_points = []

        # 收集所有主张
        claims = []
        for round_obj in session.rounds:
            for contribution in round_obj.contributions:
                # 简单的主张提取
                sentences = contribution.content.split('。')
                for sentence in sentences:
                    if any(pattern in sentence for pattern in self.claim_patterns):
                        claims.append({
                            'content': sentence.strip(),
                            'participant_id': contribution.participant_id,
                            'contribution_id': contribution.contribution_id
                        })

        # 寻找相似的主张
        consensus_candidates = await self._find_similar_claims(claims)

        # 评估共识强度
        for candidate in consensus_candidates:
            if len(candidate['supporters']) >= 2:  # 至少两个支持者
                consensus_point = ConsensusPoint(
                    statement=candidate['statement'],
                    supporting_participants=candidate['supporters'],
                    consensus_strength=len(candidate['supporters']) / len(session.participants),
                    evidence_support=candidate.get('evidence_score', 0.5)
                )
                consensus_points.append(consensus_point)

        return consensus_points

    async def _extract_argument_structure(self, contribution: DebateContribution) -> ArgumentStructure:
        """提取论证结构"""
        structure = ArgumentStructure(
            participant_id=contribution.participant_id,
            contribution_id=contribution.contribution_id
        )

        content = contribution.content
        sentences = content.split('。')

        # 提取主要主张
        main_claims = []
        for sentence in sentences:
            if any(re.search(pattern, sentence) for pattern in self.claim_patterns):
                main_claims.append(sentence.strip())

        if main_claims:
            structure.main_claim = main_claims[0]

        # 提取前提
        for sentence in sentences:
            if any(re.search(pattern, sentence) for pattern in self.reasoning_patterns):
                premise = ArgumentComponent(
                    content=sentence.strip(),
                    argument_type=ArgumentType.REASONING,
                    confidence=0.7
                )
                structure.premises.append(premise)

        # 提取证据
        for sentence in sentences:
            if any(re.search(pattern, sentence) for pattern in self.evidence_patterns):
                evidence_type = self._classify_evidence_type(sentence)
                evidence = ArgumentComponent(
                    content=sentence.strip(),
                    argument_type=ArgumentType.EVIDENCE,
                    evidence_type=evidence_type,
                    confidence=0.8
                )
                structure.evidence.append(evidence)

        # 提取反驳
        for sentence in sentences:
            if any(re.search(pattern, sentence) for pattern in self.rebuttal_patterns):
                rebuttal = ArgumentComponent(
                    content=sentence.strip(),
                    argument_type=ArgumentType.REBUTTAL,
                    confidence=0.6
                )
                structure.rebuttals.append(rebuttal)

        return structure

    async def _detect_fallacies(self, content: str) -> List[LogicalFallacy]:
        """检测逻辑谬误"""
        fallacies = []

        for fallacy, patterns in self.fallacy_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content):
                    fallacies.append(fallacy)
                    break

        return fallacies

    async def _calculate_argument_strength(self, structure: ArgumentStructure) -> float:
        """计算论证强度"""
        # 基础分数
        base_score = 0.5

        # 主张清晰度
        if structure.main_claim:
            base_score += 0.2

        # 前提支持
        premise_score = min(len(structure.premises) * 0.1, 0.3)

        # 证据支持
        evidence_score = 0.0
        for evidence in structure.evidence:
            if evidence.evidence_type:
                evidence_score += self.evidence_weights.get(evidence.evidence_type, 0.3)
        evidence_score = min(evidence_score, 0.4)

        # 逻辑谬误惩罚
        fallacy_penalty = len(structure.fallacies) * 0.1

        final_score = base_score + premise_score + evidence_score - fallacy_penalty
        return max(0.0, min(1.0, final_score))

    async def _assess_logical_consistency(self, structure: ArgumentStructure) -> float:
        """评估逻辑一致性"""
        # 简化的逻辑一致性评估
        consistency_score = 0.8

        # 逻辑谬误惩罚
        fallacy_penalty = len(structure.fallacies) * 0.2

        # 前提与结论的一致性（简化检查）
        if structure.main_claim and structure.premises:
            # 这里可以实现更复杂的逻辑一致性检查
            consistency_score += 0.1

        final_score = consistency_score - fallacy_penalty
        return max(0.0, min(1.0, final_score))

    async def _assess_evidence_quality(self, structure: ArgumentStructure) -> float:
        """评估证据质量"""
        if not structure.evidence:
            return 0.3  # 无证据的基础分数

        total_quality = 0.0
        for evidence in structure.evidence:
            if evidence.evidence_type:
                quality = self.evidence_weights.get(evidence.evidence_type, 0.3)
                total_quality += quality

        # 平均质量
        average_quality = total_quality / len(structure.evidence)

        # 证据多样性奖励
        unique_types = len(set(e.evidence_type for e in structure.evidence if e.evidence_type))
        diversity_bonus = min(unique_types * 0.05, 0.2)

        final_score = average_quality + diversity_bonus
        return max(0.0, min(1.0, final_score))

    def _classify_evidence_type(self, sentence: str) -> EvidenceType:
        """分类证据类型"""
        sentence_lower = sentence.lower()

        if any(keyword in sentence_lower for keyword in ['统计', '数据', '百分比', '%']):
            return EvidenceType.STATISTICAL
        elif any(keyword in sentence_lower for keyword in ['专家', '学者', '权威']):
            return EvidenceType.EXPERT_OPINION
        elif any(keyword in sentence_lower for keyword in ['研究', '论文', '期刊']):
            return EvidenceType.RESEARCH_PAPER
        elif any(keyword in sentence_lower for keyword in ['案例', '例子', '实例']):
            return EvidenceType.CASE_STUDY
        elif any(keyword in sentence_lower for keyword in ['历史', '过去', '以前']):
            return EvidenceType.HISTORICAL
        elif any(keyword in sentence_lower for keyword in ['经验', '实践', '实际']):
            return EvidenceType.EMPIRICAL
        elif any(keyword in sentence_lower for keyword in ['逻辑', '推理', '必然']):
            return EvidenceType.LOGICAL
        else:
            return EvidenceType.ANECDOTAL

    async def _detect_argument_relation(self, arg1: ArgumentStructure, arg2: ArgumentStructure) -> Optional[ArgumentRelation]:
        """检测两个论证之间的关系"""
        # 简化的关系检测
        content1 = arg1.main_claim.lower()
        content2 = arg2.main_claim.lower()

        if not content1 or not content2:
            return None

        # 支持关系检测
        support_keywords = ['支持', '赞同', '同意', '正确', '对的']
        if any(keyword in content2 for keyword in support_keywords):
            return ArgumentRelation(
                source_argument_id=arg2.argument_id,
                target_argument_id=arg1.argument_id,
                relation_type="supports",
                strength=0.7,
                confidence=0.6,
                explanation="检测到支持性语言"
            )

        # 反对关系检测
        oppose_keywords = ['反对', '不同意', '错误', '不对', '问题']
        if any(keyword in content2 for keyword in oppose_keywords):
            return ArgumentRelation(
                source_argument_id=arg2.argument_id,
                target_argument_id=arg1.argument_id,
                relation_type="opposes",
                strength=0.7,
                confidence=0.6,
                explanation="检测到反对性语言"
            )

        # 语义相似性检测（简化）
        common_words = set(content1.split()) & set(content2.split())
        if len(common_words) > 2:
            return ArgumentRelation(
                source_argument_id=arg1.argument_id,
                target_argument_id=arg2.argument_id,
                relation_type="clarifies",
                strength=len(common_words) / max(len(content1.split()), len(content2.split())),
                confidence=0.5,
                explanation=f"共同关键词: {', '.join(common_words)}"
            )

        return None

    async def _find_similar_claims(self, claims: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """寻找相似的主张"""
        consensus_candidates = []
        processed_claims = set()

        for i, claim1 in enumerate(claims):
            if i in processed_claims:
                continue

            similar_claims = [claim1]
            supporters = [claim1['participant_id']]

            for j, claim2 in enumerate(claims[i+1:], i+1):
                if j in processed_claims:
                    continue

                # 简化的相似性检测
                similarity = self._calculate_text_similarity(claim1['content'], claim2['content'])
                if similarity > 0.6:  # 相似度阈值
                    similar_claims.append(claim2)
                    supporters.append(claim2['participant_id'])
                    processed_claims.add(j)

            if len(similar_claims) > 1:
                # 选择最具代表性的表述
                representative_claim = max(similar_claims, key=lambda x: len(x['content']))

                consensus_candidates.append({
                    'statement': representative_claim['content'],
                    'supporters': list(set(supporters)),  # 去重
                    'evidence_score': 0.5  # 简化的证据评分
                })

            processed_claims.add(i)

        return consensus_candidates

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        # 简化的文本相似度计算
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union) if union else 0.0


class ArgumentEvaluator:
    """论证评估器"""

    def __init__(self, analyzer: ArgumentAnalyzer):
        self.analyzer = analyzer
        self.evaluation_history: List[ArgumentAnalysisResult] = []

    async def evaluate_debate_quality(self, session: DebateSession) -> Dict[str, Any]:
        """评估辩论质量"""
        analysis_results = await self.analyzer.analyze_session(session)

        # 计算整体指标
        all_arguments = []
        for result in analysis_results.values():
            all_arguments.extend(result.arguments)

        if not all_arguments:
            return {
                'overall_quality': 0.0,
                'argument_count': 0,
                'average_strength': 0.0,
                'logical_consistency': 0.0,
                'evidence_quality': 0.0,
                'consensus_points': 0,
                'fallacy_count': 0
            }

        # 统计指标
        total_strength = sum(arg.strength_score for arg in all_arguments)
        total_consistency = sum(arg.logical_consistency for arg in all_arguments)
        total_evidence_quality = sum(arg.evidence_quality for arg in all_arguments)
        total_fallacies = sum(len(arg.fallacies) for arg in all_arguments)

        consensus_points = []
        for result in analysis_results.values():
            consensus_points.extend(result.consensus_points)

        unique_consensus = {}
        for cp in consensus_points:
            if cp.statement not in unique_consensus:
                unique_consensus[cp.statement] = cp

        evaluation = {
            'overall_quality': (total_strength + total_consistency + total_evidence_quality) / (3 * len(all_arguments)),
            'argument_count': len(all_arguments),
            'average_strength': total_strength / len(all_arguments),
            'logical_consistency': total_consistency / len(all_arguments),
            'evidence_quality': total_evidence_quality / len(all_arguments),
            'consensus_points': len(unique_consensus),
            'fallacy_count': total_fallacies,
            'participant_contributions': self._analyze_participant_contributions(analysis_results),
            'debate_progression': self._analyze_debate_progression(session, analysis_results),
            'key_insights': self._extract_key_insights(analysis_results)
        }

        return evaluation

    def _analyze_participant_contributions(self, analysis_results: Dict[str, ArgumentAnalysisResult]) -> Dict[str, Any]:
        """分析参与者贡献"""
        participant_stats = defaultdict(lambda: {
            'contribution_count': 0,
            'average_quality': 0.0,
            'total_strength': 0.0,
            'fallacy_count': 0,
            'evidence_count': 0
        })

        for result in analysis_results.values():
            for argument in result.arguments:
                participant_id = argument.participant_id
                stats = participant_stats[participant_id]

                stats['contribution_count'] += 1
                stats['total_strength'] += argument.strength_score
                stats['fallacy_count'] += len(argument.fallacies)
                stats['evidence_count'] += len(argument.evidence)

        # 计算平均值
        for participant_id, stats in participant_stats.items():
            if stats['contribution_count'] > 0:
                stats['average_quality'] = stats['total_strength'] / stats['contribution_count']

        return dict(participant_stats)

    def _analyze_debate_progression(self, session: DebateSession, analysis_results: Dict[str, ArgumentAnalysisResult]) -> Dict[str, Any]:
        """分析辩论进展"""
        round_qualities = []

        for round_obj in session.rounds:
            round_arguments = []
            for contribution in round_obj.contributions:
                if contribution.contribution_id in analysis_results:
                    result = analysis_results[contribution.contribution_id]
                    round_arguments.extend(result.arguments)

            if round_arguments:
                round_quality = sum(arg.strength_score for arg in round_arguments) / len(round_arguments)
                round_qualities.append(round_quality)
            else:
                round_qualities.append(0.0)

        progression = {
            'round_qualities': round_qualities,
            'quality_trend': 'improving' if len(round_qualities) > 1 and round_qualities[-1] > round_qualities[0] else 'stable',
            'peak_round': round_qualities.index(max(round_qualities)) + 1 if round_qualities else 0,
            'consistency': 1.0 - (max(round_qualities) - min(round_qualities)) if round_qualities else 0.0
        }

        return progression

    def _extract_key_insights(self, analysis_results: Dict[str, ArgumentAnalysisResult]) -> List[str]:
        """提取关键洞察"""
        insights = []

        # 分析所有论证
        all_arguments = []
        for result in analysis_results.values():
            all_arguments.extend(result.arguments)

        if not all_arguments:
            return insights

        # 最强论证
        strongest_arg = max(all_arguments, key=lambda x: x.strength_score)
        insights.append(f"最强论证来自参与者 {strongest_arg.participant_id}: {strongest_arg.main_claim[:100]}...")

        # 证据质量分析
        evidence_counts = defaultdict(int)
        for arg in all_arguments:
            for evidence in arg.evidence:
                if evidence.evidence_type:
                    evidence_counts[evidence.evidence_type] += 1

        if evidence_counts:
            most_common_evidence = max(evidence_counts.items(), key=lambda x: x[1])
            insights.append(f"最常用的证据类型: {most_common_evidence[0].value} ({most_common_evidence[1]}次)")

        # 逻辑谬误分析
        fallacy_counts = defaultdict(int)
        for arg in all_arguments:
            for fallacy in arg.fallacies:
                fallacy_counts[fallacy] += 1

        if fallacy_counts:
            most_common_fallacy = max(fallacy_counts.items(), key=lambda x: x[1])
            insights.append(f"最常见的逻辑谬误: {most_common_fallacy[0].value} ({most_common_fallacy[1]}次)")

        return insights


# 工厂函数
def create_argument_analyzer(analyzer_type: str = "rule_based") -> ArgumentAnalyzer:
    """创建论证分析器实例"""
    if analyzer_type == "rule_based":
        return RuleBasedArgumentAnalyzer()
    else:
        # 可以扩展支持其他类型的分析器
        return RuleBasedArgumentAnalyzer()


def create_argument_evaluator(analyzer: Optional[ArgumentAnalyzer] = None) -> ArgumentEvaluator:
    """创建论证评估器实例"""
    if analyzer is None:
        analyzer = create_argument_analyzer()
    return ArgumentEvaluator(analyzer)


# 使用示例
async def example_usage():
    """使用示例"""
    # 创建分析器
    analyzer = create_argument_analyzer("rule_based")
    evaluator = create_argument_evaluator(analyzer)

    # 模拟辩论贡献
    from debate_flow_definition import DebateContribution

    contribution = DebateContribution(
        participant_id="participant_1",
        content="我认为人工智能将极大地改善教育质量。根据最新研究显示，AI辅助学习可以提高学生成绩30%。因为AI可以个性化教学内容，所以每个学生都能得到最适合的学习体验。",
        contribution_type="statement"
    )

    # 分析贡献
    result = await analyzer.analyze_contribution(contribution)

    print(f"论证强度: {result.arguments[0].strength_score:.2f}")
    print(f"逻辑一致性: {result.arguments[0].logical_consistency:.2f}")
    print(f"证据质量: {result.arguments[0].evidence_quality:.2f}")
    print(f"检测到的谬误: {[f.value for f in result.arguments[0].fallacies]}")


if __name__ == "__main__":
    asyncio.run(example_usage())

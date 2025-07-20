"""增强的记忆系统
支持多角色协同记忆、跨模型验证、社会计算和不确定性抑制
"""

import asyncio
import hashlib
import json
import logging
import sqlite3
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from src.blockchain_consensus import BlockchainConsensusEngine, ConsensusAlgorithm
from src.multi_model_adapter import MultiModelManager
from src.role_memory_bank import RoleIdentity, RoleMemoryBank


class MemoryType(Enum):
    """记忆类型"""

    IDENTITY = "identity"  # 身份记忆
    PROJECT = "project"  # 项目记忆
    DIALOGUE = "dialogue"  # 对话记忆
    EXPERIENCE = "experience"  # 经验记忆
    KNOWLEDGE = "knowledge"  # 知识记忆
    CONSENSUS = "consensus"  # 共识记忆
    VALIDATION = "validation"  # 验证记忆
    SOCIAL = "social"  # 社会计算记忆


@dataclass
class CollaborativeMemory:
    """协同记忆"""

    id: str
    project_id: str
    session_id: str
    participants: list[str]
    memory_type: MemoryType
    content: str
    confidence: float
    validation_status: str  # pending, validated, rejected
    model_agreement: dict[str, float]  # 模型间一致性
    social_consensus: Optional[float]  # 社会共识度
    timestamp: str
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class MultiModelValidation:
    """多模型验证结果"""

    validation_id: str
    content: str
    models_used: list[str]
    agreement_scores: dict[str, float]
    confidence_distribution: dict[str, float]
    uncertainty_metrics: dict[str, float]
    hallucination_detection: dict[str, bool]
    consensus_result: str
    timestamp: str


class EnhancedMemorySystem:
    """增强的记忆系统"""

    def __init__(self, data_dir: str = "data/enhanced_memory"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 核心组件
        self.role_memory_bank = RoleMemoryBank(str(self.data_dir / "role_memory"))
        self.consensus_engine = BlockchainConsensusEngine(
            ConsensusAlgorithm.PROOF_OF_AUTHORITY,
        )
        self.model_manager = MultiModelManager(self.role_memory_bank)

        # 协同记忆存储
        self.collaborative_memories: dict[str, CollaborativeMemory] = {}
        self.validation_results: dict[str, MultiModelValidation] = {}

        # 社会计算参数
        self.social_weights = {
            "expertise": 0.3,
            "reputation": 0.25,
            "consensus_history": 0.2,
            "diversity": 0.15,
            "objectivity": 0.1,
        }

        self.logger = logging.getLogger(__name__)

        # 初始化数据库
        self._init_database()

    def _init_database(self):
        """初始化数据库"""
        db_path = self.data_dir / "enhanced_memory.db"

        with sqlite3.connect(db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS collaborative_memories (
                    id TEXT PRIMARY KEY,
                    project_id TEXT,
                    session_id TEXT,
                    participants TEXT,
                    memory_type TEXT,
                    content TEXT,
                    confidence REAL,
                    validation_status TEXT,
                    model_agreement TEXT,
                    social_consensus REAL,
                    timestamp TEXT,
                    metadata TEXT
                )
            """,
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS validation_results (
                    validation_id TEXT PRIMARY KEY,
                    content TEXT,
                    models_used TEXT,
                    agreement_scores TEXT,
                    confidence_distribution TEXT,
                    uncertainty_metrics TEXT,
                    hallucination_detection TEXT,
                    consensus_result TEXT,
                    timestamp TEXT
                )
            """,
            )

    async def add_collaborative_memory(
        self,
        project_id: str,
        session_id: str,
        participants: list[str],
        content: str,
        memory_type: MemoryType,
        confidence: float = 0.5,
    ) -> str:
        """添加协同记忆"""
        memory_id = hashlib.md5(
            f"{project_id}_{session_id}_{time.time()}".encode(),
        ).hexdigest()[:16]

        # 多模型验证
        validation_result = await self._validate_with_multiple_models(
            content,
            participants,
        )

        # 社会共识计算
        social_consensus = await self._calculate_social_consensus(
            content,
            participants,
            project_id,
        )

        # 创建协同记忆
        memory = CollaborativeMemory(
            id=memory_id,
            project_id=project_id,
            session_id=session_id,
            participants=participants,
            memory_type=memory_type,
            content=content,
            confidence=confidence,
            validation_status="validated"
            if validation_result.agreement_scores.get("overall", 0) > 0.7
            else "pending",
            model_agreement=validation_result.agreement_scores,
            social_consensus=social_consensus,
            timestamp=datetime.now().isoformat(),
        )

        # 存储记忆
        self.collaborative_memories[memory_id] = memory
        self.validation_results[memory_id] = validation_result

        # 保存到数据库
        await self._save_collaborative_memory(memory)
        await self._save_validation_result(validation_result)

        # 更新角色记忆
        for participant_id in participants:
            self.role_memory_bank.add_memory(
                role_id=participant_id,
                content=f"协同记忆: {content}",
                memory_type=memory_type.value,
                importance=confidence,
                project_id=project_id,
                session_id=session_id,
                tags=["协同", "多模型验证"],
            )

        self.logger.info(f"添加协同记忆: {memory_id}")
        return memory_id

    async def _validate_with_multiple_models(
        self,
        content: str,
        participants: list[str],
    ) -> MultiModelValidation:
        """多模型验证"""
        validation_id = hashlib.md5(f"validation_{time.time()}".encode()).hexdigest()[
            :16
        ]

        # 获取可用的模型
        available_models = self.model_manager.get_available_models()
        models_to_use = available_models[:3]  # 使用前3个模型

        # 并行验证
        validation_tasks = []
        for model_name in models_to_use:
            task = self._validate_with_single_model(model_name, content)
            validation_tasks.append(task)

        validation_results = await asyncio.gather(
            *validation_tasks,
            return_exceptions=True,
        )

        # 分析验证结果
        agreement_scores = {}
        confidence_distribution = {}
        uncertainty_metrics = {}
        hallucination_detection = {}

        valid_results = [r for r in validation_results if not isinstance(r, Exception)]

        if valid_results:
            # 计算一致性分数
            agreement_scores = self._calculate_agreement_scores(valid_results)
            confidence_distribution = self._calculate_confidence_distribution(
                valid_results,
            )
            uncertainty_metrics = self._calculate_uncertainty_metrics(valid_results)
            hallucination_detection = self._detect_hallucinations(valid_results)

        # 生成共识结果
        consensus_result = self._generate_consensus_result(
            valid_results,
            agreement_scores,
        )

        validation_result = MultiModelValidation(
            validation_id=validation_id,
            content=content,
            models_used=models_to_use,
            agreement_scores=agreement_scores,
            confidence_distribution=confidence_distribution,
            uncertainty_metrics=uncertainty_metrics,
            hallucination_detection=hallucination_detection,
            consensus_result=consensus_result,
            timestamp=datetime.now().isoformat(),
        )

        return validation_result

    async def _validate_with_single_model(
        self,
        model_name: str,
        content: str,
    ) -> dict[str, Any]:
        """使用单个模型验证"""
        try:
            # 构建验证提示
            validation_prompt = f"""
            请验证以下内容的准确性、一致性和可信度：

            内容：{content}

            请从以下维度进行评估：
            1. 事实准确性 (0-1)
            2. 逻辑一致性 (0-1)
            3. 可信度 (0-1)
            4. 是否存在幻觉 (true/false)
            5. 不确定性程度 (0-1)

            请以JSON格式返回结果。
            """

            # 调用模型
            response = await self.model_manager.generate_response(
                model_name=model_name,
                prompt=validation_prompt,
                max_tokens=500,
            )

            # 解析响应
            try:
                result = json.loads(response.content)
                return {
                    "model": model_name,
                    "accuracy": result.get("factual_accuracy", 0.5),
                    "consistency": result.get("logical_consistency", 0.5),
                    "credibility": result.get("credibility", 0.5),
                    "hallucination": result.get("hallucination", False),
                    "uncertainty": result.get("uncertainty", 0.5),
                }
            except json.JSONDecodeError:
                return {
                    "model": model_name,
                    "accuracy": 0.5,
                    "consistency": 0.5,
                    "credibility": 0.5,
                    "hallucination": True,
                    "uncertainty": 0.8,
                }

        except Exception as e:
            self.logger.error(f"模型验证失败 {model_name}: {e}")
            return {
                "model": model_name,
                "accuracy": 0.3,
                "consistency": 0.3,
                "credibility": 0.3,
                "hallucination": True,
                "uncertainty": 1.0,
            }

    def _calculate_agreement_scores(
        self,
        validation_results: list[dict[str, Any]],
    ) -> dict[str, float]:
        """计算一致性分数"""
        if not validation_results:
            return {"overall": 0.0}

        # 计算各维度的一致性
        dimensions = ["accuracy", "consistency", "credibility"]
        agreement_scores = {}

        for dimension in dimensions:
            values = [r.get(dimension, 0.5) for r in validation_results]
            mean_value = sum(values) / len(values)
            variance = sum((v - mean_value) ** 2 for v in values) / len(values)
            agreement = max(0, 1 - variance)  # 方差越小，一致性越高
            agreement_scores[dimension] = agreement

        # 计算整体一致性
        overall_agreement = sum(agreement_scores.values()) / len(agreement_scores)
        agreement_scores["overall"] = overall_agreement

        return agreement_scores

    def _calculate_confidence_distribution(
        self,
        validation_results: list[dict[str, Any]],
    ) -> dict[str, float]:
        """计算置信度分布"""
        if not validation_results:
            return {}

        # 计算各模型的置信度
        confidence_scores = {}
        for result in validation_results:
            model = result.get("model", "unknown")
            confidence = (
                result.get("accuracy", 0.5)
                + result.get("consistency", 0.5)
                + result.get("credibility", 0.5)
            ) / 3
            confidence_scores[model] = confidence

        return confidence_scores

    def _calculate_uncertainty_metrics(
        self,
        validation_results: list[dict[str, Any]],
    ) -> dict[str, float]:
        """计算不确定性指标"""
        if not validation_results:
            return {"overall": 1.0}

        # 计算各维度的不确定性
        uncertainty_scores = []
        for result in validation_results:
            uncertainty = result.get("uncertainty", 0.5)
            uncertainty_scores.append(uncertainty)

        return {
            "mean": sum(uncertainty_scores) / len(uncertainty_scores),
            "max": max(uncertainty_scores),
            "min": min(uncertainty_scores),
            "overall": sum(uncertainty_scores) / len(uncertainty_scores),
        }

    def _detect_hallucinations(
        self,
        validation_results: list[dict[str, Any]],
    ) -> dict[str, bool]:
        """检测幻觉"""
        hallucination_detection = {}

        for result in validation_results:
            model = result.get("model", "unknown")
            hallucination = result.get("hallucination", False)
            hallucination_detection[model] = hallucination

        # 整体幻觉检测
        hallucination_count = sum(1 for h in hallucination_detection.values() if h)
        overall_hallucination = hallucination_count > len(hallucination_detection) / 2
        hallucination_detection["overall"] = overall_hallucination

        return hallucination_detection

    def _generate_consensus_result(
        self,
        validation_results: list[dict[str, Any]],
        agreement_scores: dict[str, float],
    ) -> str:
        """生成共识结果"""
        if not validation_results:
            return "验证失败，无法生成共识"

        overall_agreement = agreement_scores.get("overall", 0)

        if overall_agreement > 0.8:
            return "高一致性共识"
        elif overall_agreement > 0.6:
            return "中等一致性共识"
        elif overall_agreement > 0.4:
            return "低一致性共识，需要进一步验证"
        else:
            return "缺乏共识，建议重新评估"

    async def _calculate_social_consensus(
        self,
        content: str,
        participants: list[str],
        project_id: str,
    ) -> float:
        """计算社会共识度"""
        if not participants:
            return 0.0

        # 获取参与者的社会属性
        social_scores = []

        for participant_id in participants:
            # 获取专家信息
            expert_info = self.role_memory_bank.get_role_identity(participant_id)
            if not expert_info:
                continue

            # 计算社会分数
            social_score = self._calculate_individual_social_score(
                expert_info,
                content,
                project_id,
            )
            social_scores.append(social_score)

        if not social_scores:
            return 0.0

        # 计算加权社会共识
        weighted_consensus = sum(social_scores) / len(social_scores)
        return min(weighted_consensus, 1.0)

    def _calculate_individual_social_score(
        self,
        expert_info: RoleIdentity,
        content: str,
        project_id: str,
    ) -> float:
        """计算个体社会分数"""
        # 基于多个社会因素计算分数
        factors = {}

        # 1. 专业相关性
        relevance_score = self._calculate_expertise_relevance(expert_info, content)
        factors["expertise"] = relevance_score * self.social_weights["expertise"]

        # 2. 声誉分数
        reputation_score = expert_info.reputation_score
        factors["reputation"] = reputation_score * self.social_weights["reputation"]

        # 3. 共识历史
        consensus_history = self._get_consensus_history(expert_info.id, project_id)
        factors["consensus_history"] = (
            consensus_history * self.social_weights["consensus_history"]
        )

        # 4. 多样性贡献
        diversity_score = self._calculate_diversity_contribution(
            expert_info,
            project_id,
        )
        factors["diversity"] = diversity_score * self.social_weights["diversity"]

        # 5. 客观性
        objectivity_score = expert_info.personality.get("objectivity", 0.7)
        factors["objectivity"] = objectivity_score * self.social_weights["objectivity"]

        # 计算总分
        total_score = sum(factors.values())
        return min(total_score, 1.0)

    def _calculate_expertise_relevance(
        self,
        expert_info: RoleIdentity,
        content: str,
    ) -> float:
        """计算专业相关性"""
        # 简单的关键词匹配
        expert_specialties = expert_info.specialties or []
        content_lower = content.lower()

        relevance_count = 0
        for specialty in expert_specialties:
            if specialty.lower() in content_lower:
                relevance_count += 1

        if not expert_specialties:
            return 0.5

        return min(relevance_count / len(expert_specialties), 1.0)

    def _get_consensus_history(self, expert_id: str, project_id: str) -> float:
        """获取共识历史分数"""
        # 获取该专家在项目中的共识参与历史
        memories = self.role_memory_bank.retrieve_memories(
            role_id=expert_id,
            memory_types=["consensus"],
            project_id=project_id,
            limit=10,
        )

        if not memories:
            return 0.5

        # 计算历史共识成功率
        successful_consensus = sum(
            1 for m in memories if "成功" in m.content or "达成" in m.content
        )
        return successful_consensus / len(memories)

    def _calculate_diversity_contribution(
        self,
        expert_info: RoleIdentity,
        project_id: str,
    ) -> float:
        """计算多样性贡献"""
        # 检查该专家是否提供了独特的观点
        project_memories = self.role_memory_bank.retrieve_memories(
            memory_types=["project", "dialogue"],
            project_id=project_id,
            limit=50,
        )

        if not project_memories:
            return 0.5

        # 分析观点多样性
        unique_keywords = set()
        for memory in project_memories:
            if memory.role_id == expert_info.id:
                # 提取关键词
                keywords = self._extract_keywords(memory.content)
                unique_keywords.update(keywords)

        # 计算多样性分数
        diversity_score = min(len(unique_keywords) / 10, 1.0)  # 最多10个关键词
        return diversity_score

    def _extract_keywords(self, content: str) -> list[str]:
        """提取关键词"""
        # 简单的关键词提取
        import re

        words = re.findall(r"\b\w+\b", content.lower())
        # 过滤停用词
        stop_words = {"的", "是", "在", "有", "和", "与", "或", "但", "而", "如果", "那么"}
        keywords = [word for word in words if word not in stop_words and len(word) > 1]
        return keywords[:10]  # 返回前10个关键词

    async def _save_collaborative_memory(self, memory: CollaborativeMemory):
        """保存协同记忆到数据库"""
        db_path = self.data_dir / "enhanced_memory.db"

        with sqlite3.connect(db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO collaborative_memories
                (id, project_id, session_id, participants, memory_type, content,
                 confidence, validation_status, model_agreement, social_consensus,
                 timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    memory.id,
                    memory.project_id,
                    memory.session_id,
                    json.dumps(memory.participants),
                    memory.memory_type.value,
                    memory.content,
                    memory.confidence,
                    memory.validation_status,
                    json.dumps(memory.model_agreement),
                    memory.social_consensus,
                    memory.timestamp,
                    json.dumps(memory.metadata or {}),
                ),
            )

    async def _save_validation_result(self, validation_result: MultiModelValidation):
        """保存验证结果到数据库"""
        db_path = self.data_dir / "enhanced_memory.db"

        with sqlite3.connect(db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO validation_results
                (validation_id, content, models_used, agreement_scores,
                 confidence_distribution, uncertainty_metrics, hallucination_detection,
                 consensus_result, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    validation_result.validation_id,
                    validation_result.content,
                    json.dumps(validation_result.models_used),
                    json.dumps(validation_result.agreement_scores),
                    json.dumps(validation_result.confidence_distribution),
                    json.dumps(validation_result.uncertainty_metrics),
                    json.dumps(validation_result.hallucination_detection),
                    validation_result.consensus_result,
                    validation_result.timestamp,
                ),
            )

    def get_project_memory_summary(self, project_id: str) -> dict[str, Any]:
        """获取项目记忆摘要"""
        # 获取项目相关的协同记忆
        project_memories = [
            memory
            for memory in self.collaborative_memories.values()
            if memory.project_id == project_id
        ]

        if not project_memories:
            return {"status": "no_memories", "message": "项目暂无协同记忆"}

        # 计算统计信息
        total_memories = len(project_memories)
        validated_memories = sum(
            1 for m in project_memories if m.validation_status == "validated"
        )
        avg_confidence = sum(m.confidence for m in project_memories) / total_memories
        avg_social_consensus = (
            sum(m.social_consensus or 0 for m in project_memories) / total_memories
        )

        # 按类型统计
        type_counts = defaultdict(int)
        for memory in project_memories:
            type_counts[memory.memory_type.value] += 1

        return {
            "project_id": project_id,
            "total_memories": total_memories,
            "validated_memories": validated_memories,
            "validation_rate": validated_memories / total_memories
            if total_memories > 0
            else 0,
            "average_confidence": avg_confidence,
            "average_social_consensus": avg_social_consensus,
            "memory_types": dict(type_counts),
            "recent_memories": [
                {
                    "id": m.id,
                    "type": m.memory_type.value,
                    "content": m.content[:100] + "..."
                    if len(m.content) > 100
                    else m.content,
                    "confidence": m.confidence,
                    "social_consensus": m.social_consensus,
                    "timestamp": m.timestamp,
                }
                for m in sorted(
                    project_memories,
                    key=lambda x: x.timestamp,
                    reverse=True,
                )[:5]
            ],
        }

    def get_validation_insights(self, project_id: str) -> dict[str, Any]:
        """获取验证洞察"""
        # 获取项目相关的验证结果
        project_validations = [
            validation
            for validation in self.validation_results.values()
            if validation.validation_id
            in [
                memory_id
                for memory_id, memory in self.collaborative_memories.items()
                if memory.project_id == project_id
            ]
        ]

        if not project_validations:
            return {"status": "no_validations", "message": "项目暂无验证数据"}

        # 分析验证结果
        total_validations = len(project_validations)

        # 计算平均一致性
        avg_agreement = (
            sum(v.agreement_scores.get("overall", 0) for v in project_validations)
            / total_validations
        )

        # 计算幻觉检测率
        hallucination_count = sum(
            1
            for v in project_validations
            if v.hallucination_detection.get("overall", False)
        )
        hallucination_rate = hallucination_count / total_validations

        # 计算平均不确定性
        avg_uncertainty = (
            sum(v.uncertainty_metrics.get("overall", 0.5) for v in project_validations)
            / total_validations
        )

        return {
            "project_id": project_id,
            "total_validations": total_validations,
            "average_agreement": avg_agreement,
            "hallucination_rate": hallucination_rate,
            "average_uncertainty": avg_uncertainty,
            "model_performance": self._analyze_model_performance(project_validations),
            "consensus_distribution": self._analyze_consensus_distribution(
                project_validations,
            ),
        }

    def _analyze_model_performance(
        self,
        validations: list[MultiModelValidation],
    ) -> dict[str, Any]:
        """分析模型性能"""
        model_stats = defaultdict(
            lambda: {"count": 0, "agreement_sum": 0, "confidence_sum": 0},
        )

        for validation in validations:
            for model in validation.models_used:
                model_stats[model]["count"] += 1
                model_stats[model]["agreement_sum"] += validation.agreement_scores.get(
                    "overall",
                    0,
                )
                model_stats[model][
                    "confidence_sum"
                ] += validation.confidence_distribution.get(model, 0)

        # 计算平均值
        performance = {}
        for model, stats in model_stats.items():
            if stats["count"] > 0:
                performance[model] = {
                    "usage_count": stats["count"],
                    "average_agreement": stats["agreement_sum"] / stats["count"],
                    "average_confidence": stats["confidence_sum"] / stats["count"],
                }

        return performance

    def _analyze_consensus_distribution(
        self,
        validations: list[MultiModelValidation],
    ) -> dict[str, int]:
        """分析共识分布"""
        consensus_counts = defaultdict(int)

        for validation in validations:
            consensus = validation.consensus_result
            consensus_counts[consensus] += 1

        return dict(consensus_counts)

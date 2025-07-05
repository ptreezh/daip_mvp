"""观点碰撞引擎
实现多模型交叉验证、观点碰撞检测和深度共识算法集成
"""

import asyncio
import hashlib
import logging
import sqlite3
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.blockchain_consensus import BlockchainConsensusEngine, ConsensusAlgorithm
from src.multi_model_adapter import MultiModelManager
from src.unified_memory_service import (
    UnifiedMemoryService,
)


class CollisionType(Enum):
    """碰撞类型"""

    FACTUAL = "factual"  # 事实性碰撞
    LOGICAL = "logical"  # 逻辑性碰撞
    OPINION = "opinion"  # 观点性碰撞
    METHODOLOGY = "methodology"  # 方法论碰撞
    ETHICAL = "ethical"  # 伦理性碰撞


class ResolutionStrategy(Enum):
    """解决策略"""

    CONSENSUS = "consensus"  # 共识解决
    MAJORITY = "majority"  # 多数决
    EXPERT_WEIGHT = "expert_weight"  # 专家权重
    EVIDENCE_BASED = "evidence_based"  # 证据导向
    HYBRID = "hybrid"  # 混合策略


@dataclass
class OpinionCollision:
    """观点碰撞"""

    collision_id: str
    content: str
    participants: list[str]
    collision_type: CollisionType
    conflicting_opinions: dict[str, str]  # 参与者ID -> 观点内容
    confidence_scores: dict[str, float]  # 参与者ID -> 置信度
    evidence_sources: dict[str, list[str]]  # 参与者ID -> 证据来源
    timestamp: str
    resolution_strategy: ResolutionStrategy
    resolution_result: Optional[str] = None
    consensus_score: Optional[float] = None
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class CrossModelAnalysis:
    """跨模型分析结果"""

    analysis_id: str
    content: str
    models_used: list[str]
    model_opinions: dict[str, str]  # 模型名 -> 观点
    agreement_matrix: list[list[float]]  # 一致性矩阵
    disagreement_points: list[str]  # 分歧点
    consensus_confidence: float
    uncertainty_metrics: dict[str, float]
    analysis_timestamp: str
    metadata: dict[str, Any] = None


@dataclass
class ConsensusResult:
    """共识结果"""

    consensus_id: str
    collision_id: str
    final_opinion: str
    agreement_score: float
    participant_weights: dict[str, float]
    evidence_strength: float
    blockchain_verified: bool
    consensus_timestamp: str
    resolution_details: dict[str, Any] = None


class OpinionCollisionEngine:
    """观点碰撞引擎"""

    def __init__(
        self,
        memory_service: UnifiedMemoryService,
        model_manager: MultiModelManager,
    ):
        self.memory_service = memory_service
        self.model_manager = model_manager
        self.consensus_engine = BlockchainConsensusEngine(
            ConsensusAlgorithm.PROOF_OF_AUTHORITY,
        )

        # 碰撞检测配置
        self.config = {
            "similarity_threshold": 0.7,
            "confidence_threshold": 0.6,
            "min_participants": 2,
            "max_analysis_models": 5,
            "consensus_timeout": 300,  # 5分钟
            "evidence_weight": 0.3,
            "expertise_weight": 0.4,
            "consensus_weight": 0.3,
        }

        # 向量化器
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words="english")

        # 缓存
        self.collision_cache: dict[str, OpinionCollision] = {}
        self.analysis_cache: dict[str, CrossModelAnalysis] = {}
        self.consensus_cache: dict[str, ConsensusResult] = {}

        self.logger = logging.getLogger(__name__)

        # 初始化数据库
        self._init_database()

    def _init_database(self):
        """初始化数据库"""
        data_dir = Path("data/opinion_collision")
        data_dir.mkdir(parents=True, exist_ok=True)

        db_path = data_dir / "opinion_collision.db"

        with sqlite3.connect(db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS opinion_collisions (
                    collision_id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    participants TEXT NOT NULL,
                    collision_type TEXT NOT NULL,
                    conflicting_opinions TEXT NOT NULL,
                    confidence_scores TEXT NOT NULL,
                    evidence_sources TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    resolution_strategy TEXT NOT NULL,
                    resolution_result TEXT,
                    consensus_score REAL,
                    metadata TEXT
                )
            """,
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cross_model_analyses (
                    analysis_id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    models_used TEXT NOT NULL,
                    model_opinions TEXT NOT NULL,
                    agreement_matrix TEXT NOT NULL,
                    disagreement_points TEXT NOT NULL,
                    consensus_confidence REAL NOT NULL,
                    uncertainty_metrics TEXT NOT NULL,
                    analysis_timestamp TEXT NOT NULL,
                    metadata TEXT
                )
            """,
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS consensus_results (
                    consensus_id TEXT PRIMARY KEY,
                    collision_id TEXT NOT NULL,
                    final_opinion TEXT NOT NULL,
                    agreement_score REAL NOT NULL,
                    participant_weights TEXT NOT NULL,
                    evidence_strength REAL NOT NULL,
                    blockchain_verified BOOLEAN NOT NULL,
                    consensus_timestamp TEXT NOT NULL,
                    resolution_details TEXT
                )
            """,
            )

    async def detect_collision(
        self,
        content: str,
        participants: list[str],
        opinions: dict[str, str],
        confidence_scores: dict[str, float],
        evidence_sources: Optional[dict[str, list[str]]] = None,
    ) -> Optional[OpinionCollision]:
        """检测观点碰撞"""
        if len(participants) < self.config["min_participants"]:
            return None

        # 计算观点相似度
        similarity_matrix = self._calculate_opinion_similarity(opinions)

        # 检测碰撞
        collision_points = self._identify_collision_points(
            similarity_matrix,
            confidence_scores,
        )

        if not collision_points:
            return None

        # 确定碰撞类型
        collision_type = self._classify_collision_type(
            content,
            opinions,
            collision_points,
        )

        # 创建碰撞记录
        collision_id = hashlib.md5(
            f"collision_{content}_{time.time()}".encode(),
        ).hexdigest()[:16]

        collision = OpinionCollision(
            collision_id=collision_id,
            content=content,
            participants=participants,
            collision_type=collision_type,
            conflicting_opinions=opinions,
            confidence_scores=confidence_scores,
            evidence_sources=evidence_sources or {},
            timestamp=datetime.now().isoformat(),
            resolution_strategy=self._select_resolution_strategy(
                collision_type,
                participants,
            ),
            metadata={"collision_points": collision_points},
        )

        # 缓存碰撞
        self.collision_cache[collision_id] = collision

        self.logger.info(f"检测到观点碰撞: {collision_id} (类型: {collision_type.value})")
        return collision

    def _calculate_opinion_similarity(
        self,
        opinions: dict[str, str],
    ) -> list[list[float]]:
        """计算观点相似度矩阵"""
        if not opinions:
            return []

        # 提取观点文本
        opinion_texts = list(opinions.values())

        # 向量化
        try:
            vectors = self.vectorizer.fit_transform(opinion_texts)
            similarity_matrix = cosine_similarity(vectors).tolist()
        except Exception as e:
            self.logger.warning(f"向量化失败，使用简单相似度: {e}")
            # 简单的文本相似度计算
            similarity_matrix = []
            for i, text1 in enumerate(opinion_texts):
                row = []
                for j, text2 in enumerate(opinion_texts):
                    if i == j:
                        row.append(1.0)
                    else:
                        similarity = self._simple_text_similarity(text1, text2)
                        row.append(similarity)
                similarity_matrix.append(row)

        return similarity_matrix

    def _simple_text_similarity(self, text1: str, text2: str) -> float:
        """简单文本相似度计算"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    def _identify_collision_points(
        self,
        similarity_matrix: list[list[float]],
        confidence_scores: dict[str, float],
    ) -> list[tuple[int, int]]:
        """识别碰撞点"""
        collision_points = []
        participants = list(confidence_scores.keys())

        for i in range(len(similarity_matrix)):
            for j in range(i + 1, len(similarity_matrix)):
                similarity = similarity_matrix[i][j]
                confidence_i = confidence_scores.get(participants[i], 0.5)
                confidence_j = confidence_scores.get(participants[j], 0.5)

                # 如果相似度低且置信度都较高，则存在碰撞
                if (
                    similarity < self.config["similarity_threshold"]
                    and confidence_i > self.config["confidence_threshold"]
                    and confidence_j > self.config["confidence_threshold"]
                ):
                    collision_points.append((i, j))

        return collision_points

    def _classify_collision_type(
        self,
        content: str,
        opinions: dict[str, str],
        collision_points: list[tuple[int, int]],
    ) -> CollisionType:
        """分类碰撞类型"""
        # 简单的关键词分类
        content_lower = content.lower()

        # 事实性关键词
        factual_keywords = ["事实", "数据", "统计", "研究", "实验", "证据"]
        if any(keyword in content_lower for keyword in factual_keywords):
            return CollisionType.FACTUAL

        # 逻辑性关键词
        logical_keywords = ["逻辑", "推理", "论证", "因果", "关系"]
        if any(keyword in content_lower for keyword in logical_keywords):
            return CollisionType.LOGICAL

        # 方法论关键词
        methodology_keywords = ["方法", "策略", "方案", "途径", "工具"]
        if any(keyword in content_lower for keyword in methodology_keywords):
            return CollisionType.METHODOLOGY

        # 伦理性关键词
        ethical_keywords = ["道德", "伦理", "价值观", "原则", "规范"]
        if any(keyword in content_lower for keyword in ethical_keywords):
            return CollisionType.ETHICAL

        # 默认为观点性碰撞
        return CollisionType.OPINION

    def _select_resolution_strategy(
        self,
        collision_type: CollisionType,
        participants: list[str],
    ) -> ResolutionStrategy:
        """选择解决策略"""
        if collision_type == CollisionType.FACTUAL:
            return ResolutionStrategy.EVIDENCE_BASED
        elif collision_type == CollisionType.LOGICAL:
            return ResolutionStrategy.EXPERT_WEIGHT
        elif collision_type == CollisionType.METHODOLOGY:
            return ResolutionStrategy.HYBRID
        elif collision_type == CollisionType.ETHICAL:
            return ResolutionStrategy.CONSENSUS
        else:
            return ResolutionStrategy.MAJORITY

    async def cross_model_analyze(
        self,
        content: str,
        models: list[str] = None,
    ) -> CrossModelAnalysis:
        """跨模型分析"""
        analysis_id = hashlib.md5(
            f"analysis_{content}_{time.time()}".encode(),
        ).hexdigest()[:16]

        # 获取可用模型
        if not models:
            available_models = self.model_manager.get_available_models()
            models = available_models[: self.config["max_analysis_models"]]

        # 并行获取各模型观点
        analysis_tasks = []
        for model_name in models:
            task = self._get_model_opinion(model_name, content)
            analysis_tasks.append(task)

        model_responses = await asyncio.gather(*analysis_tasks, return_exceptions=True)

        # 收集有效响应
        model_opinions = {}
        valid_responses = []

        for i, response in enumerate(model_responses):
            if not isinstance(response, Exception) and response:
                model_name = models[i]
                model_opinions[model_name] = response
                valid_responses.append(response)

        if not valid_responses:
            # 返回默认分析结果
            return CrossModelAnalysis(
                analysis_id=analysis_id,
                content=content,
                models_used=models,
                model_opinions=model_opinions,
                agreement_matrix=[],
                disagreement_points=["所有模型分析失败"],
                consensus_confidence=0.0,
                uncertainty_metrics={"overall": 1.0},
                analysis_timestamp=datetime.now().isoformat(),
            )

        # 计算一致性矩阵
        agreement_matrix = self._calculate_agreement_matrix(valid_responses)

        # 识别分歧点
        disagreement_points = self._identify_disagreement_points(valid_responses)

        # 计算共识置信度
        consensus_confidence = self._calculate_consensus_confidence(agreement_matrix)

        # 计算不确定性指标
        uncertainty_metrics = self._calculate_uncertainty_metrics(valid_responses)

        analysis_result = CrossModelAnalysis(
            analysis_id=analysis_id,
            content=content,
            models_used=models,
            model_opinions=model_opinions,
            agreement_matrix=agreement_matrix,
            disagreement_points=disagreement_points,
            consensus_confidence=consensus_confidence,
            uncertainty_metrics=uncertainty_metrics,
            analysis_timestamp=datetime.now().isoformat(),
        )

        # 缓存分析结果
        self.analysis_cache[analysis_id] = analysis_result

        return analysis_result

    async def _get_model_opinion(self, model_name: str, content: str) -> str:
        """获取模型观点"""
        try:
            analysis_prompt = f"""
            请对以下内容进行分析并给出你的观点：

            内容：{content}

            请从以下维度进行分析：
            1. 主要观点
            2. 支持论据
            3. 潜在问题
            4. 建议改进

            请以结构化的方式返回你的分析结果。
            """

            response = await self.model_manager.generate_response(
                model_name=model_name,
                prompt=analysis_prompt,
                max_tokens=1000,
            )

            return response.content if response else ""

        except Exception as e:
            self.logger.error(f"获取模型观点失败 {model_name}: {e}")
            return ""

    def _calculate_agreement_matrix(self, responses: list[str]) -> list[list[float]]:
        """计算一致性矩阵"""
        if not responses:
            return []

        # 使用TF-IDF向量化
        try:
            vectors = self.vectorizer.fit_transform(responses)
            similarity_matrix = cosine_similarity(vectors).tolist()
        except Exception as e:
            self.logger.warning(f"计算一致性矩阵失败: {e}")
            # 使用简单相似度
            similarity_matrix = []
            for i, resp1 in enumerate(responses):
                row = []
                for j, resp2 in enumerate(responses):
                    if i == j:
                        row.append(1.0)
                    else:
                        similarity = self._simple_text_similarity(resp1, resp2)
                        row.append(similarity)
                similarity_matrix.append(row)

        return similarity_matrix

    def _identify_disagreement_points(self, responses: list[str]) -> list[str]:
        """识别分歧点"""
        if len(responses) < 2:
            return []

        # 简单的关键词分歧检测
        disagreement_points = []

        # 提取关键概念
        all_words = set()
        for response in responses:
            words = set(response.lower().split())
            all_words.update(words)

        # 检查每个概念的一致性
        for word in all_words:
            if len(word) < 3:  # 跳过短词
                continue

            word_occurrences = sum(
                1 for response in responses if word in response.lower()
            )
            if 0 < word_occurrences < len(responses):
                disagreement_points.append(f"概念 '{word}' 存在分歧")

        return disagreement_points[:5]  # 返回前5个分歧点

    def _calculate_consensus_confidence(
        self,
        agreement_matrix: list[list[float]],
    ) -> float:
        """计算共识置信度"""
        if not agreement_matrix:
            return 0.0

        # 计算平均一致性
        total_similarity = 0.0
        count = 0

        for i in range(len(agreement_matrix)):
            for j in range(i + 1, len(agreement_matrix)):
                total_similarity += agreement_matrix[i][j]
                count += 1

        if count == 0:
            return 0.0

        return total_similarity / count

    def _calculate_uncertainty_metrics(self, responses: list[str]) -> dict[str, float]:
        """计算不确定性指标"""
        if not responses:
            return {"overall": 1.0}

        # 计算响应的多样性
        try:
            vectors = self.vectorizer.fit_transform(responses)
            similarity_matrix = cosine_similarity(vectors)

            # 计算平均相似度
            avg_similarity = np.mean(
                similarity_matrix[np.triu_indices_from(similarity_matrix, k=1)],
            )

            # 不确定性 = 1 - 平均相似度
            uncertainty = 1.0 - avg_similarity

            return {
                "overall": uncertainty,
                "diversity": uncertainty,
                "consistency": avg_similarity,
            }
        except Exception as e:
            self.logger.warning(f"计算不确定性指标失败: {e}")
            return {"overall": 0.5}

    async def resolve_collision(self, collision: OpinionCollision) -> ConsensusResult:
        """解决观点碰撞"""
        consensus_id = hashlib.md5(
            f"consensus_{collision.collision_id}_{time.time()}".encode(),
        ).hexdigest()[:16]

        # 根据解决策略选择方法
        if collision.resolution_strategy == ResolutionStrategy.CONSENSUS:
            final_opinion, agreement_score = await self._consensus_resolution(collision)
        elif collision.resolution_strategy == ResolutionStrategy.MAJORITY:
            final_opinion, agreement_score = self._majority_resolution(collision)
        elif collision.resolution_strategy == ResolutionStrategy.EXPERT_WEIGHT:
            final_opinion, agreement_score = self._expert_weight_resolution(collision)
        elif collision.resolution_strategy == ResolutionStrategy.EVIDENCE_BASED:
            final_opinion, agreement_score = await self._evidence_based_resolution(
                collision,
            )
        else:  # HYBRID
            final_opinion, agreement_score = await self._hybrid_resolution(collision)

        # 计算参与者权重
        participant_weights = self._calculate_participant_weights(collision)

        # 计算证据强度
        evidence_strength = self._calculate_evidence_strength(collision)

        # 区块链验证
        blockchain_verified = await self._verify_consensus_on_blockchain(
            collision.content,
            final_opinion,
            collision.participants,
        )

        consensus_result = ConsensusResult(
            consensus_id=consensus_id,
            collision_id=collision.collision_id,
            final_opinion=final_opinion,
            agreement_score=agreement_score,
            participant_weights=participant_weights,
            evidence_strength=evidence_strength,
            blockchain_verified=blockchain_verified,
            consensus_timestamp=datetime.now().isoformat(),
            resolution_details={
                "strategy": collision.resolution_strategy.value,
                "collision_type": collision.collision_type.value,
            },
        )

        # 更新碰撞记录
        collision.resolution_result = final_opinion
        collision.consensus_score = agreement_score

        # 缓存共识结果
        self.consensus_cache[consensus_id] = consensus_result

        self.logger.info(f"观点碰撞解决完成: {consensus_id} (一致性: {agreement_score:.2f})")
        return consensus_result

    async def _consensus_resolution(
        self,
        collision: OpinionCollision,
    ) -> tuple[str, float]:
        """共识解决"""
        # 使用区块链共识引擎
        try:
            consensus_data = {
                "content": collision.content,
                "opinions": collision.conflicting_opinions,
                "participants": collision.participants,
                "confidence_scores": collision.confidence_scores,
            }

            result = await self.consensus_engine.build_consensus(consensus_data)

            if result.get("success"):
                return result.get("consensus", "无法达成共识"), result.get(
                    "agreement_score",
                    0.0,
                )
            else:
                return "无法达成共识", 0.0

        except Exception as e:
            self.logger.error(f"共识解决失败: {e}")
            return "共识解决失败", 0.0

    def _majority_resolution(self, collision: OpinionCollision) -> tuple[str, float]:
        """多数决解决"""
        # 按置信度加权投票
        weighted_votes = {}

        for participant, opinion in collision.conflicting_opinions.items():
            confidence = collision.confidence_scores.get(participant, 0.5)
            if opinion not in weighted_votes:
                weighted_votes[opinion] = 0.0
            weighted_votes[opinion] += confidence

        if not weighted_votes:
            return "无法确定多数意见", 0.0

        # 选择权重最高的意见
        final_opinion = max(weighted_votes.items(), key=lambda x: x[1])[0]
        total_weight = sum(weighted_votes.values())
        agreement_score = (
            weighted_votes[final_opinion] / total_weight if total_weight > 0 else 0.0
        )

        return final_opinion, agreement_score

    def _expert_weight_resolution(
        self,
        collision: OpinionCollision,
    ) -> tuple[str, float]:
        """专家权重解决"""
        # 基于参与者的专业性和声誉计算权重
        expert_weights = {}
        total_weight = 0.0

        for participant in collision.participants:
            # 获取参与者信息
            role_identity = self.memory_service.role_memory_bank.get_role_identity(
                participant,
            )
            if role_identity:
                # 基于声誉和专业性计算权重
                weight = role_identity.reputation_score * 0.6 + 0.4  # 基础权重0.4
                expert_weights[participant] = weight
                total_weight += weight
            else:
                expert_weights[participant] = 0.5  # 默认权重
                total_weight += 0.5

        # 加权选择
        weighted_opinions = {}
        for participant, opinion in collision.conflicting_opinions.items():
            weight = expert_weights.get(participant, 0.5)
            if opinion not in weighted_opinions:
                weighted_opinions[opinion] = 0.0
            weighted_opinions[opinion] += weight

        if not weighted_opinions:
            return "无法确定专家意见", 0.0

        final_opinion = max(weighted_opinions.items(), key=lambda x: x[1])[0]
        agreement_score = (
            weighted_opinions[final_opinion] / total_weight if total_weight > 0 else 0.0
        )

        return final_opinion, agreement_score

    async def _evidence_based_resolution(
        self,
        collision: OpinionCollision,
    ) -> tuple[str, float]:
        """证据导向解决"""
        # 评估各观点的证据强度
        evidence_scores = {}

        for participant, opinion in collision.conflicting_opinions.items():
            evidence_sources = collision.evidence_sources.get(participant, [])

            # 计算证据强度
            evidence_score = 0.0
            for evidence in evidence_sources:
                # 简单的证据评估
                if "研究" in evidence or "数据" in evidence:
                    evidence_score += 0.3
                elif "实验" in evidence or "测试" in evidence:
                    evidence_score += 0.4
                elif "专家" in evidence or "权威" in evidence:
                    evidence_score += 0.2
                else:
                    evidence_score += 0.1

            evidence_scores[opinion] = evidence_score

        if not evidence_scores:
            return "缺乏有效证据", 0.0

        # 选择证据最强的观点
        final_opinion = max(evidence_scores.items(), key=lambda x: x[1])[0]
        max_evidence = max(evidence_scores.values())
        total_evidence = sum(evidence_scores.values())
        agreement_score = max_evidence / total_evidence if total_evidence > 0 else 0.0

        return final_opinion, agreement_score

    async def _hybrid_resolution(
        self,
        collision: OpinionCollision,
    ) -> tuple[str, float]:
        """混合解决策略"""
        # 结合多种解决策略
        results = []

        # 1. 多数决
        majority_opinion, majority_score = self._majority_resolution(collision)
        results.append(("majority", majority_opinion, majority_score))

        # 2. 专家权重
        expert_opinion, expert_score = self._expert_weight_resolution(collision)
        results.append(("expert", expert_opinion, expert_score))

        # 3. 证据导向
        evidence_opinion, evidence_score = await self._evidence_based_resolution(
            collision,
        )
        results.append(("evidence", evidence_opinion, evidence_score))

        # 加权组合
        weighted_opinions = {}
        total_weight = 0.0

        for method, opinion, score in results:
            weight = score * 0.4  # 方法权重
            if opinion not in weighted_opinions:
                weighted_opinions[opinion] = 0.0
            weighted_opinions[opinion] += weight
            total_weight += weight

        if not weighted_opinions:
            return "混合策略无法确定结果", 0.0

        final_opinion = max(weighted_opinions.items(), key=lambda x: x[1])[0]
        agreement_score = (
            weighted_opinions[final_opinion] / total_weight if total_weight > 0 else 0.0
        )

        return final_opinion, agreement_score

    def _calculate_participant_weights(
        self,
        collision: OpinionCollision,
    ) -> dict[str, float]:
        """计算参与者权重"""
        weights = {}
        total_weight = 0.0

        for participant in collision.participants:
            # 基于置信度和声誉计算权重
            confidence = collision.confidence_scores.get(participant, 0.5)

            role_identity = self.memory_service.role_memory_bank.get_role_identity(
                participant,
            )
            reputation = role_identity.reputation_score if role_identity else 0.5

            weight = confidence * 0.6 + reputation * 0.4
            weights[participant] = weight
            total_weight += weight

        # 归一化权重
        if total_weight > 0:
            for participant in weights:
                weights[participant] /= total_weight

        return weights

    def _calculate_evidence_strength(self, collision: OpinionCollision) -> float:
        """计算证据强度"""
        if not collision.evidence_sources:
            return 0.0

        total_evidence = 0.0
        evidence_count = 0

        for participant, evidence_list in collision.evidence_sources.items():
            for evidence in evidence_list:
                # 简单的证据强度评估
                if "研究" in evidence or "数据" in evidence:
                    total_evidence += 0.8
                elif "实验" in evidence or "测试" in evidence:
                    total_evidence += 0.9
                elif "专家" in evidence or "权威" in evidence:
                    total_evidence += 0.7
                elif "案例" in evidence or "实例" in evidence:
                    total_evidence += 0.6
                else:
                    total_evidence += 0.3
                evidence_count += 1

        return total_evidence / evidence_count if evidence_count > 0 else 0.0

    async def _verify_consensus_on_blockchain(
        self,
        content: str,
        consensus: str,
        participants: list[str],
    ) -> bool:
        """在区块链上验证共识"""
        try:
            verification_data = {
                "content": content,
                "consensus": consensus,
                "participants": participants,
                "timestamp": datetime.now().isoformat(),
            }

            result = await self.consensus_engine.verify_consensus(verification_data)
            return result.get("verified", False)

        except Exception as e:
            self.logger.error(f"区块链验证失败: {e}")
            return False

    def get_collision_statistics(self) -> dict[str, Any]:
        """获取碰撞统计信息"""
        stats = {
            "total_collisions": len(self.collision_cache),
            "resolved_collisions": 0,
            "collision_types": defaultdict(int),
            "resolution_strategies": defaultdict(int),
            "average_consensus_score": 0.0,
            "total_analyses": len(self.analysis_cache),
            "total_consensus": len(self.consensus_cache),
        }

        total_consensus_score = 0.0

        for collision in self.collision_cache.values():
            stats["collision_types"][collision.collision_type.value] += 1
            stats["resolution_strategies"][collision.resolution_strategy.value] += 1

            if collision.resolution_result:
                stats["resolved_collisions"] += 1
                if collision.consensus_score:
                    total_consensus_score += collision.consensus_score

        if stats["resolved_collisions"] > 0:
            stats["average_consensus_score"] = (
                total_consensus_score / stats["resolved_collisions"]
            )

        return stats

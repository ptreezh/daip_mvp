"""统一记忆服务接口
整合两套记忆系统，实现跨模型记忆适配和多模型交叉验证
"""

import asyncio
import hashlib
import json
import logging
import sqlite3
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from src.blockchain_consensus import BlockchainConsensusEngine, ConsensusAlgorithm
from src.enhanced_memory_system import (
    CollaborativeMemory,
    EnhancedMemorySystem,
)
from src.multi_model_adapter import MultiModelManager
from src.role_memory_bank import RoleMemoryBank


class MemorySystemType(Enum):
    """记忆系统类型"""

    ROLE_MEMORY_BANK = "role_memory_bank"
    ENHANCED_MEMORY_SYSTEM = "enhanced_memory_system"


class MemoryValidationLevel(Enum):
    """记忆验证级别"""

    NONE = "none"
    BASIC = "basic"
    CROSS_MODEL = "cross_model"
    CONSENSUS = "consensus"


@dataclass
class UnifiedMemoryEntry:
    """统一记忆条目"""

    id: str
    role_id: str
    content: str
    memory_type: str
    importance: float
    confidence: float
    validation_level: MemoryValidationLevel
    system_type: MemorySystemType
    timestamp: str
    project_id: Optional[str] = None
    session_id: Optional[str] = None
    tags: list[str] = None
    metadata: dict[str, Any] = None
    cross_model_validation: Optional[dict[str, Any]] = None
    consensus_data: Optional[dict[str, Any]] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class CrossModelValidationResult:
    """跨模型验证结果"""

    validation_id: str
    content: str
    models_used: list[str]
    agreement_scores: dict[str, float]
    confidence_distribution: dict[str, float]
    uncertainty_metrics: dict[str, float]
    hallucination_detection: dict[str, bool]
    consensus_result: str
    validation_timestamp: str
    metadata: dict[str, Any] = None


@dataclass
class ConsensusResult:
    """共识结果"""

    consensus_id: str
    content: str
    participants: list[str]
    agreement_score: float
    social_consensus: float
    blockchain_verified: bool
    consensus_timestamp: str
    metadata: dict[str, Any] = None


class IUnifiedMemoryService(ABC):
    """统一记忆服务接口"""

    @abstractmethod
    async def add_memory(
        self,
        role_id: str,
        content: str,
        memory_type: str,
        importance: float = 0.5,
        confidence: float = 0.5,
        validation_level: MemoryValidationLevel = MemoryValidationLevel.BASIC,
        project_id: Optional[str] = None,
        session_id: Optional[str] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> str:
        """添加记忆"""

    @abstractmethod
    async def get_memories(
        self,
        role_id: str,
        memory_type: Optional[str] = None,
        project_id: Optional[str] = None,
        session_id: Optional[str] = None,
        validation_level: Optional[MemoryValidationLevel] = None,
        limit: int = 10,
        min_importance: float = 0.0,
    ) -> list[UnifiedMemoryEntry]:
        """获取记忆"""

    @abstractmethod
    async def build_context_for_conversation(
        self,
        role_id: str,
        current_question: str,
        project_id: Optional[str] = None,
        session_id: Optional[str] = None,
        conversation_history: Optional[list[dict[str, str]]] = None,
        target_model: str = "ollama",
    ) -> dict[str, Any]:
        """构建对话上下文"""

    @abstractmethod
    async def cross_model_validate(
        self,
        content: str,
        models: list[str] = None,
    ) -> CrossModelValidationResult:
        """跨模型验证"""

    @abstractmethod
    async def build_consensus(
        self,
        content: str,
        participants: list[str],
        project_id: Optional[str] = None,
    ) -> ConsensusResult:
        """构建共识"""


class UnifiedMemoryService(IUnifiedMemoryService):
    """统一记忆服务实现"""

    def __init__(self, data_dir: str = "data/unified_memory"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 初始化两套记忆系统
        self.role_memory_bank = RoleMemoryBank(str(self.data_dir / "role_memory"))
        self.enhanced_memory_system = EnhancedMemorySystem(
            str(self.data_dir / "enhanced_memory"),
        )

        # 多模型管理器
        self.model_manager = MultiModelManager(self.role_memory_bank)

        # 共识引擎
        self.consensus_engine = BlockchainConsensusEngine(
            ConsensusAlgorithm.PROOF_OF_AUTHORITY,
        )

        # 统一记忆缓存
        self.unified_memory_cache: dict[str, UnifiedMemoryEntry] = {}

        # 验证结果缓存
        self.validation_cache: dict[str, CrossModelValidationResult] = {}

        # 共识结果缓存
        self.consensus_cache: dict[str, ConsensusResult] = {}

        # 配置参数
        self.config = {
            "default_validation_level": MemoryValidationLevel.BASIC,
            "cross_model_threshold": 0.7,
            "consensus_threshold": 0.8,
            "max_validation_models": 3,
            "memory_compression_ratio": 0.3,
        }

        self.logger = logging.getLogger(__name__)

        # 初始化数据库
        self._init_database()

        # 加载现有数据
        self._load_existing_data()

    def _init_database(self):
        """初始化数据库"""
        db_path = self.data_dir / "unified_memory.db"

        with sqlite3.connect(db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS unified_memories (
                    id TEXT PRIMARY KEY,
                    role_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    importance REAL NOT NULL,
                    confidence REAL NOT NULL,
                    validation_level TEXT NOT NULL,
                    system_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    project_id TEXT,
                    session_id TEXT,
                    tags TEXT,
                    metadata TEXT,
                    cross_model_validation TEXT,
                    consensus_data TEXT
                )
            """,
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cross_model_validations (
                    validation_id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    models_used TEXT NOT NULL,
                    agreement_scores TEXT NOT NULL,
                    confidence_distribution TEXT NOT NULL,
                    uncertainty_metrics TEXT NOT NULL,
                    hallucination_detection TEXT NOT NULL,
                    consensus_result TEXT NOT NULL,
                    validation_timestamp TEXT NOT NULL,
                    metadata TEXT
                )
            """,
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS consensus_results (
                    consensus_id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    participants TEXT NOT NULL,
                    agreement_score REAL NOT NULL,
                    social_consensus REAL NOT NULL,
                    blockchain_verified BOOLEAN NOT NULL,
                    consensus_timestamp TEXT NOT NULL,
                    metadata TEXT
                )
            """,
            )

            # 创建索引
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_unified_memories_role_id ON unified_memories(role_id)",
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_unified_memories_project_id ON unified_memories(project_id)",
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_unified_memories_validation_level ON unified_memories(validation_level)",
            )

    def _load_existing_data(self):
        """加载现有数据"""
        try:
            # 从两套系统加载数据并统一格式
            self._sync_role_memory_bank()
            self._sync_enhanced_memory_system()
            self.logger.info("现有数据加载完成")
        except Exception as e:
            self.logger.error(f"加载现有数据失败: {e}")

    def _sync_role_memory_bank(self):
        """同步角色记忆银行数据"""
        # 获取所有角色
        role_stats = self.role_memory_bank.get_memory_statistics()

        for role_id in role_stats.get("memory_types", {}):
            memories = self.role_memory_bank.retrieve_memories(
                role_id=role_id,
                limit=100,
            )

            for memory in memories:
                unified_memory = UnifiedMemoryEntry(
                    id=memory.id,
                    role_id=memory.role_id,
                    content=memory.content,
                    memory_type=memory.memory_type,
                    importance=memory.importance,
                    confidence=0.5,  # 默认置信度
                    validation_level=MemoryValidationLevel.NONE,
                    system_type=MemorySystemType.ROLE_MEMORY_BANK,
                    timestamp=memory.timestamp,
                    project_id=memory.project_id,
                    session_id=memory.session_id,
                    tags=memory.tags,
                    metadata=memory.metadata,
                )

                self.unified_memory_cache[memory.id] = unified_memory

    def _sync_enhanced_memory_system(self):
        """同步增强记忆系统数据"""
        # 同步协同记忆
        for (
            memory_id,
            memory,
        ) in self.enhanced_memory_system.collaborative_memories.items():
            unified_memory = UnifiedMemoryEntry(
                id=memory.id,
                role_id=memory.participants[0] if memory.participants else "system",
                content=memory.content,
                memory_type=memory.memory_type.value,
                importance=memory.confidence,
                confidence=memory.confidence,
                validation_level=MemoryValidationLevel.CROSS_MODEL
                if memory.validation_status == "validated"
                else MemoryValidationLevel.BASIC,
                system_type=MemorySystemType.ENHANCED_MEMORY_SYSTEM,
                timestamp=memory.timestamp,
                project_id=memory.project_id,
                session_id=memory.session_id,
                tags=["协同记忆"],
                metadata=memory.metadata,
                cross_model_validation=memory.model_agreement,
                consensus_data={"social_consensus": memory.social_consensus},
            )

            self.unified_memory_cache[memory.id] = unified_memory

    async def add_memory(
        self,
        role_id: str,
        content: str,
        memory_type: str,
        importance: float = 0.5,
        confidence: float = 0.5,
        validation_level: MemoryValidationLevel = MemoryValidationLevel.BASIC,
        project_id: Optional[str] = None,
        session_id: Optional[str] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> str:
        """添加记忆"""
        memory_id = hashlib.md5(
            f"{role_id}_{content}_{time.time()}".encode(),
        ).hexdigest()[:16]

        # 根据验证级别进行相应处理
        cross_model_validation = None
        consensus_data = None

        if validation_level == MemoryValidationLevel.CROSS_MODEL:
            # 执行跨模型验证
            validation_result = await self.cross_model_validate(content)
            cross_model_validation = asdict(validation_result)
            confidence = validation_result.agreement_scores.get("overall", confidence)

        elif validation_level == MemoryValidationLevel.CONSENSUS:
            # 执行共识构建
            consensus_result = await self.build_consensus(
                content,
                [role_id],
                project_id,
            )
            consensus_data = asdict(consensus_result)
            confidence = consensus_result.agreement_score

        # 创建统一记忆条目
        unified_memory = UnifiedMemoryEntry(
            id=memory_id,
            role_id=role_id,
            content=content,
            memory_type=memory_type,
            importance=importance,
            confidence=confidence,
            validation_level=validation_level,
            system_type=MemorySystemType.ROLE_MEMORY_BANK,  # 默认使用角色记忆银行
            timestamp=datetime.now().isoformat(),
            project_id=project_id,
            session_id=session_id,
            tags=tags or [],
            metadata=metadata or {},
            cross_model_validation=cross_model_validation,
            consensus_data=consensus_data,
        )

        # 保存到两套系统
        self._save_to_role_memory_bank(unified_memory)
        if validation_level in [
            MemoryValidationLevel.CROSS_MODEL,
            MemoryValidationLevel.CONSENSUS,
        ]:
            self._save_to_enhanced_memory_system(unified_memory)

        # 更新缓存
        self.unified_memory_cache[memory_id] = unified_memory

        # 保存到数据库
        await self._save_unified_memory(unified_memory)

        self.logger.info(f"添加统一记忆: {memory_id} (验证级别: {validation_level.value})")
        return memory_id

    def _save_to_role_memory_bank(self, unified_memory: UnifiedMemoryEntry):
        """保存到角色记忆银行"""
        self.role_memory_bank.add_memory(
            role_id=unified_memory.role_id,
            content=unified_memory.content,
            memory_type=unified_memory.memory_type,
            importance=unified_memory.importance,
            project_id=unified_memory.project_id,
            session_id=unified_memory.session_id,
            tags=unified_memory.tags,
            metadata=unified_memory.metadata,
        )

    def _save_to_enhanced_memory_system(self, unified_memory: UnifiedMemoryEntry):
        """保存到增强记忆系统"""
        # 创建协同记忆
        collaborative_memory = CollaborativeMemory(
            id=unified_memory.id,
            project_id=unified_memory.project_id or "default",
            session_id=unified_memory.session_id or "default",
            participants=[unified_memory.role_id],
            memory_type=self.enhanced_memory_system.MemoryType(
                unified_memory.memory_type,
            ),
            content=unified_memory.content,
            confidence=unified_memory.confidence,
            validation_status="validated"
            if unified_memory.validation_level
            in [MemoryValidationLevel.CROSS_MODEL, MemoryValidationLevel.CONSENSUS]
            else "pending",
            model_agreement=unified_memory.cross_model_validation or {},
            social_consensus=unified_memory.consensus_data.get("social_consensus")
            if unified_memory.consensus_data
            else None,
            timestamp=unified_memory.timestamp,
            metadata=unified_memory.metadata,
        )

        self.enhanced_memory_system.collaborative_memories[
            unified_memory.id
        ] = collaborative_memory

    async def get_memories(
        self,
        role_id: str,
        memory_type: Optional[str] = None,
        project_id: Optional[str] = None,
        session_id: Optional[str] = None,
        validation_level: Optional[MemoryValidationLevel] = None,
        limit: int = 10,
        min_importance: float = 0.0,
    ) -> list[UnifiedMemoryEntry]:
        """获取记忆"""
        memories = []

        # 从缓存中筛选
        for memory in self.unified_memory_cache.values():
            if memory.role_id != role_id:
                continue

            if memory_type and memory.memory_type != memory_type:
                continue

            if project_id and memory.project_id != project_id:
                continue

            if session_id and memory.session_id != session_id:
                continue

            if validation_level and memory.validation_level != validation_level:
                continue

            if memory.importance < min_importance:
                continue

            memories.append(memory)

        # 按重要性和时间排序
        memories.sort(key=lambda x: (x.importance, x.timestamp), reverse=True)

        return memories[:limit]

    async def build_context_for_conversation(
        self,
        role_id: str,
        current_question: str,
        project_id: Optional[str] = None,
        session_id: Optional[str] = None,
        conversation_history: Optional[list[dict[str, str]]] = None,
        target_model: str = "ollama",
    ) -> dict[str, Any]:
        """构建对话上下文"""
        # 获取相关记忆
        relevant_memories = await self.get_memories(
            role_id=role_id,
            project_id=project_id,
            session_id=session_id,
            limit=10,
            min_importance=0.3,
        )

        # 获取角色身份
        role_identity = self.role_memory_bank.get_role_identity(role_id)

        # 构建基础上下文
        context = {
            "role_identity": asdict(role_identity) if role_identity else None,
            "relevant_memories": [asdict(memory) for memory in relevant_memories],
            "current_question": current_question,
            "project_id": project_id,
            "session_id": session_id,
            "conversation_history": conversation_history or [],
        }

        # 根据目标模型调整上下文格式
        context = self._adapt_context_for_model(context, target_model)

        return context

    def _adapt_context_for_model(
        self,
        context: dict[str, Any],
        target_model: str,
    ) -> dict[str, Any]:
        """根据目标模型调整上下文格式"""
        model_formats = {
            "ollama": {
                "context_format": "conversation_history",
                "memory_compression": "semantic_summary",
                "max_memories": 5,
            },
            "openai": {
                "context_format": "structured_context",
                "memory_compression": "key_points",
                "max_memories": 8,
            },
            "anthropic": {
                "context_format": "conversation_history",
                "memory_compression": "semantic_summary",
                "max_memories": 6,
            },
        }

        format_config = model_formats.get(target_model, model_formats["ollama"])

        # 压缩记忆数量
        if len(context["relevant_memories"]) > format_config["max_memories"]:
            context["relevant_memories"] = context["relevant_memories"][
                : format_config["max_memories"]
            ]

        # 根据压缩策略处理记忆内容
        if format_config["memory_compression"] == "key_points":
            for memory in context["relevant_memories"]:
                memory["content"] = self._extract_key_points(memory["content"])

        return context

    def _extract_key_points(self, content: str) -> str:
        """提取关键点"""
        # 简单的关键点提取
        sentences = content.split("。")
        if len(sentences) > 3:
            return "。".join(sentences[:3]) + "。"
        return content

    async def cross_model_validate(
        self,
        content: str,
        models: list[str] = None,
    ) -> CrossModelValidationResult:
        """跨模型验证"""
        validation_id = hashlib.md5(
            f"validation_{content}_{time.time()}".encode(),
        ).hexdigest()[:16]

        # 获取可用模型
        if not models:
            available_models = self.model_manager.get_available_models()
            models = available_models[: self.config["max_validation_models"]]

        # 并行验证
        validation_tasks = []
        for model_name in models:
            task = self._validate_with_single_model(model_name, content)
            validation_tasks.append(task)

        validation_results = await asyncio.gather(
            *validation_tasks,
            return_exceptions=True,
        )

        # 分析验证结果
        valid_results = [r for r in validation_results if not isinstance(r, Exception)]

        if not valid_results:
            # 返回默认验证结果
            return CrossModelValidationResult(
                validation_id=validation_id,
                content=content,
                models_used=models,
                agreement_scores={"overall": 0.0},
                confidence_distribution={},
                uncertainty_metrics={"overall": 1.0},
                hallucination_detection={"overall": True},
                consensus_result="验证失败",
                validation_timestamp=datetime.now().isoformat(),
            )

        # 计算一致性分数
        agreement_scores = self._calculate_agreement_scores(valid_results)
        confidence_distribution = self._calculate_confidence_distribution(valid_results)
        uncertainty_metrics = self._calculate_uncertainty_metrics(valid_results)
        hallucination_detection = self._detect_hallucinations(valid_results)

        # 生成共识结果
        consensus_result = self._generate_consensus_result(
            valid_results,
            agreement_scores,
        )

        validation_result = CrossModelValidationResult(
            validation_id=validation_id,
            content=content,
            models_used=models,
            agreement_scores=agreement_scores,
            confidence_distribution=confidence_distribution,
            uncertainty_metrics=uncertainty_metrics,
            hallucination_detection=hallucination_detection,
            consensus_result=consensus_result,
            validation_timestamp=datetime.now().isoformat(),
        )

        # 缓存验证结果
        self.validation_cache[validation_id] = validation_result

        return validation_result

    async def _validate_with_single_model(
        self,
        model_name: str,
        content: str,
    ) -> dict[str, Any]:
        """使用单个模型验证"""
        try:
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

            response = await self.model_manager.generate_response(
                model_name=model_name,
                prompt=validation_prompt,
                max_tokens=500,
            )

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

        dimensions = ["accuracy", "consistency", "credibility"]
        agreement_scores = {}

        for dimension in dimensions:
            values = [r.get(dimension, 0.5) for r in validation_results]
            mean_value = sum(values) / len(values)
            variance = sum((v - mean_value) ** 2 for v in values) / len(values)
            agreement = max(0, 1 - variance)
            agreement_scores[dimension] = agreement

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

        uncertainty_scores = [r.get("uncertainty", 0.5) for r in validation_results]

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

    async def build_consensus(
        self,
        content: str,
        participants: list[str],
        project_id: Optional[str] = None,
    ) -> ConsensusResult:
        """构建共识"""
        consensus_id = hashlib.md5(
            f"consensus_{content}_{time.time()}".encode(),
        ).hexdigest()[:16]

        # 计算社会共识度
        social_consensus = await self._calculate_social_consensus(
            content,
            participants,
            project_id,
        )

        # 区块链验证
        blockchain_verified = await self._verify_on_blockchain(content, participants)

        # 计算整体一致性分数
        agreement_score = (
            social_consensus * 0.7 + (1.0 if blockchain_verified else 0.0) * 0.3
        )

        consensus_result = ConsensusResult(
            consensus_id=consensus_id,
            content=content,
            participants=participants,
            agreement_score=agreement_score,
            social_consensus=social_consensus,
            blockchain_verified=blockchain_verified,
            consensus_timestamp=datetime.now().isoformat(),
        )

        # 缓存共识结果
        self.consensus_cache[consensus_id] = consensus_result

        return consensus_result

    async def _calculate_social_consensus(
        self,
        content: str,
        participants: list[str],
        project_id: Optional[str] = None,
    ) -> float:
        """计算社会共识度"""
        if not participants:
            return 0.0

        # 使用增强记忆系统的社会计算功能
        return await self.enhanced_memory_system._calculate_social_consensus(
            content,
            participants,
            project_id or "default",
        )

    async def _verify_on_blockchain(
        self,
        content: str,
        participants: list[str],
    ) -> bool:
        """在区块链上验证"""
        try:
            # 创建共识提案
            proposal = {
                "content": content,
                "participants": participants,
                "timestamp": datetime.now().isoformat(),
            }

            # 提交到共识引擎
            result = await self.consensus_engine.propose_consensus(proposal)
            return result.get("verified", False)
        except Exception as e:
            self.logger.error(f"区块链验证失败: {e}")
            return False

    async def _save_unified_memory(self, memory: UnifiedMemoryEntry):
        """保存统一记忆到数据库"""
        db_path = self.data_dir / "unified_memory.db"

        with sqlite3.connect(db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO unified_memories
                (id, role_id, content, memory_type, importance, confidence, validation_level,
                 system_type, timestamp, project_id, session_id, tags, metadata,
                 cross_model_validation, consensus_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    memory.id,
                    memory.role_id,
                    memory.content,
                    memory.memory_type,
                    memory.importance,
                    memory.confidence,
                    memory.validation_level.value,
                    memory.system_type.value,
                    memory.timestamp,
                    memory.project_id,
                    memory.session_id,
                    json.dumps(memory.tags, ensure_ascii=False),
                    json.dumps(memory.metadata, ensure_ascii=False),
                    json.dumps(memory.cross_model_validation, ensure_ascii=False)
                    if memory.cross_model_validation
                    else None,
                    json.dumps(memory.consensus_data, ensure_ascii=False)
                    if memory.consensus_data
                    else None,
                ),
            )

    def get_memory_statistics(self) -> dict[str, Any]:
        """获取记忆统计信息"""
        stats = {
            "total_memories": len(self.unified_memory_cache),
            "system_distribution": defaultdict(int),
            "validation_distribution": defaultdict(int),
            "memory_types": defaultdict(int),
            "average_confidence": 0.0,
            "validation_coverage": 0.0,
        }

        total_confidence = 0.0
        validated_count = 0

        for memory in self.unified_memory_cache.values():
            stats["system_distribution"][memory.system_type.value] += 1
            stats["validation_distribution"][memory.validation_level.value] += 1
            stats["memory_types"][memory.memory_type] += 1

            total_confidence += memory.confidence

            if memory.validation_level in [
                MemoryValidationLevel.CROSS_MODEL,
                MemoryValidationLevel.CONSENSUS,
            ]:
                validated_count += 1

        if self.unified_memory_cache:
            stats["average_confidence"] = total_confidence / len(
                self.unified_memory_cache,
            )
            stats["validation_coverage"] = validated_count / len(
                self.unified_memory_cache,
            )

        return stats

    def close(self):
        """关闭服务"""
        self.role_memory_bank.close()
        self.logger.info("统一记忆服务已关闭")

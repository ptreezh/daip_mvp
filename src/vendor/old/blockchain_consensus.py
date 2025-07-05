"""区块链共识算法工具
用于协调多专家意见冲突，基于区块链共识机制达成一致意见
"""

import hashlib
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class ConsensusAlgorithm(Enum):
    """共识算法类型"""

    PROOF_OF_STAKE = "proof_of_stake"  # 权益证明
    PROOF_OF_AUTHORITY = "proof_of_authority"  # 权威证明
    DELEGATED_PROOF_OF_STAKE = "delegated_proof_of_stake"  # 委托权益证明
    PRACTICAL_BYZANTINE_FAULT_TOLERANCE = "pbft"  # 实用拜占庭容错


@dataclass
class Expert:
    """专家信息"""

    id: str
    name: str
    category: str
    reputation_score: float  # 声誉分数 (0-100)
    stake_weight: float  # 权益权重
    authority_level: int  # 权威等级 (1-5)
    specialties: list[str]
    voting_power: float = 1.0


@dataclass
class Opinion:
    """专家意见"""

    expert_id: str
    content: str
    confidence: float  # 置信度 (0-1)
    timestamp: str
    supporting_evidence: list[str]
    hash: str = ""

    def __post_init__(self):
        if not self.hash:
            self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """计算意见哈希值"""
        data = f"{self.expert_id}{self.content}{self.confidence}{self.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class ConflictResolutionBlock:
    """冲突解决区块"""

    block_id: str
    previous_hash: str
    timestamp: str
    opinions: list[Opinion]
    consensus_result: Optional[str]
    validator_signatures: list[str]
    merkle_root: str
    nonce: int = 0
    hash: str = ""

    def __post_init__(self):
        if not self.hash:
            self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """计算区块哈希值"""
        data = f"{self.block_id}{self.previous_hash}{self.timestamp}{self.merkle_root}{self.nonce}"
        return hashlib.sha256(data.encode()).hexdigest()

    def calculate_merkle_root(self) -> str:
        """计算默克尔树根"""
        if not self.opinions:
            return hashlib.sha256(b"").hexdigest()

        hashes = [opinion.hash for opinion in self.opinions]
        while len(hashes) > 1:
            new_hashes = []
            for i in range(0, len(hashes), 2):
                if i + 1 < len(hashes):
                    combined = hashes[i] + hashes[i + 1]
                else:
                    combined = hashes[i] + hashes[i]
                new_hashes.append(hashlib.sha256(combined.encode()).hexdigest())
            hashes = new_hashes

        return hashes[0] if hashes else hashlib.sha256(b"").hexdigest()


class BlockchainConsensusEngine:
    """区块链共识引擎"""

    def __init__(
        self,
        algorithm: ConsensusAlgorithm = ConsensusAlgorithm.PROOF_OF_AUTHORITY,
    ):
        self.algorithm = algorithm
        self.blockchain: list[ConflictResolutionBlock] = []
        self.experts: dict[str, Expert] = {}
        self.pending_opinions: list[Opinion] = []
        self.consensus_threshold = 0.67  # 67%共识阈值
        self.min_validators = 3  # 最少验证者数量

        # 创建创世区块
        self._create_genesis_block()

    def _create_genesis_block(self):
        """创建创世区块"""
        genesis_block = ConflictResolutionBlock(
            block_id="genesis",
            previous_hash="0",
            timestamp=datetime.now().isoformat(),
            opinions=[],
            consensus_result=None,
            validator_signatures=[],
            merkle_root=hashlib.sha256(b"genesis").hexdigest(),
        )
        self.blockchain.append(genesis_block)

    def register_expert(self, expert: Expert):
        """注册专家"""
        self.experts[expert.id] = expert

    def submit_opinion(
        self,
        expert_id: str,
        content: str,
        confidence: float,
        supporting_evidence: list[str] = None,
    ) -> Opinion:
        """提交专家意见"""
        if expert_id not in self.experts:
            raise ValueError(f"Expert {expert_id} not registered")

        opinion = Opinion(
            expert_id=expert_id,
            content=content,
            confidence=confidence,
            timestamp=datetime.now().isoformat(),
            supporting_evidence=supporting_evidence or [],
        )

        self.pending_opinions.append(opinion)
        return opinion

    def detect_conflicts(self) -> list[tuple[Opinion, Opinion, float]]:
        """检测意见冲突"""
        conflicts = []

        for i, opinion1 in enumerate(self.pending_opinions):
            for j, opinion2 in enumerate(self.pending_opinions[i + 1 :], i + 1):
                # 简单的冲突检测：基于内容相似度
                similarity = self._calculate_content_similarity(
                    opinion1.content,
                    opinion2.content,
                )
                if similarity < 0.3:  # 相似度低于30%认为是冲突
                    conflict_score = 1.0 - similarity
                    conflicts.append((opinion1, opinion2, conflict_score))

        return conflicts

    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """计算内容相似度（简化版本）"""
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())

        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    def run_consensus(self, topic: str) -> dict[str, Any]:
        """运行共识算法"""
        if not self.pending_opinions:
            return {"status": "error", "message": "No opinions to process"}

        # 根据选择的算法运行共识
        if self.algorithm == ConsensusAlgorithm.PROOF_OF_AUTHORITY:
            return self._proof_of_authority_consensus(topic)
        elif self.algorithm == ConsensusAlgorithm.PROOF_OF_STAKE:
            return self._proof_of_stake_consensus(topic)
        elif self.algorithm == ConsensusAlgorithm.DELEGATED_PROOF_OF_STAKE:
            return self._delegated_proof_of_stake_consensus(topic)
        elif self.algorithm == ConsensusAlgorithm.PRACTICAL_BYZANTINE_FAULT_TOLERANCE:
            return self._pbft_consensus(topic)
        else:
            return {"status": "error", "message": "Unsupported consensus algorithm"}

    def _proof_of_authority_consensus(self, topic: str) -> dict[str, Any]:
        """权威证明共识算法"""
        # 按权威等级和声誉分数排序专家
        expert_scores = {}
        opinion_weights = {}

        for opinion in self.pending_opinions:
            expert = self.experts[opinion.expert_id]
            # 权威分数 = 权威等级 * 声誉分数 * 置信度
            authority_score = (
                expert.authority_level * expert.reputation_score * opinion.confidence
            )
            expert_scores[opinion.expert_id] = authority_score
            opinion_weights[opinion.hash] = authority_score

        # 选择权威分数最高的意见作为共识
        if opinion_weights:
            consensus_opinion_hash = max(opinion_weights, key=opinion_weights.get)
            consensus_opinion = next(
                op for op in self.pending_opinions if op.hash == consensus_opinion_hash
            )

            # 创建新区块
            block = self._create_consensus_block(topic, consensus_opinion.content)

            return {
                "status": "success",
                "algorithm": "Proof of Authority",
                "consensus": consensus_opinion.content,
                "consensus_expert": self.experts[consensus_opinion.expert_id].name,
                "authority_score": opinion_weights[consensus_opinion_hash],
                "block_hash": block.hash,
                "participating_experts": len(self.pending_opinions),
            }

        return {"status": "error", "message": "No valid opinions for consensus"}

    def _proof_of_stake_consensus(self, topic: str) -> dict[str, Any]:
        """权益证明共识算法"""
        # 基于专家的权益权重进行投票
        opinion_stakes = {}
        total_stake = 0

        for opinion in self.pending_opinions:
            expert = self.experts[opinion.expert_id]
            stake = expert.stake_weight * opinion.confidence
            opinion_stakes[opinion.hash] = stake
            total_stake += stake

        # 找到获得最多权益支持的意见
        if opinion_stakes and total_stake > 0:
            max_stake_hash = max(opinion_stakes, key=opinion_stakes.get)
            max_stake = opinion_stakes[max_stake_hash]

            # 检查是否达到共识阈值
            if max_stake / total_stake >= self.consensus_threshold:
                consensus_opinion = next(
                    op for op in self.pending_opinions if op.hash == max_stake_hash
                )
                block = self._create_consensus_block(topic, consensus_opinion.content)

                return {
                    "status": "success",
                    "algorithm": "Proof of Stake",
                    "consensus": consensus_opinion.content,
                    "stake_percentage": (max_stake / total_stake) * 100,
                    "block_hash": block.hash,
                    "total_stake": total_stake,
                }

        return {
            "status": "no_consensus",
            "message": "Failed to reach consensus threshold",
        }

    def _delegated_proof_of_stake_consensus(self, topic: str) -> dict[str, Any]:
        """委托权益证明共识算法"""
        # 选择权益最高的专家作为代表
        delegates = sorted(
            self.experts.values(),
            key=lambda x: x.stake_weight * x.reputation_score,
            reverse=True,
        )[
            : min(5, len(self.experts))
        ]  # 选择最多5个代表

        delegate_votes = {}
        for opinion in self.pending_opinions:
            if opinion.expert_id in [d.id for d in delegates]:
                expert = self.experts[opinion.expert_id]
                vote_weight = (
                    expert.stake_weight * expert.reputation_score * opinion.confidence
                )
                delegate_votes[opinion.hash] = vote_weight

        if delegate_votes:
            consensus_hash = max(delegate_votes, key=delegate_votes.get)
            consensus_opinion = next(
                op for op in self.pending_opinions if op.hash == consensus_hash
            )
            block = self._create_consensus_block(topic, consensus_opinion.content)

            return {
                "status": "success",
                "algorithm": "Delegated Proof of Stake",
                "consensus": consensus_opinion.content,
                "delegates_count": len(delegates),
                "vote_weight": delegate_votes[consensus_hash],
                "block_hash": block.hash,
            }

        return {"status": "error", "message": "No delegate opinions available"}

    def _pbft_consensus(self, topic: str) -> dict[str, Any]:
        """实用拜占庭容错共识算法"""
        # 简化的PBFT实现
        if len(self.pending_opinions) < self.min_validators:
            return {
                "status": "error",
                "message": f"Need at least {self.min_validators} validators",
            }

        # 三阶段：预准备、准备、提交
        opinion_votes = {}

        # 统计每个意见的支持度
        for opinion in self.pending_opinions:
            content_key = opinion.content.strip().lower()
            if content_key not in opinion_votes:
                opinion_votes[content_key] = []
            opinion_votes[content_key].append(opinion)

        # 检查是否有意见获得2/3以上支持
        required_votes = int(len(self.pending_opinions) * 2 / 3) + 1

        for content, votes in opinion_votes.items():
            if len(votes) >= required_votes:
                # 达成共识
                representative_opinion = votes[0]
                block = self._create_consensus_block(
                    topic,
                    representative_opinion.content,
                )

                return {
                    "status": "success",
                    "algorithm": "Practical Byzantine Fault Tolerance",
                    "consensus": representative_opinion.content,
                    "supporting_votes": len(votes),
                    "required_votes": required_votes,
                    "total_validators": len(self.pending_opinions),
                    "block_hash": block.hash,
                }

        return {"status": "no_consensus", "message": "Failed to reach 2/3 majority"}

    def _create_consensus_block(
        self,
        topic: str,
        consensus_content: str,
    ) -> ConflictResolutionBlock:
        """创建共识区块"""
        previous_block = self.blockchain[-1]

        block = ConflictResolutionBlock(
            block_id=str(uuid.uuid4()),
            previous_hash=previous_block.hash,
            timestamp=datetime.now().isoformat(),
            opinions=self.pending_opinions.copy(),
            consensus_result=consensus_content,
            validator_signatures=[expert.id for expert in self.experts.values()],
            merkle_root="",
        )

        block.merkle_root = block.calculate_merkle_root()
        block.hash = block.calculate_hash()

        self.blockchain.append(block)
        self.pending_opinions.clear()  # 清空待处理意见

        return block

    def get_consensus_history(self) -> list[dict[str, Any]]:
        """获取共识历史"""
        history = []
        for block in self.blockchain[1:]:  # 跳过创世区块
            history.append(
                {
                    "block_id": block.block_id,
                    "timestamp": block.timestamp,
                    "consensus_result": block.consensus_result,
                    "opinions_count": len(block.opinions),
                    "validators": block.validator_signatures,
                    "block_hash": block.hash,
                },
            )
        return history

    def validate_blockchain(self) -> bool:
        """验证区块链完整性"""
        for i in range(1, len(self.blockchain)):
            current_block = self.blockchain[i]
            previous_block = self.blockchain[i - 1]

            # 验证哈希链
            if current_block.previous_hash != previous_block.hash:
                return False

            # 验证区块哈希
            if current_block.hash != current_block.calculate_hash():
                return False

            # 验证默克尔根
            if current_block.merkle_root != current_block.calculate_merkle_root():
                return False

        return True

"""区块链共识系统与角色系统集成模块
将独立的区块链共识模块与现有角色管理系统打通
"""

import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Optional

from src.blockchain_consensus import (
    BlockchainConsensusEngine,
    ConsensusAlgorithm,
)
from src.blockchain_consensus import (
    Expert as BlockchainExpert,
)
from src.dynamic_role_manager import DynamicRoleManager, TaskContext
from src.enhanced_recommendation_engine import EnhancedRecommendationEngine
from src.expert_library import ExpertLibrary


@dataclass
class ConsensusSession:
    """共识会话"""

    session_id: str
    topic: str
    description: str
    algorithm: ConsensusAlgorithm
    participants: list[str]  # expert_ids
    status: str  # active, completed, cancelled
    created_at: str
    completed_at: Optional[str] = None
    consensus_result: Optional[dict[str, Any]] = None


class ConsensusRoleIntegration:
    """区块链共识与角色系统集成管理器"""

    def __init__(self, data_dir: str = "data/consensus"):
        self.logger = logging.getLogger(__name__)
        self.data_dir = data_dir
        self.sessions_dir = os.path.join(data_dir, "sessions")
        self.mappings_file = os.path.join(data_dir, "expert_mappings.json")

        # 确保目录存在
        os.makedirs(self.sessions_dir, exist_ok=True)

        # 初始化组件
        self.expert_library = ExpertLibrary()
        self.dynamic_role_manager = DynamicRoleManager(self.expert_library)
        self.recommendation_engine = EnhancedRecommendationEngine(self.expert_library)
        self.consensus_engine = BlockchainConsensusEngine()

        # 加载数据
        self.active_sessions: dict[str, ConsensusSession] = {}
        self.expert_mappings = self._load_expert_mappings()

        # 同步专家数据
        self._sync_experts_to_blockchain()

    def _load_expert_mappings(self) -> dict[str, str]:
        """加载专家映射关系"""
        if os.path.exists(self.mappings_file):
            try:
                with open(self.mappings_file, encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load expert mappings: {e}")
        return {}

    def _save_expert_mappings(self):
        """保存专家映射关系"""
        try:
            with open(self.mappings_file, "w", encoding="utf-8") as f:
                json.dump(self.expert_mappings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save expert mappings: {e}")

    def _sync_experts_to_blockchain(self):
        """同步专家库到区块链共识系统"""
        all_experts = self.expert_library.get_all_experts()

        for expert_data in all_experts:
            # 转换为区块链专家格式
            blockchain_expert = self._convert_to_blockchain_expert(expert_data)

            # 注册到区块链系统
            self.consensus_engine.register_expert(blockchain_expert)

            # 记录映射关系
            self.expert_mappings[expert_data["id"]] = blockchain_expert.id

        self._save_expert_mappings()
        self.logger.info(
            f"Synced {len(all_experts)} experts to blockchain consensus system",
        )

    def _convert_to_blockchain_expert(
        self,
        expert_data: dict[str, Any],
    ) -> BlockchainExpert:
        """将专家库专家转换为区块链专家格式"""
        # 计算权威等级 (1-5)
        authority_level = self._calculate_authority_level(expert_data)

        # 计算权益权重
        stake_weight = self._calculate_stake_weight(expert_data)

        # 获取声誉分数 (0-100)
        reputation_score = expert_data.get("reputation_score", 50.0)
        if reputation_score <= 1.0:  # 如果是0-1范围，转换为0-100
            reputation_score *= 100

        blockchain_expert = BlockchainExpert(
            id=expert_data["id"],
            name=expert_data["name"],
            category=expert_data.get("category", "general"),
            reputation_score=reputation_score,
            stake_weight=stake_weight,
            authority_level=authority_level,
            specialties=expert_data.get("specialties", []),
            voting_power=self._calculate_voting_power(expert_data),
        )

        return blockchain_expert

    def _calculate_authority_level(self, expert_data: dict[str, Any]) -> int:
        """计算专家权威等级 (1-5)"""
        # 基于经验年限、评级、专业领域数量等因素
        experience_years = expert_data.get("experience_years", 0)
        rating = expert_data.get("rating", 0.0)
        specialties_count = len(expert_data.get("specialties", []))

        # 权威等级计算逻辑
        level = 1

        if experience_years >= 15 and rating >= 4.5:
            level = 5
        elif experience_years >= 10 and rating >= 4.0:
            level = 4
        elif experience_years >= 5 and rating >= 3.5:
            level = 3
        elif experience_years >= 2 and rating >= 3.0:
            level = 2

        # 专业领域加成
        if specialties_count >= 3:
            level = min(5, level + 1)

        return level

    def _calculate_stake_weight(self, expert_data: dict[str, Any]) -> float:
        """计算专家权益权重"""
        # 基于声誉、经验、活跃度等因素
        reputation = expert_data.get("reputation_score", 0.5)
        experience_years = expert_data.get("experience_years", 0)
        activity_score = expert_data.get("recent_activity_score", 0.5)

        # 权益权重计算
        base_weight = (
            reputation * 0.4
            + min(experience_years / 20, 1.0) * 0.4
            + activity_score * 0.2
        )

        return max(0.1, min(1.0, base_weight))

    def _calculate_voting_power(self, expert_data: dict[str, Any]) -> float:
        """计算投票权重"""
        # 综合考虑多个因素
        reputation = expert_data.get("reputation_score", 0.5)
        authority_level = self._calculate_authority_level(expert_data)
        collaboration_score = expert_data.get("collaboration_score", 0.5)

        voting_power = (
            reputation * 0.5 + (authority_level / 5) * 0.3 + collaboration_score * 0.2
        )

        return max(0.1, min(2.0, voting_power))

    def create_consensus_session(
        self,
        topic: str,
        description: str,
        algorithm: ConsensusAlgorithm = ConsensusAlgorithm.PROOF_OF_AUTHORITY,
        required_expertise: list[str] = None,
        max_participants: int = 10,
    ) -> str:
        """创建共识会话"""
        session_id = f"consensus_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 推荐合适的专家参与
        recommended_experts = self._recommend_consensus_participants(
            topic,
            required_expertise,
            max_participants,
        )

        # 创建会话
        session = ConsensusSession(
            session_id=session_id,
            topic=topic,
            description=description,
            algorithm=algorithm,
            participants=[expert["id"] for expert in recommended_experts],
            status="active",
            created_at=datetime.now().isoformat(),
        )

        self.active_sessions[session_id] = session
        self._save_session(session)

        # 设置共识引擎算法
        self.consensus_engine.algorithm = algorithm

        self.logger.info(
            f"Created consensus session: {session_id} with {len(recommended_experts)} participants",
        )

        return session_id

    def _recommend_consensus_participants(
        self,
        topic: str,
        required_expertise: list[str] = None,
        max_participants: int = 10,
    ) -> list[dict[str, Any]]:
        """推荐共识参与者"""
        if required_expertise is None:
            required_expertise = []

        # 创建任务上下文
        task_context = TaskContext(
            task_id=f"consensus_{topic}",
            task_type="共识决策",
            domain="专家协商",
            complexity="高",
            required_skills=required_expertise,
            preferred_skills=[],
            collaboration_type="共识建立",
        )

        # 获取推荐专家
        recommended_experts = self.dynamic_role_manager.load_roles_for_task(
            task_context,
            max_roles=max_participants,
        )

        # 增强推荐信息
        enhanced_experts = []
        for expert in recommended_experts:
            # 计算共识适合度
            consensus_fitness = self._calculate_consensus_fitness(expert, topic)

            expert_info = {
                "id": expert["id"],
                "name": expert["name"],
                "specialties": expert.get("specialties", []),
                "reputation_score": expert.get("reputation_score", 0.5),
                "authority_level": self._calculate_authority_level(expert),
                "consensus_fitness": consensus_fitness,
                "voting_power": self._calculate_voting_power(expert),
            }
            enhanced_experts.append(expert_info)

        # 按共识适合度排序
        enhanced_experts.sort(key=lambda x: x["consensus_fitness"], reverse=True)

        return enhanced_experts

    def _calculate_consensus_fitness(self, expert: dict[str, Any], topic: str) -> float:
        """计算专家的共识适合度"""
        # 基于多个因素计算适合度
        factors = {
            "relevance": self.recommendation_engine.calculate_relevance_score(
                expert,
                topic,
            ),
            "reputation": expert.get("reputation_score", 0.5),
            "collaboration": expert.get("collaboration_score", 0.5),
            "objectivity": expert.get("objectivity_score", 0.7),  # 客观性分数
            "communication": expert.get("communication_score", 0.6),  # 沟通能力分数
        }

        # 加权计算
        weights = {
            "relevance": 0.3,
            "reputation": 0.25,
            "collaboration": 0.2,
            "objectivity": 0.15,
            "communication": 0.1,
        }

        fitness = sum(factors[key] * weights[key] for key in factors)
        return min(fitness, 1.0)

    def submit_expert_opinion(
        self,
        session_id: str,
        expert_id: str,
        content: str,
        confidence: float,
        supporting_evidence: list[str] = None,
    ) -> bool:
        """提交专家意见"""
        if session_id not in self.active_sessions:
            return False

        session = self.active_sessions[session_id]
        if expert_id not in session.participants:
            return False

        # 获取区块链专家ID
        blockchain_expert_id = self.expert_mappings.get(expert_id, expert_id)

        try:
            # 提交意见到区块链共识系统
            opinion = self.consensus_engine.submit_opinion(
                blockchain_expert_id,
                content,
                confidence,
                supporting_evidence,
            )

            self.logger.info(
                f"Opinion submitted by {expert_id} in session {session_id}",
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to submit opinion: {e}")
            return False

    def run_consensus(self, session_id: str) -> dict[str, Any]:
        """运行共识算法"""
        if session_id not in self.active_sessions:
            return {"status": "error", "message": "Session not found"}

        session = self.active_sessions[session_id]
        if session.status != "active":
            return {"status": "error", "message": "Session not active"}

        try:
            # 运行共识算法
            consensus_result = self.consensus_engine.run_consensus(session.topic)

            # 更新会话状态
            session.status = "completed"
            session.completed_at = datetime.now().isoformat()
            session.consensus_result = consensus_result

            self._save_session(session)

            # 更新参与专家的声誉分数
            self._update_expert_reputation_after_consensus(session, consensus_result)

            self.logger.info(f"Consensus completed for session {session_id}")

            return {
                "session_id": session_id,
                "consensus_result": consensus_result,
                "participants": len(session.participants),
                "algorithm": session.algorithm.value,
            }
        except Exception as e:
            self.logger.error(f"Failed to run consensus: {e}")
            return {"status": "error", "message": str(e)}

    def _update_expert_reputation_after_consensus(
        self,
        session: ConsensusSession,
        consensus_result: dict[str, Any],
    ):
        """根据共识结果更新专家声誉"""
        if consensus_result.get("status") != "success":
            return

        # 获取共识内容
        consensus_content = consensus_result.get("consensus", "")

        # 分析每个专家的贡献
        for expert_id in session.participants:
            blockchain_expert_id = self.expert_mappings.get(expert_id, expert_id)

            # 计算专家贡献度
            contribution_score = self._calculate_expert_contribution(
                blockchain_expert_id,
                consensus_content,
            )

            # 更新声誉分数
            current_reputation = self.expert_library.get_expert_by_id(expert_id)
            if current_reputation:
                new_reputation = self._adjust_reputation_score(
                    current_reputation.get("reputation_score", 0.5),
                    contribution_score,
                )

                # 更新专家信息
                self.expert_library.update_expert(
                    expert_id,
                    {
                        "reputation_score": new_reputation,
                        "last_consensus_participation": datetime.now().isoformat(),
                    },
                )

    def _calculate_expert_contribution(
        self,
        blockchain_expert_id: str,
        consensus_content: str,
    ) -> float:
        """计算专家在共识中的贡献度"""
        # 查找专家的意见
        expert_opinion = None
        for opinion in self.consensus_engine.pending_opinions:
            if opinion.expert_id == blockchain_expert_id:
                expert_opinion = opinion
                break

        if not expert_opinion:
            return 0.0

        # 计算意见与最终共识的相似度
        similarity = self._calculate_content_similarity(
            expert_opinion.content,
            consensus_content,
        )

        # 考虑置信度
        contribution = similarity * expert_opinion.confidence

        return min(contribution, 1.0)

    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """计算内容相似度"""
        # 简单的词汇重叠相似度计算
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0

    def _adjust_reputation_score(
        self,
        current_score: float,
        contribution: float,
    ) -> float:
        """调整声誉分数"""
        # 基于贡献度调整声誉分数
        adjustment = (contribution - 0.5) * 0.1  # 最大调整±0.05
        new_score = current_score + adjustment

        return max(0.0, min(1.0, new_score))

    def get_session_status(self, session_id: str) -> dict[str, Any]:
        """获取会话状态"""
        if session_id not in self.active_sessions:
            return {"status": "not_found"}

        session = self.active_sessions[session_id]

        # 获取参与者详细信息
        participants_info = []
        for expert_id in session.participants:
            expert = self.expert_library.get_expert_by_id(expert_id)
            if expert:
                participants_info.append(
                    {
                        "id": expert_id,
                        "name": expert["name"],
                        "specialties": expert.get("specialties", []),
                        "reputation_score": expert.get("reputation_score", 0.5),
                    },
                )

        # 获取已提交的意见数量
        blockchain_participant_ids = [
            self.expert_mappings.get(eid, eid) for eid in session.participants
        ]
        submitted_opinions = len(
            [
                op
                for op in self.consensus_engine.pending_opinions
                if op.expert_id in blockchain_participant_ids
            ],
        )

        return {
            "session_id": session_id,
            "topic": session.topic,
            "description": session.description,
            "algorithm": session.algorithm.value,
            "status": session.status,
            "created_at": session.created_at,
            "completed_at": session.completed_at,
            "participants": participants_info,
            "total_participants": len(session.participants),
            "submitted_opinions": submitted_opinions,
            "consensus_result": session.consensus_result,
        }

    def get_expert_consensus_history(self, expert_id: str) -> list[dict[str, Any]]:
        """获取专家的共识参与历史"""
        history = []

        # 遍历所有会话文件
        if os.path.exists(self.sessions_dir):
            for filename in os.listdir(self.sessions_dir):
                if filename.endswith(".json"):
                    session_path = os.path.join(self.sessions_dir, filename)
                    try:
                        with open(session_path, encoding="utf-8") as f:
                            session_data = json.load(f)

                        if expert_id in session_data.get("participants", []):
                            history.append(
                                {
                                    "session_id": session_data["session_id"],
                                    "topic": session_data["topic"],
                                    "status": session_data["status"],
                                    "created_at": session_data["created_at"],
                                    "completed_at": session_data.get("completed_at"),
                                    "algorithm": session_data["algorithm"],
                                    "consensus_achieved": session_data.get(
                                        "consensus_result",
                                        {},
                                    ).get("status")
                                    == "success",
                                },
                            )
                    except Exception as e:
                        self.logger.error(f"Failed to load session {filename}: {e}")

        # 按时间排序
        history.sort(key=lambda x: x["created_at"], reverse=True)

        return history

    def _save_session(self, session: ConsensusSession):
        """保存会话到文件"""
        session_path = os.path.join(self.sessions_dir, f"{session.session_id}.json")

        session_data = asdict(session)
        session_data["algorithm"] = session.algorithm.value

        try:
            with open(session_path, "w", encoding="utf-8") as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save session: {e}")

    def get_consensus_statistics(self) -> dict[str, Any]:
        """获取共识统计信息"""
        total_sessions = 0
        completed_sessions = 0
        successful_consensus = 0
        algorithm_usage = {}

        # 统计所有会话
        if os.path.exists(self.sessions_dir):
            for filename in os.listdir(self.sessions_dir):
                if filename.endswith(".json"):
                    try:
                        session_path = os.path.join(self.sessions_dir, filename)
                        with open(session_path, encoding="utf-8") as f:
                            session_data = json.load(f)

                        total_sessions += 1

                        if session_data["status"] == "completed":
                            completed_sessions += 1

                            if (
                                session_data.get("consensus_result", {}).get("status")
                                == "success"
                            ):
                                successful_consensus += 1

                        algorithm = session_data["algorithm"]
                        algorithm_usage[algorithm] = (
                            algorithm_usage.get(algorithm, 0) + 1
                        )

                    except Exception as e:
                        self.logger.error(f"Failed to process session {filename}: {e}")

        return {
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "successful_consensus": successful_consensus,
            "success_rate": successful_consensus / completed_sessions
            if completed_sessions > 0
            else 0,
            "algorithm_usage": algorithm_usage,
            "total_experts": len(self.expert_mappings),
            "active_sessions": len(
                [s for s in self.active_sessions.values() if s.status == "active"],
            ),
        }

    def register_expert_to_session(
        self,
        session_id: str,
        expert_id: str,
        name: str,
        category: str,
        reputation_score: float,
        stake_weight: float,
        authority_level: int,
        specialties: list[str],
    ):
        """注册专家到指定共识会话，自动同步到专家库和区块链共识系统"""
        if session_id not in self.active_sessions:
            raise ValueError("Session not found")
        session = self.active_sessions[session_id]
        if expert_id in session.participants:
            raise ValueError("Expert already registered in session")
        # 1. 专家库中查找/添加专家
        expert = self.expert_library.get_expert_by_id(expert_id)
        if not expert:
            expert_data = {
                "id": expert_id,
                "name": name,
                "category": category,
                "reputation_score": reputation_score,
                "stake_weight": stake_weight,
                "authority_level": authority_level,
                "specialties": specialties,
                # 兼容 Expert 数据结构
                "title": "",
                "description": "",
                "experience_years": 0,
                "contact_info": {},
                "skills": [],
                "languages": ["中文"],
                "availability": "可用",
                "hourly_rate": None,
                "location": "",
                "education": [],
                "certifications": [],
                "projects": [],
                "bio": "",
                "source_file": "manual_entry",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "tags": [],
            }
            self.expert_library.add_expert_manually(expert_data)
        # 2. 添加到会话参与者
        session.participants.append(expert_id)
        self._save_session(session)
        # 3. 注册到区块链共识系统
        blockchain_expert = self._convert_to_blockchain_expert(
            {
                "id": expert_id,
                "name": name,
                "category": category,
                "reputation_score": reputation_score,
                "stake_weight": stake_weight,
                "authority_level": authority_level,
                "specialties": specialties,
            },
        )
        self.consensus_engine.register_expert(blockchain_expert)
        self.expert_mappings[expert_id] = blockchain_expert.id
        self._save_expert_mappings()

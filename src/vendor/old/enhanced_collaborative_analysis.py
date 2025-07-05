"""增强的协同文档分析系统
集成动态角色管理、记忆系统和多角色协作工作流
"""

import asyncio
import json
import logging
import os
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

from src.document_parser import DocumentParser
from src.dynamic_role_manager import DynamicRoleManager, TaskContext
from src.enhanced_recommendation_engine import EnhancedRecommendationEngine
from src.expert_library import ExpertLibrary
from src.multi_role_chat import MultiRoleChatEngine


class AnalysisPhase(Enum):
    """分析阶段"""

    INITIALIZATION = "initialization"
    DOCUMENT_PARSING = "document_parsing"
    EXPERT_ASSIGNMENT = "expert_assignment"
    PARALLEL_ANALYSIS = "parallel_analysis"
    CROSS_VALIDATION = "cross_validation"
    CONSENSUS_BUILDING = "consensus_building"
    FINAL_SYNTHESIS = "final_synthesis"
    QUALITY_REVIEW = "quality_review"
    COMPLETED = "completed"


class AnalysisType(Enum):
    """分析类型"""

    FINANCIAL_REPORT = "financial_report"
    LEGAL_DOCUMENT = "legal_document"
    RESEARCH_PAPER = "research_paper"
    TECHNICAL_SPEC = "technical_spec"
    BUSINESS_PLAN = "business_plan"
    POLICY_DOCUMENT = "policy_document"
    GENERAL_ANALYSIS = "general_analysis"


@dataclass
class AnalysisTask:
    """分析任务"""

    task_id: str
    document_name: str
    document_content: str
    analysis_type: AnalysisType
    requester_id: str
    created_at: str
    current_phase: AnalysisPhase
    assigned_experts: list[str]
    analysis_results: dict[str, Any]
    collaboration_history: list[dict[str, Any]]
    quality_metrics: dict[str, float]
    estimated_completion: Optional[str] = None
    actual_completion: Optional[str] = None


@dataclass
class ExpertAnalysis:
    """专家分析结果"""

    expert_id: str
    expert_name: str
    analysis_content: str
    confidence_score: float
    key_findings: list[str]
    recommendations: list[str]
    supporting_evidence: list[str]
    analysis_timestamp: str
    review_status: str = "pending"


@dataclass
class CollaborativeMemory:
    """协作记忆"""

    memory_id: str
    task_id: str
    expert_id: str
    memory_type: str  # insight, pattern, methodology, lesson_learned
    content: str
    relevance_tags: list[str]
    created_at: str
    usage_count: int = 0
    last_accessed: Optional[str] = None


class EnhancedCollaborativeAnalysis:
    """增强的协同文档分析系统"""

    def __init__(self, data_dir: str = "data/collaborative_analysis"):
        self.data_dir = data_dir
        self.tasks_dir = os.path.join(data_dir, "tasks")
        self.memories_dir = os.path.join(data_dir, "memories")
        self.workflows_dir = os.path.join(data_dir, "workflows")

        # 确保目录存在
        for directory in [self.tasks_dir, self.memories_dir, self.workflows_dir]:
            os.makedirs(directory, exist_ok=True)

        # 初始化组件
        self.expert_library = ExpertLibrary()
        self.dynamic_role_manager = DynamicRoleManager(self.expert_library)
        self.multi_role_chat = MultiRoleChatEngine(self.expert_library)
        self.document_parser = DocumentParser()
        self.recommendation_engine = EnhancedRecommendationEngine(self.expert_library)

        # 活跃任务和记忆
        self.active_tasks: dict[str, AnalysisTask] = {}
        self.collaborative_memories: dict[str, list[CollaborativeMemory]] = {}

        # 加载现有数据
        self._load_existing_data()

        self.logger = logging.getLogger(__name__)

    def _load_existing_data(self):
        """加载现有数据"""
        # 加载活跃任务
        if os.path.exists(self.tasks_dir):
            for filename in os.listdir(self.tasks_dir):
                if filename.endswith(".json") and not filename.startswith("completed_"):
                    task_path = os.path.join(self.tasks_dir, filename)
                    try:
                        with open(task_path, encoding="utf-8") as f:
                            task_data = json.load(f)

                        # 转换为AnalysisTask对象
                        task = AnalysisTask(**task_data)
                        self.active_tasks[task.task_id] = task
                    except Exception as e:
                        self.logger.error(f"Failed to load task {filename}: {e}")

        # 加载协作记忆
        if os.path.exists(self.memories_dir):
            for filename in os.listdir(self.memories_dir):
                if filename.endswith(".json"):
                    memory_path = os.path.join(self.memories_dir, filename)
                    try:
                        with open(memory_path, encoding="utf-8") as f:
                            memories_data = json.load(f)

                        task_id = filename.replace(".json", "")
                        memories = []
                        for memory_data in memories_data:
                            memory = CollaborativeMemory(**memory_data)
                            memories.append(memory)

                        self.collaborative_memories[task_id] = memories
                    except Exception as e:
                        self.logger.error(f"Failed to load memories {filename}: {e}")

    def create_analysis_task(
        self,
        document_name: str,
        document_content: str,
        analysis_type: AnalysisType,
        requester_id: str,
        custom_requirements: list[str] = None,
    ) -> str:
        """创建分析任务"""
        task_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        # 创建任务
        task = AnalysisTask(
            task_id=task_id,
            document_name=document_name,
            document_content=document_content,
            analysis_type=analysis_type,
            requester_id=requester_id,
            created_at=datetime.now().isoformat(),
            current_phase=AnalysisPhase.INITIALIZATION,
            assigned_experts=[],
            analysis_results={},
            collaboration_history=[],
            quality_metrics={},
        )

        # 估算完成时间
        task.estimated_completion = self._estimate_completion_time(
            task,
            custom_requirements,
        )

        # 保存任务
        self.active_tasks[task_id] = task
        self._save_task(task)

        # 启动分析工作流
        asyncio.create_task(
            self._execute_analysis_workflow(task_id, custom_requirements),
        )

        self.logger.info(f"Created analysis task: {task_id}")
        return task_id

    def _estimate_completion_time(
        self,
        task: AnalysisTask,
        custom_requirements: list[str] = None,
    ) -> str:
        """估算完成时间"""
        base_hours = 4  # 基础时间

        # 根据文档长度调整
        doc_length = len(task.document_content)
        if doc_length > 10000:
            base_hours += 2
        if doc_length > 50000:
            base_hours += 4

        # 根据分析类型调整
        type_multipliers = {
            AnalysisType.FINANCIAL_REPORT: 1.2,
            AnalysisType.LEGAL_DOCUMENT: 1.5,
            AnalysisType.RESEARCH_PAPER: 1.3,
            AnalysisType.TECHNICAL_SPEC: 1.1,
            AnalysisType.BUSINESS_PLAN: 1.2,
            AnalysisType.POLICY_DOCUMENT: 1.4,
            AnalysisType.GENERAL_ANALYSIS: 1.0,
        }

        base_hours *= type_multipliers.get(task.analysis_type, 1.0)

        # 根据自定义需求调整
        if custom_requirements:
            base_hours += len(custom_requirements) * 0.5

        completion_time = datetime.now() + timedelta(hours=base_hours)
        return completion_time.isoformat()

    async def _execute_analysis_workflow(
        self,
        task_id: str,
        custom_requirements: list[str] = None,
    ):
        """执行分析工作流"""
        try:
            task = self.active_tasks[task_id]

            # 阶段1: 文档解析
            await self._phase_document_parsing(task)

            # 阶段2: 专家分配
            await self._phase_expert_assignment(task, custom_requirements)

            # 阶段3: 并行分析
            await self._phase_parallel_analysis(task)

            # 阶段4: 交叉验证
            await self._phase_cross_validation(task)

            # 阶段5: 共识建立
            await self._phase_consensus_building(task)

            # 阶段6: 最终综合
            await self._phase_final_synthesis(task)

            # 阶段7: 质量审查
            await self._phase_quality_review(task)

            # 完成任务
            task.current_phase = AnalysisPhase.COMPLETED
            task.actual_completion = datetime.now().isoformat()
            self._save_task(task)

            self.logger.info(f"Analysis workflow completed for task: {task_id}")

        except Exception as e:
            self.logger.error(f"Analysis workflow failed for task {task_id}: {e}")
            task = self.active_tasks.get(task_id)
            if task:
                task.analysis_results["error"] = str(e)
                self._save_task(task)

    async def _phase_document_parsing(self, task: AnalysisTask):
        """文档解析阶段"""
        task.current_phase = AnalysisPhase.DOCUMENT_PARSING
        self._save_task(task)

        # 解析文档
        parsing_result = self.document_parser.parse_document(
            task.document_name,
            task.document_content.encode("utf-8"),
        )

        if parsing_result.success:
            task.analysis_results["document_chunks"] = [
                {
                    "chunk_id": chunk.chunk_id,
                    "content": chunk.content,
                    "metadata": chunk.metadata,
                }
                for chunk in parsing_result.chunks
            ]
            task.analysis_results["parsing_stats"] = {
                "total_chunks": len(parsing_result.chunks),
                "total_chars": parsing_result.total_chars,
                "parsing_method": "enhanced_parser",
            }
        else:
            # 使用原始内容作为单个块
            task.analysis_results["document_chunks"] = [
                {
                    "chunk_id": "single_chunk",
                    "content": task.document_content,
                    "metadata": {"parsing_method": "fallback"},
                },
            ]

        # 记录协作历史
        task.collaboration_history.append(
            {
                "phase": "document_parsing",
                "timestamp": datetime.now().isoformat(),
                "action": "document_parsed",
                "details": task.analysis_results.get("parsing_stats", {}),
            },
        )

        self._save_task(task)

    async def _phase_expert_assignment(
        self,
        task: AnalysisTask,
        custom_requirements: list[str] = None,
    ):
        """专家分配阶段"""
        task.current_phase = AnalysisPhase.EXPERT_ASSIGNMENT
        self._save_task(task)

        # 创建任务上下文
        required_skills = self._extract_required_skills(task, custom_requirements)

        task_context = TaskContext(
            task_id=task.task_id,
            task_type="文档分析",
            domain=self._get_domain_from_analysis_type(task.analysis_type),
            complexity="高",
            required_skills=required_skills,
            preferred_skills=[],
            collaboration_type="协同分析",
        )

        # 获取推荐专家
        recommended_experts = self.dynamic_role_manager.load_roles_for_task(
            task_context,
            max_roles=6,
        )

        # 分配专家角色
        task.assigned_experts = [expert["id"] for expert in recommended_experts]

        # 记录专家分配详情
        task.analysis_results["assigned_experts"] = [
            {
                "expert_id": expert["id"],
                "name": expert["name"],
                "specialties": expert.get("specialties", []),
                "role_in_analysis": self._determine_expert_role(
                    expert,
                    task.analysis_type,
                ),
                "expected_contribution": self._estimate_expert_contribution(
                    expert,
                    task,
                ),
            }
            for expert in recommended_experts
        ]

        # 创建协作聊天室
        chat_room_name = f"analysis_{task.task_id}"
        chat_room_id = self.multi_role_chat.create_chat_room(
            room_name=chat_room_name,
            topic=f"文档分析: {task.document_name}",
            initial_participants=task.assigned_experts,
        )

        # 专家已在创建聊天室时添加

        # 记录协作历史
        task.collaboration_history.append(
            {
                "phase": "expert_assignment",
                "timestamp": datetime.now().isoformat(),
                "action": "experts_assigned",
                "details": {
                    "expert_count": len(task.assigned_experts),
                    "chat_room_created": chat_room_id,
                },
            },
        )

        self._save_task(task)

    def _extract_required_skills(
        self,
        task: AnalysisTask,
        custom_requirements: list[str] = None,
    ) -> list[str]:
        """提取所需技能"""
        skills = []

        # 基于分析类型的基础技能
        type_skills = {
            AnalysisType.FINANCIAL_REPORT: ["财务分析", "会计", "投资分析", "风险评估"],
            AnalysisType.LEGAL_DOCUMENT: ["法律分析", "合同审查", "法规解读", "风险识别"],
            AnalysisType.RESEARCH_PAPER: ["学术研究", "数据分析", "文献综述", "方法论"],
            AnalysisType.TECHNICAL_SPEC: ["技术分析", "系统设计", "标准规范", "质量评估"],
            AnalysisType.BUSINESS_PLAN: ["商业分析", "市场研究", "战略规划", "财务建模"],
            AnalysisType.POLICY_DOCUMENT: ["政策分析", "公共管理", "影响评估", "实施规划"],
            AnalysisType.GENERAL_ANALYSIS: ["综合分析", "批判性思维", "信息整合", "报告撰写"],
        }

        skills.extend(type_skills.get(task.analysis_type, []))

        # 添加自定义需求
        if custom_requirements:
            skills.extend(custom_requirements)

        # 基于文档内容的技能推断
        content_keywords = task.document_content.lower()
        if "数据" in content_keywords or "统计" in content_keywords:
            skills.append("数据分析")
        if "技术" in content_keywords or "系统" in content_keywords:
            skills.append("技术分析")
        if "市场" in content_keywords or "营销" in content_keywords:
            skills.append("市场分析")

        return list(set(skills))  # 去重

    def _get_domain_from_analysis_type(self, analysis_type: AnalysisType) -> str:
        """从分析类型获取领域"""
        domain_mapping = {
            AnalysisType.FINANCIAL_REPORT: "金融",
            AnalysisType.LEGAL_DOCUMENT: "法律",
            AnalysisType.RESEARCH_PAPER: "学术研究",
            AnalysisType.TECHNICAL_SPEC: "技术",
            AnalysisType.BUSINESS_PLAN: "商业",
            AnalysisType.POLICY_DOCUMENT: "政策",
            AnalysisType.GENERAL_ANALYSIS: "综合",
        }
        return domain_mapping.get(analysis_type, "综合")

    def _determine_expert_role(
        self,
        expert: dict[str, Any],
        analysis_type: AnalysisType,
    ) -> str:
        """确定专家在分析中的角色"""
        specialties = expert.get("specialties", [])

        # 基于专长确定角色
        if "财务" in str(specialties) and analysis_type == AnalysisType.FINANCIAL_REPORT:
            return "主要分析师"
        elif "法律" in str(specialties) and analysis_type == AnalysisType.LEGAL_DOCUMENT:
            return "法律顾问"
        elif "数据" in str(specialties):
            return "数据分析师"
        elif "技术" in str(specialties):
            return "技术专家"
        elif "市场" in str(specialties):
            return "市场分析师"
        else:
            return "协作分析师"

    def _estimate_expert_contribution(
        self,
        expert: dict[str, Any],
        task: AnalysisTask,
    ) -> str:
        """估算专家贡献"""
        relevance_score = self.recommendation_engine.calculate_relevance_score(
            expert,
            task.analysis_type.value,
        )

        if relevance_score >= 0.8:
            return "核心贡献"
        elif relevance_score >= 0.6:
            return "重要贡献"
        elif relevance_score >= 0.4:
            return "支持贡献"
        else:
            return "辅助贡献"

    def _save_task(self, task: AnalysisTask):
        """保存任务到文件"""
        task_path = os.path.join(self.tasks_dir, f"{task.task_id}.json")

        task_data = asdict(task)
        # 转换枚举为字符串
        task_data["analysis_type"] = task.analysis_type.value
        task_data["current_phase"] = task.current_phase.value

        try:
            with open(task_path, "w", encoding="utf-8") as f:
                json.dump(task_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save task: {e}")

    def get_task_status(self, task_id: str) -> dict[str, Any]:
        """获取任务状态"""
        if task_id not in self.active_tasks:
            return {"status": "not_found"}

        task = self.active_tasks[task_id]

        return {
            "task_id": task_id,
            "document_name": task.document_name,
            "analysis_type": task.analysis_type.value,
            "current_phase": task.current_phase.value,
            "assigned_experts": len(task.assigned_experts),
            "created_at": task.created_at,
            "estimated_completion": task.estimated_completion,
            "actual_completion": task.actual_completion,
            "progress_percentage": self._calculate_progress_percentage(task),
            "quality_metrics": task.quality_metrics,
            "collaboration_history": task.collaboration_history[-5:],  # 最近5个事件
        }

    def _calculate_progress_percentage(self, task: AnalysisTask) -> float:
        """计算进度百分比"""
        phase_weights = {
            AnalysisPhase.INITIALIZATION: 5,
            AnalysisPhase.DOCUMENT_PARSING: 15,
            AnalysisPhase.EXPERT_ASSIGNMENT: 25,
            AnalysisPhase.PARALLEL_ANALYSIS: 45,
            AnalysisPhase.CROSS_VALIDATION: 60,
            AnalysisPhase.CONSENSUS_BUILDING: 75,
            AnalysisPhase.FINAL_SYNTHESIS: 90,
            AnalysisPhase.QUALITY_REVIEW: 95,
            AnalysisPhase.COMPLETED: 100,
        }

        return phase_weights.get(task.current_phase, 0)

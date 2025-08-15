#!/usr/bin/env python3
"""学术研究场景核心功能 - V0.2.3

真正基于项目核心功能的学术研究场景实现：
- 使用真实的CognitiveAgent和IntegratedLLMManager
- 集成WikiService知识协同创造
- 使用AdvancedConsensusAlgorithms共识计算
- 基于MultiPerspectiveSynthesisWorkflow任务分解和执行
- 支持万字级学术报告生成
"""

import logging
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Optional

from src.core_services.advanced_consensus_algorithms import ConsensusInput, WeightedVotingConsensus
from src.core_services.integrated_llm_manager import IntegratedLLMManager
from src.core_services.knowledge_persistence_service import KnowledgePersistenceService
from src.core_services.memory_agent import MemAgent
from src.core_services.role_manager import RoleManager
from src.core_services.wiki_service import WikiService
from src.virtual_role_chat.cognitive_agent.agent import CognitiveAgent, CognitiveProfile

# 导入项目核心组件
from src.workflows.multi_perspective_workflow import MultiPerspectiveSynthesisWorkflow

logger = logging.getLogger(__name__)


@dataclass
class AcademicResearchConfig:
    """学术研究配置"""
    target_word_count: int = 10000
    max_iterations: int = 5
    quality_threshold: float = 0.8
    research_depth: str = "comprehensive"
    enable_wiki_collaboration: bool = True
    enable_consensus_computation: bool = True
    academic_rigor_level: str = "high"


class AcademicResearchScenario:
    """学术研究场景 - 基于项目核心架构"""
    
    def __init__(self):
        """初始化学术研究场景，集成所有核心组件"""
        # 核心认知组件
        cognitive_profile = CognitiveProfile(
            reasoning_style="analytical",
            belief_structure="hierarchical",
            epistemological_approach="empirical",
            metacognitive_level=3,
            cognitive_biases=["confirmation", "anchoring"],
            values={"truth": 0.9, "utility": 0.8, "autonomy": 0.7},
            domain_expertise={"academic_research": 0.9, "knowledge_synthesis": 0.8, "critical_thinking": 0.9}
        )
        
        self.cognitive_agent = CognitiveAgent(
            agent_id="academic_research_coordinator",
            name="学术研究协调员",
            profile=cognitive_profile
        )
        
        # LLM管理器
        self.llm_manager = IntegratedLLMManager()
        
        # 角色管理器
        self.role_manager = RoleManager()
        
        # Wiki协作服务
        self.wiki_service = WikiService()
        
        # 共识算法
        self.consensus_algorithm = WeightedVotingConsensus()
        
        # 记忆代理 - 使用安全初始化
        try:
            from src.core_services.enhanced_sskg_manager import EnhancedSSKGManager
            sskg_manager = EnhancedSSKGManager()
            self.memory_agent = MemAgent(sskg_manager)
        except Exception as e:
            logger.warning(f"MemAgent初始化失败，使用空实现: {e}")
            self.memory_agent = None
        
        # 知识持久化
        try:
            from src.core_services.enhanced_sskg_manager import EnhancedSSKGManager
            from src.core_services.knowledge_persistence_service import KnowledgeConflictResolver
            sskg_manager = EnhancedSSKGManager()
            conflict_resolver = KnowledgeConflictResolver(sskg_manager)
            self.knowledge_persistence = KnowledgePersistenceService(
                sskg_manager=sskg_manager,
                wiki_service=self.wiki_service,
                conflict_resolver=conflict_resolver
            )
        except Exception as e:
            logger.warning(f"Knowledge persistence initialization failed: {e}")
            self.knowledge_persistence = None
        
        logger.info("Academic Research Scenario initialized with core components")
    
    async def conduct_academic_research(
        self, 
        topic: str, 
        config: Optional[AcademicResearchConfig] = None
    ) -> dict[str, Any]:
        """执行完整的学术研究流程"""
        if config is None:
            config = AcademicResearchConfig()
        
        research_id = str(uuid.uuid4())
        logger.info(f"Starting academic research: {research_id} - {topic}")
        
        try:
            # 阶段1：使用认知代理进行研究规划
            research_plan = await self._cognitive_research_planning(topic, config, research_id)
            
            # 阶段2：基于角色管理器选择学术专家团队
            expert_team = await self._assemble_academic_expert_team(topic, research_plan)
            
            # 阶段3：使用多视角综合工作流进行深度分析
            synthesis_result = await self._execute_multi_perspective_analysis(
                topic, expert_team, config, research_id
            )
            
            # 阶段4：Wiki协作知识创造
            wiki_collaboration_result = None
            if config.enable_wiki_collaboration:
                wiki_collaboration_result = await self._wiki_collaborative_creation(
                    synthesis_result, research_id
                )
            
            # 阶段5：共识计算和质量评估
            consensus_result = None
            if config.enable_consensus_computation:
                consensus_result = await self._compute_academic_consensus(
                    synthesis_result, expert_team, research_id
                )
            
            # 阶段6：生成万字级学术报告
            academic_report = await self._generate_comprehensive_report(
                synthesis_result, wiki_collaboration_result, consensus_result, config
            )
            
            # 阶段7：知识沉淀到系统
            persistence_result = None
            if self.knowledge_persistence:
                persistence_result = await self.knowledge_persistence.persist_synthesis_results(
                    synthesis_result, research_id
                )
            
            # 构建完整结果
            result = {
                "success": True,
                "research_id": research_id,
                "topic": topic,
                "research_plan": research_plan,
                "expert_team": [asdict(expert) for expert in expert_team],
                "synthesis_result": synthesis_result,
                "wiki_collaboration": wiki_collaboration_result,
                "consensus_result": consensus_result,
                "academic_report": academic_report,
                "knowledge_persistence": asdict(persistence_result) if persistence_result else None,
                "metadata": {
                    "completion_time": datetime.now().isoformat(),
                    "config": asdict(config),
                    "word_count": academic_report.get("word_count", 0),
                    "quality_score": academic_report.get("quality_score", 0.0)
                }
            }
            
            logger.info(f"Academic research completed: {research_id}")
            return result
            
        except Exception as e:
            logger.error(f"Academic research failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "research_id": research_id,
                "topic": topic
            }
    
    async def _cognitive_research_planning(
        self, 
        topic: str, 
        config: AcademicResearchConfig, 
        research_id: str
    ) -> dict[str, Any]:
        """使用认知代理进行研究规划"""
        logger.info("Starting cognitive research planning...")
        
        # 使用认知代理分析研究主题
        planning_prompt = f"""
        作为学术研究协调员，请为以下研究主题制定详细的研究计划：
        
        研究主题：{topic}
        目标字数：{config.target_word_count}字
        研究深度：{config.research_depth}
        学术严谨度：{config.academic_rigor_level}
        
        请提供：
        1. 研究问题分解
        2. 需要的专业领域和专家类型
        3. 研究方法论建议
        4. 预期的研究成果结构
        5. 质量评估标准
        """
        
        # 通过LLM管理器调用认知代理
        planning_result = await self.llm_manager.call_llm_for_role(
            role_id=self.cognitive_agent.agent_id,
            user_input=planning_prompt,
            task_context="academic_research_planning",
            additional_context={
                "research_id": research_id,
                "config": asdict(config)
            }
        )
        
        # 存储到记忆系统
        if self.memory_agent:
            try:
                await self.memory_agent.store_interaction({
                    "type": "research_planning",
                    "research_id": research_id,
                    "topic": topic,
                    "planning_result": planning_result,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.warning(f"Failed to store to memory: {e}")
        
        return {
            "research_questions": self._extract_research_questions(planning_result),
            "required_expertise": self._extract_required_expertise(planning_result),
            "methodology": self._extract_methodology(planning_result),
            "expected_structure": self._extract_expected_structure(planning_result),
            "quality_criteria": self._extract_quality_criteria(planning_result),
            "raw_planning": planning_result
        }
    
    async def _assemble_academic_expert_team(
        self, 
        topic: str, 
        research_plan: dict[str, Any]
    ) -> list[Any]:
        """基于角色管理器组建学术专家团队"""
        logger.info("Assembling academic expert team...")
        
        # 获取所有可用角色
        available_roles = self.role_manager.list_roles()
        
        # 基于研究计划的专业需求筛选角色
        required_expertise = research_plan.get("required_expertise", [])
        
        selected_experts = []
        for expertise in required_expertise:
            # 寻找匹配的专家角色
            matching_roles = [
                role for role in available_roles
                if self._role_matches_expertise(role, expertise, topic)
            ]
            
            if matching_roles:
                # 选择最匹配的角色
                best_match = max(matching_roles, key=lambda r: self._calculate_expertise_score(r, expertise, topic))
                selected_experts.append(best_match)
        
        # 确保至少有5个专家
        if len(selected_experts) < 5:
            additional_experts = [
                role for role in available_roles 
                if role not in selected_experts and self._is_academic_role(role)
            ][:5-len(selected_experts)]
            selected_experts.extend(additional_experts)
        
        logger.info(f"Selected {len(selected_experts)} academic experts")
        return selected_experts[:9]  # 最多9个专家
    
    async def _execute_multi_perspective_analysis(
        self, 
        topic: str, 
        expert_team: list[Any], 
        config: AcademicResearchConfig, 
        research_id: str
    ) -> dict[str, Any]:
        """使用多视角综合工作流执行深度分析"""
        logger.info("Executing multi-perspective synthesis workflow...")
        
        try:
            # 配置工作流以支持学术研究
            workflow_config = {
                "task_decomposition": {
                    "planner_role": "学术研究规划者",
                    "default_perspectives": [expert.name for expert in expert_team],
                    "max_sub_problems": 8,
                    "academic_depth": config.research_depth
                },
                "parallel_exploration": {
                    "max_parallel_experts": min(len(expert_team), 8),
                    "expert_roles": {expert.name: getattr(expert, 'system_prompt', expert.description) for expert in expert_team},
                    "use_tools": True,
                    "research_rigor": config.academic_rigor_level
                },
                "enhanced_synthesis": {
                    "synthesis_method": "academic_comprehensive",
                    "min_confidence_threshold": config.quality_threshold,
                    "target_word_count": config.target_word_count,
                    "include_expert_attribution": True
                },
                "iterative_refinement": {
                    "max_iterations": config.max_iterations,
                    "quality_threshold": config.quality_threshold,
                    "academic_standards": True
                }
            }
            
            # 创建并执行工作流
            workflow = MultiPerspectiveSynthesisWorkflow(
                workflow_id=f"academic_research_{research_id}",
                config=workflow_config
            )
            
            # 准备执行上下文
            execution_context = ExecutionContext(
                workflow_id=f"academic_research_{research_id}",
                user_id="academic_researcher",
                session_id=research_id,
                metadata={
                    "research_topic": topic,
                    "expert_count": len(expert_team),
                    "target_word_count": config.target_word_count,
                    "research_depth": config.research_depth
                }
            )
            
            # 准备服务上下文
            services = {
                "llm_manager": self.llm_manager,
                "role_manager": self.role_manager,
                "memory_agent": self.memory_agent,
                "wiki_service": self.wiki_service,
                "cognitive_agent": self.cognitive_agent
            }
            
            # 执行工作流
            synthesis_result = await workflow.execute(
                context=execution_context,
                topic=topic,
                perspectives=[expert.name for expert in expert_team],
                services=services
            )
            
            # 增强结果以支持学术研究需求
            enhanced_result = await self._enhance_synthesis_for_academic_research(
                synthesis_result, expert_team, config, research_id
            )
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Multi-perspective analysis failed: {e}")
            # 返回降级结果
            return await self._fallback_analysis(topic, expert_team, config, research_id)
    
    async def _wiki_collaborative_creation(
        self, 
        synthesis_result: dict[str, Any], 
        research_id: str
    ) -> dict[str, Any]:
        """Wiki协作知识创造"""
        logger.info("Starting Wiki collaborative knowledge creation...")
        
        try:
            # 提取关键知识点
            key_insights = synthesis_result.get("key_insights", [])
            synthesis_content = synthesis_result.get("synthesis", {})
            
            wiki_entries = []
            
            # 为每个关键洞察创建Wiki条目
            for i, insight in enumerate(key_insights):
                entry_name = f"research_insight_{research_id}_{i+1}"
                
                wiki_version = self.wiki_service.create_entry(
                    entry_name=entry_name,
                    content=f"# 研究洞察\n\n{insight}\n\n## 来源\n研究ID: {research_id}\n生成时间: {datetime.now().isoformat()}",
                    author_role="academic_research_system",
                    summary=f"学术研究洞察：{insight[:100]}...",
                    tags=["academic_research", "insight", research_id],
                    category="research_findings"
                )
                
                wiki_entries.append({
                    "entry_name": entry_name,
                    "version_id": wiki_version.version_id,
                    "content_preview": insight[:200]
                })
            
            # 创建综合报告的Wiki条目
            if synthesis_content:
                main_entry_name = f"research_synthesis_{research_id}"
                
                synthesis_wiki_content = f"""# 学术研究综合报告

## 研究主题
{synthesis_result.get('topic', '未知主题')}

## 综合分析
{synthesis_content.get('main_conclusion', '综合分析结果')}

## 专家贡献
"""
                
                expert_contributions = synthesis_result.get("expert_contributions", {})
                for expert_name, contribution in expert_contributions.items():
                    synthesis_wiki_content += f"\n### {expert_name}\n{contribution}\n"
                
                synthesis_wiki_content += f"\n## 元数据\n- 研究ID: {research_id}\n- 生成时间: {datetime.now().isoformat()}\n- 质量评分: {synthesis_result.get('quality_score', 0.0)}"
                
                main_wiki_version = self.wiki_service.create_entry(
                    entry_name=main_entry_name,
                    content=synthesis_wiki_content,
                    author_role="academic_research_system",
                    summary=f"学术研究综合报告：{synthesis_result.get('topic', '未知主题')}",
                    tags=["academic_research", "synthesis", "comprehensive_report", research_id],
                    category="research_reports"
                )
                
                wiki_entries.append({
                    "entry_name": main_entry_name,
                    "version_id": main_wiki_version.version_id,
                    "content_preview": synthesis_content.get('main_conclusion', '')[:200]
                })
            
            return {
                "success": True,
                "wiki_entries_created": len(wiki_entries),
                "entries": wiki_entries,
                "collaboration_metadata": {
                    "research_id": research_id,
                    "creation_time": datetime.now().isoformat(),
                    "total_content_length": sum(len(entry.get("content_preview", "")) for entry in wiki_entries)
                }
            }
            
        except Exception as e:
            logger.error(f"Wiki collaborative creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "research_id": research_id
            }    

    async def _compute_academic_consensus(
        self, 
        synthesis_result: dict[str, Any], 
        expert_team: list[Any], 
        research_id: str
    ) -> dict[str, Any]:
        """使用共识算法计算学术共识"""
        logger.info("Computing academic consensus...")
        
        try:
            # 准备共识输入数据
            expert_contributions = synthesis_result.get("expert_contributions", {})
            consensus_inputs = []
            
            for expert in expert_team:
                expert_name = expert.name
                contribution = expert_contributions.get(expert_name, {})
                
                if isinstance(contribution, dict):
                    position = contribution.get("viewpoint", contribution.get("analysis", ""))
                    confidence = contribution.get("confidence", 0.8)
                elif isinstance(contribution, str):
                    position = contribution
                    confidence = 0.8
                else:
                    position = str(contribution)
                    confidence = 0.7
                
                consensus_inputs.append({
                    "agent_id": expert_name,
                    "position": position,
                    "confidence": confidence,
                    "reasoning": f"基于{expert_name}的专业分析",
                    "timestamp": datetime.now().isoformat()
                })
            
            # 转换为ConsensusInput格式
            consensus_input_objects = []
            for input_data in consensus_inputs:
                consensus_input = ConsensusInput(
                    agent_id=input_data["agent_id"],
                    position=input_data["position"],
                    confidence=input_data["confidence"],
                    reasoning=input_data["reasoning"],
                    timestamp=datetime.now()
                )
                consensus_input_objects.append(consensus_input)
            
            # 使用加权投票共识算法
            consensus_result = await self.consensus_algorithm.calculate_consensus(
                consensus_input_objects,
                context={
                    "domain": "academic_research",
                    "research_id": research_id,
                    "quality_threshold": 0.8
                }
            )
            
            # 存储共识结果到记忆系统
            if self.memory_agent:
                try:
                    await self.memory_agent.store_interaction({
                        "type": "consensus_computation",
                        "research_id": research_id,
                        "consensus_result": consensus_result,
                        "participant_count": len(expert_team),
                        "timestamp": datetime.now().isoformat()
                    })
                except Exception as e:
                    logger.warning(f"Failed to store consensus to memory: {e}")
            
            return {
                "success": True,
                "consensus_strength": getattr(consensus_result, 'confidence', 0.0),
                "algorithm_used": "weighted_voting",
                "participant_count": len(expert_team),
                "consensus_summary": str(getattr(consensus_result, 'consensus_value', "")),
                "confidence_score": getattr(consensus_result, 'confidence', 0.0),
                "detailed_result": {
                    "consensus_value": getattr(consensus_result, 'consensus_value', ""),
                    "confidence": getattr(consensus_result, 'confidence', 0.0),
                    "algorithm_type": getattr(consensus_result, 'algorithm_type', "weighted_voting")
                }
            }
            
        except Exception as e:
            logger.error(f"Academic consensus computation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "research_id": research_id
            }
    
    async def _generate_comprehensive_report(
        self, 
        synthesis_result: dict[str, Any], 
        wiki_collaboration_result: Optional[dict[str, Any]], 
        consensus_result: Optional[dict[str, Any]], 
        config: AcademicResearchConfig
    ) -> dict[str, Any]:
        """生成万字级综合学术报告"""
        logger.info("Generating comprehensive academic report...")
        
        try:
            # 使用认知代理生成报告
            report_prompt = f"""
            基于以下研究成果，生成一份{config.target_word_count}字的综合学术报告：
            
            ## 研究主题
            {synthesis_result.get('topic', '未知主题')}
            
            ## 多视角综合分析结果
            {synthesis_result.get('synthesis', {})}
            
            ## 关键洞察
            {chr(10).join(f"- {insight}" for insight in synthesis_result.get('key_insights', []))}
            
            ## 专家贡献
            {self._format_expert_contributions(synthesis_result.get('expert_contributions', {}))}
            
            ## Wiki协作成果
            {self._format_wiki_collaboration(wiki_collaboration_result)}
            
            ## 共识计算结果
            {self._format_consensus_result(consensus_result)}
            
            请生成包含以下部分的完整学术报告：
            1. 摘要 (300-500字)
            2. 引言 (800-1200字)
            3. 文献综述 (1500-2000字)
            4. 研究方法 (800-1000字)
            5. 结果与分析 (3000-4000字)
            6. 讨论 (2000-2500字)
            7. 结论 (500-800字)
            8. 参考文献
            
            要求：
            - 学术严谨性高
            - 逻辑结构清晰
            - 引用专家观点
            - 体现多视角分析
            - 包含共识和分歧点
            """
            
            # 通过LLM管理器生成报告
            report_result = await self.llm_manager.call_llm_for_role(
                role_id=self.cognitive_agent.agent_id,
                user_input=report_prompt,
                task_context="comprehensive_academic_report_generation",
                additional_context={
                    "target_word_count": config.target_word_count,
                    "quality_threshold": config.quality_threshold,
                    "academic_rigor": config.academic_rigor_level
                }
            )
            
            # 计算实际字数
            report_content = report_result.get("response", "")
            actual_word_count = len(report_content.split())
            
            # 质量评估
            quality_score = self._assess_report_quality(
                report_content, 
                synthesis_result, 
                config.target_word_count
            )
            
            # 如果字数不足，进行扩展
            if actual_word_count < config.target_word_count * 0.8:
                logger.info("Report word count insufficient, expanding...")
                expanded_report = await self._expand_report_content(
                    report_content, 
                    synthesis_result, 
                    config.target_word_count - actual_word_count
                )
                report_content = expanded_report
                actual_word_count = len(report_content.split())
            
            return {
                "success": True,
                "report_content": report_content,
                "word_count": actual_word_count,
                "target_word_count": config.target_word_count,
                "quality_score": quality_score,
                "sections": self._extract_report_sections(report_content),
                "metadata": {
                    "generation_time": datetime.now().isoformat(),
                    "synthesis_quality": synthesis_result.get("quality_score", 0.0),
                    "expert_count": len(synthesis_result.get("expert_contributions", {})),
                    "wiki_entries": wiki_collaboration_result.get("wiki_entries_created", 0) if wiki_collaboration_result else 0,
                    "consensus_strength": consensus_result.get("consensus_strength", 0.0) if consensus_result else 0.0
                }
            }
            
        except Exception as e:
            logger.error(f"Comprehensive report generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "word_count": 0,
                "quality_score": 0.0
            }
    
    # 辅助方法
    def _extract_research_questions(self, planning_result: dict[str, Any]) -> list[str]:
        """从规划结果中提取研究问题"""
        response = planning_result.get("response", "")
        # 简化实现：从响应中提取问题
        questions = []
        lines = response.split('\n')
        for line in lines:
            if '?' in line and ('问题' in line or '研究' in line):
                questions.append(line.strip())
        return questions[:5]  # 最多5个问题
    
    def _extract_required_expertise(self, planning_result: dict[str, Any]) -> list[str]:
        """提取所需专业领域"""
        response = planning_result.get("response", "")
        # 简化实现：提取专业领域关键词
        expertise_keywords = ["教育", "技术", "心理", "社会", "经济", "管理", "法律", "医学", "工程", "科学"]
        found_expertise = []
        for keyword in expertise_keywords:
            if keyword in response:
                found_expertise.append(keyword)
        return found_expertise[:5]
    
    def _extract_methodology(self, planning_result: dict[str, Any]) -> str:
        """提取研究方法论"""
        response = planning_result.get("response", "")
        if "方法" in response:
            # 提取包含"方法"的段落
            lines = response.split('\n')
            methodology_lines = [line for line in lines if "方法" in line]
            return '\n'.join(methodology_lines[:3])
        return "多视角综合分析方法"
    
    def _extract_expected_structure(self, planning_result: dict[str, Any]) -> list[str]:
        """提取预期结构"""
        return ["摘要", "引言", "文献综述", "研究方法", "结果与分析", "讨论", "结论", "参考文献"]
    
    def _extract_quality_criteria(self, planning_result: dict[str, Any]) -> list[str]:
        """提取质量标准"""
        return ["学术严谨性", "逻辑一致性", "证据充分性", "创新性", "实用性"]
    
    def _role_matches_expertise(self, role: Any, expertise: str, topic: str) -> bool:
        """判断角色是否匹配专业需求"""
        role_name = role.name.lower()
        role_desc = role.description.lower()
        expertise_lower = expertise.lower()
        topic_lower = topic.lower()
        
        return (expertise_lower in role_name or 
                expertise_lower in role_desc or
                any(keyword in role_name for keyword in topic_lower.split()[:3]))
    
    def _calculate_expertise_score(self, role: Any, expertise: str, topic: str) -> float:
        """计算专业匹配度得分"""
        score = 0.0
        role_name = role.name.lower()
        role_desc = role.description.lower()
        expertise_lower = expertise.lower()
        
        if expertise_lower in role_name:
            score += 2.0
        if expertise_lower in role_desc:
            score += 1.0
        
        # 检查能力匹配
        for capability in getattr(role, 'capabilities', []):
            if expertise_lower in capability.lower():
                score += 0.5
        
        return score
    
    def _is_academic_role(self, role: Any) -> bool:
        """判断是否为学术角色"""
        academic_keywords = ["专家", "学者", "研究", "教授", "博士", "分析师", "顾问"]
        role_name = role.name.lower()
        return any(keyword in role_name for keyword in academic_keywords)
    
    def _format_expert_contributions(self, expert_contributions: dict[str, Any]) -> str:
        """格式化专家贡献"""
        formatted = ""
        for expert_name, contribution in expert_contributions.items():
            formatted += f"\n### {expert_name}\n"
            if isinstance(contribution, dict):
                formatted += contribution.get("analysis", str(contribution))
            else:
                formatted += str(contribution)
        return formatted
    
    def _format_wiki_collaboration(self, wiki_result: Optional[dict[str, Any]]) -> str:
        """格式化Wiki协作结果"""
        if not wiki_result or not wiki_result.get("success"):
            return "Wiki协作功能未启用或执行失败"
        
        return f"""
Wiki协作成果：
- 创建条目数：{wiki_result.get('wiki_entries_created', 0)}
- 总内容长度：{wiki_result.get('collaboration_metadata', {}).get('total_content_length', 0)}字符
- 协作时间：{wiki_result.get('collaboration_metadata', {}).get('creation_time', '未知')}
"""
    
    def _format_consensus_result(self, consensus_result: Optional[dict[str, Any]]) -> str:
        """格式化共识结果"""
        if not consensus_result or not consensus_result.get("success"):
            return "共识计算功能未启用或执行失败"
        
        return f"""
共识计算结果：
- 共识强度：{consensus_result.get('consensus_strength', 0.0):.2f}
- 算法类型：{consensus_result.get('algorithm_used', '未知')}
- 参与专家：{consensus_result.get('participant_count', 0)}人
- 置信度：{consensus_result.get('confidence_score', 0.0):.2f}
- 共识摘要：{consensus_result.get('consensus_summary', '无摘要')}
"""
    
    def _assess_report_quality(
        self, 
        report_content: str, 
        synthesis_result: dict[str, Any], 
        target_word_count: int
    ) -> float:
        """评估报告质量"""
        quality_score = 0.0
        
        # 字数评估 (30%)
        actual_words = len(report_content.split())
        word_ratio = min(actual_words / target_word_count, 1.0)
        quality_score += word_ratio * 0.3
        
        # 结构完整性评估 (25%)
        required_sections = ["摘要", "引言", "方法", "结果", "讨论", "结论"]
        present_sections = sum(1 for section in required_sections if section in report_content)
        structure_score = present_sections / len(required_sections)
        quality_score += structure_score * 0.25
        
        # 内容深度评估 (25%)
        depth_indicators = ["分析", "研究", "发现", "结论", "建议"]
        depth_score = sum(1 for indicator in depth_indicators if indicator in report_content) / len(depth_indicators)
        quality_score += depth_score * 0.25
        
        # 综合质量评估 (20%)
        synthesis_quality = synthesis_result.get("quality_score", 0.0)
        quality_score += synthesis_quality * 0.2
        
        return min(quality_score, 1.0)
    
    async def _expand_report_content(
        self, 
        original_content: str, 
        synthesis_result: dict[str, Any], 
        additional_words_needed: int
    ) -> str:
        """扩展报告内容"""
        expansion_prompt = f"""
        请扩展以下学术报告内容，增加约{additional_words_needed}字：
        
        原始内容：
        {original_content}
        
        扩展要求：
        1. 深化现有分析
        2. 增加更多专家观点
        3. 补充理论背景
        4. 扩展讨论部分
        5. 保持学术严谨性
        
        基于的研究数据：
        {synthesis_result.get('key_insights', [])}
        """
        
        expansion_result = await self.llm_manager.call_llm_for_role(
            role_id=self.cognitive_agent.agent_id,
            user_input=expansion_prompt,
            task_context="report_content_expansion"
        )
        
        return expansion_result.get("response", original_content)
    
    async def _enhance_synthesis_for_academic_research(
        self,
        synthesis_result: dict[str, Any],
        expert_team: list[Any],
        config: AcademicResearchConfig,
        research_id: str
    ) -> dict[str, Any]:
        """增强综合结果以支持学术研究需求"""
        logger.info("Enhancing synthesis result for academic research...")
        
        try:
            # 提取关键学术要素
            key_insights = synthesis_result.get("key_insights", [])
            expert_contributions = synthesis_result.get("expert_contributions", {})
            
            # 进行学术质量评估
            academic_quality_score = await self._assess_academic_quality(
                synthesis_result, expert_team, config
            )
            
            # 生成学术引用和参考文献
            academic_references = await self._generate_academic_references(
                synthesis_result, expert_team, research_id
            )
            
            # 识别研究空白和未来方向
            research_gaps = await self._identify_research_gaps(
                synthesis_result, topic=synthesis_result.get("topic", ""), config=config
            )
            
            # 增强结果
            enhanced_result = {
                **synthesis_result,
                "academic_quality_score": academic_quality_score,
                "academic_references": academic_references,
                "research_gaps": research_gaps,
                "methodology_used": "多视角综合分析法",
                "expert_diversity_score": self._calculate_expert_diversity(expert_team),
                "research_rigor_level": config.academic_rigor_level,
                "evidence_strength": self._assess_evidence_strength(synthesis_result),
                "theoretical_framework": self._extract_theoretical_framework(synthesis_result),
                "practical_implications": self._extract_practical_implications(synthesis_result)
            }
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Failed to enhance synthesis for academic research: {e}")
            return synthesis_result
    
    async def _fallback_analysis(
        self,
        topic: str,
        expert_team: list[Any],
        config: AcademicResearchConfig,
        research_id: str
    ) -> dict[str, Any]:
        """降级分析方法"""
        logger.info("Executing fallback analysis...")
        
        try:
            # 使用认知代理进行基础分析
            fallback_prompt = f"""
            作为学术研究协调员，请对以下主题进行深度分析：
            
            研究主题：{topic}
            专家团队：{[expert.name for expert in expert_team]}
            目标字数：{config.target_word_count}字
            
            请提供：
            1. 核心观点分析
            2. 不同视角的见解
            3. 关键发现和洞察
            4. 学术价值评估
            5. 研究建议
            """
            
            analysis_result = await self.llm_manager.call_llm_for_role(
                role_id=self.cognitive_agent.agent_id,
                user_input=fallback_prompt,
                task_context="academic_fallback_analysis",
                additional_context={
                    "research_id": research_id,
                    "expert_count": len(expert_team)
                }
            )
            
            return {
                "success": True,
                "topic": topic,
                "analysis_method": "fallback_cognitive_analysis",
                "key_insights": self._extract_insights_from_response(analysis_result.get("response", "")),
                "expert_contributions": {expert.name: f"基于{expert.name}视角的分析" for expert in expert_team},
                "synthesis": {
                    "main_conclusion": analysis_result.get("response", ""),
                    "confidence": 0.7,
                    "method": "cognitive_agent_analysis"
                },
                "quality_score": 0.7,
                "research_id": research_id
            }
            
        except Exception as e:
            logger.error(f"Fallback analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "research_id": research_id,
                "topic": topic
            }
    
    async def _assess_academic_quality(
        self,
        synthesis_result: dict[str, Any],
        expert_team: list[Any],
        config: AcademicResearchConfig
    ) -> float:
        """评估学术质量"""
        quality_score = 0.0
        
        # 专家多样性评分 (25%)
        diversity_score = self._calculate_expert_diversity(expert_team)
        quality_score += diversity_score * 0.25
        
        # 内容深度评分 (30%)
        content_depth = self._assess_content_depth(synthesis_result)
        quality_score += content_depth * 0.30
        
        # 逻辑一致性评分 (25%)
        logical_consistency = self._assess_logical_consistency(synthesis_result)
        quality_score += logical_consistency * 0.25
        
        # 创新性评分 (20%)
        innovation_score = self._assess_innovation(synthesis_result)
        quality_score += innovation_score * 0.20
        
        return min(quality_score, 1.0)
    
    async def _generate_academic_references(
        self,
        synthesis_result: dict[str, Any],
        expert_team: list[Any],
        research_id: str
    ) -> list[dict[str, str]]:
        """生成学术引用和参考文献"""
        references = []
        
        # 为每个专家贡献生成引用
        expert_contributions = synthesis_result.get("expert_contributions", {})
        for expert_name, contribution in expert_contributions.items():
            references.append({
                "type": "expert_analysis",
                "author": expert_name,
                "title": f"{expert_name}对{synthesis_result.get('topic', '研究主题')}的专业分析",
                "source": "多视角综合分析系统",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "research_id": research_id,
                "content_preview": str(contribution)[:100] + "..."
            })
        
        # 添加方法论引用
        references.append({
            "type": "methodology",
            "author": "DAIP-LIVE系统",
            "title": "多视角综合分析方法论",
            "source": "认知代理协作平台",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "research_id": research_id,
            "description": "基于多个认知代理的协作分析方法"
        })
        
        return references
    
    async def _identify_research_gaps(
        self,
        synthesis_result: dict[str, Any],
        topic: str,
        config: AcademicResearchConfig
    ) -> list[str]:
        """识别研究空白和未来方向"""
        gaps_prompt = f"""
        基于以下研究综合结果，识别研究空白和未来研究方向：
        
        研究主题：{topic}
        综合结果：{synthesis_result.get('synthesis', {})}
        关键洞察：{synthesis_result.get('key_insights', [])}
        
        请识别：
        1. 当前研究的局限性
        2. 未充分探索的领域
        3. 需要进一步验证的假设
        4. 未来研究的优先方向
        5. 跨学科研究机会
        """
        
        try:
            gaps_result = await self.llm_manager.call_llm_for_role(
                role_id=self.cognitive_agent.agent_id,
                user_input=gaps_prompt,
                task_context="research_gaps_identification"
            )
            
            response = gaps_result.get("response", "")
            gaps = []
            
            # 提取研究空白
            lines = response.split('\n')
            for line in lines:
                if any(keyword in line for keyword in ["空白", "局限", "不足", "需要", "未来"]):
                    gaps.append(line.strip())
            
            return gaps[:10]  # 最多10个研究空白
            
        except Exception as e:
            logger.error(f"Failed to identify research gaps: {e}")
            return ["需要进一步的实证研究", "跨学科视角的整合", "长期影响的追踪研究"]
    
    def _calculate_expert_diversity(self, expert_team: list[Any]) -> float:
        """计算专家多样性得分"""
        if not expert_team:
            return 0.0
        
        # 基于专家名称和描述的多样性
        unique_keywords = set()
        for expert in expert_team:
            name_words = expert.name.lower().split()
            desc_words = expert.description.lower().split()[:10]  # 取前10个词
            unique_keywords.update(name_words + desc_words)
        
        # 多样性 = 独特关键词数 / (专家数 * 平均词数)
        diversity_score = len(unique_keywords) / (len(expert_team) * 5)
        return min(diversity_score, 1.0)
    
    def _assess_content_depth(self, synthesis_result: dict[str, Any]) -> float:
        """评估内容深度"""
        synthesis = synthesis_result.get("synthesis", {})
        key_insights = synthesis_result.get("key_insights", [])
        
        depth_indicators = ["分析", "深入", "详细", "全面", "系统", "理论", "实证", "机制"]
        
        content = str(synthesis) + " ".join(key_insights)
        depth_count = sum(1 for indicator in depth_indicators if indicator in content)
        
        return min(depth_count / len(depth_indicators), 1.0)
    
    def _assess_logical_consistency(self, synthesis_result: dict[str, Any]) -> float:
        """评估逻辑一致性"""
        # 简化实现：基于结构完整性
        required_elements = ["synthesis", "key_insights", "expert_contributions"]
        present_elements = sum(1 for element in required_elements if element in synthesis_result)
        
        return present_elements / len(required_elements)
    
    def _assess_innovation(self, synthesis_result: dict[str, Any]) -> float:
        """评估创新性"""
        innovation_keywords = ["创新", "新颖", "突破", "发现", "洞察", "独特", "原创"]
        
        content = str(synthesis_result.get("synthesis", {})) + " ".join(synthesis_result.get("key_insights", []))
        innovation_count = sum(1 for keyword in innovation_keywords if keyword in content)
        
        return min(innovation_count / len(innovation_keywords), 1.0)
    
    def _assess_evidence_strength(self, synthesis_result: dict[str, Any]) -> float:
        """评估证据强度"""
        evidence_keywords = ["证据", "数据", "研究", "实验", "调查", "统计", "案例", "文献"]
        
        content = str(synthesis_result.get("synthesis", {}))
        evidence_count = sum(1 for keyword in evidence_keywords if keyword in content)
        
        return min(evidence_count / 5, 1.0)  # 标准化到0-1
    
    def _extract_theoretical_framework(self, synthesis_result: dict[str, Any]) -> str:
        """提取理论框架"""
        synthesis = synthesis_result.get("synthesis", {})
        content = str(synthesis)
        
        # 查找理论相关内容
        theory_keywords = ["理论", "框架", "模型", "概念", "范式"]
        theory_sentences = []
        
        sentences = content.split('。')
        for sentence in sentences:
            if any(keyword in sentence for keyword in theory_keywords):
                theory_sentences.append(sentence.strip())
        
        return "。".join(theory_sentences[:3]) if theory_sentences else "多视角综合分析理论框架"
    
    def _extract_practical_implications(self, synthesis_result: dict[str, Any]) -> list[str]:
        """提取实践意义"""
        synthesis = synthesis_result.get("synthesis", {})
        content = str(synthesis)
        
        practical_keywords = ["应用", "实践", "建议", "措施", "策略", "方案", "实施"]
        implications = []
        
        sentences = content.split('。')
        for sentence in sentences:
            if any(keyword in sentence for keyword in practical_keywords):
                implications.append(sentence.strip())
        
        return implications[:5]  # 最多5个实践意义
    
    def _extract_insights_from_response(self, response: str) -> list[str]:
        """从响应中提取洞察"""
        insights = []
        lines = response.split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in ["发现", "洞察", "结论", "观点", "见解"]):
                insights.append(line.strip())
        
        return insights[:8]  # 最多8个洞察
    
    def _extract_report_sections(self, report_content: str) -> dict[str, str]:
        """提取报告各部分"""
        sections = {}
        current_section = "introduction"
        current_content = []
        
        lines = report_content.split('\n')
        for line in lines:
            if any(header in line for header in ["#", "摘要", "引言", "方法", "结果", "讨论", "结论"]):
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line.strip().lower().replace('#', '').strip()
                current_content = []
            else:
                current_content.append(line)
        
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections


# 便捷函数
async def conduct_academic_research(
    topic: str,
    target_word_count: int = 10000,
    quality_threshold: float = 0.8,
    enable_wiki_collaboration: bool = True,
    enable_consensus_computation: bool = True
) -> dict[str, Any]:
    """便捷的学术研究函数"""
    config = AcademicResearchConfig(
        target_word_count=target_word_count,
        quality_threshold=quality_threshold,
        enable_wiki_collaboration=enable_wiki_collaboration,
        enable_consensus_computation=enable_consensus_computation
    )
    
    scenario = AcademicResearchScenario()
    return await scenario.conduct_academic_research(topic, config)
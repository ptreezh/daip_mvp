# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-06 10:30:00
@Author  : DAIP-LIVE Team
@File    : domain_services.py
@Description:
    Domain services for the Personal Intelligence Hub.
    These services contain business logic that doesn't naturally fit within entities or value objects.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import asyncio
from abc import ABC, abstractmethod

from .entities import User, Session, Task, Message, Debate
from .value_objects import (
    EntranceType, IntentType, ConsensusLevel, UserPreference, 
    TaskPriority, TimeInterval
)
from .aggregates import SessionAggregate, TaskAggregate, DebateAggregate


class EntranceSelectorService:
    """入口选择器服务 - 智能选择最适合的入口类型"""
    
    def __init__(self):
        self.user_preferences = {}
        self.behavior_history = {}
        self.selection_rules = {
            # 基于时间敏感性的规则
            "time_sensitive": {
                "threshold": 0.8,
                "preferred_entrance": EntranceType.SECRETARIAT
            },
            # 基于查询复杂性的规则
            "complex_query": {
                "threshold": 0.7,
                "preferred_entrance": EntranceType.FORUM
            },
            # 基于用户专业水平的规则
            "expert_user": {
                "threshold": 0.6,
                "preferred_entrance": EntranceType.FORUM
            }
        }
    
    async def select_entrance(self, user: User, context: Dict[str, Any]) -> EntranceType:
        """选择最适合的入口类型"""
        # 1. 检查用户明确的偏好
        if user.preferred_entrance:
            return user.preferred_entrance
        
        # 2. 基于上下文进行智能选择
        context_features = await self._extract_context_features(user, context)
        prediction = await self._predict_optimal_entrance(context_features)
        
        # 3. 记录选择历史用于学习
        self._record_selection_history(user.user_id, prediction, context_features)
        
        return prediction
    
    async def _extract_context_features(self, user: User, context: Dict[str, Any]) -> Dict[str, float]:
        """提取上下文特征"""
        features = {}
        
        # 时间敏感性特征
        features["time_sensitivity"] = self._analyze_time_sensitivity(context)
        
        # 查询复杂性特征
        features["query_complexity"] = self._analyze_query_complexity(context)
        
        # 用户专业水平特征
        features["user_expertise"] = self._assess_user_expertise(user, context)
        
        # 历史行为特征
        features["historical_preference"] = self._get_historical_preference(user.user_id)
        
        # 交互历史特征
        features["interaction_pattern"] = self._analyze_interaction_pattern(user.user_id)
        
        return features
    
    def _analyze_time_sensitivity(self, context: Dict[str, Any]) -> float:
        """分析时间敏感性"""
        time_sensitive_keywords = ["紧急", "立即", "马上", "快速", " ASAP", "urgent"]
        query = context.get("query", "").lower()
        
        if any(keyword in query for keyword in time_sensitive_keywords):
            return 0.9
        
        # 检查是否有明确的时间限制
        time_limit = context.get("time_limit")
        if time_limit:
            if time_limit <= 300:  # 5分钟内
                return 0.95
            elif time_limit <= 1800:  # 30分钟内
                return 0.7
        
        return 0.3  # 默认低时间敏感性
    
    def _analyze_query_complexity(self, context: Dict[str, Any]) -> float:
        """分析查询复杂性"""
        query = context.get("query", "")
        
        # 基于查询长度
        length_score = min(len(query) / 500, 1.0)
        
        # 基于复杂度关键词
        complexity_keywords = [
            "分析", "评估", "比较", "综合", "深入", "详细", "全面",
            "analyze", "evaluate", "compare", "comprehensive", "detailed"
        ]
        
        complexity_count = sum(1 for keyword in complexity_keywords if keyword in query)
        complexity_score = min(complexity_count / 3, 1.0)
        
        # 基于问题类型
        question_words = ["为什么", "如何", "怎么样", "what", "why", "how", "explain"]
        has_questions = any(word in query for word in question_words)
        
        # 综合评分
        final_score = (length_score * 0.3 + complexity_score * 0.5 + (0.5 if has_questions else 0.0) * 0.2)
        
        return min(final_score, 1.0)
    
    def _assess_user_expertise(self, user: User, context: Dict[str, Any]) -> float:
        """评估用户专业水平"""
        # 基于用户历史活动
        user_history = self.behavior_history.get(user.user_id, {})
        
        # 如果是新用户，使用默认值
        if not user_history:
            return 0.5
        
        # 基于会话数量
        session_count = len(user_history.get("sessions", []))
        session_score = min(session_count / 10, 1.0)
        
        # 基于任务复杂度
        completed_tasks = user_history.get("completed_tasks", [])
        if completed_tasks:
            avg_complexity = sum(task.get("complexity", 0.5) for task in completed_tasks) / len(completed_tasks)
            complexity_score = avg_complexity
        else:
            complexity_score = 0.5
        
        # 综合评分
        return (session_score * 0.4 + complexity_score * 0.6)
    
    def _get_historical_preference(self, user_id: str) -> float:
        """获取历史偏好"""
        user_history = self.behavior_history.get(user_id, {})
        selections = user_history.get("entrance_selections", [])
        
        if not selections:
            return 0.5
        
        # 计算Forum选择的频率
        forum_selections = sum(1 for s in selections if s.get("entrance") == EntranceType.FORUM)
        forum_preference = forum_selections / len(selections)
        
        return forum_preference
    
    def _analyze_interaction_pattern(self, user_id: str) -> float:
        """分析交互模式"""
        user_history = self.behavior_history.get(user_id, {})
        sessions = user_history.get("sessions", [])
        
        if not sessions:
            return 0.5
        
        # 分析用户在不同入口的停留时间
        forum_sessions = [s for s in sessions if s.get("entrance") == EntranceType.FORUM]
        secretariat_sessions = [s for s in sessions if s.get("entrance") == EntranceType.SECRETARIAT]
        
        if forum_sessions:
            avg_forum_duration = sum(s.get("duration", 0) for s in forum_sessions) / len(forum_sessions)
        else:
            avg_forum_duration = 0
        
        if secretariat_sessions:
            avg_secretariat_duration = sum(s.get("duration", 0) for s in secretariat_sessions) / len(secretariat_sessions)
        else:
            avg_secretariat_duration = 0
        
        # 如果在Forum停留时间更长，偏好Forum
        total_duration = avg_forum_duration + avg_secretariat_duration
        if total_duration > 0:
            forum_preference = avg_forum_duration / total_duration
        else:
            forum_preference = 0.5
        
        return forum_preference
    
    async def _predict_optimal_entrance(self, features: Dict[str, float]) -> EntranceType:
        """预测最优入口类型"""
        # 应用规则引擎
        forum_score = 0.5  # 基础分数
        
        # 时间敏感性规则
        if features["time_sensitivity"] > self.selection_rules["time_sensitive"]["threshold"]:
            forum_score -= 0.3
        
        # 复杂查询规则
        if features["query_complexity"] > self.selection_rules["complex_query"]["threshold"]:
            forum_score += 0.4
        
        # 专家用户规则
        if features["user_expertise"] > self.selection_rules["expert_user"]["threshold"]:
            forum_score += 0.2
        
        # 历史偏好
        forum_score += (features["historical_preference"] - 0.5) * 0.3
        
        # 交互模式
        forum_score += (features["interaction_pattern"] - 0.5) * 0.2
        
        # 最终决策
        return EntranceType.FORUM if forum_score > 0.5 else EntranceType.SECRETARIAT
    
    def _record_selection_history(self, user_id: str, entrance: EntranceType, features: Dict[str, float]):
        """记录选择历史"""
        if user_id not in self.behavior_history:
            self.behavior_history[user_id] = {
                "entrance_selections": [],
                "sessions": [],
                "completed_tasks": []
            }
        
        self.behavior_history[user_id]["entrance_selections"].append({
            "entrance": entrance,
            "features": features,
            "timestamp": datetime.now()
        })
    
    def learn_from_feedback(self, user_id: str, entrance: EntranceType, satisfaction: float):
        """从用户反馈中学习"""
        if user_id in self.behavior_history:
            # 更新最近的选择记录
            recent_selections = self.behavior_history[user_id]["entrance_selections"]
            if recent_selections:
                recent_selections[-1]["satisfaction"] = satisfaction
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """获取用户偏好数据"""
        return self.behavior_history.get(user_id, {})


class WorkflowOrchestratorService:
    """工作流编排器服务 - 协调任务执行流程"""
    
    def __init__(self):
        self.active_workflows = {}
        self.workflow_templates = {
            "analysis": self._create_analysis_workflow,
            "discussion": self._create_discussion_workflow,
            "evaluation": self._create_evaluation_workflow,
            "summarization": self._create_summarization_workflow
        }
    
    async def plan_workflow(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """规划工作流"""
        intent_type = intent.get("type", "analysis")
        content = intent.get("content", "")
        
        # 选择工作流模板
        if intent_type not in self.workflow_templates:
            raise ValueError(f"Unsupported intent type: {intent_type}")
        
        workflow_plan = self.workflow_templates[intent_type](content, intent)
        
        # 估算执行时间
        estimated_duration = self._estimate_duration(workflow_plan)
        
        # 确定所需Agent
        required_agents = self._determine_required_agents(intent)
        
        return {
            "workflow_id": f"workflow_{len(self.active_workflows)}",
            "steps": workflow_plan,
            "estimated_duration": estimated_duration,
            "required_agents": required_agents,
            "intent": intent
        }
    
    def _create_analysis_workflow(self, content: str, intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建分析工作流"""
        return [
            {
                "step_id": "intent_analysis",
                "name": "意图分析",
                "description": "分析用户意图和需求",
                "type": "analysis",
                "estimated_time": 2.0,
                "required_agents": ["intent_analyzer"]
            },
            {
                "step_id": "team_formation",
                "name": "团队组建",
                "description": "组建专业分析团队",
                "type": "formation",
                "estimated_time": 1.5,
                "required_agents": ["team_coordinator"]
            },
            {
                "step_id": "data_collection",
                "name": "数据收集",
                "description": "收集相关数据和信息",
                "type": "collection",
                "estimated_time": 5.0,
                "required_agents": ["data_collector"]
            },
            {
                "step_id": "analysis_execution",
                "name": "分析执行",
                "description": "执行深度分析",
                "type": "execution",
                "estimated_time": 10.0,
                "required_agents": ["domain_expert", "technical_expert"]
            },
            {
                "step_id": "result_synthesis",
                "name": "结果综合",
                "description": "综合分析结果并生成报告",
                "type": "synthesis",
                "estimated_time": 3.0,
                "required_agents": ["synthesis_expert"]
            }
        ]
    
    def _create_discussion_workflow(self, content: str, intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建讨论工作流"""
        return [
            {
                "step_id": "topic_analysis",
                "name": "主题分析",
                "description": "分析讨论主题和关键问题",
                "type": "analysis",
                "estimated_time": 2.0,
                "required_agents": ["topic_analyzer"]
            },
            {
                "step_id": "participant_selection",
                "name": "参与者选择",
                "description": "选择合适的讨论参与者",
                "type": "selection",
                "estimated_time": 1.0,
                "required_agents": ["participant_selector"]
            },
            {
                "step_id": "discussion_facilitation",
                "name": "讨论促进",
                "description": "促进多角度讨论和观点交流",
                "type": "facilitation",
                "estimated_time": 15.0,
                "required_agents": ["facilitator", "domain_expert", "critic"]
            },
            {
                "step_id": "consensus_building",
                "name": "共识建立",
                "description": "帮助建立共识和结论",
                "type": "consensus",
                "estimated_time": 5.0,
                "required_agents": ["consensus_builder"]
            }
        ]
    
    def _create_evaluation_workflow(self, content: str, intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建评估工作流"""
        return [
            {
                "step_id": "criteria_definition",
                "name": "标准定义",
                "description": "定义评估标准和方法",
                "type": "definition",
                "estimated_time": 2.0,
                "required_agents": ["criteria_expert"]
            },
            {
                "step_id": "evidence_collection",
                "name": "证据收集",
                "description": "收集评估所需的证据",
                "type": "collection",
                "estimated_time": 5.0,
                "required_agents": ["evidence_collector"]
            },
            {
                "step_id": "evaluation_execution",
                "name": "评估执行",
                "description": "执行评估分析",
                "type": "execution",
                "estimated_time": 8.0,
                "required_agents": ["evaluator", "domain_expert"]
            },
            {
                "step_id": "report_generation",
                "name": "报告生成",
                "description": "生成评估报告",
                "type": "generation",
                "estimated_time": 3.0,
                "required_agents": ["report_generator"]
            }
        ]
    
    def _create_summarization_workflow(self, content: str, intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建总结工作流"""
        return [
            {
                "step_id": "content_analysis",
                "name": "内容分析",
                "description": "分析要总结的内容",
                "type": "analysis",
                "estimated_time": 2.0,
                "required_agents": ["content_analyzer"]
            },
            {
                "step_id": "key_point_extraction",
                "name": "关键点提取",
                "description": "提取关键点和重要信息",
                "type": "extraction",
                "estimated_time": 3.0,
                "required_agents": ["key_point_extractor"]
            },
            {
                "step_id": "summary_generation",
                "name": "总结生成",
                "description": "生成结构化总结",
                "type": "generation",
                "estimated_time": 4.0,
                "required_agents": ["summary_generator"]
            },
            {
                "step_id": "quality_review",
                "name": "质量审查",
                "description": "审查总结质量",
                "type": "review",
                "estimated_time": 2.0,
                "required_agents": ["quality_reviewer"]
            }
        ]
    
    def _estimate_duration(self, workflow_steps: List[Dict[str, Any]]) -> float:
        """估算工作流执行时间"""
        return sum(step.get("estimated_time", 0) for step in workflow_steps)
    
    def _determine_required_agents(self, intent: Dict[str, Any]) -> List[str]:
        """确定所需的Agent"""
        intent_type = intent.get("type", "analysis")
        
        # 基于意图类型的基础Agent
        base_agents = {
            "analysis": ["analyst", "domain_expert"],
            "discussion": ["facilitator", "domain_expert", "critic"],
            "evaluation": ["evaluator", "domain_expert"],
            "summarization": ["summarizer", "content_analyzer"]
        }
        
        agents = base_agents.get(intent_type, ["general_agent"])
        
        # 根据内容复杂度添加更多Agent
        complexity = intent.get("complexity", 0.5)
        if complexity > 0.7:
            agents.append("technical_expert")
        
        if complexity > 0.8:
            agents.append("quality_reviewer")
        
        return list(set(agents))  # 去重
    
    async def start_workflow(self, workflow_id: str, workflow_plan: Dict[str, Any]) -> bool:
        """启动工作流"""
        if workflow_id in self.active_workflows:
            return False
        
        self.active_workflows[workflow_id] = {
            "plan": workflow_plan,
            "status": "running",
            "current_step": 0,
            "start_time": datetime.now(),
            "step_results": {},
            "progress": 0.0
        }
        
        return True
    
    async def execute_step(self, workflow_id: str, step_id: str) -> Dict[str, Any]:
        """执行工作流步骤"""
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.active_workflows[workflow_id]
        
        # 查找步骤
        step = None
        for s in workflow["plan"]["steps"]:
            if s["step_id"] == step_id:
                step = s
                break
        
        if not step:
            raise ValueError(f"Step {step_id} not found in workflow")
        
        # 模拟步骤执行
        await asyncio.sleep(step.get("estimated_time", 1.0) * 0.1)  # 加速执行
        
        # 记录结果
        result = {
            "step_id": step_id,
            "status": "completed",
            "execution_time": step.get("estimated_time", 1.0),
            "output": f"Completed {step['name']}",
            "timestamp": datetime.now()
        }
        
        workflow["step_results"][step_id] = result
        workflow["current_step"] += 1
        
        # 更新进度
        total_steps = len(workflow["plan"]["steps"])
        workflow["progress"] = workflow["current_step"] / total_steps
        
        return result
    
    def get_workflow_progress(self, workflow_id: str) -> Dict[str, Any]:
        """获取工作流进度"""
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.active_workflows[workflow_id]
        
        return {
            "workflow_id": workflow_id,
            "status": workflow["status"],
            "current_step": workflow["current_step"],
            "total_steps": len(workflow["plan"]["steps"]),
            "progress_percentage": workflow["progress"] * 100,
            "estimated_time_remaining": self._calculate_remaining_time(workflow_id),
            "step_results": workflow["step_results"]
        }
    
    def _calculate_remaining_time(self, workflow_id: str) -> float:
        """计算剩余时间"""
        workflow = self.active_workflows[workflow_id]
        total_steps = len(workflow["plan"]["steps"])
        completed_steps = workflow["current_step"]
        
        if completed_steps >= total_steps:
            return 0.0
        
        # 计算剩余步骤的估算时间
        remaining_time = 0.0
        for i in range(completed_steps, total_steps):
            remaining_time += workflow["plan"]["steps"][i].get("estimated_time", 0)
        
        return remaining_time
    
    def complete_workflow(self, workflow_id: str):
        """完成工作流"""
        if workflow_id not in self.active_workflows:
            return
        
        workflow = self.active_workflows[workflow_id]
        workflow["status"] = "completed"
        workflow["end_time"] = datetime.now()
        workflow["progress"] = 1.0
    
    def fail_workflow(self, workflow_id: str, error: str):
        """工作流失败"""
        if workflow_id not in self.active_workflows:
            return
        
        workflow = self.active_workflows[workflow_id]
        workflow["status"] = "failed"
        workflow["error"] = error
        workflow["end_time"] = datetime.now()


class UserInterventionService:
    """用户干预服务 - 优化和集成用户输入"""
    
    def __init__(self):
        self.intervention_patterns = {
            "comment": self._optimize_comment,
            "question": self._optimize_question,
            "suggestion": self._optimize_suggestion,
            "correction": self._optimize_correction
        }
        self.optimization_history = {}
    
    async def optimize_input(self, raw_input: str, intent_type: str, context: Dict[str, Any]) -> str:
        """优化用户输入"""
        if intent_type not in self.intervention_patterns:
            return raw_input
        
        # 应用特定意图类型的优化
        optimized_input = await self.intervention_patterns[intent_type](raw_input, context)
        
        # 记录优化历史
        self._record_optimization(raw_input, optimized_input, intent_type, context)
        
        return optimized_input
    
    async def _optimize_comment(self, raw_input: str, context: Dict[str, Any]) -> str:
        """优化评论输入"""
        # 确保评论具有建设性
        constructive_phrases = [
            "我认为", "我觉得", "从我的角度来看", "建议考虑", "或许可以",
            "I think", "I believe", "From my perspective", "I suggest", "Perhaps"
        ]
        
        # 如果没有建设性短语，添加一个
        if not any(phrase in raw_input for phrase in constructive_phrases):
            return f"我认为{raw_input}"
        
        return raw_input
    
    async def _optimize_question(self, raw_input: str, context: Dict[str, Any]) -> str:
        """优化问题输入"""
        # 确保问题清晰明确
        question_words = ["什么", "如何", "为什么", "怎么样", "是否", "能否", "what", "how", "why", "whether"]
        
        # 如果没有疑问词，添加适当的引导
        if not any(word in raw_input for word in question_words):
            return f"关于{raw_input}，您有什么看法？"
        
        return raw_input
    
    async def _optimize_suggestion(self, raw_input: str, context: Dict[str, Any]) -> str:
        """优化建议输入"""
        # 确保建议具有可操作性
        action_phrases = ["建议", "推荐", "可以考虑", "或许可以", "suggest", "recommend", "consider"]
        
        if not any(phrase in raw_input for phrase in action_phrases):
            return f"建议{raw_input}"
        
        return raw_input
    
    async def _optimize_correction(self, raw_input: str, context: Dict[str, Any]) -> str:
        """优化纠正输入"""
        # 确保纠正具有礼貌性
        polite_phrases = ["抱歉", "不好意思", "我想指出", "可能有个小错误", "sorry", "excuse me", "I'd like to point out"]
        
        if not any(phrase in raw_input for phrase in polite_phrases):
            return f"抱歉，我想指出{raw_input}"
        
        return raw_input
    
    async def integrate_intervention(self, debate_id: str, user_intervention: Dict[str, Any]) -> Dict[str, Any]:
        """集成用户干预到讨论中"""
        # 分析干预的影响
        impact_analysis = await self._analyze_intervention_impact(user_intervention)
        
        # 生成集成建议
        integration_suggestions = await self._generate_integration_suggestions(user_intervention, impact_analysis)
        
        # 计算影响分数
        impact_score = self._calculate_impact_score(impact_analysis)
        
        return {
            "status": "integrated",
            "impact_analysis": impact_analysis,
            "integration_suggestions": integration_suggestions,
            "impact_score": impact_score,
            "timestamp": datetime.now()
        }
    
    async def _analyze_intervention_impact(self, intervention: Dict[str, Any]) -> Dict[str, Any]:
        """分析干预影响"""
        content = intervention.get("content", "")
        intent = intervention.get("intent", "comment")
        
        # 分析内容特征
        content_length = len(content)
        complexity = self._analyze_content_complexity(content)
        constructiveness = self._analyze_constructiveness(content)
        
        return {
            "content_length": content_length,
            "complexity": complexity,
            "constructiveness": constructiveness,
            "intent": intent,
            "relevance": 0.8  # 简化的相关性评分
        }
    
    def _analyze_content_complexity(self, content: str) -> float:
        """分析内容复杂性"""
        # 基于长度、词汇多样性等
        words = content.split()
        unique_words = set(words)
        
        if len(words) == 0:
            return 0.0
        
        vocabulary_diversity = len(unique_words) / len(words)
        length_factor = min(len(content) / 200, 1.0)
        
        return (vocabulary_diversity * 0.6 + length_factor * 0.4)
    
    def _analyze_constructiveness(self, content: str) -> float:
        """分析建设性"""
        constructive_words = [
            "建议", "改进", "优化", "解决方案", "方法", "策略",
            "suggest", "improve", "optimize", "solution", "method", "strategy"
        ]
        
        constructive_count = sum(1 for word in constructive_words if word in content)
        return min(constructive_count / 2, 1.0)
    
    async def _generate_integration_suggestions(self, intervention: Dict[str, Any], impact_analysis: Dict[str, Any]) -> List[str]:
        """生成集成建议"""
        suggestions = []
        
        if impact_analysis["constructiveness"] > 0.7:
            suggestions.append("该干预具有高度建设性，建议优先考虑")
        
        if impact_analysis["complexity"] > 0.8:
            suggestions.append("内容较为复杂，建议分解讨论")
        
        if impact_analysis["content_length"] > 200:
            suggestions.append("内容较长，建议提取关键点")
        
        if not suggestions:
            suggestions.append("可以正常集成到讨论中")
        
        return suggestions
    
    def _calculate_impact_score(self, impact_analysis: Dict[str, Any]) -> float:
        """计算影响分数"""
        weights = {
            "constructiveness": 0.4,
            "complexity": 0.3,
            "relevance": 0.3
        }
        
        score = (
            impact_analysis["constructiveness"] * weights["constructiveness"] +
            impact_analysis["complexity"] * weights["complexity"] +
            impact_analysis["relevance"] * weights["relevance"]
        )
        
        return min(score, 1.0)
    
    def _record_optimization(self, original: str, optimized: str, intent_type: str, context: Dict[str, Any]):
        """记录优化历史"""
        timestamp = datetime.now()
        
        if timestamp not in self.optimization_history:
            self.optimization_history[timestamp] = []
        
        self.optimization_history[timestamp].append({
            "original": original,
            "optimized": optimized,
            "intent_type": intent_type,
            "context": context
        })
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """获取优化统计信息"""
        total_optimizations = sum(len(records) for records in self.optimization_history.values())
        
        if total_optimizations == 0:
            return {"total_optimizations": 0}
        
        # 计算平均改进程度
        total_improvement = 0
        intent_distribution = {}
        
        for records in self.optimization_history.values():
            for record in records:
                original_length = len(record["original"])
                optimized_length = len(record["optimized"])
                
                # 简化的改进计算
                improvement = abs(optimized_length - original_length) / max(original_length, 1)
                total_improvement += improvement
                
                intent_type = record["intent_type"]
                intent_distribution[intent_type] = intent_distribution.get(intent_type, 0) + 1
        
        return {
            "total_optimizations": total_optimizations,
            "average_improvement": total_improvement / total_optimizations,
            "intent_distribution": intent_distribution
        }


class ConsensusTrackingService:
    """共识跟踪服务 - 实时计算和跟踪共识水平"""
    
    def __init__(self):
        self.active_debates = {}
        self.consensus_algorithms = {
            "simple_majority": self._simple_majority_consensus,
            "weighted_voting": self._weighted_voting_consensus,
            "sentiment_analysis": self._sentiment_analysis_consensus
        }
    
    async def calculate_consensus(self, debate_id: str) -> ConsensusLevel:
        """计算共识水平"""
        if debate_id not in self.active_debates:
            return ConsensusLevel(0.0)
        
        debate_data = self.active_debates[debate_id]
        
        # 使用简单多数算法
        consensus_score = await self.consensus_algorithms["simple_majority"](debate_data)
        
        return ConsensusLevel(consensus_score)
    
    async def _simple_majority_consensus(self, debate_data: Dict[str, Any]) -> float:
        """简单多数共识算法"""
        messages = debate_data.get("messages", [])
        
        if not messages:
            return 0.0
        
        # 分析消息的立场
        positions = {}
        for message in messages:
            position = self._extract_message_position(message)
            if position:
                positions[message["sender"]] = position
        
        if not positions:
            return 0.0
        
        # 计算同意的比例
        agree_count = sum(1 for pos in positions.values() if pos == "agree")
        return agree_count / len(positions)
    
    def _extract_message_position(self, message: Dict[str, Any]) -> Optional[str]:
        """提取消息立场"""
        content = message.get("content", "").lower()
        
        agree_keywords = ["同意", "赞成", "支持", "正确", "是的", "agree", "support", "correct", "yes"]
        disagree_keywords = ["不同意", "反对", "不支持", "错误", "不是", "disagree", "oppose", "incorrect", "no"]
        
        agree_count = sum(1 for keyword in agree_keywords if keyword in content)
        disagree_count = sum(1 for keyword in disagree_keywords if keyword in content)
        
        if agree_count > disagree_count:
            return "agree"
        elif disagree_count > agree_count:
            return "disagree"
        else:
            return "neutral"
    
    async def _weighted_voting_consensus(self, debate_data: Dict[str, Any]) -> float:
        """加权投票共识算法"""
        messages = debate_data.get("messages", [])
        
        if not messages:
            return 0.0
        
        # 基于发送者权重和消息内容计算加权共识
        total_weight = 0.0
        agree_weight = 0.0
        
        for message in messages:
            sender = message["sender"]
            weight = self._get_sender_weight(sender)
            position = self._extract_message_position(message)
            
            total_weight += weight
            
            if position == "agree":
                agree_weight += weight
            elif position == "disagree":
                agree_weight -= weight * 0.5  # 反对权重较低
        
        if total_weight == 0:
            return 0.0
        
        return max(0.0, min(1.0, agree_weight / total_weight))
    
    def _get_sender_weight(self, sender: str) -> float:
        """获取发送者权重"""
        # 基于发送者类型分配权重
        if sender.startswith("agent_"):
            return 0.8  # Agent权重较高
        elif sender.startswith("user_"):
            return 1.0  # 用户权重最高
        else:
            return 0.5  # 其他权重较低
    
    async def _sentiment_analysis_consensus(self, debate_data: Dict[str, Any]) -> float:
        """情感分析共识算法"""
        messages = debate_data.get("messages", [])
        
        if not messages:
            return 0.0
        
        # 分析消息情感
        sentiment_scores = []
        for message in messages:
            sentiment = self._analyze_message_sentiment(message)
            sentiment_scores.append(sentiment)
        
        # 计算情感一致性
        if not sentiment_scores:
            return 0.0
        
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        sentiment_variance = sum((score - avg_sentiment) ** 2 for score in sentiment_scores) / len(sentiment_scores)
        
        # 方差越小，共识越高
        consensus = 1.0 - min(sentiment_variance, 1.0)
        return max(0.0, consensus)
    
    def _analyze_message_sentiment(self, message: Dict[str, Any]) -> float:
        """分析消息情感"""
        content = message.get("content", "")
        
        positive_words = ["好", "优秀", "棒", "赞", "支持", "同意", "good", "excellent", "great", "support", "agree"]
        negative_words = ["不好", "差", "反对", "不同意", "bad", "poor", "oppose", "disagree"]
        
        positive_count = sum(1 for word in positive_words if word in content)
        negative_count = sum(1 for word in negative_words if word in content)
        
        total_words = len(content.split())
        if total_words == 0:
            return 0.0
        
        sentiment = (positive_count - negative_count) / total_words
        return max(-1.0, min(1.0, sentiment))
    
    async def add_agent_opinion(self, debate_id: str, agent_id: str, opinion: str, confidence: float):
        """添加Agent观点"""
        if debate_id not in self.active_debates:
            self.active_debates[debate_id] = {
                "messages": [],
                "participants": [],
                "topic": ""
            }
        
        debate_data = self.active_debates[debate_id]
        
        # 添加Agent消息
        agent_message = {
            "sender": agent_id,
            "content": opinion,
            "timestamp": datetime.now(),
            "confidence": confidence
        }
        
        debate_data["messages"].append(agent_message)
        
        if agent_id not in debate_data["participants"]:
            debate_data["participants"].append(agent_id)
    
    async def add_message(self, debate_id: str, message: Dict[str, Any]):
        """添加消息"""
        if debate_id not in self.active_debates:
            self.active_debates[debate_id] = {
                "messages": [],
                "participants": [],
                "topic": ""
            }
        
        debate_data = self.active_debates[debate_id]
        debate_data["messages"].append(message)
        
        sender = message.get("sender")
        if sender and sender not in debate_data["participants"]:
            debate_data["participants"].append(sender)
    
    async def extract_key_arguments(self, debate_id: str) -> List[Dict[str, Any]]:
        """提取关键论点"""
        if debate_id not in self.active_debates:
            return []
        
        debate_data = self.active_debates[debate_id]
        messages = debate_data.get("messages", [])
        
        # 简化的论点提取
        key_arguments = []
        
        for message in messages:
            content = message.get("content", "")
            sender = message.get("sender")
            
            # 分析论点重要性
            importance = self._analyze_argument_importance(content)
            
            if importance > 0.5:  # 只包含重要论点
                key_arguments.append({
                    "argument": content[:100] + "..." if len(content) > 100 else content,
                    "sender": sender,
                    "importance": importance,
                    "timestamp": message.get("timestamp")
                })
        
        # 按重要性排序
        key_arguments.sort(key=lambda x: x["importance"], reverse=True)
        
        return key_arguments[:5]  # 返回前5个关键论点
    
    def _analyze_argument_importance(self, content: str) -> float:
        """分析论点重要性"""
        importance_keywords = [
            "关键", "重要", "核心", "主要", "本质", "fundamental", "key", "important", "core", "essential"
        ]
        
        keyword_count = sum(1 for keyword in importance_keywords if keyword in content)
        length_factor = min(len(content) / 100, 1.0)
        
        return min((keyword_count * 0.6 + length_factor * 0.4), 1.0)
    
    def get_debate_summary(self, debate_id: str) -> Dict[str, Any]:
        """获取辩论摘要"""
        if debate_id not in self.active_debates:
            return {}
        
        debate_data = self.active_debates[debate_id]
        
        return {
            "debate_id": debate_id,
            "topic": debate_data.get("topic", ""),
            "participant_count": len(debate_data.get("participants", [])),
            "message_count": len(debate_data.get("messages", [])),
            "consensus_level": asyncio.run(self.calculate_consensus(debate_id)).value,
            "key_arguments": asyncio.run(self.extract_key_arguments(debate_id))
        }
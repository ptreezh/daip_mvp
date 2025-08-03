#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-02 16:30:00
@Author  : DAIP-LIVE Team
@File    : expert_consultation_scenario.py
@Description:
    V0.2.5 专家咨询场景核心功能实现
    
    基于现有RoleManager和核心组件实现：
    - 跨领域专家角色库扩展
    - 智能专家邀请机制
    - 结构化观点收集和整理
    - 专家观点对比分析和综合建议
    - 权威性评估系统
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid
import json

# 导入项目核心组件
from src.core_services.role_manager import RoleManager
from src.core_services.integrated_llm_manager import IntegratedLLMManager
from src.virtual_role_chat.cognitive_agent.agent import CognitiveAgent, CognitiveProfile
from src.core_services.advanced_consensus_algorithms import WeightedVotingConsensus, ConsensusInput
from src.core_services.wiki_service import WikiService
from src.workflows.critical_review_workflow import CriticalReviewWorkflow

logger = logging.getLogger(__name__)


@dataclass
class ExpertProfile:
    """专家档案"""
    expert_id: str
    name: str
    domain: str
    expertise_areas: List[str]
    authority_score: float
    background: str
    perspective: str
    specialty_keywords: List[str]
    collaboration_style: str = "analytical"


@dataclass
class ExpertOpinion:
    """专家观点"""
    expert_id: str
    expert_name: str
    opinion_text: str
    confidence_level: float
    supporting_evidence: List[str]
    recommendations: List[str]
    concerns: List[str]
    authority_weight: float
    timestamp: str


@dataclass
class ConsultationConfig:
    """咨询配置"""
    max_experts: int = 5
    min_experts: int = 3
    authority_threshold: float = 0.6
    diversity_weight: float = 0.3
    consensus_threshold: float = 0.7
    enable_critical_review: bool = True
    include_contrarian_views: bool = True


class ExpertConsultationScenario:
    """
    专家咨询场景 - V0.2.5核心功能实现
    
    专注于为用户提供高质量的专家咨询服务：
    - 智能专家选择和邀请
    - 结构化观点收集
    - 权威性评估和观点综合
    - 决策支持和建议生成
    """
    
    def __init__(self):
        """初始化专家咨询场景"""
        self.scenario_id = str(uuid.uuid4())
        
        # 核心组件
        self.role_manager = RoleManager()
        self.llm_manager = IntegratedLLMManager()
        self.consensus_algorithm = WeightedVotingConsensus()
        self.wiki_service = WikiService()
        
        # 专家库
        self.expert_profiles = self._initialize_expert_database()
        
        # 咨询历史
        self.consultation_history: List[Dict[str, Any]] = []
        
        logger.info(f"专家咨询场景初始化完成: {self.scenario_id}")
    
    def _initialize_expert_database(self) -> Dict[str, ExpertProfile]:
        """初始化专家数据库"""
        
        # 基于现有RoleManager扩展跨领域专家
        expert_database = {
            # 技术领域专家
            "tech_architect": ExpertProfile(
                expert_id="tech_architect",
                name="技术架构师",
                domain="技术",
                expertise_areas=["系统架构", "技术选型", "性能优化", "安全设计"],
                authority_score=0.9,
                background="15年大型系统架构经验，主导过多个千万用户级产品的技术架构",
                perspective="技术可行性和架构设计角度",
                specialty_keywords=["架构", "技术", "系统", "性能", "安全", "扩展性"]
            ),
            
            "ai_researcher": ExpertProfile(
                expert_id="ai_researcher", 
                name="AI研究专家",
                domain="人工智能",
                expertise_areas=["机器学习", "深度学习", "自然语言处理", "AI伦理"],
                authority_score=0.95,
                background="AI领域博士，发表过50+篇顶会论文，参与多个工业AI项目",
                perspective="AI技术前沿和应用可行性角度",
                specialty_keywords=["AI", "机器学习", "深度学习", "算法", "模型", "数据"]
            ),
            
            # 商业领域专家
            "business_strategist": ExpertProfile(
                expert_id="business_strategist",
                name="商业战略专家", 
                domain="商业",
                expertise_areas=["战略规划", "市场分析", "商业模式", "竞争分析"],
                authority_score=0.88,
                background="20年企业战略咨询经验，服务过500强企业，专注商业模式创新",
                perspective="商业价值和市场机会角度",
                specialty_keywords=["商业", "战略", "市场", "盈利", "竞争", "模式"]
            ),
            
            "financial_analyst": ExpertProfile(
                expert_id="financial_analyst",
                name="财务分析师",
                domain="金融",
                expertise_areas=["财务分析", "投资评估", "风险管理", "成本控制"],
                authority_score=0.85,
                background="CFA持证人，10年投行和企业财务经验，擅长项目投资分析",
                perspective="财务可行性和投资回报角度",
                specialty_keywords=["财务", "投资", "成本", "收益", "风险", "资金"]
            ),
            
            # 用户体验专家
            "ux_designer": ExpertProfile(
                expert_id="ux_designer",
                name="用户体验专家",
                domain="设计",
                expertise_areas=["用户研究", "交互设计", "产品体验", "用户心理"],
                authority_score=0.82,
                background="12年UX设计经验，设计过多款千万用户产品，深度理解用户行为",
                perspective="用户需求和体验设计角度",
                specialty_keywords=["用户", "体验", "设计", "交互", "界面", "可用性"]
            ),
            
            # 行业分析专家
            "industry_analyst": ExpertProfile(
                expert_id="industry_analyst",
                name="行业分析师",
                domain="行业研究",
                expertise_areas=["行业趋势", "政策分析", "市场规模", "发展预测"],
                authority_score=0.87,
                background="知名咨询公司高级分析师，跟踪多个行业15年，发布过权威行业报告",
                perspective="行业发展和趋势预测角度",
                specialty_keywords=["行业", "趋势", "政策", "监管", "发展", "预测"]
            ),
            
            # 法律合规专家
            "legal_expert": ExpertProfile(
                expert_id="legal_expert",
                name="法律专家",
                domain="法律",
                expertise_areas=["合规审查", "知识产权", "合同法", "数据保护"],
                authority_score=0.90,
                background="执业律师15年，专注科技法律，处理过大量企业合规和知产案件",
                perspective="法律风险和合规要求角度",
                specialty_keywords=["法律", "合规", "风险", "知产", "隐私", "监管"]
            ),
            
            # 运营管理专家
            "operations_expert": ExpertProfile(
                expert_id="operations_expert",
                name="运营管理专家",
                domain="运营",
                expertise_areas=["项目管理", "团队管理", "流程优化", "运营策略"],
                authority_score=0.83,
                background="PMP认证项目经理，15年企业运营经验，管理过百人团队和亿级项目",
                perspective="运营执行和管理实施角度",
                specialty_keywords=["运营", "管理", "流程", "团队", "执行", "效率"]
            )
        }
        
        logger.info(f"专家数据库初始化完成，共{len(expert_database)}位专家")
        return expert_database
    
    async def conduct_expert_consultation(
        self,
        question: str,
        context: str = "",
        config: ConsultationConfig = None
    ) -> Dict[str, Any]:
        """
        进行专家咨询
        
        Args:
            question: 咨询问题
            context: 问题背景和上下文
            config: 咨询配置
            
        Returns:
            完整的专家咨询结果
        """
        if config is None:
            config = ConsultationConfig()
            
        consultation_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        logger.info(f"开始专家咨询: {consultation_id}")
        logger.info(f"咨询问题: {question}")
        
        try:
            # 1. 智能专家选择
            selected_experts = await self._select_experts_intelligently(
                question, context, config
            )
            
            # 2. 收集专家观点
            expert_opinions = await self._collect_expert_opinions(
                question, context, selected_experts, config
            )
            
            # 3. 权威性评估
            authority_analysis = await self._evaluate_expert_authority(
                expert_opinions, question
            )
            
            # 4. 观点对比分析
            opinion_analysis = await self._analyze_opinion_differences(
                expert_opinions, authority_analysis
            )
            
            # 5. 综合建议生成
            comprehensive_advice = await self._generate_comprehensive_advice(
                question, expert_opinions, opinion_analysis, authority_analysis
            )
            
            # 6. 决策支持
            decision_support = await self._generate_decision_support(
                question, comprehensive_advice, expert_opinions
            )
            
            # 7. 知识沉淀
            await self._persist_consultation_knowledge(
                consultation_id, question, expert_opinions, comprehensive_advice
            )
            
            end_time = datetime.now()
            
            result = {
                "success": True,
                "consultation_id": consultation_id,
                "question": question,
                "context": context,
                "selected_experts": [asdict(expert) for expert in selected_experts],
                "expert_opinions": [asdict(opinion) for opinion in expert_opinions],
                "authority_analysis": authority_analysis,
                "opinion_analysis": opinion_analysis,
                "comprehensive_advice": comprehensive_advice,
                "decision_support": decision_support,
                "metadata": {
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "duration_seconds": (end_time - start_time).total_seconds(),
                    "experts_count": len(selected_experts),
                    "config": asdict(config)
                }
            }
            
            self.consultation_history.append(result)
            logger.info(f"专家咨询完成: {consultation_id}")
            return result
            
        except Exception as e:
            logger.error(f"专家咨询失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "consultation_id": consultation_id,
                "question": question
            }
    
    async def _select_experts_intelligently(
        self, 
        question: str, 
        context: str, 
        config: ConsultationConfig
    ) -> List[ExpertProfile]:
        """智能选择专家组合"""
        
        logger.info("开始智能专家选择...")
        
        # 分析问题关键词
        question_keywords = self._extract_keywords(question + " " + context)
        
        # 计算每个专家的相关性得分
        expert_scores = []
        for expert_id, expert in self.expert_profiles.items():
            
            # 关键词匹配得分
            keyword_score = self._calculate_keyword_relevance(
                question_keywords, expert.specialty_keywords
            )
            
            # 权威性得分
            authority_score = expert.authority_score
            
            # 综合得分
            total_score = (
                keyword_score * 0.7 + 
                authority_score * 0.3
            )
            
            if total_score >= config.authority_threshold:
                expert_scores.append((expert, total_score))
        
        # 按得分排序
        expert_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 选择专家，确保多样性
        selected_experts = []
        selected_domains = set()
        
        for expert, score in expert_scores:
            if len(selected_experts) >= config.max_experts:
                break
                
            # 确保域多样性
            if expert.domain not in selected_domains or len(selected_experts) < config.min_experts:
                selected_experts.append(expert)
                selected_domains.add(expert.domain)
        
        # 如果需要对立观点，添加潜在的反对声音
        if config.include_contrarian_views and len(selected_experts) < config.max_experts:
            contrarian_expert = self._select_contrarian_expert(
                selected_experts, question_keywords
            )
            if contrarian_expert:
                selected_experts.append(contrarian_expert)
        
        logger.info(f"选择了{len(selected_experts)}位专家: {[e.name for e in selected_experts]}")
        return selected_experts
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词（简化实现）"""
        # 简化的关键词提取
        import re
        
        # 移除标点符号并转为小写
        clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = clean_text.split()
        
        # 过滤停用词和短词
        stop_words = {'的', '是', '在', '和', '有', '我', '你', '他', '她', '它', '我们', '你们', '他们'}
        keywords = [word for word in words if len(word) > 1 and word not in stop_words]
        
        return list(set(keywords))  # 去重
    
    def _calculate_keyword_relevance(self, question_keywords: List[str], expert_keywords: List[str]) -> float:
        """计算关键词相关性"""
        if not question_keywords or not expert_keywords:
            return 0.0
        
        # 计算交集
        common_keywords = set(question_keywords) & set([kw.lower() for kw in expert_keywords])
        
        # 相关性得分
        relevance = len(common_keywords) / len(set(question_keywords))
        return min(relevance, 1.0)
    
    def _select_contrarian_expert(
        self, 
        selected_experts: List[ExpertProfile], 
        question_keywords: List[str]
    ) -> Optional[ExpertProfile]:
        """选择可能提供对立观点的专家"""
        
        selected_domains = {expert.domain for expert in selected_experts}
        
        # 寻找不同领域的专家
        for expert in self.expert_profiles.values():
            if expert.domain not in selected_domains:
                # 简单策略：选择第一个不同领域的高权威专家
                if expert.authority_score > 0.8:
                    return expert
        
        return None
    
    async def _collect_expert_opinions(
        self,
        question: str,
        context: str,
        experts: List[ExpertProfile],
        config: ConsultationConfig
    ) -> List[ExpertOpinion]:
        """收集专家观点"""
        
        logger.info("开始收集专家观点...")
        opinions = []
        
        for expert in experts:
            try:
                # 构建专家特定的提示
                expert_prompt = self._build_expert_prompt(expert, question, context)
                
                # 调用LLM获取专家观点
                opinion_response = await self._get_expert_opinion_from_llm(
                    expert, expert_prompt
                )
                
                # 解析和结构化观点
                structured_opinion = self._parse_expert_opinion(
                    expert, opinion_response, question
                )
                
                opinions.append(structured_opinion)
                
            except Exception as e:
                logger.error(f"收集专家{expert.name}观点失败: {e}")
                # 创建错误占位观点
                error_opinion = ExpertOpinion(
                    expert_id=expert.expert_id,
                    expert_name=expert.name,
                    opinion_text=f"抱歉，{expert.name}暂时无法提供观点。",
                    confidence_level=0.0,
                    supporting_evidence=[],
                    recommendations=[],
                    concerns=[f"技术错误: {str(e)}"],
                    authority_weight=expert.authority_score,
                    timestamp=datetime.now().isoformat()
                )
                opinions.append(error_opinion)
        
        logger.info(f"成功收集{len(opinions)}个专家观点")
        return opinions
    
    def _build_expert_prompt(self, expert: ExpertProfile, question: str, context: str) -> str:
        """构建专家特定的提示"""
        
        prompt = f"""
你是{expert.name}，在{expert.domain}领域有着丰富的经验。

你的专业背景：{expert.background}

你的专业领域包括：{', '.join(expert.expertise_areas)}

现在请从你的专业角度({expert.perspective})回答以下问题：

问题：{question}

背景信息：{context}

请提供：
1. 你的专业观点和分析
2. 支持你观点的依据或证据
3. 具体的建议和推荐方案
4. 可能的风险或担忧
5. 你对这个观点的信心程度(1-10分)

请以专业、客观的方式回答，体现你在该领域的专业水准。
        """.strip()
        
        return prompt
    
    async def _get_expert_opinion_from_llm(self, expert: ExpertProfile, prompt: str) -> str:
        """从LLM获取专家观点"""
        
        try:
            # 使用集成LLM管理器
            response = await self.llm_manager.call_llm_for_role(
                role_id=expert.expert_id,
                user_input=prompt,
                task_context=f"专家咨询 - {expert.domain}领域分析"
            )
            
            return response.get("response", "无法获取专家观点")
            
        except Exception as e:
            # 回退到模拟响应
            logger.warning(f"LLM调用失败，使用模拟响应: {e}")
            return self._generate_simulated_expert_opinion(expert, prompt)
    
    def _generate_simulated_expert_opinion(self, expert: ExpertProfile, prompt: str) -> str:
        """生成模拟专家观点（用于测试和回退）"""
        
        return f"""
从{expert.perspective}来看，这个问题涉及{expert.domain}领域的多个重要方面。

基于我在{', '.join(expert.expertise_areas)}方面的经验，我认为：

1. 核心分析：这个问题的关键在于平衡{expert.expertise_areas[0]}和{expert.expertise_areas[1] if len(expert.expertise_areas) > 1 else '实际应用'}的需求。

2. 支持依据：根据我过往的项目经验和行业观察，类似情况通常需要考虑{expert.domain}领域的最佳实践。

3. 具体建议：
   - 建议采用{expert.expertise_areas[0]}的标准方法
   - 重点关注{expert.domain}领域的风险控制
   - 确保方案的可执行性和可扩展性

4. 潜在风险：需要特别注意{expert.domain}领域可能出现的合规性和可持续性问题。

5. 信心程度：基于当前信息，我的信心程度为8/10。

总的来说，从{expert.domain}专业角度，这是一个需要谨慎考虑但有可行性的方案。
        """.strip()
    
    def _parse_expert_opinion(
        self, 
        expert: ExpertProfile, 
        opinion_text: str, 
        question: str
    ) -> ExpertOpinion:
        """解析和结构化专家观点"""
        
        # 简化的解析逻辑 - 在实际应用中可以使用更复杂的NLP技术
        
        # 提取信心程度
        confidence_level = self._extract_confidence_level(opinion_text)
        
        # 提取建议（简化版）
        recommendations = self._extract_recommendations(opinion_text)
        
        # 提取担忧（简化版）
        concerns = self._extract_concerns(opinion_text)
        
        # 提取支持证据（简化版）
        supporting_evidence = self._extract_evidence(opinion_text)
        
        return ExpertOpinion(
            expert_id=expert.expert_id,
            expert_name=expert.name,
            opinion_text=opinion_text,
            confidence_level=confidence_level,
            supporting_evidence=supporting_evidence,
            recommendations=recommendations,
            concerns=concerns,
            authority_weight=expert.authority_score,
            timestamp=datetime.now().isoformat()
        )
    
    def _extract_confidence_level(self, text: str) -> float:
        """提取信心程度"""
        import re
        
        # 查找信心程度表达
        confidence_patterns = [
            r'信心程度[：:]?\s*(\d+(?:\.\d+)?)[/／]?10',
            r'信心[：:]?\s*(\d+(?:\.\d+)?)[/／]?10',
            r'置信度[：:]?\s*(\d+(?:\.\d+)?)[/／]?10'
        ]
        
        for pattern in confidence_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    score = float(match.group(1))
                    return min(score / 10.0, 1.0)
                except:
                    pass
        
        # 默认中等信心
        return 0.7
    
    def _extract_recommendations(self, text: str) -> List[str]:
        """提取建议"""
        recommendations = []
        
        # 简化提取：查找"建议"相关的句子
        import re
        sentences = re.split(r'[。！？\n]', text)
        
        for sentence in sentences:
            if any(keyword in sentence for keyword in ['建议', '推荐', '应该', '可以考虑']):
                clean_sentence = sentence.strip()
                if len(clean_sentence) > 5:
                    recommendations.append(clean_sentence)
        
        return recommendations[:5]  # 最多5个建议
    
    def _extract_concerns(self, text: str) -> List[str]:
        """提取担忧"""
        concerns = []
        
        import re
        sentences = re.split(r'[。！？\n]', text)
        
        for sentence in sentences:
            if any(keyword in sentence for keyword in ['风险', '担忧', '问题', '挑战', '困难']):
                clean_sentence = sentence.strip()
                if len(clean_sentence) > 5:
                    concerns.append(clean_sentence)
        
        return concerns[:3]  # 最多3个担忧
    
    def _extract_evidence(self, text: str) -> List[str]:
        """提取支持证据"""
        evidence = []
        
        import re
        sentences = re.split(r'[。！？\n]', text)
        
        for sentence in sentences:
            if any(keyword in sentence for keyword in ['根据', '基于', '数据显示', '研究表明', '经验表明']):
                clean_sentence = sentence.strip()
                if len(clean_sentence) > 10:
                    evidence.append(clean_sentence)
        
        return evidence[:3]  # 最多3个证据
    
    async def _evaluate_expert_authority(
        self, 
        opinions: List[ExpertOpinion], 
        question: str
    ) -> Dict[str, Any]:
        """评估专家权威性"""
        
        logger.info("开始权威性评估...")
        
        authority_scores = {}
        
        for opinion in opinions:
            # 基础权威性得分
            base_authority = opinion.authority_weight
            
            # 观点质量得分（基于内容长度、结构等）
            content_quality = self._assess_content_quality(opinion.opinion_text)
            
            # 信心程度影响
            confidence_impact = opinion.confidence_level
            
            # 综合权威性得分
            final_authority = (
                base_authority * 0.5 +
                content_quality * 0.3 +
                confidence_impact * 0.2
            )
            
            authority_scores[opinion.expert_id] = {
                "expert_name": opinion.expert_name,
                "base_authority": base_authority,
                "content_quality": content_quality,
                "confidence_impact": confidence_impact,
                "final_authority": final_authority,
                "opinion_length": len(opinion.opinion_text),
                "recommendations_count": len(opinion.recommendations),
                "evidence_count": len(opinion.supporting_evidence)
            }
        
        # 排序找出最权威的专家
        sorted_experts = sorted(
            authority_scores.items(),
            key=lambda x: x[1]["final_authority"],
            reverse=True
        )
        
        return {
            "authority_scores": authority_scores,
            "most_authoritative": sorted_experts[0] if sorted_experts else None,
            "average_authority": sum(
                score["final_authority"] for score in authority_scores.values()
            ) / len(authority_scores) if authority_scores else 0,
            "authority_distribution": {
                "high_authority": len([s for s in authority_scores.values() if s["final_authority"] > 0.8]),
                "medium_authority": len([s for s in authority_scores.values() if 0.6 <= s["final_authority"] <= 0.8]),
                "low_authority": len([s for s in authority_scores.values() if s["final_authority"] < 0.6])
            }
        }
    
    def _assess_content_quality(self, content: str) -> float:
        """评估内容质量"""
        if not content:
            return 0.0
        
        # 简化的内容质量评估
        length_score = min(len(content) / 1000, 1.0)  # 基于长度
        structure_score = self._assess_structure(content)  # 基于结构
        
        return (length_score + structure_score) / 2
    
    def _assess_structure(self, content: str) -> float:
        """评估内容结构"""
        structure_indicators = [
            '1.', '2.', '3.',  # 数字列表
            '一、', '二、', '三、',  # 中文列表
            '首先', '其次', '最后',  # 逻辑连接词
            '总结', '结论', '建议'  # 结构性词汇
        ]
        
        indicator_count = sum(1 for indicator in structure_indicators if indicator in content)
        return min(indicator_count / 5, 1.0)
    
    async def _analyze_opinion_differences(
        self, 
        opinions: List[ExpertOpinion], 
        authority_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """分析观点差异"""
        
        logger.info("开始分析观点差异...")
        
        if len(opinions) < 2:
            return {"analysis": "专家数量不足，无法进行对比分析"}
        
        # 分析一致性和分歧点
        consensus_points = []
        disagreement_points = []
        
        # 收集所有建议
        all_recommendations = []
        for opinion in opinions:
            all_recommendations.extend(opinion.recommendations)
        
        # 收集所有担忧
        all_concerns = []
        for opinion in opinions:
            all_concerns.extend(opinion.concerns)
        
        # 分析观点分布
        confidence_levels = [opinion.confidence_level for opinion in opinions]
        avg_confidence = sum(confidence_levels) / len(confidence_levels)
        confidence_variance = sum((c - avg_confidence) ** 2 for c in confidence_levels) / len(confidence_levels)
        
        # 识别主要分歧（简化版）
        high_confidence_opinions = [op for op in opinions if op.confidence_level > 0.8]
        low_confidence_opinions = [op for op in opinions if op.confidence_level < 0.5]
        
        return {
            "opinion_summary": {
                "total_experts": len(opinions),
                "average_confidence": avg_confidence,
                "confidence_variance": confidence_variance,
                "high_confidence_count": len(high_confidence_opinions),
                "low_confidence_count": len(low_confidence_opinions)
            },
            "consensus_indicators": {
                "similar_recommendations": len(set(all_recommendations)) < len(all_recommendations) * 0.8,
                "common_concerns": len(set(all_concerns)) < len(all_concerns) * 0.8,
                "confidence_alignment": confidence_variance < 0.1
            },
            "disagreement_areas": {
                "confidence_divergence": confidence_variance > 0.2,
                "recommendation_diversity": len(set(all_recommendations)) / len(all_recommendations) if all_recommendations else 0,
                "concern_diversity": len(set(all_concerns)) / len(all_concerns) if all_concerns else 0
            },
            "most_agreed_points": self._find_common_themes(all_recommendations),
            "main_concerns": self._find_common_themes(all_concerns)
        }
    
    def _find_common_themes(self, items: List[str]) -> List[str]:
        """找出共同主题（简化版）"""
        if not items:
            return []
        
        # 简化：按关键词频次统计
        word_counts = {}
        for item in items:
            words = item.split()
            for word in words:
                if len(word) > 2:  # 忽略短词
                    word_counts[word] = word_counts.get(word, 0) + 1
        
        # 返回出现频次最高的主题
        common_themes = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        return [theme[0] for theme in common_themes[:5]]
    
    async def _generate_comprehensive_advice(
        self,
        question: str,
        opinions: List[ExpertOpinion],
        opinion_analysis: Dict[str, Any],
        authority_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成综合建议"""
        
        logger.info("开始生成综合建议...")
        
        # 权重加权的建议综合
        weighted_recommendations = self._weight_recommendations(opinions, authority_analysis)
        
        # 风险综合评估
        risk_assessment = self._synthesize_risks(opinions, authority_analysis)
        
        # 决策建议
        decision_recommendations = self._generate_decision_recommendations(
            question, weighted_recommendations, risk_assessment, opinion_analysis
        )
        
        # 实施路径
        implementation_path = self._suggest_implementation_path(
            decision_recommendations, opinions
        )
        
        return {
            "executive_summary": self._generate_executive_summary(
                question, opinions, decision_recommendations
            ),
            "weighted_recommendations": weighted_recommendations,
            "risk_assessment": risk_assessment,
            "decision_recommendations": decision_recommendations,
            "implementation_path": implementation_path,
            "expert_consensus_level": opinion_analysis.get("opinion_summary", {}).get("average_confidence", 0),
            "recommendation_confidence": self._calculate_recommendation_confidence(
                opinions, authority_analysis
            )
        }
    
    def _weight_recommendations(
        self, 
        opinions: List[ExpertOpinion], 
        authority_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """权重加权建议"""
        
        recommendation_weights = {}
        
        for opinion in opinions:
            expert_authority = authority_analysis["authority_scores"][opinion.expert_id]["final_authority"]
            
            for rec in opinion.recommendations:
                if rec not in recommendation_weights:
                    recommendation_weights[rec] = {
                        "recommendation": rec,
                        "total_weight": 0,
                        "supporting_experts": [],
                        "average_confidence": 0
                    }
                
                recommendation_weights[rec]["total_weight"] += expert_authority
                recommendation_weights[rec]["supporting_experts"].append({
                    "expert_name": opinion.expert_name,
                    "authority": expert_authority,
                    "confidence": opinion.confidence_level
                })
        
        # 计算平均信心程度
        for rec_data in recommendation_weights.values():
            if rec_data["supporting_experts"]:
                rec_data["average_confidence"] = sum(
                    expert["confidence"] for expert in rec_data["supporting_experts"]
                ) / len(rec_data["supporting_experts"])
        
        # 按权重排序
        sorted_recommendations = sorted(
            recommendation_weights.values(),
            key=lambda x: x["total_weight"],
            reverse=True
        )
        
        return sorted_recommendations[:10]  # 返回前10个建议
    
    def _synthesize_risks(
        self, 
        opinions: List[ExpertOpinion], 
        authority_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """综合风险评估"""
        
        all_concerns = []
        for opinion in opinions:
            expert_authority = authority_analysis["authority_scores"][opinion.expert_id]["final_authority"]
            for concern in opinion.concerns:
                all_concerns.append({
                    "concern": concern,
                    "expert_name": opinion.expert_name,
                    "authority_weight": expert_authority,
                    "confidence": opinion.confidence_level
                })
        
        # 风险分类（简化版）
        risk_categories = {
            "技术风险": [],
            "商业风险": [],
            "合规风险": [],
            "运营风险": [],
            "其他风险": []
        }
        
        for concern_data in all_concerns:
            concern = concern_data["concern"]
            categorized = False
            
            if any(keyword in concern for keyword in ["技术", "系统", "架构", "性能"]):
                risk_categories["技术风险"].append(concern_data)
                categorized = True
            elif any(keyword in concern for keyword in ["市场", "商业", "盈利", "竞争"]):
                risk_categories["商业风险"].append(concern_data)
                categorized = True
            elif any(keyword in concern for keyword in ["法律", "合规", "监管", "政策"]):
                risk_categories["合规风险"].append(concern_data)
                categorized = True
            elif any(keyword in concern for keyword in ["运营", "管理", "团队", "流程"]):
                risk_categories["运营风险"].append(concern_data)
                categorized = True
            
            if not categorized:
                risk_categories["其他风险"].append(concern_data)
        
        return {
            "risk_categories": risk_categories,
            "high_priority_risks": [
                concern for concern in all_concerns 
                if concern["authority_weight"] > 0.8 and concern["confidence"] > 0.7
            ],
            "risk_summary": {
                "total_risks_identified": len(all_concerns),
                "high_authority_risks": len([
                    c for c in all_concerns if c["authority_weight"] > 0.8
                ]),
                "consensus_risks": self._find_consensus_risks(all_concerns)
            }
        }
    
    def _find_consensus_risks(self, concerns: List[Dict[str, Any]]) -> List[str]:
        """找出共识风险"""
        # 简化：查找被多个专家提到的相似风险
        concern_texts = [c["concern"] for c in concerns]
        return self._find_common_themes(concern_texts)[:3]
    
    def _generate_decision_recommendations(
        self,
        question: str,
        weighted_recommendations: List[Dict[str, Any]],
        risk_assessment: Dict[str, Any],
        opinion_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成决策建议"""
        
        # 基于专家建议的决策框架
        top_recommendations = weighted_recommendations[:5]
        high_priority_risks = risk_assessment["high_priority_risks"]
        
        # 决策建议分类
        immediate_actions = []
        short_term_actions = []
        long_term_actions = []
        
        for i, rec in enumerate(top_recommendations):
            if i < 2:
                immediate_actions.append(rec["recommendation"])
            elif i < 4:
                short_term_actions.append(rec["recommendation"])
            else:
                long_term_actions.append(rec["recommendation"])
        
        # 风险缓解策略
        risk_mitigation = []
        for risk in high_priority_risks[:3]:
            risk_mitigation.append(f"针对'{risk['concern']}'的缓解措施需要重点关注")
        
        return {
            "recommended_approach": top_recommendations[0]["recommendation"] if top_recommendations else "需要更多信息",
            "confidence_level": weighted_recommendations[0]["average_confidence"] if weighted_recommendations else 0,
            "action_plan": {
                "immediate_actions": immediate_actions,
                "short_term_actions": short_term_actions,
                "long_term_actions": long_term_actions
            },
            "risk_mitigation_priorities": risk_mitigation,
            "success_factors": [
                rec["recommendation"] for rec in weighted_recommendations[:3]
            ],
            "go_no_go_recommendation": self._generate_go_no_go_decision(
                opinion_analysis, risk_assessment
            )
        }
    
    def _generate_go_no_go_decision(
        self, 
        opinion_analysis: Dict[str, Any], 
        risk_assessment: Dict[str, Any]
    ) -> Dict[str, str]:
        """生成Go/No-Go决策建议"""
        
        avg_confidence = opinion_analysis.get("opinion_summary", {}).get("average_confidence", 0)
        high_risks = len(risk_assessment.get("high_priority_risks", []))
        
        if avg_confidence > 0.7 and high_risks < 3:
            return {
                "decision": "GO",
                "rationale": "专家信心程度高，风险可控，建议推进"
            }
        elif avg_confidence < 0.4 or high_risks > 5:
            return {
                "decision": "NO-GO",
                "rationale": "专家信心不足或风险过高，建议暂停或重新评估"
            }
        else:
            return {
                "decision": "CONDITIONAL",
                "rationale": "需要进一步分析和风险缓解后再决定"
            }
    
    def _suggest_implementation_path(
        self, 
        decision_recommendations: Dict[str, Any], 
        opinions: List[ExpertOpinion]
    ) -> Dict[str, Any]:
        """建议实施路径"""
        
        return {
            "phase_1": {
                "name": "准备阶段",
                "duration": "1-2周",
                "actions": decision_recommendations.get("action_plan", {}).get("immediate_actions", [])
            },
            "phase_2": {
                "name": "执行阶段", 
                "duration": "1-3个月",
                "actions": decision_recommendations.get("action_plan", {}).get("short_term_actions", [])
            },
            "phase_3": {
                "name": "优化阶段",
                "duration": "3-6个月",
                "actions": decision_recommendations.get("action_plan", {}).get("long_term_actions", [])
            },
            "success_metrics": [
                "专家建议的落实程度",
                "风险缓解效果",
                "预期目标达成情况"
            ],
            "review_points": [
                "每个阶段结束后进行专家回顾",
                "关键风险点的定期评估",
                "实施效果的量化分析"
            ]
        }
    
    def _generate_executive_summary(
        self, 
        question: str, 
        opinions: List[ExpertOpinion], 
        decision_recommendations: Dict[str, Any]
    ) -> str:
        """生成执行摘要"""
        
        expert_names = [op.expert_name for op in opinions]
        avg_confidence = sum(op.confidence_level for op in opinions) / len(opinions) if opinions else 0
        
        return f"""
关于"{question}"的专家咨询总结：

我们邀请了{len(opinions)}位领域专家（{', '.join(expert_names)}）进行深度分析。

专家整体信心程度：{avg_confidence:.1%}

核心建议：{decision_recommendations.get('recommended_approach', '需要更多分析')}

决策建议：{decision_recommendations.get('go_no_go_recommendation', {}).get('decision', 'PENDING')}

主要行动：{', '.join(decision_recommendations.get('action_plan', {}).get('immediate_actions', [])[:2])}

本咨询为您的决策提供了多角度的专业视角和具体的实施建议。
        """.strip()
    
    def _calculate_recommendation_confidence(
        self, 
        opinions: List[ExpertOpinion], 
        authority_analysis: Dict[str, Any]
    ) -> float:
        """计算建议信心程度"""
        
        if not opinions:
            return 0.0
        
        # 加权平均信心程度
        total_weight = 0
        weighted_confidence = 0
        
        for opinion in opinions:
            authority = authority_analysis["authority_scores"][opinion.expert_id]["final_authority"]
            weighted_confidence += opinion.confidence_level * authority
            total_weight += authority
        
        return weighted_confidence / total_weight if total_weight > 0 else 0
    
    async def _generate_decision_support(
        self,
        question: str,
        comprehensive_advice: Dict[str, Any],
        expert_opinions: List[ExpertOpinion]
    ) -> Dict[str, Any]:
        """生成决策支持材料"""
        
        return {
            "decision_matrix": self._create_decision_matrix(comprehensive_advice),
            "pros_and_cons": self._extract_pros_and_cons(expert_opinions),
            "stakeholder_impact": self._analyze_stakeholder_impact(expert_opinions),
            "resource_requirements": self._estimate_resource_requirements(expert_opinions),
            "timeline_estimate": comprehensive_advice.get("implementation_path", {}),
            "alternatives": self._identify_alternatives(expert_opinions),
            "next_steps": self._recommend_next_steps(comprehensive_advice)
        }
    
    def _create_decision_matrix(self, advice: Dict[str, Any]) -> Dict[str, Any]:
        """创建决策矩阵"""
        return {
            "criteria": ["可行性", "成本效益", "风险水平", "时间投入", "资源需求"],
            "scores": {
                "可行性": advice.get("recommendation_confidence", 0) * 5,
                "成本效益": 4.0,  # 简化评分
                "风险水平": 5 - len(advice.get("risk_assessment", {}).get("high_priority_risks", [])),
                "时间投入": 3.5,
                "资源需求": 3.0
            },
            "weight": {"可行性": 0.3, "成本效益": 0.25, "风险水平": 0.2, "时间投入": 0.15, "资源需求": 0.1}
        }
    
    def _extract_pros_and_cons(self, opinions: List[ExpertOpinion]) -> Dict[str, List[str]]:
        """提取利弊分析"""
        pros = []
        cons = []
        
        for opinion in opinions:
            # 建议视为优点
            pros.extend(opinion.recommendations)
            # 担忧视为缺点
            cons.extend(opinion.concerns)
        
        return {
            "pros": list(set(pros))[:5],  # 去重并限制数量
            "cons": list(set(cons))[:5]
        }
    
    def _analyze_stakeholder_impact(self, opinions: List[ExpertOpinion]) -> Dict[str, str]:
        """分析利益相关者影响"""
        return {
            "用户": "直接受益于改进的产品或服务",
            "团队": "需要学习新技能和适应变化",
            "管理层": "需要投入资源并承担决策责任",
            "合作伙伴": "可能需要调整合作模式",
            "竞争对手": "可能面临竞争压力"
        }
    
    def _estimate_resource_requirements(self, opinions: List[ExpertOpinion]) -> Dict[str, str]:
        """估算资源需求"""
        return {
            "人力资源": "需要专业团队3-5人",
            "时间投入": "预计3-6个月",
            "资金预算": "需要根据具体方案评估",
            "技术资源": "可能需要新技术和工具",
            "外部支持": "建议聘请相关专家顾问"
        }
    
    def _identify_alternatives(self, opinions: List[ExpertOpinion]) -> List[str]:
        """识别替代方案"""
        alternatives = []
        
        # 从专家建议中提取可能的替代方案
        for opinion in opinions:
            for rec in opinion.recommendations:
                if any(keyword in rec for keyword in ["也可以", "或者", "另一种", "替代"]):
                    alternatives.append(rec)
        
        # 如果没有明确的替代方案，提供通用选项
        if not alternatives:
            alternatives = [
                "分阶段实施，降低风险",
                "寻求外部合作伙伴",
                "简化方案，快速验证",
                "暂缓决策，收集更多信息"
            ]
        
        return alternatives[:3]
    
    def _recommend_next_steps(self, advice: Dict[str, Any]) -> List[str]:
        """推荐下一步行动"""
        immediate_actions = advice.get("decision_recommendations", {}).get("action_plan", {}).get("immediate_actions", [])
        
        if immediate_actions:
            return immediate_actions[:3]
        else:
            return [
                "组织团队讨论专家建议",
                "制定详细的实施计划",
                "进行风险评估和缓解规划"
            ]
    
    async def _persist_consultation_knowledge(
        self,
        consultation_id: str,
        question: str,
        expert_opinions: List[ExpertOpinion],
        comprehensive_advice: Dict[str, Any]
    ):
        """持久化咨询知识"""
        
        try:
            # 构建知识条目
            knowledge_entry = {
                "id": consultation_id,
                "type": "expert_consultation",
                "question": question,
                "expert_count": len(expert_opinions),
                "key_recommendations": [
                    rec["recommendation"] for rec in 
                    comprehensive_advice.get("weighted_recommendations", [])[:3]
                ],
                "decision_recommendation": comprehensive_advice.get("decision_recommendations", {}).get("go_no_go_recommendation"),
                "confidence_level": comprehensive_advice.get("recommendation_confidence", 0),
                "timestamp": datetime.now().isoformat(),
                "experts_involved": [op.expert_name for op in expert_opinions]
            }
            
            # 保存到Wiki服务（简化实现）
            logger.info(f"专家咨询知识已记录: {knowledge_entry}")
            
        except Exception as e:
            logger.error(f"知识持久化失败: {e}")


# 使用示例
async def main():
    """测试专家咨询场景"""
    scenario = ExpertConsultationScenario()
    
    # 测试咨询
    question = "我们公司想要实施人工智能转型，应该如何规划和执行？"
    context = "我们是一家传统制造企业，有500名员工，希望通过AI提升生产效率和产品质量。"
    
    config = ConsultationConfig(
        max_experts=5,
        min_experts=3,
        enable_critical_review=True,
        include_contrarian_views=True
    )
    
    result = await scenario.conduct_expert_consultation(
        question=question,
        context=context,
        config=config
    )
    
    if result["success"]:
        print(f"\n专家咨询完成！")
        print(f"咨询ID: {result['consultation_id']}")
        print(f"参与专家: {len(result['selected_experts'])}位")
        print(f"执行摘要: {result['comprehensive_advice']['executive_summary']}")
        print(f"决策建议: {result['decision_support']['next_steps']}")
    else:
        print(f"咨询失败: {result['error']}")


if __name__ == "__main__":
    asyncio.run(main())
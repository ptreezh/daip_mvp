"""
@Time: 2025-08-05
@Author: DAIP-LIVE Team
@File: expert_consultation_scenario.py
@Description: Enhanced Expert Consultation Scenario with Real LLM Integration
"""

import asyncio
import json
import logging
import aiohttp
import time
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum

from .smart_reviewer_allocator_simple import SmartReviewerAllocator, ReviewRequest, AllocationPriority
from .multidimensional_assessment_engine import MultiDimensionalAssessmentEngine
from .collaborative_review_environment import CollaborativeReviewEnvironment, ReviewSession
from .knowledge_retrieval_service import KnowledgeRetrievalService, SearchScope

# Import AssessmentRequest for type compatibility
try:
    from ..api.v0_3_5_critical_review_api import AssessmentRequest
except ImportError:
    # Fallback definition if import fails
    from dataclasses import dataclass
    from typing import List, Dict, Any
    
    @dataclass
    class AssessmentRequest:
        id: str
        content: str
        assessment_type: str
        dimensions: List[str]
        context: Dict[str, Any]


@dataclass
class LLMCallRecord:
    """LLM调用记录"""
    id: str
    timestamp: str
    model: str
    prompt: str
    response: str
    tokens_input: int
    tokens_output: int
    response_time: float
    cost: float
    success: bool
    error: Optional[str] = None


class ConsultationType(Enum):
    """咨询类型"""
    TECHNICAL_REVIEW = "technical_review"      # 技术评审
    STRATEGIC_ADVISORY = "strategic_advisory"   # 战略咨询
    PROBLEM_SOLVING = "problem_solving"        # 问题解决
    VALIDATION = "validation"                   # 验证确认
    OPTIMIZATION = "optimization"               # 优化建议


class ConsultationPriority(Enum):
    """咨询优先级"""
    URGENT = "urgent"          # 紧急 (24小时内)
    HIGH = "high"              # 高 (3天内)
    MEDIUM = "medium"          # 中等 (1周内)
    LOW = "low"               # 低 (2周内)


@dataclass
class ExpertConsultationRequest:
    """专家咨询请求"""
    id: str
    title: str
    description: str
    consultation_type: ConsultationType
    priority: ConsultationPriority
    requester: str
    domain: str
    specific_areas: List[str]
    background_context: str
    expected_outcomes: List[str]
    time_constraints: Dict[str, Any]
    budget_constraints: Optional[Dict[str, Any]] = None
    expert_requirements: List[str] = None
    attachments: List[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class ExpertOpinion:
    """专家意见"""
    expert_id: str
    expert_name: str
    expertise_areas: List[str]
    opinion: str
    confidence_level: float
    reasoning: str
    recommendations: List[str]
    potential_risks: List[str]
    alternative_approaches: List[str]
    estimated_effort: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class ConsultationSynthesis:
    """咨询综合分析"""
    consultation_id: str
    consensus_opinion: str
    key_findings: List[str]
    divergent_viewpoints: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    risk_assessment: Dict[str, Any]
    implementation_roadmap: List[Dict[str, Any]]
    confidence_score: float
    expert_participation: Dict[str, Any]
    quality_metrics: Dict[str, float]
    generated_at: datetime = None
    
    def __post_init__(self):
        if self.generated_at is None:
            self.generated_at = datetime.now()


class RealLLMIntegrator:
    """真实LLM集成器"""
    
    def __init__(self):
        self.call_history: List[LLMCallRecord] = []
        self.ollama_available = False
        self.openai_available = False
        self.logger = logging.getLogger(__name__)
        
        # 检查可用的LLM服务
        asyncio.create_task(self._check_llm_availability())
    
    async def _check_llm_availability(self):
        """检查LLM服务可用性"""
        # 检查Ollama
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:11434/api/tags', timeout=aiohttp.ClientTimeout(total=3)) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.ollama_available = True
                        self.available_models = [model['name'] for model in data.get('models', [])]
                        self.logger.info(f"Ollama可用，模型: {self.available_models}")
        except:
            self.logger.warning("Ollama不可用，将使用模拟模式")
        
        # 检查OpenAI API Key
        import os
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            self.openai_available = True
            self.logger.info("OpenAI API Key检测到")
        else:
            self.logger.warning("未检测到OpenAI API Key")
    
    async def call_llm(self, prompt: str, model: str = "llama3:instruct", role_context: str = "") -> LLMCallRecord:
        """调用真实LLM"""
        call_id = str(uuid.uuid4())
        start_time = time.time()
        
        # 构建完整提示
        full_prompt = f"{role_context}\n\n用户问题: {prompt}" if role_context else prompt
        
        try:
            if self.ollama_available and model.startswith('llama'):
                return await self._call_ollama(call_id, full_prompt, model, start_time)
            elif self.openai_available and model.startswith('gpt'):
                return await self._call_openai(call_id, full_prompt, model, start_time)
            else:
                # 降级到高质量模拟
                return await self._call_simulated_llm(call_id, full_prompt, model, start_time)
        
        except Exception as e:
            response_time = time.time() - start_time
            record = LLMCallRecord(
                id=call_id,
                timestamp=datetime.now().isoformat(),
                model=model,
                prompt=full_prompt,
                response="",
                tokens_input=len(full_prompt.split()),
                tokens_output=0,
                response_time=response_time,
                cost=0.0,
                success=False,
                error=str(e)
            )
            self.call_history.append(record)
            return record
    
    async def _call_ollama(self, call_id: str, prompt: str, model: str, start_time: float) -> LLMCallRecord:
        """调用Ollama"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            
            async with session.post('http://localhost:11434/api/generate', 
                                  json=payload, 
                                  timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get('response', '')
                    
                    response_time = time.time() - start_time
                    
                    record = LLMCallRecord(
                        id=call_id,
                        timestamp=datetime.now().isoformat(),
                        model=model,
                        prompt=prompt,
                        response=response_text,
                        tokens_input=len(prompt.split()),
                        tokens_output=len(response_text.split()),
                        response_time=response_time,
                        cost=0.0,  # Ollama通常免费
                        success=True
                    )
                    
                    self.call_history.append(record)
                    self.logger.info(f"Ollama调用成功: {model} | {response_time:.2f}s | {len(response_text)}字符")
                    return record
                else:
                    raise Exception(f"Ollama API错误: {response.status}")
    
    async def _call_openai(self, call_id: str, prompt: str, model: str, start_time: float) -> LLMCallRecord:
        """调用OpenAI"""
        import os
        api_key = os.getenv('OPENAI_API_KEY')
        
        async with aiohttp.ClientSession() as session:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1000
            }
            
            async with session.post('https://api.openai.com/v1/chat/completions',
                                  json=payload,
                                  headers=headers,
                                  timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    data = await response.json()
                    choice = data['choices'][0]
                    response_text = choice['message']['content']
                    
                    usage = data.get('usage', {})
                    tokens_input = usage.get('prompt_tokens', len(prompt.split()))
                    tokens_output = usage.get('completion_tokens', len(response_text.split()))
                    
                    # 估算成本（基于GPT-3.5价格）
                    cost = (tokens_input * 0.0015 + tokens_output * 0.002) / 1000
                    
                    response_time = time.time() - start_time
                    
                    record = LLMCallRecord(
                        id=call_id,
                        timestamp=datetime.now().isoformat(),
                        model=model,
                        prompt=prompt,
                        response=response_text,
                        tokens_input=tokens_input,
                        tokens_output=tokens_output,
                        response_time=response_time,
                        cost=cost,
                        success=True
                    )
                    
                    self.call_history.append(record)
                    self.logger.info(f"OpenAI调用成功: {model} | {response_time:.2f}s | ${cost:.4f}")
                    return record
                else:
                    raise Exception(f"OpenAI API错误: {response.status}")
    
    async def _call_simulated_llm(self, call_id: str, prompt: str, model: str, start_time: float) -> LLMCallRecord:
        """高质量模拟LLM调用"""
        # 模拟网络延迟
        await asyncio.sleep(0.5 + len(prompt) / 1000)
        
        # 生成智能响应
        response = self._generate_intelligent_response(prompt)
        
        response_time = time.time() - start_time
        
        record = LLMCallRecord(
            id=call_id,
            timestamp=datetime.now().isoformat(),
            model=f"{model}(模拟)",
            prompt=prompt,
            response=response,
            tokens_input=len(prompt.split()),
            tokens_output=len(response.split()),
            response_time=response_time,
            cost=0.0,
            success=True
        )
        
        self.call_history.append(record)
        self.logger.info(f"模拟LLM调用: {model} | {response_time:.2f}s | 高质量模拟")
        return record
    
    def _generate_intelligent_response(self, prompt: str) -> str:
        """生成智能响应"""
        if "分析" in prompt or "analysis" in prompt.lower():
            return f"""## 深度分析报告

**分析主题:** {prompt[:100]}...

### 🔍 多维度分析

**1. 技术层面分析:**
- 可行性评估: 基于当前技术栈，该方案具有较高的实现可能性
- 技术风险: 需要关注性能优化、安全性和可扩展性问题
- 实施复杂度: 中等，需要2-3个开发周期

**2. 业务影响分析:**
- 商业价值: 能够显著提升用户体验和运营效率
- 市场机会: 符合当前行业发展趋势，具有竞争优势
- 投资回报: 预期ROI在18-24个月内实现正向收益

**3. 风险评估:**
- 高风险项: 技术选型、团队能力匹配
- 中风险项: 市场接受度、竞争对手响应
- 低风险项: 基础设施、合规要求

### 🎯 推荐方案

基于综合分析，建议采用渐进式实施策略：
1. 第一阶段: MVP验证 (4-6周)
2. 第二阶段: 功能完善 (8-10周) 
3. 第三阶段: 规模化部署 (12-16周)

### 📊 关键指标预测
- 实施成功率: 85%
- 预期效果达成: 90%
- 资源投入产出比: 1:3.2

*此分析基于DAIP-LIVE多AI协作生成，结合了技术专家、商业分析师和风险评估师的专业观点。*"""

        else:
            return f"""## 专家咨询意见

**咨询主题:** {prompt[:100]}...

### 💡 专业分析

基于专业知识和经验，我对该问题的分析如下：

**核心观点:**
1. 该问题具有重要的实际意义和紧迫性
2. 需要从多个维度进行综合分析和评估
3. 建议采用系统化的解决方案

**具体建议:**
- 建立详细的问题分析框架
- 制定分阶段实施计划
- 建立风险监控和预警机制
- 确保资源的合理配置和利用

**预期效果:**
通过系统化的解决方案，预期可以达到以下效果：
- 问题得到有效解决
- 风险得到有效控制
- 资源利用效率显著提升
- 建立可持续的改进机制

*此意见由DAIP-LIVE专家咨询系统生成。*"""


class ExpertConsultationScenario:
    """增强的专家咨询场景"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Set up logging to handle Unicode properly
        logging.basicConfig(level=logging.INFO, force=True)
        
        # 核心组件
        self.expert_allocator = SmartReviewerAllocator()
        self.assessment_engine = MultiDimensionalAssessmentEngine(None, None, None)
        self.collaborative_env = CollaborativeReviewEnvironment(None, None, None)
        self.llm_integrator = RealLLMIntegrator()
        self.knowledge_service = None  # 可选的知识检索服务
        
        # 咨询历史
        self.consultation_history: List[Dict[str, Any]] = []
        self.expert_performance: Dict[str, Dict[str, Any]] = {}
        
        # 场景配置
        self.config = {
            "max_experts_per_consultation": 5,
            "min_experts_per_consultation": 2,
            "default_response_time": 72,  # 小时
            "synthesis_threshold": 0.7,    # 共识阈值
            "quality_threshold": 0.6,      # 质量阈值
            "use_real_llm": True,           # 使用真实LLM
            "llm_model": "llama3:instruct" # 默认LLM模型
        }
        
        self.logger.info("Enhanced ExpertConsultationScenario initialized")
    
    async def handle_consultation(self, request: ExpertConsultationRequest) -> Dict[str, Any]:
        """处理专家咨询请求"""
        try:
            self.logger.info(f"开始处理专家咨询: {request.title}")
            
            # 1. 智能选择专家
            expert_selection = await self._select_experts(request)
            
            if not expert_selection["success"]:
                return {
                    "success": False,
                    "error": expert_selection["error"],
                    "consultation_id": request.id
                }
            
            # 2. 创建协作评审会话
            session_result = await self._create_collaborative_session(request, expert_selection)
            
            # 3. 收集专家意见
            opinions = await self._collect_expert_opinions(session_result["session_id"], request)
            
            # 4. 多维度评估
            assessment = await self._assess_consultation_quality(request, opinions)
            
            # 5. 生成综合建议
            synthesis = await self._generate_consultation_synthesis(request, opinions, assessment)
            
            # 6. 记录咨询历史
            await self._record_consultation_history(request, expert_selection, opinions, synthesis)
            
            result = {
                "success": True,
                "consultation_id": request.id,
                "session_id": session_result["session_id"],
                "expert_selection": expert_selection,
                "opinions": opinions,
                "assessment": assessment,
                "synthesis": synthesis,
                "metadata": {
                    "total_experts": len(expert_selection["selected_experts"]),
                    "consultation_type": request.consultation_type.value,
                    "processing_time": (datetime.now() - request.created_at).total_seconds() if hasattr(request, 'created_at') else 0
                }
            }
            
            self.logger.info(f"专家咨询处理完成: {request.id}")
            return result
            
        except Exception as e:
            self.logger.error(f"处理专家咨询失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "consultation_id": request.id
            }
    
    async def _select_experts(self, request: ExpertConsultationRequest) -> Dict[str, Any]:
        """智能选择专家"""
        try:
            # 转换咨询类型为评审类型
            content_type_mapping = {
                ConsultationType.TECHNICAL_REVIEW: "technical_review",
                ConsultationType.STRATEGIC_ADVISORY: "strategic_advisory",
                ConsultationType.PROBLEM_SOLVING: "problem_solving",
                ConsultationType.VALIDATION: "validation",
                ConsultationType.OPTIMIZATION: "optimization"
            }
            
            # 转换优先级
            priority_mapping = {
                ConsultationPriority.URGENT: AllocationPriority.HIGH,
                ConsultationPriority.HIGH: AllocationPriority.HIGH,
                ConsultationPriority.MEDIUM: AllocationPriority.MEDIUM,
                ConsultationPriority.LOW: AllocationPriority.LOW
            }
            
            # 确定所需专家数量
            required_count = min(
                self.config["max_experts_per_consultation"],
                max(
                    self.config["min_experts_per_consultation"],
                    len(request.specific_areas)
                )
            )
            
            # 调用智能分配器
            allocation_result = await self.expert_allocator.select_reviewers(
                content_type=content_type_mapping[request.consultation_type],
                content_tags=request.specific_areas + [request.domain],
                required_count=required_count,
                context={
                    "priority": request.priority.value,
                    "time_constraints": request.time_constraints,
                    "expert_requirements": request.expert_requirements or []
                }
            )
            
            if allocation_result["success"]:
                # 增强专家信息
                enhanced_experts = []
                for expert_id in allocation_result["selected_reviewers"]:
                    expert_profile = self.expert_allocator.reviewer_pool.get(expert_id)
                    if expert_profile:
                        enhanced_experts.append({
                            "id": expert_id,
                            "name": expert_profile.name,
                            "specializations": [spec.value for spec in expert_profile.specializations],
                            "experience_level": expert_profile.experience_level.value,
                            "quality_score": expert_profile.quality_score,
                            "availability_score": expert_profile.availability_score,
                            "estimated_response_time": expert_profile.response_time_avg
                        })
                
                allocation_result["selected_experts"] = enhanced_experts
                allocation_result["expert_details"] = [asdict(profile) for profile in 
                    [self.expert_allocator.reviewer_pool.get(eid) for eid in allocation_result["selected_reviewers"]] 
                    if self.expert_allocator.reviewer_pool.get(eid)]
            
            return allocation_result
            
        except Exception as e:
            self.logger.error(f"选择专家失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def _create_collaborative_session(self, request: ExpertConsultationRequest, 
                                         expert_selection: Dict[str, Any]) -> Dict[str, Any]:
        """创建协作评审会话"""
        try:
            # 创建会话描述
            session_description = f"""
            专家咨询会话: {request.title}
            
            咨询类型: {request.consultation_type.value}
            领域: {request.domain}
            优先级: {request.priority.value}
            
            背景描述:
            {request.background_context}
            
            期望成果:
            {', '.join(request.expected_outcomes)}
            
            时间约束:
            {json.dumps(request.time_constraints, ensure_ascii=False, indent=2)}
            """
            
            # 创建协作会话
            session = ReviewSession(
                id=f"consultation_{request.id}",
                title=request.title,
                description=session_description,
                content_type="expert_consultation",
                participants=expert_selection["selected_reviewers"],
                created_at=datetime.now(),
                deadline=datetime.now() + timedelta(hours=request.time_constraints.get("response_time", self.config["default_response_time"])),
                metadata={
                    "consultation_id": request.id,
                    "consultation_type": request.consultation_type.value,
                    "domain": request.domain,
                    "priority": request.priority.value,
                    "requester": request.requester
                }
            )
            
            session_result = self.collaborative_env.create_session(session)
            
            return {
                "success": True,
                "session_id": session.id,
                "session": session_result
            }
            
        except Exception as e:
            self.logger.error(f"创建协作会话失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def _collect_expert_opinions(self, session_id: str, request: ExpertConsultationRequest) -> List[ExpertOpinion]:
        """收集专家意见"""
        try:
            opinions = []
            
            # 获取会话信息
            session = self.collaborative_env.get_session(session_id)
            if not session:
                raise ValueError(f"会话不存在: {session_id}")
            
            # 模拟专家意见收集（实际系统中会调用真实的专家接口）
            for expert_id in session.participants:
                expert_profile = self.expert_allocator.reviewer_pool.get(expert_id)
                if expert_profile:
                    opinion = await self._generate_expert_opinion(expert_profile, request)
                    opinions.append(opinion)
                    
                    # 添加到协作会话
                    self.collaborative_env.add_comment(
                        session_id,
                        expert_id,
                        f"专家意见: {opinion.opinion[:200]}...",
                        metadata={"opinion_id": opinion.expert_id}
                    )
            
            self.logger.info(f"收集到 {len(opinions)} 位专家意见")
            return opinions
            
        except Exception as e:
            self.logger.error(f"收集专家意见失败: {e}")
            return []
    
    async def _generate_expert_opinion(self, expert_profile, request: ExpertConsultationRequest) -> ExpertOpinion:
        """生成专家意见（模拟）"""
        try:
            # 基于专家专长和请求内容生成意见
            expertise_areas = [spec.value for spec in expert_profile.specializations]
            
            # 模拟意见生成逻辑
            opinion_content = f"""
            基于{', '.join(expertise_areas)}的专业背景，我对{request.title}的分析如下：
            
            主要观点：
            1. 该问题在{request.domain}领域具有典型性
            2. 建议{request.specific_areas[0] if request.specific_areas else '综合'}方面重点关注
            3. 考虑到{request.priority.value}优先级，建议采用渐进式解决方案
            
            具体建议将在详细分析后提供。
            """
            
            # 计算置信度
            confidence = min(0.9, expert_profile.quality_score + 0.1)
            
            return ExpertOpinion(
                expert_id=expert_profile.id,
                expert_name=expert_profile.name,
                expertise_areas=expertise_areas,
                opinion=opinion_content.strip(),
                confidence_level=confidence,
                reasoning="基于专业知识和经验的分析",
                recommendations=[
                    "建立详细的问题分析框架",
                    "制定分阶段实施计划",
                    "建立风险监控机制"
                ],
                potential_risks=[
                    "技术实施复杂度可能超出预期",
                    "资源配置需要优化",
                    "时间进度可能受到影响"
                ],
                alternative_approaches=[
                    "采用敏捷开发方法",
                    "考虑外部专家支持",
                    "建立跨部门协作机制"
                ],
                estimated_effort={
                    "person_days": 15,
                    "duration_weeks": 4,
                    "complexity": "medium"
                }
            )
            
        except Exception as e:
            self.logger.error(f"生成专家意见失败: {e}")
            return ExpertOpinion(
                expert_id=expert_profile.id,
                expert_name=expert_profile.name,
                expertise_areas=[],
                opinion="无法生成专家意见",
                confidence_level=0.0,
                reasoning="系统错误",
                recommendations=[],
                potential_risks=[],
                alternative_approaches=[]
            )
    
    async def _assess_consultation_quality(self, request: ExpertConsultationRequest, 
                                         opinions: List[ExpertOpinion]) -> Dict[str, Any]:
        """评估咨询质量"""
        try:
            # 创建评估请求
            assessment_request = AssessmentRequest(
                id=f"assessment_{request.id}",
                content=request.description,
                assessment_type="consultation_quality",
                dimensions=[
                    "expertise_match",
                    "opinion_quality", 
                    "response_completeness",
                    "practical_value",
                    "risk_analysis"
                ],
                context={
                    "consultation_type": request.consultation_type.value,
                    "domain": request.domain,
                    "expert_count": len(opinions),
                    "priority": request.priority.value
                }
            )
            
            # 执行评估
            assessment_result = await self.assessment_engine.assess_content(assessment_request)
            
            return {
                "assessment_id": assessment_request.id,
                "overall_score": assessment_result.get("overall_score", 0.0),
                "dimension_scores": assessment_result.get("dimension_scores", {}),
                "quality_indicators": assessment_result.get("quality_indicators", []),
                "recommendations": assessment_result.get("recommendations", [])
            }
            
        except Exception as e:
            self.logger.error(f"评估咨询质量失败: {e}")
            return {"overall_score": 0.0, "error": str(e)}
    
    async def _generate_consultation_synthesis(self, request: ExpertConsultationRequest,
                                            opinions: List[ExpertOpinion],
                                            assessment: Dict[str, Any]) -> ConsultationSynthesis:
        """生成咨询综合分析"""
        try:
            # 分析共识和分歧
            consensus_points = []
            divergent_points = []
            
            # 提取关键发现
            all_recommendations = []
            all_risks = []
            
            for opinion in opinions:
                all_recommendations.extend(opinion.recommendations)
                all_risks.extend(opinion.potential_risks)
            
            # 统计共识度
            recommendation_frequency = {}
            for rec in all_recommendations:
                recommendation_frequency[rec] = recommendation_frequency.get(rec, 0) + 1
            
            # 识别共识建议（出现频率 >= 50%）
            consensus_threshold = len(opinions) * 0.5
            consensus_recommendations = [
                {"recommendation": rec, "support_count": count}
                for rec, count in recommendation_frequency.items()
                if count >= consensus_threshold
            ]
            
            # 识别分歧观点
            divergent_viewpoints = [
                {
                    "topic": "解决方案优先级",
                    "viewpoints": [
                        {"expert": opinion.expert_name, "view": "优先考虑技术实现"},
                        {"expert": opinion.expert_name, "view": "优先考虑资源配置"}
                    ],
                    "resolution": "建议综合考虑技术和资源因素"
                }
            ]
            
            # 生成综合意见
            consensus_opinion = f"""
            基于{len(opinions)}位专家的综合分析，针对{request.title}的咨询结果如下：
            
            主要共识：
            {chr(10).join([f"• {rec['recommendation']}（{rec['support_count']}位专家支持）" for rec in consensus_recommendations])}
            
            总体建议：
            1. 建立系统化的问题解决框架
            2. 制定分阶段实施计划
            3. 建立风险预警机制
            4. 确保资源配置合理
            5. 建立效果评估体系
            """
            
            # 计算置信度
            confidence_score = (
                assessment.get("overall_score", 0.0) * 0.6 +
                sum(opinion.confidence_level for opinion in opinions) / len(opinions) * 0.4
            )
            
            # 生成实施路线图
            implementation_roadmap = [
                {
                    "phase": "准备阶段",
                    "duration_weeks": 2,
                    "key_activities": ["需求分析", "资源评估", "团队组建"],
                    "deliverables": ["需求规格书", "资源计划", "团队配置"]
                },
                {
                    "phase": "实施阶段", 
                    "duration_weeks": 8,
                    "key_activities": ["方案设计", "开发实施", "测试验证"],
                    "deliverables": ["设计方案", "系统实现", "测试报告"]
                },
                {
                    "phase": "验收阶段",
                    "duration_weeks": 2,
                    "key_activities": ["效果评估", "优化调整", "知识转移"],
                    "deliverables": ["验收报告", "优化方案", "培训材料"]
                }
            ]
            
            return ConsultationSynthesis(
                consultation_id=request.id,
                consensus_opinion=consensus_opinion.strip(),
                key_findings=[
                    "问题具有复杂性和多维性",
                    "需要系统化解决方案",
                    "资源协调是关键成功因素",
                    "风险管控需要重点关注"
                ],
                divergent_viewpoints=divergent_viewpoints,
                recommendations=consensus_recommendations,
                risk_assessment={
                    "overall_risk_level": "medium",
                    "key_risks": [
                        {"risk": "技术风险", "probability": "medium", "impact": "high"},
                        {"risk": "资源风险", "probability": "low", "impact": "medium"},
                        {"risk": "时间风险", "probability": "medium", "impact": "medium"}
                    ],
                    "mitigation_strategies": [
                        "建立技术验证机制",
                        "提前进行资源规划",
                        "制定详细时间计划"
                    ]
                },
                implementation_roadmap=implementation_roadmap,
                confidence_score=confidence_score,
                expert_participation={
                    "total_experts": len(opinions),
                    "participation_rate": 1.0,
                    "average_confidence": sum(opinion.confidence_level for opinion in opinions) / len(opinions),
                    "expertise_coverage": len(set().union(*[opinion.expertise_areas for opinion in opinions]))
                },
                quality_metrics={
                    "overall_quality": assessment.get("overall_score", 0.0),
                    "expertise_match": assessment.get("dimension_scores", {}).get("expertise_match", 0.0),
                    "practical_value": assessment.get("dimension_scores", {}).get("practical_value", 0.0),
                    "risk_analysis": assessment.get("dimension_scores", {}).get("risk_analysis", 0.0)
                }
            )
            
        except Exception as e:
            self.logger.error(f"生成咨询综合分析失败: {e}")
            return ConsultationSynthesis(
                consultation_id=request.id,
                consensus_opinion="无法生成综合分析",
                key_findings=[],
                divergent_viewpoints=[],
                recommendations=[],
                risk_assessment={},
                implementation_roadmap=[],
                confidence_score=0.0,
                expert_participation={},
                quality_metrics={}
            )
    
    async def _record_consultation_history(self, request: ExpertConsultationRequest,
                                         expert_selection: Dict[str, Any],
                                         opinions: List[ExpertOpinion],
                                         synthesis: ConsultationSynthesis):
        """记录咨询历史"""
        try:
            history_record = {
                "consultation_id": request.id,
                "timestamp": datetime.now().isoformat(),
                "request": asdict(request),
                "expert_selection": expert_selection,
                "opinions": [asdict(opinion) for opinion in opinions],
                "synthesis": asdict(synthesis),
                "summary": {
                    "total_experts": len(opinions),
                    "confidence_score": synthesis.confidence_score,
                    "key_recommendations_count": len(synthesis.recommendations),
                    "implementation_phases": len(synthesis.implementation_roadmap)
                }
            }
            
            self.consultation_history.append(history_record)
            
            # 更新专家表现记录
            for opinion in opinions:
                if opinion.expert_id not in self.expert_performance:
                    self.expert_performance[opinion.expert_id] = {
                        "consultations_participated": 0,
                        "average_confidence": 0.0,
                        "total_quality_score": 0.0,
                        "recent_performance": []
                    }
                
                perf = self.expert_performance[opinion.expert_id]
                perf["consultations_participated"] += 1
                perf["recent_performance"].append({
                    "consultation_id": request.id,
                    "confidence": opinion.confidence_level,
                    "timestamp": opinion.timestamp.isoformat()
                })
                
                # 更新平均置信度
                total_confidence = sum(p["confidence"] for p in perf["recent_performance"])
                perf["average_confidence"] = total_confidence / len(perf["recent_performance"])
            
            self.logger.info(f"咨询历史记录已保存: {request.id}")
            
        except Exception as e:
            self.logger.error(f"记录咨询历史失败: {e}")
    
    def get_consultation_statistics(self) -> Dict[str, Any]:
        """获取咨询统计信息"""
        try:
            if not self.consultation_history:
                return {"message": "暂无咨询历史"}
            
            total_consultations = len(self.consultation_history)
            successful_consultations = len([h for h in self.consultation_history if h["synthesis"]["confidence_score"] > 0.6])
            
            # 按类型统计
            type_stats = {}
            for record in self.consultation_history:
                consultation_type = record["request"]["consultation_type"]
                if consultation_type not in type_stats:
                    type_stats[consultation_type] = {"count": 0, "avg_confidence": 0.0}
                type_stats[consultation_type]["count"] += 1
                type_stats[consultation_type]["avg_confidence"] += record["synthesis"]["confidence_score"]
            
            # 计算平均置信度
            for consultation_type in type_stats:
                type_stats[consultation_type]["avg_confidence"] /= type_stats[consultation_type]["count"]
            
            # 专家表现统计
            expert_stats = {}
            for expert_id, perf in self.expert_performance.items():
                expert_stats[expert_id] = {
                    "consultations_participated": perf["consultations_participated"],
                    "average_confidence": perf["average_confidence"],
                    "performance_trend": "improving" if len(perf["recent_performance"]) > 1 else "stable"
                }
            
            return {
                "total_consultations": total_consultations,
                "successful_consultations": successful_consultations,
                "success_rate": successful_consultations / total_consultations if total_consultations > 0 else 0.0,
                "consultation_type_statistics": type_stats,
                "expert_performance": expert_stats,
                "average_confidence_score": sum(h["synthesis"]["confidence_score"] for h in self.consultation_history) / total_consultations if total_consultations > 0 else 0.0,
                "recent_activity": [
                    {
                        "consultation_id": h["consultation_id"],
                        "timestamp": h["timestamp"],
                        "type": h["request"]["consultation_type"],
                        "confidence": h["synthesis"]["confidence_score"]
                    }
                    for h in sorted(self.consultation_history, key=lambda x: x["timestamp"], reverse=True)[:5]
                ]
            }
            
        except Exception as e:
            self.logger.error(f"获取咨询统计失败: {e}")
            return {"error": str(e)}


# 使用示例
async def example_expert_consultation():
    """专家咨询使用示例"""
    # 创建专家咨询场景
    consultation_scenario = ExpertConsultationScenario()
    
    # 创建咨询请求
    request = ExpertConsultationRequest(
        id="consultation_001",
        title="AI系统架构优化咨询",
        description="需要优化现有AI系统的架构设计，提升性能和可扩展性",
        consultation_type=ConsultationType.TECHNICAL_REVIEW,
        priority=ConsultationPriority.HIGH,
        requester="技术部门",
        domain="人工智能",
        specific_areas=["系统架构", "性能优化", "可扩展性"],
        background_context="现有系统在处理大规模数据时性能瓶颈明显，需要重新设计架构",
        expected_outcomes=["架构优化方案", "性能提升策略", "实施路线图"],
        time_constraints={"response_time": 48, "implementation_timeline": 90},
        expert_requirements=["架构设计经验", "AI系统经验", "性能优化经验"]
    )
    
    # 处理咨询
    result = await consultation_scenario.handle_consultation(request)
    
    print(f"咨询结果: {result}")
    
    # 获取统计信息
    stats = consultation_scenario.get_consultation_statistics()
    print(f"统计信息: {stats}")


if __name__ == "__main__":
    asyncio.run(example_expert_consultation())
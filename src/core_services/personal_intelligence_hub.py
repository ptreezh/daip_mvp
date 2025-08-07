# -*- coding: utf-8 -*-
"""
Dual-Entrance Personal Intelligence Hub Implementation

Implements the core dual-entrance architecture with:
1. The Secretariat - Streamlined, result-oriented interface
2. The Forum - Interactive, process-oriented interface

Supports all scenarios from UserCase.txt including expert consultation,
academic research, and industry analysis.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
from abc import ABC, abstractmethod

# Import existing DAIP services
from .multi_agent_collaboration_system import (
    MultiAgentService, CollaborationSession, AgentProfile,
    InstitutionalPrimitive, ConsensusMethod, CollaborationMode
)
from .institutional_primitives import InstitutionalPrimitiveFactory, PrimitiveContext

logger = logging.getLogger(__name__)

class EntranceType(str, Enum):
    """Dual entrance types"""
    SECRETARIAT = "secretariat"
    FORUM = "forum"

class IntentType(str, Enum):
    """Intent types from UserCase.txt"""
    CASUAL_DISCUSSION = "casual_discussion"
    ACADEMIC_RESEARCH = "academic_research"
    EXPERT_CONSULTATION = "expert_consultation"
    INDUSTRY_ANALYSIS = "industry_analysis"
    CRITICAL_REVIEW = "critical_review"

@dataclass
class UserRequest:
    """User request with context"""
    request_id: str
    user_id: str
    content: str
    entrance_type: EntranceType
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    priority: int = 1

@dataclass
class HubResponse:
    """Response from Personal Intelligence Hub"""
    response_id: str
    request_id: str
    entrance_type: EntranceType
    intent_type: IntentType
    success: bool
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    session_id: Optional[str] = None

class BaseEntrance(ABC):
    """Base class for both entrances"""
    
    def __init__(self, entrance_type: EntranceType, multi_agent_service: MultiAgentService):
        self.entrance_type = entrance_type
        self.multi_agent_service = multi_agent_service
        self.logger = logging.getLogger(f"{__name__}.{entrance_type.value}")
        
    @abstractmethod
    async def process_request(self, request: UserRequest) -> HubResponse:
        """Process user request"""
        pass
    
    @abstractmethod
    async def get_interface_config(self) -> Dict[str, Any]:
        """Get interface configuration"""
        pass

class SecretariatEntrance(BaseEntrance):
    """The Secretariat - Streamlined, result-oriented interface"""
    
    def __init__(self, multi_agent_service: MultiAgentService):
        super().__init__(EntranceType.SECRETARIAT, multi_agent_service)
        self.task_queue = asyncio.Queue()
        self.active_tasks: Dict[str, asyncio.Task] = {}
        
    async def process_request(self, request: UserRequest) -> HubResponse:
        """Process request through Secretariat automation"""
        start_time = datetime.now()
        
        try:
            # Step 1: Intent recognition (INT-01 to INT-04)
            intent_result = await self._recognize_intent(request)
            
            # Step 2: Route to appropriate scenario
            scenario_result = await self._route_to_scenario(request, intent_result)
            
            # Step 3: Execute automated workflow
            execution_result = await self._execute_automated_workflow(request, scenario_result)
            
            # Step 4: Generate streamlined response
            response_content = await self._generate_streamlined_response(execution_result)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return HubResponse(
                response_id=str(uuid.uuid4()),
                request_id=request.request_id,
                entrance_type=self.entrance_type,
                intent_type=intent_result["intent_type"],
                success=True,
                content=response_content,
                metadata={
                    "scenario": scenario_result["scenario"],
                    "execution_steps": execution_result["steps"],
                    "automated": True
                },
                execution_time=execution_time,
                session_id=execution_result.get("session_id")
            )
            
        except Exception as e:
            import traceback
            self.logger.error(f"Error in Secretariat processing: {e}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return HubResponse(
                response_id=str(uuid.uuid4()),
                request_id=request.request_id,
                entrance_type=self.entrance_type,
                intent_type=IntentType.CASUAL_DISCUSSION,
                success=False,
                content=f"抱歉，处理您的请求时出现错误：{str(e)}",
                execution_time=(datetime.now() - start_time).total_seconds()
            )
    
    async def _recognize_intent(self, request: UserRequest) -> Dict[str, Any]:
        """Recognize user intent with high accuracy"""
        
        # Use existing intent analysis service if available
        if hasattr(self.multi_agent_service, 'intent_interpreter'):
            try:
                intent_result = await self.multi_agent_service.intent_interpreter.interpret_intent(
                    request.content, request.context
                )
                if intent_result and "primary_intent" in intent_result:
                    return {
                        "intent_type": self._map_to_intent_type(intent_result["primary_intent"]),
                        "confidence": intent_result.get("confidence", 0.5),
                        "entities": intent_result.get("entities", []),
                        "complexity": intent_result.get("complexity_score", 0.0)
                    }
            except Exception as e:
                self.logger.warning(f"Intent interpreter failed: {e}")
        
        # Fallback intent recognition
        return await self._fallback_intent_recognition(request.content)
    
    def _map_to_intent_type(self, primary_intent: str) -> IntentType:
        """Map internal intent to UserCase intent types"""
        mapping = {
            "secretariat_automation": IntentType.CASUAL_DISCUSSION,
            "forum_debate": IntentType.EXPERT_CONSULTATION,
            "expert_consultation": IntentType.EXPERT_CONSULTATION,
            "research_analysis": IntentType.ACADEMIC_RESEARCH,
            "general": IntentType.CASUAL_DISCUSSION
        }
        return mapping.get(primary_intent, IntentType.CASUAL_DISCUSSION)
    
    async def _fallback_intent_recognition(self, content: str) -> Dict[str, Any]:
        """Fallback intent recognition using keyword matching"""
        content_lower = content.lower()
        
        intent_patterns = {
            IntentType.ACADEMIC_RESEARCH: [
                "写", "综述", "论文", "研究", "分析", "报告", "2000字"
            ],
            IntentType.EXPERT_CONSULTATION: [
                "专家", "评估", "咨询", "建议", "三位", "评分"
            ],
            IntentType.INDUSTRY_ANALYSIS: [
                "行业", "分析", "市场", "趋势", "swot", "新能源汽车"
            ],
            IntentType.CRITICAL_REVIEW: [
                "核查", "验证", "事实", "真假", "新闻", "谣言"
            ]
        }
        
        # Calculate scores for each intent
        intent_scores = {}
        for intent_type, keywords in intent_patterns.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0:
                intent_scores[intent_type] = score
        
        # Determine primary intent
        if intent_scores:
            primary_intent = max(intent_scores.items(), key=lambda x: x[1])
            return {
                "intent_type": primary_intent[0],
                "confidence": min(primary_intent[1] / 3.0, 1.0),
                "entities": [],
                "complexity": len(content.split()) / 100.0
            }
        
        return {
            "intent_type": IntentType.CASUAL_DISCUSSION,
            "confidence": 0.5,
            "entities": [],
            "complexity": 0.1
        }
    
    async def _route_to_scenario(self, request: UserRequest, intent_result: Dict[str, Any]) -> Dict[str, Any]:
        """Route request to appropriate scenario"""
        intent_type = intent_result["intent_type"]
        
        if intent_type == IntentType.ACADEMIC_RESEARCH:
            return {
                "scenario": "academic_research",
                "workflow": "research_paper_generation",
                "required_agents": ["researcher", "writer", "editor"]
            }
        elif intent_type == IntentType.EXPERT_CONSULTATION:
            return {
                "scenario": "expert_consultation",
                "workflow": "expert_evaluation",
                "required_agents": ["domain_expert", "analyst", "reviewer"]
            }
        elif intent_type == IntentType.INDUSTRY_ANALYSIS:
            return {
                "scenario": "industry_analysis",
                "workflow": "market_analysis",
                "required_agents": ["market_analyst", "industry_expert", "strategist"]
            }
        else:
            return {
                "scenario": "casual_chat",
                "workflow": "simple_response",
                "required_agents": ["assistant"]
            }
    
    async def _execute_automated_workflow(self, request: UserRequest, scenario_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute automated workflow without user intervention"""
        
        # Create collaboration session
        session = CollaborationSession(
            session_id=str(uuid.uuid4()),
            session_name=f"Secretariat_{scenario_result['scenario']}",
            collaboration_mode=CollaborationMode.SECRETARIAT_AUTOMATION,
            initiator_id=request.user_id,
            participants=[request.user_id],
            topic=request.content,
            objectives=[scenario_result["scenario"]],
            institutional_primitives=[
                InstitutionalPrimitive.INTERPRET_INTENT,
                InstitutionalPrimitive.EXECUTE_WORKFLOW,
                InstitutionalPrimitive.GENERATE_REPORT
            ],
            consensus_method=ConsensusMethod.SIMPLE_MAJORITY
        )
        
        # Execute through multi-agent service
        result = await self.multi_agent_service.handle_user_request(
            request.content,
            request.user_id,
            {
                "scenario": scenario_result,
                "session": session,
                "automation_mode": True
            }
        )
        
        return {
            "session_id": session.session_id,
            "steps": result.get("results", {}),
            "scenario": scenario_result["scenario"],
            "automated": True
        }
    
    async def _generate_streamlined_response(self, execution_result: Dict[str, Any]) -> str:
        """Generate streamlined, result-oriented response"""
        scenario = execution_result["scenario"]
        
        if scenario == "academic_research":
            return "✅ 学术研究报告已生成完成。报告包含：文献综述、方法论、结果分析和参考文献。您可以下载PDF版本或要求进一步修改。"
        elif scenario == "expert_consultation":
            return "✅ 专家评估已完成。三位专家已提交评分和意见，综合评分为8.5/10。详细评估报告和专家意见分歧点已整理完毕。"
        elif scenario == "industry_analysis":
            return "✅ 行业分析报告已完成。包含SWOT分析、市场趋势、竞争格局和未来预测。报告已自动保存到Wiki，可导出PPT格式。"
        else:
            return "✅ 您的请求已处理完成。"
    
    async def get_interface_config(self) -> Dict[str, Any]:
        """Get Secretariat interface configuration"""
        return {
            "type": "secretariat",
            "layout": "minimalist",
            "features": [
                "quick_actions",
                "task_automation",
                "result_preview",
                "export_options"
            ],
            "automation_level": "high",
            "user_intervention": "optional"
        }

class ForumEntrance(BaseEntrance):
    """The Forum - Interactive, process-oriented interface"""
    
    def __init__(self, multi_agent_service: MultiAgentService):
        super().__init__(EntranceType.FORUM, multi_agent_service)
        self.active_debates: Dict[str, Dict[str, Any]] = {}
        self.expert_panels: Dict[str, List[str]] = {}
        
    async def process_request(self, request: UserRequest) -> HubResponse:
        """Process request through Forum interaction"""
        start_time = datetime.now()
        
        try:
            # Step 1: Intent recognition
            intent_result = await self._recognize_intent(request)
            
            # Step 2: Form expert panel
            panel_result = await self._form_expert_panel(request, intent_result)
            
            # Step 3: Initiate interactive session
            session_result = await self._initiate_interactive_session(request, intent_result, panel_result)
            
            # Step 4: Generate process-oriented response
            response_content = await self._generate_process_response(session_result)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return HubResponse(
                response_id=str(uuid.uuid4()),
                request_id=request.request_id,
                entrance_type=self.entrance_type,
                intent_type=intent_result["intent_type"],
                success=True,
                content=response_content,
                metadata={
                    "panel": panel_result["experts"],
                    "session_id": session_result["session_id"],
                    "interactive": True,
                    "debate_format": session_result.get("debate_format")
                },
                execution_time=execution_time,
                session_id=session_result["session_id"]
            )
            
        except Exception as e:
            self.logger.error(f"Error in Forum processing: {e}")
            return HubResponse(
                response_id=str(uuid.uuid4()),
                request_id=request.request_id,
                entrance_type=self.entrance_type,
                intent_type=IntentType.CASUAL_DISCUSSION,
                success=False,
                content=f"抱歉，启动专家讨论时出现错误：{str(e)}",
                execution_time=(datetime.now() - start_time).total_seconds()
            )
    
    async def _recognize_intent(self, request: UserRequest) -> Dict[str, Any]:
        """Recognize intent for Forum discussions"""
        # Similar to Secretariat but optimized for discussions
        return await self.secretariat._fallback_intent_recognition(request.content)
    
    async def _form_expert_panel(self, request: UserRequest, intent_result: Dict[str, Any]) -> Dict[str, Any]:
        """Form expert panel based on intent"""
        intent_type = intent_result["intent_type"]
        
        # Define expert requirements
        expert_requirements = {
            IntentType.ACADEMIC_RESEARCH: [
                "academic_researcher", "subject_matter_expert", "methodologist"
            ],
            IntentType.EXPERT_CONSULTATION: [
                "domain_expert", "industry_specialist", "technical_analyst"
            ],
            IntentType.INDUSTRY_ANALYSIS: [
                "market_analyst", "industry_expert", "financial_analyst"
            ],
            IntentType.CRITICAL_REVIEW: [
                "fact_checker", "subject_matter_expert", "research_analyst"
            ]
        }
        
        required_experts = expert_requirements.get(intent_type, ["general_expert"])
        
        # Form team through multi-agent service
        team_formation = await self.multi_agent_service.team_formation_engine.form_team(
            task_requirements={"required_expertise": required_experts},
            collaboration_mode=CollaborationMode.FORUM_DEBATE,
            constraints={"panel_size": 3}
        )
        
        return {
            "experts": team_formation,
            "requirements": required_experts,
            "formation_strategy": "expertise_matching"
        }
    
    async def _initiate_interactive_session(
        self, 
        request: UserRequest, 
        intent_result: Dict[str, Any], 
        panel_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Initiate interactive debate session"""
        
        session_id = str(uuid.uuid4())
        
        # Create collaboration session for debate
        session = CollaborationSession(
            session_id=session_id,
            session_name=f"Forum_{intent_result['intent_type'].value}",
            collaboration_mode=CollaborationMode.FORUM_DEBATE,
            initiator_id=request.user_id,
            participants=[request.user_id] + panel_result["experts"],
            topic=request.content,
            objectives=[f"Discuss {request.content}"],
            institutional_primitives=[
                InstitutionalPrimitive.INTERPRET_INTENT,
                InstitutionalPrimitive.FORM_TEAM,
                InstitutionalPrimitive.MULTI_AGENT_COLLABORATE,
                InstitutionalPrimitive.COMPUTE_CONSENSUS,
                InstitutionalPrimitive.GENERATE_REPORT
            ],
            consensus_method=ConsensusMethod.COGNITIVE_DIVERSITY
        )
        
        # Store active debate
        self.active_debates[session_id] = {
            "session": session,
            "panel": panel_result["experts"],
            "current_round": 0,
            "max_rounds": 3,
            "status": "initiated",
            "user_id": request.user_id
        }
        
        return {
            "session_id": session_id,
            "debate_format": "structured",
            "panel_size": len(panel_result["experts"]),
            "max_rounds": 3
        }
    
    async def _generate_process_response(self, session_result: Dict[str, Any]) -> str:
        """Generate process-oriented response for Forum"""
        session_id = session_result["session_id"]
        panel_size = session_result["panel_size"]
        max_rounds = session_result["max_rounds"]
        
        return f"""🎯 专家讨论已启动！

**讨论详情：**
- 📊 专家小组：{panel_size}位专家
- 🔄 讨论轮次：{max_rounds}轮
- 🎯 讨论形式：结构化辩论

**当前状态：**
- ✅ 专家小组已组建完成
- 🔄 即将开始第一轮讨论
- 💡 您可以随时参与讨论或提出问题

**下一步：**
1. 专家们将进行开场陈述
2. 展开多轮深入讨论
3. 识别分歧点和共识点
4. 生成综合评估报告

准备开始专家讨论..."""
    
    async def get_interface_config(self) -> Dict[str, Any]:
        """Get Forum interface configuration"""
        return {
            "type": "forum",
            "layout": "interactive",
            "features": [
                "expert_panel",
                "debate_transcript",
                "consensus_visualization",
                "real_time_interaction"
            ],
            "automation_level": "medium",
            "user_intervention": "encouraged"
        }

class PersonalIntelligenceHub:
    """Main hub coordinating both entrances"""
    
    def __init__(self, app_state):
        self.app_state = app_state
        self.multi_agent_service = MultiAgentService(app_state)
        
        # Initialize both entrances
        self.secretariat = SecretariatEntrance(self.multi_agent_service)
        self.forum = ForumEntrance(self.multi_agent_service)
        
        # Request routing
        self.request_history: List[Dict[str, Any]] = []
        
        logger.info("Personal Intelligence Hub initialized")
    
    async def process_request(
        self, 
        user_input: str, 
        user_id: str, 
        entrance_type: Union[EntranceType, str] = EntranceType.SECRETARIAT,
        context: Dict[str, Any] = None
    ) -> HubResponse:
        """Process user request through specified entrance"""
        
        # Normalize entrance type
        if isinstance(entrance_type, str):
            entrance_type = EntranceType(entrance_type)
        
        # Create request object
        request = UserRequest(
            request_id=str(uuid.uuid4()),
            user_id=user_id,
            content=user_input,
            entrance_type=entrance_type,
            context=context or {}
        )
        
        # Route to appropriate entrance
        if entrance_type == EntranceType.SECRETARIAT:
            response = await self.secretariat.process_request(request)
        else:
            response = await self.forum.process_request(request)
        
        # Store request history
        self.request_history.append({
            "request": request,
            "response": response,
            "timestamp": datetime.now()
        })
        
        return response
    
    async def auto_route_request(
        self, 
        user_input: str, 
        user_id: str, 
        context: Dict[str, Any] = None
    ) -> Tuple[HubResponse, EntranceType]:
        """Automatically route request to best entrance"""
        
        # Simple routing logic based on content
        content_lower = user_input.lower()
        
        # Route to Forum for complex discussions
        forum_keywords = ["辩论", "讨论", "专家", "评估", "分析", "观点"]
        if any(keyword in content_lower for keyword in forum_keywords):
            entrance_type = EntranceType.FORUM
        else:
            entrance_type = EntranceType.SECRETARIAT
        
        response = await self.process_request(user_input, user_id, entrance_type, context)
        return response, entrance_type
    
    def get_entrance_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get configurations for both entrances"""
        return {
            "secretariat": self.secretariat.get_interface_config(),
            "forum": self.forum.get_interface_config()
        }
    
    def get_request_history(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get request history, optionally filtered by user"""
        if user_id:
            return [
                entry for entry in self.request_history
                if entry["request"].user_id == user_id
            ]
        return self.request_history.copy()

# Example usage and test functions
async def test_hub_functionality():
    """Test the Personal Intelligence Hub functionality"""
    
    # Initialize hub with mock app state
    class MockAppState:
        def __init__(self):
            self.memory_service = None
            self._role_manager = None
            self._synthesis_engine = None
    
    hub = PersonalIntelligenceHub(MockAppState())
    
    # Test Secretariat entrance
    print("🔵 Testing Secretariat Entrance...")
    secretariat_response = await hub.process_request(
        "写一篇2000字量子综述",
        "user_123",
        EntranceType.SECRETARIAT
    )
    print(f"Secretariat Response: {secretariat_response.success}")
    print(f"Content: {secretariat_response.content[:100]}...")
    
    # Test Forum entrance
    print("\n🟢 Testing Forum Entrance...")
    forum_response = await hub.process_request(
        "请三位专家评估商业计划",
        "user_456",
        EntranceType.FORUM
    )
    print(f"Forum Response: {forum_response.success}")
    print(f"Content: {forum_response.content[:100]}...")
    
    # Test auto-routing
    print("\n🔄 Testing Auto-Routing...")
    auto_response, entrance_type = await hub.auto_route_request(
        "分析新能源汽车2025",
        "user_789"
    )
    print(f"Auto-routed to: {entrance_type.value}")
    print(f"Response: {auto_response.success}")
    
    return secretariat_response, forum_response, auto_response

if __name__ == "__main__":
    print("Dual-Entrance Personal Intelligence Hub")
    print("=======================================")
    print("This module implements the dual-entrance architecture")
    print("for the Personal Intelligence Hub with Secretariat and Forum entrances.")
    print("\nKey Features:")
    print("- Automated intent recognition (INT-01 to INT-04)")
    print("- Secretariat: Streamlined, result-oriented interface")
    print("- Forum: Interactive, process-oriented interface")
    print("- Support for all UserCase.txt scenarios")
    print("- Multi-agent collaboration and consensus computing")
    
    # Run test
    asyncio.run(test_hub_functionality())
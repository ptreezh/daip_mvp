import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.api.dependencies import AppStateDep

# TODO: These modules need to be implemented or removed
# from src.blockchain_consensus import ConsensusAlgorithm
# from src.cognitive_conflict_gan import ConflictIntensity

router = APIRouter(
    prefix="/advanced",
    tags=["Advanced Engines"],
)

logger = logging.getLogger(__name__)


@router.post("/consensus/create_session")
async def create_consensus_session(
    state: AppStateDep, session_id: str, algorithm: str = "proof_of_authority"
):
    """Create a new blockchain consensus session."""
    # TODO: Implement blockchain consensus functionality
    logger.warning("Blockchain consensus functionality not yet implemented")
    return {"success": False, "message": "Blockchain consensus functionality not yet implemented"}


@router.post("/shor_decomposer/decompose")
async def decompose_task(state: AppStateDep, task_description: str):
    """Decompose a complex task using the Shor-inspired decomposer."""
    # TODO: Implement Shor task decomposer functionality
    logger.warning("Shor task decomposer functionality not yet implemented")
    return {"success": False, "message": "Shor task decomposer functionality not yet implemented"}


@router.post("/cognitive_gan/generate_conflict")
async def generate_cognitive_conflict(
    state: AppStateDep, session_id: str, context: dict, primary_concept: str
):
    """Generate a cognitive conflict using the GAN engine."""
    # TODO: Implement cognitive conflict GAN functionality
    logger.warning("Cognitive conflict GAN functionality not yet implemented")
    return {"success": False, "message": "Cognitive conflict GAN functionality not yet implemented"}


class IntentAnalysisRequest(BaseModel):
    user_input: str
    user_id: str
    context: Optional[list] = None

@router.post("/analyze-intent")
async def analyze_intent(state: AppStateDep, request: IntentAnalysisRequest):
    """Analyze user intent for workflow selection using LLM."""
    try:
        # Use LLM for intelligent intent analysis
        interaction_manager = state.interaction_manager
        
        # Construct LLM prompt for natural language analysis
        prompt = f"""请分析以下用户输入，判断最适合的处理方式：

用户输入："{request.user_input}"

请从以下角度分析：
1. 用户的主要意图是什么？
2. 这个任务需要什么样的处理方式？
3. 这属于什么类型的场景？

分析要点：
- 如果用户需要审查、评估、检查、验证、分析风险或问题，通常需要批判性分析
- 如果用户需要讨论、收集观点、多角度分析、综合考虑，通常需要多视角综合
- 学术研究类内容（研究、探讨、理论）通常适合多视角分析
- 专家咨询类内容（寻求建议、解决方案）通常适合批判性分析
- 轻松讨论类内容（聊天、分享、交流）通常适合多视角分析

请用自然语言详细分析，说明你的判断理由。"""

        try:
            # Call LLM for analysis using InteractionManager
            messages = [
                {"role": "system", "content": "你是一个智能工作流选择助手。请用自然语言详细分析用户输入。"},
                {"role": "user", "content": prompt}
            ]
            
            response = await interaction_manager.client.chat(
                model=interaction_manager.model,
                messages=messages
            )
            llm_response = response.get("message", {}).get("content", "").strip()
            
            # Use NLP analysis to extract workflow decision from LLM response
            analysis_result = _analyze_llm_response(llm_response, request.user_input)
            
            return {
                "workflow_type": analysis_result["workflow_type"],
                "confidence": analysis_result["confidence"],
                "reasoning": f"LLM分析: {analysis_result['reasoning']}",
                "topic": request.user_input,
                "scenario": analysis_result["scenario"],
                "llm_analysis": llm_response[:200] + "..." if len(llm_response) > 200 else llm_response
            }
            
            # Clean LLM response by removing common output formats
            cleaned_response = llm_response
            # Remove <think> tags and content
            cleaned_response = re.sub(r'<think>.*?</think>', '', cleaned_response, flags=re.DOTALL)
            # Remove other common tags
            cleaned_response = re.sub(r'</?[^>]+>', '', cleaned_response)
            # Remove extra whitespace
            cleaned_response = cleaned_response.strip()
            
            # Extract JSON from cleaned response
            json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                
                # Validate and normalize result
                workflow_type = result.get("workflow_type", "critical_review")
                if workflow_type not in ["critical_review", "multi_perspective"]:
                    workflow_type = "critical_review"
                
                confidence = float(result.get("confidence", 0.7))
                confidence = max(0.0, min(1.0, confidence))  # Clamp to [0,1]
                
                reasoning = result.get("reasoning", "基于LLM分析的结果")
                scenario = result.get("scenario", "unknown")
                
                return {
                    "workflow_type": workflow_type,
                    "confidence": confidence,
                    "reasoning": f"LLM分析: {reasoning}",
                    "topic": request.user_input,
                    "scenario": scenario
                }
            else:
                raise ValueError("无法解析LLM响应中的JSON")
                
        except Exception as llm_error:
            logger.warning(f"LLM intent analysis failed: {llm_error}, falling back to keyword analysis")
            
            # Fallback to enhanced keyword analysis
            return await _enhanced_keyword_analysis(request.user_input)
        
    except Exception as e:
        logger.error(f"Intent analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Intent analysis failed: {str(e)}")


def _analyze_llm_response(llm_response: str, user_input: str) -> dict:
    """基于NLP和正则表达式分析LLM的自然语言响应"""
    import re
    
    response_lower = llm_response.lower()
    
    # 工作流类型识别模式
    critical_indicators = [
        r"批判性?[分析审查评估]",
        r"需要[审查检查验证评估]",
        r"适合.*批判",
        r"critical.*review",
        r"风险.*分析",
        r"问题.*检查",
        r"评估.*可行性"
    ]
    
    multi_indicators = [
        r"多视角|多角度",
        r"需要.*讨论",
        r"收集.*观点",
        r"适合.*多视角",
        r"multi.*perspective",
        r"综合.*考虑",
        r"不同.*角度"
    ]
    
    # 场景识别模式
    scenario_patterns = {
        "academic_research": [
            r"学术.*研究", r"理论.*分析", r"研究.*内容",
            r"探讨.*理论", r"学术.*性质", r"研究.*类型"
        ],
        "expert_consultation": [
            r"专家.*咨询", r"寻求.*建议", r"解决.*方案",
            r"专业.*指导", r"咨询.*类型", r"建议.*导向"
        ],
        "casual_discussion": [
            r"轻松.*讨论", r"聊天.*分享", r"交流.*体验",
            r"日常.*对话", r"社交.*互动", r"休闲.*话题"
        ]
    }
    
    # 计算工作流得分
    critical_score = sum(1 for pattern in critical_indicators if re.search(pattern, response_lower))
    multi_score = sum(1 for pattern in multi_indicators if re.search(pattern, response_lower))
    
    # 计算场景得分
    scenario_scores = {}
    for scenario, patterns in scenario_patterns.items():
        score = sum(1 for pattern in patterns if re.search(pattern, response_lower))
        scenario_scores[scenario] = score
    
    # 确定最佳场景
    best_scenario = max(scenario_scores, key=scenario_scores.get) if max(scenario_scores.values()) > 0 else "unknown"
    
    # 基于用户输入的补充分析
    user_input_lower = user_input.lower()
    
    # 用户输入中的关键词加权
    if any(word in user_input_lower for word in ["分析", "审查", "评估", "检查", "验证"]):
        critical_score += 1
    if any(word in user_input_lower for word in ["讨论", "观点", "角度", "看法", "综合"]):
        multi_score += 1
    
    # 基于场景的偏好调整
    if best_scenario == "academic_research":
        multi_score += 0.5  # 学术研究倾向多视角
    elif best_scenario == "expert_consultation":
        critical_score += 0.5  # 专家咨询倾向批判性
    elif best_scenario == "casual_discussion":
        multi_score += 0.5  # 轻松讨论倾向多视角
    
    # 决策逻辑
    if critical_score > multi_score:
        workflow_type = "critical_review"
        confidence = min(0.95, 0.6 + critical_score * 0.1)
        reasoning = f"LLM分析倾向批判性审查 (批判性指标: {critical_score}, 多视角指标: {multi_score})"
    elif multi_score > critical_score:
        workflow_type = "multi_perspective"
        confidence = min(0.95, 0.6 + multi_score * 0.1)
        reasoning = f"LLM分析倾向多视角综合 (多视角指标: {multi_score}, 批判性指标: {critical_score})"
    else:
        # 平分时基于场景决定
        if best_scenario == "expert_consultation":
            workflow_type = "critical_review"
            confidence = 0.7
            reasoning = f"基于{best_scenario}场景的默认选择"
        else:
            workflow_type = "multi_perspective"
            confidence = 0.7
            reasoning = f"基于{best_scenario}场景的默认选择"
    
    return {
        "workflow_type": workflow_type,
        "confidence": confidence,
        "reasoning": reasoning,
        "scenario": best_scenario
    }


async def _enhanced_keyword_analysis(user_input: str) -> dict:
    """Enhanced keyword-based fallback analysis."""
    user_input_lower = user_input.lower()
    
    # Enhanced keyword patterns
    critical_patterns = {
        "审查类": ["审查", "检查", "验证", "评估", "分析风险", "可行性"],
        "问题类": ["问题", "错误", "漏洞", "缺陷", "不足"],
        "评价类": ["评价", "判断", "准确性", "可靠性", "有效性"]
    }
    
    multi_patterns = {
        "讨论类": ["讨论", "聊聊", "谈谈", "交流"],
        "观点类": ["观点", "看法", "意见", "角度", "视角"],
        "综合类": ["综合", "多方面", "各种", "不同角度"]
    }
    
    scenario_patterns = {
        "academic_research": ["研究", "探讨", "理论", "学术", "分析.*前景", "发展趋势"],
        "expert_consultation": ["建议", "推荐", "如何", "应该", "选择什么", "注意.*风险"],
        "casual_discussion": ["大家", "聊聊", "分享", "有趣", "经历", "推荐.*好"]
    }
    
    # Calculate scores
    critical_score = 0
    multi_score = 0
    
    for category, keywords in critical_patterns.items():
        matches = sum(1 for kw in keywords if kw in user_input_lower)
        critical_score += matches
    
    for category, keywords in multi_patterns.items():
        matches = sum(1 for kw in keywords if kw in user_input_lower)
        multi_score += matches
    
    # Determine scenario
    scenario_scores = {}
    for scenario, keywords in scenario_patterns.items():
        score = sum(1 for kw in keywords if kw in user_input_lower)
        scenario_scores[scenario] = score
    
    best_scenario = max(scenario_scores, key=scenario_scores.get) if max(scenario_scores.values()) > 0 else "unknown"
    
    # Apply scenario bias
    if best_scenario == "academic_research":
        multi_score += 1  # Academic research tends to be multi-perspective
    elif best_scenario == "expert_consultation":
        critical_score += 1  # Expert consultation tends to be critical review
    elif best_scenario == "casual_discussion":
        multi_score += 1  # Casual discussion tends to be multi-perspective
    
    # Make decision
    if critical_score > multi_score and critical_score > 0:
        workflow_type = "critical_review"
        confidence = min(0.9, 0.6 + critical_score * 0.1)
        reasoning = f"增强关键词分析: 检测到{critical_score}个批判性审查指标，场景: {best_scenario}"
    elif multi_score > 0:
        workflow_type = "multi_perspective"
        confidence = min(0.9, 0.6 + multi_score * 0.1)
        reasoning = f"增强关键词分析: 检测到{multi_score}个多视角指标，场景: {best_scenario}"
    else:
        # Default based on scenario
        if best_scenario == "expert_consultation":
            workflow_type = "critical_review"
            confidence = 0.6
        else:
            workflow_type = "multi_perspective"
            confidence = 0.6
        reasoning = f"增强关键词分析: 基于场景{best_scenario}的默认选择"
    
    return {
        "workflow_type": workflow_type,
        "confidence": confidence,
        "reasoning": reasoning,
        "topic": user_input,
        "scenario": best_scenario
    }
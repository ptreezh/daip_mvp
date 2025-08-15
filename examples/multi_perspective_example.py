"""@Time    : 2025-07-24 16:00:00
@Author  : DAIP-LIVE Team
@File    : multi_perspective_example.py
@Description:
    Example script demonstrating the use of the Multi-perspective Synthesis Workflow.
"""
import asyncio
import logging
from typing import Any

from src.core_services.llm_interface import EnhancedLLMInterface
from src.core_services.role_manager import RoleManager
from src.core_services.synthesis_engine import SynthesisEngine
from src.kernel.tool_executor import ToolExecutor
from src.workflows.multi_perspective_workflow import MultiPerspectiveSynthesisWorkflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def setup_services() -> dict[str, Any]:
    """Set up and initialize required services.
    
    Returns:
        Dictionary of service instances
    """
    # Initialize services
    llm_interface = EnhancedLLMInterface()
    role_manager = RoleManager()
    tool_executor = ToolExecutor()
    synthesis_engine = SynthesisEngine(llm_interface)
    
    # Register research tool
    tool_executor.register_tool(
        tool_func=research_tool,
        definition={
            "function": {
                "name": "research",
                "description": "Searches for information on a topic from a specific perspective",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "The topic to research"
                        },
                        "perspective": {
                            "type": "string",
                            "description": "The perspective to research from"
                        },
                        "questions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific questions to research"
                        }
                    },
                    "required": ["topic"]
                }
            }
        }
    )
    
    # Return services dictionary
    return {
        "llm_interface": llm_interface,
        "role_manager": role_manager,
        "tool_executor": tool_executor,
        "synthesis_engine": synthesis_engine
    }


def research_tool(topic: str, perspective: str = None, questions: list[str] = None) -> str:
    """Simulated research tool that would normally fetch information from external sources.
    
    Args:
        topic: The topic to research
        perspective: The perspective to research from
        questions: Specific questions to research
        
    Returns:
        Research results
    """
    # In a real implementation, this would fetch information from external sources
    # For this example, we'll return simulated research results
    
    if "AI" in topic and perspective == "经济":
        return """根据最新研究，AI对就业市场的经济影响包括：
1. 短期内，自动化可能导致某些行业就业减少，特别是重复性工作
2. 长期来看，AI预计将创造新的就业机会，但需要不同的技能集
3. 2023年研究表明，AI可能导致全球15-30%的工作发生重大变化
4. 高技能工作和创造性工作受到的影响较小，而中等技能的常规工作受影响最大"""
    
    elif "AI" in topic and perspective == "社会":
        return """社会学研究表明，AI对社会结构的影响包括：
1. 技术采用不平等可能加剧现有的社会分层
2. 需要新的社会政策来确保AI带来的利益公平分配
3. 教育系统需要适应以培养AI时代所需的新技能
4. 社区和社会关系可能因远程工作和数字化互动增加而改变"""
    
    elif "AI" in topic and perspective == "技术":
        return """技术发展趋势显示：
1. 大型语言模型正在迅速发展，能力不断提升
2. AI与机器人技术的结合正在加速物理世界的自动化
3. 边缘AI使设备能够在本地处理数据，减少对云的依赖
4. 可解释AI研究正在进步，使AI决策过程更加透明"""
    
    elif "AI" in topic and perspective == "伦理":
        return """伦理学研究关注：
1. AI决策的公平性和偏见问题
2. 人类工作的内在价值与尊严
3. 技术发展与人类福祉的平衡
4. 对AI系统的监管和问责机制"""
    
    else:
        return f"关于'{topic}'的研究结果（{perspective if perspective else '一般视角'}）：\n暂无具体研究数据。"


async def run_multi_perspective_example():
    """Run a complete Multi-perspective Synthesis Workflow example."""
    logger.info("Setting up services...")
    services = await setup_services()
    
    # Configure workflow
    workflow_config = {
        "task_decomposition": {
            "planner_role": "规划者",
            "default_perspectives": ["经济", "社会", "技术", "伦理"],
            "max_sub_problems": 4
        },
        "parallel_exploration": {
            "max_parallel_experts": 4,
            "expert_roles": {
                "economist": ["经济学", "劳动经济学", "宏观经济学"],
                "sociologist": ["社会学", "公共政策", "社会心理学"],
                "technologist": ["计算机科学", "AI研究", "机器学习"],
                "ethicist": ["伦理学", "哲学", "价值观研究"]
            },
            "default_expert_role": "专家",
            "use_tools": True
        },
        "viewpoint_collection": {
            "min_viewpoints": 3,
            "conflict_threshold": 0.3,
            "consensus_threshold": 0.7,
            "analyze_coverage": True
        },
        "enhanced_synthesis": {
            "synthesis_method": "dialectical",
            "min_confidence_threshold": 0.7,
            "include_expert_attribution": True,
            "quality_threshold": 0.75
        },
        "iterative_refinement": {
            "max_iterations": 2,
            "quality_threshold": 0.8,
            "improvement_threshold": 0.1,
            "refinement_strategies": ["depth", "breadth", "insight"]
        }
    }
    
    # Create topic
    topic = "AI对未来工作的影响"
    perspectives = ["经济", "社会", "技术", "伦理"]
    
    logger.info("Creating Multi-perspective Synthesis Workflow...")
    workflow = MultiPerspectiveSynthesisWorkflow("ai_work_impact", workflow_config)
    
    logger.info("Executing Multi-perspective Synthesis Workflow...")
    result = await workflow.execute(topic, perspectives, services)
    
    if result["success"]:
        logger.info("Workflow completed successfully!")
        
        logger.info("\n=== Topic ===\n")
        logger.info(result["topic"])
        
        logger.info("\n=== Perspectives ===\n")
        logger.info(", ".join(result["perspectives"]))
        
        logger.info("\n=== Synthesis ===\n")
        logger.info(result["synthesis"])
        
        logger.info("\n=== Key Insights ===\n")
        for i, insight in enumerate(result["key_insights"]):
            logger.info(f"{i+1}. {insight}")
        
        logger.info("\n=== Expert Contributions ===\n")
        for expert, contributions in result["expert_contributions"].items():
            logger.info(f"{expert}:")
            for contribution in contributions:
                logger.info(f"  - {contribution}")
        
        logger.info("\n=== Quality Assessment ===\n")
        logger.info(f"Overall confidence: {result['confidence']:.2f}")
        logger.info(f"Quality score: {result.get('quality_score', 0.0):.2f}")
        
        if result.get("refinement_applied", False):
            logger.info(f"Refinement applied: {result['refinement_iterations']} iterations")
        
        logger.info("\n=== Viewpoint Analysis ===\n")
        viewpoint_analysis = result.get("viewpoint_analysis", {})
        if viewpoint_analysis:
            logger.info(f"Conflicts identified: {len(viewpoint_analysis.get('conflicts', []))}")
            logger.info(f"Consensus areas: {len(viewpoint_analysis.get('consensus_areas', []))}")
            logger.info(f"Collection quality: {viewpoint_analysis.get('quality_score', 0.0):.2f}")
        
        logger.info("\n=== Sub-problems ===\n")
        for i, sub_problem in enumerate(result["sub_problems"]):
            logger.info(f"{i+1}. {sub_problem['perspective']}: {sub_problem['description']}")
    else:
        logger.error(f"Workflow failed: {result['error']}")
        if "error_details" in result:
            logger.error(f"Error details: {result['error_details']}")


if __name__ == "__main__":
    asyncio.run(run_multi_perspective_example())
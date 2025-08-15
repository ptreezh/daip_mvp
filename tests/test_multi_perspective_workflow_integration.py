"""@Time    : 2025-07-24 17:00:00
@Author  : DAIP-LIVE Team
@File    : test_multi_perspective_workflow_integration.py
@Description:
    Integration tests for the complete Multi-perspective Synthesis Workflow.
"""
from unittest.mock import AsyncMock, Mock

import pytest

from src.workflows.multi_perspective_workflow import MultiPerspectiveSynthesisWorkflow


class TestMultiPerspectiveWorkflowIntegration:
    """Integration tests for the complete Multi-perspective Synthesis Workflow."""
    
    @pytest.fixture()
    def mock_services(self):
        """Create mock services with realistic responses."""
        services = {
            "llm_interface": AsyncMock(),
            "role_manager": Mock(),
            "tool_executor": Mock(),
            "synthesis_engine": AsyncMock()
        }
        
        # Configure LLM interface for task decomposition
        async def llm_generate_side_effect(messages):
            content = messages[1]["content"]
            
            if "分解" in content and "主题" in content:
                return {
                    "content": """以下是对主题的分解：

```json
[
  {
    "perspective": "经济",
    "description": "分析AI对就业市场的经济影响",
    "questions": ["AI如何影响就业率?", "哪些行业最受影响?", "经济结构如何变化?"],
    "expertise_required": ["经济学", "劳动经济学"],
    "priority": 1
  },
  {
    "perspective": "社会",
    "description": "探讨AI对社会结构的影响",
    "questions": ["AI如何影响社会阶层?", "教育需求如何变化?"],
    "expertise_required": ["社会学", "公共政策"],
    "priority": 2
  },
  {
    "perspective": "技术",
    "description": "分析AI技术发展趋势",
    "questions": ["哪些AI技术最重要?", "技术发展方向如何?"],
    "expertise_required": ["计算机科学", "AI研究"],
    "priority": 1
  }
]
```"""
                }
            elif "经济" in content:
                return {
                    "content": """```json
{
  "viewpoint": "AI将导致短期就业市场波动，但长期将创造新的就业机会。自动化将替代重复性工作，但同时催生新的职业类型。",
  "supporting_evidence": ["历史技术革命数据显示类似模式", "麦肯锡研究预测AI将创造更多工作岗位", "新兴AI相关职业快速增长"],
  "reasoning_process": "基于历史技术革命的经济影响分析，结合当前AI技术发展趋势和就业市场数据进行推理。",
  "confidence": 0.8
}
```"""
                }
            elif "社会" in content:
                return {
                    "content": """```json
{
  "viewpoint": "AI可能加剧社会不平等，需要政策干预确保技术红利公平分配。教育体系需要根本性改革以适应AI时代。",
  "supporting_evidence": ["技术采用存在数字鸿沟", "高技能工作者受益更多", "教育资源分配不均"],
  "reasoning_process": "通过社会分层理论和技术扩散模型分析AI对不同社会群体的差异化影响。",
  "confidence": 0.75
}
```"""
                }
            elif "技术" in content:
                return {
                    "content": """```json
{
  "viewpoint": "AI技术正在快速发展，大语言模型和多模态AI将成为主导技术。边缘计算和AI芯片发展将推动技术普及。",
  "supporting_evidence": ["GPT等大模型性能快速提升", "AI芯片市场快速增长", "边缘AI应用场景扩展"],
  "reasoning_process": "基于技术发展曲线和市场趋势分析，结合产业投资和研发动向进行预测。",
  "confidence": 0.85
}
```"""
                }
            elif "改进" in content or "refinement" in content.lower():
                return {
                    "content": "建议从以下方面改进分析：1. 增加更多具体数据支撑 2. 深入探讨技术实现机制 3. 提供更详细的政策建议"
                }
            else:
                return {"content": "Generated response for testing"}
        
        services["llm_interface"].generate.side_effect = llm_generate_side_effect
        
        # Configure role manager
        def get_role_by_id_side_effect(role_id):
            role = Mock()
            if role_id == "规划者":
                role.system_prompt = "你是一位专业的任务分解专家。"
                role.name = "规划专家"
            elif "economist" in role_id or "经济" in role_id:
                role.system_prompt = "你是一位经济学专家。"
                role.name = "经济学家"
            elif "sociologist" in role_id or "社会" in role_id:
                role.system_prompt = "你是一位社会学专家。"
                role.name = "社会学家"
            elif "technologist" in role_id or "技术" in role_id:
                role.system_prompt = "你是一位技术专家。"
                role.name = "技术专家"
            else:
                role.system_prompt = "你是一位专业专家。"
                role.name = "专家"
            return role
        
        services["role_manager"].get_role_by_id.side_effect = get_role_by_id_side_effect
        
        # Configure tool executor
        services["tool_executor"].execute.return_value = {
            "status": "success",
            "result": "研究表明，AI对就业的影响因行业而异，需要综合考虑多个因素。"
        }
        
        # Configure synthesis engine
        services["synthesis_engine"].synthesize_opinions.return_value = """综合分析表明，AI对未来工作的影响是多维度的：

从经济角度看，AI将带来短期的就业结构调整，但长期将创造新的经济增长点和就业机会。自动化虽然会替代部分重复性工作，但历史经验表明技术进步最终会创造更多价值和就业。

从社会角度看，AI的普及可能加剧现有的社会不平等，特别是在技术获取和应用能力方面。这需要政策制定者采取积极措施，确保AI技术的红利能够公平分配给社会各阶层。

从技术角度看，AI技术的快速发展，特别是大语言模型和多模态AI的突破，正在重新定义工作的性质和要求。边缘计算和专用AI芯片的发展将使AI技术更加普及和实用。

关键洞察：
1. AI对工作的影响不是简单的替代关系，而是重新定义工作内容和价值创造方式
2. 教育和培训体系的改革是应对AI冲击的关键
3. 政策干预对于确保AI发展的社会效益最大化至关重要
4. 技术发展的速度要求我们必须前瞻性地规划和准备

总的来说，AI对未来工作的影响既带来挑战也蕴含机遇，关键在于如何通过教育、政策和技术创新来最大化其积极影响，同时减少负面冲击。"""
        
        return services
    
    @pytest.mark.asyncio()
    async def test_complete_workflow_execution(self, mock_services):
        """Test the complete workflow execution from start to finish."""
        # Create workflow
        workflow_config = {
            "task_decomposition": {
                "planner_role": "规划者",
                "default_perspectives": ["经济", "社会", "技术"],
                "max_sub_problems": 3
            },
            "parallel_exploration": {
                "max_parallel_experts": 3,
                "expert_roles": {
                    "economist": ["经济学", "劳动经济学"],
                    "sociologist": ["社会学", "公共政策"],
                    "technologist": ["计算机科学", "AI研究"]
                },
                "use_tools": True
            },
            "enhanced_synthesis": {
                "quality_threshold": 0.6  # Lower threshold for testing
            },
            "iterative_refinement": {
                "max_iterations": 2,
                "quality_threshold": 0.8
            }
        }
        
        workflow = MultiPerspectiveSynthesisWorkflow("test_workflow", workflow_config)
        
        # Execute workflow
        result = await workflow.execute(
            topic="AI对未来工作的影响",
            perspectives=["经济", "社会", "技术"],
            services=mock_services
        )
        
        # Verify overall success
        assert result["success"] is True
        assert result["topic"] == "AI对未来工作的影响"
        
        # Verify all steps were executed
        assert "execution_details" in result
        execution_details = result["execution_details"]
        
        # Check task decomposition
        assert "task_decomposition" in execution_details
        assert execution_details["task_decomposition"]["success"] is True
        assert execution_details["task_decomposition"]["sub_problem_count"] == 3
        
        # Check parallel exploration
        assert "parallel_exploration" in execution_details
        assert execution_details["parallel_exploration"]["success"] is True
        assert execution_details["parallel_exploration"]["viewpoint_count"] == 3
        
        # Check viewpoint collection
        assert "viewpoint_collection" in execution_details
        assert execution_details["viewpoint_collection"]["success"] is True
        
        # Check enhanced synthesis
        assert "enhanced_synthesis" in execution_details
        assert execution_details["enhanced_synthesis"]["success"] is True
        
        # Verify final results
        assert "synthesis" in result
        assert len(result["synthesis"]) > 100  # Should be substantial
        assert "key_insights" in result
        assert len(result["key_insights"]) > 0
        assert "expert_contributions" in result
        assert len(result["expert_contributions"]) > 0
        assert "confidence" in result
        assert 0.0 <= result["confidence"] <= 1.0
        
        # Verify perspectives were covered
        assert "perspectives" in result
        assert "经济" in result["perspectives"]
        assert "社会" in result["perspectives"]
        assert "技术" in result["perspectives"]
    
    @pytest.mark.asyncio()
    async def test_workflow_with_refinement(self, mock_services):
        """Test workflow execution that triggers refinement."""
        # Configure synthesis to need refinement
        original_synthesize = mock_services["synthesis_engine"].synthesize_opinions
        
        async def synthesize_with_low_quality(*args, **kwargs):
            if "改进版本" in kwargs.get("topic", ""):
                # Return improved synthesis for refinement
                return """经过改进的综合分析表明，AI对未来工作的影响具有深层次的复杂性：

从根本机制上看，AI技术正在重新定义价值创造的方式。传统的劳动密集型工作模式正在向知识密集型和创造性工作模式转变。这种转变不仅仅是技术替代，更是工作本质的重新定义。

深入分析显示，AI对不同行业的影响存在显著差异。制造业、金融服务业和客户服务行业面临较大的自动化压力，而创意产业、教育和医疗保健等需要人际互动和创造性思维的领域则相对安全。

关键洞察包括：
1. AI与人类的协作模式将成为未来工作的主流，而非简单的替代关系
2. 终身学习和技能更新将成为职业发展的必需品
3. 新的职业类型正在快速涌现，如AI训练师、算法审计师等
4. 政策制定需要平衡技术创新与社会稳定的关系

这种深度分析揭示了AI影响的多层次性和复杂性，为未来的政策制定和个人职业规划提供了重要参考。"""
            else:
                # Return low-quality synthesis that needs refinement
                return "AI会影响工作。有些工作会消失，有些会出现。需要学习新技能。"
        
        mock_services["synthesis_engine"].synthesize_opinions.side_effect = synthesize_with_low_quality
        
        workflow_config = {
            "enhanced_synthesis": {
                "quality_threshold": 0.8  # High threshold to trigger refinement
            },
            "iterative_refinement": {
                "max_iterations": 2,
                "quality_threshold": 0.7,
                "improvement_threshold": 0.05
            }
        }
        
        workflow = MultiPerspectiveSynthesisWorkflow("test_refinement", workflow_config)
        
        # Execute workflow
        result = await workflow.execute(
            topic="AI对未来工作的影响",
            services=mock_services
        )
        
        # Verify refinement was applied
        assert result["success"] is True
        assert result.get("refinement_applied", False) is True
        assert result.get("refinement_iterations", 0) > 0
        
        # Verify improved quality
        final_synthesis = result["synthesis"]
        assert len(final_synthesis) > 200  # Should be more substantial after refinement
        assert "深层次" in final_synthesis or "根本机制" in final_synthesis  # Should show depth improvement
    
    @pytest.mark.asyncio()
    async def test_workflow_error_handling(self, mock_services):
        """Test workflow error handling when a step fails."""
        # Make task decomposition fail
        mock_services["llm_interface"].generate.side_effect = Exception("LLM service unavailable")
        
        workflow = MultiPerspectiveSynthesisWorkflow("test_error")
        
        # Execute workflow
        result = await workflow.execute(
            topic="AI对未来工作的影响",
            services=mock_services
        )
        
        # Verify error handling
        assert result["success"] is False
        assert "error" in result
        assert "Task decomposition failed" in result["error"]
    
    @pytest.mark.asyncio()
    async def test_workflow_class_method(self, mock_services):
        """Test the convenience class method."""
        result = await MultiPerspectiveSynthesisWorkflow.execute_multi_perspective_synthesis(
            topic="AI对未来工作的影响",
            perspectives=["经济", "技术"],
            services=mock_services,
            workflow_config={
                "task_decomposition": {"max_sub_problems": 2}
            }
        )
        
        # Verify result
        assert result["success"] is True
        assert result["topic"] == "AI对未来工作的影响"
        assert len(result["perspectives"]) == 2


if __name__ == "__main__":
    pytest.main([__file__])
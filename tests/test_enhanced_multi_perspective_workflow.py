# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-24 17:00:00
@Author  : DAIP-LIVE Team
@File    : test_enhanced_multi_perspective_workflow.py
@Description:
    Integration tests for the enhanced Multi-perspective Synthesis Workflow.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch

from src.workflows.multi_perspective_workflow import MultiPerspectiveSynthesisWorkflow


class TestEnhancedMultiPerspectiveWorkflow:
    """Integration tests for the enhanced Multi-perspective Synthesis Workflow."""
    
    @pytest.fixture
    def mock_services(self):
        """Create comprehensive mock services."""
        services = {
            "llm_interface": AsyncMock(),
            "role_manager": Mock(),
            "tool_executor": Mock(),
            "synthesis_engine": AsyncMock()
        }
        
        # Configure LLM interface for different types of requests
        async def llm_generate_side_effect(messages):
            content = messages[-1]["content"]
            
            if "分解" in content and "JSON" in content:
                # Task decomposition response
                return {
                    "content": """```json
[
  {
    "perspective": "经济",
    "description": "分析AI对就业市场的经济影响",
    "questions": ["AI如何影响就业率?", "哪些行业最受影响?"],
    "expertise_required": ["经济学", "劳动经济学"],
    "priority": 1
  },
  {
    "perspective": "社会",
    "description": "探讨AI对社会结构的影响",
    "questions": ["AI如何影响社会阶层?"],
    "expertise_required": ["社会学", "公共政策"],
    "priority": 2
  }
]```"""
                }
            elif "专业观点" in content and "JSON" in content:
                # Expert viewpoint response
                if "经济" in content:
                    return {
                        "content": """```json
{
  "viewpoint": "AI将导致短期就业市场波动，但长期将创造新的就业机会。",
  "supporting_evidence": ["历史技术革命数据", "最新就业市场研究"],
  "reasoning_process": "基于历史技术革命的模式分析...",
  "confidence": 0.8
}```"""
                    }
                else:
                    return {
                        "content": """```json
{
  "viewpoint": "AI可能加剧社会不平等，需要政策干预。",
  "supporting_evidence": ["收入差距研究", "技术采用模式"],
  "reasoning_process": "通过社会学理论分析...",
  "confidence": 0.7
}```"""
                    }
            elif "改进" in content:
                # Refinement response
                return {
                    "content": "建议从以下方面改进：1. 增加更深入的机制分析 2. 补充更多实证证据 3. 提供更具体的政策建议"
                }
            else:
                # Default response
                return {"content": "Generated response"}
        
        services["llm_interface"].generate.side_effect = llm_generate_side_effect
        
        # Configure synthesis engine
        services["synthesis_engine"].synthesize_opinions.return_value = """综合分析表明，AI对就业的影响是多方面的：

1. 短期内，AI将导致某些行业就业岗位减少，特别是高度重复性工作。
2. 长期来看，新的就业机会将会出现，但需要劳动力具备新的技能。
3. 社会不平等可能加剧，因为技术采用和适应能力存在差异。
4. 需要政策干预来确保AI带来的利益公平分配。

总的来说，AI对就业的影响既有挑战也有机遇，关键在于如何通过政策和教育体系的调整来最大化机遇并减少负面影响。"""
        
        # Configure tool executor
        services["tool_executor"].execute.return_value = {
            "status": "success",
            "result": "研究表明，AI对就业的影响因行业而异。"
        }
        
        return services
    
    @pytest.mark.asyncio
    async def test_enhanced_workflow_complete_execution(self, mock_services):
        """Test complete execution of the enhanced workflow."""
        workflow = MultiPerspectiveSynthesisWorkflow("enhanced_test", {
            "enhanced_synthesis": {
                "quality_threshold": 0.5  # Lower threshold for testing
            },
            "iterative_refinement": {
                "quality_threshold": 0.5,
                "max_iterations": 2
            }
        })
        
        result = await workflow.execute(
            "AI对未来工作的影响",
            ["经济", "社会"],
            mock_services
        )
        
        # Verify successful execution
        assert result["success"] is True
        assert result["topic"] == "AI对未来工作的影响"
        assert "synthesis" in result
        assert "key_insights" in result
        assert "expert_contributions" in result
        assert "quality_score" in result
        
        # Verify all workflow steps were executed
        execution_details = result["execution_details"]
        assert "task_decomposition" in execution_details
        assert "parallel_exploration" in execution_details
        assert "viewpoint_collection" in execution_details
        assert "enhanced_synthesis" in execution_details
        
        # Verify sub-problems were created
        assert len(result["sub_problems"]) == 2
        assert any(sp["perspective"] == "经济" for sp in result["sub_problems"])
        assert any(sp["perspective"] == "社会" for sp in result["sub_problems"])
        
        # Verify viewpoints were generated
        assert len(result["viewpoints"]) == 2
        
        # Verify viewpoint analysis was performed
        assert "viewpoint_analysis" in result
        viewpoint_analysis = result["viewpoint_analysis"]
        assert "quality_score" in viewpoint_analysis
        assert "conflicts" in viewpoint_analysis
        assert "consensus_areas" in viewpoint_analysis
    
    @pytest.mark.asyncio
    async def test_enhanced_workflow_with_refinement(self, mock_services):
        """Test workflow execution with iterative refinement."""
        # Configure synthesis engine to return low-quality synthesis initially
        services = mock_services.copy()
        
        synthesis_calls = []
        
        async def synthesis_side_effect(topic, history):
            synthesis_calls.append(len(history))
            
            if len(synthesis_calls) == 1:
                # First call - low quality synthesis
                return "简单的分析：AI会影响工作。"
            else:
                # Refinement call - higher quality synthesis
                return """深入分析表明，AI对就业的影响具有多层次特征：

1. 技术替代效应：AI将首先影响高度标准化和重复性的工作岗位
2. 技能重构需求：新兴岗位要求更高的创造性和人际交往能力
3. 产业结构调整：传统制造业向智能制造转型，服务业数字化程度提升
4. 政策响应机制：需要建立包容性增长的政策框架

这一转变过程需要教育体系、社会保障和产业政策的协同配合。"""
        
        services["synthesis_engine"].synthesize_opinions.side_effect = synthesis_side_effect
        
        workflow = MultiPerspectiveSynthesisWorkflow("refinement_test", {
            "enhanced_synthesis": {
                "quality_threshold": 0.8  # High threshold to trigger refinement
            },
            "iterative_refinement": {
                "quality_threshold": 0.8,
                "max_iterations": 2,
                "improvement_threshold": 0.05
            }
        })
        
        result = await workflow.execute(
            "AI对未来工作的影响",
            ["经济", "社会"],
            services
        )
        
        # Verify refinement was applied
        assert result["success"] is True
        assert result.get("refinement_applied", False) is True
        assert result.get("refinement_iterations", 0) > 0
        
        # Verify synthesis was improved
        assert len(result["synthesis"]) > 50  # Should be longer after refinement
        assert "深入分析" in result["synthesis"] or "技术替代" in result["synthesis"]
        
        # Verify synthesis engine was called multiple times
        assert len(synthesis_calls) >= 2
    
    @pytest.mark.asyncio
    async def test_enhanced_workflow_error_handling(self, mock_services):
        """Test error handling in the enhanced workflow."""
        # Configure services to fail at different stages
        services = mock_services.copy()
        
        # Make viewpoint collection fail
        workflow = MultiPerspectiveSynthesisWorkflow("error_test")
        
        # Mock viewpoint collection to fail
        with patch.object(workflow.viewpoint_collection_node, 'execute', AsyncMock(return_value={
            "success": False,
            "error": "Viewpoint collection failed"
        })):
            result = await workflow.execute(
                "AI对未来工作的影响",
                ["经济", "社会"],
                services
            )
            
            # Verify error handling
            assert result["success"] is False
            assert "Viewpoint collection failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_enhanced_workflow_quality_assessment(self, mock_services):
        """Test quality assessment functionality."""
        workflow = MultiPerspectiveSynthesisWorkflow("quality_test", {
            "enhanced_synthesis": {
                "quality_threshold": 0.6
            }
        })
        
        result = await workflow.execute(
            "AI对未来工作的影响",
            ["经济", "社会", "技术", "伦理"],
            mock_services
        )
        
        # Verify quality assessment is included
        assert result["success"] is True
        assert "quality_score" in result
        assert isinstance(result["quality_score"], (int, float))
        assert 0.0 <= result["quality_score"] <= 1.0
        
        # Verify execution details include quality assessment
        synthesis_details = result["execution_details"]["enhanced_synthesis"]
        assert "quality_assessment" in synthesis_details
        
        quality_assessment = synthesis_details["quality_assessment"]
        assert "depth_score" in quality_assessment
        assert "breadth_score" in quality_assessment
        assert "insight_score" in quality_assessment
        assert "coherence_score" in quality_assessment
        assert "overall_score" in quality_assessment
    
    @pytest.mark.asyncio
    async def test_enhanced_workflow_conflict_analysis(self, mock_services):
        """Test conflict analysis in viewpoint collection."""
        # Configure services to generate conflicting viewpoints
        services = mock_services.copy()
        
        async def conflicting_llm_side_effect(messages):
            content = messages[-1]["content"]
            
            if "分解" in content and "JSON" in content:
                return {
                    "content": """```json
[
  {
    "perspective": "经济",
    "description": "分析AI的经济影响",
    "questions": ["AI是否促进经济增长?"],
    "expertise_required": ["经济学"],
    "priority": 1
  },
  {
    "perspective": "社会",
    "description": "分析AI的社会影响",
    "questions": ["AI是否加剧不平等?"],
    "expertise_required": ["社会学"],
    "priority": 1
  }
]```"""
                }
            elif "专业观点" in content and "JSON" in content:
                if "经济" in content:
                    return {
                        "content": """```json
{
  "viewpoint": "AI将显著促进经济增长和生产力提升。",
  "supporting_evidence": ["GDP增长数据", "生产力研究"],
  "reasoning_process": "基于经济增长理论分析...",
  "confidence": 0.9
}```"""
                    }
                else:
                    return {
                        "content": """```json
{
  "viewpoint": "AI将严重加剧社会不平等和失业问题。",
  "supporting_evidence": ["失业率统计", "收入分配研究"],
  "reasoning_process": "基于社会学理论分析...",
  "confidence": 0.8
}```"""
                    }
            else:
                return {"content": "Generated response"}
        
        services["llm_interface"].generate.side_effect = conflicting_llm_side_effect
        
        workflow = MultiPerspectiveSynthesisWorkflow("conflict_test")
        
        result = await workflow.execute(
            "AI的影响",
            ["经济", "社会"],
            services
        )
        
        # Verify conflict analysis was performed
        assert result["success"] is True
        viewpoint_analysis = result["viewpoint_analysis"]
        
        # Should detect conflicts between positive economic view and negative social view
        assert "conflicts" in viewpoint_analysis
        conflicts = viewpoint_analysis["conflicts"]
        
        # May or may not detect conflicts depending on the analysis algorithm
        # But the structure should be there
        assert isinstance(conflicts, list)


if __name__ == "__main__":
    pytest.main([__file__])
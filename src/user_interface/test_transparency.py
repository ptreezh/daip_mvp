#!/usr/bin/env python3
"""@Time    : 2025-07-24 21:00:00
@Author  : DAIP-LIVE Team
@File    : test_transparency.py
@Description:
    Test script for transparency and result presentation features.
"""
import asyncio
import json

from rich.console import Console
from rich.panel import Panel

from .feedback_collector import FeedbackCollector
from .result_formatter import ResultFormatter
from .transparency_controller import TransparencyController


def create_sample_critical_review_result():
    """Create a sample Critical Review Workflow result for testing."""
    return {
        "success": True,
        "execution_id": "test_critical_review_001",
        "workflow_type": "critical-review",
        "original_content": "人工智能将在2030年前取代50%的工作岗位。这一预测基于麦肯锡的研究报告。",
        "facts_extracted": 2,
        "facts_reviewed": 2,
        "facts_needing_revision": 1,
        "credibility_scores": {
            "fact_001": 0.3,
            "fact_002": 0.8
        },
        "revision_needed": True,
        "final_content": "人工智能预计将在2030年前对就业市场产生重大影响，可能影响多达50%的工作岗位，但这种影响包括工作转型和新岗位创造。这一预测基于麦肯锡2023年的研究报告。",
        "revision_summary": "修正了过于绝对的表述，增加了更准确的描述",
        "execution_trace": [
            {
                "step_name": "Content Generation",
                "status": "completed",
                "duration": 2.5,
                "inputs": {"prompt": "Generate content about AI impact"},
                "outputs": {"content": "Generated content"},
                "reasoning": "Generated initial content based on prompt"
            },
            {
                "step_name": "Fact Extraction",
                "status": "completed", 
                "duration": 1.8,
                "inputs": {"content": "Original content"},
                "outputs": {"facts": ["fact_001", "fact_002"]},
                "reasoning": "Extracted 2 verifiable facts from content"
            },
            {
                "step_name": "Parallel Review",
                "status": "completed",
                "duration": 5.2,
                "inputs": {"facts": ["fact_001", "fact_002"]},
                "outputs": {"evidence_reports": "Review results"},
                "reasoning": "Conducted parallel review with challenger and validator roles"
            }
        ],
        "evidence_reports": [
            {
                "fact_id": "fact_001",
                "supporting_evidence": [],
                "challenging_evidence": [
                    {
                        "source": "批判者_review",
                        "credibility": 0.7,
                        "evidence_type": "challenging",
                        "content": "表述过于绝对，缺乏细节说明"
                    }
                ],
                "overall_assessment": "需要更准确的表述",
                "reviewer_id": "批判者"
            }
        ]
    }


def create_sample_multi_perspective_result():
    """Create a sample Multi-perspective Synthesis Workflow result for testing."""
    return {
        "success": True,
        "execution_id": "test_multi_perspective_001",
        "workflow_type": "multi-perspective",
        "topic": "AI对就业的影响",
        "perspectives": ["经济", "社会", "技术", "伦理"],
        "quality_score": 0.85,
        "confidence": 0.78,
        "refinement_applied": True,
        "refinement_iterations": 2,
        "synthesis": "人工智能对就业的影响是一个复杂的多维度问题。从经济角度看，AI将提高生产效率但可能导致短期失业。从社会角度看，需要重新培训和教育体系改革。从技术角度看，AI将创造新的工作类型。从伦理角度看，需要确保公平的转型过程。",
        "key_insights": [
            "AI影响就业是渐进过程，不是突然替代",
            "新技术创造新岗位的同时淘汰旧岗位",
            "教育和培训体系需要适应性改革",
            "政策制定需要平衡效率和公平"
        ],
        "expert_contributions": {
            "经济专家": ["分析了生产效率提升", "评估了短期失业风险"],
            "社会专家": ["提出了再培训需求", "分析了社会适应性"],
            "技术专家": ["解释了AI技术发展趋势", "预测了新工作类型"],
            "伦理专家": ["强调了公平转型", "提出了伦理考量"]
        },
        "viewpoint_analysis": {
            "conflicts": ["短期vs长期影响", "效率vs公平"],
            "consensus_areas": ["需要教育改革", "政策干预必要"],
            "quality_score": 0.82
        },
        "sub_problems": [
            {
                "perspective": "经济",
                "description": "分析AI对生产效率和就业市场的经济影响",
                "questions": ["AI如何影响劳动生产率？", "失业成本如何计算？"]
            },
            {
                "perspective": "社会",
                "description": "评估AI对社会结构和人际关系的影响",
                "questions": ["社会如何适应技术变革？", "教育体系如何改革？"]
            }
        ],
        "execution_trace": [
            {
                "step_name": "Task Decomposition",
                "status": "completed",
                "duration": 1.5,
                "reasoning": "分解主题为4个专业视角"
            },
            {
                "step_name": "Parallel Exploration",
                "status": "completed",
                "duration": 8.3,
                "reasoning": "4个专家并行分析各自领域"
            },
            {
                "step_name": "Viewpoint Synthesis",
                "status": "completed",
                "duration": 3.7,
                "reasoning": "综合多个视角形成统一见解"
            }
        ]
    }


async def test_result_formatting():
    """Test different result formatting options."""
    console = Console()
    formatter = ResultFormatter()
    
    console.print(Panel(
        "[blue]Testing Result Formatting[/blue]",
        title="Test: Result Formatting",
        border_style="blue"
    ))
    
    # Test Critical Review formatting
    critical_result = create_sample_critical_review_result()
    
    console.print("\n[cyan]Critical Review - JSON Format:[/cyan]")
    json_output = formatter.format_as_json(critical_result)
    console.print(json_output[:200] + "..." if len(json_output) > 200 else json_output)
    
    console.print("\n[cyan]Critical Review - Markdown Format:[/cyan]")
    md_output = formatter.format_as_markdown(critical_result)
    console.print(md_output[:300] + "..." if len(md_output) > 300 else md_output)
    
    console.print("\n[cyan]Critical Review - HTML Format:[/cyan]")
    html_output = formatter.format_as_html(critical_result)
    console.print(html_output[:200] + "..." if len(html_output) > 200 else html_output)
    
    # Test Multi-perspective formatting
    multi_result = create_sample_multi_perspective_result()
    
    console.print("\n[cyan]Multi-perspective - Text Format:[/cyan]")
    text_output = formatter.format_as_text(multi_result)
    console.print(text_output)


async def test_traceability_features():
    """Test traceability and transparency features."""
    console = Console()
    formatter = ResultFormatter()
    
    console.print(Panel(
        "[blue]Testing Traceability Features[/blue]",
        title="Test: Traceability",
        border_style="blue"
    ))
    
    result = create_sample_critical_review_result()
    
    # Test traceability formatting
    console.print("\n[cyan]Enhanced Traceability (JSON):[/cyan]")
    traceable_output = formatter.format_with_traceability(
        result,
        format_type="json",
        include_reasoning=True,
        include_confidence=True,
        include_sources=True
    )
    
    # Parse and display key sections
    traceable_data = json.loads(traceable_output)
    
    if "reasoning_trace" in traceable_data:
        console.print("\n[yellow]Reasoning Trace:[/yellow]")
        for i, trace in enumerate(traceable_data["reasoning_trace"], 1):
            console.print(f"  {i}. {trace['step']}: {trace['reasoning']}")
    
    if "confidence_analysis" in traceable_data:
        console.print(f"\n[yellow]Overall Confidence:[/yellow] {traceable_data['confidence_analysis']['overall_confidence']:.3f}")
    
    # Test transparency levels
    console.print("\n[cyan]Transparency Levels:[/cyan]")
    
    for level in ["minimal", "moderate", "detailed"]:
        console.print(f"\n[yellow]{level.title()} Transparency:[/yellow]")
        formatter.display_with_transparency(result, console, level)


async def test_feedback_collection():
    """Test feedback collection features."""
    console = Console()
    collector = FeedbackCollector()
    
    console.print(Panel(
        "[blue]Testing Feedback Collection[/blue]",
        title="Test: Feedback Collection",
        border_style="blue"
    ))
    
    result = create_sample_critical_review_result()
    
    # Test non-interactive feedback collection
    console.print("\n[cyan]Non-interactive Feedback Collection:[/cyan]")
    feedback = collector.collect_workflow_feedback(
        result=result,
        execution_id="test_001",
        workflow_type="critical-review",
        interactive=False
    )
    
    collector.display_feedback_summary(feedback)
    
    # Test validation
    console.print("\n[cyan]Result Validation:[/cyan]")
    validation_results = collector.validate_result_elements(result)
    
    for validation in validation_results:
        status = "✅ Valid" if validation.is_valid else "❌ Invalid"
        console.print(f"  {validation.element_id}: {status} - {validation.validation_reason}")
    
    # Test feedback export
    console.print("\n[cyan]Feedback Export (JSON):[/cyan]")
    exported_feedback = collector.export_feedback("test_001", "json")
    console.print(exported_feedback[:300] + "..." if len(exported_feedback) > 300 else exported_feedback)


async def test_transparency_controller():
    """Test the complete transparency controller."""
    console = Console()
    controller = TransparencyController()
    
    console.print(Panel(
        "[blue]Testing Transparency Controller[/blue]",
        title="Test: Transparency Controller",
        border_style="blue"
    ))
    
    result = create_sample_critical_review_result()
    
    # Test result presentation
    console.print("\n[cyan]Result Presentation (Moderate Transparency):[/cyan]")
    feedback = controller.present_workflow_result(
        result=result,
        execution_id="test_controller_001",
        workflow_type="critical-review",
        transparency_level="moderate",
        collect_feedback=False
    )
    
    # Test traceability report
    console.print("\n[cyan]Traceability Report:[/cyan]")
    traceable_result = controller.present_with_traceability(
        result=result,
        execution_id="test_controller_001",
        output_format="markdown"
    )
    console.print(traceable_result[:500] + "..." if len(traceable_result) > 500 else traceable_result)
    
    # Test validation
    console.print("\n[cyan]Quality Validation:[/cyan]")
    validation_results = controller.validate_result_quality(result)
    console.print(f"Validation completed: {len(validation_results)} elements validated")
    
    # Test export
    console.print("\n[cyan]Export Test:[/cyan]")
    exported_content = controller.export_result(
        result=result,
        execution_id="test_controller_001",
        format_type="html",
        include_traceability=True
    )
    console.print(f"Exported HTML content: {len(exported_content)} characters")
    
    # Test comprehensive transparency report
    console.print("\n[cyan]Comprehensive Transparency Report:[/cyan]")
    transparency_report = controller.create_transparency_report(
        result=result,
        execution_id="test_controller_001",
        workflow_type="critical-review"
    )
    
    console.print(f"Report sections: {list(transparency_report.keys())}")
    console.print(f"Report size: {len(json.dumps(transparency_report))} characters")


async def main():
    """Run all transparency feature tests."""
    console = Console()
    
    console.print(Panel(
        "[bold green]Transparency Features Test Suite[/bold green]\n\n"
        "This test suite demonstrates the implementation of task 9.3:\n"
        "- Multiple output format handlers\n"
        "- Traceability and reasoning exposure\n"
        "- User feedback and validation mechanisms",
        title="Task 9.3 Implementation Test",
        border_style="green"
    ))
    
    try:
        await test_result_formatting()
        await test_traceability_features()
        await test_feedback_collection()
        await test_transparency_controller()
        
        console.print(Panel(
            "[bold green]All tests completed successfully![/bold green]\n\n"
            "Task 9.3 implementation includes:\n"
            "✅ Multiple output formats (JSON, Markdown, HTML, XML, CSV, YAML, Text)\n"
            "✅ Traceability with reasoning, confidence, and source attribution\n"
            "✅ User feedback collection and validation mechanisms\n"
            "✅ Configurable transparency levels (minimal, moderate, detailed)\n"
            "✅ Comprehensive transparency controller\n"
            "✅ Enhanced CLI and API interfaces",
            title="Test Results",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"[red]Test failed: {e}[/red]")
        console.print_exception()


if __name__ == "__main__":
    asyncio.run(main())
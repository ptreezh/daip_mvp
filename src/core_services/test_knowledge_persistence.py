#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-24 23:45:00
@Author  : DAIP-LIVE Team
@File    : test_knowledge_persistence.py
@Description:
    Test script for knowledge persistence mechanisms.
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .enhanced_sskg_manager import EnhancedSSKGManager
from .wiki_service import WikiService
from .knowledge_persistence_service import KnowledgePersistenceService
from .knowledge_retrieval_service import KnowledgeRetrievalService, SearchScope
from .workflow_knowledge_integrator import (
    WorkflowKnowledgeIntegrator,
    WorkflowIntegrationConfig
)

console = Console()


def create_sample_critical_review_result():
    """Create a sample Critical Review workflow result for testing."""
    return {
        "success": True,
        "execution_id": "test_critical_review_001",
        "workflow_type": "critical-review",
        "original_content": "人工智能将在2030年前取代50%的工作岗位。这一预测基于麦肯锡的研究报告。AI技术的发展速度正在加快。",
        "facts_extracted": 3,
        "facts_reviewed": 3,
        "facts_needing_revision": 1,
        "extracted_facts": [
            {
                "id": "fact_001",
                "content": "人工智能将在2030年前取代50%的工作岗位",
                "confidence": 0.3,
                "source_location": "sentence 1",
                "fact_type": "prediction",
                "metadata": {
                    "extraction_method": "llm",
                    "extraction_timestamp": datetime.now().isoformat()
                }
            },
            {
                "id": "fact_002", 
                "content": "这一预测基于麦肯锡的研究报告",
                "confidence": 0.8,
                "source_location": "sentence 2",
                "fact_type": "attribution",
                "metadata": {
                    "extraction_method": "llm",
                    "extraction_timestamp": datetime.now().isoformat()
                }
            },
            {
                "id": "fact_003",
                "content": "AI技术的发展速度正在加快",
                "confidence": 0.7,
                "source_location": "sentence 3", 
                "fact_type": "general",
                "metadata": {
                    "extraction_method": "llm",
                    "extraction_timestamp": datetime.now().isoformat()
                }
            }
        ],
        "credibility_scores": {
            "fact_001": 0.3,
            "fact_002": 0.8,
            "fact_003": 0.7
        },
        "evidence_reports": [
            {
                "fact_id": "fact_001",
                "supporting_evidence": [],
                "challenging_evidence": [
                    {
                        "source": "批判者_review",
                        "credibility": 0.7,
                        "evidence_type": "challenging",
                        "content": "表述过于绝对，缺乏细节说明和时间范围的准确性"
                    }
                ],
                "overall_assessment": "需要更准确和细致的表述",
                "reviewer_id": "批判者"
            },
            {
                "fact_id": "fact_002",
                "supporting_evidence": [
                    {
                        "source": "验证者_review",
                        "credibility": 0.8,
                        "evidence_type": "supporting",
                        "content": "麦肯锡确实发布了相关研究报告"
                    }
                ],
                "challenging_evidence": [],
                "overall_assessment": "来源可靠，表述准确",
                "reviewer_id": "验证者"
            },
            {
                "fact_id": "fact_003",
                "supporting_evidence": [
                    {
                        "source": "验证者_review",
                        "credibility": 0.7,
                        "evidence_type": "supporting",
                        "content": "AI技术发展确实在加速，有多项指标支持"
                    }
                ],
                "challenging_evidence": [],
                "overall_assessment": "基本准确的观察",
                "reviewer_id": "验证者"
            }
        ],
        "revision_needed": True,
        "revised_content": "人工智能预计将在2030年前对就业市场产生重大影响，可能影响多达50%的工作岗位，但这种影响包括工作转型和新岗位创造。这一预测基于麦肯锡2023年的研究报告。AI技术的发展速度正在加快，为各行业带来新的机遇和挑战。",
        "revision_summary": "修正了过于绝对的表述，增加了更准确和平衡的描述"
    }


def create_sample_multi_perspective_result():
    """Create a sample Multi-perspective Synthesis workflow result for testing."""
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
        "synthesis": "人工智能对就业的影响是一个复杂的多维度问题。从经济角度看，AI将提高生产效率但可能导致短期失业。从社会角度看，需要重新培训和教育体系改革。从技术角度看，AI将创造新的工作类型。从伦理角度看，需要确保公平的转型过程。综合各方观点，AI对就业的影响将是渐进的，需要政策制定者、企业和个人共同应对这一转型。",
        "key_insights": [
            "AI影响就业是渐进过程，不是突然替代",
            "新技术创造新岗位的同时淘汰旧岗位",
            "教育和培训体系需要适应性改革",
            "政策制定需要平衡效率和公平",
            "个人需要持续学习和技能更新"
        ],
        "expert_contributions": {
            "经济专家": [
                "分析了生产效率提升对经济的积极影响",
                "评估了短期失业风险和长期就业结构变化",
                "提出了经济政策建议"
            ],
            "社会专家": [
                "提出了再培训和教育改革的需求",
                "分析了社会适应性和包容性问题",
                "强调了社会保障体系的重要性"
            ],
            "技术专家": [
                "解释了AI技术发展趋势和应用前景",
                "预测了新兴工作类型和技能需求",
                "分析了人机协作的可能性"
            ],
            "伦理专家": [
                "强调了公平转型的重要性",
                "提出了伦理考量和价值观问题",
                "建议了负责任的AI发展路径"
            ]
        },
        "viewpoint_analysis": {
            "conflicts": [
                "短期vs长期影响的权衡",
                "效率提升vs就业保障的平衡",
                "技术发展速度vs社会适应能力"
            ],
            "consensus_areas": [
                "需要教育和培训体系改革",
                "政策干预和引导的必要性",
                "人机协作是未来趋势",
                "需要渐进式转型策略"
            ],
            "quality_score": 0.82
        },
        "sub_problems": [
            {
                "perspective": "经济",
                "description": "分析AI对生产效率和就业市场的经济影响",
                "questions": [
                    "AI如何影响劳动生产率？",
                    "失业成本如何计算和补偿？",
                    "新经济模式如何适应AI时代？"
                ]
            },
            {
                "perspective": "社会",
                "description": "评估AI对社会结构和人际关系的影响",
                "questions": [
                    "社会如何适应技术变革？",
                    "教育体系如何改革？",
                    "社会保障如何完善？"
                ]
            },
            {
                "perspective": "技术",
                "description": "分析AI技术发展对工作方式的改变",
                "questions": [
                    "哪些工作最容易被AI替代？",
                    "人机协作如何实现？",
                    "新技术岗位有哪些？"
                ]
            },
            {
                "perspective": "伦理",
                "description": "探讨AI发展中的伦理问题和价值观",
                "questions": [
                    "如何确保AI发展的公平性？",
                    "技术进步的社会责任是什么？",
                    "如何平衡效率和人文关怀？"
                ]
            }
        ]
    }


async def test_knowledge_persistence_service():
    """Test the knowledge persistence service."""
    console.print(Panel(
        "[blue]Testing Knowledge Persistence Service[/blue]",
        title="Test: Knowledge Persistence",
        border_style="blue"
    ))
    
    # Initialize services
    sskg_manager = EnhancedSSKGManager()
    wiki_service = WikiService()
    persistence_service = KnowledgePersistenceService(
        sskg_manager=sskg_manager,
        wiki_service=wiki_service
    )
    
    # Test Critical Review persistence
    console.print("\n[cyan]Testing Critical Review Persistence:[/cyan]")
    critical_result = create_sample_critical_review_result()
    
    persistence_results = await persistence_service.persist_critical_review_results(
        critical_result, "test_critical_001"
    )
    
    # Display results
    table = Table(title="Critical Review Persistence Results")
    table.add_column("Fact ID", style="cyan")
    table.add_column("Success", style="green")
    table.add_column("Confidence", style="magenta")
    table.add_column("Conflicts", style="yellow")
    
    for result in persistence_results:
        success_icon = "✅" if result.success else "❌"
        table.add_row(
            result.metadata.get("fact_id", "Unknown"),
            success_icon,
            f"{result.metadata.get('confidence_score', 0):.2f}",
            str(len(result.conflicts_detected))
        )
    
    console.print(table)
    
    # Test Multi-perspective Synthesis persistence
    console.print("\n[cyan]Testing Multi-perspective Synthesis Persistence:[/cyan]")
    synthesis_result = create_sample_multi_perspective_result()
    
    synthesis_persistence = await persistence_service.persist_synthesis_results(
        synthesis_result, "test_synthesis_001"
    )
    
    console.print(f"Synthesis Persistence: {'✅ Success' if synthesis_persistence.success else '❌ Failed'}")
    console.print(f"Node ID: {synthesis_persistence.persisted_node_id}")
    console.print(f"Conflicts Detected: {len(synthesis_persistence.conflicts_detected)}")
    console.print(f"Wiki Page: {'Created' if synthesis_persistence.wiki_page_id else 'Not created'}")
    
    # Get persistence statistics
    console.print("\n[cyan]Persistence Statistics:[/cyan]")
    stats = persistence_service.get_persistence_statistics()
    
    stats_table = Table(title="Persistence Statistics")
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="magenta")
    
    for key, value in stats.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                stats_table.add_row(f"{key}.{sub_key}", str(sub_value))
        else:
            stats_table.add_row(key, str(value))
    
    console.print(stats_table)


async def test_knowledge_retrieval_service():
    """Test the knowledge retrieval service."""
    console.print(Panel(
        "[blue]Testing Knowledge Retrieval Service[/blue]",
        title="Test: Knowledge Retrieval",
        border_style="blue"
    ))
    
    # Initialize services (reuse from persistence test)
    sskg_manager = EnhancedSSKGManager()
    wiki_service = WikiService()
    retrieval_service = KnowledgeRetrievalService(
        sskg_manager=sskg_manager,
        wiki_service=wiki_service
    )
    
    # First, add some test data
    persistence_service = KnowledgePersistenceService(
        sskg_manager=sskg_manager,
        wiki_service=wiki_service
    )
    
    # Add test data
    critical_result = create_sample_critical_review_result()
    synthesis_result = create_sample_multi_perspective_result()
    
    await persistence_service.persist_critical_review_results(critical_result, "test_001")
    await persistence_service.persist_synthesis_results(synthesis_result, "test_002")
    
    # Test semantic search
    console.print("\n[cyan]Testing Semantic Search:[/cyan]")
    
    search_queries = [
        "人工智能就业影响",
        "AI technology development",
        "麦肯锡研究报告",
        "工作岗位替代"
    ]
    
    for query in search_queries:
        console.print(f"\n[yellow]Search Query:[/yellow] {query}")
        
        search_results = await retrieval_service.semantic_search(
            query=query,
            scope=SearchScope.ALL,
            limit=3
        )
        
        if search_results:
            for i, result in enumerate(search_results, 1):
                console.print(f"  {i}. [{result.node_type}] {result.content[:100]}...")
                console.print(f"     Confidence: {result.confidence:.2f}, Relevance: {result.relevance_score:.2f}")
        else:
            console.print("  No results found")
    
    # Test cross-session knowledge sharing
    console.print("\n[cyan]Testing Cross-session Knowledge Sharing:[/cyan]")
    
    session_context = {
        "topic": "AI就业影响",
        "keywords": ["人工智能", "工作", "就业"],
        "user_id": "test_user"
    }
    
    cross_session_knowledge = await retrieval_service.get_cross_session_knowledge(
        session_context=session_context,
        time_window_days=30
    )
    
    console.print(f"Facts found: {len(cross_session_knowledge['facts'])}")
    console.print(f"Synthesis found: {len(cross_session_knowledge['synthesis'])}")
    console.print(f"Wiki pages found: {len(cross_session_knowledge['wiki_pages'])}")
    console.print(f"Knowledge connections: {len(cross_session_knowledge['knowledge_connections'])}")
    
    # Test knowledge quality assessment
    console.print("\n[cyan]Testing Knowledge Quality Assessment:[/cyan]")
    
    # Get some nodes to assess
    all_nodes = sskg_manager.query(sskg_manager.KnowledgeQuery(limit=3))
    
    for node in all_nodes:
        assessment = await retrieval_service.assess_knowledge_quality(node.id)
        
        console.print(f"\n[yellow]Node:[/yellow] {node.content[:50]}...")
        console.print(f"Overall Quality: {assessment.overall_quality:.2f}")
        console.print(f"Recommendations: {len(assessment.recommendations)}")
        
        for rec in assessment.recommendations[:2]:  # Show first 2 recommendations
            console.print(f"  - {rec}")
    
    # Test knowledge statistics
    console.print("\n[cyan]Knowledge Statistics:[/cyan]")
    stats = retrieval_service.get_knowledge_statistics()
    
    for key, value in stats.items():
        if isinstance(value, dict):
            console.print(f"{key}:")
            for sub_key, sub_value in value.items():
                console.print(f"  {sub_key}: {sub_value}")
        else:
            console.print(f"{key}: {value}")


async def test_workflow_integration():
    """Test the workflow knowledge integrator."""
    console.print(Panel(
        "[blue]Testing Workflow Knowledge Integration[/blue]",
        title="Test: Workflow Integration",
        border_style="blue"
    ))
    
    # Initialize services
    sskg_manager = EnhancedSSKGManager()
    wiki_service = WikiService()
    
    config = WorkflowIntegrationConfig(
        auto_persist_facts=True,
        auto_persist_synthesis=True,
        min_confidence_threshold=0.5,
        create_wiki_pages=True,
        enable_cross_session_sharing=True
    )
    
    integrator = WorkflowKnowledgeIntegrator(
        sskg_manager=sskg_manager,
        wiki_service=wiki_service,
        config=config
    )
    
    # Test Critical Review integration
    console.print("\n[cyan]Testing Critical Review Integration:[/cyan]")
    
    critical_result = create_sample_critical_review_result()
    enhanced_critical = await integrator.integrate_critical_review_workflow(
        workflow_result=critical_result,
        execution_id="integration_test_001"
    )
    
    # Display integration results
    if "knowledge_persistence" in enhanced_critical:
        persistence_info = enhanced_critical["knowledge_persistence"]
        console.print(f"Facts Persisted: {persistence_info['facts_persisted']}")
        console.print(f"Persistence Failures: {persistence_info['persistence_failures']}")
        console.print(f"Conflicts Detected: {persistence_info['conflicts_detected']}")
        console.print(f"Wiki Pages Created: {persistence_info['wiki_pages_created']}")
    
    # Test Multi-perspective integration
    console.print("\n[cyan]Testing Multi-perspective Integration:[/cyan]")
    
    synthesis_result = create_sample_multi_perspective_result()
    enhanced_synthesis = await integrator.integrate_multi_perspective_workflow(
        workflow_result=synthesis_result,
        execution_id="integration_test_002"
    )
    
    # Display integration results
    if "knowledge_persistence" in enhanced_synthesis:
        persistence_info = enhanced_synthesis["knowledge_persistence"]
        console.print(f"Synthesis Persisted: {persistence_info['synthesis_persisted']}")
        console.print(f"Conflicts Detected: {persistence_info['conflicts_detected']}")
        console.print(f"Wiki Page Created: {persistence_info['wiki_page_created']}")
    
    # Test cross-session knowledge sharing
    if "cross_session_knowledge" in enhanced_synthesis:
        cross_session = enhanced_synthesis["cross_session_knowledge"]
        console.print(f"Related Facts: {len(cross_session['facts'])}")
        console.print(f"Related Synthesis: {len(cross_session['related_synthesis'])}")
        console.print(f"Knowledge Connections: {len(cross_session['knowledge_connections'])}")
    
    # Get integration statistics
    console.print("\n[cyan]Integration Statistics:[/cyan]")
    integration_stats = integrator.get_integration_statistics()
    
    for key, value in integration_stats.items():
        if isinstance(value, dict):
            console.print(f"{key}:")
            for sub_key, sub_value in value.items():
                console.print(f"  {sub_key}: {sub_value}")
        else:
            console.print(f"{key}: {value}")


async def test_knowledge_search():
    """Test knowledge search functionality."""
    console.print(Panel(
        "[blue]Testing Knowledge Search[/blue]",
        title="Test: Knowledge Search",
        border_style="blue"
    ))
    
    # Initialize services and add test data
    sskg_manager = EnhancedSSKGManager()
    wiki_service = WikiService()
    integrator = WorkflowKnowledgeIntegrator(
        sskg_manager=sskg_manager,
        wiki_service=wiki_service
    )
    
    # Add test data
    critical_result = create_sample_critical_review_result()
    synthesis_result = create_sample_multi_perspective_result()
    
    await integrator.integrate_critical_review_workflow(critical_result, "search_test_001")
    await integrator.integrate_multi_perspective_workflow(synthesis_result, "search_test_002")
    
    # Test search functionality
    console.print("\n[cyan]Testing Knowledge Search:[/cyan]")
    
    search_results = await integrator.search_knowledge(
        query="人工智能对就业的影响",
        knowledge_types=["facts", "synthesis"],
        min_confidence=0.5,
        limit=5
    )
    
    console.print(f"Search Results: {search_results['total_results']} items found")
    
    for i, result in enumerate(search_results['results'], 1):
        console.print(f"\n{i}. [{result['type']}] {result['content'][:100]}...")
        console.print(f"   Confidence: {result['confidence']:.2f}")
        console.print(f"   Created: {result['created_at']}")
        
        if result['type'] == 'fact':
            console.print(f"   Source: {result.get('source', 'Unknown')}")
        elif result['type'] == 'concept':
            console.print(f"   Topic: {result.get('topic', 'Unknown')}")


async def main():
    """Run all knowledge persistence tests."""
    console.print(Panel(
        "[bold green]Knowledge Persistence Mechanisms Test Suite[/bold green]\n\n"
        "This test suite demonstrates the implementation of task 10.1:\n"
        "- Automatic fact persistence from Critical Review\n"
        "- Synthesis result storage from Multi-perspective Synthesis\n"
        "- Confidence scoring and evidence source tracking\n"
        "- Cross-session knowledge sharing\n"
        "- Semantic search capabilities\n"
        "- Knowledge quality assessment",
        title="Task 10.1 Implementation Test",
        border_style="green"
    ))
    
    try:
        await test_knowledge_persistence_service()
        await test_knowledge_retrieval_service()
        await test_workflow_integration()
        await test_knowledge_search()
        
        console.print(Panel(
            "[bold green]All tests completed successfully![/bold green]\n\n"
            "Task 10.1 implementation includes:\n"
            "✅ Automatic fact persistence from Critical Review workflows\n"
            "✅ Synthesis result storage from Multi-perspective workflows\n"
            "✅ Confidence scoring and evidence source tracking\n"
            "✅ Cross-session knowledge sharing capabilities\n"
            "✅ Semantic search for validated information\n"
            "✅ Knowledge quality assessment metrics\n"
            "✅ Knowledge evolution tracking\n"
            "✅ Workflow integration decorators\n"
            "✅ Comprehensive statistics and monitoring",
            title="Test Results",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"[red]Test failed: {e}[/red]")
        console.print_exception()


if __name__ == "__main__":
    asyncio.run(main())
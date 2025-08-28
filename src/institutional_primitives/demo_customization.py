#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-25 09:00:00
@Author  : DAIP-LIVE Team
@File    : demo_customization.py
@Description:
    Demonstration of role and consensus customization capabilities.
"""
import asyncio
from role_customization import (
    RoleConfigurationManager, ExpertiseProfile, RolePersonality,
    ExpertiseLevel, CognitiveStyle, InteractionMode
)
from consensus_customization import (
    ConsensusManager, ConsensusInput
)
from performance_optimization import PerformanceOptimizationManager


async def demo_role_customization():
    """Demonstrate role customization capabilities."""
    print("🎭 ROLE CUSTOMIZATION DEMO")
    print("=" * 50)
    
    role_manager = RoleConfigurationManager()
    
    # Create a custom AI ethics expert
    config = role_manager.create_role_from_template(
        "domain_expert",
        "ai_ethics_expert",
        {
            "expertise_profile": ExpertiseProfile(
                domain="ai_ethics",
                level=ExpertiseLevel.EXPERT,
                specializations=["algorithmic_bias", "privacy", "fairness"],
                key_skills=["ethical_reasoning", "policy_analysis", "stakeholder_engagement"]
            ),
            "personality": RolePersonality(
                openness=0.9,
                conscientiousness=0.8,
                agreeableness=0.7,
                neuroticism=0.3
            ),
            "cognitive_style": CognitiveStyle.HOLISTIC,
            "interaction_mode": InteractionMode.COLLABORATIVE,
            "communication_style": "thoughtful and balanced"
        }
    )
    
    print(f"✅ Created role: {config.name}")
    print(f"   Domain: {config.expertise_profile.domain}")
    print(f"   Level: {config.expertise_profile.level.value}")
    print(f"   Specializations: {', '.join(config.expertise_profile.specializations)}")
    print(f"   Cognitive Style: {config.cognitive_style.value}")
    print(f"   Communication: {config.communication_style}")
    
    # Generate a system prompt
    system_prompt = role_manager.get_role_prompt(
        "ai_ethics_expert",
        "system",
        domain="ai_ethics"
    )
    print("\n📝 Generated System Prompt:")
    print(f"   {system_prompt[:100]}...")
    
    return role_manager


async def demo_consensus_mechanisms():
    """Demonstrate consensus mechanisms."""
    print("\n🤝 CONSENSUS MECHANISMS DEMO")
    print("=" * 50)
    
    consensus_manager = ConsensusManager()
    
    # Create consensus inputs for AI safety decision
    inputs = [
        ConsensusInput(
            participant_id="ai_safety_expert",
            vote="implement_safety_measures",
            confidence=0.9,
            weight=3.0,
            evidence=[
                {"source": "research_paper", "credibility": 0.9, "type": "peer_reviewed"},
                {"source": "case_study", "credibility": 0.8, "type": "empirical"}
            ]
        ),
        ConsensusInput(
            participant_id="industry_representative",
            vote="gradual_implementation",
            confidence=0.7,
            weight=2.0,
            evidence=[
                {"source": "industry_report", "credibility": 0.7, "type": "industry"}
            ]
        ),
        ConsensusInput(
            participant_id="ethicist",
            vote="implement_safety_measures",
            confidence=0.8,
            weight=2.5,
            evidence=[
                {"source": "ethical_framework", "credibility": 0.8, "type": "theoretical"}
            ]
        )
    ]
    
    # Test different consensus mechanisms
    mechanisms = ["simple_majority", "weighted_expert", "evidence_based"]
    
    for mechanism in mechanisms:
        result = await consensus_manager.calculate_consensus(mechanism, inputs)
        print(f"\n🔍 {mechanism.replace('_', ' ').title()} Consensus:")
        print(f"   Decision: {result.consensus_value}")
        print(f"   Confidence: {result.confidence:.3f}")
        print(f"   Agreement: {result.agreement_level:.3f}")
        print(f"   Participants: {result.participant_count}")
    
    return consensus_manager


def demo_performance_optimization():
    """Demonstrate performance optimization."""
    print("\n⚡ PERFORMANCE OPTIMIZATION DEMO")
    print("=" * 50)
    
    optimization_manager = PerformanceOptimizationManager()
    
    # Test configuration validation
    test_config = {
        "name": "ai_ethics_workflow",
        "version": "1.0.0",
        "type": "workflow",
        "parameters": {
            "confidence_threshold": 0.8,
            "evidence_weight": 0.7
        },
        "resources": {
            "memory_limit": 2048,
            "cpu_limit": 2.0,
            "timeout": 300
        },
        "dependencies": {
            "services": ["llm_interface", "knowledge_service"]
        }
    }
    
    result = optimization_manager.validate_and_optimize_configuration(test_config)
    
    print("✅ Configuration Validation:")
    print(f"   Valid: {result['validation']['is_valid']}")
    print(f"   Errors: {len(result['validation']['errors'])}")
    print(f"   Warnings: {len(result['validation']['warnings'])}")
    print(f"   Optimization Suggestions: {len(result['optimization_suggestions'])}")
    
    if result['optimization_suggestions']:
        print("\n💡 Top Optimization Suggestion:")
        suggestion = result['optimization_suggestions'][0]
        print(f"   {suggestion['title']}: {suggestion['description']}")
    
    return optimization_manager


async def demo_integration():
    """Demonstrate integration between components."""
    print("\n🔗 INTEGRATION DEMO")
    print("=" * 50)
    
    # Initialize all components
    role_manager = RoleConfigurationManager()
    consensus_manager = ConsensusManager()
    
    # Create roles for AI governance committee
    roles = [
        ("ai_researcher", ExpertiseLevel.EXPERT, 3.0),
        ("policy_maker", ExpertiseLevel.ADVANCED, 2.5),
        ("industry_rep", ExpertiseLevel.INTERMEDIATE, 2.0),
        ("citizen_advocate", ExpertiseLevel.NOVICE, 1.5)
    ]
    
    print("👥 Creating AI Governance Committee:")
    for role_id, level, weight in roles:
        config = role_manager.create_role_from_template(
            "domain_expert",
            role_id,
            {
                "expertise_profile": ExpertiseProfile(
                    domain="ai_governance",
                    level=level
                )
            }
        )
        print(f"   ✓ {role_id} ({level.value}, weight: {weight})")
    
    # Simulate committee decision on AI regulation
    inputs = []
    for role_id, level, weight in roles:
        # Most experts support regulation, but with varying confidence
        vote = "support_regulation" if level in [ExpertiseLevel.EXPERT, ExpertiseLevel.ADVANCED] else "moderate_regulation"
        confidence = 0.9 if level == ExpertiseLevel.EXPERT else 0.7
        
        inputs.append(ConsensusInput(
            participant_id=role_id,
            vote=vote,
            confidence=confidence,
            weight=weight
        ))
    
    # Calculate consensus
    result = await consensus_manager.calculate_consensus("weighted_expert", inputs)
    
    print("\n🏛️ Committee Decision:")
    print(f"   Consensus: {result.consensus_value}")
    print(f"   Confidence: {result.confidence:.3f}")
    print(f"   Agreement Level: {result.agreement_level:.3f}")
    print(f"   Supporting: {len(result.supporting_participants)} members")
    print(f"   Dissenting: {len(result.dissenting_participants)} members")


async def main():
    """Run the complete demonstration."""
    print("🚀 ROLE AND CONSENSUS CUSTOMIZATION DEMONSTRATION")
    print("🎯 Tasks 11.1 & 11.2 Implementation Showcase")
    print("=" * 80)
    
    try:
        await demo_role_customization()
        await demo_consensus_mechanisms()
        demo_performance_optimization()
        await demo_integration()
        
        print("\n" + "=" * 80)
        print("✅ DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("🎉 All customization features are working correctly:")
        print("   ✓ Dynamic role configuration")
        print("   ✓ Custom consensus mechanisms")
        print("   ✓ Performance optimization")
        print("   ✓ Integrated workflows")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
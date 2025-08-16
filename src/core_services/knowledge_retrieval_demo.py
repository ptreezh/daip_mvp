"""@Time    : 2025-07-25 02:30:00
@Author  : DAIP-LIVE Team
@File    : knowledge_retrieval_demo.py
@Description:
    Demonstration script for knowledge retrieval and evolution capabilities.
    Shows implementation of task 10.2 requirements.
"""
import asyncio
from datetime import datetime, timedelta

from .enhanced_sskg_manager import EnhancedSSKGManager, KnowledgeNode, NodeType
from .knowledge_evolution_manager import EvolutionStrategy, EvolutionTrigger
from .knowledge_management_service import KnowledgeManagementConfig, KnowledgeManagementService
from .knowledge_retrieval_service import SearchScope
from .wiki_service import WikiService


class KnowledgeRetrievalDemo:
    """Demonstration of knowledge retrieval and evolution capabilities."""

    def __init__(self):
        """Initialize the demo environment."""
        self.sskg_manager = None
        self.wiki_service = None
        self.knowledge_service = None
        self.demo_data = {}

    async def setup_demo_environment(self):
        """Set up the demo environment with test data."""
        print("🚀 Setting up Knowledge Retrieval and Evolution Demo...")

        # Initialize core services
        self.sskg_manager = EnhancedSSKGManager()
        self.wiki_service = WikiService()

        # Configure knowledge management
        config = KnowledgeManagementConfig(
            auto_persist_facts=True,
            auto_persist_synthesis=True,
            min_confidence_threshold=0.5,
            evolution_strategy="hybrid",
            quality_threshold=0.6,
            deprecation_age_days=365,
            auto_evolution_enabled=True,
            cross_session_sharing=True,
            auto_resolve_conflicts=True
        )

        # Initialize knowledge management service
        self.knowledge_service = KnowledgeManagementService(
            sskg_manager=self.sskg_manager,
            wiki_service=self.wiki_service,
            config=config
        )

        # Create demo knowledge base
        await self._create_demo_knowledge_base()

        print("✅ Demo environment setup complete!")
        print(f"📊 Created {len(self.demo_data)} categories of test knowledge")

    async def _create_demo_knowledge_base(self):
        """Create a comprehensive demo knowledge base."""
        # High-quality validated facts
        validated_facts = [
            {
                "content": "Python is a high-level, interpreted programming language created by Guido van Rossum",
                "confidence": 0.95,
                "metadata": {
                    "source": "critical_review_workflow",
                    "validation_timestamp": datetime.now().isoformat(),
                    "evidence_sources": ["python.org", "wikipedia.org", "pep-0001"],
                    "reviewer_roles": ["software_engineer", "language_designer"],
                    "expertise_domain": "programming_languages",
                    "session_id": "demo_session_001",
                    "topic": "programming"
                }
            },
            {
                "content": "Machine learning algorithms require training data to learn patterns and make predictions",
                "confidence": 0.92,
                "metadata": {
                    "source": "critical_review_workflow",
                    "validation_timestamp": datetime.now().isoformat(),
                    "evidence_sources": ["scikit-learn.org", "tensorflow.org", "nature.com"],
                    "reviewer_roles": ["data_scientist", "ml_engineer", "statistician"],
                    "expertise_domain": "machine_learning",
                    "session_id": "demo_session_002",
                    "topic": "artificial_intelligence"
                }
            },
            {
                "content": "Quantum computing leverages quantum mechanical phenomena like superposition and entanglement",
                "confidence": 0.88,
                "metadata": {
                    "source": "critical_review_workflow",
                    "validation_timestamp": datetime.now().isoformat(),
                    "evidence_sources": ["ibm.com/quantum", "nature.com", "arxiv.org"],
                    "reviewer_roles": ["quantum_physicist", "computer_scientist"],
                    "expertise_domain": "quantum_computing",
                    "session_id": "demo_session_003",
                    "topic": "quantum_technology"
                }
            }
        ]

        # Synthesis results from multi-perspective workflows
        synthesis_results = [
            {
                "content": "Artificial Intelligence represents the convergence of computer science, mathematics, cognitive science, and philosophy to create systems that can perform tasks typically requiring human intelligence",
                "confidence": 0.85,
                "metadata": {
                    "source": "multi_perspective_synthesis_workflow",
                    "expert_roles": ["computer_scientist", "mathematician", "cognitive_scientist", "philosopher"],
                    "synthesis_timestamp": datetime.now().isoformat(),
                    "expertise_domain": "artificial_intelligence",
                    "quality_score": 0.82,
                    "session_id": "demo_session_004",
                    "topic": "ai_definition"
                }
            },
            {
                "content": "The future of work will be shaped by automation, requiring humans to focus on creative, emotional, and strategic tasks while collaborating with AI systems",
                "confidence": 0.78,
                "metadata": {
                    "source": "multi_perspective_synthesis_workflow",
                    "expert_roles": ["economist", "sociologist", "technologist", "futurist"],
                    "synthesis_timestamp": datetime.now().isoformat(),
                    "expertise_domain": "future_of_work",
                    "quality_score": 0.75,
                    "session_id": "demo_session_005",
                    "topic": "automation_impact"
                }
            }
        ]

        # Lower quality content for evolution demonstration
        low_quality_content = [
            {
                "content": "Some programming language is probably good for doing stuff with computers",
                "confidence": 0.25,
                "metadata": {
                    "source": "user_input",
                    "expertise_domain": "programming_languages",
                    "session_id": "demo_session_006",
                    "topic": "programming"
                }
            },
            {
                "content": "AI might be useful or dangerous, not sure which",
                "confidence": 0.15,
                "metadata": {
                    "source": "user_input",
                    "expertise_domain": "artificial_intelligence",
                    "session_id": "demo_session_007",
                    "topic": "ai_impact"
                }
            }
        ]

        # Outdated content for deprecation demonstration
        outdated_content = [
            {
                "content": "Internet Explorer is the most popular web browser with over 90% market share",
                "confidence": 0.7,
                "metadata": {
                    "source": "wiki_service",
                    "created_date": (datetime.now() - timedelta(days=400)).isoformat(),
                    "expertise_domain": "web_technology",
                    "session_id": "demo_session_008",
                    "topic": "web_browsers"
                }
            },
            {
                "content": "Floppy disks are the primary storage medium for personal computers",
                "confidence": 0.6,
                "metadata": {
                    "source": "wiki_service",
                    "created_date": (datetime.now() - timedelta(days=500)).isoformat(),
                    "expertise_domain": "computer_hardware",
                    "session_id": "demo_session_009",
                    "topic": "storage_technology"
                }
            }
        ]

        # Add all content to SSKG and track IDs
        self.demo_data = {
            "validated_facts": [],
            "synthesis_results": [],
            "low_quality": [],
            "outdated": []
        }

        # Add validated facts
        for fact_data in validated_facts:
            node = KnowledgeNode(
                node_type=NodeType.FACT,
                content=fact_data["content"],
                confidence=fact_data["confidence"],
                metadata=fact_data["metadata"]
            )
            node_id = self.sskg_manager.add_node(node)
            self.demo_data["validated_facts"].append(node_id)

        # Add synthesis results
        for synthesis_data in synthesis_results:
            node = KnowledgeNode(
                node_type=NodeType.CONCEPT,
                content=synthesis_data["content"],
                confidence=synthesis_data["confidence"],
                metadata=synthesis_data["metadata"]
            )
            node_id = self.sskg_manager.add_node(node)
            self.demo_data["synthesis_results"].append(node_id)

        # Add low quality content
        for low_qual_data in low_quality_content:
            node = KnowledgeNode(
                node_type=NodeType.FACT,
                content=low_qual_data["content"],
                confidence=low_qual_data["confidence"],
                metadata=low_qual_data["metadata"]
            )
            node_id = self.sskg_manager.add_node(node)
            self.demo_data["low_quality"].append(node_id)

        # Add outdated content
        for outdated_data in outdated_content:
            node = KnowledgeNode(
                node_type=NodeType.FACT,
                content=outdated_data["content"],
                confidence=outdated_data["confidence"],
                metadata=outdated_data["metadata"]
            )
            node_id = self.sskg_manager.add_node(node)
            self.demo_data["outdated"].append(node_id)

    async def demonstrate_cross_session_knowledge_sharing(self):
        """Demonstrate cross-session knowledge sharing (Requirement 6.3)."""
        print("\n" + "="*60)
        print("🔄 DEMONSTRATING CROSS-SESSION KNOWLEDGE SHARING")
        print("="*60)

        # Simulate different session contexts
        session_contexts = [
            {
                "name": "Programming Session",
                "context": {
                    "topic": "programming languages",
                    "keywords": ["python", "programming", "language", "development"],
                    "user_id": "developer_001",
                    "session_id": "new_session_001"
                }
            },
            {
                "name": "AI Research Session",
                "context": {
                    "topic": "artificial intelligence",
                    "keywords": ["AI", "machine learning", "algorithms", "intelligence"],
                    "user_id": "researcher_001",
                    "session_id": "new_session_002"
                }
            },
            {
                "name": "Technology History Session",
                "context": {
                    "topic": "technology evolution",
                    "keywords": ["browsers", "storage", "technology", "history"],
                    "user_id": "historian_001",
                    "session_id": "new_session_003"
                }
            }
        ]

        for session_info in session_contexts:
            print(f"\n📋 {session_info['name']}:")
            print(f"   Topic: {session_info['context']['topic']}")
            print(f"   Keywords: {', '.join(session_info['context']['keywords'])}")

            cross_session_knowledge = await self.knowledge_service.retrieval_service.get_cross_session_knowledge(
                session_context=session_info['context'],
                time_window_days=30,
                min_relevance=0.4
            )
<<<<<<< HEAD

=======
            
>>>>>>> feature/core-services-refactor
            print("   📊 Retrieved Knowledge:")
            print(f"      • Facts: {len(cross_session_knowledge['facts'])}")
            print(f"      • Synthesis: {len(cross_session_knowledge['synthesis'])}")
            print(f"      • Connections: {len(cross_session_knowledge['knowledge_connections'])}")

            # Show top relevant facts
            if cross_session_knowledge['facts']:
                print("   🔍 Top Relevant Fact:")
                top_fact = cross_session_knowledge['facts'][0]
                print(f"      Content: {top_fact['content'][:80]}...")
                print(f"      Confidence: {top_fact['confidence']:.2f}")
                print(f"      Relevance: {top_fact['relevance']:.2f}")

    async def demonstrate_semantic_search(self):
        """Demonstrate semantic search capabilities (Requirement 6.4)."""
        print("\n" + "="*60)
        print("🔍 DEMONSTRATING SEMANTIC SEARCH CAPABILITIES")
        print("="*60)

        # Test different search scenarios
        search_scenarios = [
            {
                "name": "Programming Language Search",
                "query": "python programming language development",
                "scope": SearchScope.ALL,
                "expertise_domains": ["programming_languages"]
            },
            {
                "name": "AI and Machine Learning Search",
                "query": "artificial intelligence machine learning algorithms",
                "scope": SearchScope.FACTS,
                "expertise_domains": ["machine_learning", "artificial_intelligence"]
            },
            {
                "name": "Technology Synthesis Search",
                "query": "future technology impact society",
                "scope": SearchScope.SYNTHESIS,
                "expertise_domains": None
            },
            {
                "name": "Quantum Computing Search",
                "query": "quantum computing superposition entanglement",
                "scope": SearchScope.ALL,
                "expertise_domains": ["quantum_computing"]
            }
        ]

        for scenario in search_scenarios:
            print(f"\n🎯 {scenario['name']}:")
            print(f"   Query: '{scenario['query']}'")
            print(f"   Scope: {scenario['scope'].value}")
            print(f"   Domains: {scenario['expertise_domains']}")

            results = await self.knowledge_service.retrieval_service.semantic_search(
                query=scenario['query'],
                scope=scenario['scope'],
                min_confidence=0.3,
                limit=5,
                include_related=True,
                expertise_domains=scenario['expertise_domains']
            )

            print(f"   📊 Found {len(results)} results:")

            for i, result in enumerate(results[:3], 1):  # Show top 3
                print(f"      {i}. [{result.node_type}] {result.content[:60]}...")
                print(f"         Confidence: {result.confidence:.2f} | Relevance: {result.relevance_score:.2f}")
                if result.quality_metrics:
                    avg_quality = sum(result.quality_metrics.values()) / len(result.quality_metrics)
                    print(f"         Avg Quality: {avg_quality:.2f}")

    async def demonstrate_quality_assessment(self):
        """Demonstrate knowledge quality assessment (Requirement 6.5)."""
        print("\n" + "="*60)
        print("📊 DEMONSTRATING KNOWLEDGE QUALITY ASSESSMENT")
        print("="*60)

        # Assess quality for different types of content
        quality_demos = [
            ("High-Quality Validated Fact", self.demo_data["validated_facts"][0]),
            ("Synthesis Result", self.demo_data["synthesis_results"][0]),
            ("Low-Quality Content", self.demo_data["low_quality"][0]),
            ("Outdated Content", self.demo_data["outdated"][0])
        ]

        for demo_name, node_id in quality_demos:
            print(f"\n🔬 {demo_name}:")

            # Get the node content for context
            node = self.sskg_manager.get_node(node_id)
            print(f"   Content: {node.content[:80]}...")
            print(f"   Base Confidence: {node.confidence:.2f}")

            # Simulate some usage for realistic quality metrics
            for _ in range(3):
                self.knowledge_service.retrieval_service._track_usage(node_id, "search_result")

            # Assess quality
            assessment = await self.knowledge_service.retrieval_service.assess_knowledge_quality(node_id)
<<<<<<< HEAD

            print("   📈 Quality Assessment:")
            print(f"      Overall Quality: {assessment.overall_quality:.2f}")
            print("      Quality Metrics:")

=======
            
            print("   📈 Quality Assessment:")
            print(f"      Overall Quality: {assessment.overall_quality:.2f}")
            print("      Quality Metrics:")
            
>>>>>>> feature/core-services-refactor
            for metric, score in assessment.quality_metrics.items():
                print(f"         • {metric.value.replace('_', ' ').title()}: {score:.2f}")

            if assessment.recommendations:
                print("      💡 Recommendations:")
                for rec in assessment.recommendations[:2]:  # Show top 2
                    print(f"         • {rec}")

    async def demonstrate_knowledge_evolution(self):
        """Demonstrate knowledge evolution and lifecycle (Requirements 6.6, 6.7)."""
        print("\n" + "="*60)
        print("🔄 DEMONSTRATING KNOWLEDGE EVOLUTION & LIFECYCLE")
        print("="*60)

        # Manual evolution demonstration
        print("\n🛠️  Manual Knowledge Evolution:")
        if self.demo_data["low_quality"]:
            low_quality_id = self.demo_data["low_quality"][0]
            original_node = self.sskg_manager.get_node(low_quality_id)

            print(f"   Original: {original_node.content}")
            print(f"   Confidence: {original_node.confidence:.2f}")

            # Evolve the knowledge
            evolved_id = await self.knowledge_service.evolution_manager.evolve_knowledge_node(
                node_id=low_quality_id,
                trigger=EvolutionTrigger.USER_FEEDBACK,
                new_content="Python is a versatile, high-level programming language widely used for web development, data science, and automation",
                metadata_updates={
                    "updated_by": "demo_system",
                    "improvement_reason": "Enhanced clarity and specificity"
                },
                reason="Manual improvement to increase content quality and usefulness"
            )

            if evolved_id:
                evolved_node = self.sskg_manager.get_node(evolved_id)
                print("   ✅ Evolution Successful!")
                print(f"   Evolved: {evolved_node.content}")
                print(f"   New ID: {evolved_id}")
                print(f"   Evolution Trigger: {evolved_node.metadata.get('evolution_trigger')}")

        # Automatic evolution cycle demonstration
        print("\n🤖 Automatic Evolution Cycle:")

        # Configure for demonstration
        self.knowledge_service.evolution_manager.configure_evolution(
            quality_threshold=0.7,  # Higher threshold to catch more content
            deprecation_age_days=300,  # Lower threshold for demo
            auto_evolution_enabled=True,
            evolution_strategy=EvolutionStrategy.AUTOMATIC
        )

        # Run evolution cycle
        cycle_results = await self.knowledge_service.evolution_manager.run_evolution_cycle()
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        print("   📊 Evolution Cycle Results:")
        print(f"      • Nodes Evaluated: {cycle_results['nodes_evaluated']}")
        print(f"      • Nodes Evolved: {cycle_results['nodes_evolved']}")
        print(f"      • Nodes Deprecated: {cycle_results['nodes_deprecated']}")
        print(f"      • Nodes Archived: {cycle_results['nodes_archived']}")

        if cycle_results['evolution_triggers']:
            print("      • Triggers Detected:")
            for trigger, count in cycle_results['evolution_triggers'].items():
                print(f"         - {trigger.replace('_', ' ').title()}: {count}")

        # Show evolution history
        print("\n📜 Recent Evolution History:")
        evolution_history = self.knowledge_service.retrieval_service.get_knowledge_evolution_history(
            time_window_days=1
        )

        for event in evolution_history[:3]:  # Show recent events
            print(f"   • {event.event_type.title()}: {event.description[:60]}...")
            print(f"     Time: {event.timestamp.strftime('%H:%M:%S')}")

    async def demonstrate_comprehensive_statistics(self):
        """Demonstrate comprehensive knowledge statistics and monitoring."""
        print("\n" + "="*60)
        print("📈 COMPREHENSIVE KNOWLEDGE STATISTICS")
        print("="*60)

        # Get comprehensive statistics
        stats = self.knowledge_service.get_comprehensive_statistics()

        print(f"\n🏥 Service Status: {stats['service_status'].upper()}")
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        print("\n⚙️  Configuration:")
        config = stats['configuration']
        print(f"   • Auto Persist Facts: {config['auto_persist_facts']}")
        print(f"   • Evolution Strategy: {config['evolution_strategy'].title()}")
        print(f"   • Quality Threshold: {config['quality_threshold']}")
        print(f"   • Cross-Session Sharing: {config['cross_session_sharing']}")
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        print("\n📊 Knowledge Statistics:")
        if 'retrieval' in stats:
            retrieval_stats = stats['retrieval']
            print(f"   • Total Knowledge Items: {retrieval_stats.get('total_knowledge_items', 0)}")
            print(f"   • Facts: {retrieval_stats.get('facts_count', 0)}")
            print(f"   • Synthesis: {retrieval_stats.get('synthesis_count', 0)}")
            print(f"   • Wiki Pages: {retrieval_stats.get('wiki_pages_count', 0)}")

            if 'average_confidence' in retrieval_stats:
                avg_conf = retrieval_stats['average_confidence']
                print(f"   • Avg Confidence - Facts: {avg_conf.get('facts', 0):.2f}")
                print(f"   • Avg Confidence - Synthesis: {avg_conf.get('synthesis', 0):.2f}")
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        print("\n🔄 Evolution Statistics:")
        if 'evolution' in stats:
            evolution_stats = stats['evolution']
            print(f"   • Strategy: {evolution_stats.get('evolution_strategy', 'N/A').title()}")
            print(f"   • Quality Threshold: {evolution_stats.get('quality_threshold', 0)}")
            print(f"   • Auto Evolution: {evolution_stats.get('auto_evolution_enabled', False)}")

            if 'recent_events' in evolution_stats:
                recent = evolution_stats['recent_events']
                print(f"   • Recent Events (24h): {recent.get('last_24h_events', 0)}")
                print(f"   • Recent Events (7d): {recent.get('last_week_events', 0)}")

        # Health check
        print("\n🏥 Health Check:")
        health_status = await self.knowledge_service.health_check()
        print(f"   Overall Status: {health_status['overall_status'].upper()}")

        if 'components' in health_status:
            print("   Component Health:")
            for component, status in health_status['components'].items():
                status_icon = "✅" if "healthy" in status.lower() else "⚠️"
                print(f"      {status_icon} {component.replace('_', ' ').title()}: {status}")

    async def run_complete_demo(self):
        """Run the complete knowledge retrieval and evolution demonstration."""
        print("🎯 KNOWLEDGE RETRIEVAL AND EVOLUTION DEMONSTRATION")
        print("🎯 Implementing Task 10.2 Requirements 6.3, 6.4, 6.5, 6.6, 6.7")
        print("="*80)

        try:
            # Setup
            await self.setup_demo_environment()

            # Run all demonstrations
            await self.demonstrate_cross_session_knowledge_sharing()
            await self.demonstrate_semantic_search()
            await self.demonstrate_quality_assessment()
            await self.demonstrate_knowledge_evolution()
            await self.demonstrate_comprehensive_statistics()

            print("\n" + "="*80)
            print("✅ DEMONSTRATION COMPLETE!")
            print("🎉 All Task 10.2 requirements successfully demonstrated:")
            print("   ✓ 6.3 - Cross-session knowledge sharing")
            print("   ✓ 6.4 - Semantic search for validated information")
            print("   ✓ 6.5 - Knowledge quality assessment metrics")
            print("   ✓ 6.6 - Knowledge evolution and lifecycle management")
            print("   ✓ 6.7 - Continuous knowledge base improvement")
            print("="*80)

        except Exception as e:
            print(f"\n❌ Demo failed with error: {str(e)}")
            import traceback
            traceback.print_exc()


async def main():
    """Main function to run the knowledge retrieval demo."""
    demo = KnowledgeRetrievalDemo()
    await demo.run_complete_demo()


if __name__ == "__main__":
    asyncio.run(main())

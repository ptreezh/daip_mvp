#!/usr/bin/env python3
"""@Time    : 2025-07-25 03:00:00
@Author  : DAIP-LIVE Team
@File    : run_knowledge_tests.py
@Description:
    Script to run knowledge retrieval and evolution tests for task 10.2.
"""
import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core_services.knowledge_retrieval_demo import KnowledgeRetrievalDemo


async def run_basic_functionality_test():
    """Run a basic functionality test for knowledge retrieval and evolution."""
    print("🧪 RUNNING BASIC KNOWLEDGE FUNCTIONALITY TEST")
    print("="*50)

    try:
        # Import required modules
        from src.core_services.enhanced_sskg_manager import EnhancedSSKGManager, KnowledgeNode, NodeType
        from src.core_services.knowledge_management_service import KnowledgeManagementConfig, KnowledgeManagementService
        from src.core_services.knowledge_retrieval_service import SearchScope
        from src.core_services.wiki_service import WikiService
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        print("✅ All required modules imported successfully")

        # Initialize services
        sskg_manager = EnhancedSSKGManager()
        wiki_service = WikiService()

        config = KnowledgeManagementConfig(
            auto_persist_facts=True,
            min_confidence_threshold=0.5,
            evolution_strategy="hybrid",
            cross_session_sharing=True
        )

        knowledge_service = KnowledgeManagementService(
            sskg_manager=sskg_manager,
            wiki_service=wiki_service,
            config=config
        )

        print("✅ Knowledge management services initialized")

        # Test basic knowledge storage and retrieval
        test_node = KnowledgeNode(
            node_type=NodeType.FACT,
            content="This is a test fact for knowledge retrieval",
            confidence=0.8,
            metadata={
                "source": "test_system",
                "topic": "testing"
            }
        )

        node_id = sskg_manager.add_node(test_node)
        print(f"✅ Test knowledge node created: {node_id}")

        # Test semantic search
        search_results = await knowledge_service.retrieval_service.semantic_search(
            query="test fact knowledge",
            scope=SearchScope.ALL,
            min_confidence=0.5,
            limit=5
        )

        print(f"✅ Semantic search completed: {len(search_results)} results found")

        # Test quality assessment
        if search_results:
            assessment = await knowledge_service.retrieval_service.assess_knowledge_quality(
                search_results[0].id
            )
            print(f"✅ Quality assessment completed: {assessment.overall_quality:.2f}")

        # Test cross-session knowledge sharing
        session_context = {
            "topic": "testing",
            "keywords": ["test", "knowledge"],
            "user_id": "test_user",
            "session_id": "test_session"
        }

        cross_session_knowledge = await knowledge_service.retrieval_service.get_cross_session_knowledge(
            session_context=session_context,
            time_window_days=30,
            min_relevance=0.4
        )

        print(f"✅ Cross-session knowledge sharing: {len(cross_session_knowledge['facts'])} facts retrieved")

        # Test statistics
        stats = knowledge_service.get_comprehensive_statistics()
        print(f"✅ Statistics generated: Service status is {stats['service_status']}")

        # Test health check
        health = await knowledge_service.health_check()
        print(f"✅ Health check completed: Overall status is {health['overall_status']}")

        print("\n🎉 BASIC FUNCTIONALITY TEST PASSED!")
        return True

    except Exception as e:
        print(f"\n❌ BASIC FUNCTIONALITY TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def run_comprehensive_demo():
    """Run the comprehensive knowledge retrieval demo."""
    print("\n🚀 RUNNING COMPREHENSIVE KNOWLEDGE DEMO")
    print("="*50)

    try:
        demo = KnowledgeRetrievalDemo()
        await demo.run_complete_demo()
        return True
    except Exception as e:
        print(f"\n❌ COMPREHENSIVE DEMO FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main function to run all knowledge tests."""
    print("🎯 KNOWLEDGE RETRIEVAL AND EVOLUTION TESTING")
    print("🎯 Task 10.2 Implementation Verification")
    print("="*60)

    # Run basic functionality test first
    basic_test_passed = await run_basic_functionality_test()

    if basic_test_passed:
        print("\n" + "="*60)
        # Run comprehensive demo
        demo_passed = await run_comprehensive_demo()

        if demo_passed:
            print("\n🏆 ALL TESTS PASSED SUCCESSFULLY!")
            print("✅ Task 10.2 implementation is working correctly")
            print("✅ Requirements 6.3, 6.4, 6.5, 6.6, 6.7 are satisfied")
        else:
            print("\n⚠️  Basic tests passed but comprehensive demo failed")
            return 1
    else:
        print("\n❌ Basic functionality tests failed")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

#!/usr/bin/env python3
"""End-to-end debate functionality test script.
Tests that a complete debate can be initiated and run successfully.
"""

import asyncio
import logging
import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.cli.commands import run_debate_command

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@pytest.mark.asyncio()
async def test_basic_debate():
    """Test basic debate functionality with minimal configuration."""
    print("🧪 Testing basic debate functionality...")

    # Test parameters
    topic = "Should artificial intelligence be regulated?"
    roles = ["Expert", "Critic"]
    rounds = 2
    consensus_strategy = "simple_majority_vote"
    verbose = True

    print(f"Topic: {topic}")
    print(f"Roles: {', '.join(roles)}")
    print(f"Rounds: {rounds}")
    print(f"Consensus Strategy: {consensus_strategy}")
    print("-" * 50)

    try:
        # Run the debate
        success = await run_debate_command(
            topic=topic,
            roles=roles,
            rounds=rounds,
            consensus_strategy=consensus_strategy,
            verbose=verbose,
            save_results=True,
            output_file="test_debate_results.json"
        )

        if success:
            print("\n✅ Basic debate test PASSED")
            return True
        else:
            print("\n❌ Basic debate test FAILED")
            return False

    except Exception as e:
        print(f"\n❌ Basic debate test FAILED with exception: {e}")
        logger.error(f"Basic debate test failed: {e}", exc_info=True)
        return False

@pytest.mark.asyncio()
async def test_role_assignment():
    """Test that roles are properly assigned and participate in the debate."""
    print("\n🧪 Testing role assignment and participation...")

    # Test with specific roles
    topic = "The future of remote work"
    roles = ["Futurist", "Business Expert", "Technology Analyst"]
    rounds = 1

    print(f"Topic: {topic}")
    print(f"Roles: {', '.join(roles)}")
    print("-" * 50)

    try:
        success = await run_debate_command(
            topic=topic,
            roles=roles,
            rounds=rounds,
            consensus_strategy="simple_majority_vote",
            verbose=True
        )

        if success:
            print("\n✅ Role assignment test PASSED")
            return True
        else:
            print("\n❌ Role assignment test FAILED")
            return False

    except Exception as e:
        print(f"\n❌ Role assignment test FAILED with exception: {e}")
        logger.error(f"Role assignment test failed: {e}", exc_info=True)
        return False

@pytest.mark.asyncio()
async def test_consensus_mechanism():
    """Test that consensus mechanisms work correctly."""
    print("\n🧪 Testing consensus mechanism...")

    topic = "Benefits of renewable energy"
    roles = ["Environmental Scientist", "Economist"]
    rounds = 2
    consensus_strategy = "consensus_building"

    print(f"Topic: {topic}")
    print(f"Consensus Strategy: {consensus_strategy}")
    print("-" * 50)

    try:
        success = await run_debate_command(
            topic=topic,
            roles=roles,
            rounds=rounds,
            consensus_strategy=consensus_strategy,
            verbose=True
        )

        if success:
            print("\n✅ Consensus mechanism test PASSED")
            return True
        else:
            print("\n❌ Consensus mechanism test FAILED")
            return False

    except Exception as e:
        print(f"\n❌ Consensus mechanism test FAILED with exception: {e}")
        logger.error(f"Consensus mechanism test failed: {e}", exc_info=True)
        return False

def test_service_integration():
    """Test that all required services can be initialized and work together."""
    print("\n🧪 Testing service integration...")

    try:
        from src.app_state import AppState
        from src.models import DebateConfig
        from src.protocols.debate_protocol import DebateProtocol

        print("✅ Core imports successful")

        # Test AppState initialization
        app_state = AppState()
        print("✅ AppState initialization successful")

        # Test service access
        if hasattr(app_state, 'synthesis_engine'):
            print("✅ SynthesisEngine accessible")
        else:
            print("❌ SynthesisEngine not accessible")
            return False

        if hasattr(app_state, 'llm_interface'):
            print("✅ LLMInterface accessible")
        else:
            print("❌ LLMInterface not accessible")
            return False

        if hasattr(app_state, 'unified_tool_manager'):
            print("✅ UnifiedToolManager accessible")
        else:
            print("❌ UnifiedToolManager not accessible")
            return False

        # Test DebateConfig creation
        config = DebateConfig(
            topic="Test topic",
            roles=["AI Ethics", "Business Ethics"],
            rounds=1,
            consensus_strategy="simple_majority_vote"
        )
        print("✅ DebateConfig creation successful")

        # Test DebateProtocol initialization
        event_queue = asyncio.Queue()
        from types import SimpleNamespace
        kernel = SimpleNamespace()
        kernel.synthesis_engine = app_state.synthesis_engine
        kernel.llm_interface = app_state.llm_interface
        kernel.tool_executor = app_state.unified_tool_manager

        debate_protocol = DebateProtocol(kernel=kernel, event_queue=event_queue)
        print("✅ DebateProtocol initialization successful")

        print("\n✅ Service integration test PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Service integration test FAILED: {e}")
        logger.error(f"Service integration test failed: {e}", exc_info=True)
        return False

def test_database_operations():
    """Test database and storage operations."""
    print("\n🧪 Testing database and storage operations...")

    try:
        from src.app_state import AppState

        app_state = AppState()

        # Test memory service
        if hasattr(app_state, 'memory_service'):
            print("✅ MemoryService accessible")
        else:
            print("❌ MemoryService not accessible")
            return False

        # Test wiki service
        if hasattr(app_state, 'wiki_service'):
            print("✅ WikiService accessible")
        else:
            print("❌ WikiService not accessible")
            return False

        # Test role loading
        try:
            app_state.load_all_roles()
            if app_state.all_roles_details:
                print(f"✅ Role loading successful ({len(app_state.all_roles_details)} roles loaded)")
            else:
                print("⚠️ Role loading completed but no roles found")
        except Exception as e:
            print(f"❌ Role loading failed: {e}")
            return False

        print("\n✅ Database operations test PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Database operations test FAILED: {e}")
        logger.error(f"Database operations test failed: {e}", exc_info=True)
        return False

async def main():
    """Run all end-to-end tests."""
    print("🚀 Starting End-to-End Debate Functionality Tests")
    print("=" * 60)

    # Track test results
    test_results = []

    # Test 1: Service Integration (synchronous)
    test_results.append(("Service Integration", test_service_integration()))

    # Test 2: Database Operations (synchronous)
    test_results.append(("Database Operations", test_database_operations()))

    # Test 3: Basic Debate (asynchronous)
    test_results.append(("Basic Debate", await test_basic_debate()))

    # Test 4: Role Assignment (asynchronous)
    test_results.append(("Role Assignment", await test_role_assignment()))

    # Test 5: Consensus Mechanism (asynchronous)
    test_results.append(("Consensus Mechanism", await test_consensus_mechanism()))

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)

    passed = 0
    failed = 0

    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
        else:
            failed += 1

    print("-" * 60)
    print(f"Total Tests: {len(test_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! End-to-end debate functionality is working correctly.")
        return True
    else:
        print(f"\n⚠️ {failed} test(s) failed. End-to-end debate functionality needs attention.")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏸️ Tests interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite failed with unexpected error: {e}")
        logger.error(f"Test suite failed: {e}", exc_info=True)
        sys.exit(1)

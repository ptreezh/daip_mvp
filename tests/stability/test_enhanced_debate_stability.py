"""
Stability Tests for Enhanced Debate Features
"""

import asyncio
import gc
import os
import tempfile
import threading
import time

import pytest

from daip_live.config import ConfigManager
from daip_live.container import Container
from daip_live.core.models import (
    DebateCompleteEvent,
    DebateStartEvent,
    DebateTurnCompleteEvent,
)
from daip_live.p8_debate_system.history_tracker import DebateHistoryTracker


class TestEnhancedDebateStability:
    """Long-term stability tests for enhanced debate features."""

    def test_memory_leak_detection(self):
        """Test for memory leaks during extended usage."""
        import psutil

        # Measure memory before
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Create and destroy multiple debate systems
        for i in range(20):
            tracker = DebateHistoryTracker()

            # Simulate some operations
            session_id = f"memory_leak_test_{i:03d}"
            start_event = DebateStartEvent(
                topic=f"Memory Leak Test {i}",
                roles=["Leak_Test_Role"],
                rounds=1,
                session_id=session_id,
            )
            asyncio.run(tracker.start_tracking(start_event))

            turn_event = DebateTurnCompleteEvent(
                participant="Leak_Test_Role",
                round_number=1,
                content_preview=f"Memory test content {i}",
                session_id=session_id,
            )
            asyncio.run(tracker.add_turn(turn_event))

            complete_event = DebateCompleteEvent(
                session_id=session_id, summary=f"Memory leak test {i} completed"
            )
            asyncio.run(tracker.complete_debate(complete_event))

            # Explicitly delete the tracker
            del tracker
            gc.collect()

        # Force garbage collection
        gc.collect()

        # Measure memory after
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable after 20 iterations
        assert (
            memory_increase < 20.0
        )  # Should not grow more than 20MB for 20 operations

    def test_connection_leak_detection(self):
        """Test for resource connection leaks."""
        (len(os.listdir("/proc/self/fd")) if os.name != "nt" else 0)  # For Unix/Linux
        initial_threads = threading.active_count()

        # Perform operations that might create connections/resources
        tracker = DebateHistoryTracker()

        for i in range(10):
            session_id = f"connection_leak_test_{i:03d}"

            start_event = DebateStartEvent(
                topic=f"Connection Leak Test {i}",
                roles=["Conn_Test_Role"],
                rounds=1,
                session_id=session_id,
            )
            asyncio.run(tracker.start_tracking(start_event))

            turn_event = DebateTurnCompleteEvent(
                participant="Conn_Test_Role",
                round_number=1,
                content_preview=f"Connection test content {i}",
                session_id=session_id,
            )
            asyncio.run(tracker.add_turn(turn_event))

            complete_event = DebateCompleteEvent(
                session_id=session_id, summary=f"Connection leak test {i} completed"
            )
            asyncio.run(tracker.complete_debate(complete_event))

        # Check for resource growth
        final_threads = threading.active_count()
        thread_increase = final_threads - initial_threads

        assert thread_increase < 5  # Should not create too many threads

    def test_24_hour_stability_simulation(self):
        """Test simulated 24-hour stability with frequent operations."""
        start_time = time.time()
        target_duration = (
            5  # Test for 5 seconds in this automated test (simulating longer)
        )

        operation_count = 0

        while time.time() - start_time < target_duration:
            tracker = DebateHistoryTracker()

            # Perform a quick debate cycle
            session_id = f"stability_cycle_{operation_count:04d}"

            start_event = DebateStartEvent(
                topic=f"Stability Cycle Test {operation_count}",
                roles=["Stab_Role_A", "Stab_Role_B"],
                rounds=1,
                session_id=session_id,
            )
            asyncio.run(tracker.start_tracking(start_event))

            # Add turns
            for j in range(2):
                turn_event = DebateTurnCompleteEvent(
                    participant="Stab_Role_A" if j == 0 else "Stab_Role_B",
                    round_number=1,
                    content_preview=f"Stability test content {operation_count}-{j}",
                    session_id=session_id,
                )
                asyncio.run(tracker.add_turn(turn_event))

            complete_event = DebateCompleteEvent(
                session_id=session_id,
                summary=f"Stability cycle test {operation_count} completed",
            )
            asyncio.run(tracker.complete_debate(complete_event))

            operation_count += 1

            # Small delay to prevent overwhelming the system
            time.sleep(0.01)

        # Verify all operations completed successfully
        assert operation_count > 0

        # Test that we can still use the system after extensive operations
        final_tracker = DebateHistoryTracker()
        final_session_id = "post_stability_verification"

        start_event = DebateStartEvent(
            topic="Post-Stability Verification",
            roles=["Verification_Role"],
            rounds=1,
            session_id=final_session_id,
        )
        history = asyncio.run(final_tracker.start_tracking(start_event))
        assert history.session_id == final_session_id
        assert history.topic == "Post-Stability Verification"

        turn_event = DebateTurnCompleteEvent(
            participant="Verification_Role",
            round_number=1,
            content_preview="Post-stability verification content",
            session_id=final_session_id,
        )
        updated_history = asyncio.run(final_tracker.add_turn(turn_event))
        assert len(updated_history.turns) == 1
        assert updated_history.turns[0].content == "Post-stability verification content"

        complete_event = DebateCompleteEvent(
            session_id=final_session_id,
            summary="Post-stability verification completed successfully",
        )
        final_history = asyncio.run(final_tracker.complete_debate(complete_event))
        assert final_history.status == "completed"

    def test_component_reuse_after_operations(self):
        """Test that components can be reused after intensive operations."""
        tracker = DebateHistoryTracker()

        # Perform a series of operations
        for cycle in range(5):
            session_id = f"reuse_test_{cycle:02d}"

            # Start debate
            start_event = DebateStartEvent(
                topic=f"Reuse Test Cycle {cycle}",
                roles=["Reuse_Role_1", "Reuse_Role_2"],
                rounds=2,
                session_id=session_id,
            )
            history = asyncio.run(tracker.start_tracking(start_event))

            # Add multiple turns
            for round_num in range(1, 3):
                for participant in ["Reuse_Role_1", "Reuse_Role_2"]:
                    turn_event = DebateTurnCompleteEvent(
                        participant=participant,
                        round_number=round_num,
                        content_preview=f"Cycle {cycle}, Round {round_num}, {participant}",  # noqa: E501
                        session_id=session_id,
                    )
                    asyncio.run(tracker.add_turn(turn_event))

            # Complete debate
            complete_event = DebateCompleteEvent(
                session_id=session_id, summary=f"Reuse test cycle {cycle} completed"
            )
            final_history = asyncio.run(tracker.complete_debate(complete_event))

            # Verify this debate completed successfully
            assert final_history.status == "completed"
            assert len(final_history.turns) == 4  # 2 rounds * 2 participants
            assert final_history.total_rounds == 2

        # Verify that all debates are retrievable
        all_histories = asyncio.run(tracker.get_all_histories())
        assert len(all_histories) == 5

        for cycle in range(5):
            session_id = f"reuse_test_{cycle:02d}"
            history = asyncio.run(tracker.get_history(session_id))
            assert history is not None
            assert history.session_id == session_id
            assert len(history.turns) == 4
            assert history.status == "completed"

    def test_container_component_stability(self):
        """Test container component stability over extended usage."""

        # Create temporary config
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("""
database:
  path: ":memory:"
llm_provider:
  default_model: "mock-model"
  embedding_model: "mock-embedding"
knowledge_base:
  directory: "./test_knowledge"
role_manager:
  roles_dir: "./test_roles"
wiki:
  pages_directory: "./test_wiki"
debate:
  logs_directory: "./test_debate_logs"
paper:
  download_directory: "./test_paper"
""")
            config_path = f.name

        try:
            # Test multiple container instantiations
            for i in range(3):
                container = Container()
                # 源码权威: Container 无 config 属性，用 config_manager provider 覆盖
                # （dependency-injector override 机制）
                container.config_manager.override(ConfigManager(config_path))

                # Get components multiple times
                debate_history_tracker = container.debate_history_tracker()
                session_manager = container.session_manager()
                role_manager = container.role_manager()

                assert debate_history_tracker is not None
                assert session_manager is not None
                assert role_manager is not None

                # Test basic operations with components
                test_session_id = f"container_stability_{i:02d}"

                start_event = DebateStartEvent(
                    topic=f"Container Stability Test {i}",
                    roles=["Container_Test_Role"],
                    rounds=1,
                    session_id=test_session_id,
                )

                # Use the debate history tracker from the container
                history = asyncio.run(
                    debate_history_tracker.start_tracking(start_event)
                )
                assert history.session_id == test_session_id

                # Complete the operation
                complete_event = DebateCompleteEvent(
                    session_id=test_session_id,
                    summary=f"Container stability test {i} completed",
                )
                final_history = asyncio.run(
                    debate_history_tracker.complete_debate(complete_event)
                )
                assert final_history.status == "completed"

            # Test that the same container can be reused
            container = Container()
            container.config_manager.override(ConfigManager(config_path))

            reuse_tracker = container.debate_history_tracker()
            reuse_session_id = "container_reuse_test"

            start_event = DebateStartEvent(
                topic="Container Reuse Test",
                roles=["Reuse_Test_Role"],
                rounds=1,
                session_id=reuse_session_id,
            )
            history = asyncio.run(reuse_tracker.start_tracking(start_event))
            assert history.session_id == reuse_session_id

            complete_event = DebateCompleteEvent(
                session_id=reuse_session_id, summary="Container reuse test completed"
            )
            final_history = asyncio.run(reuse_tracker.complete_debate(complete_event))
            assert final_history.status == "completed"

        finally:
            os.unlink(config_path)

    def test_async_operation_consistency(self):
        """Test consistency of async operations."""

        async def run_async_consistency_test():
            tracker = DebateHistoryTracker()

            # Run multiple async operations in sequence
            results = []

            for i in range(10):
                session_id = f"async_consistency_{i:02d}"

                # Start debate
                start_event = DebateStartEvent(
                    topic=f"Async Consistency Test {i}",
                    roles=["Async_Role"],
                    rounds=1,
                    session_id=session_id,
                )
                await tracker.start_tracking(start_event)

                # Add turn
                turn_event = DebateTurnCompleteEvent(
                    participant="Async_Role",
                    round_number=1,
                    content_preview=f"Async consistency content {i}",
                    session_id=session_id,
                )
                await tracker.add_turn(turn_event)

                # Complete
                complete_event = DebateCompleteEvent(
                    session_id=session_id,
                    summary=f"Async consistency test {i} completed",
                )
                final_history = await tracker.complete_debate(complete_event)

                # Verify consistency
                assert final_history.status == "completed"
                assert final_history.session_id == session_id
                assert len(final_history.turns) == 1
                assert (
                    final_history.turns[0].content == f"Async consistency content {i}"
                )

                results.append(True)

            return all(results)

        result = asyncio.run(run_async_consistency_test())
        assert result is True

    def test_state_preservation_across_operations(self):
        """Test that state is preserved correctly across operations."""
        tracker = DebateHistoryTracker()

        # Create several debates with different characteristics
        debates = [
            {
                "id": "state_preserve_01",
                "topic": "Short Debate",
                "roles": ["Quick_A"],
                "rounds": 1,
                "turns": 1,
            },
            {
                "id": "state_preserve_02",
                "topic": "Medium Debate",
                "roles": ["Med_A", "Med_B"],
                "rounds": 2,
                "turns": 4,
            },
            {
                "id": "state_preserve_03",
                "topic": "Long Debate",
                "roles": ["Long_A", "Long_B", "Long_C"],
                "rounds": 3,
                "turns": 9,  # 3 rounds * 3 participants
            },
        ]

        for debate in debates:
            # Start debate
            start_event = DebateStartEvent(
                topic=debate["topic"],
                roles=debate["roles"],
                rounds=debate["rounds"],
                session_id=debate["id"],
            )
            history = asyncio.run(tracker.start_tracking(start_event))

            assert history.session_id == debate["id"]
            assert history.topic == debate["topic"]
            assert len(history.participants) == len(debate["roles"])
            assert history.total_rounds == debate["rounds"]

            # Add the expected number of turns
            for j in range(debate["turns"]):
                participant = debate["roles"][j % len(debate["roles"])]
                round_num = (j // len(debate["roles"])) + 1
                turn_event = DebateTurnCompleteEvent(
                    participant=participant,
                    round_number=round_num,
                    content_preview=f"Turn {j + 1} by {participant}",
                    session_id=debate["id"],
                )
                asyncio.run(tracker.add_turn(turn_event))

            # Complete debate
            complete_event = DebateCompleteEvent(
                session_id=debate["id"],
                summary=f"{debate['topic']} completed successfully",
            )
            final_history = asyncio.run(tracker.complete_debate(complete_event))

            assert final_history.status == "completed"
            assert len(final_history.turns) == debate["turns"]

        # Verify all debates remain retrievable with correct state
        for debate in debates:
            retrieved_history = asyncio.run(tracker.get_history(debate["id"]))
            assert retrieved_history is not None
            assert retrieved_history.session_id == debate["id"]
            assert retrieved_history.topic == debate["topic"]
            assert retrieved_history.status == "completed"
            assert len(retrieved_history.turns) == debate["turns"]

            # Verify content for first and last turn
            if retrieved_history.turns:
                assert "Turn 1" in retrieved_history.turns[0].content
                assert f"Turn {debate['turns']}" in retrieved_history.turns[-1].content

    def test_error_recovery_stability(self):
        """Test system stability after error conditions."""
        tracker = DebateHistoryTracker()

        # Test normal operation
        normal_session = "error_recovery_normal"
        start_event = DebateStartEvent(
            topic="Normal Operation Before Error",
            roles=["Normal_Role"],
            rounds=1,
            session_id=normal_session,
        )
        history = asyncio.run(tracker.start_tracking(start_event))
        assert history.session_id == normal_session

        normal_turn = DebateTurnCompleteEvent(
            participant="Normal_Role",
            round_number=1,
            content_preview="Normal content before error simulation",
            session_id=normal_session,
        )
        updated_history = asyncio.run(tracker.add_turn(normal_turn))
        assert len(updated_history.turns) == 1

        # Test that non-existent session returns None gracefully (error condition)
        none_result = asyncio.run(tracker.get_history("nonexistent_session"))
        assert none_result is None

        # Verify normal operation can continue after error
        continue_session = "error_recovery_continue"
        continue_start_event = DebateStartEvent(
            topic="Operation After Error",
            roles=["Continue_Role"],
            rounds=1,
            session_id=continue_session,
        )
        continue_history = asyncio.run(tracker.start_tracking(continue_start_event))
        assert continue_history.session_id == continue_session

        continue_turn = DebateTurnCompleteEvent(
            participant="Continue_Role",
            round_number=1,
            content_preview="Content after error handling",
            session_id=continue_session,
        )
        continue_updated = asyncio.run(tracker.add_turn(continue_turn))
        assert len(continue_updated.turns) == 1
        assert continue_updated.turns[0].content == "Content after error handling"

        # Complete both debates normally
        normal_complete = DebateCompleteEvent(
            session_id=normal_session, summary="Normal operation test completed"
        )
        final_normal = asyncio.run(tracker.complete_debate(normal_complete))
        assert final_normal.status == "completed"

        continue_complete = DebateCompleteEvent(
            session_id=continue_session, summary="Continue after error test completed"
        )
        final_continue = asyncio.run(tracker.complete_debate(continue_complete))
        assert final_continue.status == "completed"

        # Verify both debates are retrievable
        retrieved_normal = asyncio.run(tracker.get_history(normal_session))
        retrieved_continue = asyncio.run(tracker.get_history(continue_session))

        assert retrieved_normal is not None
        assert retrieved_continue is not None
        assert retrieved_normal.session_id == normal_session
        assert retrieved_continue.session_id == continue_session
        assert retrieved_normal.status == "completed"
        assert retrieved_continue.status == "completed"


if __name__ == "__main__":
    pytest.main([__file__])

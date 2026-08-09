"""
Stress Tests for Enhanced Debate Features
"""

import asyncio
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import psutil
import pytest

from daip_live.core.models import (
    DebateCompleteEvent,
    DebateStartEvent,
    DebateTurnCompleteEvent,
)
from daip_live.p8_debate_system.history_tracker import DebateHistoryTracker


class TestEnhancedDebateStress:
    """Stress tests for enhanced debate features."""

    def test_high_volume_concurrent_debates(self):
        """Test system performance with high volume of concurrent debates."""

        async def run_stress_test():
            tracker = DebateHistoryTracker()

            # Create a high volume of debates concurrently
            num_debates = 50
            tasks = []

            for i in range(num_debates):
                session_id = f"stress_concurrent_{i:03d}"

                start_event = DebateStartEvent(
                    topic=f"Stress Test Debate #{i}",
                    roles=[f"Role_{i}_A", f"Role_{i}_B"],
                    rounds=2,
                    session_id=session_id,
                )

                task = tracker.start_tracking(start_event)
                tasks.append(task)

            # Start all debates concurrently
            histories = await asyncio.gather(*tasks)

            # Add turns to each debate (more intensive operation)
            turn_tasks = []
            for i, history in enumerate(histories):
                # Each debate gets multiple turns to increase load
                for j in range(4):  # 4 turns per debate
                    turn_event = DebateTurnCompleteEvent(
                        participant=f"Role_{i}_A" if j % 2 == 0 else f"Role_{i}_B",
                        round_number=j // 2 + 1,
                        content_preview=f"Stress test debate {i}, turn {j}, content "
                        + "x" * 50,
                        session_id=f"stress_concurrent_{i:03d}",
                    )
                    task = tracker.add_turn(turn_event)
                    turn_tasks.append(task)

            # Execute all turns concurrently
            await asyncio.gather(*turn_tasks)

            # Complete all debates
            complete_tasks = []
            for i in range(num_debates):
                complete_event = DebateCompleteEvent(
                    session_id=f"stress_concurrent_{i:03d}",
                    summary=f"Stress test debate {i} completed successfully",
                )
                task = tracker.complete_debate(complete_event)
                complete_tasks.append(task)

            # Complete all debates concurrently
            final_histories = await asyncio.gather(*complete_tasks)

            # Verify all debates completed successfully
            assert len(final_histories) == num_debates
            for history in final_histories:
                assert history.status == "completed"
                assert len(history.turns) == 4  # Each debate had 4 turns

            return True

        start_time = time.time()
        result = asyncio.run(run_stress_test())
        end_time = time.time()

        execution_time = end_time - start_time

        assert result is True
        assert execution_time < 30.0  # Should complete in under 30 seconds

    def test_memory_usage_under_heavy_load(self):
        """Test memory usage under heavy system load."""
        import gc

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        tracker = DebateHistoryTracker()
        num_debates = 20

        # Create and run multiple debates to stress test memory
        for i in range(num_debates):
            session_id = f"stress_memory_{i:03d}"

            # Start debate
            start_event = DebateStartEvent(
                topic=f"Heavy Memory Load Test #{i}",
                roles=[f"Mem_Role_{i}_X", f"Mem_Role_{i}_Y"],
                rounds=3,
                session_id=session_id,
            )
            asyncio.run(tracker.start_tracking(start_event))

            # Add multiple turns with substantial content
            for j in range(6):  # 3 rounds * 2 roles = 6 turns
                content = (
                    f"Memory stress test content {i}-{j}: "
                    + "Very long content string " * 20
                )
                turn_event = DebateTurnCompleteEvent(
                    participant=f"Mem_Role_{i}_X" if j % 2 == 0 else f"Mem_Role_{i}_Y",
                    round_number=j // 2 + 1,
                    content_preview=content,
                    session_id=session_id,
                )
                asyncio.run(tracker.add_turn(turn_event))

            # Complete debate
            complete_event = DebateCompleteEvent(
                session_id=session_id,
                summary=f"Heavy memory load test {i} completed successfully",
            )
            asyncio.run(tracker.complete_debate(complete_event))

        # Force garbage collection to clean up
        gc.collect()

        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Under heavy load, memory increase should be reasonable
        assert (
            memory_increase < 100.0
        )  # Should not exceed 100MB increase for 20 debates

    def test_long_running_stability(self):
        """Test system stability over extended periods."""

        async def run_long_stability_test():
            tracker = DebateHistoryTracker()

            # Run a sustained load test for a longer period
            start_time = time.time()
            debate_count = 0

            # Run for approximately 10 seconds
            while time.time() - start_time < 10:
                session_id = f"long_stability_{debate_count:03d}"

                # Create a debate
                start_event = DebateStartEvent(
                    topic=f"Long Stability Test {debate_count}",
                    roles=["Stab_Role_A", "Stab_Role_B"],
                    rounds=1,
                    session_id=session_id,
                )
                await tracker.start_tracking(start_event)

                # Add a turn
                turn_event = DebateTurnCompleteEvent(
                    participant="Stab_Role_A",
                    round_number=1,
                    content_preview=f"Long running test turn {debate_count}",
                    session_id=session_id,
                )
                await tracker.add_turn(turn_event)

                # Complete the debate
                complete_event = DebateCompleteEvent(
                    session_id=session_id,
                    summary=f"Long running stability test {debate_count} completed",
                )
                final_history = await tracker.complete_debate(complete_event)

                # Verify completion
                assert final_history.status == "completed"

                debate_count += 1

                # Small delay to prevent overwhelming the system
                await asyncio.sleep(0.01)

            return debate_count > 0

        result = asyncio.run(run_long_stability_test())
        assert result is True

    def test_thread_pool_concurrency_stress(self):
        """Test system behavior with thread pool concurrency."""

        def run_single_debate(debate_id):
            """Run a single debate in a thread."""
            tracker = DebateHistoryTracker()

            session_id = f"thread_stress_{debate_id:03d}"
            start_event = DebateStartEvent(
                topic=f"Thread Pool Stress Test {debate_id}",
                roles=[f"Thread_Role_{debate_id}_P", f"Thread_Role_{debate_id}_Q"],
                rounds=2,
                session_id=session_id,
            )

            asyncio.run(tracker.start_tracking(start_event))

            for j in range(4):  # 4 turns per debate
                turn_event = DebateTurnCompleteEvent(
                    participant=f"Thread_Role_{debate_id}_P"
                    if j % 2 == 0
                    else f"Thread_Role_{debate_id}_Q",
                    round_number=j // 2 + 1,
                    content_preview=f"Thread stress debate {debate_id}, turn {j}",
                    session_id=session_id,
                )
                asyncio.run(tracker.add_turn(turn_event))

            complete_event = DebateCompleteEvent(
                session_id=session_id,
                summary=f"Thread pool stress test {debate_id} completed",
            )
            final_history = asyncio.run(tracker.complete_debate(complete_event))

            return final_history.status == "completed"

        # Use thread pool to run multiple debates concurrently
        num_threads = 20
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(run_single_debate, i) for i in range(num_threads)
            ]
            results = [future.result() for future in futures]

        # Verify all threads completed successfully
        assert all(results), (
            f"Not all threads completed successfully: {sum(results)}/{num_threads}"
        )

    def test_large_payload_handling(self):
        """Test system performance with large payloads."""

        async def run_large_payload_test():
            tracker = DebateHistoryTracker()

            session_id = "large_payload_001"

            # Create debate with roles that will have large content
            start_event = DebateStartEvent(
                topic="Large Payload Test Debate",
                roles=["Large_Payload_Pro", "Large_Payload_Con"],
                rounds=2,
                session_id=session_id,
            )

            await tracker.start_tracking(start_event)

            # Add turns with very large content
            large_content = (
                "Very detailed and extensive argument that contains a lot of information "  # noqa: E501
                * 500
            )
            for i in range(4):  # 2 rounds * 2 roles
                turn_event = DebateTurnCompleteEvent(
                    participant="Large_Payload_Pro"
                    if i % 2 == 0
                    else "Large_Payload_Con",
                    round_number=i // 2 + 1,
                    content_preview=large_content,
                    session_id=session_id,
                )
                await tracker.add_turn(turn_event)

            complete_event = DebateCompleteEvent(
                session_id=session_id,
                summary="Large payload test completed with very large content strings",
            )
            final_history = await tracker.complete_debate(complete_event)

            # Verify the large content was preserved
            assert final_history.status == "completed"
            assert len(final_history.turns) == 4

            for turn in final_history.turns:
                assert len(turn.content) > 1000  # Should contain large content
                assert "Very detailed and extensive argument" in turn.content

            return True

        start_time = time.time()
        result = asyncio.run(run_large_payload_test())
        end_time = time.time()

        execution_time = end_time - start_time

        assert result is True
        assert execution_time < 10.0  # Should complete in under 10 seconds

    def test_history_retention_and_retrieval_stress(self):
        """Test system performance with history retention and retrieval under stress."""

        async def run_history_stress():
            tracker = DebateHistoryTracker()

            # Create multiple debates
            num_debates = 30
            debate_ids = []

            for i in range(num_debates):
                session_id = f"history_stress_{i:03d}"
                debate_ids.append(session_id)

                start_event = DebateStartEvent(
                    topic=f"History Stress Test {i}",
                    roles=["Hist_Role_A", "Hist_Role_B"],
                    rounds=1,
                    session_id=session_id,
                )

                await tracker.start_tracking(start_event)

                turn_event = DebateTurnCompleteEvent(
                    participant="Hist_Role_A",
                    round_number=1,
                    content_preview=f"History stress content {i}",
                    session_id=session_id,
                )
                await tracker.add_turn(turn_event)

                complete_event = DebateCompleteEvent(
                    session_id=session_id, summary=f"History stress test {i} completed"
                )
                await tracker.complete_debate(complete_event)

            # Test retrieval of all histories multiple times to stress the retrieval system  # noqa: E501
            for retrieval_round in range(3):  # Do retrieval 3 times
                retrieved_histories = await tracker.get_all_histories()
                assert len(retrieved_histories) == num_debates

                # Verify each history individually
                for debate_id in debate_ids:
                    history = await tracker.get_history(debate_id)
                    assert history is not None
                    assert history.session_id == debate_id
                    assert history.status == "completed"

            return True

        result = asyncio.run(run_history_stress())
        assert result is True

    def test_component_resource_leak_detection(self):
        """Test for potential resource leaks in system components."""
        import gc

        # Monitor resources before
        initial_threads = threading.active_count()

        # Create and use multiple trackers to stress resource management
        for i in range(10):
            tracker = DebateHistoryTracker()

            # Use the tracker for operations
            session_id = f"resource_leak_test_{i}"
            start_event = DebateStartEvent(
                topic=f"Resource Leak Test {i}",
                roles=["Res_Role_X", "Res_Role_Y"],
                rounds=1,
                session_id=session_id,
            )
            asyncio.run(tracker.start_tracking(start_event))

            turn_event = DebateTurnCompleteEvent(
                participant="Res_Role_X",
                round_number=1,
                content_preview=f"Resource leak test content {i}",
                session_id=session_id,
            )
            asyncio.run(tracker.add_turn(turn_event))

            complete_event = DebateCompleteEvent(
                session_id=session_id, summary=f"Resource leak test {i} completed"
            )
            asyncio.run(tracker.complete_debate(complete_event))

            # Explicitly delete tracker
            del tracker
            gc.collect()

        # Check for resource leaks
        final_threads = threading.active_count()
        thread_increase = final_threads - initial_threads

        # Thread count should not increase significantly
        assert thread_increase < 5  # Allow small fluctuations but not massive increases

    def test_error_recovery_under_stress(self):
        """Test system recovery from errors under stress conditions."""

        async def run_error_recovery_test():
            tracker = DebateHistoryTracker()

            # Test normal operations first
            normal_session = "error_recovery_normal_001"
            start_event = DebateStartEvent(
                topic="Error Recovery Normal Test",
                roles=["Norm_Role_A", "Norm_Role_B"],
                rounds=1,
                session_id=normal_session,
            )
            await tracker.start_tracking(start_event)

            # Add a turn with normal content
            normal_turn = DebateTurnCompleteEvent(
                participant="Norm_Role_A",
                round_number=1,
                content_preview="Normal operation before error test",
                session_id=normal_session,
            )
            await tracker.add_turn(normal_turn)

            # Test error handling by trying to retrieve non-existent history
            none_result = await tracker.get_history("non_existent_session")
            assert none_result is None  # Should handle gracefully

            # Add another turn after error test
            post_error_turn = DebateTurnCompleteEvent(
                participant="Norm_Role_B",
                round_number=1,
                content_preview="Operation after error handling",
                session_id=normal_session,
            )
            await tracker.add_turn(post_error_turn)

            # Complete debate normally
            complete_event = DebateCompleteEvent(
                session_id=normal_session,
                summary="Error recovery test completed successfully after error handling",  # noqa: E501
            )
            final_history = await tracker.complete_debate(complete_event)

            # Verify normal operation continues after error handling
            assert final_history.status == "completed"
            assert len(final_history.turns) == 2
            assert (
                final_history.turns[0].content == "Normal operation before error test"
            )
            assert final_history.turns[1].content == "Operation after error handling"

            return True

        result = asyncio.run(run_error_recovery_test())
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__])

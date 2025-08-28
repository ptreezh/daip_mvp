import asyncio
import unittest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.core_services.conflict_resolution_system import (
    ConflictResolutionSystem,
    Conflict,
    ConflictType,
    ConflictPriority,
    ResolutionStrategy,
    ResolutionResult,
)

class TestConflictResolutionSystem(unittest.TestCase):
    def setUp(self):
        self.system = ConflictResolutionSystem()
        self.system._process_conflicts = AsyncMock() # Prevent background task from running

    def test_detect_conflict_concurrent_edit(self):
        async def run_test():
            operations = [
                {"resource_id": "doc1", "user_id": "user1", "type": "edit", "timestamp": datetime.now()},
                {"resource_id": "doc1", "user_id": "user2", "type": "edit", "timestamp": datetime.now()}
            ]
            conflict = await self.system.detect_conflict(operations)
            self.assertIsInstance(conflict, Conflict)
            self.assertEqual(conflict.conflict_type, ConflictType.CONCURRENT_EDIT)
            self.assertEqual(conflict.priority, ConflictPriority.HIGH)

        asyncio.run(run_test())

    def test_submit_conflict(self):
        async def run_test():
            conflict = Conflict(
                conflict_id="conflict1",
                conflict_type=ConflictType.COMMENT_CONFLICT,
                priority=ConflictPriority.MEDIUM,
                affected_resources=["comment1"],
                conflicting_operations=[],
                timestamp=datetime.now(),
                user_ids={"user1"}
            )
            conflict_id = await self.system.submit_conflict(conflict)
            self.assertEqual(conflict_id, "conflict1")
            self.assertIn("conflict1", self.system.active_conflicts)
            self.assertFalse(self.system.conflict_queue.empty())

        asyncio.run(run_test())

    def test_resolve_conflict_manual_review(self):
        async def run_test():
            conflict = Conflict(
                conflict_id="conflict2",
                conflict_type=ConflictType.COMMENT_CONFLICT,
                priority=ConflictPriority.MEDIUM,
                affected_resources=["comment2"],
                conflicting_operations=[
                    {"user_id": "user1", "content": "Comment A", "timestamp": datetime.now()},
                    {"user_id": "user2", "content": "Comment B", "timestamp": datetime.now()}
                ],
                timestamp=datetime.now(),
                user_ids={"user1", "user2"}
            )
            await self.system.submit_conflict(conflict)

            result = await self.system.resolve_conflict("conflict2", ResolutionStrategy.MANUAL_REVIEW)
            self.assertIsInstance(result, ResolutionResult)
            self.assertTrue(result.success)
            self.assertEqual(result.resolution_strategy, ResolutionStrategy.LAST_WRITE_WINS) # Manual review falls back to LWW
            self.assertIn("conflict2", self.system.resolved_conflicts)
            self.assertNotIn("conflict2", self.system.active_conflicts)

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()

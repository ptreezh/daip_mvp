import asyncio
import unittest
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from src.core_services.conflict_resolution_strategies import (
    MajorityVoteStrategy,
    ExpertJudgmentStrategy,
    ResolutionStrategy,
)
from src.core_services.conflict_resolution_system import Conflict, ResolutionResult, ConflictType, ConflictPriority

@dataclass
class ConflictStatement:
    agent_id: str
    statement: str
    confidence: float
    expert_rating: Optional[float] = None # For ExpertJudgmentStrategy

class TestConflictResolutionStrategies(unittest.TestCase):
    def test_majority_vote_strategy(self):
        async def run_test():
            strategy = MajorityVoteStrategy()
            conflict_id = "test_conflict_1"

            statements = [
                ConflictStatement(agent_id="agent1", statement="Option A", confidence=0.8),
                ConflictStatement(agent_id="agent2", statement="Option B", confidence=0.6),
                ConflictStatement(agent_id="agent3", statement="Option A", confidence=0.9),
            ]

            conflict = Conflict(
                conflict_id=conflict_id,
                conflict_type=ConflictType.DIRECT_CONTRADICTION,
                priority=ConflictPriority.MEDIUM,
                affected_resources=["resource1"],
                conflicting_operations=[
                    {"user_id": s.agent_id, "content": s.statement, "confidence": s.confidence}
                    for s in statements
                ],
                timestamp=datetime.now(),
                user_ids={s.agent_id for s in statements}
            )

            result = await strategy.resolve_conflict(conflict)

            self.assertIsInstance(result, ResolutionResult)
            self.assertTrue(result.success)
            self.assertEqual(result.resolution_strategy, ResolutionStrategy.VOTING)
            self.assertEqual(result.resolved_operations[0]["content"], "Option A")
            self.assertGreater(result.resolution_time, datetime(2020, 1, 1)) # Check if timestamp is set

        asyncio.run(run_test())

    def test_expert_judgment_strategy(self):
        async def run_test():
            strategy = ExpertJudgmentStrategy()
            conflict_id = "test_conflict_2"

            statements = [
                ConflictStatement(agent_id="agent1", statement="Option A", confidence=0.7, expert_rating=0.9),
                ConflictStatement(agent_id="agent2", statement="Option B", confidence=0.9, expert_rating=0.7),
                ConflictStatement(agent_id="agent3", statement="Option A", confidence=0.8, expert_rating=0.8),
            ]

            conflict = Conflict(
                conflict_id=conflict_id,
                conflict_type=ConflictType.DIRECT_CONTRADICTION,
                priority=ConflictPriority.MEDIUM,
                affected_resources=["resource2"],
                conflicting_operations=[
                    {"user_id": s.agent_id, "content": s.statement, "confidence": s.confidence, "expert_rating": s.expert_rating}
                    for s in statements
                ],
                timestamp=datetime.now(),
                user_ids={s.agent_id for s in statements}
            )

            result = await strategy.resolve_conflict(conflict)

            self.assertIsInstance(result, ResolutionResult)
            self.assertTrue(result.success)
            self.assertEqual(result.resolution_strategy, ResolutionStrategy.PRIORITY_BASED) # ExpertJudgment uses PriorityBased
            self.assertEqual(result.resolved_operations[0]["content"], "Option A")
            self.assertGreater(result.resolution_time, datetime(2020, 1, 1)) # Check if timestamp is set

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()

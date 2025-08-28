import asyncio
import unittest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.core_services.context_collaboration_engine import ContextCollaborationEngine

class TestContextCollaborationEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ContextCollaborationEngine()
        self.engine.shared_context_pool = {}
        self.engine.participant_context_relevance = {}

    def test_share_context(self):
        async def run_test():
            context_id = "ctx1"
            content = "This is a shared context about AI."
            source_participant_id = "user1"
            target_participant_ids = ["user2", "user3"]

            await self.engine.share_context(context_id, content, source_participant_id, target_participant_ids)

            self.assertIn(context_id, self.engine.shared_context_pool)
            shared_context = self.engine.shared_context_pool[context_id]
            self.assertEqual(shared_context["content"], content)
            self.assertEqual(shared_context["source_participant_id"], source_participant_id)
            self.assertIn("timestamp", shared_context)

            for target_id in target_participant_ids:
                self.assertIn(target_id, self.engine.participant_context_relevance)
                self.assertIn(context_id, self.engine.participant_context_relevance[target_id])
                self.assertGreater(self.engine.participant_context_relevance[target_id][context_id]["relevance_score"], 0)

        asyncio.run(run_test())

    def test_retrieve_shared_context(self):
        async def run_test():
            # Setup shared context
            context_id1 = "ctx1"
            content1 = "Context about machine learning."
            source_participant_id1 = "user1"
            target_participant_ids1 = ["user2"]
            await self.engine.share_context(context_id1, content1, source_participant_id1, target_participant_ids1)

            context_id2 = "ctx2"
            content2 = "Context about deep learning."
            source_participant_id2 = "user3"
            target_participant_ids2 = ["user2"]
            await self.engine.share_context(context_id2, content2, source_participant_id2, target_participant_ids2)

            # Retrieve context for user2
            retrieved_contexts = await self.engine.retrieve_shared_context("user2", "learning")

            self.assertEqual(len(retrieved_contexts), 2)
            self.assertIn(content1, [c["content"] for c in retrieved_contexts])
            self.assertIn(content2, [c["content"] for c in retrieved_contexts])

        asyncio.run(run_test())

    def test_update_context_relevance(self):
        async def run_test():
            context_id = "ctx1"
            content = "Context to update."
            source_participant_id = "user1"
            target_participant_ids = ["user2"]
            await self.engine.share_context(context_id, content, source_participant_id, target_participant_ids)

            # Update relevance
            await self.engine.update_context_relevance("user2", context_id, 0.9)

            self.assertEqual(self.engine.participant_context_relevance["user2"][context_id]["relevance_score"], 0.9)
            self.assertIn("last_updated", self.engine.participant_context_relevance["user2"][context_id])

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()

import asyncio
import unittest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.core_services.collaborative_review_environment import (
    CollaborativeReviewEnvironment,
    ReviewSession,
    ReviewComment,
    ReviewActionType,
    AnnotationType,
    DiscussionThread,
    DiscussionStatus,
)

class TestCollaborativeReviewEnvironment(unittest.TestCase):
    def setUp(self):
        self.mock_sskg_manager = AsyncMock()
        self.mock_memory_agent = AsyncMock()
        self.mock_allocator = MagicMock()
        self.mock_allocator.reviewer_profiles = {"reviewer_001": MagicMock(), "reviewer_002": MagicMock()}
        self.env = CollaborativeReviewEnvironment(
            sskg_manager=self.mock_sskg_manager,
            memory_agent=self.mock_memory_agent,
            allocator=self.mock_allocator
        )
        # Patch background tasks to prevent them from running during tests
        self.env._start_background_tasks = MagicMock()

        # Mock internal methods and dependencies
        self.env._record_event = AsyncMock()
        self.env.notification_system = MagicMock()
        self.env.notification_system.notify_participants = AsyncMock()
        self.env._broadcast_event = AsyncMock()

    def test_create_review_session(self):
        async def run_test():
            review_request_id = "req_123"
            participants = ["reviewer_001", "reviewer_002"]
            content = "Test document content"

            session = await self.env.create_review_session(
                review_request_id, participants, content
            )

            self.assertIsInstance(session, ReviewSession)
            self.assertIn(session.id, self.env.active_sessions)
            self.assertEqual(session.review_request_id, review_request_id)
            self.assertEqual(session.participants, participants)
            self.assertEqual(session.content, content)
            self.env._record_event.assert_called_once()
            self.env.notification_system.notify_participants.assert_called_once()

        asyncio.run(run_test())

    def test_add_comment(self):
        async def run_test():
            session_id = "session_123"
            reviewer_id = "reviewer_001"
            content = "This is a test comment."
            position = {"line_start": 1, "line_end": 2, "char_start": 0, "char_end": 10}

            # Create a mock session
            mock_session = ReviewSession(
                id=session_id,
                review_request_id="req_123",
                participants=[reviewer_id],
                content="",
                comments=[],
                annotations=[],
                discussions=[],
                created_at=datetime.now(),
                last_activity=datetime.now()
            )
            self.env.active_sessions[session_id] = mock_session

            comment = await self.env.add_comment(
                session_id, reviewer_id, content, position
            )

            self.assertIsInstance(comment, ReviewComment)
            self.assertEqual(comment.content, content)
            self.assertIn(comment, mock_session.comments)
            self.env._record_event.assert_called_once()
            self.env._broadcast_event.assert_called_once()

        asyncio.run(run_test())

    def test_get_session_state(self):
        async def run_test():
            session_id = "session_123"
            # Create a mock session with some data
            mock_session = ReviewSession(
                id=session_id,
                review_request_id="req_123",
                participants=["reviewer_001", "reviewer_002"],
                content="",
                comments=[
                    ReviewComment(id="c1", reviewer_id="r1", content="test", timestamp=datetime.now(), position={}, type=ReviewActionType.ADD_COMMENT)
                ],
                annotations=[
                    MagicMock(id="a1", reviewer_id="r1", type=AnnotationType.HIGHLIGHT, content="test", position={}, color="#000", timestamp=datetime.now())
                ],
                discussions=[
                    DiscussionThread(id="d1", title="test", description="test", initiator_id="r1", participants=set(), comments=[], status=DiscussionStatus.ACTIVE, created_at=datetime.now(), last_activity=datetime.now(), related_sections=[])
                ],
                created_at=datetime.now(),
                last_activity=datetime.now(),
                version_control={
                    "current_version": 1,
                    "versions": [{
                        "version": 1,
                        "content": "mock content",
                        "timestamp": datetime.now().isoformat(),
                        "author": "system"
                    }]
                }
            )
            self.env.active_sessions[session_id] = mock_session
            self.env.user_presence = {"reviewer_001": {"online": True, "last_seen": datetime.now()}}

            state = await self.env.get_session_state(session_id)

            self.assertEqual(state["session_id"], session_id)
            self.assertEqual(state["comments_count"], 1)
            self.assertEqual(state["annotations_count"], 1)
            self.assertEqual(state["discussions_count"], 1)
            self.assertEqual(len([p for p in state["participants_status"].values() if p.get("online")]), 1)

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()
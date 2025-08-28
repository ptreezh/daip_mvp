import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.core_services.chat_service import ChatService
from src.models import ChatMessage
from src.multi_role_chat import MultiRoleChatEngine
from src.virtual_role_chat.models import ChatRoom, ChatRoomConfig
from fastapi import HTTPException

class TestChatService(unittest.TestCase):
    def setUp(self):
        self.mock_app_state = MagicMock()
        self.mock_app_state.chat_engines = {}
        self.mock_app_state.expert_service = MagicMock()
        self.chat_service = ChatService(self.mock_app_state)

    def test_create_chat_engine_success(self):
        engine_id = "test_engine"
        model_type = "test_model"
        self.chat_service.create_chat_engine(engine_id, model_type)
        self.assertIn(engine_id, self.mock_app_state.chat_engines)
        self.assertIsInstance(self.mock_app_state.chat_engines[engine_id], MultiRoleChatEngine)
        self.assertEqual(self.mock_app_state.chat_engines[engine_id].model_type, model_type)

    def test_create_chat_engine_already_exists(self):
        engine_id = "test_engine"
        model_type = "test_model"
        self.chat_service.create_chat_engine(engine_id, model_type) # Create once
        with self.assertRaisesRegex(HTTPException, "Chat engine with this ID already exists."):
            self.chat_service.create_chat_engine(engine_id, model_type) # Try to create again

    def test_create_chat_engine_no_expert_service(self):
        engine_id = "test_engine"
        model_type = "test_model"
        self.mock_app_state.expert_service = None # Simulate no expert service
        with self.assertRaisesRegex(HTTPException, "Expert service is not available."):
            self.chat_service.create_chat_engine(engine_id, model_type)

    def test_get_room_details_success(self):
        async def run_test():
            engine_id = "test_engine"
            room_id = "test_room"
            self.chat_service.create_chat_engine(engine_id, "test_model")
            
            # Manually add a chat room to the engine's internal state
            mock_chat_room = ChatRoom(
                id=room_id,
                config=ChatRoomConfig(name="Test Room", topic="Test Topic", roles=[]),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self.mock_app_state.chat_engines[engine_id].chat_rooms[room_id] = mock_chat_room

            room = self.chat_service.get_room_details(engine_id, room_id)
            self.assertEqual(room.id, room_id)
            self.assertEqual(room.config.name, "Test Room")

        asyncio.run(run_test())

    def test_get_room_details_not_found(self):
        async def run_test():
            engine_id = "test_engine"
            room_id = "non_existent_room"
            self.chat_service.create_chat_engine(engine_id, "test_model")
            with self.assertRaisesRegex(HTTPException, r"Chat room not found."):
                self.chat_service.get_room_details(engine_id, room_id)

        asyncio.run(run_test())

    def test_send_message_to_room_success(self):
        async def run_test():
            engine_id = "test_engine"
            room_id = "test_room"
            sender_name = "User"
            content = "Hello, world!"

            self.chat_service.create_chat_engine(engine_id, "test_model")
            mock_chat_room = ChatRoom(
                id=room_id,
                config=ChatRoomConfig(name="Test Room", topic="Test Topic", roles=[]),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self.mock_app_state.chat_engines[engine_id].chat_rooms[room_id] = mock_chat_room
            self.mock_app_state.chat_engines[engine_id].room_messages[room_id] = []
            self.mock_app_state.chat_engines[engine_id].send_user_message = AsyncMock(return_value=True)

            success = await self.chat_service.send_message_to_room(engine_id, room_id, content, sender_name)
            self.assertTrue(success)
            self.mock_app_state.chat_engines[engine_id].send_user_message.assert_called_once_with(room_id, content, sender_name)

        asyncio.run(run_test())

    def test_send_message_to_room_not_found(self):
        async def run_test():
            engine_id = "test_engine"
            room_id = "non_existent_room"
            sender_name = "User"
            content = "Hello, world!"

            self.chat_service.create_chat_engine(engine_id, "test_model")
            with self.assertRaisesRegex(HTTPException, r"Chat room with ID 'non_existent_room' not found."):
                await self.chat_service.send_message_to_room(engine_id, room_id, content, sender_name)

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()
"""
Conversation Manager for Personal Assistant System
"""

import uuid
from datetime import datetime
from typing import Optional


class Message:
    def __init__(self, role: str, content: str, message_id: str = None):
        self.id = message_id or str(uuid.uuid4())
        self.role = role
        self.content = content
        self.timestamp = datetime.now()

    def to_dict(self):
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
        }


class Conversation:
    def __init__(self, title: str, conversation_id: str = None, context: str = ""):
        self.id = conversation_id or str(uuid.uuid4())
        self.title = title
        self.context = context
        self.messages: list[Message] = []
        self.created_at = datetime.now()
        self.updated_at = self.created_at

    def add_message(self, role: str, content: str) -> str:
        message = Message(role, content)
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message.id

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "context": self.context,
            "messages": [msg.to_dict() for msg in self.messages],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class ConversationManager:
    def __init__(self):
        self.conversations: dict[str, Conversation] = {}
        self.current_conversation: Optional[str] = None

    def start_conversation(self, title: str, context: str = "") -> str:
        conversation = Conversation(title, context=context)
        self.conversations[conversation.id] = conversation
        self.current_conversation = conversation.id
        return conversation.id

    def add_message(
        self, conversation_id: str, role: str, content: str
    ) -> Optional[str]:
        if conversation_id in self.conversations:
            return self.conversations[conversation_id].add_message(role, content)
        return None

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        return self.conversations.get(conversation_id)

    def list_conversations(self) -> list[Conversation]:
        return list(self.conversations.values())

    def delete_conversation(self, conversation_id: str) -> bool:
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            if self.current_conversation == conversation_id:
                self.current_conversation = None
            return True
        return False

    def get_conversation_summary(self, conversation_id: str) -> str:
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return "Conversation not found"

        if not conversation.messages:
            return f"Empty conversation: {conversation.title}"

        # Generate simple summary
        first_message = conversation.messages[0].content[:50]
        message_count = len(conversation.messages)
        return f"Conversation '{conversation.title}': {first_message}... ({message_count} messages)"  # noqa: E501

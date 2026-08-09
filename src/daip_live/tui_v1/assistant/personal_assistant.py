"""
Personal Assistant for newP6 TUI

Core personal assistant functionality with conversation management,
task handling, memory system, and skill execution.
"""

import json
import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class AssistantState(Enum):
    """Assistant operational states"""

    IDLE = "idle"
    THINKING = "thinking"
    RESPONDING = "responding"
    PROCESSING = "processing"
    ERROR = "error"


class PersonalAssistant:
    """Core personal assistant implementation"""

    def __init__(
        self,
        name: str,
        model_provider: str = "openai",
        model: str = "gpt-4",
        personality: str = "helpful and professional",
        specialization: str = "general assistance",
        preferences: Optional[dict[str, Any]] = None,
        assistant_id: Optional[str] = None,
    ):
        self.id = assistant_id or str(uuid.uuid4())
        self.name = name
        self.model_provider = model_provider
        self.model = model
        self.personality = personality
        self.specialization = specialization
        self.preferences = preferences or {}
        self.state = AssistantState.IDLE

        # Core managers
        self.conversation_manager = ConversationManager()
        self.task_manager = TaskManager()
        self.memory_manager = MemoryManager()
        self.skill_manager = SkillManager()

        # Assistant data
        self.created_at = datetime.now()
        self.last_active = self.created_at
        self.interaction_count = 0
        self.satisfaction_scores: list[float] = []

        # Learning data
        self.interaction_patterns: dict[str, int] = {}
        self.user_preferences: dict[str, Any] = {}
        self.common_responses: dict[str, str] = {}

        logger.info(f"Initialized PersonalAssistant: {self.name}")

    async def process_message(
        self,
        message: str,
        context: Optional[dict[str, Any]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> dict[str, Any]:
        """Process user message and generate response"""
        try:
            self.state = AssistantState.THINKING
            self.last_active = datetime.now()

            # Store user message in conversation
            conversation_id = self._get_or_create_conversation()
            self.conversation_manager.add_message(
                conversation_id=conversation_id, role="user", content=message
            )

            # Build context for response
            response_context = self._build_response_context(message, context)

            # Get model response
            response = await self._get_model_response(
                response_context, temperature, max_tokens
            )

            # Store assistant response
            self.conversation_manager.add_message(
                conversation_id=conversation_id,
                role="assistant",
                content=response["content"],
            )

            # Update interaction data
            self.interaction_count += 1
            self._update_interaction_patterns(message)

            self.state = AssistantState.IDLE
            return response

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self.state = AssistantState.ERROR
            return {
                "content": f"I apologize, but I encountered an error: {str(e)}",
                "error": True,
                "timestamp": datetime.now().isoformat(),
            }

    def _get_or_create_conversation(self) -> str:
        """Get current conversation or create new one"""
        if self.conversation_manager.current_conversation:
            return self.conversation_manager.current_conversation

        # Create new conversation
        conversation_id = self.conversation_manager.start_conversation(
            title=f"Conversation {len(self.conversation_manager.list_conversations()) + 1}",  # noqa: E501
            context=f"Conversation with {self.name}",
        )
        return conversation_id

    def _build_response_context(
        self, message: str, external_context: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Build context for model response"""
        # Get relevant memories
        relevant_memories = self.memory_manager.search_memories(message, limit=5)

        # Get conversation history
        conversation_history = self._get_conversation_context()

        # Build system prompt
        system_prompt = self._build_system_prompt()

        return {
            "system_prompt": system_prompt,
            "conversation_history": conversation_history,
            "relevant_memories": relevant_memories,
            "user_preferences": self.user_preferences,
            "current_message": message,
            "external_context": external_context or {},
            "assistant_profile": {
                "name": self.name,
                "personality": self.personality,
                "specialization": self.specialization,
                "preferences": self.preferences,
            },
        }

    def _build_system_prompt(self) -> str:
        """Build system prompt based on assistant profile"""
        prompt_parts = [
            f"You are {self.name}, a personal AI assistant.",
            f"Personality: {self.personality}",
            f"Specialization: {self.specialization}",
        ]

        if self.preferences:
            prompt_parts.append(
                f"Preferences: {json.dumps(self.preferences, indent=2)}"
            )

        # Add memory context
        if len(self.memory_manager.list_memories()) > 0:
            prompt_parts.append(
                "Remember: You have access to previous interactions and user preferences. Use this information to provide personalized responses."  # noqa: E501
            )

        prompt_parts.append(
            "Provide helpful, accurate, and personalized responses while maintaining your personality."  # noqa: E501
        )

        return "\n".join(prompt_parts)

    def _get_conversation_context(self, limit: int = 10) -> list[dict[str, str]]:
        """Get recent conversation history"""
        if not self.conversation_manager.current_conversation:
            return []

        conversation = self.conversation_manager.get_conversation(
            self.conversation_manager.current_conversation
        )
        if not conversation:
            return []

        # Get recent messages
        recent_messages = (
            conversation.messages[-limit:]
            if len(conversation.messages) > limit
            else conversation.messages
        )

        return [{"role": msg.role, "content": msg.content} for msg in recent_messages]

    async def _get_model_response(
        self,
        context: dict[str, Any],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> dict[str, Any]:
        """Get response from model provider"""
        try:
            # This would integrate with the actual model provider
            # For now, return a mock response

            context.get("system_prompt", "")
            conversation_history = context.get("conversation_history", [])
            current_message = context.get("current_message", "")

            # Simple response generation based on context
            response_content = self._generate_response(
                current_message, context, conversation_history
            )

            return {
                "content": response_content,
                "tokens": len(response_content.split()),
                "model": self.model,
                "timestamp": datetime.now().isoformat(),
                "context_used": bool(context.get("relevant_memories")),
            }

        except Exception as e:
            logger.error(f"Error getting model response: {e}")
            return {
                "content": "I apologize, but I'm having trouble connecting right now. Please try again.",  # noqa: E501
                "error": True,
                "timestamp": datetime.now().isoformat(),
            }

    def _generate_response(
        self, message: str, context: dict[str, Any], history: list[dict[str, str]]
    ) -> str:
        """Generate response based on context (mock implementation)"""
        message_lower = message.lower()

        # Check for specific patterns
        if any(greeting in message_lower for greeting in ["hello", "hi", "hey"]):
            return f"Hello! I'm {self.name}, your personal assistant. {self.personality[:50]}... How can I help you today?"  # noqa: E501

        if any(
            help_word in message_lower for help_word in ["help", "assist", "support"]
        ):
            return f"I'd be happy to help you! As your personal assistant specializing in {self.specialization}, I can assist with various tasks. What would you like help with?"  # noqa: E501

        # Check for task-related keywords
        if any(
            task_word in message_lower
            for task_word in ["task", "todo", "schedule", "remind"]
        ):
            return "I can help you manage tasks and schedules. Would you like me to create a new task, check your existing tasks, or set up reminders?"  # noqa: E501

        # Check for memory-related keywords
        if any(
            memory_word in message_lower
            for memory_word in ["remember", "note", "save", "store"]
        ):
            return "I can help you remember important information. What would you like me to store for future reference?"  # noqa: E501

        # Default response
        return f"I understand you're saying: {message}. As your personal assistant, I'm here to help. Could you tell me more about what you need assistance with?"  # noqa: E501

    def create_task(
        self,
        title: str,
        description: str,
        priority: str = "medium",
        due_date: Optional[datetime] = None,
        tags: Optional[list[str]] = None,
    ) -> str:
        """Create a new task"""
        task_id = self.task_manager.create_task(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            tags=tags,
        )

        logger.info(f"Created task: {title} ({task_id})")
        return task_id

    def get_tasks(self, status_filter: Optional[str] = None) -> list[dict[str, Any]]:
        """Get tasks with optional status filter"""
        if status_filter:
            return self.task_manager.filter_tasks(status=status_filter)
        return self.task_manager.list_tasks()

    def store_memory(
        self,
        content: str,
        category: str = "general",
        importance: str = "medium",
        tags: Optional[list[str]] = None,
    ) -> str:
        """Store information in memory"""
        memory_id = self.memory_manager.store_memory(
            content=content, category=category, importance=importance, tags=tags or []
        )

        logger.info(f"Stored memory: {content[:50]}... ({memory_id})")
        return memory_id

    def search_memories(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Search stored memories"""
        memories = self.memory_manager.search_memories(query, limit=limit)
        return [mem.to_dict() for mem in memories]

    def get_conversation_summary(self) -> str:
        """Get summary of current conversation"""
        if not self.conversation_manager.current_conversation:
            return "No active conversation"

        return self.conversation_manager.get_conversation_summary(
            self.conversation_manager.current_conversation
        )

    def record_interaction(
        self,
        user_input: str,
        assistant_response: str,
        satisfaction_score: Optional[float] = None,
    ) -> None:
        """Record interaction for learning"""
        if satisfaction_score is not None:
            self.satisfaction_scores.append(satisfaction_score)

        # Update patterns
        self._update_interaction_patterns(user_input)

        # Update user preferences based on patterns
        self._update_user_preferences(user_input, assistant_response)

    def _update_interaction_patterns(self, message: str) -> None:
        """Update interaction pattern tracking"""
        # Extract key topics
        words = message.lower().split()
        for word in words:
            if len(word) > 3:  # Track meaningful words
                self.interaction_patterns[word] = (
                    self.interaction_patterns.get(word, 0) + 1
                )

    def _update_user_preferences(
        self, user_input: str, assistant_response: str
    ) -> None:
        """Update user preferences based on interactions"""
        # Simple preference extraction
        user_input_lower = user_input.lower()

        # Check for time preferences
        if any(
            time_word in user_input_lower
            for time_word in ["morning", "afternoon", "evening"]
        ):
            for time_word in ["morning", "afternoon", "evening"]:
                if time_word in user_input_lower:
                    self.user_preferences["preferred_time"] = time_word
                    break

        # Check for formality preferences
        if any(
            formal_word in user_input_lower
            for formal_word in ["formal", "professional", "casual", "friendly"]
        ):
            if "formal" in user_input_lower or "professional" in user_input_lower:
                self.user_preferences["formality"] = "formal"
            elif "casual" in user_input_lower or "friendly" in user_input_lower:
                self.user_preferences["formality"] = "casual"

    def get_learning_insights(self) -> dict[str, Any]:
        """Get insights from learning data"""
        if not self.satisfaction_scores:
            return {"message": "No interaction data available yet"}

        avg_satisfaction = sum(self.satisfaction_scores) / len(self.satisfaction_scores)

        # Get common topics
        common_topics = sorted(
            self.interaction_patterns.items(), key=lambda x: x[1], reverse=True
        )[:5]

        return {
            "total_interactions": self.interaction_count,
            "average_satisfaction": avg_satisfaction,
            "common_topics": [
                {"topic": topic, "count": count} for topic, count in common_topics
            ],
            "user_preferences": self.user_preferences,
            "conversation_count": len(self.conversation_manager.list_conversations()),
            "task_count": len(self.task_manager.list_tasks()),
            "memory_count": len(self.memory_manager.list_memories()),
        }

    def backup_state(self) -> dict[str, Any]:
        """Backup complete assistant state"""
        return {
            "assistant_info": {
                "id": self.id,
                "name": self.name,
                "model_provider": self.model_provider,
                "model": self.model,
                "personality": self.personality,
                "specialization": self.specialization,
                "preferences": self.preferences,
                "created_at": self.created_at.isoformat(),
            },
            "learning_data": {
                "interaction_count": self.interaction_count,
                "satisfaction_scores": self.satisfaction_scores,
                "interaction_patterns": self.interaction_patterns,
                "user_preferences": self.user_preferences,
                "common_responses": self.common_responses,
            },
            "conversations": [
                conv.to_dict()
                for conv in self.conversation_manager.list_conversations()
            ],
            "tasks": [task.to_dict() for task in self.task_manager.list_tasks()],
            "memories": [mem.to_dict() for mem in self.memory_manager.list_memories()],
            "skills": [skill.to_dict() for skill in self.skill_manager.list_skills()],
        }

    def restore_state(self, backup_data: dict[str, Any]) -> bool:
        """Restore assistant state from backup"""
        try:
            # Restore basic info
            if "assistant_info" in backup_data:
                info = backup_data["assistant_info"]
                self.id = info.get("id", self.id)
                self.name = info.get("name", self.name)
                self.personality = info.get("personality", self.personality)
                self.specialization = info.get("specialization", self.specialization)
                self.preferences = info.get("preferences", {})

            # Restore learning data
            if "learning_data" in backup_data:
                learning = backup_data["learning_data"]
                self.interaction_count = learning.get("interaction_count", 0)
                self.satisfaction_scores = learning.get("satisfaction_scores", [])
                self.interaction_patterns = learning.get("interaction_patterns", {})
                self.user_preferences = learning.get("user_preferences", {})
                self.common_responses = learning.get("common_responses", {})

            logger.info(f"Restored assistant state: {self.name}")
            return True

        except Exception as e:
            logger.error(f"Error restoring assistant state: {e}")
            return False

    def get_status(self) -> dict[str, Any]:
        """Get current assistant status"""
        return {
            "id": self.id,
            "name": self.name,
            "state": self.state.value,
            "model": f"{self.model_provider}/{self.model}",
            "last_active": self.last_active.isoformat(),
            "interaction_count": self.interaction_count,
            "current_conversation": self.conversation_manager.current_conversation,
            "active_tasks": len(self.task_manager.filter_tasks(status="active")),
            "memory_count": len(self.memory_manager.list_memories()),
            "satisfaction_avg": sum(self.satisfaction_scores)
            / len(self.satisfaction_scores)
            if self.satisfaction_scores
            else 0.0,
        }

    def __str__(self) -> str:
        """String representation"""
        return f"PersonalAssistant({self.name}@{self.model})"

    def __repr__(self) -> str:
        """Detailed string representation"""
        return (
            f"PersonalAssistant(id={self.id[:8]}..., name='{self.name}', "
            f"model='{self.model}', state={self.state.value}, "
            f"interactions={self.interaction_count})"
        )


# Import supporting classes (would be implemented in separate files)
class ConversationManager:
    """Conversation management (placeholder)"""

    def __init__(self):
        self.conversations = {}
        self.current_conversation = None

    def start_conversation(self, title, context=""):
        conv_id = str(uuid.uuid4())
        self.conversations[conv_id] = {"id": conv_id, "title": title, "messages": []}
        self.current_conversation = conv_id
        return conv_id

    def add_message(self, conversation_id, role, content):
        if conversation_id in self.conversations:
            msg_id = str(uuid.uuid4())
            self.conversations[conversation_id]["messages"].append(
                {
                    "id": msg_id,
                    "role": role,
                    "content": content,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            return msg_id
        return None

    def get_conversation(self, conversation_id):
        return self.conversations.get(conversation_id)

    def list_conversations(self):
        return list(self.conversations.values())

    def get_conversation_summary(self, conversation_id):
        conv = self.get_conversation(conversation_id)
        if not conv:
            return "No conversation found"
        return f"Conversation '{conv['title']}' with {len(conv['messages'])} messages"


class TaskManager:
    """Task management (placeholder)"""

    def __init__(self):
        self.tasks = {}

    def create_task(
        self, title, description, priority="medium", due_date=None, tags=None
    ):
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {
            "id": task_id,
            "title": title,
            "description": description,
            "priority": priority,
            "due_date": due_date,
            "tags": tags or [],
            "status": "active",
            "created_at": datetime.now(),
        }
        return task_id

    def filter_tasks(self, status=None):
        return [
            task
            for task in self.tasks.values()
            if not status or task.get("status") == status
        ]

    def list_tasks(self):
        return list(self.tasks.values())


class MemoryManager:
    """Memory management (placeholder)"""

    def __init__(self):
        self.memories = {}

    def store_memory(self, content, category="general", importance="medium", tags=None):
        memory_id = str(uuid.uuid4())
        self.memories[memory_id] = {
            "id": memory_id,
            "content": content,
            "category": category,
            "importance": importance,
            "tags": tags or [],
            "created_at": datetime.now(),
        }
        return memory_id

    def search_memories(self, query, limit=10):
        query_lower = query.lower()
        results = []
        for mem in self.memories.values():
            if query_lower in mem["content"].lower():
                results.append(mem)
                if len(results) >= limit:
                    break
        return results

    def list_memories(self):
        return list(self.memories.values())


class SkillManager:
    """Skill management (placeholder)"""

    def __init__(self):
        self.skills = {}

    def list_skills(self):
        return list(self.skills.values())

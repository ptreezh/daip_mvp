"""
DAIP Personal Assistant Tests for newP6 TUI

This test suite implements TDD approach for personal assistant functionality.
Tests are written first (RED), then implementation follows (GREEN), then refactoring.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime, timedelta
from enum import Enum
import json

# Import real implementations (will fail initially - RED phase)
from daip_live.tui_v1.assistant.personal_assistant import PersonalAssistant
from daip_live.tui_v1.assistant.assistant_profile import AssistantProfile
from daip_live.tui_v1.assistant.conversation_manager import ConversationManager
from daip_live.tui_v1.assistant.task_manager import TaskManager, TaskStatus
from daip_live.tui_v1.assistant.memory_manager import MemoryManager
from daip_live.tui_v1.assistant.assistant_skills import SkillManager, SkillType


class TestAssistantProfile:
    """Test assistant profile functionality"""

    def test_profile_creation(self):
        """Test assistant profile creation"""
        # This will fail initially - driving need for AssistantProfile class
        profile = AssistantProfile(
            name="Alex",
            personality="friendly and helpful",
            specialization="general assistance",
            preferences={"language": "English", "formality": "casual"}
        )

        assert profile is not None
        assert profile.name == "Alex"
        assert profile.personality == "friendly and helpful"
        assert profile.specialization == "general assistance"
        assert profile.preferences["language"] == "English"
        assert hasattr(profile, 'created_at')

    def test_profile_update(self):
        """Test updating assistant profile"""
        profile = AssistantProfile(
            name="Assistant",
            personality="professional",
            specialization="tech support"
        )

        profile.update_personality("more casual and conversational")
        profile.update_specialization("customer service")

        assert profile.personality == "more casual and conversational"
        assert profile.specialization == "customer service"

    def test_profile_preferences(self):
        """Test managing profile preferences"""
        profile = AssistantProfile("Bot", "neutral", "general")

        profile.set_preference("response_length", "medium")
        profile.set_preference("include_emoji", True)
        profile.set_preference("formality_level", 0.5)

        assert profile.get_preference("response_length") == "medium"
        assert profile.get_preference("include_emoji") == True
        assert profile.get_preference("formality_level") == 0.5

    def test_profile_serialization(self):
        """Test profile serialization"""
        profile = AssistantProfile(
            name="TestBot",
            personality="test personality",
            specialization="testing",
            preferences={"test": "value"}
        )

        profile_dict = profile.to_dict()

        assert profile_dict["name"] == "TestBot"
        assert profile_dict["personality"] == "test personality"
        assert profile_dict["preferences"]["test"] == "value"
        assert "created_at" in profile_dict

    def test_profile_from_dict(self):
        """Test creating profile from dictionary"""
        data = {
            "name": "RestoredBot",
            "personality": "restored personality",
            "specialization": "restored specialization",
            "preferences": {"key": "value"}
        }

        profile = AssistantProfile.from_dict(data)

        assert profile.name == "RestoredBot"
        assert profile.personality == "restored personality"
        assert profile.specialization == "restored specialization"
        assert profile.preferences["key"] == "value"


class TestConversationManager:
    """Test conversation management functionality"""

    def test_conversation_creation(self):
        """Test conversation creation"""
        # This will fail initially - driving need for ConversationManager class
        manager = ConversationManager()

        assert manager is not None
        assert len(manager.list_conversations()) == 0
        assert hasattr(manager, 'conversations')
        assert hasattr(manager, 'current_conversation')

    def test_start_conversation(self):
        """Test starting a new conversation"""
        manager = ConversationManager()

        conversation_id = manager.start_conversation(
            title="Project Discussion",
            context="Discussing new project ideas"
        )

        assert conversation_id is not None
        assert manager.current_conversation == conversation_id
        assert len(manager.list_conversations()) == 1

    def test_add_message(self):
        """Test adding messages to conversation"""
        manager = ConversationManager()
        conv_id = manager.start_conversation("Test Chat")

        # Add user message
        user_msg_id = manager.add_message(
            conversation_id=conv_id,
            role="user",
            content="Hello, assistant!"
        )

        # Add assistant response
        assistant_msg_id = manager.add_message(
            conversation_id=conv_id,
            role="assistant",
            content="Hello! How can I help you today?"
        )

        assert user_msg_id is not None
        assert assistant_msg_id is not None

        conversation = manager.get_conversation(conv_id)
        assert len(conversation.messages) == 2
        assert conversation.messages[0].content == "Hello, assistant!"
        assert conversation.messages[1].content == "Hello! How can I help you today?"

    def test_conversation_summary(self):
        """Test generating conversation summary"""
        manager = ConversationManager()
        conv_id = manager.start_conversation("Planning Session")

        # Add messages
        manager.add_message(conv_id, "user", "We need to plan our quarterly goals")
        manager.add_message(conv_id, "assistant", "Great! Let's start with your main objectives")
        manager.add_message(conv_id, "user", "Focus on product development and team growth")

        summary = manager.get_conversation_summary(conv_id)

        assert "planning" in summary.lower()
        assert "quarterly" in summary.lower()
        assert "product development" in summary.lower()

    def test_search_conversations(self):
        """Test searching conversations"""
        manager = ConversationManager()

        # Create multiple conversations
        conv1 = manager.start_conversation("Project Alpha")
        conv2 = manager.start_conversation("Marketing Plan")

        manager.add_message(conv1, "user", "Working on project alpha features")
        manager.add_message(conv2, "user", "Planning marketing strategy")

        # Search conversations
        results = manager.search_conversations("project")

        assert len(results) == 1
        assert results[0].title == "Project Alpha"

    def test_export_conversation(self):
        """Test exporting conversation"""
        manager = ConversationManager()
        conv_id = manager.start_conversation("Test Export")

        manager.add_message(conv_id, "user", "Test message")
        manager.add_message(conv_id, "assistant", "Test response")

        exported = manager.export_conversation(conv_id, format="json")

        assert "messages" in exported
        assert len(exported["messages"]) == 2
        assert exported["title"] == "Test Export"

    def test_delete_conversation(self):
        """Test deleting conversation"""
        manager = ConversationManager()
        conv_id = manager.start_conversation("To Delete")

        assert len(manager.list_conversations()) == 1

        success = manager.delete_conversation(conv_id)

        assert success == True
        assert len(manager.list_conversations()) == 0


class TestTaskManager:
    """Test task management functionality"""

    def test_task_creation(self):
        """Test task creation"""
        # This will fail initially - driving need for TaskManager class
        manager = TaskManager()

        task_id = manager.create_task(
            title="Complete project documentation",
            description="Write comprehensive docs for the new feature",
            priority="high",
            due_date=datetime.now() + timedelta(days=3)
        )

        assert task_id is not None
        assert len(manager.list_tasks()) == 1

    def test_task_status_update(self):
        """Test updating task status"""
        manager = TaskManager()

        task_id = manager.create_task(
            title="Test Task",
            description="Test description"
        )

        # Update status
        manager.update_task_status(task_id, TaskStatus.IN_PROGRESS)
        manager.update_task_status(task_id, TaskStatus.COMPLETED)

        task = manager.get_task(task_id)
        assert task.status == TaskStatus.COMPLETED

    def test_task_assignment(self):
        """Test assigning tasks"""
        manager = TaskManager()

        task_id = manager.create_task(
            title="Assigned Task",
            description="Task to be assigned"
        )

        manager.assign_task(task_id, "team_member_1")
        manager.assign_task(task_id, "team_member_2")

        task = manager.get_task(task_id)
        assert "team_member_1" in task.assignees
        assert "team_member_2" in task.assignees

    def test_task_deadline_tracking(self):
        """Test task deadline tracking"""
        manager = TaskManager()
        due_date = datetime.now() + timedelta(days=1)

        task_id = manager.create_task(
            title="Urgent Task",
            description="Due tomorrow",
            due_date=due_date
        )

        overdue_tasks = manager.get_overdue_tasks()
        assert len(overdue_tasks) == 0

        # Simulate time passing
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime.now() + timedelta(days=2)
            overdue_tasks = manager.get_overdue_tasks()
            assert len(overdue_tasks) == 1

    def test_task_filtering(self):
        """Test filtering tasks"""
        manager = TaskManager()

        # Create tasks with different priorities
        high_task = manager.create_task("High Priority Task", "Desc", priority="high")
        medium_task = manager.create_task("Medium Priority Task", "Desc", priority="medium")
        low_task = manager.create_task("Low Priority Task", "Desc", priority="low")

        high_priority_tasks = manager.filter_tasks(priority="high")
        assert len(high_priority_tasks) == 1

        completed_task = manager.create_task("Completed Task", "Desc")
        manager.update_task_status(completed_task, TaskStatus.COMPLETED)

        active_tasks = manager.filter_tasks(status=TaskStatus.ACTIVE)
        assert len(active_tasks) == 3


class TestMemoryManager:
    """Test memory management functionality"""

    def test_memory_creation(self):
        """Test memory manager creation"""
        # This will fail initially - driving need for MemoryManager class
        memory = MemoryManager(max_memory_items=1000)

        assert memory is not None
        assert memory.max_memory_items == 1000
        assert hasattr(memory, 'short_term_memory')
        assert hasattr(memory, 'long_term_memory')

    def test_store_memory(self):
        """Test storing memories"""
        memory = MemoryManager()

        memory_id = memory.store_memory(
            content="User prefers morning meetings",
            category="preference",
            importance="medium",
            tags=["meetings", "schedule"]
        )

        assert memory_id is not None
        assert len(memory.list_memories()) == 1

    def test_retrieve_memories(self):
        """Test retrieving memories"""
        memory = MemoryManager()

        # Store multiple memories
        memory.store_memory("User likes coffee", "preference", "high", ["drinks"])
        memory.store_memory("User works in tech", "fact", "medium", ["work", "industry"])
        memory.store_memory("Project deadline next week", "task", "high", ["deadline"])

        # Retrieve by category
        preferences = memory.retrieve_memories(category="preference")
        assert len(preferences) == 1
        assert "coffee" in preferences[0].content

        # Retrieve by tags
        work_memories = memory.retrieve_memories(tags=["work"])
        assert len(work_memories) == 1
        assert "tech" in work_memories[0].content

    def test_memory_search(self):
        """Test searching memories"""
        memory = MemoryManager()

        memory.store_memory("User's favorite color is blue", "preference", "medium")
        memory.store_memory("User drives a Toyota", "fact", "low")
        memory.store_memory("Meeting scheduled for tomorrow", "task", "high")

        # Search for "color"
        results = memory.search_memories("color")
        assert len(results) == 1
        assert "blue" in results[0].content

        # Search for "meeting"
        results = memory.search_memories("meeting")
        assert len(results) == 1
        assert "tomorrow" in results[0].content

    def test_memory_cleanup(self):
        """Test memory cleanup"""
        memory = MemoryManager(max_memory_items=2)

        # Store more memories than the limit
        memory.store_memory("Memory 1", "test", "medium")
        memory.store_memory("Memory 2", "test", "medium")
        memory.store_memory("Memory 3", "test", "medium")

        # Should only keep the most recent 2 memories
        assert len(memory.list_memories()) == 2
        assert "Memory 3" in [mem.content for mem in memory.list_memories()]
        assert "Memory 2" in [mem.content for mem in memory.list_memories()]

    def test_memory_importance_decay(self):
        """Test memory importance decay over time"""
        memory = MemoryManager()

        memory_id = memory.store_memory(
            "Important memory",
            "important",
            importance="high"
        )

        # Simulate time passing and decay
        memory.apply_importance_decay()
        updated_memory = memory.get_memory(memory_id)

        # Importance should be reduced slightly
        assert updated_memory.importance < 1.0


class TestSkillManager:
    """Test skill management functionality"""

    def test_skill_creation(self):
        """Test skill creation"""
        # This will fail initially - driving need for SkillManager class
        skills = SkillManager()

        skill_id = skills.register_skill(
            name="code_review",
            description="Review and improve code quality",
            skill_type=SkillType.ANALYSIS,
            capabilities=["syntax_check", "logic_analysis", "best_practices"]
        )

        assert skill_id is not None
        assert len(skills.list_skills()) == 1

    def test_skill_execution(self):
        """Test skill execution"""
        skills = SkillManager()

        skills.register_skill(
            name="text_summarization",
            description="Summarize long texts",
            skill_type=SkillType.PROCESSING,
            capabilities=["extract_key_points", "generate_summary"]
        )

        # Mock skill execution
        with patch.object(skills, '_execute_skill') as mock_execute:
            mock_execute.return_value = {
                "summary": "Text discusses project planning and deadlines",
                "key_points": ["project planning", "deadlines"],
                "confidence": 0.85
            }

            result = skills.execute_skill(
                "text_summarization",
                input_data={"text": "Long text about project planning and deadlines..."}
            )

            assert result["confidence"] == 0.85
            assert "project planning" in result["summary"]

    def test_skill_recommendation(self):
        """Test skill recommendation based on context"""
        skills = SkillManager()

        # Register different skills
        skills.register_skill("data_analysis", "Analyze datasets", SkillType.ANALYSIS)
        skills.register_skill("writing_assistance", "Help with writing", SkillType.CREATION)
        skills.register_skill("code_generation", "Generate code", SkillType.CREATION)

        # Get recommendations for different contexts
        code_recommendations = skills.recommend_skills(context="programming task")
        writing_recommendations = skills.recommend_skills(context="writing a report")

        assert any("code" in skill.name.lower() for skill in code_recommendations)
        assert any("writing" in skill.name.lower() for skill in writing_recommendations)

    def test_skill_chaining(self):
        """Test chaining multiple skills"""
        skills = SkillManager()

        skills.register_skill("data_extraction", "Extract data", SkillType.PROCESSING)
        skills.register_skill("data_analysis", "Analyze data", SkillType.ANALYSIS)
        skills.register_skill("report_generation", "Generate reports", SkillType.CREATION)

        # Create skill chain
        chain = skills.create_skill_chain([
            "data_extraction",
            "data_analysis",
            "report_generation"
        ])

        # Mock chain execution
        with patch.object(skills, '_execute_chain') as mock_chain:
            mock_chain.return_value = {
                "extracted_data": {"key": "value"},
                "analysis": {"trend": "increasing"},
                "report": "Data shows increasing trend"
            }

            result = skills.execute_chain(chain, input_data={"source": "document.pdf"})

            assert "extracted_data" in result
            assert "analysis" in result
            assert "report" in result

    def test_skill_learning(self):
        """Test skill improvement through learning"""
        skills = SkillManager()

        skill_id = skills.register_skill(
            "classification",
            "Classify text",
            SkillType.ANALYSIS
        )

        # Record successful execution
        skills.record_skill_execution(skill_id, success=True, quality_score=0.8)
        skills.record_skill_execution(skill_id, success=True, quality_score=0.9)
        skills.record_skill_execution(skill_id, success=False, quality_score=0.3)

        skill = skills.get_skill(skill_id)
        assert skill.success_rate == 0.67  # 2/3 success rate
        assert skill.average_quality == 0.67  # Average of successful executions

    def test_skill_compatibility(self):
        """Test checking skill compatibility"""
        skills = SkillManager()

        skills.register_skill("text_processing", "Process text", SkillType.PROCESSING)
        skills.register_skill("image_analysis", "Analyze images", SkillType.ANALYSIS)

        # Check compatibility
        text_text = skills.check_compatibility("text_processing", "text_processing")
        text_image = skills.check_compatibility("text_processing", "image_analysis")

        assert text_text.compatible == True
        assert text_image.compatible == False


class TestPersonalAssistant:
    """Test personal assistant functionality"""

    def test_assistant_creation(self):
        """Test personal assistant creation"""
        # This will fail initially - driving need for PersonalAssistant class
        assistant = PersonalAssistant(
            name="Alex",
            model_provider="openai",
            model="gpt-4"
        )

        assert assistant is not None
        assert assistant.name == "Alex"
        assert assistant.model_provider == "openai"
        assert assistant.model == "gpt-4"
        assert hasattr(assistant, 'profile')
        assert hasattr(assistant, 'conversation_manager')

    def test_assistant_initialization(self):
        """Test assistant initialization with profile"""
        profile = AssistantProfile(
            name="Sam",
            personality="professional but friendly",
            specialization="business analysis"
        )

        assistant = PersonalAssistant(
            name="Sam",
            model_provider="anthropic",
            model="claude-3",
            profile=profile
        )

        assert assistant.profile.personality == "professional but friendly"
        assert assistant.profile.specialization == "business analysis"

    @pytest.mark.asyncio
    async def test_assistant_conversation(self):
        """Test having a conversation with assistant"""
        assistant = PersonalAssistant(
            name="Test Assistant",
            model_provider="openai",
            model="gpt-4"
        )

        # Mock model response
        with patch.object(assistant, '_get_model_response') as mock_response:
            mock_response.return_value = {
                "content": "Hello! I'm your personal assistant. How can I help you today?",
                "tokens": 15
            }

            response = await assistant.process_message("Hello, assistant!")

            assert "Hello!" in response["content"]
            assert response["tokens"] == 15

    @pytest.mark.asyncio
    async def test_assistant_task_handling(self):
        """Test assistant task handling"""
        assistant = PersonalAssistant("Task Assistant", "openai", "gpt-4")

        # Create a task
        task_id = assistant.task_manager.create_task(
            title="Schedule meeting",
            description="Schedule team meeting for next week"
        )

        # Mock task processing
        with patch.object(assistant, '_process_task') as mock_process:
            mock_process.return_value = {
                "status": "completed",
                "result": "Meeting scheduled for Tuesday at 2 PM",
                "action_items": ["Send calendar invites", "Prepare agenda"]
            }

            result = await assistant.handle_task(task_id)

            assert result["status"] == "completed"
            assert "Tuesday at 2 PM" in result["result"]

    def test_assistant_memory_usage(self):
        """Test assistant using memory to remember context"""
        assistant = PersonalAssistant("Memory Assistant", "openai", "gpt-4")

        # Store information in memory
        assistant.memory_manager.store_memory(
            "User prefers morning meetings",
            "preference",
            "high",
            ["meetings", "schedule"]
        )

        assistant.memory_manager.store_memory(
            "User is working on Project Alpha",
            "fact",
            "medium",
            ["project", "work"]
        )

        # Retrieve relevant memories
        memories = assistant.memory_manager.retrieve_memories(tags=["meetings"])

        assert len(memories) == 1
        assert "morning meetings" in memories[0].content

    @pytest.mark.asyncio
    async def test_assistant_skill_usage(self):
        """Test assistant using specialized skills"""
        assistant = PersonalAssistant("Skilled Assistant", "openai", "gpt-4")

        # Register skills
        assistant.skill_manager.register_skill(
            "data_analysis",
            "Analyze data patterns",
            SkillType.ANALYSIS
        )

        # Mock skill execution
        with patch.object(assistant.skill_manager, 'execute_skill') as mock_skill:
            mock_skill.return_value = {
                "patterns": ["increasing trend", "seasonal variation"],
                "insights": ["Q4 shows highest growth"],
                "confidence": 0.92
            }

            result = await assistant.use_skill(
                "data_analysis",
                {"data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
            )

            assert "increasing trend" in str(result["patterns"])
            assert result["confidence"] == 0.92

    def test_assistant_learning(self):
        """Test assistant learning from interactions"""
        assistant = PersonalAssistant("Learning Assistant", "openai", "gpt-4")

        # Record conversation patterns
        assistant.record_interaction(
            user_input="Can you help me with Python code?",
            assistant_response="I'd be happy to help with Python!",
            satisfaction_score=0.9
        )

        assistant.record_interaction(
            user_input="How do I create a function?",
            assistant_response="Here's how to create a Python function...",
            satisfaction_score=0.85
        )

        # Get learning insights
        insights = assistant.get_learning_insights()

        assert "Python" in insights["common_topics"]
        assert insights["average_satisfaction"] > 0.8

    def test_assistant_backup_restore(self):
        """Test assistant backup and restore"""
        assistant = PersonalAssistant("Backup Test", "openai", "gpt-4")

        # Add some data
        assistant.conversation_manager.start_conversation("Test Conversation")
        assistant.memory_manager.store_memory("Test memory", "test", "medium")

        # Backup assistant state
        backup_data = assistant.backup_state()

        # Create new assistant and restore
        new_assistant = PersonalAssistant("Restored Assistant", "openai", "gpt-4")
        restore_success = new_assistant.restore_state(backup_data)

        assert restore_success == True
        assert len(new_assistant.conversation_manager.list_conversations()) == 1
        assert len(new_assistant.memory_manager.list_memories()) == 1

    def test_assistant_analytics(self):
        """Test assistant analytics"""
        assistant = PersonalAssistant("Analytics Assistant", "openai", "gpt-4")

        # Add some activity
        assistant.conversation_manager.start_conversation("Chat 1")
        assistant.task_manager.create_task("Task 1")
        assistant.memory_manager.store_memory("Memory 1", "test", "medium")

        # Get analytics
        analytics = assistant.get_analytics()

        assert "conversation_count" in analytics
        assert analytics["conversation_count"] == 1
        assert "task_count" in analytics
        assert analytics["task_count"] == 1
        assert "memory_count" in analytics
        assert analytics["memory_count"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
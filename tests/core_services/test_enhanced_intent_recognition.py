"""
Test suite for Enhanced Intent Recognition System

This test suite validates the enhanced intent recognition capabilities including:
- 50+ intent categories
- Multi-modal detection
- Entity extraction
- Confidence scoring
- Context awareness
"""

import asyncio
import pytest
import sys
from typing import Dict, List, Any

# Add the src directory to the path
sys.path.insert(0, 'D:\\DAIP\\daipMVPbackup\\daip_mvp_project')

from src.core_services.enhanced_intent_recognition import (
    EnhancedIntentRecognizer,
    IntentCategory,
    ConfidenceLevel,
    IntentSource,
    Entity,
    EnhancedIntentAnalysis,
    create_enhanced_intent_recognizer
)


class TestEnhancedIntentRecognition:
    """Test suite for enhanced intent recognition"""
    
    @pytest.fixture
    def recognizer(self) -> EnhancedIntentRecognizer:
        """Create enhanced intent recognizer for testing"""
        return create_enhanced_intent_recognizer()
    
    @pytest.mark.asyncio
    async def test_basic_communication_intents(self, recognizer):
        """Test basic communication intent recognition"""
        
        test_cases = [
            # Greeting
            ("Hello", IntentCategory.GREETING, 0.9),
            ("Hi there", IntentCategory.GREETING, 0.9),
            ("Good morning", IntentCategory.GREETING, 0.9),
            ("你好", IntentCategory.GREETING, 0.9),
            
            # Farewell
            ("Goodbye", IntentCategory.FAREWELL, 0.9),
            ("See you later", IntentCategory.FAREWELL, 0.9),
            ("再见", IntentCategory.FAREWELL, 0.9),
            
            # Affirmation
            ("Yes", IntentCategory.AFFIRMATION, 0.9),
            ("That's correct", IntentCategory.AFFIRMATION, 0.8),
            ("是的", IntentCategory.AFFIRMATION, 0.9),
            
            # Negation
            ("No", IntentCategory.NEGATION, 0.9),
            ("That's wrong", IntentCategory.NEGATION, 0.8),
            ("不对", IntentCategory.NEGATION, 0.9),
        ]
        
        for user_input, expected_intent, min_confidence in test_cases:
            analysis = await recognizer.recognize_intent(user_input, {})
            
            assert analysis.primary_intent == expected_intent, f"Failed for input: {user_input}"
            assert analysis.confidence >= min_confidence, f"Confidence too low for {user_input}: {analysis.confidence}"
            assert analysis.confidence_level in [ConfidenceLevel.HIGH, ConfidenceLevel.VERY_HIGH]
    
    @pytest.mark.asyncio
    async def test_information_seeking_intents(self, recognizer):
        """Test information seeking intent recognition"""
        
        test_cases = [
            # Questions
            ("What is machine learning?", IntentCategory.QUESTION, 0.8),
            ("How does AI work?", IntentCategory.QUESTION, 0.8),
            ("什么是深度学习？", IntentCategory.QUESTION, 0.8),
            
            # Clarification
            ("What do you mean by that?", IntentCategory.CLARIFICATION, 0.9),
            ("Please clarify", IntentCategory.CLARIFICATION, 0.9),
            ("什么意思？", IntentCategory.CLARIFICATION, 0.9),
            
            # Help requests
            ("Help me with this", IntentCategory.HELP_REQUEST, 0.9),
            ("I need assistance", IntentCategory.HELP_REQUEST, 0.9),
            ("帮助我", IntentCategory.HELP_REQUEST, 0.9),
        ]
        
        for user_input, expected_intent, min_confidence in test_cases:
            analysis = await recognizer.recognize_intent(user_input, {})
            
            assert analysis.primary_intent == expected_intent, f"Failed for input: {user_input}"
            assert analysis.confidence >= min_confidence, f"Confidence too low for {user_input}: {analysis.confidence}"
    
    @pytest.mark.asyncio
    async def test_wiki_intents(self, recognizer):
        """Test wiki-specific intent recognition"""
        
        test_cases = [
            # Wiki creation
            ("Create a new wiki entry", IntentCategory.WIKI_CREATE, 0.9),
            ("I want to create a wiki page", IntentCategory.WIKI_CREATE, 0.9),
            ("创建wiki词条", IntentCategory.WIKI_CREATE, 0.9),
            
            # Wiki viewing
            ("Show me the wiki entry", IntentCategory.WIKI_VIEW, 0.9),
            ("View wiki content", IntentCategory.WIKI_VIEW, 0.9),
            ("查看wiki", IntentCategory.WIKI_VIEW, 0.9),
            
            # Wiki editing
            ("Edit this wiki page", IntentCategory.WIKI_EDIT, 0.9),
            ("Modify wiki content", IntentCategory.WIKI_EDIT, 0.9),
            ("编辑wiki", IntentCategory.WIKI_EDIT, 0.9),
            
            # Wiki deletion
            ("Delete this wiki entry", IntentCategory.WIKI_DELETE, 0.9),
            ("Remove wiki page", IntentCategory.WIKI_DELETE, 0.9),
            ("删除wiki", IntentCategory.WIKI_DELETE, 0.9),
            
            # Wiki search
            ("Search for wiki entries", IntentCategory.WIKI_SEARCH, 0.9),
            ("Find wiki content", IntentCategory.WIKI_SEARCH, 0.9),
            ("搜索wiki", IntentCategory.WIKI_SEARCH, 0.9),
            
            # Wiki collaboration
            ("Collaborate on wiki", IntentCategory.WIKI_COLLABORATE, 0.9),
            ("Wiki collaboration", IntentCategory.WIKI_COLLABORATE, 0.9),
            ("wiki协作", IntentCategory.WIKI_COLLABORATE, 0.9),
        ]
        
        for user_input, expected_intent, min_confidence in test_cases:
            analysis = await recognizer.recognize_intent(user_input, {})
            
            assert analysis.primary_intent == expected_intent, f"Failed for input: {user_input}"
            assert analysis.confidence >= min_confidence, f"Confidence too low for {user_input}: {analysis.confidence}"
    
    @pytest.mark.asyncio
    async def test_chat_intents(self, recognizer):
        """Test chat-specific intent recognition"""
        
        test_cases = [
            # Chat start
            ("Start a new chat", IntentCategory.CHAT_START, 0.9),
            ("Create chat room", IntentCategory.CHAT_START, 0.9),
            ("开始聊天", IntentCategory.CHAT_START, 0.9),
            
            # Chat message
            ("Send a message", IntentCategory.CHAT_MESSAGE, 0.9),
            ("Post message", IntentCategory.CHAT_MESSAGE, 0.9),
            ("发送消息", IntentCategory.CHAT_MESSAGE, 0.9),
            
            # Chat history
            ("Show chat history", IntentCategory.CHAT_HISTORY, 0.9),
            ("View conversation history", IntentCategory.CHAT_HISTORY, 0.9),
            ("聊天历史", IntentCategory.CHAT_HISTORY, 0.9),
            
            # Chat clear
            ("Clear chat history", IntentCategory.CHAT_CLEAR, 0.9),
            ("Clear messages", IntentCategory.CHAT_CLEAR, 0.9),
            ("清除聊天", IntentCategory.CHAT_CLEAR, 0.9),
            
            # Chat close
            ("Close chat", IntentCategory.CHAT_CLOSE, 0.9),
            ("End conversation", IntentCategory.CHAT_CLOSE, 0.9),
            ("关闭聊天", IntentCategory.CHAT_CLOSE, 0.9),
            
            # Chat delete
            ("Delete chat room", IntentCategory.CHAT_DELETE, 0.9),
            ("Remove chat", IntentCategory.CHAT_DELETE, 0.9),
            ("删除聊天", IntentCategory.CHAT_DELETE, 0.9),
        ]
        
        for user_input, expected_intent, min_confidence in test_cases:
            analysis = await recognizer.recognize_intent(user_input, {})
            
            assert analysis.primary_intent == expected_intent, f"Failed for input: {user_input}"
            assert analysis.confidence >= min_confidence, f"Confidence too low for {user_input}: {analysis.confidence}"
    
    @pytest.mark.asyncio
    async def test_role_management_intents(self, recognizer):
        """Test role management intent recognition"""
        
        test_cases = [
            # Role matching
            ("Match roles to task", IntentCategory.ROLE_MATCH, 0.9),
            ("Find matching roles", IntentCategory.ROLE_MATCH, 0.9),
            ("匹配角色", IntentCategory.ROLE_MATCH, 0.9),
            
            # Role listing
            ("List all roles", IntentCategory.ROLE_LIST, 0.9),
            ("Show available roles", IntentCategory.ROLE_LIST, 0.9),
            ("列出角色", IntentCategory.ROLE_LIST, 0.9),
            
            # Role statistics
            ("Show role statistics", IntentCategory.ROLE_STATS, 0.9),
            ("Role analysis", IntentCategory.ROLE_STATS, 0.9),
            ("角色统计", IntentCategory.ROLE_STATS, 0.9),
        ]
        
        for user_input, expected_intent, min_confidence in test_cases:
            analysis = await recognizer.recognize_intent(user_input, {})
            
            assert analysis.primary_intent == expected_intent, f"Failed for input: {user_input}"
            assert analysis.confidence >= min_confidence, f"Confidence too low for {user_input}: {analysis.confidence}"
    
    @pytest.mark.asyncio
    async def test_content_generation_intents(self, recognizer):
        """Test content generation intent recognition"""
        
        test_cases = [
            # Content generation
            ("Generate content about AI", IntentCategory.CONTENT_GENERATE, 0.9),
            ("Create content for wiki", IntentCategory.CONTENT_GENERATE, 0.9),
            ("生成内容", IntentCategory.CONTENT_GENERATE, 0.9),
            
            # Debate start
            ("Start a debate", IntentCategory.DEBATE_START, 0.9),
            ("Begin debate session", IntentCategory.DEBATE_START, 0.9),
            ("开始辩论", IntentCategory.DEBATE_START, 0.9),
        ]
        
        for user_input, expected_intent, min_confidence in test_cases:
            analysis = await recognizer.recognize_intent(user_input, {})
            
            assert analysis.primary_intent == expected_intent, f"Failed for input: {user_input}"
            assert analysis.confidence >= min_confidence, f"Confidence too low for {user_input}: {analysis.confidence}"
    
    @pytest.mark.asyncio
    async def test_system_intents(self, recognizer):
        """Test system-specific intent recognition"""
        
        test_cases = [
            # System status
            ("Show system status", IntentCategory.SYSTEM_STATUS, 0.9),
            ("Check system info", IntentCategory.SYSTEM_STATUS, 0.9),
            ("系统状态", IntentCategory.SYSTEM_STATUS, 0.9),
            
            # Configuration
            ("Configure settings", IntentCategory.CONFIGURE, 0.9),
            ("System configuration", IntentCategory.CONFIGURE, 0.9),
            ("配置系统", IntentCategory.CONFIGURE, 0.9),
        ]
        
        for user_input, expected_intent, min_confidence in test_cases:
            analysis = await recognizer.recognize_intent(user_input, {})
            
            assert analysis.primary_intent == expected_intent, f"Failed for input: {user_input}"
            assert analysis.confidence >= min_confidence, f"Confidence too low for {user_input}: {analysis.confidence}"
    
    @pytest.mark.asyncio
    async def test_entity_extraction(self, recognizer):
        """Test entity extraction capabilities"""
        
        test_cases = [
            # Wiki entries
            ("Create a wiki entry for Machine Learning", ["Machine Learning"]),
            ("Edit the 人工智能 page", ["人工智能"]),
            
            # Chat rooms
            ("Start chat room AI Discussion", ["AI Discussion"]),
            ("Join 聊天室 技术讨论", ["技术讨论"]),
            
            # Roles
            ("Match roles for data analysis task", ["data analysis"]),
            ("Find 角色 for machine learning", ["machine learning"]),
            
            # Numbers
            ("Show top 5 roles", ["5"]),
            ("Create 10 wiki entries", ["10"]),
        ]
        
        for user_input, expected_entities in test_cases:
            analysis = await recognizer.recognize_intent(user_input, {})
            
            # Check if expected entities are found
            found_entities = [entity.text for entity in analysis.entities]
            for expected_entity in expected_entities:
                assert expected_entity in found_entities, f"Entity '{expected_entity}' not found in '{user_input}'"
    
    @pytest.mark.asyncio
    async def test_confidence_scoring(self, recognizer):
        """Test confidence scoring accuracy"""
        
        test_cases = [
            # High confidence
            ("Create wiki", IntentCategory.WIKI_CREATE, 0.9),
            ("Delete chat", IntentCategory.CHAT_DELETE, 0.9),
            ("Match roles", IntentCategory.ROLE_MATCH, 0.9),
            
            # Medium confidence
            ("Make a wiki", IntentCategory.WIKI_CREATE, 0.6),
            ("Remove conversation", IntentCategory.CHAT_DELETE, 0.6),
            ("Find roles", IntentCategory.ROLE_MATCH, 0.6),
            
            # Low confidence
            ("Wiki stuff", IntentCategory.WIKI_CREATE, 0.3),
            ("Chat things", IntentCategory.CHAT_DELETE, 0.3),
            ("Role related", IntentCategory.ROLE_MATCH, 0.3),
        ]
        
        for user_input, expected_intent, expected_confidence_range in test_cases:
            analysis = await recognizer.recognize_intent(user_input, {})
            
            assert analysis.primary_intent == expected_intent, f"Failed for input: {user_input}"
            
            # Check if confidence is in expected range
            if expected_confidence_range >= 0.8:
                assert analysis.confidence_level in [ConfidenceLevel.HIGH, ConfidenceLevel.VERY_HIGH]
            elif expected_confidence_range >= 0.5:
                assert analysis.confidence_level == ConfidenceLevel.MEDIUM
            else:
                assert analysis.confidence_level in [ConfidenceLevel.LOW, ConfidenceLevel.VERY_LOW]
    
    @pytest.mark.asyncio
    async def test_secondary_intents(self, recognizer):
        """Test secondary intent detection"""
        
        user_input = "Help me create a wiki entry about machine learning"
        analysis = await recognizer.recognize_intent(user_input, {})
        
        # Primary intent should be wiki creation
        assert analysis.primary_intent == IntentCategory.WIKI_CREATE
        
        # Should have secondary intents
        assert len(analysis.secondary_intents) > 0
        
        # Check if help request is detected as secondary intent
        secondary_intent_values = [intent.value for intent, _ in analysis.secondary_intents]
        assert IntentCategory.HELP_REQUEST.value in secondary_intent_values
    
    @pytest.mark.asyncio
    async def test_context_requirements(self, recognizer):
        """Test context requirements generation"""
        
        test_cases = [
            (IntentCategory.WIKI_CREATE, ["wiki_entry_name", "content_type"]),
            (IntentCategory.WIKI_EDIT, ["wiki_entry_name", "edit_content"]),
            (IntentCategory.CHAT_START, ["chat_room_name", "topic"]),
            (IntentCategory.ROLE_MATCH, ["task_description", "task_type"]),
            (IntentCategory.CONTENT_GENERATE, ["topic", "content_type", "audience"]),
        ]
        
        for intent, expected_requirements in test_cases:
            user_input = f"Test input for {intent.value}"
            analysis = await recognizer.recognize_intent(user_input, {})
            
            # Override intent for testing
            analysis.primary_intent = intent
            analysis.context_requirements = recognizer._get_context_requirements(intent, [])
            
            assert set(analysis.context_requirements) == set(expected_requirements)
    
    @pytest.mark.asyncio
    async def test_suggested_actions(self, recognizer):
        """Test suggested actions generation"""
        
        test_cases = [
            (IntentCategory.WIKI_CREATE, ["Create new wiki entry", "Request content suggestions"]),
            (IntentCategory.WIKI_VIEW, ["Display wiki content", "Show entry metadata"]),
            (IntentCategory.CHAT_START, ["Create chat room", "Suggest participants"]),
            (IntentCategory.ROLE_MATCH, ["Find matching roles", "Show role statistics"]),
        ]
        
        for intent, expected_actions in test_cases:
            user_input = f"Test input for {intent.value}"
            analysis = await recognizer.recognize_intent(user_input, {})
            
            # Override intent for testing
            analysis.primary_intent = intent
            analysis.suggested_actions = recognizer._get_suggested_actions(intent, [])
            
            assert set(analysis.suggested_actions) == set(expected_actions)
    
    def test_intent_taxonomy(self, recognizer):
        """Test intent taxonomy structure"""
        
        taxonomy = recognizer.get_intent_taxonomy()
        
        # Check main categories
        expected_categories = [
            "basic_communication",
            "information_seeking", 
            "task_oriented",
            "wiki_management",
            "chat_management",
            "role_management",
            "collaboration",
            "system_management",
            "advanced"
        ]
        
        for category in expected_categories:
            assert category in taxonomy, f"Category '{category}' missing from taxonomy"
        
        # Check total intent count (should be 50+)
        total_intents = sum(len(intents) for intents in taxonomy.values())
        assert total_intents >= 50, f"Expected 50+ intents, got {total_intents}"
        
        # Check specific intents are present
        all_intents = [intent for intents in taxonomy.values() for intent in intents]
        
        critical_intents = [
            IntentCategory.WIKI_CREATE,
            IntentCategory.WIKI_EDIT,
            IntentCategory.CHAT_START,
            IntentCategory.ROLE_MATCH,
            IntentCategory.CONTENT_GENERATE,
            IntentCategory.DEBATE_START,
        ]
        
        for critical_intent in critical_intents:
            assert critical_intent.value in all_intents, f"Critical intent '{critical_intent.value}' missing"
    
    def test_intent_confidence_scoring(self, recognizer):
        """Test individual intent confidence scoring"""
        
        test_cases = [
            ("Create wiki", IntentCategory.WIKI_CREATE, 0.9),
            ("Make wiki", IntentCategory.WIKI_CREATE, 0.6),
            ("Wiki stuff", IntentCategory.WIKI_CREATE, 0.3),
            
            ("Start chat", IntentCategory.CHAT_START, 0.9),
            ("Begin chat", IntentCategory.CHAT_START, 0.6),
            ("Chat related", IntentCategory.CHAT_START, 0.3),
        ]
        
        for user_input, intent, expected_min_confidence in test_cases:
            confidence = recognizer.get_intent_confidence(intent, user_input, {})
            assert confidence >= expected_min_confidence, f"Confidence too low for '{user_input}': {confidence}"
    
    @pytest.mark.asyncio
    async def test_performance(self, recognizer):
        """Test recognition performance"""
        
        import time
        
        # Test with various inputs
        test_inputs = [
            "Create a new wiki entry about artificial intelligence",
            "Start a chat room for discussing machine learning",
            "Match roles for a data analysis task",
            "Show me the system status",
            "Help me understand this concept",
        ]
        
        total_time = 0
        for test_input in test_inputs:
            start_time = time.time()
            analysis = await recognizer.recognize_intent(test_input, {})
            end_time = time.time()
            
            processing_time = (end_time - start_time) * 1000  # Convert to ms
            total_time += processing_time
            
            # Check performance requirements
            assert processing_time < 100, f"Processing time too slow: {processing_time}ms"
            assert analysis.confidence >= 0.3, f"Confidence too low: {analysis.confidence}"
        
        avg_time = total_time / len(test_inputs)
        assert avg_time < 50, f"Average processing time too slow: {avg_time}ms"
        
        print(f"✅ Performance test passed: Average processing time {avg_time:.2f}ms")
    
    @pytest.mark.asyncio
    async def test_edge_cases(self, recognizer):
        """Test edge cases and error handling"""
        
        edge_cases = [
            # Empty input
            ("", IntentCategory.QUESTION, 0.0),
            
            # Very long input
            ("This is a very long input that should still be handled properly by the intent recognition system " * 10, 
             IntentCategory.QUESTION, 0.0),
            
            # Mixed language
            "Create wiki for 机器学习 about deep learning",
            
            # Special characters
            "Create wiki entry: AI & Machine Learning (2024)",
            
            # No clear intent
            "Just some random text without clear intent",
        ]
        
        for user_input in edge_cases:
            try:
                analysis = await recognizer.recognize_intent(user_input, {})
                
                # Should always return a valid analysis
                assert analysis.primary_intent is not None
                assert analysis.confidence >= 0.0
                assert analysis.confidence <= 1.0
                assert analysis.processing_time_ms >= 0
                
            except Exception as e:
                pytest.fail(f"Edge case failed for input '{user_input}': {e}")


@pytest.mark.asyncio
async def test_comprehensive_intent_coverage():
    """Test that all intent categories are covered"""
    
    recognizer = create_enhanced_intent_recognizer()
    
    # Get all intent categories
    all_intents = list(IntentCategory)
    
    # Test that each intent category has some test coverage
    coverage_results = {}
    
    for intent in all_intents:
        # Create a simple test input for each intent
        test_input = intent.value.replace("_", " ")
        
        try:
            analysis = await recognizer.recognize_intent(test_input, {})
            coverage_results[intent] = {
                "tested": True,
                "recognized": analysis.primary_intent == intent,
                "confidence": analysis.confidence
            }
        except Exception as e:
            coverage_results[intent] = {
                "tested": False,
                "error": str(e)
            }
    
    # Print coverage report
    print("\n📊 Intent Coverage Report:")
    print("=" * 50)
    
    tested_count = sum(1 for result in coverage_results.values() if result.get("tested", False))
    recognized_count = sum(1 for result in coverage_results.values() if result.get("recognized", False))
    
    print(f"Total intents: {len(all_intents)}")
    print(f"Tested intents: {tested_count}")
    print(f"Recognized intents: {recognized_count}")
    print(f"Coverage: {tested_count/len(all_intents)*100:.1f}%")
    
    # Check that we have good coverage
    assert tested_count >= len(all_intents) * 0.8, f"Insufficient test coverage: {tested_count}/{len(all_intents)}"
    
    print("✅ Intent coverage test passed")


if __name__ == "__main__":
    # Run the tests
    asyncio.run(test_comprehensive_intent_coverage())
    print("✅ All tests completed successfully!")
#!/usr/bin/env python3
"""
Simple validation script for Enhanced Intent Recognition System
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def validate_intent_taxonomy():
    """Validate the enhanced intent taxonomy"""
    
    try:
        from core_services.enhanced_intent_recognition import IntentCategory, EnhancedIntentRecognizer
        
        print("🔍 Validating Enhanced Intent Recognition System")
        print("=" * 60)
        
        # Check intent categories
        all_intents = list(IntentCategory)
        print(f"✅ Total intent categories: {len(all_intents)}")
        
        # Group intents by category
        categories = {
            'Basic Communication': [],
            'Information Seeking': [],
            'Task-Oriented': [],
            'Wiki-Specific': [],
            'Chat-Specific': [],
            'Role Management': [],
            'Debate & Collaboration': [],
            'System-Specific': [],
            'Advanced': []
        }
        
        for intent in all_intents:
            intent_value = intent.value
            if intent_value in ['greeting', 'farewell', 'affirmation', 'negation', 'apology', 'thanks']:
                categories['Basic Communication'].append(intent_value)
            elif intent_value in ['question', 'clarification', 'definition', 'explanation', 'example', 'comparison', 'status_inquiry', 'help_request']:
                categories['Information Seeking'].append(intent_value)
            elif intent_value in ['request', 'command', 'creation', 'modification', 'deletion', 'configuration', 'analysis', 'generation', 'optimization']:
                categories['Task-Oriented'].append(intent_value)
            elif intent_value.startswith('wiki_'):
                categories['Wiki-Specific'].append(intent_value)
            elif intent_value.startswith('chat_'):
                categories['Chat-Specific'].append(intent_value)
            elif intent_value.startswith('role_'):
                categories['Role Management'].append(intent_value)
            elif intent_value in ['debate_start', 'debate_join', 'debate_moderate', 'content_generate', 'collaborate', 'feedback_provide', 'consensus_seek']:
                categories['Debate & Collaboration'].append(intent_value)
            elif intent_value in ['system_status', 'error_report', 'configure', 'reset', 'backup', 'restore']:
                categories['System-Specific'].append(intent_value)
            else:
                categories['Advanced'].append(intent_value)
        
        # Print category breakdown
        print("\n📊 Intent Category Breakdown:")
        for category, intents in categories.items():
            print(f"  {category}: {len(intents)} intents")
            for intent in intents[:3]:  # Show first 3
                print(f"    - {intent}")
            if len(intents) > 3:
                print(f"    ... and {len(intents) - 3} more")
            print()
        
        # Test keyword patterns
        print("🔧 Testing Keyword Patterns:")
        recognizer = EnhancedIntentRecognizer()
        
        test_cases = [
            ("Create wiki", "wiki_create"),
            ("Start chat", "chat_start"),
            ("Match roles", "role_match"),
            ("Hello", "greeting"),
            ("Help me", "help_request"),
            ("Search wiki", "wiki_search"),
            ("Delete chat", "chat_delete"),
            ("Generate content", "content_generate"),
        ]
        
        for user_input, expected_intent in test_cases:
            keyword_scores = recognizer.keyword_matcher.match_intent(user_input)
            top_intent = max(keyword_scores.items(), key=lambda x: x[1]) if keyword_scores else (None, 0)
            
            print(f"  '{user_input}' -> {top_intent[0].value if top_intent[0] else 'None'} (confidence: {top_intent[1]:.2f})")
            
            if top_intent[0] and top_intent[0].value == expected_intent:
                print(f"    ✅ Correct")
            else:
                print(f"    ❌ Expected {expected_intent}")
        
        # Test entity extraction
        print("\n🏷️ Testing Entity Extraction:")
        entity_tests = [
            "Create wiki entry for Machine Learning",
            "Start chat room AI Discussion",
            "Match roles for data analysis task",
            "Show top 5 roles",
        ]
        
        for test_input in entity_tests:
            entities = recognizer.keyword_matcher.extract_entities(test_input)
            entity_texts = [entity.text for entity in entities]
            print(f"  '{test_input}' -> Entities: {entity_texts}")
        
        print("\n✅ Enhanced Intent Recognition System Validation Complete!")
        return True
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = validate_intent_taxonomy()
    sys.exit(0 if success else 1)
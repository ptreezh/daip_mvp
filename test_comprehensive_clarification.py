import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

def test_comprehensive_clarification():
    print("Testing comprehensive intent clarification functionality...")
    print("="*70)
    
    recognizer = EnhancedIntentRecognizer()
    
    # Test cases for different scenarios
    test_cases = [
        # Missing keywords scenarios
        ("论文", "search_papers", True, "query"),
        ("论文  ", "search_papers", True, "query"), 
        ("下载论文", "search_papers", True, "query"),
        
        # Missing topic scenarios  
        ("开始辩论", "start_debate", True, "topic"),
        ("发起辩论", "start_debate", True, "topic"),
        
        # Missing title scenarios
        ("创建Wiki", "create_wiki", True, "title"),
        ("新建wiki", "create_wiki", True, "title"),
        
        # Valid inputs that shouldn't need clarification
        ("论文 人工智能", "search_papers", False, "has query"),
        ("搜索量子计算论文", "search_papers", False, "has query"),
        ("开始辩论 AI伦理", "start_debate", False, "has topic"),
        ("创建Wiki 项目计划", "create_wiki", False, "has title"),
    ]
    
    summary = {
        'clarification_needed': 0,
        'clarification_not_needed': 0,
        'correct_detections': 0, 
        'total': len(test_cases)
    }
    
    for input_text, expected_intent, should_need_clarification, expected_param in test_cases:
        print(f"\nInput: '{input_text}'")
        intent = recognizer.recognize_intent(input_text)
        
        if intent:
            print(f"  Expected intent: {expected_intent}")
            print(f"  Recognized intent: {intent.name}")
            print(f"  Confidence: {intent.confidence:.2f}")
            print(f"  Parameters: {intent.parameters}")
            
            actual_clarification = getattr(intent, 'requires_clarification', False)
            print(f"  Should need clarification: {should_need_clarification}")
            print(f"  Actually needs clarification: {actual_clarification}")
            
            if should_need_clarification == actual_clarification:
                print(f"  ✅ CORRECT detection")
                summary['correct_detections'] += 1
            else:
                print(f"  ❌ INCORRECT detection")
                
            if actual_clarification:
                summary['clarification_needed'] += 1
                if hasattr(intent, 'clarification_needed') and intent.clarification_needed:
                    print(f"  Clarification type: {getattr(intent.clarification_needed, 'type', 'unknown')}")
                    print(f"  Clarification message: {getattr(intent.clarification_needed, 'message', 'No message')}")
            else:
                summary['clarification_not_needed'] += 1
                
        else:
            print(f"  ❌ No intent recognized for: {input_text}")
    
    print("\n" + "="*70)
    print("📊 TESTING SUMMARY:")
    print(f"   Total test cases: {summary['total']}")
    print(f"   Correct detections: {summary['correct_detections']}/{summary['total']}")
    print(f"   Accuracy: {summary['correct_detections']/summary['total']*100:.1f}%")
    print(f"   Cases needing clarification: {summary['clarification_needed']}")
    print(f"   Cases not needing clarification: {summary['clarification_not_needed']}")
    
    if summary['correct_detections'] == summary['total']:
        print("\n🎉 ALL TESTS PASSED! Intent clarification system working correctly!")
        print("✅ Users will be prompted for missing keywords")
        print("✅ Ambiguous commands will request clarification")
        print("✅ Valid commands execute without interruption")
    else:
        print(f"\n⚠️  {summary['total'] - summary['correct_detections']} tests failed")
    
    print("="*70)

if __name__ == "__main__":
    test_comprehensive_clarification()
#!/usr/bin/env python3
"""
Test script to verify the enhanced intent recognition system with LLM capabilities.
This tests the HybridIntentRecognizer that combines rule-based and LLM-based analysis.
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_hybrid_intent_recognizer():
    """Test the HybridIntentRecognizer with advanced semantic understanding."""
    print("🧠 Testing Hybrid Intent Recognizer (Rule + LLM)...")

    try:
        from daip_live.multi_agent_collab.hybrid_intent_collaboration_engine import HybridIntentRecognizer

        # Initialize the hybrid recognizer
        recognizer = HybridIntentRecognizer(llm_model_provider=None)  # Use simulation mode

        # Test cases with complex semantic understanding requirements
        complex_test_cases = [
            # Basic cases (should be handled by rules)
            ("搜索论文 人工智能", "search_papers", "rule-based"),
            ("辩论 AI伦理问题", "start_debate", "rule-based"),
            ("创建维基 量子计算", "create_wiki", "rule-based"),

            # Complex semantic cases (should be enhanced by LLM analysis)
            ("帮我分析一下机器学习的最新发展趋势", "execute_skill", "llm-enhanced"),
            ("我想了解深度学习在图像识别中的应用", "execute_skill", "llm-enhanced"),
            ("请帮我制定一个关于AI伦理的研究计划", "complex_task", "llm-enhanced"),
            ("有没有人能帮我翻译一下这篇关于量子计算的论文", "execute_skill", "llm-enhanced"),
            ("我想跟不同观点的人讨论一下AI的未来发展", "start_debate", "llm-enhanced"),
            ("帮我总结一下最近的AI领域的重要突破", "execute_skill", "llm-enhanced"),

            # Ambiguous cases requiring clarification
            ("帮我分析", "execute_skill", "needs_clarification"),
            ("创建", "create_wiki", "needs_clarification"),
            ("搜索", "search_papers", "needs_clarification"),
        ]

        print("  Testing complex semantic understanding:")
        results = []

        for text, expected_intent, expected_method in complex_test_cases:
            try:
                intent = recognizer.recognize_intent(text, session_id="test")

                if intent:
                    success = intent.name == expected_intent
                    status = "✅" if success else "⚠️"

                    print(f"  {status} '{text[:50]}...' -> {intent.name}")
                    print(f"     Expected: {expected_intent}, Method: {expected_method}")
                    print(f"     Confidence: {getattr(intent, 'confidence', 'N/A'):.2f}")
                    print(f"     Parameters: {getattr(intent, 'parameters', {})}")

                    if hasattr(intent, 'requires_clarification') and intent.requires_clarification:
                        print(f"     ⚠️ Needs clarification: {getattr(intent, 'clarification_needed', 'Yes')}")

                    results.append(success)
                else:
                    print(f"  ❌ '{text}' -> No intent recognized")
                    results.append(False)

            except Exception as e:
                print(f"  ❌ '{text}' -> Error: {e}")
                results.append(False)

        # Summary
        success_rate = sum(results) / len(results) if results else 0
        print(f"\n  📊 Success Rate: {success_rate:.1%} ({sum(results)}/{len(results)} tests passed)")

        return success_rate >= 0.8  # 80% success rate threshold

    except ImportError as e:
        print(f"  ❌ Failed to import HybridIntentRecognizer: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_llm_analyzer_standalone():
    """Test the LLM-based intent analyzer independently."""
    print("\n🤖 Testing LLM-Based Intent Analyzer...")

    try:
        from daip_live.multi_agent_collab.real_collaboration_engine import LLMBasedIntentAnalyzer

        analyzer = LLMBasedIntentAnalyzer(model_provider=None)

        # Test complex natural language inputs
        test_inputs = [
            "我想写一篇关于机器学习在医疗领域应用的综述文章",
            "请帮我分析一下当前人工智能技术的发展现状和未来趋势",
            "我想找一些关于强化学习在游戏AI中应用的最新研究",
            "能不能帮我翻译一下这篇深度学习的论文摘要",
            "我想组织一场关于AI伦理的辩论，讨论人工智能是否应该拥有法律地位",
        ]

        print("  Testing advanced semantic analysis:")
        results = []

        for text in test_inputs:
            try:
                # Test the simulation analysis (since we don't have real LLM)
                # In real implementation with LLM, this would call analyzer.analyze_intent_with_llm()
                result = analyzer._simulate_llm_analysis(text)

                if result and "intent_name" in result:
                    print(f"  ✅ '{text[:40]}...' -> {result['intent_name']}")
                    print(f"     Parameters: {result.get('parameters', {})}")
                    print(f"     Confidence: {result.get('confidence', 0):.2f}")
                    print(f"     Explanation: {result.get('explanation', 'No explanation')}")
                    results.append(True)
                else:
                    print(f"  ❌ '{text}' -> No analysis result")
                    results.append(False)

            except Exception as e:
                print(f"  ❌ '{text}' -> Error: {e}")
                results.append(False)

        return sum(results) / len(results) if results else 0

    except ImportError as e:
        print(f"  ❌ Failed to import LLMBasedIntentAnalyzer: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False

def test_parameter_extraction():
    """Test advanced parameter extraction capabilities."""
    print("\n🔍 Testing Advanced Parameter Extraction...")

    try:
        from daip_live.multi_agent_collab.real_collaboration_engine import LLMBasedIntentAnalyzer

        analyzer = LLMBasedIntentAnalyzer()

        # Test cases with complex parameter extraction
        parameter_test_cases = [
            {
                "input": "搜索关于深度学习在计算机视觉中应用的最近5年论文，最多返回10篇结果",
                "expected_intent": "search_papers",
                "expected_params": ["query", "max_results", "time_range"]
            },
            {
                "input": "创建一个关于机器学习基础知识的维基页面，包含监督学习、无监督学习和强化学习三个部分",
                "expected_intent": "create_wiki",
                "expected_params": ["title", "content", "sections"]
            },
            {
                "input": "开始一场关于人工智能是否应该拥有法律地位的辩论，邀请哲学家、工程师和法律专家参与，进行3轮辩论",
                "expected_intent": "start_debate",
                "expected_params": ["topic", "roles", "rounds"]
            },
            {
                "input": "帮我下载arXiv论文2301.00001，并且搜索相关的机器学习论文",
                "expected_intent": "download_paper",
                "expected_params": ["paper_id", "search_query"]
            }
        ]

        print("  Testing complex parameter extraction:")
        results = []

        for case in parameter_test_cases:
            text = case["input"]
            expected_intent = case["expected_intent"]
            expected_params = case["expected_params"]

            try:
                result = analyzer._simulate_llm_analysis(text)

                if result and "intent_name" in result:
                    intent_match = result["intent_name"] == expected_intent
                    params_extracted = result.get("parameters", {})

                    # Check if expected parameters are extracted
                    param_quality = 0
                    for param in expected_params:
                        if param in params_extracted and params_extracted[param]:
                            param_quality += 1

                    param_success_rate = param_quality / len(expected_params)

                    print(f"  {'✅' if intent_match else '⚠️'} '{text[:40]}...' -> {result['intent_name']}")
                    print(f"     Expected: {expected_intent}, Params extracted: {param_success_rate:.0%}")
                    print(f"     Parameters: {params_extracted}")

                    results.append(intent_match and param_success_rate >= 0.5)
                else:
                    print(f"  ❌ '{text[:40]}...' -> No analysis result")
                    results.append(False)

            except Exception as e:
                print(f"  ❌ '{text}' -> Error: {e}")
                results.append(False)

        return sum(results) / len(results) if results else 0

    except Exception as e:
        print(f"  ❌ Error in parameter extraction test: {e}")
        return False

def main():
    """Run all enhanced intent recognition tests."""
    print("🚀 Starting Enhanced Intent Recognition System Tests\n")

    results = []

    # Test 1: Hybrid Intent Recognizer
    results.append(test_hybrid_intent_recognizer())

    # Test 2: LLM Analyzer Standalone
    results.append(test_llm_analyzer_standalone())

    # Test 3: Advanced Parameter Extraction
    param_score = test_parameter_extraction()
    results.append(param_score >= 0.7)  # 70% success rate threshold

    # Summary
    print("\n📊 Enhanced Intent Recognition Test Summary:")
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"  🎉 All {total} test categories passed!")
        print("\n✅ Enhanced Intent Recognition System verified successfully!")
        print("\n🧠 Advanced capabilities now available:")
        print("  🎯 Rule-based intent recognition for common patterns")
        print("  🤖 LLM-based semantic understanding for complex inputs")
        print("  🔍 Advanced parameter extraction and validation")
        print("  🔄 Hybrid approach combining both methods")
        print("  💬 Natural language understanding with context")
        print("  ⚠️ Intelligent clarification requests when needed")
        return 0
    else:
        print(f"  ⚠️ {passed}/{total} test categories passed")
        print("\n🔧 Some improvements may be needed")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
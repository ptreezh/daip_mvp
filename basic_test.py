#!/usr/bin/env python3
"""
真正的基础测试 - 验证代码是否能运行
"""

import sys
import os

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_import():
    """测试基本导入"""
    print("=== 测试1: 基本导入 ===")
    try:
        from core_services.enhanced_intent_recognition import IntentCategory
        print("✅ IntentCategory 导入成功")
        
        # 检查IntentCategory是否有值
        categories = list(IntentCategory)
        print(f"✅ 找到 {len(categories)} 个意图类别")
        
        # 显示前几个
        for i, category in enumerate(categories[:5]):
            print(f"  {i+1}. {category.value}")
        
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_basic_functionality():
    """测试基本功能"""
    print("\n=== 测试2: 基本功能 ===")
    try:
        from core_services.enhanced_intent_recognition import EnhancedIntentRecognizer
        
        # 创建识别器
        recognizer = EnhancedIntentRecognizer()
        print("✅ EnhancedIntentRecognizer 创建成功")
        
        # 测试关键词匹配
        test_input = "Create wiki"
        scores = recognizer.keyword_matcher.match_intent(test_input)
        print(f"✅ 关键词匹配测试: '{test_input}' -> {len(scores)} 个匹配")
        
        if scores:
            top_intent = max(scores.items(), key=lambda x: x[1])
            print(f"  最佳匹配: {top_intent[0].value} (置信度: {top_intent[1]:.2f})")
        
        return True
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_entity_extraction():
    """测试实体提取"""
    print("\n=== 测试3: 实体提取 ===")
    try:
        from core_services.enhanced_intent_recognition import EnhancedIntentRecognizer
        
        recognizer = EnhancedIntentRecognizer()
        
        test_input = "Create wiki entry for Machine Learning"
        entities = recognizer.keyword_matcher.extract_entities(test_input)
        print(f"✅ 实体提取测试: '{test_input}' -> {len(entities)} 个实体")
        
        for entity in entities:
            print(f"  实体: {entity.text} (类型: {entity.label})")
        
        return True
    except Exception as e:
        print(f"❌ 实体提取测试失败: {e}")
        return False

def test_async_functionality():
    """测试异步功能"""
    print("\n=== 测试4: 异步功能 ===")
    try:
        import asyncio
        from core_services.enhanced_intent_recognition import EnhancedIntentRecognizer
        
        async def test_recognize():
            recognizer = EnhancedIntentRecognizer()
            result = await recognizer.recognize_intent("Create wiki", {})
            return result
        
        result = asyncio.run(test_recognize())
        print(f"✅ 异步识别测试成功")
        print(f"  意图: {result.primary_intent.value}")
        print(f"  置信度: {result.confidence:.2f}")
        
        return True
    except Exception as e:
        print(f"❌ 异步功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🔍 开始基础测试...")
    print("=" * 50)
    
    tests = [
        test_basic_import,
        test_basic_functionality,
        test_entity_extraction,
        test_async_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print(f"❌ {test.__name__} 失败")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有基础测试通过！")
        return True
    else:
        print("⚠️  部分测试失败，需要修复")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
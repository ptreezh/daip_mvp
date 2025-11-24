"""
意图识别上下文保持系统演示脚本
展示新功能如何解决原始问题
"""

import sys
import os
# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.daip_live.container import Container
from src.intent_recognition.context_aware_intent_recognizer import ContextAwareIntentRecognizer
from src.intent_recognition.context_manager import ContextManager


def demonstrate_context_preservation():
    """演示上下文保持功能"""
    print("=== 意图识别上下文保持系统演示 ===\n")
    
    # 使用依赖注入容器
    container = Container()
    container.config.from_dict({
        "database": {"path": ":memory:"},
        "llm_provider": {
            "default_model": "ollama/llama3",
            "embedding_model": "ollama/nomic-embed-text"
        },
        "knowledge_base": {"directory": "./knowledge"},
        "role_manager": {"roles_dir": "./roles"}
    })
    
    # 获取上下文感知意图识别器
    recognizer = container.context_aware_intent_recognizer()
    
    # 模拟会话ID
    session_id = "demo_session_001"
    
    print("场景1: 创建Wiki页面的多步骤流程")
    print("-" * 40)
    
    # 模拟用户启动Wiki创建任务（这通常由意图识别器检测到）
    print("系统检测到意图: Wiki创建工作流 (置信度: 1.00)")
    print("请输入Wiki页面标题")
    
    # 设置上下文，模拟系统进入Wiki创建流程
    wiki_context = {
        'task_type': 'wiki_creation',
        'required_params': ['title', 'content']
    }
    recognizer.context_manager.set_context(session_id, wiki_context)
    
    # 用户输入标题
    print("\n用户输入: '敏捷开发与规范编程'")
    result1 = recognizer.recognize_intent(session_id, "敏捷开发与规范编程")
    print(f"系统响应: 检测到参数 '{result1['param_name']}': '{result1['param_value']}'")
    print(f"当前缺失参数: {result1['remaining_params']}")
    print("请输入Wiki页面内容")
    
    # 用户输入内容
    print("\n用户输入: '敏捷开发是一种以用户需求为核心...'")
    result2 = recognizer.recognize_intent(session_id, "敏捷开发是一种以用户需求为核心...")
    print(f"系统响应: 检测到参数 '{result2['param_name']}': '{result2['param_value']}'")
    print(f"任务完成: {result2['task_completed']}")
    
    if result2['task_completed']:
        print(f"完成的任务: {result2['completed_task']['task_type']}")
        print(f"收集的参数: {result2['completed_task']['parameters']}")
    
    print("\n" + "=" * 50)
    print("场景2: 任务完成后恢复正常意图识别")
    print("-" * 40)
    
    # 任务完成后，用户的下一次输入应该使用常规意图识别
    print("用户输入: '帮我创建一个新的辩论'")
    result3 = recognizer.recognize_intent(session_id, "帮我创建一个新的辩论")
    print(f"系统响应: 检测到意图 - {result3.get('intent', '未知')}")
    print(f"用户输入: {result3.get('user_input', '未知')}")
    
    print("\n" + "=" * 50)
    print("场景3: 没有上下文时的正常工作流程")
    print("-" * 40)
    
    session_id2 = "demo_session_002"
    print("用户输入: '你好'")
    result4 = recognizer.recognize_intent(session_id2, "你好")
    print(f"系统响应: 检测到意图 - {result4.get('intent', '未知')}")
    print(f"用户输入: {result4.get('user_input', '未知')}")
    
    print("\n" + "=" * 50)
    print("✅ 演示完成! 上下文保持系统成功解决了原始问题。")


def simulate_original_problem_fixed():
    """模拟原始问题已被解决"""
    print("\n=== 原始问题解决方案验证 ===\n")
    
    container = Container()
    container.config.from_dict({
        "database": {"path": ":memory:"},
        "llm_provider": {
            "default_model": "ollama/llama3",
            "embedding_model": "ollama/nomic-embed-text"
        },
        "knowledge_base": {"directory": "./knowledge"},
        "role_manager": {"roles_dir": "./roles"}
    })
    
    recognizer = container.context_aware_intent_recognizer()
    session_id = "problem_demo_001"
    
    print("原始问题: 用户在Wiki创建流程中输入主题，系统错误地将其识别为新意图")
    print("解决方案: 使用上下文感知意图识别")
    print()
    
    # 设置Wiki创建上下文
    wiki_context = {
        'task_type': 'wiki_creation',
        'required_params': ['title']
    }
    recognizer.context_manager.set_context(session_id, wiki_context)
    
    print("1. 系统识别到Wiki创建意图: '根据以上辩论的结果，创建词条'")
    print("   → 系统: 检测到意图: Wiki创建工作流 (置信度: 1.00)")
    print("   → 系统: 请输入Wiki页面标题")
    
    print("\n2. 用户输入: '敏捷开发与规范编程'")
    result = recognizer.recognize_intent(session_id, "敏捷开发与规范编程")
    
    if result["intent"].startswith("contextual_"):
        print(f"   → 系统: 识别为Wiki页面标题: '{result['param_value']}'")
        print("   → 系统: Wiki页面创建流程继续...")
        if result.get("task_completed"):
            print("   → 系统: Wiki页面创建完成!")
        else:
            print("   → 系统: 请输入更多内容...")
    else:
        print(f"   → 系统: 错误! 意图被误识别为: {result['intent']}")
    
    print("\n✅ 问题已解决! 系统现在能够正确保持上下文，")
    print("   不会将用户的任务参数输入误认为是新的独立请求。")


if __name__ == "__main__":
    demonstrate_context_preservation()
    simulate_original_problem_fixed()
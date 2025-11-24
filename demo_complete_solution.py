"""
综合演示：完整的对话历史分析和上下文感知解决方案
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.daip_live.container import Container


def demonstrate_complete_solution():
    """演示完整的解决方案"""
    print("=== 完整解决方案演示 ===\n")
    
    # 创建容器实例
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
    context_manager = container.context_manager()
    
    print("场景1: 传统流程 - 用户需重复输入信息")
    print("-" * 50)
    print("用户: '我们来辩论AI对就业的影响'")
    print("系统: 开始辩论流程...")
    print("（一系列辩论交互）")
    print("系统: 辩论结束，结论是AI对就业既有促进也有挑战")
    print()
    print("用户: '请根据辩论结果创建wiki词条'")
    print("系统: 请输入Wiki页面标题")  # 传统系统要求重复输入
    print("用户: 'AI对就业的影响'")  # 用户需再次输入
    print("系统: 请输入Wiki页面内容")  # 传统系统要求重复输入
    print("用户: 'AI对就业既有促进也有挑战，关键在于如何平衡'")  # 用户需再次输入
    print()
    
    print("场景2: 新解决方案 - 系统自动从历史中提取信息")
    print("-" * 50)
    
    session_id = "complete_demo_001"
    
    # 模拟添加辩论历史记录
    session_state = context_manager.get_session_state(session_id)
    if not session_state:
        from src.intent_recognition.session_state import SessionState
        session_state = SessionState(session_id=session_id)
        context_manager.sessions[session_id] = session_state
    
    debate_history = [
        {"role": "user", "content": "我们来辩论AI对就业的影响", "timestamp": "2025-11-23 21:00:00"},
        {"role": "assistant", "content": "好的，AI对就业的影响是一个重要话题。", "timestamp": "2025-11-23 21:00:01"},
        {"role": "user", "content": "AI可能导致某些岗位消失", "timestamp": "2025-11-23 21:00:02"},
        {"role": "assistant", "content": "但也可能创造新的就业机会", "timestamp": "2025-11-23 21:00:03"},
        {"role": "user", "content": "关键是如何平衡", "timestamp": "2025-11-23 21:00:04"},
        {"role": "system", "content": "辩论总结：AI对就业既有促进也有挑战，关键在于如何平衡。", "timestamp": "2025-11-23 21:00:05"}
    ]
    
    for msg in debate_history:
        session_state.add_to_history(msg)
    
    # 设置Wiki创建上下文
    wiki_context = {
        'task_type': 'create_wiki',
        'required_params': ['title', 'content']
    }
    context_manager.set_context(session_id, wiki_context)
    
    print("用户: '请根据辩论结果创建wiki词条'")
    result = recognizer.recognize_intent(session_id, "请根据辩论结果创建wiki词条")
    
    print(f"系统: 识别到参数 'title': '{result.get('param_name', 'N/A')}'")
    print(f"填充的参数: {result.get('filled_params', [])}")
    
    if result.get('history_content'):
        history_content = result['history_content']
        print(f"系统从历史中提取到:")
        print(f"  - 主题: {history_content.get('topic', 'N/A')}")
        print(f"  - 内容: {history_content.get('content', 'N/A')}")
        print(f"  - 置信度: {history_content.get('confidence', 0.0):.2f}")
    
    if result['task_completed']:
        print("✅ 任务自动完成!")
        print(f"   完成的任务: {result['completed_task']['task_type']}")
        print(f"   收集的参数: {result['completed_task']['parameters']}")
    
    print("\n" + "="*60)
    print("场景3: 参数提取和历史分析的结合")
    print("-" * 50)
    
    session_id2 = "combined_demo_001"
    
    # 添加另一段历史记录
    session_state2 = context_manager.get_session_state(session_id2)
    if not session_state2:
        session_state2 = SessionState(session_id=session_id2)
        context_manager.sessions[session_id2] = session_state2
    
    debate_history2 = [
        {"role": "user", "content": "讨论ChatGPT对教育的影响", "timestamp": "2025-11-23 21:10:00"},
        {"role": "assistant", "content": "ChatGPT对教育有双面性，需要合理使用。", "timestamp": "2025-11-23 21:10:01"},
        {"role": "system", "content": "讨论总结：ChatGPT对教育有双面性，关键在于合理使用和监管。", "timestamp": "2025-11-23 21:10:02"}
    ]
    
    for msg in debate_history2:
        session_state2.add_to_history(msg)
    
    # 设置需要填充的上下文
    context_manager.set_context(session_id2, {
        'task_type': 'create_wiki',
        'required_params': ['title', 'content']
    })
    
    # 用户直接提供信息的输入
    user_input = "创建关于ChatGPT教育影响的词条"
    print(f"用户: {user_input}")
    
    result2 = recognizer.recognize_intent(session_id2, user_input)
    print(f"系统处理结果:")
    print(f"  - 提取的参数: {result2.get('extracted_params', {})}")
    print(f"  - 填充的参数: {result2.get('filled_params', [])}")
    print(f"  - 历史内容: {result2.get('history_content', {})}")
    
    print("\n" + "="*60)
    print("✅ 完整解决方案演示完成!")
    print("\n解决方案特性:")
    print("1. 上下文保持 - 在多步骤任务中保持会话连贯")
    print("2. 参数提取 - 从用户输入中自动提取关键信息") 
    print("3. 历史分析 - 从对话历史中提取相关辩论结果")
    print("4. 智能填充 - 自动使用提取的信息填充任务参数")
    print("5. 无缝集成 - 与现有系统完全兼容")


def show_before_after_comparison():
    """显示改进前后的对比"""
    print("\n" + "="*60)
    print("改进前后对比")
    print("="*60)
    
    print("\n【原始系统流程】")
    print("用户: '我们来辩论AI对就业的影响'")
    print("系统: 开启辩论流程...")
    print("（辩论进行中）")
    print("系统: 辩论结束，结果是...")
    print()
    print("用户: '请根据辩论结果创建wiki词条'")
    print("系统: 请输入Wiki页面标题")  # 系统不知道辩论结果
    print("用户: 需要输入标题")  # 用户重复输入
    print("系统: 请输入Wiki页面内容")  # 系统不知道辩论结果
    print("用户: 需要输入内容")  # 用户重复输入
    print("（用户体验差，重复劳动）")
    
    print("\n【新系统流程】")
    print("用户: '我们来辩论AI对就业的影响'")
    print("系统: 开启辩论流程...")
    print("（辩论进行中）")
    print("系统: 辩论结束，结果已记录")
    print()
    print("用户: '请根据辩论结果创建wiki词条'")
    print("系统: 正在分析历史记录...")  # 系统分析历史
    print("系统: 已从历史中提取到标题和内容")  # 系统自动填充
    print("系统: Wiki词条创建完成！")  # 任务自动完成
    print("（用户体验好，智能高效）")
    
    print("\n✅ 新系统解决了以下问题:")
    print("• 会话上下文丢失问题")
    print("• 无法从历史中提取信息问题") 
    print("• 用户重复输入问题")
    print("• 任务流程中断问题")


if __name__ == "__main__":
    demonstrate_complete_solution()
    show_before_after_comparison()
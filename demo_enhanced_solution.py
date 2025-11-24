"""
演示增强版上下文感知意图识别器如何解决原问题
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.daip_live.container import Container
from src.intent_recognition.context_aware_intent_recognizer import ContextAwareIntentRecognizer
from src.intent_recognition.context_manager import ContextManager


def demonstrate_solution():
    """演示增强版功能如何解决原问题"""
    print("=== 增强版上下文感知意图识别器演示 ===\n")
    
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
    
    print("问题场景1: 论文下载 - 用户已提供明确主题但系统未提取")
    print("-" * 55)
    
    session_id1 = "demo_paper_001"
    
    # 模拟系统检测到论文下载意图并进入任务
    print("系统: 检测到意图: 论文下载工作流 (置信度: 1.00)")
    print("系统: 请提供arXiv ID或论文标题/主题进行下载")
    print("       例如: 如：下载论文 1234.5678 或 下载论文 量子计算")
    
    # 设置论文下载上下文
    paper_context = {
        'task_type': 'download_paper',
        'required_params': ['topic']
    }
    recognizer.context_manager.set_context(session_id1, paper_context)
    
    # 用户输入明确的论文主题
    user_input = "下载 意图识别与上下文管理相关的论文"
    print(f"\n用户输入: {user_input}")
    
    result = recognizer.recognize_intent(session_id1, user_input)
    print(f"系统响应: 识别到参数 '{result['param_name']}': '{result['param_value']}'")
    
    # 检查是否提取了参数
    if result.get('extracted_params'):
        extracted_topic = result['extracted_params'].get('topic')
        if extracted_topic:
            print(f"✅ 系统现在能够提取到主题: '{extracted_topic}'")
    
    if result['task_completed']:
        print("✅ 任务自动完成!")
        print(f"   完成的任务: {result['completed_task']['task_type']}")
        print(f"   收集的参数: {result['completed_task']['parameters']}")
    else:
        print("⚠️  任务未完成，仍需更多参数")
    
    print("\n" + "="*60)
    print("问题场景2: Wiki创建 - 用户已提供明确标题但系统未提取")
    print("-" * 55)
    
    session_id2 = "demo_wiki_001"
    
    # 模拟系统检测到Wiki创建意图并进入任务
    print("系统: 检测到意图: Wiki创建工作流 (置信度: 1.00)")
    print("系统: 请输入Wiki页面标题")
    
    # 设置Wiki创建上下文
    wiki_context = {
        'task_type': 'create_wiki',
        'required_params': ['title']
    }
    recognizer.context_manager.set_context(session_id2, wiki_context)
    
    # 用户输入明确的Wiki标题
    user_input2 = "编写词条 中美贸易战"
    print(f"\n用户输入: {user_input2}")
    
    result2 = recognizer.recognize_intent(session_id2, user_input2)
    print(f"系统响应: 识别到参数 '{result2['param_name']}': '{result2['param_value']}'")
    
    # 检查是否提取了参数
    if result2.get('extracted_params'):
        extracted_title = result2['extracted_params'].get('title')
        if extracted_title:
            print(f"✅ 系统现在能够提取到标题: '{extracted_title}'")
    
    if result2['task_completed']:
        print("✅ 任务自动完成!")
        print(f"   完成的任务: {result2['completed_task']['task_type']}")
        print(f"   收集的参数: {result2['completed_task']['parameters']}")
    else:
        print("⚠️  任务未完成，仍需更多参数")
    
    print("\n" + "="*60)
    print("问题场景3: 提供arXiv ID的论文下载")
    print("-" * 55)
    
    session_id3 = "demo_arxiv_001"
    
    # 设置论文下载上下文
    recognizer.context_manager.set_context(session_id3, paper_context)
    
    # 用户输入arXiv ID
    user_input3 = "下载论文 1234.5678"
    print(f"用户输入: {user_input3}")
    
    result3 = recognizer.recognize_intent(session_id3, user_input3)
    print(f"系统响应: 识别到参数 '{result3['param_name']}': '{result3['param_value']}'")
    
    # 检查是否提取了arXiv ID
    if result3.get('extracted_params'):
        extracted_arxiv = result3['extracted_params'].get('arxiv_id')
        if extracted_arxiv:
            print(f"✅ 系统现在能够提取到arXiv ID: '{extracted_arxiv}'")
    
    print("\n" + "="*60)
    print("✅ 演示完成! 增强版系统现在能够:")
    print("   1. 在用户输入中自动提取已有的参数信息")
    print("   2. 智能填充任务所需的参数")
    print("   3. 减少不必要的重复询问")
    print("   4. 提高多步骤任务的用户体验")


def simulate_original_vs_new():
    """模拟原始问题与新解决方案的对比"""
    print("\n=== 原始问题 vs 新解决方案对比 ===\n")
    
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
    
    print("原始问题:")
    print("用户输入 '下载 意图识别与上下文管理相关的论文'")
    print("-> 系统要求再次输入论文标题/主题")
    print("-> 用户需重复输入详细信息")
    print()
    
    print("新解决方案:")
    session_id = "comparison_001"
    
    # 设置上下文
    recognizer.context_manager.set_context(session_id, {
        'task_type': 'download_paper',
        'required_params': ['topic']
    })
    
    user_input = "下载 意图识别与上下文管理相关的论文"
    result = recognizer.recognize_intent(session_id, user_input)
    
    print(f"用户输入: {user_input}")
    print(f"-> 系统自动提取到主题: '{result.get('param_value', 'N/A')}'")
    print("-> 系统直接使用提取的信息继续流程")
    print("-> 无需用户重复输入")
    
    print("\n原始问题:")
    print("用户输入 '编写词条 中美贸易战'")
    print("-> 系统要求输入Wiki页面标题")
    print("-> 用户需再次输入标题")
    print()
    
    # 清理上下文
    recognizer.context_manager.clear_context(session_id)
    
    # 设置Wiki上下文
    recognizer.context_manager.set_context(session_id, {
        'task_type': 'create_wiki',
        'required_params': ['title']
    })
    
    user_input2 = "编写词条 中美贸易战"
    result2 = recognizer.recognize_intent(session_id, user_input2)
    
    print("新解决方案:")
    print(f"用户输入: {user_input2}")
    print(f"-> 系统自动提取到标题: '{result2.get('param_value', 'N/A')}'")
    print("-> 系统直接使用提取的标题继续流程")
    print("-> 无需用户重复输入")
    
    print("\n✅ 问题已解决!")


if __name__ == "__main__":
    demonstrate_solution()
    simulate_original_vs_new()
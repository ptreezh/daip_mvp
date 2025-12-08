"""
快速验证意图识别上下文保持系统是否可以立即运行
"""
import sys
import os
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_system():
    print("正在验证意图识别上下文保持系统...")
    
    try:
        # 1. 测试容器导入
        print("✓ 1. 导入依赖注入容器...")
        from src.daip_live.container import Container
        
        # 2. 测试新组件导入
        print("✓ 2. 导入新组件...")
        from src.intent_recognition.context_manager import ContextManager
        from src.intent_recognition.context_aware_intent_recognizer import ContextAwareIntentRecognizer
        
        # 3. 创建容器实例
        print("✓ 3. 创建容器实例...")
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
        
        # 4. 获取服务实例
        print("✓ 4. 获取服务实例...")
        context_manager = container.context_manager()
        context_aware_recognizer = container.context_aware_intent_recognizer()
        
        # 5. 验证组件类型
        print("✓ 5. 验证组件类型...")
        assert isinstance(context_manager, ContextManager), "ContextManager类型错误"
        assert isinstance(context_aware_recognizer, ContextAwareIntentRecognizer), "ContextAwareIntentRecognizer类型错误"
        
        # 6. 测试基本功能
        print("✓ 6. 测试基本功能...")
        session_id = "test_session"
        
        # 设置一个Wiki创建上下文
        wiki_context = {
            'task_type': 'wiki_creation',
            'required_params': ['title', 'content']
        }
        context_manager.set_context(session_id, wiki_context)
        
        # 验证是否在任务中
        assert context_manager.is_in_task(session_id), "上下文设置失败"
        
        # 使用上下文感知识别器处理输入
        result = context_aware_recognizer.recognize_intent(session_id, "敏捷开发与规范编程")
        
        # 验证结果
        assert result.get("param_name") == "title", f"参数名错误: {result}"
        assert result.get("param_value") == "敏捷开发与规范编程", f"参数值错误: {result}"
        
        # 清理上下文
        context_manager.clear_context(session_id)
        assert not context_manager.is_in_task(session_id), "上下文清理失败"
        
        print("✓ 7. 所有测试通过!")
        print("\n🎉 意图识别上下文保持系统已成功集成，可以立即体验!")
        print("\n系统现在可以解决以下问题：")
        print("- 在多步骤任务中保持上下文连贯性")
        print("- 正确识别用户输入为当前任务参数，而非新意图")
        print("- 任务完成后自动恢复正常意图识别")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_system()
    if success:
        print("\n✅ 系统验证成功！您可以立即体验新功能。")
    else:
        print("\n❌ 系统验证失败，请检查错误信息。")
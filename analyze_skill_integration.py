"""
分析技能扩展系统集成问题
"""
import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer
from daip_live.skills.manager import SkillManager
from daip_live.skills.text_analysis import TextAnalysisSkill

def analyze_skill_integration():
    print("="*70)
    print("🔍 技能扩展系统集成分析")
    print("="*70)
    
    # 检查技能管理器
    skill_manager = SkillManager()
    text_skill = TextAnalysisSkill()
    skill_manager.register_skill(text_skill)
    
    print(f"✅ 技能管理器: 已初始化")
    print(f"✅ 已注册技能: {skill_manager.list_skills()}")
    
    # 检查意图识别器
    recognizer = EnhancedIntentRecognizer()
    
    print(f"\n📋 检查意图识别器中的技能相关模式:")
    skill_related_patterns = []
    for intent_name, config in recognizer.intent_patterns.items():
        patterns = config.get("patterns", [])
        skill_patterns = [p for p in patterns if any(keyword in p.lower() for keyword in ["skill", "analy", "text", "process", "assist"])]
        if skill_patterns:
            print(f"  {intent_name}: {skill_patterns[:3]}...")  # 显示前3个
            skill_related_patterns.extend([(intent_name, pattern) for pattern in skill_patterns])
    
    print(f"\n📝 检查技能相关的用户输入:")
    test_inputs = [
        # 技能相关
        "运行技能",
        "执行技能", 
        "使用技能",
        "技能执行",
        "帮我分析文本",
        "分析这段文本",
        "文本分析",
        "处理文本",
        "运行文本分析",
        "使用分析技能",
        "执行分析任务",
        "技能助手",
        "运行助手技能"
    ]
    
    recognized_as_skill = 0
    total_tests = len(test_inputs)
    
    for test_input in test_inputs:
        intent = recognizer.recognize_intent(test_input)
        if intent:
            has_skill_related = any(keyword in intent.name.lower() for keyword in ["skill", "question", "search", "analyze", "process"])
            print(f"  {'✅' if has_skill_related else '➡️ '} '{test_input}' → {intent.name} (置信度: {intent.confidence:.2f})")
            if has_skill_related:
                recognized_as_skill += 1
        else:
            print(f"  ❌ '{test_input}' → 未识别")
    
    print(f"\n📊 技能识别统计: {recognized_as_skill}/{total_tests}")
    
    # 问题诊断
    print(f"\n⚠️  问题分析:")
    
    # 技能集成不足的可能原因：
    print(f"1. 意图识别器可能没有专门的技能执行路径")
    print(f"2. 缺少从自然语言到具体技能的映射")
    print(f"3. TUI可能没有集成技能执行逻辑")
    print(f"4. 技能执行工作流可能未完成")
    
    print(f"\n🎯 需要添加以下集成:")
    print(f"  - 技能执行意图 (skill_execute 或类似)")
    print(f"  - 自然语言到技能的映射")
    print(f"  - 技能执行事件系统")
    print(f"  - TUI技能命令处理")
    
    # 定义需要完成的任务
    print(f"\n📋 技能扩展系统缺少的集成任务:")
    
    missing_tasks = [
        "1. 添加技能执行意图识别模式",
        "2. 实现自然语言到技能的映射逻辑", 
        "3. 创建技能执行工作流处理器",
        "4. 集成技能执行到TUI界面",
        "5. 添加技能执行相关的事件模型",
        "6. 创建技能状态管理和错误处理"
    ]
    
    for task in missing_tasks:
        print(f"   ❌ {task}")
    
    print(f"\n💡 建议解决方案:")
    print(f"   1. 扩展意图识别器以支持技能意图")
    print(f"   2. 添加技能命令的自然语言模式")
    print(f"   3. 更新TUI以处理技能执行请求") 
    print(f"   4. 集成技能执行与现有工作流系统")
    
    print("="*70)
    return len(missing_tasks)

if __name__ == "__main__":
    missing_integration_count = analyze_skill_integration()
    print(f"\n⚠️  发现 {missing_integration_count} 个技能集成缺失项需要补充")
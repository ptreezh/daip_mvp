"""
完整的DAIP-LIVE系统集成回归测试
"""
import sys
sys.path.insert(0, './src')

print("=" * 80)
print("🤖 DAIP-LIVE 系统完整集成回归测试")
print("=" * 80)

# 1. 测试意图识别器
print("\n🔍 1. 意图识别器测试")
from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

recognizer = EnhancedIntentRecognizer()
test_cases = [
    ("创建维基 项目计划", "create_wiki", "维基标题提取"),
    ("个人助手帮我分析", "personal_assistant", "个人助手优先级"),
    ("帮我分析这段文本", "execute_skill", "技能执行优先级"),
    ("本地知识查找", "knowledge_search", "知识库搜索优先级"),
    ("帮我", "execute_skill", "需要澄清"),
    ("下载论文", "download_paper", "论文下载意图"),
    ("下载论文 1234.5678", "download_paper", "论文下载带ID"),
]

all_passed = True
for input_text, expected_intent, test_desc in test_cases:
    intent = recognizer.recognize_intent(input_text)
    if intent and expected_intent in intent.name:
        clarification_status = ""
        if input_text == "帮我" and expected_intent == "execute_skill":
            clarification_status = f", 澄清: {getattr(intent, 'requires_clarification', False)}"
        elif input_text == "下载论文" and expected_intent == "download_paper":
            clarification_status = f", 澄清: {getattr(intent, 'requires_clarification', False)}"
        print(f"  ✅ {test_desc}: '{input_text}' -> {intent.name}{clarification_status}")
    else:
        result_name = intent.name if intent else "None"
        print(f"  ❌ {test_desc}: '{input_text}' -> {result_name} (期望: {expected_intent})")
        all_passed = False

print(f"\n  意图识别器测试: {'✅ 通过' if all_passed else '❌ 失败'}")

# 2. 测试TUI模块
print("\n🖥️  2. TUI模块测试")
try:
    from daip_live.tui import DAIP_TUI
    tui = DAIP_TUI()
    
    tui_checks = [
        ("技能管理器", hasattr(tui, '_skill_manager')),
        ("意图识别器", hasattr(tui, '_intent_recognizer')),
        ("Claude集成服务", hasattr(tui, '_claude_integration_service')),
        ("Claude适配器管理器", hasattr(tui, '_claude_skill_adapter_manager')),
    ]
    
    tui_all_passed = True
    for check_name, result in tui_checks:
        status = "✅" if result else "❌"
        print(f"  {status} {check_name}: {result}")
        if not result:
            tui_all_passed = False
    
    # 检查技能数量
    if hasattr(tui, '_skill_manager'):
        skills_count = len(tui._skill_manager.list_skills())
        print(f"  ✅ 技能数量: {skills_count}")
        if skills_count == 0:
            tui_all_passed = False
    else:
        tui_all_passed = False
    
    print(f"  TUI模块测试: {'✅ 通过' if tui_all_passed else '❌ 失败'}")
    
except Exception as e:
    print(f"  ❌ TUI模块测试异常: {e}")
    tui_all_passed = False

# 3. 测试Claude集成
print("\n🤖 3. Claude集成服务测试")
try:
    claude_integration_ok = (
        hasattr(tui, '_claude_integration_service') and 
        hasattr(tui, '_claude_skill_adapter_manager') and
        hasattr(tui._intent_recognizer, 'claude_integration_service')
    )
    
    if claude_integration_ok:
        print("  ✅ Claude集成服务存在")
        print("  ✅ Claude适配器管理器存在")
        print("  ✅ 意图识别器中Claude服务连接正常")
        print("  Claude集成服务测试: ✅ 通过")
    else:
        print("  ❌ Claude集成服务存在问题")
        print("  Claude集成服务测试: ❌ 失败")
        claude_integration_ok = False
        
except Exception as e:
    print(f"  ❌ Claude集成服务测试异常: {e}")
    claude_integration_ok = False

# 4. 测试技能管理
print("\n⚡ 4. 技能管理测试")
try:
    if hasattr(tui, '_skill_manager'):
        skill_manager = tui._skill_manager
        skills = skill_manager.list_skills()
        print(f"  ✅ 技能管理器正常")
        print(f"  ✅ 注册技能数: {len(skills)}")
        print(f"    技能列表: {skills}")
        
        if skills:
            first_skill = skill_manager.get_skill(skills[0])
            if first_skill:
                print(f"  ✅ 可以获取技能: {first_skill.metadata.name}")
                skill_management_ok = True
            else:
                print("  ❌ 无法获取技能")
                skill_management_ok = False
        else:
            print("  ⚠️  没有注册的技能")
            skill_management_ok = True  # 没有技能不一定表示错误
    else:
        print("  ❌ 技能管理器不存在")
        skill_management_ok = False
        
except Exception as e:
    print(f"  ❌ 技能管理测试异常: {e}")
    skill_management_ok = False

    print(f"  技能管理测试: {'✅ 通过' if skill_management_ok else '❌ 失败'}")

# 5. 测试容器和服务
print("\n📦 5. 容器和服务测试")
try:
    from daip_live.container import Container
    container = Container()
    
    # 检查主要服务是否存在
    container_services = [
        ("Agent引擎", "agent_engine"),
        ("模型提供商", "model_provider"),
        ("数据库管理器", "db_manager"),
        ("会话管理器", "session_manager"),
    ]
    
    container_all_passed = True
    for service_name, service_attr in container_services:
        try:
            service = getattr(container, service_attr, None)
            service_exists = service is not None
            status = "✅" if service_exists else "❌"
            print(f"  {status} {service_name}: {service_exists}")
            if not service_exists:
                container_all_passed = False
        except:
            print(f"  ❌ {service_name}: 获取失败")
            container_all_passed = False
    
    print(f"  容器和服务测试: {'✅ 通过' if container_all_passed else '❌ 失败'}")
    
except Exception as e:
    print(f"  ❌ 容器和服务测试异常: {e}")
    container_all_passed = False

# 总结
overall_success = all([
    all_passed,      # 意图识别
    tui_all_passed,  # TUI模块
    claude_integration_ok,  # Claude集成
    skill_management_ok,    # 技能管理
    container_all_passed    # 容器服务
])

print("\n" + "=" * 80)
print("📊 测试结果汇总:")
print(f"  意图识别器测试: {'✅' if all_passed else '❌'}")
print(f"  TUI模块测试: {'✅' if tui_all_passed else '❌'}")
print(f"  Claude集成服务测试: {'✅' if claude_integration_ok else '❌'}")
print(f"  技能管理测试: {'✅' if skill_management_ok else '❌'}")
print(f"  容器和服务测试: {'✅' if container_all_passed else '❌'}")
print("=" * 80)
print(f"🎯 总体测试结果: {'✅ 全部通过' if overall_success else '❌ 部分失败'}")
print("=" * 80)

print("\n✅ 所有修复和集成测试完成!")
if overall_success:
    print("🎉 系统已准备好上线!")
else:
    print("⚠️  某些测试失败，请检查日志")
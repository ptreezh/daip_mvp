"""
完整的集成测试 - 验证各个组件正确协同工作
"""
import sys
import asyncio
sys.path.insert(0, './src')

print("="*100)
print("🔬 DAIP-LIVE 完整集成测试")
print("="*100)

print("\n1. 测试意图识别器与后端服务集成:")

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer
from daip_live.tui import DAIP_TUI
from daip_live.container import Container

# 测试意图识别器初始化
try:
    recognizer = EnhancedIntentRecognizer()
    print("   ✅ 意图识别器初始化成功")
except Exception as e:
    print(f"   ❌ 意图识别器初始化失败: {e}")

# 测试TUI初始化（这会初始化所有后端服务）
try:
    tui = DAIP_TUI()
    print("   ✅ TUI初始化成功，所有服务组件已加载")
    
    # 检查关键服务是否正确集成
    services_check = [
        ("意图识别器", hasattr(tui, '_intent_recognizer')),
        ("技能管理器", hasattr(tui, '_skill_manager')),
        ("Claude集成服务", hasattr(tui, '_claude_integration_service')),
        ("模型提供者", hasattr(tui, '_model_provider')),
        ("维基管理器", hasattr(tui, '_wiki_manager')),
        ("辩论管理器", hasattr(tui, '_debate_manager'))
    ]
    
    all_services_ok = True
    for service_name, exists in services_check:
        status = "✅" if exists else "❌"
        print(f"      {status} {service_name}: {exists}")
        if not exists:
            all_services_ok = False
    
    if all_services_ok:
        print("   ✅ 所有核心服务正确集成")
    else:
        print("   ❌ 部分服务集成失败")
        
except Exception as e:
    print(f"   ❌ TUI初始化失败: {e}")
    import traceback
    traceback.print_exc()

print("\n2. 测试意图-服务调用链路:")

# 测试完整工作流
test_workflows = [
    ("创建维基测试", "创建维基 人工智能发展史", lambda intent: hasattr(tui, '_wiki_manager') and intent.name == 'create_wiki'),
    ("辩论启动测试", "辩论 AI伦理问题", lambda intent: hasattr(tui, '_debate_manager') and 'debate' in intent.name), 
    ("论文下载测试", "下载论文 机器学习综述", lambda intent: hasattr(tui, '_model_provider') and 'download' in intent.name),
    ("技能执行测试", "帮我分析这段文本", lambda intent: hasattr(tui, '_skill_manager') and 'skill' in intent.name)
]

workflow_success = 0
for workflow_name, test_input, validation_func in test_workflows:
    intent = recognizer.recognize_intent(test_input)
    if intent and validation_func(intent):
        print(f"   ✅ {workflow_name}: '{test_input}' -> {intent.name}")
        workflow_success += 1
    else:
        print(f"   ❌ {workflow_name}: '{test_input}' -> {intent.name if intent else 'None'}")

print(f"   工作流集成成功率: {workflow_success}/{len(test_workflows)}")

print("\n3. 测试参数提取与服务调用集成:")

# 测试参数正确传递给服务
param_integration_tests = [
    ("维基参数传递", "创建维基 项目计划", lambda intent: intent.parameters.get('title', '') == '项目计划'),
    ("辩论参数传递", "辩论 量子计算", lambda intent: intent.parameters.get('topic', '') == '量子计算'),
    ("论文参数传递", "下载论文 深度学习", lambda intent: intent.parameters.get('search_query', '') == '深度学习')
]

param_success = 0
for test_name, test_input, validation_func in param_integration_tests:
    intent = recognizer.recognize_intent(test_input)
    if intent and validation_func(intent):
        print(f"   ✅ {test_name}: 参数正确提取和传递")
        param_success += 1
    else:
        print(f"   ❌ {test_name}: 参数提取或传递错误")
        if intent:
            print(f"      实际参数: {intent.parameters}")

print(f"   参数集成成功率: {param_success}/{len(param_integration_tests)}")

print("\n4. 测试澄清机制与用户交互集成:")

clarification_tests = [
    ("简单维基澄清", "创建维基", lambda intent: getattr(intent, 'requires_clarification', False)),
    ("简单辩论澄清", "辩论", lambda intent: getattr(intent, 'requires_clarification', False)),
    ("简单论文澄清", "下载论文", lambda intent: getattr(intent, 'requires_clarification', False))
]

clarification_success = 0
for test_name, test_input, validation_func in clarification_tests:
    intent = recognizer.recognize_intent(test_input)
    if intent and validation_func(intent):
        print(f"   ✅ {test_name}: 正确触发澄清机制")
        clarification_success += 1
    else:
        print(f"   ❌ {test_name}: 澄清机制失效")
        if intent:
            print(f"      需要澄清: {getattr(intent, 'requires_clarification', False)}")

print(f"   澄清集成成功率: {clarification_success}/{len(clarification_tests)}")

print("\n5. 测试容器依赖注入:")

try:
    container = Container()
    container_dependencies = [
        ("意图识别器", hasattr(container, 'intent_recognizer')),
        ("技能管理器", hasattr(container, 'skill_manager')),
        ("模型提供者", hasattr(container, 'model_provider')),
        ("维基管理器", hasattr(container, 'wiki_manager')),
        ("辩论管理器", hasattr(container, 'debate_manager'))
    ]
    
    container_success = 0
    for dep_name, exists in container_dependencies:
        status = "✅" if exists else "❌"
        print(f"   {status} {dep_name}: {exists}")
        if exists:
            container_success += 1
    
    print(f"   容器依赖注入成功率: {container_success}/{len(container_dependencies)}")
    
except Exception as e:
    print(f"   ❌ 容器初始化失败: {e}")
    container_success = 0

print("\n📋 集成测试摘要:")
overall_score = (workflow_success/len(test_workflows) + param_success/len(param_integration_tests) + 
                 clarification_success/len(clarification_tests) + container_success/len(container_dependencies) if 'container_dependencies' in locals() else 0) * 25

print(f"   工作流集成: {workflow_success}/{len(test_workflows)} ({workflow_success/len(test_workflows)*100:.0f}%)")
print(f"   参数集成: {param_success}/{len(param_integration_tests)} ({param_success/len(param_integration_tests)*100:.0f}%)") 
print(f"   澄清集成: {clarification_success}/{len(clarification_tests)} ({clarification_success/len(clarification_tests)*100:.0f}%)")
print(f"   容器集成: {container_success}/{len(container_dependencies) if 'container_dependencies' in locals() else 0} ({container_success/(len(container_dependencies) if 'container_dependencies' in locals() else 1)*100:.0f}%)")
print(f"   综合集成评分: {overall_score:.1f}/100")

integration_passed = overall_score >= 80  # 设定80分以上为集成通过
print(f"\n🎯 集成测试结果: {'✅ 通过' if integration_passed else '❌ 未通过'}")
print("="*100)
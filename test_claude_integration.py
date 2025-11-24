import sys
sys.path.insert(0, './src')
from daip_live.tui import DAIP_TUI

# 创建TUI实例
tui = DAIP_TUI()
print('✅ TUI实例化成功')

# 检查Claude技能集成服务
print(f'✅ Claude集成服务存在: {hasattr(tui, "_claude_integration_service")}')
if hasattr(tui, '_claude_integration_service'):
    print(f'  Claude集成服务: {tui._claude_integration_service}')
    
    # 检查Claude技能适配器管理器
    print(f'✅ Claude技能适配器管理器存在: {hasattr(tui, "_claude_skill_adapter_manager")}')
    if hasattr(tui, '_claude_skill_adapter_manager'):
        print(f'  Claude技能适配器管理器: {tui._claude_skill_adapter_manager}')
        
    # 检查意图识别器中的Claude集成服务
    print(f'✅ 意图识别器存在: {hasattr(tui, "_intent_recognizer")}')
    if hasattr(tui, '_intent_recognizer'):
        intent_recognizer = tui._intent_recognizer
        print(f'  意图识别器Claude集成服务存在: {hasattr(intent_recognizer, "claude_integration_service")}')
        if hasattr(intent_recognizer, 'claude_integration_service'):
            print(f'  意图识别器Claude集成服务: {intent_recognizer.claude_integration_service}')
        else:
            print('  ❌ 意图识别器中未找到Claude集成服务')
else:
    print('  ❌ Claude集成服务不存在')

# 检查TUI的技能管理器
if hasattr(tui, '_skill_manager'):
    skills = tui._skill_manager.list_skills()
    print(f'✅ TUI技能管理器存在，注册技能数: {len(skills)}')
    print(f'  技能列表: {skills}')
else:
    print('❌ TUI没有技能管理器')

print('Claude技能集成服务测试完成')
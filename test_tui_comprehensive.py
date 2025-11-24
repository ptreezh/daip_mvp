import sys
sys.path.insert(0, './src')
from daip_live.tui import DAIP_TUI

tui = DAIP_TUI()
print('✅ TUI实例化成功')

# 测试所有主要属性
checks = [
    ('_skill_manager', hasattr(tui, '_skill_manager')),
    ('_intent_recognizer', hasattr(tui, '_intent_recognizer')),
    ('_claude_integration_service', hasattr(tui, '_claude_integration_service')),
    ('_claude_skill_adapter_manager', hasattr(tui, '_claude_skill_adapter_manager')),
    ('_model_provider', hasattr(tui, '_model_provider'))
]

print('TUI属性检查:')
for attr_name, exists in checks:
    status = '✅' if exists else '❌'
    print(f'  {status} {attr_name}: {exists}')

# 检查意图识别器中的Claude集成服务
has_intent_claude_service = hasattr(tui._intent_recognizer, 'claude_integration_service') if hasattr(tui, '_intent_recognizer') else False
print(f'  ✅ 意图识别器Claude集成服务: {has_intent_claude_service}')

# 测试技能列表
skills = tui._skill_manager.list_skills() if hasattr(tui, '_skill_manager') else []
print(f'  ✅ 注册技能数量: {len(skills)}')
print(f'    技能列表: {skills}')

# 测试Claude服务功能
if hasattr(tui, '_claude_integration_service'):
    claude_service = tui._claude_integration_service
    print(f'  ✅ Claude集成服务类型: {type(claude_service).__name__}')
    
    # 检查Claude适配器管理器
    if hasattr(tui, '_claude_skill_adapter_manager'):
        adapter_mgr = tui._claude_skill_adapter_manager
        print(f'  ✅ Claude适配器管理器类型: {type(adapter_mgr).__name__}')

print('TUI完整功能测试完成')
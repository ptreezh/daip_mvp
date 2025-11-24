import sys
sys.path.insert(0, './src')
from daip_live.tui import DAIP_TUI

# 测试TUI实例化和基本属性
tui = DAIP_TUI()
print('TUI 实例化成功')

# 测试关键属性是否存在
attributes_to_check = ['_skill_manager', '_intent_recognizer', '_model_provider']
for attr in attributes_to_check:
    if hasattr(tui, attr):
        print(f'  ✅ 属性 {attr} 存在')
    else:
        print(f'  ❌ 属性 {attr} 缺失')

print('TUI基础功能测试完成')
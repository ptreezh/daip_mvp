import sys
sys.path.insert(0, './src')
from daip_live.tui import DAIP_TUI

# 创建TUI实例
tui = DAIP_TUI()
print('✅ TUI实例化成功')

# 测试技能管理器功能
skill_manager = tui._skill_manager
print(f'✅ 技能管理器: {skill_manager}')

# 检查技能列表
skills_list = skill_manager.list_skills()
print(f'✅ 当前技能数量: {len(skills_list)}')
print(f'  技能列表: {skills_list}')

# 测试技能执行
if skills_list:
    first_skill_name = skills_list[0]
    skill = skill_manager.get_skill(first_skill_name)
    if skill:
        print(f'✅ 成功获取技能: {first_skill_name}')
        print(f'  技能描述: {skill.metadata.description}')
    else:
        print(f'❌ 无法获取技能: {first_skill_name}')
else:
    print('⚠️  没有可用的技能')

print('技能管理功能测试完成')
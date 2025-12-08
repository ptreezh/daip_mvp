#!/usr/bin/env python3
"""
全面测试智能默认命令功能
严格检查各个指令的各种场景和参数应用流程
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_comprehensive_command_scenarios():
    """全面测试命令场景"""
    print("🧪 全面测试智能默认命令场景...")

    try:
        from daip_live.tui.simplified_main import SimplifiedTUI
        tui = SimplifiedTUI()

        # 全面的测试用例
        test_cases = [
            # 基础单一命令（无参数）-> 应该添加默认子命令
            {
                'input': ('debate', ''),
                'expected': ('debate', 'start'),
                'description': '无参数debate命令',
                'category': 'basic_defaults'
            },
            {
                'input': ('wiki', ''),
                'expected': ('wiki', 'create'),
                'description': '无参数wiki命令',
                'category': 'basic_defaults'
            },
            {
                'input': ('search', ''),
                'expected': ('search', 'papers'),
                'description': '无参数search命令',
                'category': 'basic_defaults'
            },
            {
                'input': ('doc', ''),
                'expected': ('doc', 'search'),
                'description': '无参数doc命令',
                'category': 'basic_defaults'
            },
            {
                'input': ('model', ''),
                'expected': ('model', 'list'),
                'description': '无参数model命令',
                'category': 'basic_defaults'
            },
            {
                'input': ('session', ''),
                'expected': ('session', 'list'),
                'description': '无参数session命令',
                'category': 'basic_defaults'
            },
            {
                'input': ('todo', ''),
                'expected': ('todo', 'list'),
                'description': '无参数todo命令',
                'category': 'basic_defaults'
            },
            {
                'input': ('help', ''),
                'expected': ('help', 'show'),
                'description': '无参数help命令',
                'category': 'basic_defaults'
            },

            # 有参数的单一命令 -> 应该在参数前添加默认子命令
            {
                'input': ('debate', 'AI伦理话题'),
                'expected': ('debate', 'start AI伦理话题'),
                'description': '有参数debate命令',
                'category': 'with_args'
            },
            {
                'input': ('wiki', '机器学习基础'),
                'expected': ('wiki', 'create 机器学习基础'),
                'description': '有参数wiki命令',
                'category': 'with_args'
            },
            {
                'input': ('search', '深度学习'),
                'expected': ('search', 'papers 深度学习'),
                'description': '有参数search命令',
                'category': 'with_args'
            },
            {
                'input': ('doc', 'Python编程'),
                'expected': ('doc', 'search Python编程'),
                'description': '有参数doc命令',
                'category': 'with_args'
            },
            {
                'input': ('model', 'gpt-4'),
                'expected': ('model', 'list gpt-4'),
                'description': '有参数model命令',
                'category': 'with_args'
            },

            # 已包含默认子命令 -> 不应该修改
            {
                'input': ('debate', 'start AI话题'),
                'expected': ('debate', 'start AI话题'),
                'description': '已包含默认子命令的debate',
                'category': 'already_has_default'
            },
            {
                'input': ('wiki', 'create 新页面'),
                'expected': ('wiki', 'create 新页面'),
                'description': '已包含默认子命令的wiki',
                'category': 'already_has_default'
            },
            {
                'input': ('search', 'papers 机器学习'),
                'expected': ('search', 'papers 机器学习'),
                'description': '已包含默认子命令的search',
                'category': 'already_has_default'
            },
            {
                'input': ('model', 'list all'),
                'expected': ('model', 'list all'),
                'description': '已包含默认子命令的model',
                'category': 'already_has_default'
            },
            {
                'input': ('help', 'show commands'),
                'expected': ('help', 'show commands'),
                'description': '已包含默认子命令的help',
                'category': 'already_has_default'
            },

            # 默认子命令本身 -> 不应该转换
            {
                'input': ('start', ''),
                'expected': ('start', ''),
                'description': 'start命令本身',
                'category': 'default_commands'
            },
            {
                'input': ('create', ''),
                'expected': ('create', ''),
                'description': 'create命令本身',
                'category': 'default_commands'
            },
            {
                'input': ('list', ''),
                'expected': ('list', ''),
                'description': 'list命令本身',
                'category': 'default_commands'
            },
            {
                'input': ('show', ''),
                'expected': ('show', ''),
                'description': 'show命令本身',
                'category': 'default_commands'
            },
            {
                'input': ('search', ''),
                'expected': ('search', 'papers'),
                'description': 'search命令本身（应该获得默认papers）',
                'category': 'default_commands'
            },
            {
                'input': ('papers', ''),
                'expected': ('papers', ''),
                'description': 'papers命令本身',
                'category': 'default_commands'
            },

            # 默认子命令本身有参数 -> 不应该转换
            {
                'input': ('start', 'AI话题'),
                'expected': ('start', 'AI话题'),
                'description': 'start命令有参数',
                'category': 'default_commands_with_args'
            },
            {
                'input': ('create', '新wiki'),
                'expected': ('create', '新wiki'),
                'description': 'create命令有参数',
                'category': 'default_commands_with_args'
            },
            {
                'input': ('list', 'all'),
                'expected': ('list', 'all'),
                'description': 'list命令有参数',
                'category': 'default_commands_with_args'
            },
            {
                'input': ('show', 'help'),
                'expected': ('show', 'help'),
                'description': 'show命令有参数',
                'category': 'default_commands_with_args'
            },

            # 非映射命令 -> 不应该修改
            {
                'input': ('custom', 'command'),
                'expected': ('custom', 'command'),
                'description': '非映射命令',
                'category': 'unmapped_commands'
            },
            {
                'input': ('unknown', ''),
                'expected': ('unknown', ''),
                'description': '未知的空命令',
                'category': 'unmapped_commands'
            },

            # 复杂参数场景
            {
                'input': ('debate', 'start multi topic AI伦理'),
                'expected': ('debate', 'start AI伦理'),
                'description': '复杂参数debate（已包含start）',
                'category': 'complex_args'
            },
            {
                'input': ('wiki', 'create page title 内容'),
                'expected': ('wiki', 'create page title 内容'),
                'description': '复杂参数wiki（已包含create）',
                'category': 'complex_args'
            },
            {
                'input': ('search', 'latest papers about AI'),
                'expected': ('search', 'papers latest papers about AI'),
                'description': '复杂参数search',
                'category': 'complex_args'
            },

            # 边界情况
            {
                'input': ('', ''),
                'expected': ('', ''),
                'description': '空命令',
                'category': 'edge_cases'
            },
            {
                'input': ('debate', '   '),
                'expected': ('debate', 'start'),
                'description': '空白参数',
                'category': 'edge_cases'
            },
            {
                'input': ('Debate', 'topic'),
                'expected': ('Debate', 'start topic'),
                'description': '大小写混合',
                'category': 'edge_cases'
            }
        ]

        print("  🔍 开始全面测试:")
        results = {}
        category_stats = {}

        for i, test_case in enumerate(test_cases, 1):
            cmd, args = test_case['input']
            expected_cmd, expected_args = test_case['expected']
            description = test_case['description']
            category = test_case['category']

            # 执行测试
            actual_cmd, actual_args = tui._apply_smart_defaults(cmd, args)

            # 检查结果
            success = (actual_cmd == expected_cmd and actual_args == expected_args)
            status = "✅" if success else "❌"

            # 显示结果
            print(f"    {i:2d}. {status} {description}")
            print(f"        输入: /{cmd} '{args}'")
            print(f"        期望: /{expected_cmd} '{expected_args}'")
            print(f"        实际: /{actual_cmd} '{actual_args}'")

            if not success:
                print(f"        ❌ 测试失败!")

            # 统计结果
            if category not in results:
                results[category] = {'passed': 0, 'total': 0}
                category_stats[category] = test_case['description']  # 用于显示

            results[category]['total'] += 1
            if success:
                results[category]['passed'] += 1

        # 显示分类统计
        print("\n  📊 分类统计:")
        all_passed = True
        for category, stats in results.items():
            passed = stats['passed']
            total = stats['total']
            percentage = (passed / total * 100) if total > 0 else 0
            status = "✅" if passed == total else "❌"
            print(f"    {status} {category}: {passed}/{total} ({percentage:.1f}%)")
            if passed != total:
                all_passed = False

        return all_passed

    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        return False

def test_user_workflow_scenarios():
    """测试用户工作流程场景"""
    print("\n🔄 测试用户工作流程场景...")

    workflows = [
        {
            'name': '新用户快速开始辩论',
            'steps': [
                ('debate', 'AI伦理辩论'),
                ('wiki', '创建辩论记录'),
                ('search', '查找相关资料'),
                ('model', '查看可用模型'),
                ('help', '获取帮助')
            ],
            'description': '新用户进行一场完整辩论的流程'
        },
        {
            'name': '知识管理流程',
            'steps': [
                ('doc', '搜索Python文档'),
                ('wiki', '创建学习笔记'),
                ('todo', '添加学习任务'),
                ('session', '查看会话历史')
            ],
            'description': '用户进行知识管理的流程'
        },
        {
            'name': '模型探索流程',
            'steps': [
                ('model', ''),
                ('model', 'list available'),
                ('model', 'status check'),
                ('help', 'model commands')
            ],
            'description': '用户探索和选择模型的流程'
        }
    ]

    try:
        from daip_live.tui.simplified_main import SimplifiedTUI
        tui = SimplifiedTUI()

        print("  🔍 测试工作流程:")
        for workflow in workflows:
            print(f"\n    📋 {workflow['name']}:")
            print(f"        {workflow['description']}")

            for i, (cmd, args) in enumerate(workflow['steps'], 1):
                result_cmd, result_args = tui._apply_smart_defaults(cmd, args)
                print(f"        步骤{i:2d}: /{cmd} '{args}' -> /{result_cmd} '{result_args}'")

        return True

    except Exception as e:
        print(f"  ❌ 工作流程测试失败: {e}")
        return False

def test_command_consistency():
    """测试命令一致性"""
    print("\n🔧 测试命令一致性...")

    try:
        from daip_live.tui.simplified_main import SimplifiedTUI
        tui = SimplifiedTUI()

        # 检查所有映射命令的一致性
        default_mappings = {
            'debate': 'start',
            'wiki': 'create',
            'search': 'papers',
            'doc': 'search',
            'model': 'list',
            'session': 'list',
            'todo': 'list',
            'help': 'show',
            'quit': 'confirm',
            'exit': 'confirm',
            'clear': 'screen',
            'compact': 'session',
            'scaffold': 'project'
        }

        print("  🔍 检查映射一致性:")
        consistency_passed = True

        for cmd, default_subcmd in default_mappings.items():
            # 测试无参数情况
            result_cmd, result_args = tui._apply_smart_defaults(cmd, '')
            expected = (cmd, default_subcmd)

            if (result_cmd, result_args) != expected:
                print(f"    ❌ {cmd}: 期望 {expected}, 实际 {(result_cmd, result_args)}")
                consistency_passed = False
            else:
                print(f"    ✅ {cmd} -> {default_subcmd}")

            # 测试有参数情况
            test_arg = "test_parameter"
            result_cmd, result_args = tui._apply_smart_defaults(cmd, test_arg)
            expected = (cmd, f"{default_subcmd} {test_arg}")

            if (result_cmd, result_args) != expected:
                print(f"    ❌ {cmd} {test_arg}: 期望 {expected}, 实际 {(result_cmd, result_args)}")
                consistency_passed = False
            else:
                print(f"    ✅ {cmd} {test_arg} -> {default_subcmd} {test_arg}")

        return consistency_passed

    except Exception as e:
        print(f"  ❌ 一致性测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 全面智能默认命令功能测试\n")

    results = []

    # 测试1: 全面命令场景
    results.append(test_comprehensive_command_scenarios())

    # 测试2: 用户工作流程
    results.append(test_user_workflow_scenarios())

    # 测试3: 命令一致性
    results.append(test_command_consistency())

    # 总结
    passed = sum(results)
    total = len(results)

    print(f"\n📊 全面测试总结:")
    if passed == total:
        print(f"  🎉 所有 {total} 个测试类别通过!")
        print("\n✅ 智能默认命令功能全面验证成功!")
        print("\n🎯 功能总结:")
        print("  🤖 智能识别单一子命令并自动添加默认值")
        print("  ⚡ 支持有参数和无参数两种场景")
        print("  🔧 保持已包含默认子命令的命令不变")
        print("  🛡️ 正确处理默认子命令本身")
        print("  🎨 简化用户操作，减少记忆负担")
        print("  📋 提供一致的用户体验")
        return 0
    else:
        print(f"  ⚠️ {passed}/{total} 个测试类别通过")
        print("\n🔧 仍需一些改进")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
#!/usr/bin/env python3
"""
分析单一大文件TUI vs 模块化TUI的功能差异
用于确保模块化TUI具备所有原有功能
"""

import sys
import os
import re

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def analyze_monolithic_tui_features():
    """分析单一大文件TUI的所有功能"""
    print("🔍 分析单一大文件TUI功能...")

    tui_file = "src/daip_live/tui.py"

    if not os.path.exists(tui_file):
        print(f"❌ 单一大文件TUI不存在: {tui_file}")
        return {}

    with open(tui_file, 'r', encoding='utf-8') as f:
        content = f.read()

    features = {
        "classes": [],
        "actions": [],
        "handlers": [],
        "commands": [],
        "screens": [],
        "bindings": [],
        "css_classes": []
    }

    # 提取类定义
    classes = re.findall(r'^class\s+(\w+)', content, re.MULTILINE)
    features["classes"] = [cls for cls in classes if cls not in ["Message", "Enum", "Any", "Optional", "Dict", "List"]]

    # 提取action方法
    actions = re.findall(r'def\s+action_(\w+)\s*\(', content)
    features["actions"] = actions

    # 提取handler方法
    handlers = re.findall(r'def\s+_handle_(\w+)_command\s*\(', content)
    features["handlers"] = handlers

    # 提取bind键绑定
    bindings = re.findall(r'Binding\([^,]+,\s*"([^"]+)"', content)
    features["bindings"] = bindings

    # 提取CSS类
    css_classes = re.findall(r'\.(\w+)\s*{', content)
    features["css_classes"] = css_classes

    # 分析具体功能模块
    # 查找所有以 _handle_ 开头的方法（包括非命令处理器）
    all_handlers = re.findall(r'def\s+(_handle_\w+)\s*\(', content)
    features["all_handler_methods"] = all_handlers

    # 查找异步方法
    async_methods = re.findall(r'async def\s+(\w+)\s*\(', content)
    features["async_methods"] = async_methods

    return features

def analyze_modular_tui_features():
    """分析模块化TUI的所有功能"""
    print("🔍 分析模块化TUI功能...")

    modular_tui_dir = "src/daip_live/tui"

    if not os.path.exists(modular_tui_dir):
        print(f"❌ 模块化TUI目录不存在: {modular_tui_dir}")
        return {}

    features = {
        "classes": [],
        "actions": [],
        "handlers": [],
        "commands": [],
        "screens": [],
        "bindings": [],
        "css_classes": [],
        "files": []
    }

    # 遍历所有模块文件
    for filename in os.listdir(modular_tui_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            filepath = os.path.join(modular_tui_dir, filename)
            features["files"].append(filename)

            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取类定义
            classes = re.findall(r'^class\s+(\w+)', content, re.MULTILINE)
            features["classes"].extend([f"{cls}({filename})" for cls in classes])

            # 提取action方法
            actions = re.findall(r'def\s+action_(\w+)\s*\(', content)
            features["actions"].extend([f"{action}({filename})" for action in actions])

            # 提取handler方法
            handlers = re.findall(r'def\s+_handle_(\w+)_command\s*\(', content)
            features["handlers"].extend([f"{handler}({filename})" for handler in handlers])

            # 提取bind键绑定
            bindings = re.findall(r'Binding\([^,]+,\s*"([^"]+)"', content)
            features["bindings"].extend([f"{binding}({filename})" for binding in bindings])

            # 提取CSS类
            css_classes = re.findall(r'\.(\w+)\s*{', content)
            features["css_classes"].extend([f"{css_class}({filename})" for css_class in css_classes])

            # 查找所有处理方法
            all_handlers = re.findall(r'def\s+(_handle_\w+)\s*\(', content)
            features["all_handler_methods"] = features.get("all_handler_methods", []) + [f"{handler}({filename})" for handler in all_handlers]

            # 查找异步方法
            async_methods = re.findall(r'async def\s+(\w+)\s*\(', content)
            features["async_methods"] = features.get("async_methods", []) + [f"{method}({filename})" for method in async_methods]

    return features

def compare_features(monolithic, modular):
    """对比两个TUI的功能差异"""
    print("\n📊 功能对比分析:")

    # 提取纯功能名称（去掉文件名后缀）
    monolithic_actions = set(monolithic.get("actions", []))
    modular_actions = set([action.split('(')[0] for action in modular.get("actions", [])])

    monolithic_handlers = set(monolithic.get("handlers", []))
    modular_handlers = set([handler.split('(')[0] for handler in modular.get("handlers", [])])

    monolithic_bindings = set(monolithic.get("bindings", []))
    modular_bindings = set([binding.split('(')[0] for binding in modular.get("bindings", [])])

    # 计算差异
    missing_actions = monolithic_actions - modular_actions
    missing_handlers = monolithic_handlers - modular_handlers
    missing_bindings = monolithic_bindings - modular_bindings

    print(f"\n🎯 Actions对比:")
    print(f"  单一大文件TUI: {len(monolithic_actions)} 个")
    print(f"  模块化TUI: {len(modular_actions)} 个")
    if missing_actions:
        print(f"  ❌ 缺失的Actions: {sorted(missing_actions)}")
    else:
        print("  ✅ 所有Actions都已实现")

    print(f"\n🔧 Command Handlers对比:")
    print(f"  单一大文件TUI: {len(monolithic_handlers)} 个")
    print(f"  模块化TUI: {len(modular_handlers)} 个")
    if missing_handlers:
        print(f"  ❌ 缺失的Handlers: {sorted(missing_handlers)}")
    else:
        print("  ✅ 所有Command Handlers都已实现")

    print(f"\n⌨️ Key Bindings对比:")
    print(f"  单一大文件TUI: {len(monolithic_bindings)} 个")
    print(f"  模块化TUI: {len(modular_bindings)} 个")
    if missing_bindings:
        print(f"  ❌ 缺失的Bindings: {sorted(missing_bindings)}")
    else:
        print("  ✅ 所有Key Bindings都已实现")

    return {
        "missing_actions": missing_actions,
        "missing_handlers": missing_handlers,
        "missing_bindings": missing_bindings
    }

def main():
    """主分析函数"""
    print("🚀 开始TUI功能对比分析\n")

    # 分析单一大文件TUI
    monolithic_features = analyze_monolithic_tui_features()

    print(f"✅ 单一大文件TUI分析完成:")
    print(f"  📁 类: {len(monolithic_features.get('classes', []))} 个")
    print(f"  ⚡ Actions: {len(monolithic_features.get('actions', []))} 个")
    print(f"  🔧 Command Handlers: {len(monolithic_features.get('handlers', []))} 个")
    print(f"  ⌨️ Key Bindings: {len(monolithic_features.get('bindings', []))} 个")
    print(f"  🎨 CSS Classes: {len(monolithic_features.get('css_classes', []))} 个")

    # 分析模块化TUI
    modular_features = analyze_modular_tui_features()

    print(f"\n✅ 模块化TUI分析完成:")
    print(f"  📁 文件: {len(modular_features.get('files', []))} 个")
    print(f"  📁 类: {len(modular_features.get('classes', []))} 个")
    print(f"  ⚡ Actions: {len(modular_features.get('actions', []))} 个")
    print(f"  🔧 Command Handlers: {len(modular_features.get('handlers', []))} 个")
    print(f"  ⌨️ Key Bindings: {len(modular_features.get('bindings', []))} 个")
    print(f"  🎨 CSS Classes: {len(modular_features.get('css_classes', []))} 个")

    # 对比分析
    missing_features = compare_features(monolithic_features, modular_features)

    # 生成修复建议
    print(f"\n🛠️ 修复建议:")
    total_missing = (
        len(missing_features["missing_actions"]) +
        len(missing_features["missing_handlers"]) +
        len(missing_features["missing_bindings"])
    )

    if total_missing > 0:
        print(f"  📋 总共需要实现 {total_missing} 个缺失功能")

        if missing_features["missing_actions"]:
            print(f"\n  ⚡ 缺失的Actions需要在相应的模块中实现:")
            for action in sorted(missing_features["missing_actions"]):
                print(f"    - action_{action}")

        if missing_features["missing_handlers"]:
            print(f"\n  🔧 缺失的Command Handlers需要在commands.py或相应模块中实现:")
            for handler in sorted(missing_features["missing_handlers"]):
                print(f"    - _handle_{handler}_command")

        if missing_features["missing_bindings"]:
            print(f"\n  ⌨️ 缺失的Key Bindings需要在主TUI类中添加:")
            for binding in sorted(missing_features["missing_bindings"]):
                print(f"    - {binding}")
    else:
        print("  ✅ 模块化TUI已经具备所有单一大文件TUI的功能!")

    return missing_features

if __name__ == "__main__":
    missing_features = main()
    sys.exit(0 if sum(len(v) for v in missing_features.values()) == 0 else 1)
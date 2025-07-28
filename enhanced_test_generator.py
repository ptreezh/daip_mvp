#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强的测试生成器
能够分析构造函数参数并生成正确的实例化代码
"""

import json
import ast
from pathlib import Path
from typing import Dict, List, Any, Optional

class EnhancedTestGenerator:
    """增强的测试生成器"""
    
    def __init__(self):
        self.interface_map = self._load_interface_map()
        self.architecture_map = self._load_architecture_map()
    
    def _load_interface_map(self) -> Dict[str, Any]:
        """加载接口映射"""
        try:
            with open("interface_map.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _load_architecture_map(self) -> Dict[str, Any]:
        """加载架构映射"""
        try:
            with open("architecture_map.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def get_constructor_info(self, class_name: str) -> Dict[str, Any]:
        """获取构造函数信息"""
        class_info = self.interface_map.get("available_classes", {}).get(class_name)
        if not class_info:
            return {}
        
        full_name = class_info["full_name"]
        class_details = self.architecture_map.get("classes", {}).get(full_name, {})
        
        # 查找__init__方法
        for method in class_details.get("methods", []):
            if method["name"] == "__init__":
                return method
        
        return {}
    
    def generate_constructor_call(self, class_name: str) -> str:
        """生成构造函数调用代码"""
        constructor_info = self.get_constructor_info(class_name)
        
        if not constructor_info:
            return f"{class_name}()"
        
        args = constructor_info.get("args", [])
        
        # 移除self参数
        if args and args[0] == "self":
            args = args[1:]
        
        if not args:
            return f"{class_name}()"
        
        # 为常见参数生成默认值
        arg_defaults = {
            "console": "Console()",
            "command_queue": "asyncio.Queue()",
            "config": "{}",
            "config_dir": '".kiro/config"',
            "llm_interface": "None",
            "role_manager": "None",
            "services": "{}",
            "workflow_name": '"test_workflow"',
            "execution_id": '"test_execution"'
        }
        
        constructor_args = []
        required_imports = set()
        
        for arg in args:
            if arg in arg_defaults:
                constructor_args.append(f"{arg}={arg_defaults[arg]}")
                
                # 添加必要的导入
                if arg == "console":
                    required_imports.add("from rich.console import Console")
                elif arg == "command_queue":
                    required_imports.add("import asyncio")
            else:
                # 尝试猜测参数类型
                if "path" in arg.lower() or "dir" in arg.lower():
                    constructor_args.append(f'{arg}="test_path"')
                elif "name" in arg.lower():
                    constructor_args.append(f'{arg}="test_name"')
                elif "id" in arg.lower():
                    constructor_args.append(f'{arg}="test_id"')
                else:
                    constructor_args.append(f"{arg}=None")
        
        constructor_call = f"{class_name}({', '.join(constructor_args)})"
        
        return constructor_call, required_imports
    
    def generate_enhanced_class_test(self, class_name: str) -> str:
        """生成增强的类测试代码"""
        class_info = self.interface_map.get("available_classes", {}).get(class_name)
        if not class_info:
            return f'# ❌ 未找到类 {class_name}'
        
        import_stmt = f"from {class_info['module']} import {class_name}"
        constructor_result = self.generate_constructor_call(class_name)
        
        if isinstance(constructor_result, tuple):
            constructor_call, required_imports = constructor_result
            additional_imports = "\n".join(required_imports)
        else:
            constructor_call = constructor_result
            additional_imports = ""
        
        # 获取方法和属性
        methods = self.interface_map.get("class_methods", {}).get(class_name, [])
        attributes = self.interface_map.get("class_attributes", {}).get(class_name, [])
        
        test_code = f'''def test_{class_name.lower()}():
    """测试{class_name}"""
    try:
        {import_stmt}
        {additional_imports}
        
        # 创建实例
        instance = {constructor_call}
        
        # 验证实例创建成功
        assert instance is not None, "实例创建失败"'''
        
        # 只测试公共属性
        public_attributes = [attr for attr in attributes if not attr.startswith('_')]
        for attr in public_attributes[:3]:  # 只测试前3个
            test_code += f'''
        assert hasattr(instance, '{attr}'), "缺少{attr}属性"'''
        
        # 只测试公共方法
        public_methods = [method for method in methods if not method.startswith('_')]
        for method in public_methods[:3]:  # 只测试前3个
            test_code += f'''
        assert hasattr(instance, '{method}'), "缺少{method}方法"'''
        
        test_code += f'''
        
        print("✅ {class_name}验证通过")
        return True
        
    except Exception as e:
        print(f"❌ {class_name}验证失败: {{e}}")
        return False'''
        
        return test_code
    
    def generate_complete_test_file(self) -> str:
        """生成完整的测试文件"""
        
        # 查找用户干预相关的类
        relevant_classes = []
        
        # 搜索相关类
        all_classes = self.interface_map.get("available_classes", {})
        keywords = ["intervention", "steering", "parameter", "customizer", "transparency", "interactive"]
        
        for class_name in all_classes:
            for keyword in keywords:
                if keyword.lower() in class_name.lower():
                    relevant_classes.append(class_name)
                    break
        
        # 去重并排序
        relevant_classes = sorted(list(set(relevant_classes)))
        
        test_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强的用户干预机制验证 - 基于真实架构和构造函数分析
"""

import sys
import os
import asyncio
sys.path.append('src')

'''
        
        # 为每个类生成测试
        for class_name in relevant_classes:
            test_code += self.generate_enhanced_class_test(class_name) + "\n\n"
        
        # 生成主函数
        test_code += f'''async def main():
    """主验证函数"""
    print("🚀 开始验证用户干预机制 (增强版)")
    
    tests = ['''
        
        for class_name in relevant_classes:
            test_name = f"test_{class_name.lower()}"
            test_code += f'''
        ("{class_name}", {test_name}),'''
        
        test_code += '''
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 验证 {test_name}...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
                
            if result:
                passed += 1
            else:
                print(f"❌ {test_name} 验证失败")
        except Exception as e:
            print(f"❌ {test_name} 验证异常: {e}")
    
    print(f"\n📊 验证结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✅ 所有验证通过")
        return True
    else:
        print("⚠️ 部分验证失败")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)'''
        
        return test_code

def main():
    """主函数"""
    generator = EnhancedTestGenerator()
    
    if not generator.interface_map:
        print("请先运行: python project_architecture_map.py")
        return
    
    print("🎯 增强测试生成器")
    print("=" * 50)
    
    # 生成增强的测试
    test_code = generator.generate_complete_test_file()
    
    with open("enhanced_user_intervention_test.py", 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("✅ 增强测试文件已生成: enhanced_user_intervention_test.py")
    
    # 显示找到的相关类
    all_classes = generator.interface_map.get("available_classes", {})
    keywords = ["intervention", "steering", "parameter", "customizer", "transparency", "interactive"]
    
    relevant_classes = []
    for class_name in all_classes:
        for keyword in keywords:
            if keyword.lower() in class_name.lower():
                relevant_classes.append(class_name)
                break
    
    print(f"\n🔍 找到 {len(relevant_classes)} 个相关类:")
    for class_name in sorted(set(relevant_classes)):
        constructor_info = generator.get_constructor_info(class_name)
        args = constructor_info.get("args", [])
        if args and args[0] == "self":
            args = args[1:]
        print(f"   - {class_name}({', '.join(args)})")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""智能测试生成器
基于真实的项目架构生成准确的测试代码
"""

import json
from typing import Any, Optional


class SmartTestGenerator:
    """智能测试生成器"""
    
    def __init__(self):
        self.interface_map = self._load_interface_map()
        self.architecture_map = self._load_architecture_map()
    
    def _load_interface_map(self) -> dict[str, Any]:
        """加载接口映射"""
        try:
            with open("interface_map.json", encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ interface_map.json 未找到，请先运行 project_architecture_map.py")
            return {}
    
    def _load_architecture_map(self) -> dict[str, Any]:
        """加载架构映射"""
        try:
            with open("architecture_map.json", encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ architecture_map.json 未找到，请先运行 project_architecture_map.py")
            return {}
    
    def find_class_info(self, class_name: str) -> Optional[dict[str, Any]]:
        """查找类信息"""
        if class_name in self.interface_map.get("available_classes", {}):
            class_info = self.interface_map["available_classes"][class_name]
            full_name = class_info["full_name"]
            
            # 从架构映射中获取详细信息
            if full_name in self.architecture_map.get("classes", {}):
                detailed_info = self.architecture_map["classes"][full_name]
                return {
                    **class_info,
                    **detailed_info
                }
        return None
    
    def generate_import_statement(self, class_name: str) -> str:
        """生成正确的导入语句"""
        class_info = self.find_class_info(class_name)
        if class_info:
            module = class_info["module"]
            return f"from {module} import {class_name}"
        return f"# ❌ 未找到类 {class_name} 的导入信息"
    
    def generate_class_test(self, class_name: str, test_name: str = None) -> str:
        """生成类测试代码"""
        class_info = self.find_class_info(class_name)
        if not class_info:
            return f'# ❌ 未找到类 {class_name}'
        
        test_name = test_name or f"test_{class_name.lower()}"
        import_stmt = self.generate_import_statement(class_name)
        
        # 获取方法和属性
        methods = self.interface_map.get("class_methods", {}).get(class_name, [])
        attributes = self.interface_map.get("class_attributes", {}).get(class_name, [])
        
        # 生成测试代码
        test_code = f'''def {test_name}():
    """测试{class_name}"""
    try:
        {import_stmt}
        
        # 创建实例
        instance = {class_name}()
        
        # 验证基本属性'''
        
        for attr in attributes[:5]:  # 只测试前5个属性
            test_code += f'''
        assert hasattr(instance, '{attr}'), "缺少{attr}属性"'''
        
        test_code += '''
        
        # 验证基本方法'''
        
        for method in methods[:5]:  # 只测试前5个方法
            if not method.startswith('_'):  # 跳过私有方法
                test_code += f'''
        assert hasattr(instance, '{method}'), "缺少{method}方法"'''
        
        test_code += f'''
        
        print("✅ {class_name}验证通过")
        return True
        
    except Exception as e:
        print(f"❌ {class_name}验证失败: {{e}}")
        return False'''
        
        return test_code
    
    def generate_user_intervention_test(self) -> str:
        """生成用户干预机制的准确测试"""
        # 查找相关类
        relevant_classes = [
            "UserInterventionHandler",
            "WorkflowSteering", 
            "ParameterManager",
            "WorkflowCustomizer",
            "TransparencyController",
            "InteractiveController"
        ]
        
        found_classes = []
        for class_name in relevant_classes:
            if self.find_class_info(class_name):
                found_classes.append(class_name)
        
        test_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证用户干预机制 - 基于真实架构生成
"""

import sys
import os
import asyncio
sys.path.append('src')

'''
        
        # 为每个找到的类生成测试
        for class_name in found_classes:
            test_code += self.generate_class_test(class_name) + "\n\n"
        
        # 生成主测试函数
        test_code += '''async def main():
    """主验证函数"""
    print("🚀 开始验证用户干预机制")
    
    tests = ['''
        
        for class_name in found_classes:
            test_name = f"test_{class_name.lower()}"
            test_code += f'''
        ("{class_name}", {test_name}),'''
        
        test_code += '''
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\\n📋 验证 {test_name}...")
        if asyncio.iscoroutinefunction(test_func):
            result = await test_func()
        else:
            result = test_func()
            
        if result:
            passed += 1
        else:
            print(f"❌ {test_name} 验证失败，停止后续测试")
            break
    
    if passed == total:
        print(f"\\n✅ 所有验证通过 ({passed}/{total})")
        return True
    else:
        print(f"\\n❌ 验证失败 ({passed}/{total})")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)'''
        
        return test_code
    
    def list_available_classes(self, pattern: str = "") -> list[str]:
        """列出可用的类"""
        classes = list(self.interface_map.get("available_classes", {}).keys())
        if pattern:
            classes = [c for c in classes if pattern.lower() in c.lower()]
        return sorted(classes)
    
    def get_class_details(self, class_name: str) -> str:
        """获取类的详细信息"""
        class_info = self.find_class_info(class_name)
        if not class_info:
            return f"❌ 未找到类 {class_name}"
        
        details = f"""
📋 类信息: {class_name}
   模块: {class_info['module']}
   文件: {class_info['file']}
   
🔧 方法 ({len(self.interface_map.get('class_methods', {}).get(class_name, []))})个:
"""
        methods = self.interface_map.get("class_methods", {}).get(class_name, [])
        for method in methods[:10]:  # 只显示前10个
            details += f"   - {method}\n"
        
        if len(methods) > 10:
            details += f"   ... 还有 {len(methods) - 10} 个方法\n"
        
        details += f"""
📦 属性 ({len(self.interface_map.get('class_attributes', {}).get(class_name, []))})个:
"""
        attributes = self.interface_map.get("class_attributes", {}).get(class_name, [])
        for attr in attributes[:10]:  # 只显示前10个
            details += f"   - {attr}\n"
        
        if len(attributes) > 10:
            details += f"   ... 还有 {len(attributes) - 10} 个属性\n"
        
        return details

def main():
    """主函数"""
    generator = SmartTestGenerator()
    
    if not generator.interface_map:
        print("请先运行: python project_architecture_map.py")
        return
    
    print("🎯 智能测试生成器")
    print("=" * 50)
    
    # 生成用户干预测试
    print("📝 生成用户干预机制测试...")
    test_code = generator.generate_user_intervention_test()
    
    with open("smart_user_intervention_test.py", 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("✅ 测试文件已生成: smart_user_intervention_test.py")
    
    # 显示相关类信息
    print("\\n🔍 相关类信息:")
    intervention_classes = generator.list_available_classes("intervention")
    workflow_classes = generator.list_available_classes("workflow")
    parameter_classes = generator.list_available_classes("parameter")
    
    print(f"   干预相关: {intervention_classes}")
    print(f"   工作流相关: {workflow_classes[:5]}...")  # 只显示前5个
    print(f"   参数相关: {parameter_classes}")

if __name__ == "__main__":
    main()
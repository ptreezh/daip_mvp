#!/usr/bin/env python3
"""项目架构映射工具
用于生成完整的项目结构、类定义、方法签名等信息
"""

import ast
import json
from pathlib import Path
from typing import Any


class ProjectArchitectureMapper:
    """项目架构映射器"""
    
    def __init__(self, project_root: str = "src"):
        self.project_root = Path(project_root)
        self.architecture_map = {
            "modules": {},
            "classes": {},
            "functions": {},
            "imports": {},
            "errors": []
        }
    
    def scan_project(self):
        """扫描整个项目结构"""
        print("🔍 开始扫描项目架构...")
        
        for py_file in self.project_root.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
                
            try:
                self._analyze_file(py_file)
            except Exception as e:
                self.architecture_map["errors"].append({
                    "file": str(py_file),
                    "error": str(e)
                })
        
        print(f"✅ 扫描完成，发现 {len(self.architecture_map['modules'])} 个模块")
        return self.architecture_map
    
    def _analyze_file(self, file_path: Path):
        """分析单个Python文件"""
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            module_name = self._get_module_name(file_path)
            
            module_info = {
                "path": str(file_path),
                "classes": [],
                "functions": [],
                "imports": []
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = self._analyze_class(node)
                    module_info["classes"].append(class_info)
                    self.architecture_map["classes"][f"{module_name}.{node.name}"] = class_info
                
                elif isinstance(node, ast.FunctionDef):
                    func_info = self._analyze_function(node)
                    module_info["functions"].append(func_info)
                    self.architecture_map["functions"][f"{module_name}.{node.name}"] = func_info
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    import_info = self._analyze_import(node)
                    module_info["imports"].append(import_info)
            
            self.architecture_map["modules"][module_name] = module_info
            
        except Exception as e:
            self.architecture_map["errors"].append({
                "file": str(file_path),
                "error": f"Parse error: {str(e)}"
            })
    
    def _get_module_name(self, file_path: Path) -> str:
        """获取模块名"""
        relative_path = file_path.relative_to(self.project_root.parent)
        module_parts = list(relative_path.parts[:-1]) + [relative_path.stem]
        if module_parts[-1] == "__init__":
            module_parts = module_parts[:-1]
        return ".".join(module_parts)
    
    def _analyze_class(self, node: ast.ClassDef) -> dict[str, Any]:
        """分析类定义"""
        methods = []
        attributes = []
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = {
                    "name": item.name,
                    "args": [arg.arg for arg in item.args.args],
                    "is_async": isinstance(item, ast.AsyncFunctionDef),
                    "decorators": [self._get_decorator_name(d) for d in item.decorator_list]
                }
                methods.append(method_info)
            
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attributes.append(target.id)
        
        return {
            "name": node.name,
            "bases": [self._get_base_name(base) for base in node.bases],
            "methods": methods,
            "attributes": attributes,
            "decorators": [self._get_decorator_name(d) for d in node.decorator_list]
        }
    
    def _analyze_function(self, node: ast.FunctionDef) -> dict[str, Any]:
        """分析函数定义"""
        return {
            "name": node.name,
            "args": [arg.arg for arg in node.args.args],
            "is_async": isinstance(node, ast.AsyncFunctionDef),
            "decorators": [self._get_decorator_name(d) for d in node.decorator_list]
        }
    
    def _analyze_import(self, node) -> dict[str, Any]:
        """分析导入语句"""
        if isinstance(node, ast.Import):
            return {
                "type": "import",
                "modules": [alias.name for alias in node.names],
                "aliases": {alias.name: alias.asname for alias in node.names if alias.asname}
            }
        elif isinstance(node, ast.ImportFrom):
            return {
                "type": "from_import",
                "module": node.module,
                "names": [alias.name for alias in node.names],
                "aliases": {alias.name: alias.asname for alias in node.names if alias.asname}
            }
    
    def _get_decorator_name(self, decorator) -> str:
        """获取装饰器名称"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f"{decorator.value.id}.{decorator.attr}"
        return str(decorator)
    
    def _get_base_name(self, base) -> str:
        """获取基类名称"""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return f"{base.value.id}.{base.attr}"
        return str(base)
    
    def generate_interface_map(self) -> dict[str, Any]:
        """生成接口映射"""
        interface_map = {
            "available_classes": {},
            "class_methods": {},
            "class_attributes": {},
            "import_map": {}
        }
        
        # 整理可用的类
        for class_full_name, class_info in self.architecture_map["classes"].items():
            module_name = ".".join(class_full_name.split(".")[:-1])
            class_name = class_full_name.split(".")[-1]
            
            interface_map["available_classes"][class_name] = {
                "full_name": class_full_name,
                "module": module_name,
                "file": self.architecture_map["modules"].get(module_name, {}).get("path", "")
            }
            
            interface_map["class_methods"][class_name] = [
                method["name"] for method in class_info["methods"]
            ]
            
            interface_map["class_attributes"][class_name] = class_info["attributes"]
        
        # 整理导入映射
        for module_name, module_info in self.architecture_map["modules"].items():
            for import_info in module_info["imports"]:
                if import_info["type"] == "from_import" and import_info["module"]:
                    for name in import_info["names"]:
                        interface_map["import_map"][name] = {
                            "from_module": import_info["module"],
                            "in_module": module_name
                        }
        
        return interface_map
    
    def save_architecture_map(self, output_file: str = "architecture_map.json"):
        """保存架构映射到文件"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.architecture_map, f, indent=2, ensure_ascii=False)
        print(f"📁 架构映射已保存到 {output_file}")
    
    def save_interface_map(self, output_file: str = "interface_map.json"):
        """保存接口映射到文件"""
        interface_map = self.generate_interface_map()
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(interface_map, f, indent=2, ensure_ascii=False)
        print(f"📁 接口映射已保存到 {output_file}")
    
    def print_summary(self):
        """打印项目摘要"""
        print("\n📊 项目架构摘要:")
        print(f"   模块数量: {len(self.architecture_map['modules'])}")
        print(f"   类数量: {len(self.architecture_map['classes'])}")
        print(f"   函数数量: {len(self.architecture_map['functions'])}")
        print(f"   错误数量: {len(self.architecture_map['errors'])}")
        
        if self.architecture_map['errors']:
            print("\n❌ 发现的错误:")
            for error in self.architecture_map['errors'][:5]:  # 只显示前5个
                print(f"   {error['file']}: {error['error']}")
        
        print("\n🏗️ 主要模块:")
        for module_name, module_info in list(self.architecture_map['modules'].items())[:10]:
            class_count = len(module_info['classes'])
            func_count = len(module_info['functions'])
            print(f"   {module_name}: {class_count} 类, {func_count} 函数")

def main():
    """主函数"""
    mapper = ProjectArchitectureMapper()
    
    # 扫描项目
    architecture_map = mapper.scan_project()
    
    # 保存映射文件
    mapper.save_architecture_map()
    mapper.save_interface_map()
    
    # 打印摘要
    mapper.print_summary()
    
    print("\n✅ 项目架构映射完成！")
    print("   - architecture_map.json: 完整的项目结构")
    print("   - interface_map.json: 类和方法的快速查找")

if __name__ == "__main__":
    main()
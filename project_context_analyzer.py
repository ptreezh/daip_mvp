#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目上下文分析器

在开始任何编码任务前，必须使用此工具进行全面的项目上下文分析
确保充分理解现有实现、接口依赖和架构约束
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProjectContextAnalyzer:
    """项目上下文分析器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.required_docs = [
            "PROJECT_SUMMARY.md",
            "IMPLEMENTATION_SUMMARY.md", 
            "architecture_map.json",
            "interface_map.json",
            "STANDARD_WORKFLOW.md"
        ]
        
        self.context = {}
        self.analysis_report = {}
    
    def analyze_full_context(self, task_description: str) -> Dict[str, Any]:
        """执行完整的项目上下文分析"""
        logger.info("🔍 开始项目上下文分析...")
        
        # 步骤1：读取核心文档
        self._read_core_documents()
        
        # 步骤2：分析架构映射
        self._analyze_architecture_mapping()
        
        # 步骤3：分析接口依赖
        self._analyze_interface_dependencies()
        
        # 步骤4：扫描相关实现
        self._scan_related_implementations(task_description)
        
        # 步骤5：生成分析报告
        self._generate_analysis_report(task_description)
        
        logger.info("✅ 项目上下文分析完成")
        return self.analysis_report
    
    def _read_core_documents(self):
        """读取核心文档"""
        logger.info("📚 读取核心文档...")
        
        self.context['documents'] = {}
        missing_docs = []
        
        for doc in self.required_docs:
            doc_path = self.project_root / doc
            if doc_path.exists():
                try:
                    if doc.endswith('.json'):
                        with open(doc_path, 'r', encoding='utf-8') as f:
                            self.context['documents'][doc] = json.load(f)
                    else:
                        with open(doc_path, 'r', encoding='utf-8') as f:
                            self.context['documents'][doc] = f.read()
                    logger.info(f"✅ 已读取: {doc}")
                except Exception as e:
                    logger.error(f"❌ 读取失败 {doc}: {e}")
                    missing_docs.append(doc)
            else:
                logger.warning(f"⚠️ 文档不存在: {doc}")
                missing_docs.append(doc)
        
        if missing_docs:
            logger.warning(f"缺少关键文档: {missing_docs}")
    
    def _analyze_architecture_mapping(self):
        """分析架构映射"""
        logger.info("🏗️ 分析架构映射...")
        
        arch_map = self.context['documents'].get('architecture_map.json', {})
        if not arch_map:
            logger.error("❌ 无法加载architecture_map.json")
            return
        
        modules = arch_map.get('modules', {})
        
        self.context['architecture'] = {
            'total_modules': len(modules),
            'core_services': [m for m in modules.keys() if 'core_services' in m],
            'frontend_modules': [m for m in modules.keys() if 'frontend' in m],
            'api_modules': [m for m in modules.keys() if 'api' in m],
            'workflow_modules': [m for m in modules.keys() if 'workflow' in m],
            'module_dependencies': self._extract_module_dependencies(modules)
        }
        
        logger.info(f"📊 发现 {len(modules)} 个模块")
        logger.info(f"🔧 核心服务: {len(self.context['architecture']['core_services'])} 个")
        logger.info(f"🎨 前端模块: {len(self.context['architecture']['frontend_modules'])} 个")
    
    def _analyze_interface_dependencies(self):
        """分析接口依赖"""
        logger.info("🔗 分析接口依赖...")
        
        interface_map = self.context['documents'].get('interface_map.json', {})
        if not interface_map:
            logger.error("❌ 无法加载interface_map.json")
            return
        
        available_classes = interface_map.get('available_classes', {})
        
        self.context['interfaces'] = {
            'total_classes': len(available_classes),
            'classes_by_module': self._group_classes_by_module(available_classes),
            'service_classes': self._find_service_classes(available_classes),
            'model_classes': self._find_model_classes(available_classes),
            'exception_classes': self._find_exception_classes(available_classes)
        }
        
        logger.info(f"📋 发现 {len(available_classes)} 个可用类")
    
    def _scan_related_implementations(self, task_description: str):
        """扫描相关实现"""
        logger.info("🔍 扫描相关实现...")
        
        # 基于任务描述查找相关关键词
        keywords = self._extract_keywords_from_task(task_description)
        
        related_modules = []
        related_classes = []
        
        # 在架构映射中搜索相关模块
        arch_map = self.context['documents'].get('architecture_map.json', {})
        modules = arch_map.get('modules', {})
        
        for module_name, module_info in modules.items():
            if any(keyword.lower() in module_name.lower() for keyword in keywords):
                related_modules.append({
                    'name': module_name,
                    'path': module_info.get('path'),
                    'classes': [cls['name'] for cls in module_info.get('classes', [])],
                    'functions': [func['name'] for func in module_info.get('functions', [])]
                })
        
        # 在接口映射中搜索相关类
        interface_map = self.context['documents'].get('interface_map.json', {})
        available_classes = interface_map.get('available_classes', {})
        
        for class_name, class_info in available_classes.items():
            if any(keyword.lower() in class_name.lower() for keyword in keywords):
                related_classes.append({
                    'name': class_name,
                    'module': class_info.get('module'),
                    'file': class_info.get('file')
                })
        
        self.context['related_implementations'] = {
            'keywords': keywords,
            'related_modules': related_modules,
            'related_classes': related_classes
        }
        
        logger.info(f"🎯 发现 {len(related_modules)} 个相关模块")
        logger.info(f"📦 发现 {len(related_classes)} 个相关类")
    
    def _generate_analysis_report(self, task_description: str):
        """生成分析报告"""
        logger.info("📊 生成分析报告...")
        
        self.analysis_report = {
            'task_description': task_description,
            'analysis_timestamp': str(Path().cwd()),
            'project_overview': self._extract_project_overview(),
            'architecture_summary': self._summarize_architecture(),
            'interface_summary': self._summarize_interfaces(),
            'related_implementations': self.context.get('related_implementations', {}),
            'recommendations': self._generate_recommendations(task_description),
            'risk_assessment': self._assess_risks(task_description),
            'required_dependencies': self._identify_required_dependencies(task_description)
        }
    
    def _extract_project_overview(self) -> Dict[str, Any]:
        """提取项目概述"""
        project_summary = self.context['documents'].get('PROJECT_SUMMARY.md', '')
        impl_summary = self.context['documents'].get('IMPLEMENTATION_SUMMARY.md', '')
        
        return {
            'project_type': self._extract_project_type(project_summary),
            'main_features': self._extract_main_features(project_summary),
            'implementation_status': self._extract_implementation_status(impl_summary),
            'key_technologies': self._extract_key_technologies(project_summary)
        }
    
    def _summarize_architecture(self) -> Dict[str, Any]:
        """总结架构信息"""
        arch = self.context.get('architecture', {})
        return {
            'total_modules': arch.get('total_modules', 0),
            'core_services_count': len(arch.get('core_services', [])),
            'frontend_modules_count': len(arch.get('frontend_modules', [])),
            'key_services': arch.get('core_services', [])[:10]  # 前10个核心服务
        }
    
    def _summarize_interfaces(self) -> Dict[str, Any]:
        """总结接口信息"""
        interfaces = self.context.get('interfaces', {})
        return {
            'total_classes': interfaces.get('total_classes', 0),
            'service_classes_count': len(interfaces.get('service_classes', [])),
            'model_classes_count': len(interfaces.get('model_classes', [])),
            'key_services': list(interfaces.get('service_classes', {}).keys())[:10]
        }
    
    def _generate_recommendations(self, task_description: str) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 基于相关实现生成建议
        related = self.context.get('related_implementations', {})
        if related.get('related_modules'):
            recommendations.append(
                f"发现 {len(related['related_modules'])} 个相关模块，建议先检查是否存在重复实现"
            )
        
        if related.get('related_classes'):
            recommendations.append(
                f"发现 {len(related['related_classes'])} 个相关类，建议复用现有接口"
            )
        
        # 基于架构模式生成建议
        arch = self.context.get('architecture', {})
        if arch.get('core_services'):
            recommendations.append("建议遵循现有的core_services架构模式")
        
        return recommendations
    
    def _assess_risks(self, task_description: str) -> List[str]:
        """评估风险"""
        risks = []
        
        # 检查是否可能重复开发
        related = self.context.get('related_implementations', {})
        if len(related.get('related_modules', [])) > 3:
            risks.append("⚠️ 高风险：发现多个相关模块，可能存在重复开发")
        
        # 检查依赖复杂性
        interfaces = self.context.get('interfaces', {})
        if interfaces.get('total_classes', 0) > 100:
            risks.append("⚠️ 中风险：系统复杂度较高，需要仔细管理依赖关系")
        
        return risks
    
    def _identify_required_dependencies(self, task_description: str) -> List[Dict[str, str]]:
        """识别必需依赖"""
        dependencies = []
        
        # 基于相关类识别依赖
        related = self.context.get('related_implementations', {})
        for cls in related.get('related_classes', []):
            dependencies.append({
                'type': 'class',
                'name': cls['name'],
                'module': cls['module'],
                'file': cls['file']
            })
        
        return dependencies
    
    # 辅助方法
    def _extract_module_dependencies(self, modules: Dict) -> Dict[str, List[str]]:
        """提取模块依赖关系"""
        dependencies = {}
        for module_name, module_info in modules.items():
            imports = module_info.get('imports', [])
            deps = []
            for imp in imports:
                if imp.get('type') == 'from_import':
                    deps.append(imp.get('module', ''))
                elif imp.get('type') == 'import':
                    deps.extend(imp.get('modules', []))
            dependencies[module_name] = deps
        return dependencies
    
    def _group_classes_by_module(self, classes: Dict) -> Dict[str, List[str]]:
        """按模块分组类"""
        grouped = {}
        for class_name, class_info in classes.items():
            module = class_info.get('module', 'unknown')
            if module not in grouped:
                grouped[module] = []
            grouped[module].append(class_name)
        return grouped
    
    def _find_service_classes(self, classes: Dict) -> Dict[str, Dict]:
        """查找服务类"""
        services = {}
        for class_name, class_info in classes.items():
            if 'service' in class_name.lower() or 'manager' in class_name.lower():
                services[class_name] = class_info
        return services
    
    def _find_model_classes(self, classes: Dict) -> Dict[str, Dict]:
        """查找模型类"""
        models = {}
        for class_name, class_info in classes.items():
            module = class_info.get('module', '')
            if 'models' in module or class_name.endswith('Request') or class_name.endswith('Response'):
                models[class_name] = class_info
        return models
    
    def _find_exception_classes(self, classes: Dict) -> Dict[str, Dict]:
        """查找异常类"""
        exceptions = {}
        for class_name, class_info in classes.items():
            if 'error' in class_name.lower() or 'exception' in class_name.lower():
                exceptions[class_name] = class_info
        return exceptions
    
    def _extract_keywords_from_task(self, task_description: str) -> List[str]:
        """从任务描述中提取关键词"""
        # 简单的关键词提取，可以根据需要改进
        keywords = []
        
        # 常见的技术关键词
        tech_keywords = [
            'frontend', 'backend', 'api', 'service', 'manager', 'interface',
            'chat', 'role', 'workflow', 'agent', 'memory', 'wiki', 'task',
            'llm', 'consensus', 'debate', 'synthesis', 'cognitive'
        ]
        
        task_lower = task_description.lower()
        for keyword in tech_keywords:
            if keyword in task_lower:
                keywords.append(keyword)
        
        # 从任务描述中提取名词
        words = task_description.split()
        for word in words:
            if len(word) > 3 and word.isalpha():
                keywords.append(word)
        
        return list(set(keywords))
    
    def _extract_project_type(self, summary: str) -> str:
        """提取项目类型"""
        if 'chat' in summary.lower() and 'role' in summary.lower():
            return "虚拟角色聊天系统"
        return "未知项目类型"
    
    def _extract_main_features(self, summary: str) -> List[str]:
        """提取主要功能"""
        features = []
        if '认知代理' in summary:
            features.append('认知代理系统')
        if '制度原语' in summary:
            features.append('制度原语框架')
        if '工作流' in summary:
            features.append('工作流引擎')
        return features
    
    def _extract_implementation_status(self, impl_summary: str) -> str:
        """提取实现状态"""
        if '✅' in impl_summary:
            return "部分完成"
        return "状态未知"
    
    def _extract_key_technologies(self, summary: str) -> List[str]:
        """提取关键技术"""
        technologies = []
        if 'LLM' in summary or 'llm' in summary:
            technologies.append('大语言模型')
        if 'FastAPI' in summary:
            technologies.append('FastAPI')
        if 'Python' in summary:
            technologies.append('Python')
        return technologies
    
    def print_analysis_report(self):
        """打印分析报告"""
        report = self.analysis_report
        
        print("=" * 80)
        print("📊 项目上下文分析报告")
        print("=" * 80)
        
        print(f"\n🎯 任务描述: {report['task_description']}")
        
        print(f"\n📋 项目概述:")
        overview = report['project_overview']
        print(f"  • 项目类型: {overview['project_type']}")
        print(f"  • 主要功能: {', '.join(overview['main_features'])}")
        print(f"  • 实现状态: {overview['implementation_status']}")
        print(f"  • 关键技术: {', '.join(overview['key_technologies'])}")
        
        print(f"\n🏗️ 架构总结:")
        arch = report['architecture_summary']
        print(f"  • 总模块数: {arch['total_modules']}")
        print(f"  • 核心服务: {arch['core_services_count']} 个")
        print(f"  • 前端模块: {arch['frontend_modules_count']} 个")
        
        print(f"\n🔗 接口总结:")
        interfaces = report['interface_summary']
        print(f"  • 总类数: {interfaces['total_classes']}")
        print(f"  • 服务类: {interfaces['service_classes_count']} 个")
        print(f"  • 模型类: {interfaces['model_classes_count']} 个")
        
        print(f"\n🎯 相关实现:")
        related = report['related_implementations']
        print(f"  • 相关模块: {len(related.get('related_modules', []))} 个")
        print(f"  • 相关类: {len(related.get('related_classes', []))} 个")
        
        if related.get('related_modules'):
            print("  • 相关模块列表:")
            for module in related['related_modules'][:5]:  # 显示前5个
                print(f"    - {module['name']}")
        
        print(f"\n💡 建议:")
        for rec in report['recommendations']:
            print(f"  • {rec}")
        
        print(f"\n⚠️ 风险评估:")
        for risk in report['risk_assessment']:
            print(f"  • {risk}")
        
        print(f"\n📦 必需依赖:")
        for dep in report['required_dependencies'][:10]:  # 显示前10个
            print(f"  • {dep['name']} ({dep['module']})")
        
        print("\n" + "=" * 80)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python project_context_analyzer.py '任务描述'")
        print("示例: python project_context_analyzer.py '集成现有前端组件'")
        sys.exit(1)
    
    task_description = sys.argv[1]
    
    analyzer = ProjectContextAnalyzer()
    analyzer.analyze_full_context(task_description)
    analyzer.print_analysis_report()
    
    # 保存分析报告
    report_file = f"context_analysis_report_{task_description.replace(' ', '_')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(analyzer.analysis_report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 分析报告已保存到: {report_file}")


if __name__ == '__main__':
    main()
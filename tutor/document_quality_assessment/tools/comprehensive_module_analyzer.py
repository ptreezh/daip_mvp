#!/usr/bin/env python3
"""
DAIP-LIVE 全面模块分析器
分析项目中的所有模块结构，包括P1-P8、newP系列、p0-p9等实际模块
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict, Counter
from dataclasses import dataclass


@dataclass
class ModuleInfo:
    """模块信息"""
    module_id: str
    module_name: str
    module_path: str
    module_type: str  # 'original', 'new', 'auxiliary', 'archived'
    documents: List[Dict]
    sub_modules: List[str]
    dependencies: List[str]
    description: str
    status: str  # 'active', 'planned', 'archived', 'replaced'


class ComprehensiveModuleAnalyzer:
    """全面模块分析器"""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.docs_path = self.base_path / "docs"

        # 定义完整的模块映射
        self.module_patterns = {
            # 核心P模块 (original)
            'p0': {'name': 'Core Interfaces', 'type': 'original'},
            'p1': {'name': 'Data Persistence', 'type': 'original'},
            'p2': {'name': 'Knowledge Manager', 'type': 'original'},
            'p3': {'name': 'Model Provider', 'type': 'original'},
            'p4': {'name': 'Role Manager Tools', 'type': 'original'},
            'p5': {'name': 'Agent Engine', 'type': 'original'},
            'p6': {'name': 'CLI TUI', 'type': 'original'},
            'p7': {'name': 'GUI', 'type': 'original'},
            'p8': {'name': 'Debate System', 'type': 'original'},
            'p9': {'name': 'Scaffolding', 'type': 'archived'},

            # P8子模块
            'p8_debate_system': {'name': 'Debate System Core', 'type': 'original'},
            'p8_human_assistant': {'name': 'Human Assistant', 'type': 'original'},
            'p8_wiki_system': {'name': 'Wiki System', 'type': 'original'},

            # newP系列 (重构/新版本)
            'newP5': {'name': 'Refactored Agent Engine', 'type': 'new'},
            'newP6': {'name': 'Refactored CLI TUI', 'type': 'new'},
            'newP7': {'name': 'Refactored GUI', 'type': 'new'},

            # 辅助模块
            'p_aux_config': {'name': 'Configuration Management', 'type': 'auxiliary'},
            'p_aux_memory': {'name': 'Memory Management', 'type': 'auxiliary'},

            # 其他主要模块
            'compliance': {'name': 'Compliance Checklists', 'type': 'support'},
            'procedure': {'name': 'Procedures & Guidelines', 'type': 'support'},
            'process': {'name': 'Process Management', 'type': 'support'},
            'architecture': {'name': 'Architecture Solutions', 'type': 'support'},
            'cli-enhancement': {'name': 'CLI Enhancement Projects', 'type': 'project'},
            'specifications': {'name': 'Specification Documents', 'type': 'support'},
            'specs': {'name': 'Specification Specs', 'type': 'support'},
        }

    def discover_all_modules(self) -> Dict[str, ModuleInfo]:
        """发现所有模块"""
        modules = {}

        # 遍历docs目录寻找所有可能的模块
        for item in self.docs_path.iterdir():
            if item.is_dir():
                module_id = self.identify_module_id(item.name, item)
                if module_id:
                    modules[module_id] = self.analyze_module(module_id, item)

        return modules

    def identify_module_id(self, dir_name: str, dir_path: Path) -> str:
        """识别模块ID"""
        dir_name_lower = dir_name.lower()

        # 直接匹配
        if dir_name_lower in self.module_patterns:
            return dir_name_lower

        # 模式匹配
        for pattern in self.module_patterns:
            if re.search(pattern, dir_name_lower, re.IGNORECASE):
                return pattern

        # 检查子目录
        for sub_item in dir_path.iterdir():
            if sub_item.is_dir():
                sub_id = self.identify_module_id(sub_item.name, sub_item)
                if sub_id:
                    return sub_id

        return None

    def analyze_module(self, module_id: str, module_path: Path) -> ModuleInfo:
        """分析单个模块"""
        pattern_info = self.module_patterns.get(module_id, {
            'name': module_id,
            'type': 'unknown'
        })

        # 收集文档
        documents = []
        for doc_file in module_path.rglob("*.md"):
            doc_info = {
                'file_name': doc_file.name,
                'relative_path': str(doc_file.relative_to(self.docs_path)),
                'file_size': doc_file.stat().st_size,
                'file_type': self.classify_document_type(doc_file.name)
            }
            documents.append(doc_info)

        # 查找子模块
        sub_modules = []
        for sub_dir in module_path.iterdir():
            if sub_dir.is_dir():
                sub_id = self.identify_module_id(sub_dir.name, sub_dir)
                if sub_id and sub_id != module_id:
                    sub_modules.append(sub_id)

        # 读取描述
        description = self.extract_module_description(module_path)

        # 确定状态
        status = self.determine_module_status(module_id, pattern_info['type'], module_path)

        return ModuleInfo(
            module_id=module_id,
            module_name=pattern_info['name'],
            module_path=str(module_path.relative_to(self.base_path)),
            module_type=pattern_info['type'],
            documents=documents,
            sub_modules=sub_modules,
            dependencies=self.extract_dependencies(module_path),
            description=description,
            status=status
        )

    def classify_document_type(self, file_name: str) -> str:
        """分类文档类型"""
        file_name_lower = file_name.lower()

        if 'spec' in file_name_lower:
            return 'specification'
        elif 'requirement' in file_name_lower:
            return 'requirement'
        elif 'design' in file_name_lower:
            return 'design'
        elif 'implementation' in file_name_lower:
            return 'implementation'
        elif 'plan' in file_name_lower:
            return 'plan'
        elif 'test' in file_name_lower:
            return 'test'
        elif 'checklist' in file_name_lower:
            return 'checklist'
        elif 'guide' in file_name_lower:
            return 'guide'
        elif 'manual' in file_name_lower:
            return 'manual'
        elif 'readme' in file_name_lower:
            return 'readme'
        elif 'todo' in file_name_lower or 'task' in file_name_lower:
            return 'task'
        elif 'report' in file_name_lower:
            return 'report'
        else:
            return 'general'

    def extract_module_description(self, module_path: Path) -> str:
        """提取模块描述"""
        # 尝试从README读取
        readme_file = module_path / "README.md"
        if readme_file.exists():
            try:
                with open(readme_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 提取第一段作为描述
                    lines = content.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            return line[:200]  # 限制长度
            except:
                pass

        # 尝试从其他主要文件读取
        for doc_file in module_path.glob("*.md"):
            if doc_file.name in ['SPEC.md', 'plan.md', 'README.md']:
                try:
                    with open(doc_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # 查找描述段落
                        desc_match = re.search(r'(?:概述|介绍|简介|overview)[:：]\s*(.+?)(?:\n\n|\n#|$)', content, re.IGNORECASE | re.DOTALL)
                        if desc_match:
                            return desc_match.group(1).strip()[:200]
                except:
                    continue

        return f"{module_path.name} 模块"

    def determine_module_status(self, module_id: str, module_type: str, module_path: Path) -> str:
        """确定模块状态"""
        # archived类型
        if module_type == 'archived':
            return 'archived'

        # newP系列
        if module_type == 'new':
            # 检查是否有对应的老模块
            old_module_id = module_id.replace('new', '').lower()
            if self.module_patterns.get(old_module_id, {}).get('type') == 'original':
                return 'replacing'
            return 'new'

        # 检查是否有新版本
        new_module_id = f"new{module_id.lower()}"
        if new_module_id in self.module_patterns:
            return 'replaced'

        # 检查是否有文档
        doc_count = len(list(module_path.rglob("*.md")))
        if doc_count == 0:
            return 'empty'

        # 检查是否有COMPLIANCE_CHECKLIST（完成状态）
        if (module_path / "COMPLIANCE_CHECKLIST.md").exists():
            return 'completed'

        return 'active'

    def extract_dependencies(self, module_path: Path) -> List[str]:
        """提取模块依赖"""
        dependencies = []

        for doc_file in module_path.rglob("*.md"):
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # 查找模块依赖引用
                    for module_id in self.module_patterns.keys():
                        if module_id in content:
                            dependencies.append(module_id)
            except:
                continue

        return list(set(dependencies))

    def analyze_module_relationships(self, modules: Dict[str, ModuleInfo]) -> Dict:
        """分析模块间关系"""
        relationships = {
            'module_hierarchy': {},
            'dependency_graph': {},
            'evolution_paths': {},
            'module_clusters': {}
        }

        # 构建层次结构
        core_modules = {k: v for k, v in modules.items() if v.module_type == 'original'}
        new_modules = {k: v for k, v in modules.items() if v.module_type == 'new'}
        aux_modules = {k: v for k, v in modules.items() if v.module_type == 'auxiliary'}

        relationships['module_hierarchy'] = {
            'core_p_modules': {k: {
                'name': v.module_name,
                'status': v.status,
                'doc_count': len(v.documents)
            } for k, v in core_modules.items() if re.match(r'^p[0-9]$', k)},
            'new_p_modules': {k: {
                'name': v.module_name,
                'replaces': k.replace('new', '').lower() if k.replace('new', '').lower() in core_modules else None,
                'status': v.status,
                'doc_count': len(v.documents)
            } for k, v in new_modules.items()},
            'auxiliary_modules': {k: {
                'name': v.module_name,
                'status': v.status,
                'doc_count': len(v.documents)
            } for k, v in aux_modules.items()},
            'support_modules': {k: {
                'name': v.module_name,
                'type': v.module_type,
                'doc_count': len(v.documents)
            } for k, v in modules.items() if v.module_type in ['support', 'project']}
        }

        # 构建依赖图
        for module_id, module_info in modules.items():
            relationships['dependency_graph'][module_id] = {
                'name': module_info.module_name,
                'dependencies': module_info.dependencies,
                'dependents': []
            }

        # 计算反向依赖
        for module_id, module_info in modules.items():
            for dep in module_info.dependencies:
                if dep in relationships['dependency_graph']:
                    relationships['dependency_graph'][dep]['dependents'].append(module_id)

        # 分析演化路径
        evolution_paths = {}
        for new_id, new_module in new_modules.items():
            old_id = new_id.replace('new', '').lower()
            if old_id in core_modules:
                evolution_paths[new_id] = {
                    'from': old_id,
                    'to': new_id,
                    'status': 'evolution',
                    'reason': self.analyze_evolution_reason(old_id, new_id, modules)
                }

        relationships['evolution_paths'] = evolution_paths

        return relationships

    def analyze_evolution_reason(self, old_id: str, new_id: str, modules: Dict[str, ModuleInfo]) -> str:
        """分析演化原因"""
        old_module = modules.get(old_id)
        new_module = modules.get(new_id)

        if not old_module or not new_module:
            return "信息不足"

        # 基于文档类型分析
        old_docs = set(doc['file_type'] for doc in old_module.documents)
        new_docs = set(doc['file_type'] for doc in new_module.documents)

        if 'checklist' in new_docs and 'checklist' not in old_docs:
            return "增加了合规检查"
        elif len(new_module.documents) > len(old_module.documents):
            return "文档扩展和完善"
        elif 'test' in new_docs and 'test' not in old_docs:
            return "增加了测试覆盖"
        else:
            return "重构和优化"

    def generate_teaching_structure(self, modules: Dict[str, ModuleInfo], relationships: Dict) -> Dict:
        """生成教学结构"""
        teaching_structure = {
            'learning_tracks': {},
            'module_labs': {},
            'practice_projects': {},
            'assessment_criteria': {}
        }

        # 定义学习路径
        teaching_structure['learning_tracks'] = {
            'foundational': {
                'title': '基础学习路径',
                'description': '学习DAIP-LIVE的基础架构和核心概念',
                'duration': '4-6周',
                'modules': ['p1', 'p6'],
                'prerequisites': [],
                'learning_outcomes': [
                    '掌握数据持久化基础',
                    '理解TUI界面开发',
                    '学会基础的模块化设计'
                ]
            },
            'core_development': {
                'title': '核心开发路径',
                'description': '深入学习AI系统开发和模块协作',
                'duration': '6-8周',
                'modules': ['p2', 'p3', 'p5'],
                'prerequisites': ['foundational'],
                'learning_outcomes': [
                    '掌握知识管理和向量搜索',
                    '理解多模型集成',
                    '学会智能执行引擎'
                ]
            },
            'advanced_features': {
                'title': '高级特性路径',
                'description': '掌握高级功能和系统优化',
                'duration': '4-6周',
                'modules': ['p4', 'p8', 'p7'],
                'prerequisites': ['core_development'],
                'learning_outcomes': [
                    '掌握角色管理和权限',
                    '理解多模型辩论系统',
                    '学会Web界面集成'
                ]
            },
            'refactoring_mastery': {
                'title': '重构精通路径',
                'description': '学习系统重构和架构优化',
                'duration': '3-4周',
                'modules': ['newP5', 'newP6', 'newP7'],
                'prerequisites': ['advanced_features'],
                'learning_outcomes': [
                    '理解重构原理和方法',
                    '掌握架构优化技巧',
                    '学会系统迁移和升级'
                ]
            }
        }

        # 为每个模块创建实验室
        for module_id, module_info in modules.items():
            if module_info.module_type in ['original', 'new'] and not module_info.status == 'archived':
                teaching_structure['module_labs'][module_id] = self.create_module_lab(module_info)

        # 生成实践项目
        teaching_structure['practice_projects'] = {
            'personal_assistant': {
                'title': '个人助理应用',
                'difficulty': 'intermediate',
                'duration': '3-4周',
                'modules': ['p1', 'p3', 'p5', 'p6'],
                'description': '开发一个功能完整的个人助理应用',
                'skills': ['数据持久化', 'AI集成', 'TUI开发']
            },
            'knowledge_system': {
                'title': '知识管理系统',
                'difficulty': 'advanced',
                'duration': '4-5周',
                'modules': ['p1', 'p2', 'p3', 'p7'],
                'description': '构建一个企业级的知识管理系统',
                'skills': ['向量搜索', 'Web界面', '多用户协作']
            },
            'debate_platform': {
                'title': '智能辩论平台',
                'difficulty': 'expert',
                'duration': '5-6周',
                'modules': ['p1', 'p3', 'p4', 'p5', 'p6', 'p8'],
                'description': '开发多模型协作的智能辩论系统',
                'skills': ['多模型协作', '角色管理', '系统集成']
            },
            'system_refactor': {
                'title': '系统重构项目',
                'difficulty': 'expert',
                'duration': '4-5周',
                'modules': ['newP5', 'newP6', 'newP7'],
                'description': '参与DAIP-LIVE系统的重构工作',
                'skills': ['系统重构', '架构优化', '迁移管理']
            }
        }

        # 评估标准
        teaching_structure['assessment_criteria'] = {
            'module_mastery': {
                'theory_understanding': 30,
                'practical_implementation': 40,
                'documentation_quality': 20,
                'integration_ability': 10
            },
            'project_delivery': {
                'requirement_analysis': 20,
                'design_quality': 25,
                'implementation': 30,
                'testing': 15,
                'documentation': 10
            }
        }

        return teaching_structure

    def create_module_lab(self, module_info: ModuleInfo) -> Dict:
        """为模块创建实验室"""
        # 按文档类型分组
        doc_groups = defaultdict(list)
        for doc in module_info.documents:
            doc_groups[doc['file_type']].append(doc)

        # 创建学习序列
        learning_sequence = [
            {
                'phase': 1,
                'title': '理论学习',
                'documents': doc_groups.get('specification', []) + doc_groups.get('requirement', []),
                'activities': ['阅读规格文档', '理解设计原理', '分析需求规格']
            },
            {
                'phase': 2,
                'title': '设计理解',
                'documents': doc_groups.get('design', []),
                'activities': ['分析架构设计', '理解接口定义', '学习最佳实践']
            },
            {
                'phase': 3,
                'title': '代码实践',
                'documents': doc_groups.get('implementation', []),
                'activities': ['阅读源代码', '运行示例', '修改功能', '扩展特性']
            },
            {
                'phase': 4,
                'title': '测试验证',
                'documents': doc_groups.get('test', []),
                'activities': ['运行测试', '编写测试用例', '性能测试', '质量检查']
            },
            {
                'phase': 5,
                'title': '综合实践',
                'documents': doc_groups.get('checklist', []) + doc_groups.get('guide', []),
                'activities': ['完成合规检查', '实施最佳实践', '编写学习总结']
            }
        ]

        return {
            'module_id': module_info.module_id,
            'module_name': module_info.module_name,
            'module_type': module_info.module_type,
            'status': module_info.status,
            'document_count': len(module_info.documents),
            'sub_modules': module_info.sub_modules,
            'learning_sequence': learning_sequence,
            'exercises': self.generate_module_exercises(module_info)
        }

    def generate_module_exercises(self, module_info: ModuleInfo) -> List[Dict]:
        """生成模块练习"""
        exercises = []

        # 基础练习
        exercises.append({
            'level': 'beginner',
            'title': f'{module_info.module_name}基础理解',
            'objectives': [
                f'理解{module_info.module_name}的核心概念',
                f'掌握{module_info.module_name}的基本使用',
                f'完成{module_info.module_name}的配置和运行'
            ],
            'tasks': [
                '阅读相关规格文档',
                '运行基础示例代码',
                '完成配置练习',
                '编写学习笔记'
            ],
            'estimated_time': '2-3小时'
        })

        # 进阶练习
        exercises.append({
            'level': 'intermediate',
            'title': f'{module_info.module_name}功能扩展',
            'objectives': [
                f'掌握{module_info.module_name}的扩展方法',
                f'理解{module_info.module_name}的接口设计',
                f'能够进行{module_info.module_name}的功能定制'
            ],
            'tasks': [
                '分析源代码实现',
                '实现功能扩展',
                '编写单元测试',
                '优化性能表现'
            ],
            'estimated_time': '4-6小时'
        })

        # 高级练习
        exercises.append({
            'level': 'advanced',
            'title': f'{module_info.module_name}高级应用',
            'objectives': [
                f'掌握{module_info.module_name}的高级特性',
                f'能够进行{module_info.module_name}的架构优化',
                f'具备{module_info.module_name}的问题排查能力'
            ],
            'tasks': [
                '设计新的功能模块',
                '性能优化和调优',
                '编写技术文档',
                '贡献开源项目'
            ],
            'estimated_time': '6-8小时'
        })

        return exercises

    def generate_analysis_report(self, modules: Dict[str, ModuleInfo], relationships: Dict, teaching_structure: Dict) -> str:
        """生成分析报告"""
        report = f"""# DAIP-LIVE 全面模块分析报告

## 📊 分析概览

本报告基于DAIP-LIVE项目的实际文档结构，分析了项目中的所有模块，包括P1-P8核心模块、newP系列重构模块、辅助模块等。

### 发现的模块统计
- **总模块数**: {len(modules)}
- **原始P模块**: {len([m for m in modules.values() if m.module_type == 'original' and re.match(r'^p[0-9]$', m.module_id)])}
- **newP系列模块**: {len([m for m in modules.values() if m.module_type == 'new'])}
- **辅助模块**: {len([m for m in modules.values() if m.module_type == 'auxiliary'])}
- **支持模块**: {len([m for m in modules.values() if m.module_type in ['support', 'project']])}
- **已归档模块**: {len([m for m in modules.values() if m.status == 'archived'])}

## 🏗️ 核心模块分析

### 原始P模块 (P1-P9)
"""

        # 添加原始P模块详情
        p_modules = {k: v for k, v in modules.items() if v.module_type == 'original' and re.match(r'^p[0-9]$', k)}
        for module_id in sorted(p_modules.keys()):
            module = p_modules[module_id]
            report += f"""
#### {module_id.upper()}: {module.module_name}
- **状态**: {module.status}
- **文档数量**: {len(module.documents)}
- **子模块**: {len(module.sub_modules)}
- **依赖关系**: {', '.join(module.dependencies) if module.dependencies else '无'}
- **描述**: {module.description}
"""

        # 添加newP系列分析
        report += f"""
### NewP系列模块 (重构版本)
"""
        new_p_modules = {k: v for k, v in modules.items() if v.module_type == 'new'}
        for module_id in sorted(new_p_modules.keys()):
            module = new_p_modules[module_id]
            old_id = module_id.replace('new', '').lower()
            report += f"""
#### {module_id}: {module.module_name}
- **状态**: {module.status}
- **文档数量**: {len(module.documents)}
- **替换模块**: {old_id if old_id in modules else '无'}
- **文档数量**: {len(module.documents)}
- **描述**: {module.description}
"""

        # 模块关系分析
        report += f"""
## 🔗 模块关系分析

### 演化路径
"""
        evolution_paths = relationships.get('evolution_paths', {})
        for new_id, path_info in evolution_paths.items():
            report += f"""
- **{new_id} → {path_info['from']}**: {path_info['reason']}
"""

        # 教学结构设计
        report += f"""
## 🎓 教学结构设计

### 学习路径
"""
        for track_id, track_info in teaching_structure['learning_tracks'].items():
            report += f"""
#### {track_info['title']}
- **时长**: {track_info['duration']}
- **涉及模块**: {', '.join(track_info['modules'])}
- **前置条件**: {', '.join(track_info['prerequisites']) if track_info['prerequisites'] else '无'}
- **学习成果**: {', '.join(track_info['learning_outcomes'])}
"""

        # 实践项目
        report += f"""
### 实践项目
"""
        for project_id, project_info in teaching_structure['practice_projects'].items():
            report += f"""
#### {project_info['title']}
- **难度**: {project_info['difficulty']}
- **时长**: {project_info['duration']}
- **涉及模块**: {', '.join(project_info['modules'])}
- **项目描述**: {project_info['description']}
- **核心技能**: {', '.join(project_info['skills'])}
"""

        # 总结和建议
        report += f"""
## 💡 总结与建议

### 关键发现
1. **模块化架构完善**: DAIP-LIVE拥有完整的模块化架构，从P0到P9覆盖系统各个方面
2. **持续重构进化**: newP系列显示了系统的持续改进和重构过程
3. **文档支撑充分**: 每个模块都有丰富的文档支撑，包括规格、设计、实现、测试等
4. **教学价值巨大**: 实际的项目结构为教学提供了完美的案例

### 教学建议
1. **循序渐进**: 按照P1→P6→P2→P3→P5→P4→P8→P7的顺序进行教学
2. **理论实践结合**: 以规格文档为理论指导，以源代码为实践载体
3. **重构教学**: 利用newP系列展示系统重构的方法和技巧
4. **项目驱动**: 通过跨模块项目巩固学习成果

### 实施策略
1. **模块化教学**: 每个模块作为独立的教学单元
2. **文档引导**: 强调文档质量的重要性
3. **实践导向**: 重视代码实现和测试验证
4. **质量意识**: 培养专业的开发习惯和标准

本分析为教学平台的设计提供了完整的数据支撑和实施指导。
"""

        return report


def main():
    """主函数"""
    import sys

    if len(sys.argv) < 3:
        print("用法: python comprehensive_module_analyzer.py <项目根目录> <输出目录>")
        return

    project_root = sys.argv[1]
    output_dir = sys.argv[2]

    # 确保输出目录存在
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    analyzer = ComprehensiveModuleAnalyzer(project_root)

    print("开始全面模块分析...")

    # 发现所有模块
    modules = analyzer.discover_all_modules()
    print(f"发现 {len(modules)} 个模块")

    # 分析模块关系
    relationships = analyzer.analyze_module_relationships(modules)

    # 生成教学结构
    teaching_structure = analyzer.generate_teaching_structure(modules, relationships)

    # 保存分析结果
    modules_file = Path(output_dir) / "comprehensive_modules_analysis.json"
    with open(modules_file, 'w', encoding='utf-8') as f:
        modules_data = {k: {
            'module_id': v.module_id,
            'module_name': v.module_name,
            'module_path': v.module_path,
            'module_type': v.module_type,
            'documents': v.documents,
            'sub_modules': v.sub_modules,
            'dependencies': v.dependencies,
            'description': v.description,
            'status': v.status
        } for k, v in modules.items()}
        json.dump(modules_data, f, ensure_ascii=False, indent=2, default=str)

    relationships_file = Path(output_dir) / "module_relationships.json"
    with open(relationships_file, 'w', encoding='utf-8') as f:
        json.dump(relationships, f, ensure_ascii=False, indent=2, default=str)

    teaching_file = Path(output_dir) / "teaching_structure.json"
    with open(teaching_file, 'w', encoding='utf-8') as f:
        json.dump(teaching_structure, f, ensure_ascii=False, indent=2, default=str)

    # 生成分析报告
    report = analyzer.generate_analysis_report(modules, relationships, teaching_structure)
    report_file = Path(output_dir) / "comprehensive_analysis_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"全面模块分析完成！")
    print(f"- 模块分析数据: {modules_file}")
    print(f"- 模块关系数据: {relationships_file}")
    print(f"- 教学结构数据: {teaching_file}")
    print(f"- 分析报告: {report_file}")


if __name__ == "__main__":
    main()
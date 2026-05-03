#!/usr/bin/env python3
"""
DAIP-LIVE 交互式模块实验室系统
基于真实的P1-P8模块、newP系列重构模块、compliance检查等实际项目结构
为学习者提供真实的SPEC驱动开发实践环境
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import yaml

# 模块实验室核心组件
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from document_quality_assessment.tools.comprehensive_module_analyzer import (
    ComprehensiveModuleAnalyzer,
    ModuleInfo
)

@dataclass
class LearningObjective:
    """学习目标定义"""
    id: str
    title: str
    description: str
    prerequisites: List[str]
    expected_outcomes: List[str]
    estimated_time: str  # 预计学习时间

@dataclass
class LabExercise:
    """实验练习定义"""
    id: str
    title: str
    difficulty: str  # beginner, intermediate, advanced
    description: str
    instructions: List[str]
    expected_results: List[str]
    hints: List[str]
    solution_code: Optional[str] = None
    validation_script: Optional[str] = None

@dataclass
class ModuleLab:
    """模块实验室定义"""
    module_id: str
    module_name: str
    module_type: str  # original, refactored, support
    learning_objectives: List[LearningObjective]
    lab_exercises: List[LabExercise]
    related_documents: List[str]
    source_code_files: List[str]
    test_files: List[str]
    compliance_items: List[str]

class InteractiveModuleLab:
    """交互式模块实验室主系统"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.tutor_dir = self.project_root / "tutor"
        self.labs_dir = self.tutor_dir / "module_labs"
        self.docs_dir = self.project_root / "docs"
        self.specs_dir = self.project_root / "specs"

        # 确保目录存在
        self.labs_dir.mkdir(parents=True, exist_ok=True)

        # 初始化模块分析器
        self.analyzer = ComprehensiveModuleAnalyzer(project_root)

        # 模块实验室配置
        self.lab_config = self._load_lab_config()

    def _load_lab_config(self) -> Dict:
        """加载实验室配置"""
        config_file = self.labs_dir / "lab_config.yaml"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return self._create_default_lab_config()

    def _create_default_lab_config(self) -> Dict:
        """创建默认实验室配置"""
        return {
            "lab_settings": {
                "auto_save_progress": True,
                "show_hints": True,
                "enable_solutions": True,
                "difficulty_progression": True
            },
            "ui_settings": {
                "theme": "light",
                "code_editor": "monokai",
                "font_size": 14,
                "show_line_numbers": True
            },
            "assessment_settings": {
                "passing_score": 70,
                "allow_retakes": True,
                "show_feedback": True
            }
        }

    async def generate_all_module_labs(self) -> Dict[str, ModuleLab]:
        """为所有模块生成实验室"""
        # 首先进行全面的模块分析
        analysis = self.analyzer.discover_all_modules()

        module_labs = {}

        # 为每个分析出的模块创建实验室
        for module_id, module_analysis in analysis.items():
            lab = await self._create_module_lab(module_id, module_analysis)
            if lab:
                module_labs[module_id] = lab

        # 保存实验室配置
        await self._save_module_labs(module_labs)

        return module_labs

    async def _create_module_lab(self, module_id: str, analysis: ModuleInfo) -> Optional[ModuleLab]:
        """为单个模块创建实验室"""
        try:
            # 根据模块类型创建学习目标
            learning_objectives = self._create_learning_objectives(module_id, analysis)

            # 创建实验练习
            lab_exercises = await self._create_lab_exercises(module_id, analysis)

            # 获取相关文档和代码文件
            related_documents = self._get_related_documents(module_id, analysis)
            source_code_files = self._get_source_code_files(module_id, analysis)
            test_files = self._get_test_files(module_id, analysis)
            compliance_items = self._get_compliance_items(module_id, analysis)

            return ModuleLab(
                module_id=module_id,
                module_name=analysis.module_name,
                module_type=analysis.module_type,
                learning_objectives=learning_objectives,
                lab_exercises=lab_exercises,
                related_documents=related_documents,
                source_code_files=source_code_files,
                test_files=test_files,
                compliance_items=compliance_items
            )

        except Exception as e:
            print(f"创建模块实验室失败 {module_id}: {e}")
            return None

    def _create_learning_objectives(self, module_id: str, analysis: ModuleInfo) -> List[LearningObjective]:
        """根据模块创建学习目标"""
        objectives = []

        # 基础学习目标
        base_objectives = {
            'p0': [
                LearningObjective(
                    id="p0-01",
                    title="理解核心接口设计原理",
                    description="掌握DAIP-LIVE系统核心接口的设计思想和实现方式",
                    prerequisites=["Python基础", "面向对象编程"],
                    expected_outcomes=["能够解释接口设计原则", "能够实现基础接口"],
                    estimated_time="2小时"
                ),
                LearningObjective(
                    id="p0-02",
                    title="接口契约与规范理解",
                    description="理解接口契约的重要性，学习如何编写清晰的接口规范",
                    prerequisites=["接口设计基础"],
                    expected_outcomes=["能够编写接口规范", "理解版本兼容性"],
                    estimated_time="3小时"
                )
            ],
            'p1': [
                LearningObjective(
                    id="p1-01",
                    title="SQLite数据库集成",
                    description="学习如何在Python应用中集成SQLite数据库",
                    prerequisites=["SQL基础", "Python编程"],
                    expected_outcomes=["能够设计数据库表结构", "能够实现CRUD操作"],
                    estimated_time="4小时"
                ),
                LearningObjective(
                    id="p1-02",
                    title="SQLAlchemy ORM应用",
                    description="掌握SQLAlchemy ORM的使用，理解数据持久化的最佳实践",
                    prerequisites=["数据库基础", "Python面向对象"],
                    expected_outcomes=["能够使用ORM进行数据操作", "理解数据库迁移"],
                    estimated_time="6小时"
                )
            ],
            'p2': [
                LearningObjective(
                    id="p2-01",
                    title="向量搜索基础",
                    description="理解向量搜索的原理，学习FAISS库的使用",
                    prerequisites=["线性代数基础", "Python编程"],
                    expected_outcomes=["能够实现向量相似度搜索", "理解embedding概念"],
                    estimated_time="5小时"
                ),
                LearningObjective(
                    id="p2-02",
                    title="Wiki系统设计",
                    description="学习如何设计企业级wiki系统，包括页面管理、标签系统等",
                    prerequisites=["Web开发基础", "数据库设计"],
                    expected_outcomes=["能够设计wiki系统架构", "实现页面CRUD功能"],
                    estimated_time="8小时"
                )
            ],
            'p3': [
                LearningObjective(
                    id="p3-01",
                    title="多模型集成架构",
                    description="学习如何设计支持多个AI模型提供商的统一接口",
                    prerequisites=["API设计", "异步编程"],
                    expected_outcomes=["能够设计模型抽象层", "实现模型切换机制"],
                    estimated_time="6小时"
                ),
                LearningObjective(
                    id="p3-02",
                    title="LiteLLM框架应用",
                    description="掌握LiteLLM框架的使用，实现统一的多模型调用",
                    prerequisites=["Python异步编程", "REST API"],
                    expected_outcomes=["能够集成多种LLM服务", "处理API限制和错误"],
                    estimated_time="4小时"
                )
            ],
            'p4': [
                LearningObjective(
                    id="p4-01",
                    title="角色管理系统设计",
                    description="学习如何设计灵活的AI角色管理系统",
                    prerequisites=["配置管理", "Python高级特性"],
                    expected_outcomes=["能够设计角色配置系统", "实现动态角色加载"],
                    estimated_time="5小时"
                ),
                LearningObjective(
                    id="p4-02",
                    title="工具扩展机制",
                    description="理解工具系统的设计模式，学习如何扩展AI能力",
                    prerequisites=["插件系统设计", "Python元编程"],
                    expected_outcomes=["能够设计工具接口", "实现工具注册机制"],
                    estimated_time="7小时"
                )
            ],
            'p5': [
                LearningObjective(
                    id="p5-01",
                    title="智能执行引擎设计",
                    description="学习AI驱动任务执行引擎的核心原理和实现",
                    prerequisites=["设计模式", "异步编程", "AI基础"],
                    expected_outcomes=["能够设计任务执行流程", "实现上下文管理"],
                    estimated_time="8小时"
                ),
                LearningObjective(
                    id="p5-02",
                    title="事件驱动架构",
                    description="掌握事件驱动架构的设计和实现，理解组件解耦的重要性",
                    prerequisites=["设计模式", "消息队列"],
                    expected_outcomes=["能够设计事件系统", "实现组件间通信"],
                    estimated_time="6小时"
                )
            ],
            'p6': [
                LearningObjective(
                    id="p6-01",
                    title="Textual TUI开发",
                    description="学习使用Textual框架创建现代化的终端用户界面",
                    prerequisites=["Python异步编程", "UI设计基础"],
                    expected_outcomes=["能够创建TUI应用", "处理用户交互事件"],
                    estimated_time="6小时"
                ),
                LearningObjective(
                    id="p6-02",
                    title="CLI命令设计",
                    description="学习如何设计用户友好的命令行界面",
                    prerequisites=["argparse库", "用户体验设计"],
                    expected_outcomes=["能够设计CLI接口", "实现命令补全和帮助"],
                    estimated_time="4小时"
                )
            ],
            'p7': [
                LearningObjective(
                    id="p7-01",
                    title="Streamlit GUI开发",
                    description="学习使用Streamlit快速创建Web应用界面",
                    prerequisites=["Web开发基础", "Python编程"],
                    expected_outcomes=["能够创建Streamlit应用", "实现交互式组件"],
                    estimated_time="5小时"
                ),
                LearningObjective(
                    id="p7-02",
                    title="Web API设计",
                    description="学习如何设计和实现RESTful API接口",
                    prerequisites=["HTTP协议", "JSON数据格式"],
                    expected_outcomes=["能够设计API接口", "实现认证和授权"],
                    estimated_time="6小时"
                )
            ],
            'p8': [
                LearningObjective(
                    id="p8-01",
                    title="多模型协作系统",
                    description="学习如何设计和实现多个AI模型的协作系统",
                    prerequisites=["分布式系统", "AI基础", "并发编程"],
                    expected_outcomes=["能够设计协作机制", "实现角色分配算法"],
                    estimated_time="10小时"
                ),
                LearningObjective(
                    id="p8-02",
                    title="辩论系统设计",
                    description="理解AI辩论系统的设计原理，实现智能对话管理",
                    prerequisites=["自然语言处理", "对话系统"],
                    expected_outcomes=["能够设计辩论流程", "实现观点生成机制"],
                    estimated_time="8小时"
                )
            ]
        }

        # newP系列模块的学习目标（重构专项）
        newp_objectives = {
            'newP5': [
                LearningObjective(
                    id="newp5-01",
                    title="Agent引擎重构实践",
                    description="学习如何将单体Agent引擎重构为事件驱动架构",
                    prerequisites=["原始P5模块", "重构模式", "事件驱动设计"],
                    expected_outcomes=["能够识别重构机会", "实现渐进式重构"],
                    estimated_time="12小时"
                ),
                LearningObjective(
                    id="newp5-02",
                    title="领域服务分离",
                    description="学习领域驱动设计中的服务分离原则",
                    prerequisites=["DDD基础", "面向对象设计"],
                    expected_outcomes=["能够划分领域边界", "实现服务层分离"],
                    estimated_time="8小时"
                )
            ],
            'newP6': [
                LearningObjective(
                    id="newp6-01",
                    title="TUI模块化重构",
                    description="学习如何将单体TUI重构为模块化架构",
                    prerequisites=["原始P6模块", "组件设计", "状态管理"],
                    expected_outcomes=["能够设计模块化TUI", "实现组件解耦"],
                    estimated_time="10小时"
                )
            ],
            'newP7': [
                LearningObjective(
                    id="newp7-01",
                    title="MVVM架构实践",
                    description="学习MVVM架构在GUI应用中的应用",
                    prerequisites=["GUI开发", "设计模式"],
                    expected_outcomes=["能够实现MVVM架构", "分离视图和逻辑"],
                    estimated_time="8小时"
                )
            ]
        }

        # 合并学习目标
        all_objectives = {**base_objectives, **newp_objectives}

        return all_objectives.get(module_id, [])

    async def _create_lab_exercises(self, module_id: str, analysis: ModuleInfo) -> List[LabExercise]:
        """为模块创建实验练习"""
        exercises = []

        # 根据模块类型和难度创建练习
        if module_id in ['p1', 'p2', 'p3']:
            exercises.extend([
                LabExercise(
                    id=f"{module_id}-basic",
                    title=f"{analysis.name}基础实现",
                    difficulty="beginner",
                    description=f"实现{analysis.name}模块的核心功能",
                    instructions=[
                        f"阅读{module_id}模块的规格文档",
                        "分析设计要求和接口定义",
                        "按照规格实现核心功能",
                        "编写单元测试验证功能"
                    ],
                    expected_results=[
                        "核心功能正常工作",
                        "通过所有单元测试",
                        "代码符合项目规范"
                    ],
                    hints=[
                        "从接口定义开始实现",
                        "参考项目中的现有代码",
                        "注意错误处理和边界条件"
                    ]
                )
            ])

        if module_id in ['p4', 'p5', 'p6']:
            exercises.extend([
                LabExercise(
                    id=f"{module_id}-intermediate",
                    title=f"{analysis.name}高级特性",
                    difficulty="intermediate",
                    description=f"实现{analysis.name}模块的高级功能和优化",
                    instructions=[
                        "分析现有实现的不足",
                        "设计改进方案",
                        "实现性能优化",
                        "添加扩展功能"
                    ],
                    expected_results=[
                        "性能显著提升",
                        "功能更加完善",
                        "代码质量提高"
                    ],
                    hints=[
                        "使用性能分析工具",
                        "考虑并发和异步处理",
                        "保持向后兼容性"
                    ]
                )
            ])

        if module_id in ['p7', 'p8'] or module_id.startswith('newP'):
            exercises.extend([
                LabExercise(
                    id=f"{module_id}-advanced",
                    title=f"{analysis.name}系统集成",
                    difficulty="advanced",
                    description=f"将{analysis.name}模块集成到完整系统中",
                    instructions=[
                        "分析模块间的依赖关系",
                        "实现集成接口",
                        "处理系统集成问题",
                        "编写集成测试"
                    ],
                    expected_results=[
                        "系统无缝集成",
                        "跨模块功能正常",
                        "整体性能稳定"
                    ],
                    hints=[
                        "使用依赖注入",
                        "实现松耦合设计",
                        "注意配置管理"
                    ]
                )
            ])

        return exercises

    def _get_related_documents(self, module_id: str, analysis: ModuleInfo) -> List[str]:
        """获取模块相关的规格文档"""
        related_docs = []

        # 查找规格文档
        specs_patterns = [
            f"**/p{module_id[1:]}*.md",
            f"**/{module_id}*.md",
            f"**/*{module_id}*.md"
        ]

        for pattern in specs_patterns:
            for doc_path in self.project_root.glob(pattern):
                if doc_path.is_file() and doc_path.suffix == '.md':
                    relative_path = str(doc_path.relative_to(self.project_root))
                    related_docs.append(relative_path)

        return related_docs

    def _get_source_code_files(self, module_id: str, analysis: ModuleInfo) -> List[str]:
        """获取模块的源代码文件"""
        source_files = []

        # 查找源代码目录
        src_dirs = [
            self.project_root / "src" / "daip_live",
            self.project_root / "src"
        ]

        # 根据模块类型查找源代码
        module_mappings = {
            'p0': ['core', 'interfaces'],
            'p1': ['persistence', 'database'],
            'p2': ['wiki', 'knowledge'],
            'p3': ['model_provider', 'models'],
            'p4': ['p4_role_manager_tools', 'role_manager', 'tools'],
            'p5': ['agent_engine'],
            'p6': ['cli', 'tui'],
            'p7': ['p7_gui', 'gui'],
            'p8': ['p8_debate_system', 'debate']
        }

        module_dirs = module_mappings.get(module_id, [module_id])

        for src_dir in src_dirs:
            if not src_dir.exists():
                continue

            for module_dir in module_dirs:
                module_path = src_dir / module_dir
                if module_path.exists():
                    for py_file in module_path.rglob("*.py"):
                        if py_file.is_file():
                            relative_path = str(py_file.relative_to(self.project_root))
                            source_files.append(relative_path)

        return source_files

    def _get_test_files(self, module_id: str, analysis: ModuleInfo) -> List[str]:
        """获取模块的测试文件"""
        test_files = []

        # 查找测试目录
        test_dir = self.project_root / "tests"
        if not test_dir.exists():
            return test_files

        # 模块到测试目录的映射
        test_mappings = {
            'p0': ['test_core', 'test_interfaces'],
            'p1': ['test_persistence', 'test_database'],
            'p2': ['test_wiki', 'test_knowledge'],
            'p3': ['test_model_provider', 'test_models'],
            'p4': ['test_role_manager', 'test_tools'],
            'p5': ['test_agent_engine'],
            'p6': ['test_cli', 'test_tui'],
            'p7': ['test_gui'],
            'p8': ['test_debate_system', 'test_debate']
        }

        test_dirs = test_mappings.get(module_id, [f"test_{module_id}"])

        for test_dir_name in test_dirs:
            test_path = test_dir / test_dir_name
            if test_path.exists():
                for test_file in test_path.rglob("*.py"):
                    if test_file.is_file():
                        relative_path = str(test_file.relative_to(self.project_root))
                        test_files.append(relative_path)

        return test_files

    def _get_compliance_items(self, module_id: str, analysis: ModuleInfo) -> List[str]:
        """获取模块的合规检查项"""
        compliance_items = []

        # 查找合规检查文档
        compliance_patterns = [
            f"**/compliance/**/*{module_id}*.md",
            f"**/compliance/**/*p{module_id[1:]}*.md",
            f"**/procedure/**/*{module_id}*.md"
        ]

        for pattern in compliance_patterns:
            for compliance_file in self.project_root.glob(pattern):
                if compliance_file.is_file() and compliance_file.suffix == '.md':
                    relative_path = str(compliance_file.relative_to(self.project_root))
                    compliance_items.append(relative_path)

        return compliance_items

    async def _save_module_labs(self, module_labs: Dict[str, ModuleLab]) -> None:
        """保存模块实验室配置"""
        # 保存为JSON格式
        labs_data = {}
        for module_id, lab in module_labs.items():
            labs_data[module_id] = {
                'module_id': lab.module_id,
                'module_name': lab.module_name,
                'module_type': lab.module_type,
                'learning_objectives': [asdict(obj) for obj in lab.learning_objectives],
                'lab_exercises': [asdict(ex) for ex in lab.lab_exercises],
                'related_documents': lab.related_documents,
                'source_code_files': lab.source_code_files,
                'test_files': lab.test_files,
                'compliance_items': lab.compliance_items
            }

        # 保存到文件
        labs_file = self.labs_dir / "module_labs.json"
        with open(labs_file, 'w', encoding='utf-8') as f:
            json.dump(labs_data, f, indent=2, ensure_ascii=False)

        # 保存配置文件
        config_file = self.labs_dir / "lab_config.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.lab_config, f, default_flow_style=False, allow_unicode=True)

        print(f"✅ 模块实验室配置已保存到: {labs_file}")
        print(f"✅ 实验室配置已保存到: {config_file}")

# 命令行接口
async def main():
    """主函数 - 生成所有模块实验室"""
    project_root = Path(__file__).parent.parent.parent

    print("🎓 DAIP-LIVE 交互式模块实验室生成器")
    print("=" * 50)
    print(f"项目根目录: {project_root}")

    # 创建模块实验室系统
    lab_system = InteractiveModuleLab(str(project_root))

    print("\n🔍 分析项目模块结构...")
    module_labs = await lab_system.generate_all_module_labs()

    print(f"\n📊 模块实验室生成完成:")
    print(f"   总模块数: {len(module_labs)}")

    for module_id, lab in module_labs.items():
        print(f"   📚 {lab.module_name} ({module_id})")
        print(f"      学习目标: {len(lab.learning_objectives)}个")
        print(f"      实验练习: {len(lab.lab_exercises)}个")
        print(f"      相关文档: {len(lab.related_documents)}份")
        print(f"      源码文件: {len(lab.source_code_files)}个")
        print(f"      测试文件: {len(lab.test_files)}个")
        print(f"      合规检查: {len(lab.compliance_items)}项")
        print()

    print("🎉 模块实验室系统初始化完成！")
    print("💡 学习者可以开始基于真实项目结构的模块化学习之旅")

if __name__ == "__main__":
    asyncio.run(main())
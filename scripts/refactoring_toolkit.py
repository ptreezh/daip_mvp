#!/usr/bin/env python3
"""
DAIP-LIVE P5-P7 模块重构工具包

提供自动化工具来执行Agent Engine解耦、TUI组件化和GUI实现。
"""

import argparse
import asyncio
import sys
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import subprocess
import shutil

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@dataclass
class RefactoringConfig:
    """重构配置"""
    target_module: str
    backup_enabled: bool = True
    test_enabled: bool = True
    dry_run: bool = False
    verbose: bool = False


class RefactoringToolkit:
    """重构工具包"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.src_dir = project_root / "src"
        self.backup_dir = project_root / "backups"
        self.reports_dir = project_root / "reports"

        # 创建目录
        self.backup_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)

    def create_backup(self, module_path: Path) -> str:
        """创建模块备份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{module_path.name}_backup_{timestamp}"
        backup_path = self.backup_dir / backup_name

        if module_path.exists():
            shutil.copytree(module_path, backup_path)
            print(f"✅ 备份已创建: {backup_path}")
            return str(backup_path)
        else:
            print(f"⚠️  模块不存在: {module_path}")
            return ""

    def analyze_complexity(self, module_path: Path) -> Dict[str, Any]:
        """分析模块复杂度"""
        print(f"🔍 分析模块复杂度: {module_path}")

        complexity_report = {
            "module": str(module_path),
            "files": [],
            "total_lines": 0,
            "total_classes": 0,
            "total_methods": 0,
            "max_file_lines": 0,
            "max_class_lines": 0,
            "max_method_lines": 0,
            "dependencies": set(),
            "issues": []
        }

        for py_file in module_path.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue

            file_analysis = self._analyze_file(py_file)
            complexity_report["files"].append(file_analysis)
            complexity_report["total_lines"] += file_analysis["lines"]
            complexity_report["total_classes"] += file_analysis["classes"]
            complexity_report["total_methods"] += file_analysis["methods"]
            complexity_report["max_file_lines"] = max(
                complexity_report["max_file_lines"], file_analysis["lines"]
            )
            complexity_report["dependencies"].update(file_analysis["dependencies"])

        # 分析复杂度指标
        complexity_report["complexity_score"] = self._calculate_complexity_score(complexity_report)
        complexity_report["dependencies"] = list(complexity_report["dependencies"])

        return complexity_report

    def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """分析单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ 无法读取文件 {file_path}: {e}")
            return {"file": str(file_path), "error": str(e)}

        lines = content.split('\n')
        file_analysis = {
            "file": str(file_path),
            "lines": len(lines),
            "classes": 0,
            "methods": 0,
            "max_method_lines": 0,
            "dependencies": set(),
            "issues": []
        }

        # 简单的复杂度分析
        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # 统计类
            if stripped.startswith("class "):
                file_analysis["classes"] += 1

            # 统计方法
            if stripped.startswith("def ") or stripped.startswith("async def "):
                file_analysis["methods"] += 1

            # 查找依赖
            if stripped.startswith("from ") and " import " in stripped:
                try:
                    parts = stripped.split(" from ")[1].split(" import ")
                    if len(parts) >= 2:
                        import_parts = parts[0]
                        if import_parts.startswith("daip_live."):
                            file_analysis["dependencies"].add(import_parts)
                except IndexError:
                    # 忽略解析错误
                    pass

            # 检查问题
            if len(stripped) > 100:
                file_analysis["issues"].append(f"行{i}: 代码行过长 ({len(stripped)} 字符)")

            if "TODO" in stripped.upper() or "FIXME" in stripped.upper():
                file_analysis["issues"].append(f"行{i}: 包含待办事项")

        return file_analysis

    def _calculate_complexity_score(self, analysis: Dict[str, Any]) -> int:
        """计算复杂度评分"""
        score = 0

        # 文件数量影响
        score += len(analysis["files"]) * 5

        # 代码行数影响
        score += analysis["total_lines"] // 100

        # 类和方法数量影响
        score += analysis["total_classes"] * 10
        score += analysis["total_methods"] * 3

        # 依赖数量影响
        score += len(analysis["dependencies"]) * 8

        # 问题数量影响
        total_issues = sum(len(f.get("issues", [])) for f in analysis["files"])
        score += total_issues * 5

        return score

    async def refactor_p5_agent_engine(self, config: RefactoringConfig) -> bool:
        """重构P5 Agent Engine"""
        print("🚀 开始重构P5 Agent Engine...")

        agent_engine_path = self.src_dir / "daip_live" / "agent_engine"

        # 备份
        if config.backup_enabled:
            backup_path = self.create_backup(agent_engine_path)

        # 分析复杂度
        complexity_report = self.analyze_complexity(agent_engine_path)
        print(f"📊 复杂度评分: {complexity_report['complexity_score']}")

        # 生成重构建议
        suggestions = self._generate_p5_suggestions(complexity_report)
        print("💡 重构建议:")
        for suggestion in suggestions:
            print(f"  • {suggestion}")

        # 保存报告
        report_file = self.reports_dir / "p5_agent_engine_analysis.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(complexity_report, f, indent=2, ensure_ascii=False, default=str)

        print(f"📋 分析报告已保存: {report_file}")

        return True

    async def refactor_p6_tui(self, config: RefactoringConfig) -> bool:
        """重构P6 TUI"""
        print("🚀 开始重构P6 TUI...")

        tui_files = [
            self.src_dir / "daip_live" / "tui.py",
            self.src_dir / "daip_live" / "tui_enhanced.py",
            self.src_dir / "daip_live" / "tui_logo.py",
        ]

        # 分析TUI文件
        tui_analysis = {
            "files": [],
            "total_lines": 0,
            "largest_file": "",
            "max_lines": 0,
            "issues": []
        }

        for tui_file in tui_files:
            if tui_file.exists():
                file_analysis = self._analyze_file(tui_file)
                tui_analysis["files"].append(file_analysis)
                tui_analysis["total_lines"] += file_analysis["lines"]

                if file_analysis["lines"] > tui_analysis["max_lines"]:
                    tui_analysis["max_lines"] = file_analysis["lines"]
                    tui_analysis["largest_file"] = str(tui_file.name)

        print(f"📊 TUI分析结果:")
        print(f"  • 总行数: {tui_analysis['total_lines']}")
        print(f"  • 最大文件: {tui_analysis['largest_file']} ({tui_analysis['max_lines']} 行)")

        # 生成组件化建议
        component_suggestions = self._generate_p6_suggestions(tui_analysis)
        print("💡 组件化建议:")
        for suggestion in component_suggestions:
            print(f"  • {suggestion}")

        # 保存报告
        report_file = self.reports_dir / "p6_tui_analysis.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(tui_analysis, f, indent=2, ensure_ascii=False, default=str)

        print(f"📋 分析报告已保存: {report_file}")

        return True

    async def implement_p7_gui(self, config: RefactoringConfig) -> bool:
        """实现P7 GUI"""
        print("🚀 开始实现P7 GUI...")

        gui_path = self.src_dir / "daip_live" / "p7_gui"

        # 检查现有GUI实现
        if gui_path.exists():
            existing_files = list(gui_path.rglob("*.py"))
            print(f"📁 现有GUI文件: {len(existing_files)}")

            for file_path in existing_files:
                file_analysis = self._analyze_file(file_path)
                print(f"  • {file_path.name}: {file_analysis['lines']} 行")
        else:
            print("📁 GUI模块不存在，需要创建")
            gui_path.mkdir(parents=True, exist_ok=True)

        # 生成GUI实现建议
        gui_suggestions = self._generate_p7_suggestions()
        print("💡 GUI实现建议:")
        for suggestion in gui_suggestions:
            print(f"  • {suggestion}")

        return True

    def _generate_p5_suggestions(self, analysis: Dict[str, Any]) -> List[str]:
        """生成P5重构建议"""
        suggestions = []

        if analysis["total_lines"] > 2000:
            suggestions.append("模块过大，建议拆分为多个子模块")

        if analysis["total_classes"] > 20:
            suggestions.append("类数量过多，建议按职责分组")

        if len(analysis["dependencies"]) > 10:
            suggestions.append("依赖过多，建议使用依赖注入解耦")

        max_file = max(analysis["files"], key=lambda x: x.get("lines", 0))
        if max_file.get("lines", 0) > 500:
            suggestions.append(f"文件 {max_file['file']} 过大，建议拆分")

        # 检查特定问题
        large_files = [f for f in analysis["files"] if f.get("lines", 0) > 300]
        if large_files:
            suggestions.append(f"发现 {len(large_files)} 个大文件，建议重构")

        return suggestions

    def _generate_p6_suggestions(self, analysis: Dict[str, Any]) -> List[str]:
        """生成P6组件化建议"""
        suggestions = []

        if analysis.get("total_lines", 0) > 1000:
            suggestions.append("TUI代码过多，强烈建议组件化重构")

        if analysis.get("max_lines", 0) > 500:
            suggestions.append(f"主文件 {analysis.get('largest_file', '未知')} 过大，应拆分为组件")

        suggestions.append("建议实现组件基类和接口")
        suggestions.append("建议建立状态管理系统")
        suggestions.append("建议实现事件驱动架构")
        suggestions.append("建议创建可复用的UI组件库")

        return suggestions

    def _generate_p7_suggestions(self) -> List[str]:
        """生成P7实现建议"""
        suggestions = [
            "建议采用MVVM架构模式",
            "建议使用CustomTkinter作为GUI框架",
            "建议实现与TUI共享的业务逻辑层",
            "建议建立响应式布局系统",
            "建议实现主题和样式管理",
            "建议添加键盘快捷键支持",
            "建议实现拖拽功能",
            "建议添加系统托盘集成",
            "建议实现多语言支持",
            "建议添加插件机制"
        ]

        return suggestions

    async def run_tests(self, module_name: str) -> bool:
        """运行模块测试"""
        print(f"🧪 运行 {module_name} 模块测试...")

        test_patterns = [
            f"tests/**/test_{module_name}*.py",
            f"tests/{module_name}/**/*.py"
        ]

        for pattern in test_patterns:
            try:
                result = subprocess.run([
                    sys.executable, "-m", "pytest",
                    pattern, "-v", "--tb=short"
                ], cwd=self.project_root, capture_output=True, text=True)

                if result.returncode == 0:
                    print(f"✅ {pattern} 测试通过")
                else:
                    print(f"❌ {pattern} 测试失败")
                    print(result.stderr)
            except Exception as e:
                print(f"❌ 运行测试时出错: {e}")

        return True

    def generate_summary_report(self) -> Dict[str, Any]:
        """生成综合报告"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "modules_analyzed": [],
            "recommendations": [],
            "next_steps": []
        }

        # 分析P5
        p5_path = self.src_dir / "daip_live" / "agent_engine"
        if p5_path.exists():
            p5_analysis = self.analyze_complexity(p5_path)
            summary["modules_analyzed"].append({
                "name": "P5 Agent Engine",
                "complexity": p5_analysis["complexity_score"],
                "status": "high_complexity",
                "recommendations": self._generate_p5_suggestions(p5_analysis)
            })

        # 分析P6
        summary["modules_analyzed"].append({
            "name": "P6 TUI",
            "status": "needs_modularization",
            "recommendations": self._generate_p6_suggestions({})
        })

        # 分析P7
        summary["modules_analyzed"].append({
            "name": "P7 GUI",
            "status": "needs_implementation",
            "recommendations": self._generate_p7_suggestions()
        })

        # 总体建议
        summary["recommendations"] = [
            "优先进行P5 Agent Engine的解耦重构",
            "采用事件驱动架构降低模块间耦合",
            "实施渐进式重构，避免大爆炸式改动",
            "建立完善的测试保障体系",
            "制定详细的分阶段实施计划"
        ]

        # 下一步行动
        summary["next_steps"] = [
            "1. 详细设计P5解耦架构",
            "2. 实现事件总线系统",
            "3. 拆分Agent Engine核心组件",
            "4. 设计P6组件化架构",
            "5. 实现TUI组件库",
            "6. 设计P7 MVVM架构",
            "7. 实现GUI核心功能",
            "8. 集成测试和优化"
        ]

        return summary


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="DAIP-LIVE P5-P7 重构工具包")
    parser.add_argument("command", choices=[
        "analyze", "refactor-p5", "refactor-p6", "implement-p7", "test", "report"
    ], help="执行的命令")
    parser.add_argument("--project-root", default=".", help="项目根目录")
    parser.add_argument("--no-backup", action="store_true", help="禁用备份")
    parser.add_argument("--no-test", action="store_true", help="跳过测试")
    parser.add_argument("--dry-run", action="store_true", help="试运行模式")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    toolkit = RefactoringToolkit(project_root)

    config = RefactoringConfig(
        target_module="",
        backup_enabled=not args.no_backup,
        test_enabled=not args.no_test,
        dry_run=args.dry_run,
        verbose=args.verbose
    )

    if args.command == "analyze":
        print("🔍 开始全面分析...")
        # 分析所有模块
        p5_path = project_root / "src" / "daip_live" / "agent_engine"
        if p5_path.exists():
            p5_analysis = toolkit.analyze_complexity(p5_path)
            print(f"P5 Agent Engine 复杂度评分: {p5_analysis['complexity_score']}")

        # 生成综合报告
        summary = toolkit.generate_summary_report()
        report_file = project_root / "reports" / "refactoring_summary.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False, default=str)

        print(f"📋 综合报告已生成: {report_file}")

    elif args.command == "refactor-p5":
        await toolkit.refactor_p5_agent_engine(config)
        if config.test_enabled:
            await toolkit.run_tests("agent_engine")

    elif args.command == "refactor-p6":
        await toolkit.refactor_p6_tui(config)
        if config.test_enabled:
            await toolkit.run_tests("tui")

    elif args.command == "implement-p7":
        await toolkit.implement_p7_gui(config)

    elif args.command == "test":
        await toolkit.run_tests("agent_engine")
        await toolkit.run_tests("tui")

    elif args.command == "report":
        summary = toolkit.generate_summary_report()
        print("📊 重构分析报告")
        print("=" * 50)
        for module in summary["modules_analyzed"]:
            print(f"\n🔹 {module['name']}")
            if "complexity" in module:
                print(f"   复杂度评分: {module['complexity']}")
            print(f"   状态: {module['status']}")
            print("   建议:")
            for rec in module["recommendations"]:
                print(f"     • {rec}")

        print(f"\n📋 总体建议:")
        for rec in summary["recommendations"]:
            print(f"  • {rec}")

        print(f"\n🚀 下一步行动:")
        for step in summary["next_steps"]:
            print(f"  {step}")


if __name__ == "__main__":
    from datetime import datetime
    asyncio.run(main())
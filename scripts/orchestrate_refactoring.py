#!/usr/bin/env python3
"""
DAIP-LIVE P5-P7 重构编排脚本

自动化执行备份、隔离、重构和测试的完整流程。
"""

import asyncio
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

# 添加脚本路径
sys.path.insert(0, str(Path(__file__).parent))

from isolation_backup_manager import IsolationBackupManager, IsolationConfig
from refactoring_toolkit import RefactoringToolkit, RefactoringConfig

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/orchestration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class RefactoringPhase:
    """重构阶段定义"""
    name: str
    module_paths: List[str]
    config_file: str
    test_patterns: List[str]
    dependencies: List[str] = None


class RefactoringOrchestrator:
    """重构编排器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.backup_manager = IsolationBackupManager(project_root)
        self.refactoring_toolkit = RefactoringToolkit(project_root)

        # 确保必要目录存在
        (project_root / "logs").mkdir(exist_ok=True)

        # 定义重构阶段
        self.phases = {
            "p5": RefactoringPhase(
                name="P5 Agent Engine 解耦重构",
                module_paths=["src/daip_live/agent_engine"],
                config_file="configs/p5_agent_engine_isolation.json",
                test_patterns=["tests/agent_engine/**/*.py", "tests/**/test_agent_engine*.py"],
                dependencies=["core", "memory", "persistence"]
            ),
            "p6": RefactoringPhase(
                name="P6 TUI 组件化重构",
                module_paths=["src/daip_live/tui.py", "src/daip_live/tui_enhanced.py", "src/daip_live/tui_logo.py"],
                config_file="configs/p6_tui_isolation.json",
                test_patterns=["tests/tui/**/*.py", "tests/**/test_tui*.py"],
                dependencies=["agent_engine", "core"]
            ),
            "p7": RefactoringPhase(
                name="P7 GUI 完整实现",
                module_paths=["src/daip_live/p7_gui"],
                config_file="configs/p7_gui_isolation.json",
                test_patterns=["tests/gui/**/*.py", "tests/**/test_gui*.py"],
                dependencies=["agent_engine", "core", "shared"]
            )
        }

    async def execute_phase(self, phase_name: str, config: RefactoringConfig) -> bool:
        """执行单个重构阶段"""
        if phase_name not in self.phases:
            logger.error(f"未知阶段: {phase_name}")
            return False

        phase = self.phases[phase_name]
        logger.info(f"🚀 开始执行阶段: {phase.name}")

        try:
            # 步骤1: 创建备份
            logger.info("📦 创建备份...")
            backup_id = self.backup_manager.create_backup(
                phase.module_paths,
                phase_name
            )

            if not backup_id:
                logger.error("❌ 备份创建失败")
                return False

            # 步骤2: 验证备份完整性
            logger.info("🔍 验证备份完整性...")
            if not self.backup_manager.verify_backup_integrity(backup_id):
                logger.error("❌ 备份完整性验证失败")
                return False

            # 步骤3: 创建隔离版本
            logger.info("🏝️ 创建隔离版本...")
            with open(self.project_root / phase.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            isolation_config = IsolationConfig(**config_data)
            isolated_id = self.backup_manager.create_isolated_version(backup_id, isolation_config)

            if not isolated_id:
                logger.error("❌ 隔离版本创建失败")
                return False

            # 步骤4: 运行重构工具
            logger.info("🔧 执行重构分析...")
            if phase_name == "p5":
                success = await self.refactoring_toolkit.refactor_p5_agent_engine(config)
            elif phase_name == "p6":
                success = await self.refactoring_toolkit.refactor_p6_tui(config)
            elif phase_name == "p7":
                success = await self.refactoring_toolkit.implement_p7_gui(config)
            else:
                success = False

            if not success:
                logger.error("❌ 重构执行失败")
                return False

            # 步骤5: 运行测试（如果启用）
            if config.test_enabled:
                logger.info("🧪 运行测试...")
                for pattern in phase.test_patterns:
                    test_success = await self.refactoring_toolkit.run_tests(pattern.split('/')[-1].replace('.py', ''))
                    if not test_success:
                        logger.warning(f"⚠️ 测试失败: {pattern}")

            # 步骤6: 生成阶段报告
            logger.info("📊 生成阶段报告...")
            await self._generate_phase_report(phase_name, backup_id, isolated_id, phase)

            logger.info(f"✅ 阶段 {phase_name} 执行完成")
            return True

        except Exception as e:
            logger.error(f"❌ 阶段 {phase_name} 执行失败: {e}")
            return False

    async def execute_all_phases(self, config: RefactoringConfig) -> bool:
        """执行所有重构阶段"""
        logger.info("🎯 开始执行完整重构流程...")

        results = {}

        for phase_name in ["p5", "p6", "p7"]:
            logger.info(f"\n{'='*60}")
            logger.info(f"执行阶段: {phase_name.upper()}")
            logger.info(f"{'='*60}")

            success = await self.execute_phase(phase_name, config)
            results[phase_name] = success

            if not success:
                logger.error(f"❌ 阶段 {phase_name} 失败，停止执行")
                break

            # 阶段间暂停，让用户确认
            if not config.dry_run:
                logger.info(f"⏸️ 阶段 {phase_name} 完成，可以继续下一个阶段...")
                await asyncio.sleep(2)

        # 生成最终报告
        await self._generate_final_report(results)

        return all(results.values())

    async def rollback_phase(self, phase_name: str) -> bool:
        """回滚单个阶段"""
        if phase_name not in self.phases:
            logger.error(f"未知阶段: {phase_name}")
            return False

        logger.info(f"🔄 开始回滚阶段: {phase_name}")

        # 查找最新的备份
        backups = self.backup_manager.list_backups()
        phase_backups = [b for b in backups if b.module_name == phase_name]

        if not phase_backups:
            logger.error(f"找不到阶段 {phase_name} 的备份")
            return False

        latest_backup = phase_backups[0]

        # 恢复备份
        success = self.backup_manager.restore_backup(latest_backup.backup_id)

        if success:
            logger.info(f"✅ 阶段 {phase_name} 回滚完成")
        else:
            logger.error(f"❌ 阶段 {phase_name} 回滚失败")

        return success

    async def rollback_all_phases(self) -> bool:
        """回滚所有阶段"""
        logger.info("🔄 开始回滚所有阶段...")

        results = {}

        for phase_name in ["p7", "p6", "p5"]:  # 逆序回滚
            success = await self.rollback_phase(phase_name)
            results[phase_name] = success

        return all(results.values())

    async def _generate_phase_report(self, phase_name: str, backup_id: str, isolated_id: str, phase: RefactoringPhase):
        """生成阶段报告"""
        report = {
            "phase": phase_name,
            "phase_name": phase.name,
            "timestamp": datetime.now().isoformat(),
            "backup_id": backup_id,
            "isolated_id": isolated_id,
            "module_paths": phase.module_paths,
            "config_file": phase.config_file,
            "test_patterns": phase.test_patterns,
            "dependencies": phase.dependencies or []
        }

        report_file = self.project_root / "reports" / f"{phase_name}_phase_report.json"
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"📋 阶段报告已生成: {report_file}")

    async def _generate_final_report(self, results: Dict[str, bool]):
        """生成最终报告"""
        report = {
            "orchestration": "P5-P7 Refactoring",
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "results": results,
            "success": all(results.values()),
            "summary": {
                "total_phases": len(results),
                "successful_phases": sum(results.values()),
                "failed_phases": len(results) - sum(results.values())
            }
        }

        report_file = self.project_root / "reports" / "orchestration_final_report.json"

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"📋 最终报告已生成: {report_file}")

    def get_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        backups = self.backup_manager.list_backups()

        status = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "total_backups": len(backups),
            "backups_by_module": {},
            "phases": {}
        }

        # 按模块分组备份
        for backup in backups:
            if backup.module_name not in status["backups_by_module"]:
                status["backups_by_module"][backup.module_name] = []
            status["backups_by_module"][backup.module_name].append({
                "backup_id": backup.backup_id,
                "timestamp": backup.timestamp,
                "file_count": backup.file_count,
                "size_mb": backup.total_size / 1024 / 1024,
                "integrity_ok": self.backup_manager.verify_backup_integrity(backup.backup_id)
            })

        # 检查各阶段状态
        for phase_name, phase in self.phases.items():
            phase_backups = status["backups_by_module"].get(phase_name, [])
            status["phases"][phase_name] = {
                "name": phase.name,
                "has_backup": len(phase_backups) > 0,
                "latest_backup": phase_backups[0] if phase_backups else None,
                "module_exists": any((self.project_root / path).exists() for path in phase.module_paths),
                "config_exists": (self.project_root / phase.config_file).exists()
            }

        return status


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="DAIP-LIVE P5-P7 重构编排器")
    parser.add_argument("command", choices=[
        "execute", "execute-all", "rollback", "rollback-all", "status", "report"
    ], help="执行的命令")
    parser.add_argument("--phase", choices=["p5", "p6", "p7"], help="指定阶段")
    parser.add_argument("--project-root", default=".", help="项目根目录")
    parser.add_argument("--no-backup", action="store_true", help="禁用备份")
    parser.add_argument("--no-test", action="store_true", help="跳过测试")
    parser.add_argument("--dry-run", action="store_true", help="试运行模式")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    orchestrator = RefactoringOrchestrator(project_root)

    config = RefactoringConfig(
        target_module="",
        backup_enabled=not args.no_backup,
        test_enabled=not args.no_test,
        dry_run=args.dry_run,
        verbose=args.verbose
    )

    if args.command == "execute":
        if not args.phase:
            print("❌ execute 命令需要 --phase 参数")
            sys.exit(1)

        success = await orchestrator.execute_phase(args.phase, config)
        sys.exit(0 if success else 1)

    elif args.command == "execute-all":
        success = await orchestrator.execute_all_phases(config)
        sys.exit(0 if success else 1)

    elif args.command == "rollback":
        if not args.phase:
            print("❌ rollback 命令需要 --phase 参数")
            sys.exit(1)

        success = await orchestrator.rollback_phase(args.phase)
        sys.exit(0 if success else 1)

    elif args.command == "rollback-all":
        success = await orchestrator.rollback_all_phases()
        sys.exit(0 if success else 1)

    elif args.command == "status":
        status = orchestrator.get_status()
        print("📊 DAIP-LIVE P5-P7 重构状态")
        print("=" * 50)
        print(f"项目根目录: {status['project_root']}")
        print(f"总备份数: {status['total_backups']}")
        print()

        for phase_name, phase_status in status["phases"].items():
            print(f"🔹 {phase_name.upper()}: {phase_status['name']}")
            print(f"   备份状态: {'✅ 有备份' if phase_status['has_backup'] else '❌ 无备份'}")
            print(f"   模块存在: {'✅ 是' if phase_status['module_exists'] else '❌ 否'}")
            print(f"   配置存在: {'✅ 是' if phase_status['config_exists'] else '❌ 否'}")

            if phase_status['latest_backup']:
                backup = phase_status['latest_backup']
                print(f"   最新备份: {backup['backup_id']}")
                print(f"   备份时间: {backup['timestamp']}")
                print(f"   备份大小: {backup['size_mb']:.2f} MB")
                print(f"   完整性: {'✅ 完整' if backup['integrity_ok'] else '❌ 损坏'}")
            print()

    elif args.command == "report":
        status = orchestrator.get_status()
        report_file = project_root / "reports" / "status_report.json"
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(status, f, indent=2, ensure_ascii=False)

        print(f"📋 状态报告已生成: {report_file}")


if __name__ == "__main__":
    asyncio.run(main())
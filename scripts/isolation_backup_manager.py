#!/usr/bin/env python3
"""
DAIP-LIVE P5-P7 模块重构隔离备份系统

实现安全的零影响重构策略，支持新旧版本并行运行和快速回滚。
"""

import os
import sys
import json
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import hashlib
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/isolation_backup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class BackupMetadata:
    """备份元数据"""
    backup_id: str
    timestamp: str
    module_name: str
    original_path: str
    backup_path: str
    file_count: int
    total_size: int
    checksum: str
    dependencies: List[str]
    config_files: List[str]
    data_files: List[str]


@dataclass
class IsolationConfig:
    """隔离配置"""
    module_name: str
    original_paths: List[str]
    isolated_paths: List[str]
    config_overrides: Dict[str, Any]
    port_overrides: Dict[str, int]
    data_overrides: Dict[str, str]


class IsolationBackupManager:
    """隔离备份管理器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.backup_dir = project_root / "backups"
        self.isolation_dir = project_root / "isolated_versions"
        self.config_dir = project_root / "configs"
        self.metadata_file = self.backup_dir / "backup_metadata.json"

        # 创建目录
        self.backup_dir.mkdir(exist_ok=True)
        self.isolation_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)
        (self.project_root / "logs").mkdir(exist_ok=True)

        self.load_metadata()

    def load_metadata(self):
        """加载备份元数据"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.backups = {bid: BackupMetadata(**meta) for bid, meta in data.items()}
            except Exception as e:
                logger.error(f"加载备份元数据失败: {e}")
                self.backups = {}
        else:
            self.backups = {}

    def save_metadata(self):
        """保存备份元数据"""
        try:
            data = {bid: asdict(meta) for bid, meta in self.backups.items()}
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存备份元数据失败: {e}")

    def calculate_checksum(self, path: Path) -> str:
        """计算目录校验和"""
        hash_md5 = hashlib.md5()
        for file_path in sorted(path.rglob('*')):
            if file_path.is_file():
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def get_directory_size(self, path: Path) -> Tuple[int, int]:
        """获取目录大小和文件数量"""
        total_size = 0
        file_count = 0
        for file_path in path.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
                file_count += 1
        return total_size, file_count

    def create_backup(self, module_paths: List[str], module_name: str) -> str:
        """创建模块备份"""
        logger.info(f"开始备份模块: {module_name}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_id = f"{module_name}_backup_{timestamp}"
        backup_path = self.backup_dir / backup_id

        try:
            backup_path.mkdir(exist_ok=True)

            total_size = 0
            total_files = 0
            backed_up_paths = []

            for module_path in module_paths:
                src_path = self.project_root / module_path
                if not src_path.exists():
                    logger.warning(f"路径不存在: {src_path}")
                    continue

                dest_path = backup_path / src_path.relative_to(self.project_root)
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                if src_path.is_file():
                    shutil.copy2(src_path, dest_path)
                    total_files += 1
                    total_size += src_path.stat().st_size
                else:
                    shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
                    size, files = self.get_directory_size(dest_path)
                    total_size += size
                    total_files += files

                backed_up_paths.append(module_path)
                logger.info(f"已备份: {module_path}")

            # 计算校验和
            checksum = self.calculate_checksum(backup_path)

            # 查找依赖和配置文件
            dependencies = self._find_dependencies(module_paths)
            config_files = self._find_config_files(module_paths)
            data_files = self._find_data_files(module_paths)

            # 创建元数据
            metadata = BackupMetadata(
                backup_id=backup_id,
                timestamp=timestamp,
                module_name=module_name,
                original_path=json.dumps(module_paths),
                backup_path=str(backup_path),
                file_count=total_files,
                total_size=total_size,
                checksum=checksum,
                dependencies=dependencies,
                config_files=config_files,
                data_files=data_files
            )

            self.backups[backup_id] = metadata
            self.save_metadata()

            logger.info(f"备份完成: {backup_id}")
            logger.info(f"备份路径: {backup_path}")
            logger.info(f"文件数量: {total_files}, 总大小: {total_size / 1024 / 1024:.2f} MB")

            return backup_id

        except Exception as e:
            logger.error(f"备份失败: {e}")
            # 清理失败的备份
            if backup_path.exists():
                shutil.rmtree(backup_path)
            raise

    def _find_dependencies(self, module_paths: List[str]) -> List[str]:
        """查找模块依赖"""
        dependencies = set()
        for module_path in module_paths:
            src_path = self.project_root / module_path
            if src_path.is_file() and src_path.suffix == '.py':
                try:
                    with open(src_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # 简单的依赖分析
                        for line in content.split('\n'):
                            if line.strip().startswith('from daip_live.'):
                                parts = line.strip().split(' ')
                                if len(parts) >= 4:
                                    dep = parts[1]
                                    dependencies.add(dep)
                except Exception as e:
                    logger.warning(f"分析依赖失败 {src_path}: {e}")
        return list(dependencies)

    def _find_config_files(self, module_paths: List[str]) -> List[str]:
        """查找相关配置文件"""
        config_files = []
        config_patterns = ['*.yaml', '*.yml', '*.json', '*.toml', '*.ini']

        for pattern in config_patterns:
            for config_file in self.project_root.rglob(pattern):
                # 检查是否与模块相关
                rel_path = str(config_file.relative_to(self.project_root))
                if any(module in rel_path for module in ['config', 'setting', module_paths[0].split('/')[0]]):
                    config_files.append(rel_path)

        return config_files

    def _find_data_files(self, module_paths: List[str]) -> List[str]:
        """查找相关数据文件"""
        data_files = []
        data_patterns = ['data/', 'database/', 'db/', 'storage/']

        for pattern in data_patterns:
            data_path = self.project_root / pattern
            if data_path.exists():
                data_files.extend([str(p.relative_to(self.project_root)) for p in data_path.rglob('*') if p.is_file()])

        return data_files

    def create_isolated_version(self, backup_id: str, isolation_config: IsolationConfig) -> str:
        """创建隔离版本"""
        if backup_id not in self.backups:
            raise ValueError(f"备份不存在: {backup_id}")

        logger.info(f"创建隔离版本: {isolation_config.module_name}")

        backup_metadata = self.backups[backup_id]
        backup_path = Path(backup_metadata.backup_path)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        isolated_id = f"{isolation_config.module_name}_isolated_{timestamp}"
        isolated_path = self.isolation_dir / isolated_id

        try:
            # 复制备份到隔离目录
            shutil.copytree(backup_path, isolated_path)

            # 创建隔离配置
            isolated_config = {
                "isolation_id": isolated_id,
                "module_name": isolation_config.module_name,
                "original_backup": backup_id,
                "timestamp": timestamp,
                "path_mappings": dict(zip(isolation_config.original_paths, isolation_config.isolated_paths)),
                "config_overrides": isolation_config.config_overrides,
                "port_overrides": isolation_config.port_overrides,
                "data_overrides": isolation_config.data_overrides
            }

            config_file = isolated_path / "isolation_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(isolated_config, f, indent=2, ensure_ascii=False)

            # 应用配置覆盖
            self._apply_config_overrides(isolated_path, isolation_config)

            # 创建启动脚本
            self._create_startup_script(isolated_path, isolation_config)

            logger.info(f"隔离版本创建完成: {isolated_id}")
            logger.info(f"隔离路径: {isolated_path}")

            return isolated_id

        except Exception as e:
            logger.error(f"创建隔离版本失败: {e}")
            if isolated_path.exists():
                shutil.rmtree(isolated_path)
            raise

    def _apply_config_overrides(self, isolated_path: Path, config: IsolationConfig):
        """应用配置覆盖"""
        for config_file, overrides in config.config_overrides.items():
            config_path = isolated_path / config_file
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        data = json.load(f) if config_path.suffix == '.json' else {}

                    data.update(overrides)

                    with open(config_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)

                    logger.info(f"应用配置覆盖: {config_file}")
                except Exception as e:
                    logger.warning(f"应用配置覆盖失败 {config_file}: {e}")

    def _create_startup_script(self, isolated_path: Path, config: IsolationConfig):
        """创建启动脚本"""
        script_content = f'''#!/usr/bin/env python3
"""
DAIP-LIVE {config.module_name} 隔离版本启动脚本
"""

import sys
import os
from pathlib import Path

# 设置隔离路径
isolated_root = Path(__file__).parent
sys.path.insert(0, str(isolated_root / "src"))

# 设置环境变量
os.environ["DAIP_ISOLATED_MODE"] = "1"
os.environ["DAIP_ISOLATION_ID"] = isolated_root.name

# 应用端口覆盖
port_overrides = {config.port_overrides}
for service, port in port_overrides.items():
    os.environ[f"DAIP_PORT_{{service.upper()}}"] = str(port)

# 应用数据覆盖
data_overrides = {config.data_overrides}
for service, data_path in data_overrides.items():
    os.environ[f"DAIP_DATA_{{service.upper()}}"] = str(isolated_root / data_path)

print("🚀 启动DAIP-LIVE {config.module_name} 隔离版本...")
print(f"📁 隔离路径: {{isolated_root}}")
print(f"🔧 配置覆盖: {{len(config.config_overrides)}} 项")
print(f"🌐 端口覆盖: {{len(config.port_overrides)}} 项")
print(f"💾 数据覆盖: {{len(config.data_overrides)}} 项")

# 启动主程序
if __name__ == "__main__":
    try:
        # 这里应该根据具体模块调整启动逻辑
        from daip_live.main import main
        main()
    except ImportError as e:
        print(f"❌ 启动失败: {{e}}")
        print("请检查模块路径和依赖关系")
        sys.exit(1)
'''

        script_path = isolated_path / "start_isolated.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)

        # 设置执行权限 (Unix系统)
        if os.name != 'nt':
            os.chmod(script_path, 0o755)

        logger.info(f"创建启动脚本: {script_path}")

    def restore_backup(self, backup_id: str) -> bool:
        """恢复备份"""
        if backup_id not in self.backups:
            logger.error(f"备份不存在: {backup_id}")
            return False

        logger.info(f"开始恢复备份: {backup_id}")

        backup_metadata = self.backups[backup_id]
        backup_path = Path(backup_metadata.backup_path)

        try:
            original_paths = json.loads(backup_metadata.original_path)

            for original_path in original_paths:
                src_path = backup_path / Path(original_path).relative_to(self.project_root)
                dest_path = self.project_root / original_path

                if dest_path.exists():
                    if dest_path.is_file():
                        dest_path.unlink()
                    else:
                        shutil.rmtree(dest_path)

                if src_path.is_file():
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_path, dest_path)
                else:
                    shutil.copytree(src_path, dest_path)

                logger.info(f"已恢复: {original_path}")

            logger.info("备份恢复完成")
            return True

        except Exception as e:
            logger.error(f"恢复备份失败: {e}")
            return False

    def list_backups(self) -> List[BackupMetadata]:
        """列出所有备份"""
        return sorted(self.backups.values(), key=lambda x: x.timestamp, reverse=True)

    def delete_backup(self, backup_id: str) -> bool:
        """删除备份"""
        if backup_id not in self.backups:
            logger.error(f"备份不存在: {backup_id}")
            return False

        try:
            backup_metadata = self.backups[backup_id]
            backup_path = Path(backup_metadata.backup_path)

            if backup_path.exists():
                shutil.rmtree(backup_path)

            del self.backups[backup_id]
            self.save_metadata()

            logger.info(f"备份已删除: {backup_id}")
            return True

        except Exception as e:
            logger.error(f"删除备份失败: {e}")
            return False

    def verify_backup_integrity(self, backup_id: str) -> bool:
        """验证备份完整性"""
        if backup_id not in self.backups:
            logger.error(f"备份不存在: {backup_id}")
            return False

        backup_metadata = self.backups[backup_id]
        backup_path = Path(backup_metadata.backup_path)

        if not backup_path.exists():
            logger.error(f"备份路径不存在: {backup_path}")
            return False

        try:
            # 重新计算校验和
            current_checksum = self.calculate_checksum(backup_path)
            if current_checksum != backup_metadata.checksum:
                logger.error(f"备份校验和不匹配: {backup_id}")
                return False

            # 检查文件数量
            total_size, file_count = self.get_directory_size(backup_path)
            if file_count != backup_metadata.file_count:
                logger.error(f"备份文件数量不匹配: {backup_id}")
                return False

            logger.info(f"备份完整性验证通过: {backup_id}")
            return True

        except Exception as e:
            logger.error(f"验证备份完整性失败: {e}")
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="DAIP-LIVE P5-P7 隔离备份管理器")
    parser.add_argument("command", choices=[
        "backup", "restore", "isolate", "list", "verify", "delete"
    ], help="执行的命令")
    parser.add_argument("--project-root", default=".", help="项目根目录")
    parser.add_argument("--module-name", help="模块名称")
    parser.add_argument("--module-paths", nargs="+", help="模块路径列表")
    parser.add_argument("--backup-id", help="备份ID")
    parser.add_argument("--config-file", help="配置文件路径")

    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    manager = IsolationBackupManager(project_root)

    if args.command == "backup":
        if not args.module_name or not args.module_paths:
            print("❌ 备份命令需要 --module-name 和 --module-paths 参数")
            sys.exit(1)

        backup_id = manager.create_backup(args.module_paths, args.module_name)
        print(f"✅ 备份创建成功: {backup_id}")

    elif args.command == "restore":
        if not args.backup_id:
            print("❌ 恢复命令需要 --backup-id 参数")
            sys.exit(1)

        success = manager.restore_backup(args.backup_id)
        if success:
            print("✅ 备份恢复成功")
        else:
            print("❌ 备份恢复失败")
            sys.exit(1)

    elif args.command == "isolate":
        if not args.backup_id or not args.config_file:
            print("❌ 隔离命令需要 --backup-id 和 --config-file 参数")
            sys.exit(1)

        # 加载隔离配置
        with open(args.config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        config = IsolationConfig(**config_data)
        isolated_id = manager.create_isolated_version(args.backup_id, config)
        print(f"✅ 隔离版本创建成功: {isolated_id}")

    elif args.command == "list":
        backups = manager.list_backups()
        print(f"📋 共有 {len(backups)} 个备份:")
        for backup in backups:
            size_mb = backup.total_size / 1024 / 1024
            print(f"  • {backup.backup_id}")
            print(f"    模块: {backup.module_name}")
            print(f"    时间: {backup.timestamp}")
            print(f"    大小: {size_mb:.2f} MB, 文件: {backup.file_count}")
            print(f"    状态: {'✅ 完整' if manager.verify_backup_integrity(backup.backup_id) else '❌ 损坏'}")
            print()

    elif args.command == "verify":
        if not args.backup_id:
            print("❌ 验证命令需要 --backup-id 参数")
            sys.exit(1)

        success = manager.verify_backup_integrity(args.backup_id)
        if success:
            print("✅ 备份完整性验证通过")
        else:
            print("❌ 备份完整性验证失败")
            sys.exit(1)

    elif args.command == "delete":
        if not args.backup_id:
            print("❌ 删除命令需要 --backup-id 参数")
            sys.exit(1)

        success = manager.delete_backup(args.backup_id)
        if success:
            print("✅ 备份删除成功")
        else:
            print("❌ 备份删除失败")
            sys.exit(1)


if __name__ == "__main__":
    main()
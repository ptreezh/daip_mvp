"""记忆系统分离管理器
确保基于文件的记忆银行系统和轻量级记忆服务完全独立运行
"""

import json
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from src.lightweight_memory_service import LightweightMemoryService
from src.memory_bank_manager import MemoryBankManager


class MemorySystemType(Enum):
    """记忆系统类型"""

    FILE_BASED = "file_based"  # 基于文件的记忆银行系统
    LIGHTWEIGHT = "lightweight"  # 轻量级记忆服务


@dataclass
class MemorySystemConfig:
    """记忆系统配置"""

    system_type: MemorySystemType
    enabled: bool = True
    base_path: str = ""
    config: dict[str, Any] = None

    def __post_init__(self):
        if self.config is None:
            self.config = {}


class MemorySystemSeparationManager:
    """记忆系统分离管理器

    职责：
    1. 确保两套记忆系统完全独立运行
    2. 提供统一的接口进行系统选择
    3. 防止数据交叉污染
    4. 提供系统状态监控
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # 系统配置
        self.systems: dict[MemorySystemType, MemorySystemConfig] = {
            MemorySystemType.FILE_BASED: MemorySystemConfig(
                system_type=MemorySystemType.FILE_BASED,
                enabled=True,
                base_path="memory_bank",
                config={
                    "auto_backup": True,
                    "version_control": True,
                    "integrity_check": True,
                },
            ),
            MemorySystemType.LIGHTWEIGHT: MemorySystemConfig(
                system_type=MemorySystemType.LIGHTWEIGHT,
                enabled=True,
                base_path="data/lightweight_memory",
                config={
                    "async_processing": True,
                    "caching_enabled": True,
                    "batch_operations": True,
                },
            ),
        }

        # 系统实例
        self.system_instances: dict[MemorySystemType, Any] = {}

        # 初始化系统
        self._initialize_systems()

        self.logger.info("记忆系统分离管理器初始化完成")

    def _initialize_systems(self):
        """初始化记忆系统"""
        try:
            # 初始化基于文件的记忆银行系统
            if self.systems[MemorySystemType.FILE_BASED].enabled:
                self.system_instances[MemorySystemType.FILE_BASED] = MemoryBankManager(
                    base_path=self.systems[MemorySystemType.FILE_BASED].base_path,
                )
                self.logger.info("基于文件的记忆银行系统初始化完成")

            # 初始化轻量级记忆服务
            if self.systems[MemorySystemType.LIGHTWEIGHT].enabled:
                self.system_instances[
                    MemorySystemType.LIGHTWEIGHT
                ] = LightweightMemoryService(
                    data_dir=self.systems[MemorySystemType.LIGHTWEIGHT].base_path,
                )
                self.logger.info("轻量级记忆服务初始化完成")

        except Exception as e:
            self.logger.error(f"记忆系统初始化失败: {e}")
            raise

    def get_system(self, system_type: MemorySystemType) -> Optional[Any]:
        """获取指定的记忆系统实例

        Args:
        ----
            system_type: 记忆系统类型

        Returns:
        -------
            记忆系统实例或None

        """
        if not self.systems[system_type].enabled:
            self.logger.warning(f"记忆系统 {system_type.value} 未启用")
            return None

        return self.system_instances.get(system_type)

    def is_system_enabled(self, system_type: MemorySystemType) -> bool:
        """检查记忆系统是否启用"""
        return self.systems[system_type].enabled

    def get_system_status(self) -> dict[str, Any]:
        """获取所有记忆系统状态"""
        status = {
            "file_based": {
                "enabled": self.systems[MemorySystemType.FILE_BASED].enabled,
                "initialized": MemorySystemType.FILE_BASED in self.system_instances,
                "base_path": self.systems[MemorySystemType.FILE_BASED].base_path,
                "config": self.systems[MemorySystemType.FILE_BASED].config,
            },
            "lightweight": {
                "enabled": self.systems[MemorySystemType.LIGHTWEIGHT].enabled,
                "initialized": MemorySystemType.LIGHTWEIGHT in self.system_instances,
                "base_path": self.systems[MemorySystemType.LIGHTWEIGHT].base_path,
                "config": self.systems[MemorySystemType.LIGHTWEIGHT].config,
            },
        }

        # 添加系统详细信息
        if MemorySystemType.FILE_BASED in self.system_instances:
            try:
                file_based_system = self.system_instances[MemorySystemType.FILE_BASED]
                status["file_based"][
                    "summary"
                ] = file_based_system.get_memory_bank_summary()
                status["file_based"][
                    "integrity"
                ] = file_based_system.validate_memory_bank_integrity()
            except Exception as e:
                status["file_based"]["error"] = str(e)

        if MemorySystemType.LIGHTWEIGHT in self.system_instances:
            try:
                lightweight_system = self.system_instances[MemorySystemType.LIGHTWEIGHT]
                status["lightweight"]["stats"] = lightweight_system.get_statistics()
            except Exception as e:
                status["lightweight"]["error"] = str(e)

        return status

    def validate_separation(self) -> dict[str, Any]:
        """验证记忆系统分离状态"""
        validation = {
            "separation_valid": True,
            "issues": [],
            "warnings": [],
            "recommendations": [],
        }

        # 检查路径分离
        file_based_path = Path(self.systems[MemorySystemType.FILE_BASED].base_path)
        lightweight_path = Path(self.systems[MemorySystemType.LIGHTWEIGHT].base_path)

        if file_based_path.resolve() == lightweight_path.resolve():
            validation["separation_valid"] = False
            validation["issues"].append("记忆系统路径重叠，存在数据污染风险")

        # 检查路径包含关系
        if (
            file_based_path.resolve() in lightweight_path.resolve().parents
            or lightweight_path.resolve() in file_based_path.resolve().parents
        ):
            validation["warnings"].append("记忆系统路径存在包含关系，建议使用完全独立的路径")

        # 检查配置冲突
        file_based_config = self.systems[MemorySystemType.FILE_BASED].config
        lightweight_config = self.systems[MemorySystemType.LIGHTWEIGHT].config

        # 检查端口冲突（如果轻量级服务使用网络接口）
        if "port" in file_based_config and "port" in lightweight_config:
            if file_based_config["port"] == lightweight_config["port"]:
                validation["issues"].append("记忆系统端口冲突")

        # 检查数据库冲突
        if "database" in file_based_config and "database" in lightweight_config:
            if file_based_config["database"] == lightweight_config["database"]:
                validation["issues"].append("记忆系统数据库冲突")

        # 生成建议
        if validation["warnings"]:
            validation["recommendations"].append("考虑使用完全独立的路径结构")

        if validation["issues"]:
            validation["recommendations"].append("立即修复分离问题以避免数据污染")

        return validation

    def get_usage_guidelines(self) -> dict[str, str]:
        """获取记忆系统使用指南"""
        return {
            "file_based": """
基于文件的记忆银行系统使用指南：
- 用途：AI虚拟团队协作，项目管理和团队记忆
- 存储：Markdown文件，支持版本控制和备份
- 访问：通过MemoryBankManager类
- 特点：人类可读，易于调试，支持Git版本控制
- 适用场景：长期项目协作，团队决策记录，架构文档管理
            """,
            "lightweight": """
轻量级记忆服务使用指南：
- 用途：虚拟角色对话记忆，个人角色状态管理
- 存储：SQLite数据库，支持异步处理和缓存
- 访问：通过LightweightMemoryService类
- 特点：高性能，低延迟，支持并发访问
- 适用场景：实时对话，角色身份维护，会话状态管理
            """,
            "separation": """
记忆系统分离原则：
1. 严格禁止跨系统数据访问
2. 使用不同的路径和配置
3. 避免共享数据库或文件
4. 定期验证分离状态
5. 监控系统间可能的冲突
            """,
        }

    def export_system_data(
        self,
        system_type: MemorySystemType,
        export_path: str,
    ) -> bool:
        """导出记忆系统数据"""
        try:
            system = self.get_system(system_type)
            if not system:
                return False

            if system_type == MemorySystemType.FILE_BASED:
                return system.export_memory_bank(export_path)
            elif system_type == MemorySystemType.LIGHTWEIGHT:
                # 轻量级系统的导出功能
                return self._export_lightweight_data(system, export_path)

            return False
        except Exception as e:
            self.logger.error(f"导出记忆系统数据失败: {e}")
            return False

    def _export_lightweight_data(
        self,
        system: LightweightMemoryService,
        export_path: str,
    ) -> bool:
        """导出轻量级记忆系统数据"""
        try:
            export_dir = Path(export_path)
            export_dir.mkdir(parents=True, exist_ok=True)

            # 获取统计数据
            stats = system.get_statistics()

            # 导出配置
            config_data = {
                "system_type": "lightweight_memory_service",
                "export_timestamp": system.get_current_timestamp(),
                "statistics": stats,
            }

            config_file = export_dir / "export_config.json"
            config_file.write_text(
                json.dumps(config_data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

            self.logger.info(f"轻量级记忆系统数据导出到: {export_path}")
            return True
        except Exception as e:
            self.logger.error(f"导出轻量级记忆系统数据失败: {e}")
            return False

    def cleanup_system(self, system_type: MemorySystemType) -> bool:
        """清理记忆系统数据"""
        try:
            if system_type == MemorySystemType.FILE_BASED:
                # 基于文件的系统清理
                system = self.get_system(system_type)
                if system:
                    # 创建备份
                    backup_path = (
                        f"backup_{system_type.value}_{system.get_current_timestamp()}"
                    )
                    system.export_memory_bank(backup_path)

                    # 清理文件
                    base_path = Path(self.systems[system_type].base_path)
                    if base_path.exists():
                        import shutil

                        shutil.rmtree(base_path)
                        self.logger.info(f"已清理基于文件的记忆系统: {base_path}")
                        return True

            elif system_type == MemorySystemType.LIGHTWEIGHT:
                # 轻量级系统清理
                system = self.get_system(system_type)
                if system:
                    # 清理数据库
                    await system.cleanup_database()
                    self.logger.info("已清理轻量级记忆系统")
                    return True

            return False
        except Exception as e:
            self.logger.error(f"清理记忆系统失败: {e}")
            return False

    def get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime

        return datetime.now().isoformat()


# 全局实例
memory_separation_manager = MemorySystemSeparationManager()


def get_memory_system(system_type: MemorySystemType) -> Optional[Any]:
    """获取记忆系统的便捷函数"""
    return memory_separation_manager.get_system(system_type)


def get_file_based_memory_system() -> Optional[MemoryBankManager]:
    """获取基于文件的记忆银行系统"""
    return get_memory_system(MemorySystemType.FILE_BASED)


def get_lightweight_memory_system() -> Optional[LightweightMemoryService]:
    """获取轻量级记忆服务"""
    return get_memory_system(MemorySystemType.LIGHTWEIGHT)


def validate_memory_systems_separation() -> dict[str, Any]:
    """验证记忆系统分离状态"""
    return memory_separation_manager.validate_separation()


def get_memory_systems_status() -> dict[str, Any]:
    """获取记忆系统状态"""
    return memory_separation_manager.get_system_status()

"""Model Monitoring Service.

This service automatically updates the model registry on system startup and shutdown.
It can also be used to generate standalone scripts for checking model availability.
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import Any, Optional

from src.model_registry import ModelRegistry


class ModelMonitor:
    """A service to monitor the availability of various models."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize the ModelMonitor.

        Args:
            config (Optional[dict[str, Any]], optional): A configuration dictionary.
                This can contain settings for different model platforms. Defaults to None.
        """
        self.config = config or {}
        self.registry = ModelRegistry()
        self.logger = logging.getLogger(__name__)
        self.running = False

        # 设置信号处理
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        if sys.platform != "win32":
            # For Unix-based systems
            signal.signal(signal.SIGTERM, self._signal_handler)
            signal.signal(signal.SIGINT, self._signal_handler)
        else:
            # For Windows
            signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle termination signals to trigger a graceful shutdown."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(self.shutdown())

    async def startup(self):
        """Perform model detection on application startup.

        This method refreshes the model registry and logs a summary of
        available models.

        Raises:
            Exception: If refreshing models fails.
        """
        self.logger.info("🚀 Starting model monitor...")
        self.running = True

        try:
            # 刷新模型注册表
            await self.registry.refresh_all_models(self.config)

            # 显示摘要
            summary = self.registry.get_registry_summary()
            self.logger.info("📊 Model registry summary:")
            self.logger.info(f"   Total models: {summary['total_models']}")
            self.logger.info(f"   Available models: {summary['available_count']}")

            for platform, info in summary["platforms"].items():
                self.logger.info(
                    f"   {platform}: {info['available']}/{info['total']} available",
                )

        except Exception as e:
            self.logger.error(f"Failed to refresh models on startup: {e}")

    async def shutdown(self):
        """Perform final model detection on application shutdown.

        This method ensures the final state of model availability is recorded
        and saved to the registry file.

        Raises:
            Exception: If there's an error during the shutdown process.
        """
        if not self.running:
            return

        self.logger.info("🔄 Shutting down model monitor...")
        self.running = False

        try:
            # 再次检测模型状态
            await self.registry.refresh_all_models(self.config)

            # 保存最终状态
            self.registry.save_registry()

            self.logger.info("✅ Model monitor shutdown complete")

        except Exception as e:
            self.logger.error(f"Error during model monitor shutdown: {e}")

    async def periodic_check(self, interval_minutes: int = 30):
        """Periodically check the status of all models.

        Args:
            interval_minutes (int, optional): The interval in minutes between checks.
                Defaults to 30.
        """
        while self.running:
            try:
                await asyncio.sleep(interval_minutes * 60)

                if self.running:
                    self.logger.info("🔍 Performing periodic model check...")
                    await self.registry.refresh_all_models(self.config)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in periodic model check: {e}")

    def get_available_models(self, platform: Optional[str] = None):
        """Get a list of available models.

        Args:
            platform (Optional[str], optional): The platform to filter by (e.g., 'ollama').
                If None, returns all available models. Defaults to None.

        Returns:
            list: A list of available model details.
        """
        return self.registry.get_available_models(platform)

    def get_registry_summary(self):
        """Get a summary of the model registry.

        Returns:
            dict: A dictionary containing statistics about the models.
        """
        return self.registry.get_registry_summary()


# 全局模型监控实例
_model_monitor: Optional[ModelMonitor] = None


def get_model_monitor(config: Optional[dict[str, Any]] = None) -> ModelMonitor:
    """Get the global singleton instance of the ModelMonitor.

    Args:
        config (Optional[dict[str, Any]], optional): Configuration for the monitor.
            Defaults to None.
    """
    global _model_monitor
    if _model_monitor is None:
        _model_monitor = ModelMonitor(config)
    return _model_monitor


async def startup_model_monitor(config: Optional[dict[str, Any]] = None):
    """Convenience function to start the global model monitor.

    Args:
        config (Optional[dict[str, Any]], optional): Configuration for the monitor.
            Defaults to None.
    """
    monitor = get_model_monitor(config)
    await monitor.startup()
    return monitor


async def shutdown_model_monitor():
    """Convenience function to shut down the global model monitor."""
    global _model_monitor
    if _model_monitor:
        await _model_monitor.shutdown()


def create_model_check_script():
    """Create a standalone Python script to check model availability.

    This script can be run independently of the main application.

    Returns:
        Path: The path to the created script.
    """
    script_content = '''#!/usr/bin/env python3
"""
独立的模型检查脚本
可以在系统启动/关闭时调用
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.model_registry import ModelRegistry
from src.utils import load_config


async def main():
    """主函数"""
    print("🔍 Checking available models...")

    # 加载配置
    try:
        config = load_config()
    except:
        config = {}

    # 创建注册表
    registry = ModelRegistry()

    # 刷新模型
    await registry.refresh_all_models(config)

    # 显示结果
    summary = registry.get_registry_summary()

    print(f"📊 Model Check Results:")
    print(f"   Total models: {summary['total_models']}")
    print(f"   Available models: {summary['available_count']}")
    print()

    for platform, info in summary['platforms'].items():
        print(f"🔧 {platform.upper()}:")
        print(f"   Available: {info['available']}/{info['total']}")

        for model in info['models']:
            status_icon = "✅" if model['status'] == 'available' else "❌"
            size_info = f" ({model['size']})" if model['size'] else ""
            print(f"   {status_icon} {model['name']}{size_info}")
        print()

    print("✅ Model check completed!")


if __name__ == "__main__":
    asyncio.run(main())
'''

    script_path = Path("check_models.py")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)

    # 在Unix系统上设置执行权限
    if sys.platform != "win32":
        os.chmod(script_path, 0o755)

    return script_path


# 创建Windows批处理脚本
def create_windows_scripts():
    """Create Windows batch scripts for startup and shutdown checks."""
    # 启动脚本
    startup_script = """@echo off
echo Starting DAIP Insight Engine...
cd /d "%~dp0"
python check_models.py
echo Model check completed.
"""

    with open("startup_check.bat", "w", encoding="utf-8") as f:
        f.write(startup_script)

    # 关闭脚本
    shutdown_script = """@echo off
echo Shutting down DAIP Insight Engine...
cd /d "%~dp0"
python check_models.py
echo Final model check completed.
"""

    with open("shutdown_check.bat", "w", encoding="utf-8") as f:
        f.write(shutdown_script)


# 创建Linux/Mac脚本
def create_unix_scripts():
    """Create Unix shell scripts for startup and shutdown checks."""
    # 启动脚本
    startup_script = """#!/bin/bash
echo "Starting DAIP Insight Engine..."
cd "$(dirname "$0")"
python3 check_models.py
echo "Model check completed."
"""

    with open("startup_check.sh", "w", encoding="utf-8") as f:
        f.write(startup_script)

    # 关闭脚本
    shutdown_script = """#!/bin/bash
echo "Shutting down DAIP Insight Engine..."
cd "$(dirname "$0")"
python3 check_models.py
echo "Final model check completed."
"""

    with open("shutdown_check.sh", "w", encoding="utf-8") as f:
        f.write(shutdown_script)

    # 设置执行权限
    os.chmod("startup_check.sh", 0o755)
    os.chmod("shutdown_check.sh", 0o755)


def setup_model_monitoring():
    """Set up all necessary scripts for model monitoring."""
    print("🔧 Setting up model monitoring scripts...")

    # 创建独立检查脚本
    script_path = create_model_check_script()
    print(f"✅ Created model check script: {script_path}")

    # 根据操作系统创建相应脚本
    if sys.platform == "win32":
        create_windows_scripts()
        print("✅ Created Windows startup/shutdown scripts:")
        print("   - startup_check.bat")
        print("   - shutdown_check.bat")
    else:
        create_unix_scripts()
        print("✅ Created Unix startup/shutdown scripts:")
        print("   - startup_check.sh")
        print("   - shutdown_check.sh")

    print("\n📋 Usage Instructions:")
    print("1. Run model check manually:")
    if sys.platform == "win32":
        print("   python check_models.py")
    else:
        print("   python3 check_models.py")

    print("\n2. Integrate with system startup:")
    if sys.platform == "win32":
        print("   - Add startup_check.bat to Windows startup folder")
        print("   - Or use Task Scheduler for more control")
    else:
        print("   - Add to ~/.bashrc or ~/.profile:")
        print("   - Or use systemd service for automatic startup")

    print("\n3. The model registry will be saved to: data/model_registry.json")


if __name__ == "__main__":
    setup_model_monitoring()

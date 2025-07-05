"""模型监控服务 - 在系统启动和关闭时自动更新模型注册表
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import Any, Optional

from src.model_registry import ModelRegistry


class ModelMonitor:
    """模型监控服务"""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.registry = ModelRegistry()
        self.logger = logging.getLogger(__name__)
        self.running = False

        # 设置信号处理
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """设置信号处理器"""
        if sys.platform != "win32":
            # Unix系统
            signal.signal(signal.SIGTERM, self._signal_handler)
            signal.signal(signal.SIGINT, self._signal_handler)
        else:
            # Windows系统
            signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """信号处理器"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(self.shutdown())

    async def startup(self):
        """启动时的模型检测"""
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
        """关闭时的模型检测"""
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
        """定期检查模型状态"""
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
        """获取可用模型列表"""
        return self.registry.get_available_models(platform)

    def get_registry_summary(self):
        """获取注册表摘要"""
        return self.registry.get_registry_summary()


# 全局模型监控实例
_model_monitor: Optional[ModelMonitor] = None


def get_model_monitor(config: Optional[dict[str, Any]] = None) -> ModelMonitor:
    """获取全局模型监控实例"""
    global _model_monitor
    if _model_monitor is None:
        _model_monitor = ModelMonitor(config)
    return _model_monitor


async def startup_model_monitor(config: Optional[dict[str, Any]] = None):
    """启动模型监控"""
    monitor = get_model_monitor(config)
    await monitor.startup()
    return monitor


async def shutdown_model_monitor():
    """关闭模型监控"""
    global _model_monitor
    if _model_monitor:
        await _model_monitor.shutdown()


def create_model_check_script():
    """创建独立的模型检查脚本"""
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
    """创建Windows启动/关闭脚本"""
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
    """创建Unix启动/关闭脚本"""
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
    """设置模型监控脚本"""
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

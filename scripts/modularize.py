#!/usr/bin/env python3
"""
DAIP-LIVE 模块化工具

用于自动化模块编译、测试和部署的脚本。
"""

import argparse
import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# from daip_live.core.interfaces import ModuleContract


class ModuleManager:
    """模块管理器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.src_dir = project_root / "src"
        self.modules_dir = self.src_dir / "daip_live"
        self.dist_dir = project_root / "dist"
        self.dist_dir.mkdir(exist_ok=True)

    def discover_modules(self) -> List[str]:
        """发现所有模块"""
        modules = []
        for item in self.modules_dir.iterdir():
            if item.is_dir() and not item.name.startswith("__"):
                init_file = item / "__init__.py"
                if init_file.exists():
                    modules.append(item.name)
        return modules

    async def compile_module(self, module_name: str) -> bool:
        """编译单个模块"""
        print(f"🔨 编译模块: {module_name}")

        module_path = self.modules_dir / module_name
        if not module_path.exists():
            print(f"❌ 模块不存在: {module_name}")
            return False

        # 创建模块包结构
        package_dir = self.dist_dir / f"daip_live_{module_name}"
        package_dir.mkdir(exist_ok=True)

        # 复制模块文件
        result = subprocess.run([
            "cp", "-r", str(module_path), str(package_dir)
        ], capture_output=True)

        if result.returncode != 0:
            print(f"❌ 复制文件失败: {result.stderr.decode()}")
            return False

        # 创建setup.py
        setup_content = f'''
from setuptools import setup, find_packages

setup(
    name="daip-live-{module_name}",
    version="1.0.0",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "pydantic>=2.7.4,<3.0.0",
    ],
)
'''
        setup_file = package_dir / "setup.py"
        setup_file.write_text(setup_content.strip())

        # 构建wheel包
        result = subprocess.run([
            sys.executable, "-m", "build", "--wheel"
        ], cwd=package_dir, capture_output=True)

        if result.returncode != 0:
            print(f"❌ 构建失败: {result.stderr.decode()}")
            return False

        print(f"✅ 模块编译成功: {module_name}")
        return True

    async def test_module(self, module_name: str) -> bool:
        """测试单个模块"""
        print(f"🧪 测试模块: {module_name}")

        # 运行模块特定的测试
        test_patterns = [
            f"tests/**/test_{module_name}*.py",
            f"tests/{module_name}/**/*.py"
        ]

        for pattern in test_patterns:
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                pattern, "-v", "--tb=short"
            ], cwd=self.project_root, capture_output=True)

            if result.returncode != 0:
                print(f"❌ 测试失败: {result.stderr.decode()}")
                return False

        print(f"✅ 模块测试通过: {module_name}")
        return True

    async def check_dependencies(self, module_name: str) -> bool:
        """检查模块依赖"""
        print(f"🔍 检查依赖: {module_name}")

        module_path = self.modules_dir / module_name
        init_file = module_path / "__init__.py"

        if not init_file.exists():
            return True

        # 简单的导入检查
        try:
            spec = importlib.util.spec_from_file_location(
                f"daip_live.{module_name}", str(init_file)
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 检查是否有依赖声明
            if hasattr(module, 'get_dependencies'):
                deps = module.get_dependencies()
                print(f"   依赖: {deps}")

            print(f"✅ 依赖检查通过: {module_name}")
            return True

        except Exception as e:
            print(f"❌ 依赖检查失败: {e}")
            return False

    async def health_check(self, module_name: str) -> bool:
        """模块健康检查"""
        print(f"🏥 健康检查: {module_name}")

        try:
            # 尝试导入模块
            module = importlib.import_module(f"daip_live.{module_name}")

            # 检查是否有健康检查方法
            if hasattr(module, 'health_check'):
                result = await module.health_check()
                if result:
                    print(f"✅ 健康检查通过: {module_name}")
                    return False
                else:
                    print(f"❌ 健康检查失败: {module_name}")
                    return False
            else:
                print(f"⚠️  无健康检查方法: {module_name}")
                return True

        except Exception as e:
            print(f"❌ 健康检查异常: {e}")
            return False


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="DAIP-LIVE 模块化工具")
    parser.add_argument("command", choices=[
        "discover", "compile", "test", "check", "health", "all"
    ], help="执行的命令")
    parser.add_argument("--module", help="指定模块名称")
    parser.add_argument("--project-root", default=".", help="项目根目录")

    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    manager = ModuleManager(project_root)

    if args.command == "discover":
        modules = manager.discover_modules()
        print(f"发现的模块: {modules}")

    elif args.command == "compile":
        if args.module:
            await manager.compile_module(args.module)
        else:
            modules = manager.discover_modules()
            for module in modules:
                await manager.compile_module(module)

    elif args.command == "test":
        if args.module:
            await manager.test_module(args.module)
        else:
            modules = manager.discover_modules()
            for module in modules:
                await manager.test_module(module)

    elif args.command == "check":
        if args.module:
            await manager.check_dependencies(args.module)
        else:
            modules = manager.discover_modules()
            for module in modules:
                await manager.check_dependencies(module)

    elif args.command == "health":
        if args.module:
            await manager.health_check(args.module)
        else:
            modules = manager.discover_modules()
            for module in modules:
                await manager.health_check(module)

    elif args.command == "all":
        modules = manager.discover_modules()
        if args.module:
            modules = [args.module]

        for module in modules:
            print(f"\n🚀 处理模块: {module}")
            print("=" * 50)

            # 检查依赖
            if not await manager.check_dependencies(module):
                continue

            # 编译模块
            if not await manager.compile_module(module):
                continue

            # 测试模块
            if not await manager.test_module(module):
                continue

            # 健康检查
            await manager.health_check(module)

            print(f"✅ 模块处理完成: {module}")


if __name__ == "__main__":
    import importlib.util
    asyncio.run(main())
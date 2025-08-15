#!/usr/bin/env python3
"""集成演示系统启动脚本

启动DAIP-LIVE真实演示系统，包含所有集成组件
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_dependencies():
    """检查依赖项"""
    required_packages = [
        'lona',
        'asyncio',
        'websockets',
        'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    return True


def check_backend_services():
    """检查后端服务状态"""
    print("🔍 检查后端服务状态...")
    
    # 检查Ollama服务
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama服务: 运行中")
        else:
            print("⚠️ Ollama服务: 响应异常")
    except Exception as e:
        print(f"❌ Ollama服务: 不可用 ({e})")
        print("请启动Ollama服务: ollama serve")
    
    # 检查角色库
    roles_dir = project_root / "roles"
    if roles_dir.exists():
        role_files = list(roles_dir.glob("*.json"))
        print(f"✅ 角色库: {len(role_files)} 个角色已加载")
    else:
        print("⚠️ 角色库: 目录不存在")
    
    # 检查核心服务
    core_services_dir = project_root / "src" / "core_services"
    if core_services_dir.exists():
        print("✅ 核心服务: 目录存在")
    else:
        print("❌ 核心服务: 目录不存在")


async def initialize_services():
    """初始化服务"""
    print("🔧 初始化服务...")
    
    try:
        # 这里可以添加服务初始化逻辑
        # 例如：预加载模型、初始化数据库连接等
        await asyncio.sleep(1)  # 模拟初始化时间
        print("✅ 服务初始化完成")
        return True
    except Exception as e:
        print(f"❌ 服务初始化失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 70)
    print("🎭 DAIP-LIVE 真实演示系统")
    print("基于制度原语的集体智慧涌现平台")
    print("=" * 70)
    print()
    
    # 检查依赖
    print("📦 检查依赖项...")
    if not check_dependencies():
        sys.exit(1)
    print("✅ 依赖项检查通过")
    print()
    
    # 检查后端服务
    check_backend_services()
    print()
    
    # 初始化服务
    print("🚀 启动集成演示系统...")
    
    try:
        # 导入并启动应用
        from integrated_demo_app import app, startup_tasks
        
        print("📍 访问地址: http://localhost:8080")
        print("🔴 真实LLM调用: 已启用")
        print("📊 透明度监控: 已启用")
        print("🔍 完全透明: 已启用")
        print("⚡ 实时监控: 已启用")
        print()
        print("🎯 演示功能:")
        print("  • AI伦理决策分析")
        print("  • 产品策略评估")
        print("  • 技术风险评估")
        print("  • 自定义场景演示")
        print()
        print("按 Ctrl+C 停止服务器")
        print("=" * 70)
        
        # 启动应用（Lona会处理异步任务）
        app.run(
            host='localhost',
            port=8080,
            debug=True,
            shutdown_timeout=10
        )
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保所有组件文件都存在")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n👋 演示系统已停止")
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        logger.exception("启动异常")
        sys.exit(1)


if __name__ == '__main__':
    main()
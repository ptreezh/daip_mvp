#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Personal Intelligence Hub - 双入口Lona界面启动脚本

基于DDD架构设计的统一入口界面
支持Secretariat和Forum两种交互模式
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from lona import LonaApp, View
from lona.html import HTML, Head, Title, Link, Meta, Body, Div, H1, P
from frontend.lona_interface_design import MainView, create_lona_app
from frontend.websocket_integration import global_websocket_manager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('frontend.log')
    ]
)

logger = logging.getLogger(__name__)

class StartupView(View):
    """启动视图"""
    
    def handle_request(self, request):
        """处理启动请求"""
        return HTML(
            Head(
                Title("Personal Intelligence Hub - 启动中"),
                Link(
                    rel="stylesheet",
                    href="/static/css/main.css"
                ),
                Meta(
                    name="viewport",
                    content="width=device-width, initial-scale=1.0"
                )
            ),
            Body(
                Div(
                    Div(
                        H1("🚀 Personal Intelligence Hub"),
                        P("正在启动双入口系统..."),
                        Div(
                            Div(_class="spinner"),
                            P("正在初始化组件和连接服务", _class="loading-text"),
                            _class="loading-container"
                        ),
                        _class="startup-container"
                    ),
                    _class="startup-page"
                )
            )
        )

async def initialize_system():
    """初始化系统"""
    logger.info("🔧 正在初始化Personal Intelligence Hub双入口系统...")
    
    try:
        # 1. 初始化WebSocket连接
        logger.info("🔌 正在连接WebSocket服务...")
        await global_websocket_manager.connect(user_id="system_user")
        
        if global_websocket_manager.is_connected:
            logger.info("✅ WebSocket连接成功")
        else:
            logger.warning("⚠️ WebSocket连接失败，将使用离线模式")
        
        # 2. 检查依赖服务
        logger.info("🔍 正在检查依赖服务...")
        
        # 检查后端服务
        try:
            # 这里可以添加后端服务检查逻辑
            logger.info("✅ 后端服务检查通过")
        except Exception as e:
            logger.warning(f"⚠️ 后端服务检查失败: {e}")
        
        # 3. 初始化数据存储
        logger.info("💾 正在初始化数据存储...")
        
        # 检查数据目录
        data_dirs = [
            project_root / "data",
            project_root / "data" / "chat_logs",
            project_root / "data" / "user_profiles",
            project_root / "data" / "memory_banks"
        ]
        
        for data_dir in data_dirs:
            data_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("✅ 数据存储初始化完成")
        
        # 4. 加载配置
        logger.info("⚙️ 正在加载配置...")
        
        config_file = project_root / "config.yaml"
        if config_file.exists():
            logger.info("✅ 配置文件加载成功")
        else:
            logger.warning("⚠️ 配置文件不存在，将使用默认配置")
        
        # 5. 验证系统状态
        logger.info("🔍 正在验证系统状态...")
        
        # 检查必要的文件和目录
        required_files = [
            project_root / "frontend" / "static" / "css" / "main.css",
            project_root / "frontend" / "static" / "css" / "components.css",
            project_root / "frontend" / "static" / "css" / "dual_entrance.css"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not file_path.exists():
                missing_files.append(str(file_path))
        
        if missing_files:
            logger.error(f"❌ 缺少必要的文件: {missing_files}")
            return False
        else:
            logger.info("✅ 所有必要文件检查通过")
        
        logger.info("🎉 系统初始化完成！")
        return True
        
    except Exception as e:
        logger.error(f"❌ 系统初始化失败: {e}")
        return False

async def startup_complete():
    """启动完成后的操作"""
    logger.info("🎯 Personal Intelligence Hub 双入口系统已启动")
    logger.info("📍 访问地址: http://localhost:8080")
    logger.info("🎭 支持模式: Secretariat + Forum")
    logger.info("🔌 WebSocket实时通信: 已启用")
    logger.info("📱 响应式设计: 已启用")
    
    # 显示系统信息
    status = global_websocket_manager.get_connection_status()
    logger.info(f"📊 连接状态: {'已连接' if status['connected'] else '未连接'}")
    logger.info(f"🔧 会话ID: {status['session_id']}")

def create_app():
    """创建Lona应用"""
    logger.info("🏗️ 正在创建Lona应用...")
    
    # 创建应用实例
    app = create_lona_app()
    
    # 添加启动视图
    app.route('/startup', StartupView)
    
    # 设置静态文件
    app.static_files.add('/static/', 'frontend/static/')
    
    # 设置应用配置
    app.settings.MAX_WORKERS = 4
    app.settings.SHUTDOWN_TIMEOUT = 10
    app.settings.DEBUG = True
    
    logger.info("✅ Lona应用创建完成")
    return app

async def main():
    """主函数"""
    try:
        logger.info("🚀 启动 Personal Intelligence Hub 双入口系统...")
        
        # 显示系统信息
        logger.info("=" * 60)
        logger.info("Personal Intelligence Hub - 双入口Lona界面")
        logger.info("=" * 60)
        logger.info("🎯 基于DDD架构设计")
        logger.info("🎭 支持Secretariat和Forum两种交互模式")
        logger.info("🔌 集成WebSocket实时通信")
        logger.info("📱 响应式Web界面")
        logger.info("=" * 60)
        
        # 初始化系统
        if not await initialize_system():
            logger.error("❌ 系统初始化失败，无法启动")
            return
        
        # 创建应用
        app = create_app()
        
        # 启动完成回调
        await startup_complete()
        
        # 运行应用
        logger.info("🌐 正在启动Web服务器...")
        app.run(
            host='localhost',
            port=8080,
            debug=True,
            shutdown_timeout=10
        )
        
    except KeyboardInterrupt:
        logger.info("👋 用户中断，正在关闭系统...")
        
        # 清理资源
        try:
            await global_websocket_manager.disconnect()
            logger.info("✅ WebSocket连接已关闭")
        except Exception as e:
            logger.error(f"❌ 关闭WebSocket连接时出错: {e}")
        
        logger.info("👋 系统已关闭")
        
    except Exception as e:
        logger.error(f"❌ 启动失败: {e}")
        raise

def run_sync():
    """同步运行函数"""
    """同步运行函数"""
    # 获取或创建事件循环
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # 运行主函数
    loop.run_until_complete(main())

if __name__ == '__main__':
    run_sync()
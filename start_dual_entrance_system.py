#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双入口系统启动脚本

快速启动Personal Intelligence Hub双入口系统
"""

import sys
import os
import subprocess
import asyncio
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """检查依赖"""
    logger.info("检查系统依赖...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        logger.error("需要Python 3.8或更高版本")
        return False
    
    # 检查必要的包
    required_packages = [
        'lona',
        'fastapi',
        'uvicorn',
        'websockets',
        'aiofiles',
        'jinja2',
        'python-multipart'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"缺少必要的包: {', '.join(missing_packages)}")
        logger.info("请运行: pip install " + " ".join(missing_packages))
        return False
    
    logger.info("所有依赖检查通过")
    return True

def start_backend_server():
    """启动后端服务器"""
    logger.info("启动后端服务器...")
    
    try:
        # 启动FastAPI后端
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "src.main:app",
            "--host", "localhost", "--port", "8000",
            "--reload", "--log-level", "info"
        ])
        
        logger.info(f"后端服务器已启动 (PID: {backend_process.pid})")
        return backend_process
        
    except Exception as e:
        logger.error(f"启动后端服务器失败: {e}")
        return None

def start_frontend_server():
    """启动前端服务器"""
    logger.info("启动前端服务器...")
    
    try:
        # 启动Lona前端
        frontend_process = subprocess.Popen([
            sys.executable, "frontend/dual_entrance_app.py"
        ])
        
        logger.info(f"前端服务器已启动 (PID: {frontend_process.pid})")
        return frontend_process
        
    except Exception as e:
        logger.error(f"启动前端服务器失败: {e}")
        return None

def main():
    """主函数"""
    print("🚀 启动 Personal Intelligence Hub 双入口系统")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 启动后端服务器
    backend_process = start_backend_server()
    if not backend_process:
        logger.error("无法启动后端服务器")
        sys.exit(1)
    
    # 等待后端服务器启动
    logger.info("等待后端服务器启动...")
    import time
    time.sleep(5)
    
    # 启动前端服务器
    frontend_process = start_frontend_server()
    if not frontend_process:
        logger.error("无法启动前端服务器")
        backend_process.terminate()
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ 双入口系统启动成功!")
    print("📍 访问地址:")
    print("   • 主页面: http://localhost:8080")
    print("   • Secretariat: http://localhost:8080/secretariat")
    print("   • Forum: http://localhost:8080/forum")
    print("   • 后端API: http://localhost:8000/docs")
    print("=" * 50)
    print("💡 提示:")
    print("   • 按 Ctrl+C 停止服务器")
    print("   • 查看日志获取更多信息")
    print("=" * 50)
    
    try:
        # 等待用户中断
        while True:
            import time
            time.sleep(1)
            
            # 检查进程是否还在运行
            if backend_process.poll() is not None:
                logger.error("后端服务器已停止")
                break
            
            if frontend_process.poll() is not None:
                logger.error("前端服务器已停止")
                break
                
    except KeyboardInterrupt:
        print("\n\n🛑 正在停止服务器...")
        
        # 停止前端服务器
        if frontend_process and frontend_process.poll() is None:
            frontend_process.terminate()
            logger.info("前端服务器已停止")
        
        # 停止后端服务器
        if backend_process and backend_process.poll() is None:
            backend_process.terminate()
            logger.info("后端服务器已停止")
        
        print("✅ 所有服务器已停止")
        sys.exit(0)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时状态监控演示

展示任务3.1.2的实时状态监控功能
包括透明度监控、WebSocket通信和系统状态实时更新
"""

import asyncio
import logging
import sys
from datetime import datetime
from typing import Dict, Any

from lona import LonaApp, View
from lona.html import HTML, Div, H1, H2, P, Button, Span

# 导入组件和服务
from components.transparency_monitor import TransparencyMonitor
from services.websocket_manager import websocket_manager, realtime_manager, MessageType, WebSocketMessage

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 创建Lona应用
app = LonaApp(__file__)


class RealtimeMonitoringDemoView(View):
    """实时状态监控演示视图"""
    
    def __init__(self, server, view_runtime, request):
        super().__init__(server, view_runtime, request)
        
        # 初始化透明度监控器
        self.transparency_monitor = TransparencyMonitor(
            websocket_manager=websocket_manager,
            realtime_manager=realtime_manager
        )
        
        # 演示状态
        self.demo_running = False
        self.demo_task = None
        
        logger.info("实时状态监控演示视图已初始化")
    
    async def handle_start_demo(self, event):
        """处理开始演示按钮"""
        if not self.demo_running:
            self.demo_running = True
            
            # 连接WebSocket
            await websocket_manager.connect()
            
            # 启动透明度监控
            await self.transparency_monitor.start_monitoring()
            
            # 启动演示任务
            self.demo_task = asyncio.create_task(self._run_demo_simulation())
            
            logger.info("实时状态监控演示已启动")
            await self.refresh()
    
    async def handle_stop_demo(self, event):
        """处理停止演示按钮"""
        if self.demo_running:
            self.demo_running = False
            
            # 停止演示任务
            if self.demo_task:
                self.demo_task.cancel()
                self.demo_task = None
            
            # 停止透明度监控
            await self.transparency_monitor.stop_monitoring()
            
            # 断开WebSocket
            await websocket_manager.disconnect()
            
            logger.info("实时状态监控演示已停止")
            await self.refresh()
    
    async def _run_demo_simulation(self):
        """运行演示模拟"""
        try:
            # 模拟一系列系统事件
            demo_events = [
                # 系统启动
                {
                    "delay": 1,
                    "type": "system_status",
                    "data": {
                        "type": "backend_connection",
                        "data": {"connected": True}
                    }
                },
                # LLM服务上线
                {
                    "delay": 2,
                    "type": "system_status", 
                    "data": {
                        "type": "llm_service",
                        "data": {
                            "service": "ollama",
                            "status": "healthy",
                            "response_time": 1.2
                        }
                    }
                },
                # 角色库加载
                {
                    "delay": 1,
                    "type": "system_status",
                    "data": {
                        "type": "role_library",
                        "data": {"status": "loaded"}
                    }
                },
                # 代理激活
                {
                    "delay": 2,
                    "type": "agent_status",
                    "data": {
                        "agent_id": "demo_agent_001",
                        "name": "演示专家",
                        "status": "thinking",
                        "framework": "演示推理",
                        "confidence": 0.85,
                        "current_task": "分析演示场景"
                    }
                },
                # LLM调用
                {
                    "delay": 3,
                    "type": "llm_call",
                    "data": {
                        "id": "demo_call_001",
                        "model": "llama3:instruct",
                        "input_tokens": 200,
                        "output_tokens": 350,
                        "response_time": 2.1,
                        "cost": 0.0035,
                        "success": True,
                        "provider": "ollama"
                    }
                },
                # 工作流启动
                {
                    "delay": 1,
                    "type": "workflow",
                    "data": {
                        "workflow_id": "demo_workflow_001",
                        "type": "demo_analysis",
                        "status": "started",
                        "progress": 0,
                        "workflows": ["演示分析"],
                        "roles": ["演示专家"]
                    }
                },
                # 工作流进度更新
                {
                    "delay": 3,
                    "type": "workflow",
                    "data": {
                        "workflow_id": "demo_workflow_001",
                        "status": "running",
                        "progress": 50
                    }
                },
                # 代理状态更新
                {
                    "delay": 2,
                    "type": "agent_status",
                    "data": {
                        "agent_id": "demo_agent_001",
                        "status": "processing",
                        "current_task": "生成演示结果"
                    }
                },
                # 工作流完成
                {
                    "delay": 3,
                    "type": "workflow",
                    "data": {
                        "workflow_id": "demo_workflow_001",
                        "status": "completed",
                        "progress": 100,
                        "result": {
                            "success": True,
                            "insights": ["演示洞察1", "演示洞察2"]
                        }
                    }
                },
                # 代理完成
                {
                    "delay": 1,
                    "type": "agent_status",
                    "data": {
                        "agent_id": "demo_agent_001",
                        "status": "completed",
                        "current_task": "演示任务已完成"
                    }
                }
            ]
            
            # 执行演示事件
            for event in demo_events:
                if not self.demo_running:
                    break
                
                await asyncio.sleep(event["delay"])
                
                # 发送事件到透明度监控器
                if event["type"] == "agent_status":
                    await self.transparency_monitor.update_agent_status(event["data"])
                elif event["type"] == "system_status":
                    await self.transparency_monitor.update_system_status(event["data"])
                elif event["type"] == "workflow":
                    await self.transparency_monitor.update_workflow_status(event["data"])
                elif event["type"] == "llm_call":
                    await self.transparency_monitor.log_llm_call(event["data"])
                
                # 刷新界面
                await self.refresh()
            
            # 演示完成后循环重复
            if self.demo_running:
                await asyncio.sleep(5)  # 等待5秒后重新开始
                self.demo_task = asyncio.create_task(self._run_demo_simulation())
        
        except asyncio.CancelledError:
            logger.info("演示模拟已取消")
        except Exception as e:
            logger.error(f"演示模拟出错: {e}")
    
    def render(self) -> HTML:
        """渲染演示界面"""
        # 创建控制按钮
        if self.demo_running:
            control_button = Button(
                "🛑 停止演示",
                _class="btn btn-danger",
                onclick=self.handle_stop_demo
            )
            status_text = "🟢 演示运行中"
        else:
            control_button = Button(
                "▶️ 开始演示",
                _class="btn btn-success", 
                onclick=self.handle_start_demo
            )
            status_text = "⏸️ 演示已停止"
        
        return HTML(
            Div(
                # 标题区域
                Div(
                    H1("🔍 实时状态监控演示", style="text-align: center; color: #2c3e50; margin-bottom: 20px;"),
                    P("任务3.1.2: 基于现有TransparencyMonitor展示系统状态", 
                      style="text-align: center; color: #7f8c8d; margin-bottom: 30px;"),
                    style="padding: 20px; background: #ecf0f1; border-radius: 10px; margin-bottom: 20px;"
                ),
                
                # 控制面板
                Div(
                    H2("🎛️ 演示控制", style="margin-bottom: 15px;"),
                    Div(
                        Span(status_text, style="margin-right: 20px; font-weight: bold;"),
                        control_button,
                        style="display: flex; align-items: center; justify-content: center; padding: 15px;"
                    ),
                    style="background: #fff; border: 1px solid #ddd; border-radius: 8px; margin-bottom: 20px;"
                ),
                
                # 功能说明
                Div(
                    H2("✨ 功能特性", style="margin-bottom: 15px;"),
                    Div(
                        P("• 🏥 实时系统健康状态监控"),
                        P("• 🤖 代理状态和活动跟踪"),
                        P("• 📡 LLM调用透明度展示"),
                        P("• 🔄 工作流执行进度监控"),
                        P("• ⚡ 性能指标实时计算"),
                        P("• 🔌 WebSocket实时通信"),
                        style="padding: 15px;"
                    ),
                    style="background: #fff; border: 1px solid #ddd; border-radius: 8px; margin-bottom: 20px;"
                ),
                
                # 透明度监控组件
                Div(
                    H2("📊 实时监控面板", style="margin-bottom: 15px;"),
                    self.transparency_monitor.render(),
                    style="background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 20px;"
                ),
                
                style="max-width: 1200px; margin: 0 auto; padding: 20px;"
            ),
            style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8f9fa; min-height: 100vh;"
        )


# 路由配置
app.route('/', RealtimeMonitoringDemoView)


if __name__ == '__main__':
    print("🚀 启动实时状态监控演示")
    print("="*60)
    print("📍 访问地址: http://localhost:8080")
    print("🔍 功能: 实时状态监控、透明度展示、WebSocket通信")
    print("⚡ 特性: 系统健康监控、代理状态跟踪、工作流进度监控")
    print("="*60)
    
    try:
        app.run(
            host='127.0.0.1',
            port=8080,
            debug=True
        )
    except KeyboardInterrupt:
        print("\n⏹️  演示已停止")
    except Exception as e:
        print(f"\n💥 启动失败: {e}")
        sys.exit(1)
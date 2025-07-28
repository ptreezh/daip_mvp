#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
透明度监控组件 - 简化版本

实时显示系统内部运作过程，提供完全透明度
"""

from lona.html.widget import Widget
from lona.html import HTML, Div, H3, P, Span
from datetime import datetime


class TransparencyMonitor(Widget):
    """透明度监控组件"""
    
    def __init__(self):
        super().__init__()
        
        # 模拟数据
        self.active_agents = [
            {"name": "Dr. 理性分析师", "status": "idle", "framework": "科学分析"},
            {"name": "创意直觉师", "status": "thinking", "framework": "直觉洞察"},
        ]
        
        self.llm_calls = [
            {"model": "gpt-4", "tokens": 1250, "cost": 0.025, "time": "14:30:15"},
            {"model": "claude-3", "tokens": 890, "cost": 0.018, "time": "14:29:42"},
        ]
    
    async def update_agent_status(self, data):
        """更新代理状态（WebSocket回调）"""
        try:
            # 更新代理状态数据
            agent_id = data.get("agent_id")
            status = data.get("status")
            framework = data.get("framework")
            
            # 查找并更新对应代理
            for agent in self.active_agents:
                if agent.get("id") == agent_id or agent["name"] == data.get("name"):
                    agent["status"] = status
                    if framework:
                        agent["framework"] = framework
                    break
            else:
                # 如果代理不存在，添加新代理
                self.active_agents.append({
                    "name": data.get("name", f"Agent-{agent_id}"),
                    "status": status,
                    "framework": framework or "未知"
                })
            
            # 刷新组件显示
            await self.refresh()
            
        except Exception as e:
            print(f"更新代理状态失败: {e}")
    
    def render(self) -> HTML:
        return Div(
            H3("🔍 系统透明度", _class="panel-title"),
            
            # 活跃代理状态
            Div(
                P("活跃代理:", style="font-weight: 600; margin-bottom: 10px;"),
                *[
                    Div(
                        Span(agent["name"], style="font-weight: 500;"),
                        Span(
                            agent["status"], 
                            _class=f"badge badge-{'success' if agent['status'] == 'thinking' else 'info'}",
                            style="margin-left: 10px;"
                        ),
                        P(f"推理框架: {agent['framework']}", style="font-size: 0.85rem; color: #6c757d; margin: 5px 0;"),
                        style="padding: 8px; border: 1px solid #e9ecef; border-radius: 6px; margin-bottom: 8px;"
                    )
                    for agent in self.active_agents
                ],
                style="margin-bottom: 20px;"
            ),
            
            # LLM调用监控
            Div(
                P("LLM调用记录:", style="font-weight: 600; margin-bottom: 10px;"),
                *[
                    Div(
                        P(f"模型: {call['model']}", style="margin: 0; font-weight: 500;"),
                        P(f"Token: {call['tokens']} | 成本: ${call['cost']:.3f}", style="margin: 0; font-size: 0.85rem;"),
                        P(f"时间: {call['time']}", style="margin: 0; font-size: 0.8rem; color: #6c757d;"),
                        style="padding: 8px; background: #f8f9fa; border-radius: 6px; margin-bottom: 6px;"
                    )
                    for call in self.llm_calls
                ],
                style="margin-bottom: 15px;"
            ),
            
            # Token使用统计
            Div(
                P("Token使用统计", style="color: white; font-weight: 600; margin: 0;"),
                P("总计: 2,140 tokens | 成本: $0.043", style="color: white; margin: 5px 0 0 0; font-size: 0.9rem;"),
                style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 12px; border-radius: 6px;"
            ),
            
            _class="transparency-monitor"
        )

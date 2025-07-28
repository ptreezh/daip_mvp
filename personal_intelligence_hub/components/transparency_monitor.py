"""
Personal Intelligence Hub - Transparency Monitor Component

实时透明度监控面板组件
"""

from lona.html import HTML, Div, H3, P, Span, Button
from datetime import datetime
from typing import List, Optional

from personal_intelligence_hub.models.transparency_models import (
    SystemStatus, AgentStatusInfo, LLMCall, AgentStatus, 
    TokenUsage, MemoryOperation, OperationLog
)


class TransparencyMonitor:
    """透明度监控组件"""
    
    def __init__(self):
        self.system_status = SystemStatus(active_agents=[])
        self.operation_logs: List = []
        self.backend_service = None
        self.auto_refresh = True
        self.refresh_interval = 5  # 5秒刷新一次
        self.refresh_task = None
    
    async def _ensure_backend_service(self):
        """确保后端服务已初始化"""
        if self.backend_service is None:
            from personal_intelligence_hub.services.backend_integration import get_backend_service
            self.backend_service = await get_backend_service()
    
    async def start_auto_refresh(self):
        """启动自动刷新"""
        if self.refresh_task is None and self.auto_refresh:
            self.refresh_task = asyncio.create_task(self._refresh_loop())
    
    async def stop_auto_refresh(self):
        """停止自动刷新"""
        if self.refresh_task:
            self.refresh_task.cancel()
            self.refresh_task = None
    
    async def _refresh_loop(self):
        """自动刷新循环"""
        while self.auto_refresh:
            try:
                await self.update_system_status()
                await asyncio.sleep(self.refresh_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in transparency monitor refresh loop: {e}")
                await asyncio.sleep(self.refresh_interval)
    
    async def update_system_status(self):
        """更新系统状态"""
        try:
            await self._ensure_backend_service()
            
            # 获取后端健康状态
            health_status = await self.backend_service.check_backend_health()
            
            # 模拟代理状态（实际应该从后端获取）
            active_agents = []
            if "backend" in health_status and health_status["backend"].status.value == "healthy":
                # 模拟一些活跃代理
                sample_agents = [
                    AgentStatusInfo(
                        agent_id="critic_ai_001",
                        name="Critic-AI",
                        status=AgentStatus.THINKING,
                        current_task="分析用户输入",
                        reasoning_framework="批判性思维",
                        epistemology="证伪主义"
                    ),
                    AgentStatusInfo(
                        agent_id="analyst_ai_002", 
                        name="Analyst-AI",
                        status=AgentStatus.RESPONDING,
                        current_task="生成分析报告",
                        reasoning_framework="系统分析",
                        epistemology="实证主义"
                    )
                ]
                active_agents = sample_agents
            
            # 模拟LLM调用记录
            llm_calls = []
            if active_agents:
                for i, agent in enumerate(active_agents):
                    call = LLMCall(
                        id=f"call_{datetime.now().timestamp()}_{i}",
                        model_id="gpt-4",
                        input_tokens=150 + i * 50,
                        output_tokens=300 + i * 100,
                        cost=0.002 + i * 0.001,
                        latency=1.2 + i * 0.3,
                        timestamp=datetime.now(),
                        success=True
                    )
                    llm_calls.append(call)
            
            # 计算Token使用统计
            total_input = sum(call.input_tokens for call in llm_calls)
            total_output = sum(call.output_tokens for call in llm_calls)
            total_cost = sum(call.cost for call in llm_calls)
            
            token_usage = TokenUsage(
                input_tokens=total_input,
                output_tokens=total_output,
                total_tokens=total_input + total_output,
                estimated_cost=total_cost
            ) if llm_calls else None
            
            # 更新系统状态
            self.system_status = SystemStatus(
                active_agents=active_agents,
                llm_calls=llm_calls,
                token_usage=token_usage
            )
            
            await self.refresh()
            
        except Exception as e:
            logger.error(f"Failed to update system status: {e}")
    
    async def update_status(self, status: SystemStatus):
        """更新系统状态（外部调用）"""
        self.system_status = status
        await self.refresh()
    
    def render_agent_status(self, agent: AgentStatusInfo) -> HTML:
        """渲染代理状态"""
        status_colors = {
            AgentStatus.IDLE: "gray",
            AgentStatus.THINKING: "blue",
            AgentStatus.RESPONDING: "green",
            AgentStatus.WAITING: "orange"
        }
        
        status_color = status_colors.get(agent.status, "gray")
        
        return Div(
            Div(
                Span("🤖", _class="agent-avatar"),
                Span(agent.name, _class="agent-name"),
                _class="agent-header"
            ),
            Div(
                Span(
                    agent.status.value,
                    _class=f"agent-status status-{status_color}"
                ),
                _class="agent-status-container"
            ),
            Div(
                P(f"推理框架: {agent.reasoning_framework or 'N/A'}"),
                P(f"认识论: {agent.epistemology or 'N/A'}"),
                P(f"当前任务: {agent.current_task or '空闲'}"),
                _class="agent-details"
            ),
            _class="agent-status-card"
        )
    
    def render_llm_call(self, call: LLMCall) -> HTML:
        """渲染LLM调用信息"""
        return Div(
            Div(
                Span("🤖", _class="llm-icon"),
                Span(call.model_id, _class="model-name"),
                _class="llm-header"
            ),
            Div(
                P(f"输入: {call.input_tokens} tokens"),
                P(f"输出: {call.output_tokens} tokens"),
                P(f"成本: ${call.cost:.4f}"),
                P(f"延迟: {call.latency:.2f}s"),
                _class="llm-metrics"
            ),
            Div(
                call.timestamp.strftime("%H:%M:%S"),
                _class="llm-timestamp"
            ),
            _class="llm-call-card"
        )
    
    def render_token_usage(self) -> HTML:
        """渲染Token使用统计"""
        if not self.system_status.token_usage:
            return Div(
                P("暂无Token使用数据"),
                _class="no-data"
            )
        
        usage = self.system_status.token_usage
        return Div(
            H3("📊 Token使用统计"),
            Div(
                P(f"输入Tokens: {usage.input_tokens:,}"),
                P(f"输出Tokens: {usage.output_tokens:,}"),
                P(f"总计Tokens: {usage.total_tokens:,}"),
                P(f"预估成本: ${usage.estimated_cost:.4f}"),
                _class="token-stats"
            ),
            _class="token-usage"
        )
    
    async def handle_refresh_click(self, event):
        """处理手动刷新按钮点击"""
        await self.update_system_status()
    
    async def handle_auto_refresh_toggle(self, event):
        """处理自动刷新开关"""
        self.auto_refresh = not self.auto_refresh
        if self.auto_refresh:
            await self.start_auto_refresh()
        else:
            await self.stop_auto_refresh()
        await self.refresh()
    
    def render(self) -> HTML:
        """渲染透明度监控面板"""
        # 创建控制按钮
        refresh_button = Button("🔄 刷新", _class="refresh-button")
        refresh_button.onclick = self.handle_refresh_click
        
        auto_refresh_button = Button(
            f"{'⏸️ 停止' if self.auto_refresh else '▶️ 启动'}自动刷新",
            _class="auto-refresh-button"
        )
        auto_refresh_button.onclick = self.handle_auto_refresh_toggle
        
        return Div(
            # 标题和控制区域
            Div(
                H3("🔍 系统透明度监控", _class="monitor-title"),
                Div(
                    refresh_button,
                    auto_refresh_button,
                    _class="monitor-controls"
                ),
                _class="monitor-header"
            ),
            
            # 系统状态指示器
            Div(
                Span(
                    "🟢 系统运行正常" if self.system_status.active_agents 
                    else "🟡 系统空闲",
                    _class="system-status-indicator"
                ),
                Span(
                    f"最后更新: {datetime.now().strftime('%H:%M:%S')}",
                    _class="last-update"
                ),
                _class="status-bar"
            ),
            
            # 活跃代理状态
            Div(
                H3("🤖 活跃代理"),
                Div(
                    *[self.render_agent_status(agent) 
                      for agent in self.system_status.active_agents],
                    _class="agents-container"
                ) if self.system_status.active_agents else Div(
                    P("暂无活跃代理"),
                    P("系统处于空闲状态，等待用户输入"),
                    _class="no-agents"
                ),
                _class="active-agents-section"
            ),
            
            # LLM调用监控
            Div(
                H3("📡 LLM调用"),
                Div(
                    *[self.render_llm_call(call) 
                      for call in (self.system_status.llm_calls or [])[-5:]],  # 显示最近5次调用
                    _class="llm-calls-container"
                ) if self.system_status.llm_calls else Div(
                    P("暂无LLM调用记录"),
                    P("开始对话后将显示LLM调用详情"),
                    _class="no-calls"
                ),
                _class="llm-calls-section"
            ),
            
            # Token使用统计
            self.render_token_usage(),
            
            _class="transparency-monitor"
        )

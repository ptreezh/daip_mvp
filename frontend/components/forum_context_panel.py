#!/usr/bin/env python3
"""@Time    : 2025-08-06 11:15:00
@Author  : DAIP-LIVE Team
@File    : forum_context_panel.py
@Description:
    Forum上下文面板组件 - 实时显示共识跟踪和辩论状态
"""

import logging
from typing import Any

from lona.html import HTML, Div
from lona.html.widget import Widget

# 配置日志
logger = logging.getLogger(__name__)


class ForumContextPanel(Widget):
    """Forum上下文面板组件"""
    
    def __init__(self, session_id: str):
        super().__init__()
        
        self.session_id = session_id
        self.topic = ""
        self.consensus_level = 0.0
        self.active_agents = []
        self.key_arguments = []
        self.discussion_status = "active"
        self.message_count = 0
        self.user_intervention_count = 0
        self.session_duration = 0
        
        # 创建UI元素
        self.topic_header = Div(_class="forum-topic-header")
        self.consensus_meter = Div(_class="forum-consensus-meter")
        self.agents_list = Div(_class="forum-agents-list")
        self.arguments_list = Div(_class="forum-arguments-list")
        self.status_info = Div(_class="forum-status-info")
        self.session_stats = Div(_class="forum-session-stats")
        
        # 初始化显示
        self.update_display()
        
        logger.info(f"Forum上下文面板初始化完成，会话ID: {self.session_id}")
    
    def update_context(self, context_data: dict[str, Any]):
        """更新上下文信息"""
        try:
            self.topic = context_data.get("topic", "")
            self.consensus_level = context_data.get("consensus_level", 0.0)
            self.active_agents = context_data.get("active_agents", [])
            self.key_arguments = context_data.get("key_arguments", [])
            self.discussion_status = context_data.get("status", "active")
            self.message_count = context_data.get("message_count", 0)
            self.user_intervention_count = context_data.get("user_intervention_count", 0)
            self.session_duration = context_data.get("duration", 0)
            
            # 更新显示
            self.update_display()
            
        except Exception as e:
            logger.error(f"更新上下文失败: {e}")
    
    def update_display(self):
        """更新显示内容"""
        self.update_topic_header()
        self.update_consensus_meter()
        self.update_agents_list()
        self.update_arguments_list()
        self.update_status_info()
        self.update_session_stats()
    
    def update_topic_header(self):
        """更新话题头部"""
        if not self.topic:
            topic_content = HTML("""
                <div class="topic-placeholder">
                    <span class="topic-icon">🏛️</span>
                    <span class="topic-text">等待话题开始...</span>
                </div>
            """)
        else:
            topic_content = HTML("""
                <div class="topic-active">
                    <div class="topic-title">
                        <span class="topic-icon">🎯</span>
                        <span class="topic-text">{topic}</span>
                    </div>
                    <div class="topic-meta">
                        <span class="status-badge status-{status}">{status_text}</span>
                    </div>
                </div>
            """.format(
                topic=self.topic[:50] + "..." if len(self.topic) > 50 else self.topic,
                status=self.discussion_status,
                status_text=self.get_status_text()
            ))
        
        self.topic_header.set_html(topic_content)
    
    def update_consensus_meter(self):
        """更新共识度计"""
        consensus_percentage = int(self.consensus_level * 100)
        consensus_color = self.get_consensus_color()
        consensus_description = self.get_consensus_description()
        
        meter_content = HTML(f"""
            <div class="consensus-header">
                <span class="consensus-title">📊 共识度</span>
                <span class="consensus-value">{consensus_percentage}%</span>
            </div>
            <div class="consensus-bar-container">
                <div class="consensus-bar consensus-{consensus_color}" style="width: {consensus_percentage}%"></div>
            </div>
            <div class="consensus-description">{consensus_description}</div>
        """)
        
        self.consensus_meter.set_html(meter_content)
    
    def update_agents_list(self):
        """更新活跃Agent列表"""
        if not self.active_agents:
            agents_content = HTML("""
                <div class="agents-empty">
                    <span class="agents-icon">🤖</span>
                    <span class="agents-text">暂无活跃Agent</span>
                </div>
            """)
        else:
            agents_items = []
            for i, agent in enumerate(self.active_agents[:5]):  # 最多显示5个
                agent_name = self.get_agent_display_name(agent)
                agents_items.append(f"""
                    <div class="agent-item agent-{i % 3}">
                        <span class="agent-avatar">{agent_name[:2].upper()}</span>
                        <span class="agent-name">{agent_name}</span>
                    </div>
                """)
            
            if len(self.active_agents) > 5:
                agents_items.append(f"""
                    <div class="agent-more">
                        <span class="more-text">+{len(self.active_agents) - 5} 更多</span>
                    </div>
                """)
            
            agents_content = HTML("""
                <div class="agents-list">
                    <div class="agents-header">
                        <span class="agents-title">🤖 活跃专家 ({count})</span>
                    </div>
                    <div class="agents-grid">
                        {agents_items}
                    </div>
                </div>
            """.format(
                count=len(self.active_agents),
                agents_items="".join(agents_items)
            ))
        
        self.agents_list.set_html(agents_content)
    
    def update_arguments_list(self):
        """更新关键论点列表"""
        if not self.key_arguments:
            arguments_content = HTML("""
                <div class="arguments-empty">
                    <span class="arguments-icon">💭</span>
                    <span class="arguments-text">暂无关键论点</span>
                </div>
            """)
        else:
            arguments_items = []
            for i, argument in enumerate(self.key_arguments[:3]):  # 最多显示3个
                content = argument.get("content", "")
                sender = argument.get("sender", "未知")
                importance = argument.get("importance", 0.5)
                
                arguments_items.append(f"""
                    <div class="argument-item argument-{i % 2}">
                        <div class="argument-header">
                            <span class="argument-sender">{sender}</span>
                            <span class="argument-importance">重要性: {int(importance * 100)}%</span>
                        </div>
                        <div class="argument-content">
                            {content[:80]}...
                        </div>
                    </div>
                """)
            
            arguments_content = HTML("""
                <div class="arguments-list">
                    <div class="arguments-header">
                        <span class="arguments-title">💡 关键论点</span>
                    </div>
                    <div class="arguments-items">
                        {arguments_items}
                    </div>
                </div>
            """.format(
                arguments_items="".join(arguments_items)
            ))
        
        self.arguments_list.set_html(arguments_content)
    
    def update_status_info(self):
        """更新状态信息"""
        status_items = [
            ("状态", self.get_status_text()),
            ("活跃Agent", len(self.active_agents)),
            ("消息数量", self.message_count),
            ("用户干预", self.user_intervention_count)
        ]
        
        status_content = HTML("""
            <div class="status-info">
                <div class="status-header">
                    <span class="status-title">📈 实时状态</span>
                </div>
                <div class="status-items">
                    {status_items}
                </div>
            </div>
        """.format(
            status_items="".join([
                f"""
                <div class="status-item">
                    <span class="status-label">{label}:</span>
                    <span class="status-value">{value}</span>
                </div>
                """ for label, value in status_items
            ])
        ))
        
        self.status_info.set_html(status_content)
    
    def update_session_stats(self):
        """更新会话统计"""
        duration_minutes = int(self.session_duration // 60)
        duration_seconds = int(self.session_duration % 60)
        
        stats_items = [
            ("会话时长", f"{duration_minutes}分{duration_seconds}秒"),
            ("平均共识度", f"{int(self.consensus_level * 100)}%"),
            ("参与度", self.get_participation_level()),
            ("效率", self.get_efficiency_level())
        ]
        
        stats_content = HTML("""
            <div class="session-stats">
                <div class="stats-header">
                    <span class="stats-title">📊 会话统计</span>
                </div>
                <div class="stats-items">
                    {stats_items}
                </div>
            </div>
        """.format(
            stats_items="".join([
                f"""
                <div class="stat-item">
                    <span class="stat-label">{label}:</span>
                    <span class="stat-value">{value}</span>
                </div>
                """ for label, value in stats_items
            ])
        ))
        
        self.session_stats.set_html(stats_content)
    
    def get_status_text(self) -> str:
        """获取状态文本"""
        status_map = {
            "active": "🟢 活跃",
            "paused": "⏸️ 暂停",
            "completed": "✅ 已完成",
            "error": "❌ 错误"
        }
        return status_map.get(self.discussion_status, "❓ 未知")
    
    def get_consensus_color(self) -> str:
        """获取共识度颜色"""
        if self.consensus_level >= 0.8:
            return "high"
        elif self.consensus_level >= 0.6:
            return "medium"
        elif self.consensus_level >= 0.4:
            return "low"
        else:
            return "very-low"
    
    def get_consensus_description(self) -> str:
        """获取共识度描述"""
        if self.consensus_level >= 0.8:
            return "高度共识 - 参与者意见高度一致"
        elif self.consensus_level >= 0.6:
            return "中等共识 - 基本达成一致"
        elif self.consensus_level >= 0.4:
            return "部分共识 - 存在分歧但有共同点"
        else:
            return "低共识 - 分歧较大"
    
    def get_agent_display_name(self, agent_id: str) -> str:
        """获取Agent显示名称"""
        # 简单的ID到名称映射
        name_map = {
            "technical_expert": "技术专家",
            "business_analyst": "商业分析师",
            "research_scientist": "研究科学家",
            "ethics_expert": "伦理专家",
            "legal_expert": "法律专家"
        }
        return name_map.get(agent_id, agent_id.replace("_", " ").title())
    
    def get_participation_level(self) -> str:
        """获取参与度"""
        if self.user_intervention_count >= 5:
            return "高"
        elif self.user_intervention_count >= 2:
            return "中"
        elif self.user_intervention_count >= 1:
            return "低"
        else:
            return "无"
    
    def get_efficiency_level(self) -> str:
        """获取效率水平"""
        if self.message_count > 0:
            efficiency = self.consensus_level / (self.message_count / 10)
            if efficiency >= 0.7:
                return "高"
            elif efficiency >= 0.4:
                return "中"
            else:
                return "低"
        return "无"
    
    def render(self) -> HTML:
        """渲染上下文面板"""
        return Div(
            self.topic_header,
            self.consensus_meter,
            self.agents_list,
            self.arguments_list,
            self.status_info,
            self.session_stats,
            _class="forum-context-panel"
        )
    
    def set_topic(self, topic: str):
        """设置话题"""
        self.topic = topic
        self.update_topic_header()
    
    def set_consensus_level(self, level: float):
        """设置共识度"""
        self.consensus_level = level
        self.update_consensus_meter()
    
    def set_active_agents(self, agents: list[str]):
        """设置活跃Agent"""
        self.active_agents = agents
        self.update_agents_list()
    
    def add_key_argument(self, argument: dict[str, Any]):
        """添加关键论点"""
        self.key_arguments.append(argument)
        self.update_arguments_list()
    
    def set_discussion_status(self, status: str):
        """设置讨论状态"""
        self.discussion_status = status
        self.update_status_info()
    
    def update_message_count(self, count: int):
        """更新消息数量"""
        self.message_count = count
        self.update_status_info()
    
    def update_user_intervention_count(self, count: int):
        """更新用户干预数量"""
        self.user_intervention_count = count
        self.update_status_info()
    
    def update_session_duration(self, duration: float):
        """更新会话时长"""
        self.session_duration = duration
        self.update_session_stats()
    
    def get_context_summary(self) -> dict[str, Any]:
        """获取上下文摘要"""
        return {
            "session_id": self.session_id,
            "topic": self.topic,
            "consensus_level": self.consensus_level,
            "active_agents_count": len(self.active_agents),
            "key_arguments_count": len(self.key_arguments),
            "discussion_status": self.discussion_status,
            "message_count": self.message_count,
            "user_intervention_count": self.user_intervention_count,
            "session_duration": self.session_duration
        }
    
    def reset(self):
        """重置上下文面板"""
        self.topic = ""
        self.consensus_level = 0.0
        self.active_agents = []
        self.key_arguments = []
        self.discussion_status = "active"
        self.message_count = 0
        self.user_intervention_count = 0
        self.session_duration = 0
        
        self.update_display()
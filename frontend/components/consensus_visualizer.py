#!/usr/bin/env python3
"""
@Time    : 2025-08-18 11:00:00
@Author  : DAIP-LIVE Team
@File    : consensus_visualizer.py
@Description:
    前端共识可视化组件 - 实现共识过程的可视化
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from lona.html import Widget, Div, HTML, Span, H3, P
from lona.html import Canvas

from ..services.forum_websocket_integration import forum_websocket_integration

# 配置日志
logger = logging.getLogger(__name__)


class ConsensusVisualizer(Widget):
    """共识可视化组件"""
    
    def __init__(self, session_id: str):
        super().__init__()
        
        self.session_id = session_id
        self.consensus_level = 0.0
        self.consensus_history: List[Dict[str, Any]] = []
        self.participant_agreement: Dict[str, float] = {}
        self.key_arguments: List[Dict[str, Any]] = []
        
        # 创建UI元素
        self.create_ui()
        
        # 设置WebSocket处理
        self.setup_websocket_handlers()
        
        logger.info(f"共识可视化组件初始化完成，会话ID: {session_id}")
    
    def create_ui(self):
        """创建UI元素"""
        # 共识概览头部
        self.overview_header = Div(
            H3("📊 共识分析", _class="consensus-title"),
            Div(
                Span(f"当前共识度: {self.get_consensus_percentage()}%", _class="consensus-current"),
                Span(f"状态: {self.get_consensus_status()}", _class="consensus-status"),
                _class="consensus-overview-info"
            ),
            _class="consensus-overview-header"
        )
        
        # 共识度图表
        self.consensus_chart = Div(
            Canvas(
                id="consensus-canvas",
                width=400,
                height=200,
                _class="consensus-canvas"
            ),
            _class="consensus-chart-container"
        )
        
        # 参与者一致性矩阵
        self.agreement_matrix = Div(
            H4("🤝 参与者一致性", _class="matrix-title"),
            Div(_class="matrix-placeholder"),
            _class="agreement-matrix"
        )
        
        # 关键论点展示
        self.key_arguments_panel = Div(
            H4("💭 关键论点", _class="arguments-title"),
            Div(_class="arguments-placeholder"),
            _class="key-arguments-panel"
        )
        
        # 共识时间线
        self.timeline = Div(
            H4("📈 共识时间线", _class="timeline-title"),
            Div(_class="timeline-placeholder"),
            _class="consensus-timeline"
        )
        
        # 质量指标
        self.quality_metrics = Div(
            H4("🎯 质量指标", _class="metrics-title"),
            Div(_class="metrics-placeholder"),
            _class="quality-metrics"
        )
    
    def setup_websocket_handlers(self):
        """设置WebSocket消息处理器"""
        forum_websocket_integration.register_handler(
            f"consensus_viz_{self.session_id}",
            self.handle_consensus_update
        )
    
    async def handle_consensus_update(self, data: Dict[str, Any]):
        """处理共识更新"""
        try:
            # 更新共识度
            if "consensus_level" in data:
                self.update_consensus_level(data["consensus_level"])
            
            # 更新参与者一致性
            if "participant_agreement" in data:
                self.update_participant_agreement(data["participant_agreement"])
            
            # 更新关键论点
            if "key_arguments" in data:
                self.update_key_arguments(data["key_arguments"])
            
            # 更新质量指标
            if "quality_metrics" in data:
                self.update_quality_metrics(data["quality_metrics"])
            
            # 更新显示
            self.update_display()
            
        except Exception as e:
            logger.error(f"处理共识更新失败: {e}")
    
    def update_consensus_level(self, level: float):
        """更新共识度"""
        self.consensus_level = level
        
        # 添加到历史记录
        self.consensus_history.append({
            "timestamp": datetime.now(),
            "level": level
        })
        
        # 限制历史记录长度
        if len(self.consensus_history) > 50:
            self.consensus_history = self.consensus_history[-50:]
    
    def update_participant_agreement(self, agreement: Dict[str, float]):
        """更新参与者一致性"""
        self.participant_agreement = agreement
    
    def update_key_arguments(self, arguments: List[Dict[str, Any]]):
        """更新关键论点"""
        self.key_arguments = arguments
    
    def update_quality_metrics(self, metrics: Dict[str, Any]):
        """更新质量指标"""
        self.quality_metrics = metrics
    
    def update_display(self):
        """更新显示"""
        # 更新共识概览
        self.overview_header.nodes = [
            H3("📊 共识分析", _class="consensus-title"),
            Div(
                Span(f"当前共识度: {self.get_consensus_percentage()}%", _class="consensus-current"),
                Span(f"状态: {self.get_consensus_status()}", _class="consensus-status"),
                _class="consensus-overview-info"
            )
        ]
        
        # 更新共识图表
        self.update_consensus_chart()
        
        # 更新参与者一致性矩阵
        self.update_agreement_matrix_display()
        
        # 更新关键论点
        self.update_key_arguments_display()
        
        # 更新时间线
        self.update_timeline_display()
        
        # 更新质量指标
        self.update_quality_metrics_display()
    
    def update_consensus_chart(self):
        """更新共识度图表"""
        if not self.consensus_history:
            self.consensus_chart.nodes = [
                Div(
                    P("暂无共识数据", _class="chart-placeholder"),
                    _class="consensus-chart-placeholder"
                )
            ]
            return
        
        # 创建简单的HTML图表（实际项目中可以使用更复杂的图表库）
        chart_content = self.create_simple_chart()
        self.consensus_chart.nodes = [chart_content]
    
    def create_simple_chart(self) -> HTML:
        """创建简单的HTML图表"""
        if len(self.consensus_history) < 2:
            return HTML("<div class='chart-placeholder'>需要更多数据点</div>")
        
        # 计算图表数据
        max_level = max(max(h["level"] for h in self.consensus_history), 1.0)
        chart_width = 400
        chart_height = 200
        
        # 生成SVG路径
        points = []
        for i, record in enumerate(self.consensus_history[-20:]):  # 显示最近20个点
            x = (i / 19) * chart_width if len(self.consensus_history) > 1 else 0
            y = chart_height - (record["level"] / max_level) * chart_height
            points.append(f"{x},{y}")
        
        svg_content = f"""
        <svg width="{chart_width}" height="{chart_height}" class="consensus-svg">
            <defs>
                <linearGradient id="consensusGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:#4CAF50;stop-opacity:0.8" />
                    <stop offset="100%" style="stop-color:#4CAF50;stop-opacity:0.1" />
                </linearGradient>
            </defs>
            
            <!-- 网格线 -->
            <g class="chart-grid">
                <line x1="0" y1="0" x2="0" y2="{chart_height}" stroke="#ddd" stroke-width="1"/>
                <line x1="0" y1="{chart_height}" x2="{chart_width}" y2="{chart_height}" stroke="#ddd" stroke-width="1"/>
                <line x1="0" y1="{chart_height/2}" x2="{chart_width}" y2="{chart_height/2}" stroke="#eee" stroke-width="1"/>
            </g>
            
            <!-- 共识度曲线 -->
            <polyline
                points="{' '.join(points)}"
                fill="none"
                stroke="#4CAF50"
                stroke-width="2"
                class="consensus-line"
            />
            
            <!-- 数据点 -->
            {''.join([
                f'<circle cx="{(i/19)*chart_width if len(self.consensus_history) > 1 else 0}" '
                f'cy="{chart_height - (record["level"]/max_level)*chart_height}" '
                f'r="3" fill="#4CAF50" class="data-point"/>'
                for i, record in enumerate(self.consensus_history[-20:])
            ])}
            
            <!-- 当前值标签 -->
            <text x="{chart_width-10}" y="15" text-anchor="end" class="chart-label">
                {self.get_consensus_percentage()}%
            </text>
        </svg>
        """
        
        return HTML(svg_content)
    
    def update_agreement_matrix_display(self):
        """更新参与者一致性矩阵显示"""
        if not self.participant_agreement:
            self.agreement_matrix.nodes[1] = Div(
                P("暂无参与者数据", _class="matrix-placeholder"),
                _class="agreement-matrix-placeholder"
            )
            return
        
        # 创建一致性矩阵
        participants = list(self.participant_agreement.keys())
        if len(participants) < 2:
            self.agreement_matrix.nodes[1] = Div(
                P("需要至少2个参与者", _class="matrix-placeholder"),
                _class="agreement-matrix-placeholder"
            )
            return
        
        matrix_html = "<div class='agreement-matrix-grid'>"
        
        # 表头
        matrix_html += "<div class='matrix-cell matrix-header'></div>"
        for participant in participants:
            matrix_html += f"<div class='matrix-cell matrix-header'>{participant[:8]}</div>"
        
        # 矩阵内容
        for i, p1 in enumerate(participants):
            matrix_html += f"<div class='matrix-cell matrix-header'>{p1[:8]}</div>"
            for j, p2 in enumerate(participants):
                if i == j:
                    # 对角线显示自身一致性
                    agreement = self.participant_agreement[p1]
                    color = self.get_consensus_color(agreement)
                else:
                    # 简化处理：显示平均一致性
                    agreement = (self.participant_agreement[p1] + self.participant_agreement[p2]) / 2
                    color = self.get_consensus_color(agreement)
                
                matrix_html += f"<div class='matrix-cell matrix-{color}'>{agreement:.1f}</div>"
        
        matrix_html += "</div>"
        
        self.agreement_matrix.nodes[1] = HTML(matrix_html)
    
    def update_key_arguments_display(self):
        """更新关键论点显示"""
        if not self.key_arguments:
            self.key_arguments_panel.nodes[1] = Div(
                P("暂无关键论点", _class="arguments-placeholder"),
                _class="key-arguments-placeholder"
            )
            return
        
        arguments_html = "<div class='key-arguments-list'>"
        
        for i, argument in enumerate(self.key_arguments[:5]):  # 显示前5个论点
            importance = argument.get("importance", 0.5)
            agreement = argument.get("agreement", 0.0)
            content = argument.get("content", "")[:100] + "..." if len(argument.get("content", "")) > 100 else argument.get("content", "")
            
            arguments_html += f"""
            <div class="key-argument-item">
                <div class="argument-header">
                    <span class="argument-importance">重要性: {importance:.1f}</span>
                    <span class="argument-agreement">支持度: {agreement:.1f}</span>
                </div>
                <div class="argument-content">{content}</div>
            </div>
            """
        
        arguments_html += "</div>"
        
        self.key_arguments_panel.nodes[1] = HTML(arguments_html)
    
    def update_timeline_display(self):
        """更新时间线显示"""
        if not self.consensus_history:
            self.timeline.nodes[1] = Div(
                P("暂无时间线数据", _class="timeline-placeholder"),
                _class="timeline-placeholder"
            )
            return
        
        timeline_html = "<div class='consensus-timeline-list'>"
        
        # 显示最近的重要变化
        significant_changes = []
        for i in range(1, len(self.consensus_history)):
            change = abs(self.consensus_history[i]["level"] - self.consensus_history[i-1]["level"])
            if change > 0.1:  # 10%以上的变化
                significant_changes.append(self.consensus_history[i])
        
        for change in significant_changes[-5:]:  # 显示最近5个重要变化
            level = change["level"]
            timestamp = change["timestamp"]
            color = self.get_consensus_color(level)
            
            timeline_html += f"""
            <div class='timeline-item timeline-{color}'>
                <div class='timeline-time'>{timestamp.strftime('%H:%M:%S')}</div>
                <div class='timeline-level'>共识度: {level:.1%}</div>
            </div>
            """
        
        if not significant_changes:
            timeline_html += "<div class='timeline-item'>暂无显著变化</div>"
        
        timeline_html += "</div>"
        
        self.timeline.nodes[1] = HTML(timeline_html)
    
    def update_quality_metrics_display(self):
        """更新质量指标显示"""
        if not self.quality_metrics:
            self.quality_metrics.nodes[1] = Div(
                P("暂无质量指标", _class="metrics-placeholder"),
                _class="quality-placeholder"
            )
            return
        
        metrics_html = "<div class='quality-metrics-grid'>"
        
        # 显示各种质量指标
        metrics = [
            ("参与度", self.quality_metrics.get("participation", 0.0)),
            ("多样性", self.quality_metrics.get("diversity", 0.0)),
            ("建设性", self.quality_metrics.get("constructiveness", 0.0)),
            ("相关性", self.quality_metrics.get("relevance", 0.0))
        ]
        
        for name, value in metrics:
            color = self.get_consensus_color(value)
            metrics_html += f"""
            <div class='metric-item metric-{color}'>
                <div class='metric-name'>{name}</div>
                <div class='metric-value'>{value:.1f}</div>
            </div>
            """
        
        metrics_html += "</div>"
        
        self.quality_metrics.nodes[1] = HTML(metrics_html)
    
    def get_consensus_percentage(self) -> int:
        """获取共识度百分比"""
        return int(self.consensus_level * 100)
    
    def get_consensus_status(self) -> str:
        """获取共识状态"""
        if self.consensus_level >= 0.8:
            return "高度共识"
        elif self.consensus_level >= 0.6:
            return "基本共识"
        elif self.consensus_level >= 0.4:
            return "部分共识"
        else:
            return "分歧较大"
    
    def get_consensus_color(self, level: float) -> str:
        """根据共识度获取颜色"""
        if level >= 0.8:
            return "high"
        elif level >= 0.6:
            return "medium"
        elif level >= 0.4:
            return "low"
        else:
            return "poor"
    
    def get_consensus_summary(self) -> Dict[str, Any]:
        """获取共识摘要"""
        return {
            "session_id": self.session_id,
            "current_level": self.consensus_level,
            "status": self.get_consensus_status(),
            "history_count": len(self.consensus_history),
            "participant_count": len(self.participant_agreement),
            "key_arguments_count": len(self.key_arguments)
        }
    
    def reset(self):
        """重置可视化组件"""
        self.consensus_level = 0.0
        self.consensus_history.clear()
        self.participant_agreement.clear()
        self.key_arguments.clear()
        self.quality_metrics.clear()
        self.update_display()
    
    def render(self) -> HTML:
        """渲染共识可视化组件"""
        return Div(
            self.overview_header,
            Div(
                self.consensus_chart,
                self.agreement_matrix,
                _class="consensus-top-row"
            ),
            Div(
                self.key_arguments_panel,
                self.timeline,
                _class="consensus-middle-row"
            ),
            self.quality_metrics,
            _class="consensus-visualizer"
        )
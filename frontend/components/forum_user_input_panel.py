#!/usr/bin/env python3
"""@Time    : 2025-08-06 11:00:00
@Author  : DAIP-LIVE Team
@File    : forum_user_input_panel.py
@Description:
    Forum用户输入面板组件 - 提供意图选择和输入优化功能
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

from lona.html import HTML, Button, Div, Select, Span, TextArea
from lona.html.widget import Widget

from ..services.dual_entrance_websocket_manager import dual_entrance_websocket_manager

# 配置日志
logger = logging.getLogger(__name__)


class ForumUserInputPanel(Widget):
    """Forum用户输入面板组件"""
    
    def __init__(self, session_id: str):
        super().__init__()
        
        self.session_id = session_id
        self.input_text = ""
        self.selected_intent = "comment"
        self.optimized_preview = ""
        self.optimization_confidence = 0.0
        self.is_optimizing = False
        
        # 意图类型定义
        self.intent_types = [
            {"value": "comment", "label": "💬 评论", "description": "对讨论内容发表看法"},
            {"value": "question", "label": "❓ 提问", "description": "向专家们提问"},
            {"value": "suggestion", "label": "💡 建议", "description": "提出改进建议"},
            {"value": "correction", "label": "✏️ 纠正", "description": "纠正错误观点"}
        ]
        
        # 创建UI元素
        self.intent_selector = Select(
            _class="forum-intent-selector",
            values=[(intent["value"], intent["label"]) for intent in self.intent_types]
        )
        
        self.input_field = TextArea(
            placeholder="输入您的观点、问题或建议...",
            _class="forum-input-textarea",
            rows=3
        )
        
        self.optimize_button = Button(
            "🔄 优化输入",
            _class="btn btn-secondary forum-optimize-button"
        )
        
        self.send_button = Button(
            "📤 发送",
            _class="btn btn-primary forum-send-button"
        )
        
        self.preview_area = Div(
            _class="forum-optimization-preview"
        )
        
        self.intent_description = Div(
            _class="forum-intent-description"
        )
        
        # 绑定事件
        self.intent_selector.handle_change = self.handle_intent_change
        self.input_field.handle_change = self.handle_input_change
        self.optimize_button.handle_click = self.handle_optimize_click
        self.send_button.handle_click = self.handle_send_click
        
        # 初始化意图描述
        self.update_intent_description()
        
        logger.info(f"Forum用户输入面板初始化完成，会话ID: {self.session_id}")
    
    def handle_intent_change(self, event):
        """处理意图选择变化"""
        self.selected_intent = event.data
        self.update_intent_description()
        self.clear_optimization_preview()
    
    def handle_input_change(self, event):
        """处理输入变化"""
        self.input_text = event.data
        self.clear_optimization_preview()
        
        # 自动优化（当输入足够长时）
        if len(self.input_text.strip()) > 10:
            asyncio.create_task(self.auto_optimize())
    
    def handle_optimize_click(self, event):
        """手动优化点击"""
        if self.input_text.strip():
            asyncio.create_task(self.optimize_input())
    
    def handle_send_click(self, event):
        """发送点击"""
        if self.input_text.strip():
            asyncio.create_task(self.send_input())
    
    def update_intent_description(self):
        """更新意图描述"""
        intent_info = next((intent for intent in self.intent_types if intent["value"] == self.selected_intent), None)
        
        if intent_info:
            self.intent_description.set_text(intent_info["description"])
    
    def clear_optimization_preview(self):
        """清空优化预览"""
        self.optimized_preview = ""
        self.optimization_confidence = 0.0
        self.preview_area.set_text("")
    
    async def auto_optimize(self):
        """自动优化输入"""
        try:
            # 延迟一段时间避免频繁请求
            await asyncio.sleep(1.0)
            
            # 检查输入是否还有效
            if len(self.input_text.strip()) > 10 and not self.optimized_preview:
                await self.optimize_input()
                
        except Exception as e:
            logger.error(f"自动优化失败: {e}")
    
    async def optimize_input(self):
        """优化用户输入"""
        try:
            if self.is_optimizing:
                return
            
            self.is_optimizing = True
            self.optimize_button.disabled = True
            self.optimize_button.value = "⏳ 优化中..."
            
            # 发送优化请求
            optimization_request = {
                "type": "optimize_user_input",
                "input": self.input_text,
                "intent": self.selected_intent,
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat()
            }
            
            await dual_entrance_websocket_manager.send_message(optimization_request)
            
            # 模拟优化过程（实际应该等待后端响应）
            await asyncio.sleep(1.0)
            
            # 这里应该接收后端的优化结果
            # 现在使用模拟优化
            optimized_result = await self.simulate_optimization()
            
            self.optimized_preview = optimized_result["optimized_text"]
            self.optimization_confidence = optimized_result["confidence"]
            
            # 更新预览区域
            self.update_optimization_preview()
            
        except Exception as e:
            logger.error(f"优化输入失败: {e}")
            self.preview_area.set_text("❌ 优化失败，请重试")
        finally:
            self.is_optimizing = False
            self.optimize_button.disabled = False
            self.optimize_button.value = "🔄 优化输入"
    
    async def simulate_optimization(self) -> dict[str, Any]:
        """模拟优化结果（实际应该从后端获取）"""
        original_text = self.input_text.strip()
        
        # 基于意图类型的简单优化逻辑
        if self.selected_intent == "question":
            if not original_text.endswith("?"):
                optimized_text = original_text + "?"
            else:
                optimized_text = original_text
        elif self.selected_intent == "suggestion":
            if not original_text.startswith("我建议"):
                optimized_text = f"我建议{original_text}"
            else:
                optimized_text = original_text
        elif self.selected_intent == "correction":
            if original_text.startswith("不对") or original_text.startswith("错误"):
                optimized_text = f"需要纠正的是：{original_text}"
            else:
                optimized_text = original_text
        else:  # comment
            optimized_text = original_text
        
        return {
            "optimized_text": optimized_text,
            "confidence": 0.85,
            "improvements": ["语气优化", "表达更清晰"],
            "original_text": original_text
        }
    
    def update_optimization_preview(self):
        """更新优化预览"""
        if not self.optimized_preview:
            self.preview_area.set_text("")
            return
        
        confidence_percentage = int(self.optimization_confidence * 100)
        confidence_color = "success" if confidence_percentage >= 80 else "warning" if confidence_percentage >= 60 else "danger"
        
        preview_content = HTML("""
            <div class="optimization-header">
                <span class="optimization-title">🎯 优化建议</span>
                <span class="optimization-confidence badge badge-{confidence_color}">{confidence}%</span>
            </div>
            <div class="optimization-content">
                <div class="original-text">
                    <strong>原始输入:</strong> {original_text}
                </div>
                <div class="optimized-text">
                    <strong>优化后:</strong> {optimized_text}
                </div>
            </div>
        """.format(
            confidence_color=confidence_color,
            confidence=confidence_percentage,
            original_text=self.input_text[:100] + "..." if len(self.input_text) > 100 else self.input_text,
            optimized_text=self.optimized_preview[:100] + "..." if len(self.optimized_preview) > 100 else self.optimized_preview
        ))
        
        self.preview_area.set_html(preview_content)
    
    async def send_input(self):
        """发送输入"""
        try:
            # 使用优化后的输入（如果有）
            final_input = self.optimized_preview if self.optimized_preview else self.input_text
            
            # 创建用户干预消息
            user_intervention = {
                "type": "forum_user_intervention",
                "message": {
                    "content": final_input,
                    "intent": self.selected_intent,
                    "timestamp": datetime.now().isoformat(),
                    "optimized": bool(self.optimized_preview)
                },
                "session_id": self.session_id
            }
            
            # 发送到后端
            await dual_entrance_websocket_manager.send_message(user_intervention)
            
            # 清空输入
            self.input_text = ""
            self.input_field.value = ""
            self.clear_optimization_preview()
            
            logger.info(f"用户输入已发送: {self.session_id}")
            
        except Exception as e:
            logger.error(f"发送输入失败: {e}")
    
    def render(self) -> HTML:
        """渲染用户输入面板"""
        return Div(
            Div(
                Span("💭 输入意图:", _class="input-label"),
                self.intent_selector,
                self.intent_description,
                _class="forum-intent-section"
            ),
            Div(
                Span("📝 您的观点:", _class="input-label"),
                self.input_field,
                _class="forum-input-section"
            ),
            Div(
                self.optimize_button,
                self.send_button,
                _class="forum-button-section"
            ),
            self.preview_area,
            _class="forum-user-input-panel"
        )
    
    def set_input_text(self, text: str):
        """设置输入文本"""
        self.input_text = text
        self.input_field.value = text
        self.clear_optimization_preview()
    
    def get_current_input(self) -> dict[str, Any]:
        """获取当前输入状态"""
        return {
            "input_text": self.input_text,
            "selected_intent": self.selected_intent,
            "optimized_preview": self.optimized_preview,
            "optimization_confidence": self.optimization_confidence,
            "is_optimizing": self.is_optimizing
        }
    
    def reset(self):
        """重置输入面板"""
        self.input_text = ""
        self.selected_intent = "comment"
        self.optimized_preview = ""
        self.optimization_confidence = 0.0
        self.is_optimizing = False
        
        self.input_field.value = ""
        self.intent_selector.value = "comment"
        self.clear_optimization_preview()
        self.update_intent_description()
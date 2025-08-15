#!/usr/bin/env python3
"""智能记忆管理面板组件

基于MemAgent提供记忆管理界面，支持记忆查看、编辑和组织
"""

from enum import Enum
from typing import Any, Optional

from lona.html import H3, HTML, Button, Div, Option, P, Select, Span, TextInput
from lona.html.widget import Widget

from .base_components import Button as CustomButton
from .base_components import ButtonVariant, Input, Modal


class MemoryType(str, Enum):
    """记忆类型枚举"""
    EPISODIC = "episodic"
    SEMANTIC = "semantic" 
    PROCEDURAL = "procedural"
    META = "meta"


class MemoryPanel(Widget):
    """智能记忆管理面板"""
    
    def __init__(self, memory_service):
        super().__init__()
        
        self.memory_service = memory_service
        self.current_memories: list[dict[str, Any]] = []
        self.selected_memory: Optional[dict[str, Any]] = None
        self.filter_type: Optional[MemoryType] = None
        self.search_query: str = ""
        
        # 创建UI组件
        self._create_components()
        
        # 加载初始数据
        self._load_memories()
    
    def _create_components(self):
        """创建UI组件"""
        # 搜索输入框
        self.search_input = Input(
            placeholder="搜索记忆内容...",
            onkeydown=self._handle_search_keydown
        )
        
        # 类型过滤器
        self.type_filter = Select()
        self.type_filter.append(Option("所有类型", value=""))
        for mem_type in MemoryType:
            self.type_filter.append(Option(
                self._get_memory_type_display(mem_type), 
                value=mem_type.value
            ))
        
        # 搜索按钮
        self.search_button = CustomButton(
            "搜索", 
            variant=ButtonVariant.PRIMARY,
            onclick=self._handle_search
        )
        
        # 新建记忆按钮
        self.new_memory_button = CustomButton(
            "新建记忆",
            variant=ButtonVariant.SUCCESS, 
            onclick=self._handle_new_memory
        )
        
        # 记忆编辑模态框
        self.edit_modal = Modal(
            title="编辑记忆",
            size="large",
            closable=True
        )
    
    def _get_memory_type_display(self, memory_type: MemoryType) -> str:
        """获取记忆类型显示名称"""
        type_names = {
            MemoryType.EPISODIC: "📅 情节记忆",
            MemoryType.SEMANTIC: "📚 语义记忆", 
            MemoryType.PROCEDURAL: "⚙️ 程序记忆",
            MemoryType.META: "🧠 元认知记忆"
        }
        return type_names.get(memory_type, memory_type.value)
    
    async def _load_memories(self):
        """加载记忆数据"""
        try:
            # 模拟从MemAgent加载记忆数据
            self.current_memories = [
                {
                    "id": "mem_001",
                    "content": "用户询问了关于AI伦理的问题，特别关注算法公平性",
                    "memory_type": MemoryType.EPISODIC,
                    "source_id": "user_001",
                    "importance": 0.85,
                    "recency": 0.9,
                    "created_at": "2025-01-15 14:30:00",
                    "access_count": 3,
                    "related_memories": ["mem_002", "mem_005"]
                },
                {
                    "id": "mem_002", 
                    "content": "AI伦理的核心原则包括公平性、透明性、可解释性和问责制",
                    "memory_type": MemoryType.SEMANTIC,
                    "source_id": "system",
                    "importance": 0.95,
                    "recency": 0.8,
                    "created_at": "2025-01-15 14:25:00",
                    "access_count": 8,
                    "related_memories": ["mem_001", "mem_003"]
                },
                {
                    "id": "mem_003",
                    "content": "评估AI系统伦理风险的步骤：1.识别利益相关者 2.评估潜在影响 3.制定缓解措施",
                    "memory_type": MemoryType.PROCEDURAL,
                    "source_id": "assistant",
                    "importance": 0.8,
                    "recency": 0.7,
                    "created_at": "2025-01-15 14:20:00", 
                    "access_count": 5,
                    "related_memories": ["mem_002"]
                }
            ]
        except Exception as e:
            print(f"加载记忆失败: {e}")
    
    async def _handle_search_keydown(self, event):
        """处理搜索框按键事件"""
        if event.key == 'Enter':
            await self._handle_search(event)
    
    async def _handle_search(self, event):
        """处理搜索操作"""
        self.search_query = self.search_input.current_value
        filter_type = self.type_filter.value
        self.filter_type = MemoryType(filter_type) if filter_type else None
        
        # 过滤记忆
        await self._filter_memories()
    async def _filter_memories(self):
        """根据搜索条件过滤记忆"""
        filtered = []
        
        for memory in self.current_memories:
            # 类型过滤
            if self.filter_type and memory["memory_type"] != self.filter_type:
                continue
            
            # 内容搜索
            if self.search_query and self.search_query.lower() not in memory["content"].lower():
                continue
            
            filtered.append(memory)
        
        # 按重要性和时近性排序
        filtered.sort(key=lambda m: (m["importance"] + m["recency"]) / 2, reverse=True)
        self.current_memories = filtered
    
    async def _handle_new_memory(self, event):
        """处理新建记忆"""
        # 创建新记忆表单
        self.edit_modal.clear_content()
        self.edit_modal.add_content(
            self._create_memory_form()
        )
        self.edit_modal.open()
    async def _handle_edit_memory(self, memory_id: str):
        """处理编辑记忆"""
        self.selected_memory = next(
            (m for m in self.current_memories if m["id"] == memory_id), 
            None
        )
        
        if self.selected_memory:
            self.edit_modal.clear_content()
            self.edit_modal.add_content(
                self._create_memory_form(self.selected_memory)
            )
            self.edit_modal.open()
    async def _handle_delete_memory(self, memory_id: str):
        """处理删除记忆"""
        self.current_memories = [
            m for m in self.current_memories if m["id"] != memory_id
        ]
    def _create_memory_form(self, memory: Optional[dict[str, Any]] = None) -> HTML:
        """创建记忆编辑表单"""
        is_edit = memory is not None
        
        # 内容输入框
        content_input = TextInput(
            placeholder="输入记忆内容...",
            value=memory["content"] if is_edit else "",
            style="width: 100%; min-height: 100px;"
        )
        
        # 类型选择
        type_select = Select(style="width: 100%;")
        for mem_type in MemoryType:
            selected = is_edit and memory["memory_type"] == mem_type
            type_select.append(Option(
                self._get_memory_type_display(mem_type),
                value=mem_type.value,
                selected=selected
            ))
        
        # 重要性滑块（简化为输入框）
        importance_input = TextInput(
            placeholder="重要性 (0.0-1.0)",
            value=str(memory["importance"]) if is_edit else "0.5",
            type="number",
            min="0",
            max="1",
            step="0.1",
            style="width: 100%;"
        )
        
        return Div(
            # 内容
            Div(
                P("记忆内容:", style="font-weight: 600; margin-bottom: 5px;"),
                content_input,
                style="margin-bottom: 15px;"
            ),
            
            # 类型
            Div(
                P("记忆类型:", style="font-weight: 600; margin-bottom: 5px;"),
                type_select,
                style="margin-bottom: 15px;"
            ),
            
            # 重要性
            Div(
                P("重要性:", style="font-weight: 600; margin-bottom: 5px;"),
                importance_input,
                style="margin-bottom: 20px;"
            ),
            
            # 按钮
            Div(
                Button(
                    "保存" if is_edit else "创建",
                    _class="btn btn-success",
                    style="margin-right: 10px;"
                ),
                Button(
                    "取消",
                    _class="btn btn-secondary",
                    onclick=lambda e: self.edit_modal.close()
                ),
                style="text-align: right;"
            )
        )
    
    def _create_memory_card(self, memory: dict[str, Any]) -> HTML:
        """创建记忆卡片"""
        memory_type_display = self._get_memory_type_display(memory["memory_type"])
        
        # 重要性和时近性指示器
        importance_color = "success" if memory["importance"] > 0.7 else "warning" if memory["importance"] > 0.4 else "secondary"
        recency_color = "success" if memory["recency"] > 0.7 else "warning" if memory["recency"] > 0.4 else "secondary"
        
        return Div(
            # 卡片头部
            Div(
                Div(
                    Span(memory_type_display, style="font-weight: 600;"),
                    Span(f"ID: {memory['id']}", style="font-size: 0.8rem; color: #6c757d; margin-left: 10px;"),
                    style="flex: 1;"
                ),
                Div(
                    Button(
                        "编辑",
                        _class="btn btn-outline-primary btn-sm",
                        onclick=lambda e: self._handle_edit_memory(memory["id"]),
                        style="margin-right: 5px;"
                    ),
                    Button(
                        "删除", 
                        _class="btn btn-outline-danger btn-sm",
                        onclick=lambda e: self._handle_delete_memory(memory["id"])
                    ),
                    style="display: flex; gap: 5px;"
                ),
                style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;"
            ),
            
            # 记忆内容
            Div(
                P(memory["content"], style="line-height: 1.4; margin-bottom: 10px;"),
                style="margin-bottom: 15px;"
            ),
            
            # 元数据
            Div(
                Div(
                    Span("重要性:", style="font-weight: 500; margin-right: 5px;"),
                    Span(
                        f"{memory['importance']:.2f}",
                        _class=f"badge badge-{importance_color}"
                    ),
                    style="margin-right: 15px;"
                ),
                Div(
                    Span("时近性:", style="font-weight: 500; margin-right: 5px;"),
                    Span(
                        f"{memory['recency']:.2f}",
                        _class=f"badge badge-{recency_color}"
                    ),
                    style="margin-right: 15px;"
                ),
                Div(
                    Span("访问次数:", style="font-weight: 500; margin-right: 5px;"),
                    Span(str(memory["access_count"]), _class="badge badge-info"),
                    style="margin-right: 15px;"
                ),
                style="display: flex; flex-wrap: wrap; margin-bottom: 10px;"
            ),
            
            # 时间和来源信息
            Div(
                P(f"来源: {memory['source_id']}", style="font-size: 0.8rem; color: #6c757d; margin: 0;"),
                P(f"创建时间: {memory['created_at']}", style="font-size: 0.8rem; color: #6c757d; margin: 0;"),
                style="border-top: 1px solid #e9ecef; padding-top: 8px;"
            ),
            
            # 相关记忆
            Div(
                P("相关记忆:", style="font-weight: 500; margin-bottom: 5px;") if memory.get("related_memories") else Div(),
                *[
                    Span(
                        related_id,
                        _class="badge badge-light",
                        style="margin-right: 5px; margin-bottom: 3px; cursor: pointer;",
                        title=f"点击查看记忆 {related_id}"
                    )
                    for related_id in memory.get("related_memories", [])
                ] if memory.get("related_memories") else [],
                style="margin-top: 10px;" if memory.get("related_memories") else "display: none;"
            ),
            
            _class="memory-card",
            style="border: 1px solid #e9ecef; border-radius: 8px; padding: 15px; margin-bottom: 15px; background: #fff;"
        )
    
    def render(self) -> HTML:
        """渲染记忆管理面板"""
        return Div(
            H3("🧠 智能记忆管理", _class="panel-title", style="margin-bottom: 20px;"),
            
            # 搜索和过滤区域
            Div(
                Div(
                    self.search_input.render(),
                    style="flex: 1; margin-right: 10px;"
                ),
                Div(
                    self.type_filter,
                    style="width: 150px; margin-right: 10px;"
                ),
                self.search_button.render(),
                self.new_memory_button.render(),
                style="display: flex; align-items: center; margin-bottom: 20px; gap: 10px;"
            ),
            
            # 记忆列表
            Div(
                *[self._create_memory_card(memory) for memory in self.current_memories],
                style="min-height: 200px;"
            ),
            
            # 编辑模态框
            self.edit_modal.render(),
            
            _class="memory-panel"
        )
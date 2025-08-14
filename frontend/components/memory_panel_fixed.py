#!/usr/bin/env python3
"""智能记忆管理面板组件（修复版）

基于MemAgent提供记忆管理界面，支持记忆查看、编辑和组织
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from lona.html import H3, HTML, Button, Div, Option, P, Select, Span, TextInput
from lona.html.widget import Widget


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
        self.current_memories: List[Dict[str, Any]] = []
        self.selected_memory: Optional[Dict[str, Any]] = None
        self.filter_type: Optional[MemoryType] = None
        self.search_query: str = ""

        # 创建UI组件
        self._create_components()

        # 加载初始数据
        self._load_memories()

    def _create_components(self):
        """创建UI组件"""
        # 搜索输入框
        self.search_input = TextInput(
            placeholder="搜索记忆内容...",
            _class="form-input"
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
        self.search_button = Button(
            "搜索",
            _class="btn btn-primary"
        )

        # 新建记忆按钮
        self.new_memory_button = Button(
            "新建记忆",
            _class="btn btn-success"
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
                }
            ]
        except Exception as e:
            print(f"加载记忆失败: {e}")

    def _create_memory_card(self, memory: Dict[str, Any]) -> HTML:
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
                        style="margin-right: 5px;"
                    ),
                    Button(
                        "删除",
                        _class="btn btn-outline-danger btn-sm"
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
                    self.search_input,
                    style="flex: 1; margin-right: 10px;"
                ),
                Div(
                    self.type_filter,
                    style="width: 150px; margin-right: 10px;"
                ),
                self.search_button,
                self.new_memory_button,
                style="display: flex; align-items: center; margin-bottom: 20px; gap: 10px;"
            ),

            # 记忆列表
            Div(
                *[self._create_memory_card(memory) for memory in self.current_memories],
                style="min-height: 200px;"
            ),

            _class="memory-panel"
        )

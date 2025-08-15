#!/usr/bin/env python3
"""基础UI组件库

提供Personal Intelligence Hub使用的通用Lona组件
包括按钮、输入框、面板、卡片等基础组件
"""

from collections.abc import Callable
from enum import Enum
from typing import Any, Optional

from lona.html import H3, HTML, Div, P, Span
from lona.html import Button as LonaButton
from lona.html import TextInput as LonaInput
from lona.html.widget import Widget


class ButtonVariant(Enum):
    """按钮变体枚举"""
    PRIMARY = "primary"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"
    SECONDARY = "secondary"


class ButtonSize(Enum):
    """按钮尺寸枚举"""
    SMALL = "sm"
    MEDIUM = "md"
    LARGE = "lg"


class Button(Widget):
    """通用按钮组件"""
    
    def __init__(self, text: str, variant: ButtonVariant = ButtonVariant.PRIMARY, 
                 size: ButtonSize = ButtonSize.MEDIUM, disabled: bool = False,
                 onclick: Optional[Callable] = None, **kwargs):
        super().__init__()
        
        self.text = text
        self.variant = variant
        self.size = size
        self.disabled = disabled
        self.onclick = onclick
        self.kwargs = kwargs
        
        # 创建底层Lona按钮
        self.button = LonaButton(
            text,
            disabled=disabled,
            _class=f"btn btn-{variant.value} btn-{size.value}",
            **kwargs
        )
        
        if onclick:
            self.button.addEventListener('click', onclick)
    
    def set_loading(self, loading: bool = True):
        """设置加载状态"""
        if loading:
            self.button.disabled = True
            self.button.innerHTML = f'<span class="loading"></span> {self.text}'
        else:
            self.button.disabled = self.disabled
            self.button.innerHTML = self.text
    
    def render(self) -> HTML:
        return self.button


class Input(Widget):
    """通用输入框组件"""
    
    def __init__(self, placeholder: str = "", value: str = "", 
                 input_type: str = "text", disabled: bool = False,
                 onchange: Optional[Callable] = None, 
                 onkeydown: Optional[Callable] = None, **kwargs):
        super().__init__()
        
        self.placeholder = placeholder
        self.value = value
        self.input_type = input_type
        self.disabled = disabled
        self.onchange = onchange
        self.onkeydown = onkeydown
        self.kwargs = kwargs
        
        # 创建底层Lona输入框
        self.input = LonaInput(
            placeholder=placeholder,
            value=value,
            type=input_type,
            disabled=disabled,
            _class="form-input",
            **kwargs
        )
        
        if onchange:
            self.input.addEventListener('change', onchange)
        if onkeydown:
            self.input.addEventListener('keydown', onkeydown)
    
    @property
    def current_value(self) -> str:
        """获取当前输入值"""
        return self.input.value
    
    def clear(self):
        """清空输入框"""
        self.input.value = ""
    
    def focus(self):
        """聚焦输入框"""
        # Lona会在客户端执行focus
        pass
    
    def render(self) -> HTML:
        return self.input


class Panel(Widget):
    """通用面板组件"""
    
    def __init__(self, title: Optional[str] = None, 
                 border_color: Optional[str] = None,
                 collapsible: bool = False, collapsed: bool = False,
                 **kwargs):
        super().__init__()
        
        self.title = title
        self.border_color = border_color
        self.collapsible = collapsible
        self.collapsed = collapsed
        self.kwargs = kwargs
        self.content_items: list[HTML] = []
        
        # 面板样式类
        panel_classes = ["panel"]
        if border_color:
            panel_classes.append(f"panel-{border_color}")
        
        self.panel_div = Div(_class=" ".join(panel_classes), **kwargs)
    
    def add_content(self, *items: HTML):
        """添加内容到面板"""
        self.content_items.extend(items)
    
    def clear_content(self):
        """清空面板内容"""
        self.content_items.clear()
    
    def toggle_collapse(self):
        """切换折叠状态"""
        if self.collapsible:
            self.collapsed = not self.collapsed
    
    def render(self) -> HTML:
        panel_content = []
        
        # 添加标题
        if self.title:
            title_div = Div(
                H3(self.title),
                _class="panel-header"
            )
            if self.collapsible:
                title_div.addEventListener('click', lambda e: self.toggle_collapse())
                title_div._class += " collapsible"
            panel_content.append(title_div)
        
        # 添加内容（如果未折叠）
        if not self.collapsed:
            content_div = Div(
                *self.content_items,
                _class="panel-content"
            )
            panel_content.append(content_div)
        
        self.panel_div.clear()
        self.panel_div.append(*panel_content)
        
        return self.panel_div


class Card(Widget):
    """卡片组件"""
    
    def __init__(self, title: Optional[str] = None, 
                 subtitle: Optional[str] = None,
                 clickable: bool = False,
                 onclick: Optional[Callable] = None, **kwargs):
        super().__init__()
        
        self.title = title
        self.subtitle = subtitle
        self.clickable = clickable
        self.onclick = onclick
        self.kwargs = kwargs
        self.content_items: list[HTML] = []
        
        # 卡片样式类
        card_classes = ["card"]
        if clickable:
            card_classes.append("card-clickable")
        
        self.card_div = Div(_class=" ".join(card_classes), **kwargs)
        
        if clickable and onclick:
            self.card_div.addEventListener('click', onclick)
    
    def add_content(self, *items: HTML):
        """添加内容到卡片"""
        self.content_items.extend(items)
    
    def render(self) -> HTML:
        card_content = []
        
        # 添加标题和副标题
        if self.title or self.subtitle:
            header_content = []
            if self.title:
                header_content.append(H3(self.title, _class="card-title"))
            if self.subtitle:
                header_content.append(P(self.subtitle, _class="card-subtitle"))
            
            card_content.append(Div(*header_content, _class="card-header"))
        
        # 添加内容
        if self.content_items:
            card_content.append(Div(*self.content_items, _class="card-body"))
        
        self.card_div.clear()
        self.card_div.append(*card_content)
        
        return self.card_div


class Badge(Widget):
    """徽章组件"""
    
    def __init__(self, text: str, variant: str = "info", **kwargs):
        super().__init__()
        
        self.text = text
        self.variant = variant
        self.kwargs = kwargs
    
    def render(self) -> HTML:
        return Span(
            self.text,
            _class=f"badge badge-{self.variant}",
            **self.kwargs
        )


class StatusIndicator(Widget):
    """状态指示器组件"""
    
    def __init__(self, status: str, text: Optional[str] = None, **kwargs):
        super().__init__()
        
        self.status = status
        self.text = text or status.replace('_', ' ').title()
        self.kwargs = kwargs
        
        # 状态颜色映射
        self.status_colors = {
            'idle': 'gray',
            'active': 'green',
            'thinking': 'blue',
            'responding': 'green',
            'waiting': 'orange',
            'error': 'red',
            'offline': 'gray'
        }
    
    def render(self) -> HTML:
        color = self.status_colors.get(self.status, 'gray')
        
        return Div(
            Span(_class=f"status-dot status-{color}"),
            Span(self.text, _class="status-text"),
            _class="status-indicator",
            **self.kwargs
        )


class ProgressBar(Widget):
    """进度条组件"""
    
    def __init__(self, value: float = 0.0, max_value: float = 100.0,
                 show_text: bool = True, variant: str = "primary", **kwargs):
        super().__init__()
        
        self.value = max(0, min(value, max_value))
        self.max_value = max_value
        self.show_text = show_text
        self.variant = variant
        self.kwargs = kwargs
    
    def update_progress(self, value: float):
        """更新进度值"""
        self.value = max(0, min(value, self.max_value))
    
    def render(self) -> HTML:
        percentage = (self.value / self.max_value) * 100
        
        progress_content = [
            Div(
                _class=f"progress-fill progress-{self.variant}",
                style=f"width: {percentage}%"
            )
        ]
        
        if self.show_text:
            progress_content.append(
                Span(
                    f"{percentage:.1f}%",
                    _class="progress-text"
                )
            )
        
        return Div(
            *progress_content,
            _class="progress-bar",
            **self.kwargs
        )


class LoadingSpinner(Widget):
    """加载动画组件"""
    
    def __init__(self, size: str = "medium", text: Optional[str] = None, **kwargs):
        super().__init__()
        
        self.size = size
        self.text = text
        self.kwargs = kwargs
    
    def render(self) -> HTML:
        spinner_content = [
            Div(_class=f"spinner spinner-{self.size}")
        ]
        
        if self.text:
            spinner_content.append(
                P(self.text, _class="spinner-text")
            )
        
        return Div(
            *spinner_content,
            _class="loading-spinner",
            **self.kwargs
        )


class Tooltip(Widget):
    """工具提示组件"""
    
    def __init__(self, content: HTML, tooltip_text: str, 
                 position: str = "top", **kwargs):
        super().__init__()
        
        self.content = content
        self.tooltip_text = tooltip_text
        self.position = position
        self.kwargs = kwargs
    
    def render(self) -> HTML:
        return Div(
            self.content,
            Div(
                self.tooltip_text,
                _class=f"tooltip tooltip-{self.position}"
            ),
            _class="tooltip-container",
            **self.kwargs
        )


class Modal(Widget):
    """模态对话框组件"""
    
    def __init__(self, title: str, show: bool = False, 
                 closable: bool = True, size: str = "medium", **kwargs):
        super().__init__()
        
        self.title = title
        self.show = show
        self.closable = closable
        self.size = size
        self.kwargs = kwargs
        self.content_items: list[HTML] = []
        self.footer_items: list[HTML] = []
    
    def add_content(self, *items: HTML):
        """添加内容到模态框"""
        self.content_items.extend(items)
    
    def add_footer(self, *items: HTML):
        """添加底部按钮到模态框"""
        self.footer_items.extend(items)
    
    def open(self):
        """打开模态框"""
        self.show = True
    
    def close(self):
        """关闭模态框"""
        self.show = False
    
    def render(self) -> HTML:
        if not self.show:
            return Div()
        
        modal_content = [
            # 模态框头部
            Div(
                H3(self.title, _class="modal-title"),
                Button("×", variant=ButtonVariant.SECONDARY, 
                      onclick=lambda e: self.close()) if self.closable else Div(),
                _class="modal-header"
            ),
            
            # 模态框内容
            Div(
                *self.content_items,
                _class="modal-body"
            )
        ]
        
        # 模态框底部
        if self.footer_items:
            modal_content.append(
                Div(
                    *self.footer_items,
                    _class="modal-footer"
                )
            )
        
        return Div(
            Div(
                Div(
                    *modal_content,
                    _class=f"modal-content modal-{self.size}"
                ),
                _class="modal-dialog"
            ),
            _class="modal-overlay",
            **self.kwargs
        )


class Tabs(Widget):
    """标签页组件"""
    
    def __init__(self, **kwargs):
        super().__init__()
        
        self.kwargs = kwargs
        self.tabs: list[dict[str, Any]] = []
        self.active_tab = 0
    
    def add_tab(self, title: str, content: HTML, disabled: bool = False):
        """添加标签页"""
        self.tabs.append({
            'title': title,
            'content': content,
            'disabled': disabled
        })
    
    def set_active_tab(self, index: int):
        """设置活跃标签页"""
        if 0 <= index < len(self.tabs) and not self.tabs[index]['disabled']:
            self.active_tab = index
    
    def render(self) -> HTML:
        if not self.tabs:
            return Div()
        
        # 标签页头部
        tab_headers = []
        for i, tab in enumerate(self.tabs):
            tab_classes = ["tab-header"]
            if i == self.active_tab:
                tab_classes.append("active")
            if tab['disabled']:
                tab_classes.append("disabled")
            
            tab_headers.append(
                Div(
                    tab['title'],
                    _class=" ".join(tab_classes),
                    onclick=lambda e, idx=i: self.set_active_tab(idx) if not tab['disabled'] else None
                )
            )
        
        # 当前标签页内容
        active_content = self.tabs[self.active_tab]['content'] if self.tabs else Div()
        
        return Div(
            Div(
                *tab_headers,
                _class="tab-headers"
            ),
            Div(
                active_content,
                _class="tab-content"
            ),
            _class="tabs-container",
            **self.kwargs
        )

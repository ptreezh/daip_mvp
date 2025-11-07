"""
TUI组件基类示例

这个文件展示了TUI组件基类的核心设计，
用于指导实际的组件实现工作。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
import logging

from textual.app import ComposeResult
from textual.widgets import Widget
from textual.containers import Container
from textual.reactive import reactive
from textual.message import Message

logger = logging.getLogger(__name__)


@dataclass
class ComponentState:
    """组件状态数据类"""
    id: str
    visible: bool = True
    enabled: bool = True
    focusable: bool = True
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class ComponentEvent(Message):
    """组件事件基类"""

    def __init__(self, component_id: str, event_type: str, data: Dict[str, Any] = None):
        self.component_id = component_id
        self.event_type = event_type
        self.data = data or {}
        super().__init__()


class StateChangedEvent(ComponentEvent):
    """状态变更事件"""

    def __init__(self, component_id: str, old_state: ComponentState, new_state: ComponentState):
        super().__init__(component_id, "state_changed", {
            "old_state": old_state,
            "new_state": new_state
        })


class TUIComponent(ABC):
    """TUI组件抽象基类"""

    def __init__(self, component_id: str, **kwargs):
        self.component_id = component_id
        self._state = ComponentState(id=component_id, **kwargs)
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._parent: Optional['TUIComponent'] = None
        self._children: List['TUIComponent'] = []
        self._widget: Optional[Widget] = None

        # 组件配置
        self.config = {
            'auto_mount': True,
            'lazy_render': False,
            'state_persistence': False,
            'event_bubbling': True
        }
        self.config.update(kwargs)

    @property
    def state(self) -> ComponentState:
        """获取组件状态"""
        return self._state

    @property
    def widget(self) -> Optional[Widget]:
        """获取组件关联的Widget"""
        return self._widget

    @property
    def children(self) -> List['TUIComponent']:
        """获取子组件列表"""
        return self._children.copy()

    @property
    def parent(self) -> Optional['TUIComponent']:
        """获取父组件"""
        return self._parent

    @abstractmethod
    def render(self) -> Widget:
        """
        渲染组件
        必须由子类实现
        """
        pass

    async def mount(self) -> None:
        """
        组件挂载
        在组件被添加到DOM时调用
        """
        logger.debug(f"Mounting component: {self.component_id}")

        # 创建Widget
        self._widget = self.render()

        # 设置Widget ID
        if self._widget:
            self._widget.id = self.component_id

        # 挂载子组件
        for child in self._children:
            if child.config.get('auto_mount', True):
                await child.mount()

        # 触发挂载事件
        await self._emit_event("mounted", {"component_id": self.component_id})

    async def unmount(self) -> None:
        """
        组件卸载
        在组件从DOM移除时调用
        """
        logger.debug(f"Unmounting component: {self.component_id}")

        # 卸载子组件
        for child in self._children:
            await child.unmount()

        # 清理资源
        self._widget = None
        self._event_handlers.clear()

        # 触发卸载事件
        await self._emit_event("unmounted", {"component_id": self.component_id})

    def update_state(self, **kwargs) -> None:
        """
        更新组件状态
        """
        old_state = self._state

        # 更新状态
        for key, value in kwargs.items():
            if hasattr(old_state, key):
                setattr(old_state, key, value)
            else:
                old_state.data[key] = value

        old_state.updated_at = datetime.now()

        # 触发状态变更事件
        self._handle_state_changed(old_state)

    def _handle_state_changed(self, old_state: ComponentState) -> None:
        """处理状态变更"""
        # 通知订阅者
        self._notify_subscribers("state_changed", old_state, self._state)

        # 更新Widget
        if self._widget:
            self._update_widget()

    @abstractmethod
    def _update_widget(self) -> None:
        """
        更新Widget显示
        必须由子类实现
        """
        pass

    def add_child(self, child: 'TUIComponent') -> None:
        """添加子组件"""
        if child not in self._children:
            child._parent = self
            self._children.append(child)
            logger.debug(f"Added child {child.component_id} to {self.component_id}")

    def remove_child(self, child: 'TUIComponent') -> None:
        """移除子组件"""
        if child in self._children:
            child._parent = None
            self._children.remove(child)
            logger.debug(f"Removed child {child.component_id} from {self.component_id}")

    def find_child(self, component_id: str) -> Optional['TUIComponent']:
        """查找子组件"""
        for child in self._children:
            if child.component_id == component_id:
                return child
            # 递归查找
            found = child.find_child(component_id)
            if found:
                return found
        return None

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """订阅事件"""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
        logger.debug(f"Subscribed to {event_type} in {self.component_id}")

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """取消订阅事件"""
        if event_type in self._event_handlers:
            try:
                self._event_handlers[event_type].remove(handler)
                logger.debug(f"Unsubscribed from {event_type} in {self.component_id}")
            except ValueError:
                logger.warning(f"Handler not found for event type {event_type}")

    async def _emit_event(self, event_type: str, data: Dict[str, Any] = None) -> None:
        """发出事件"""
        event = ComponentEvent(self.component_id, event_type, data)

        # 通知本地订阅者
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {e}")

        # 事件冒泡
        if self.config.get('event_bubbling', True) and self._parent:
            await self._parent._emit_event(event_type, data)

    def _notify_subscribers(self, event_type: str, *args) -> None:
        """通知订阅者"""
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                try:
                    handler(*args)
                except Exception as e:
                    logger.error(f"Error in subscriber handler for {event_type}: {e}")

    async def handle_event(self, event: ComponentEvent) -> None:
        """处理事件"""
        # 默认实现，子类可以重写
        pass

    def get_state_dict(self) -> Dict[str, Any]:
        """获取状态字典"""
        return {
            'id': self._state.id,
            'visible': self._state.visible,
            'enabled': self._state.enabled,
            'focusable': self._state.focusable,
            'data': self._state.data,
            'metadata': self._state.metadata,
            'created_at': self._state.created_at.isoformat(),
            'updated_at': self._state.updated_at.isoformat()
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id='{self.component_id}')>"


# 导入必要的模块
import asyncio


class ContainerComponent(TUIComponent):
    """容器组件基类"""

    def __init__(self, component_id: str, **kwargs):
        super().__init__(component_id, **kwargs)
        self._container = None

    def render(self) -> Widget:
        """渲染容器"""
        from textual.containers import Vertical
        self._container = Vertical(id=self.component_id)
        return self._container

    def _update_widget(self) -> None:
        """更新容器"""
        if self._container:
            # 根据状态更新容器样式
            self._container.display = self.state.visible
            # 其他状态相关的更新...

    async def add_child_widget(self, child_widget: Widget) -> None:
        """添加子Widget到容器"""
        if self._container and child_widget:
            self._container.mount(child_widget)


# 使用示例
async def example_usage():
    """组件使用示例"""

    class TestComponent(ContainerComponent):
        """测试组件"""

        def __init__(self, component_id: str):
            super().__init__(component_id)
            self.message = "Hello, World!"

        def render(self) -> Widget:
            from textual.widgets import Label
            container = super().render()
            # 添加标签到容器
            label = Label(self.message)
            container.mount(label)
            return container

        def _update_widget(self) -> None:
            super()._update_widget()
            # 更新消息显示
            if self._container and 'message' in self.state.data:
                # 更新标签内容
                pass

    # 创建组件
    component = TestComponent("test_component")

    # 订阅事件
    def on_state_changed(old_state, new_state):
        print(f"State changed from {old_state.data} to {new_state.data}")

    component.subscribe("state_changed", on_state_changed)

    # 挂载组件
    await component.mount()

    # 更新状态
    component.update_state(message="Hello, Updated World!")

    # 卸载组件
    await component.unmount()


if __name__ == "__main__":
    asyncio.run(example_usage())
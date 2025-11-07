"""
ViewModel基类示例

这个文件展示了MVVM架构中ViewModel基类的核心设计，
用于指导实际的ViewModel实现工作。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Callable, List
from dataclasses import dataclass, field
from datetime import datetime
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class PropertyChangeNotification(Enum):
    """属性变更通知类型"""
    PROPERTY_CHANGED = "property_changed"
    COLLECTION_CHANGED = "collection_changed"
    COMMAND_CHANGED = "command_changed"


@dataclass
class PropertyChangedEventArgs:
    """属性变更事件参数"""
    property_name: str
    old_value: Any
    new_value: Any
    timestamp: datetime = field(default_factory=datetime.now)
    source: Optional[str] = None


@dataclass
class Command:
    """命令封装"""

    def __init__(self, execute_func: Callable, can_execute_func: Callable = None):
        self.execute_func = execute_func
        self.can_execute_func = can_execute_func
        self._last_result = None
        self._last_error = None

    def execute(self, *args, **kwargs) -> Any:
        """执行命令"""
        if not self.can_execute():
            raise ValueError("Command cannot be executed")

        try:
            self._last_result = self.execute_func(*args, **kwargs)
            self._last_error = None
            return self._last_result
        except Exception as e:
            self._last_error = e
            logger.error(f"Command execution failed: {e}")
            raise

    def can_execute(self) -> bool:
        """检查是否可以执行"""
        if self.can_execute_func:
            try:
                return self.can_execute_func()
            except Exception as e:
                logger.error(f"Error checking command can_execute: {e}")
                return False
        return True

    @property
    def last_result(self) -> Any:
        """获取最后一次执行结果"""
        return self._last_result

    @property
    def last_error(self) -> Optional[Exception]:
        """获取最后一次执行错误"""
        return self._last_error


class ObservableProperty:
    """可观察属性"""

    def __init__(self, initial_value: Any = None, property_name: str = None):
        self._value = initial_value
        self._property_name = property_name
        self._subscribers: List[Callable] = []
        self._notification_enabled = True

    def get(self) -> Any:
        """获取属性值"""
        return self._value

    def set(self, value: Any, notify: bool = True) -> None:
        """设置属性值"""
        if self._value != value:
            old_value = self._value
            self._value = value

            if notify and self._notification_enabled:
                self._notify_subscribers(old_value, value)

    def subscribe(self, callback: Callable[[Any, Any], None]) -> None:
        """订阅属性变更"""
        if callback not in self._subscribers:
            self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[Any, Any], None]) -> None:
        """取消订阅属性变更"""
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    def _notify_subscribers(self, old_value: Any, new_value: Any) -> None:
        """通知订阅者"""
        for callback in self._subscribers:
            try:
                callback(old_value, new_value)
            except Exception as e:
                logger.error(f"Error in property change callback: {e}")

    def disable_notification(self) -> None:
        """禁用通知"""
        self._notification_enabled = False

    def enable_notification(self) -> None:
        """启用通知"""
        self._notification_enabled = True

    def __str__(self) -> str:
        return f"ObservableProperty({self._value})"


class ViewModel(ABC):
    """ViewModel基类"""

    def __init__(self):
        self._properties: Dict[str, ObservableProperty] = {}
        self._commands: Dict[str, Command] = {}
        self._property_change_handlers: Dict[str, List[Callable]] = {}
        self._is_disposed = False
        self._parent_viewmodel: Optional['ViewModel'] = None
        self._child_viewmodels: List['ViewModel'] = []

    def set_property(self, name: str, value: Any, notify: bool = True) -> None:
        """设置属性值并触发通知"""
        if self._is_disposed:
            logger.warning(f"Attempting to set property {name} on disposed ViewModel")
            return

        if name not in self._properties:
            # 创建新的可观察属性
            self._properties[name] = ObservableProperty(value, name)

        # 设置属性值
        old_value = self._properties[name].get()
        self._properties[name].set(value, notify)

        # 触发属性变更处理器
        if notify:
            self._on_property_changed(name, old_value, value)

    def get_property(self, name: str, default: Any = None) -> Any:
        """获取属性值"""
        if name in self._properties:
            return self._properties[name].get()
        return default

    def observe_property(self, name: str, callback: Callable[[Any, Any], None]) -> None:
        """观察属性变更"""
        if name not in self._properties:
            self._properties[name] = ObservableProperty(None, name)

        self._properties[name].subscribe(callback)

    def register_command(self, name: str, command: Command) -> None:
        """注册命令"""
        self._commands[name] = command
        logger.debug(f"Registered command: {name}")

    def execute_command(self, name: str, *args, **kwargs) -> Any:
        """执行命令"""
        if name not in self._commands:
            raise ValueError(f"Command '{name}' not found")

        command = self._commands[name]
        result = command.execute(*args, **kwargs)

        # 触发命令执行后处理
        self._on_command_executed(name, result)

        return result

    def can_execute_command(self, name: str) -> bool:
        """检查命令是否可以执行"""
        if name not in self._commands:
            return False
        return self._commands[name].can_execute()

    def add_child_viewmodel(self, child: 'ViewModel') -> None:
        """添加子ViewModel"""
        if child not in self._child_viewmodels:
            child._parent_viewmodel = self
            self._child_viewmodels.append(child)
            logger.debug(f"Added child ViewModel: {child.__class__.__name__}")

    def remove_child_viewmodel(self, child: 'ViewModel') -> None:
        """移除子ViewModel"""
        if child in self._child_viewmodels:
            child._parent_viewmodel = None
            self._child_viewmodels.remove(child)
            logger.debug(f"Removed child ViewModel: {child.__class__.__name__}")

    def dispose(self) -> None:
        """释放资源"""
        if self._is_disposed:
            return

        logger.debug(f"Disposing ViewModel: {self.__class__.__name__}")

        # 释放子ViewModel
        for child in self._child_viewmodels:
            child.dispose()

        # 清理属性
        self._properties.clear()
        self._commands.clear()
        self._property_change_handlers.clear()

        self._is_disposed = True

    def _on_property_changed(self, property_name: str, old_value: Any, new_value: Any) -> None:
        """属性变更处理"""
        # 调用注册的处理器
        if property_name in self._property_change_handlers:
            for handler in self._property_change_handlers[property_name]:
                try:
                    handler(old_value, new_value)
                except Exception as e:
                    logger.error(f"Error in property change handler for {property_name}: {e}")

        # 通知父ViewModel
        if self._parent_viewmodel:
            self._parent_viewmodel._on_child_property_changed(self, property_name, old_value, new_value)

    def _on_child_property_changed(self, child: 'ViewModel', property_name: str, old_value: Any, new_value: Any) -> None:
        """子ViewModel属性变更处理"""
        # 默认实现，子类可以重写
        pass

    def _on_command_executed(self, command_name: str, result: Any) -> None:
        """命令执行后处理"""
        # 默认实现，子类可以重写
        pass

    def get_all_properties(self) -> Dict[str, Any]:
        """获取所有属性值"""
        return {name: prop.get() for name, prop in self._properties.items()}

    def get_all_commands(self) -> List[str]:
        """获取所有命令名称"""
        return list(self._commands.keys())

    def validate(self) -> List[str]:
        """验证ViewModel状态，返回错误信息列表"""
        errors = []

        # 检查必需属性
        required_properties = self.get_required_properties()
        for prop_name in required_properties:
            if prop_name not in self._properties or self._properties[prop_name].get() is None:
                errors.append(f"Required property '{prop_name}' is missing or null")

        # 检查属性值有效性
        validation_rules = self.get_validation_rules()
        for prop_name, validator in validation_rules.items():
            if prop_name in self._properties:
                value = self._properties[prop_name].get()
                try:
                    if not validator(value):
                        errors.append(f"Property '{prop_name}' failed validation")
                except Exception as e:
                    errors.append(f"Error validating property '{prop_name}': {e}")

        return errors

    def get_required_properties(self) -> List[str]:
        """获取必需属性列表，子类可重写"""
        return []

    def get_validation_rules(self) -> Dict[str, Callable[[Any], bool]]:
        """获取验证规则，子类可重写"""
        return {}

    def __del__(self):
        """析构函数"""
        self.dispose()


class ViewModelCollection(ViewModel):
    """ViewModel集合基类"""

    def __init__(self):
        super().__init__()
        self._items: List[Any] = []
        self._selected_item: Optional[Any] = None

    def add_item(self, item: Any) -> None:
        """添加项目"""
        self._items.append(item)
        self.set_property("items", self._items.copy())

    def remove_item(self, item: Any) -> None:
        """移除项目"""
        if item in self._items:
            self._items.remove(item)
            if self._selected_item == item:
                self._selected_item = None
                self.set_property("selected_item", None)
            self.set_property("items", self._items.copy())

    def select_item(self, item: Any) -> None:
        """选择项目"""
        if item in self._items:
            self._selected_item = item
            self.set_property("selected_item", item)

    def get_items(self) -> List[Any]:
        """获取项目列表"""
        return self._items.copy()

    def get_selected_item(self) -> Optional[Any]:
        """获取选中项目"""
        return self._selected_item


# 使用示例
class MainViewModel(ViewModel):
    """主窗口ViewModel示例"""

    def __init__(self):
        super().__init__()

        # 初始化属性
        self.set_property("title", "DAIP-LIVE")
        self.set_property("is_loading", False)
        self.set_property("current_view", "home")
        self.set_property("user_name", "")

        # 注册命令
        self.register_command("navigate", Command(self._navigate))
        self.register_command("load_data", Command(self._load_data, self._can_load_data))

        # 观察属性变更
        self.observe_property("is_loading", self._on_loading_changed)

    def _navigate(self, view_name: str) -> None:
        """导航命令实现"""
        old_view = self.get_property("current_view")
        self.set_property("current_view", view_name)
        logger.info(f"Navigated from {old_view} to {view_name}")

    def _load_data(self) -> None:
        """加载数据命令实现"""
        self.set_property("is_loading", True)
        # 模拟异步加载数据
        import threading
        import time

        def load_data_async():
            time.sleep(2)  # 模拟加载时间
            self.set_property("is_loading", False)

        threading.Thread(target=load_data_async).start()

    def _can_load_data(self) -> bool:
        """检查是否可以加载数据"""
        return not self.get_property("is_loading", False)

    def _on_loading_changed(self, old_value: bool, new_value: bool) -> None:
        """加载状态变更处理"""
        if new_value:
            logger.info("Started loading data")
        else:
            logger.info("Finished loading data")

    def get_required_properties(self) -> List[str]:
        return ["title", "current_view"]

    def get_validation_rules(self) -> Dict[str, Callable[[Any], bool]]:
        return {
            "title": lambda x: isinstance(x, str) and len(x.strip()) > 0,
            "user_name": lambda x: x is None or isinstance(x, str)
        }


# 使用示例
async def example_usage():
    """ViewModel使用示例"""

    # 创建ViewModel
    main_viewmodel = MainViewModel()

    # 观察属性变更
    def on_title_changed(old_value, new_value):
        print(f"Title changed from '{old_value}' to '{new_value}'")

    main_viewmodel.observe_property("title", on_title_changed)

    # 设置属性
    main_viewmodel.set_property("title", "DAIP-LIVE GUI")
    main_viewmodel.set_property("user_name", "Alice")

    # 执行命令
    main_viewmodel.execute_command("navigate", "chat")
    main_viewmodel.execute_command("load_data")

    # 检查命令可执行性
    can_load = main_viewmodel.can_execute_command("load_data")
    print(f"Can load data: {can_load}")

    # 验证ViewModel
    errors = main_viewmodel.validate()
    if errors:
        print(f"Validation errors: {errors}")
    else:
        print("ViewModel is valid")

    # 获取所有属性
    properties = main_viewmodel.get_all_properties()
    print(f"All properties: {properties}")

    # 释放资源
    main_viewmodel.dispose()


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
"""
P5 Agent Engine 事件总线设计示例

这个文件展示了新架构中事件总线的核心设计，
用于指导实际的实现工作。
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Callable, Any, Optional, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class EventType(Enum):
    """事件类型枚举"""
    SESSION_STARTED = "session_started"
    SESSION_COMPLETED = "session_completed"
    SESSION_FAILED = "session_failed"

    INTENT_RECOGNIZED = "intent_recognized"
    INTENT_RECOGNITION_FAILED = "intent_recognition_failed"

    EXECUTION_STARTED = "execution_started"
    EXECUTION_PROGRESS = "execution_progress"
    EXECUTION_COMPLETED = "execution_completed"
    EXECUTION_FAILED = "execution_failed"

    STATE_CHANGED = "state_changed"
    PERMISSION_REQUESTED = "permission_requested"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_DENIED = "permission_denied"


@dataclass
class Event:
    """事件基类"""
    type: EventType
    timestamp: datetime = field(default_factory=datetime.now)
    session_id: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'type': self.type.value,
            'timestamp': self.timestamp.isoformat(),
            'session_id': self.session_id,
            'data': self.data,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """从字典创建事件"""
        return cls(
            type=EventType(data['type']),
            timestamp=datetime.fromisoformat(data['timestamp']),
            session_id=data.get('session_id'),
            data=data.get('data', {}),
            metadata=data.get('metadata', {})
        )


@dataclass
class SessionStarted(Event):
    """会话开始事件"""
    type: EventType = EventType.SESSION_STARTED

    def __post_init__(self):
        if 'goal' not in self.data:
            raise ValueError("SessionStarted event must contain 'goal' in data")


@dataclass
class IntentRecognized(Event):
    """意图识别事件"""
    type: EventType = EventType.INTENT_RECOGNIZED

    def __post_init__(self):
        if 'intent' not in self.data:
            raise ValueError("IntentRecognized event must contain 'intent' in data")
        if 'confidence' not in self.data:
            raise ValueError("IntentRecognized event must contain 'confidence' in data")


class EventHandler(ABC):
    """事件处理器抽象基类"""

    @abstractmethod
    async def handle(self, event: Event) -> Optional[Event]:
        """处理事件，返回可选的新事件"""
        pass

    @property
    @abstractmethod
    def handled_types(self) -> List[EventType]:
        """返回此处理器处理的事件类型"""
        pass


class EventBus:
    """事件总线核心实现"""

    def __init__(self, max_history: int = 10000):
        self._handlers: Dict[EventType, List[EventHandler]] = {}
        self._queues: Dict[str, asyncio.Queue] = {}
        self._history: List[Event] = []
        self._max_history = max_history
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._running = False

    async def start(self):
        """启动事件总线"""
        self._running = True
        logger.info("EventBus started")

    async def stop(self):
        """停止事件总线"""
        self._running = False
        self._executor.shutdown(wait=True)
        logger.info("EventBus stopped")

    def subscribe(self, event_type: EventType, handler: EventHandler):
        """订阅事件类型"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.debug(f"Handler {handler.__class__.__name__} subscribed to {event_type}")

    def unsubscribe(self, event_type: EventType, handler: EventHandler):
        """取消订阅事件类型"""
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
                logger.debug(f"Handler {handler.__class__.__name__} unsubscribed from {event_type}")
            except ValueError:
                logger.warning(f"Handler not found for event type {event_type}")

    async def publish(self, event: Event) -> bool:
        """发布事件"""
        if not self._running:
            logger.warning("EventBus is not running, event dropped")
            return False

        try:
            # 添加到历史记录
            self._add_to_history(event)

            # 获取处理器
            handlers = self._handlers.get(event.type, [])

            if not handlers:
                logger.debug(f"No handlers for event type {event.type}")
                return True

            # 并行处理所有处理器
            tasks = []
            for handler in handlers:
                task = asyncio.create_task(self._handle_event(handler, event))
                tasks.append(task)

            # 等待所有处理器完成
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

            # 发送到会话队列（如果有的话）
            if event.session_id and event.session_id in self._queues:
                await self._queues[event.session_id].put(event)

            logger.debug(f"Event {event.type} published and processed")
            return True

        except Exception as e:
            logger.error(f"Error publishing event {event.type}: {e}")
            return False

    async def _handle_event(self, handler: EventHandler, event: Event):
        """处理单个事件"""
        try:
            result = await handler.handle(event)
            if result:
                await self.publish(result)
        except Exception as e:
            logger.error(f"Handler {handler.__class__.__name__} failed to process event {event.type}: {e}")

    def create_session_queue(self, session_id: str) -> asyncio.Queue:
        """为会话创建专用队列"""
        if session_id not in self._queues:
            self._queues[session_id] = asyncio.Queue(maxsize=1000)
            logger.debug(f"Created queue for session {session_id}")
        return self._queues[session_id]

    def remove_session_queue(self, session_id: str):
        """移除会话队列"""
        if session_id in self._queues:
            del self._queues[session_id]
            logger.debug(f"Removed queue for session {session_id}")

    async def stream(self, session_id: str) -> AsyncGenerator[Event, None]:
        """流式获取会话事件"""
        queue = self.create_session_queue(session_id)

        try:
            while True:
                event = await queue.get()
                yield event
                if event.type in [EventType.SESSION_COMPLETED, EventType.SESSION_FAILED]:
                    break
        finally:
            self.remove_session_queue(session_id)

    def _add_to_history(self, event: Event):
        """添加事件到历史记录"""
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history.pop(0)

    def get_history(self, event_type: Optional[EventType] = None,
                   session_id: Optional[str] = None,
                   limit: int = 100) -> List[Event]:
        """获取历史事件"""
        events = self._history

        if event_type:
            events = [e for e in events if e.type == event_type]

        if session_id:
            events = [e for e in events if e.session_id == session_id]

        return events[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        """获取事件总线统计信息"""
        return {
            'total_events': len(self._history),
            'handlers_count': {event_type: len(handlers) for event_type, handlers in self._handlers.items()},
            'active_sessions': len(self._queues),
            'running': self._running
        }


class IntentRecognitionHandler(EventHandler):
    """意图识别处理器示例"""

    def __init__(self, intent_service):
        self.intent_service = intent_service

    async def handle(self, event: Event) -> Optional[Event]:
        """处理会话开始事件，进行意图识别"""
        if event.type != EventType.SESSION_STARTED:
            return None

        try:
            goal = event.data.get('goal', '')
            intent_result = await self.intent_service.recognize_intent(goal)

            return IntentRecognized(
                session_id=event.session_id,
                data={
                    'intent': intent_result.intent,
                    'confidence': intent_result.confidence,
                    'parameters': intent_result.parameters
                }
            )
        except Exception as e:
            logger.error(f"Intent recognition failed: {e}")
            return Event(
                type=EventType.INTENT_RECOGNITION_FAILED,
                session_id=event.session_id,
                data={'error': str(e)}
            )

    @property
    def handled_types(self) -> List[EventType]:
        return [EventType.SESSION_STARTED]


# 使用示例
async def example_usage():
    """事件总线使用示例"""

    # 创建事件总线
    event_bus = EventBus()
    await event_bus.start()

    # 创建意图识别服务（模拟）
    class MockIntentService:
        async def recognize_intent(self, goal: str):
            class Result:
                def __init__(self):
                    self.intent = "chat"
                    self.confidence = 0.95
                    self.parameters = {}
            return Result()

    # 注册处理器
    intent_handler = IntentRecognitionHandler(MockIntentService())
    event_bus.subscribe(EventType.SESSION_STARTED, intent_handler)

    # 发布会话开始事件
    session_started = SessionStarted(
        session_id="test_session_001",
        data={'goal': '帮我分析一下这个项目的架构'}
    )

    await event_bus.publish(session_started)

    # 流式获取会话事件
    async for event in event_bus.stream("test_session_001"):
        print(f"Received event: {event.type}")
        if event.type == EventType.INTENT_RECOGNIZED:
            print(f"Intent: {event.data.get('intent')}")
            print(f"Confidence: {event.data.get('confidence')}")

    # 获取统计信息
    stats = event_bus.get_stats()
    print(f"EventBus stats: {stats}")

    await event_bus.stop()


if __name__ == "__main__":
    asyncio.run(example_usage())
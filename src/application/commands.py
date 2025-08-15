"""@Time    : 2025-08-06 10:30:00
@Author  : DAIP-LIVE Team
@File    : commands.py
@Description:
    Command handlers for the Personal Intelligence Hub.
    These handlers implement the Command part of CQRS pattern.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ..domain.value_objects import EntranceType, IntentType, MessageIntent, TaskPriority


@dataclass
class BaseCommand:
    """基础命令类"""
    command_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CreateUserCommand(BaseCommand):
    """创建用户命令"""
    user_id: str = ""
    username: str = ""
    email: str = ""
    preferred_entrance: EntranceType = EntranceType.SECRETARIAT
    preferences: dict[str, Any] = field(default_factory=dict)


@dataclass
class CreateSessionCommand(BaseCommand):
    """创建会话命令"""
    user_id: str = ""
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class CreateTaskCommand(BaseCommand):
    """创建任务命令"""
    session_id: str = ""
    content: str = ""
    intent_type: IntentType = IntentType.COMMENT
    priority: TaskPriority = field(default_factory=lambda: TaskPriority("normal"))
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessMessageCommand(BaseCommand):
    """处理消息命令"""
    session_id: str = ""
    content: str = ""
    sender: str = ""
    message_intent: MessageIntent = field(default_factory=lambda: MessageIntent.COMMENT)
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class StartDebateCommand(BaseCommand):
    """开始辩论命令"""
    session_id: str = ""
    topic: str = ""
    participants: list[str] = field(default_factory=list)


@dataclass
class PauseSessionCommand(BaseCommand):
    """暂停会话命令"""
    session_id: str = ""


@dataclass
class ResumeSessionCommand(BaseCommand):
    """恢复会话命令"""
    session_id: str = ""


@dataclass
class CompleteSessionCommand(BaseCommand):
    """完成会话命令"""
    session_id: str = ""
    reason: str = "user_request"


@dataclass
class ExecuteTaskCommand(BaseCommand):
    """执行任务命令"""
    task_id: str = ""


@dataclass
class UpdateUserPreferencesCommand(BaseCommand):
    """更新用户偏好命令"""
    user_id: str = ""
    preferences: dict[str, Any] = field(default_factory=dict)


@dataclass
class SwitchSessionEntranceCommand(BaseCommand):
    """切换会话入口命令"""
    session_id: str = ""
    new_entrance: EntranceType = EntranceType.SECRETARIAT


class CommandResult:
    """命令执行结果"""
    
    def __init__(self, success: bool, data: Any = None, error: str = None):
        self.success = success
        self.data = data
        self.error = error
        self.timestamp = datetime.now()
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "timestamp": self.timestamp.isoformat()
        }


class CommandHandler(ABC):
    """命令处理器接口"""
    
    @abstractmethod
    async def handle(self, command: BaseCommand) -> CommandResult:
        """处理命令"""
        pass


class CreateUserCommandHandler(CommandHandler):
    """创建用户命令处理器"""
    
    def __init__(self, create_user_use_case):
        self.create_user_use_case = create_user_use_case
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def handle(self, command: CreateUserCommand) -> CommandResult:
        """处理创建用户命令"""
        try:
            result = await self.create_user_use_case.execute(
                user_id=command.user_id,
                username=command.username,
                email=command.email,
                preferred_entrance=command.preferred_entrance,
                preferences=command.preferences
            )
            
            return CommandResult(result.success, result.data, result.error)
            
        except Exception as e:
            self.logger.error(f"Error handling CreateUserCommand: {e}")
            return CommandResult(False, error=str(e))


class CreateSessionCommandHandler(CommandHandler):
    """创建会话命令处理器"""
    
    def __init__(self, create_session_use_case):
        self.create_session_use_case = create_session_use_case
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def handle(self, command: CreateSessionCommand) -> CommandResult:
        """处理创建会话命令"""
        try:
            result = await self.create_session_use_case.execute(
                user_id=command.user_id,
                context=command.context
            )
            
            return CommandResult(result.success, result.data, result.error)
            
        except Exception as e:
            self.logger.error(f"Error handling CreateSessionCommand: {e}")
            return CommandResult(False, error=str(e))


class CreateTaskCommandHandler(CommandHandler):
    """创建任务命令处理器"""
    
    def __init__(self, create_task_use_case):
        self.create_task_use_case = create_task_use_case
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def handle(self, command: CreateTaskCommand) -> CommandResult:
        """处理创建任务命令"""
        try:
            result = await self.create_task_use_case.execute(
                session_id=command.session_id,
                content=command.content,
                intent_type=command.intent_type,
                priority=command.priority,
                context=command.context
            )
            
            return CommandResult(result.success, result.data, result.error)
            
        except Exception as e:
            self.logger.error(f"Error handling CreateTaskCommand: {e}")
            return CommandResult(False, error=str(e))


class ProcessMessageCommandHandler(CommandHandler):
    """处理消息命令处理器"""
    
    def __init__(self, process_message_use_case):
        self.process_message_use_case = process_message_use_case
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def handle(self, command: ProcessMessageCommand) -> CommandResult:
        """处理消息命令"""
        try:
            result = await self.process_message_use_case.execute(
                session_id=command.session_id,
                content=command.content,
                sender=command.sender,
                message_intent=command.message_intent,
                context=command.context
            )
            
            return CommandResult(result.success, result.data, result.error)
            
        except Exception as e:
            self.logger.error(f"Error handling ProcessMessageCommand: {e}")
            return CommandResult(False, error=str(e))


class StartDebateCommandHandler(CommandHandler):
    """开始辩论命令处理器"""
    
    def __init__(self, start_debate_use_case):
        self.start_debate_use_case = start_debate_use_case
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def handle(self, command: StartDebateCommand) -> CommandResult:
        """处理开始辩论命令"""
        try:
            result = await self.start_debate_use_case.execute(
                session_id=command.session_id,
                topic=command.topic,
                participants=command.participants
            )
            
            return CommandResult(result.success, result.data, result.error)
            
        except Exception as e:
            self.logger.error(f"Error handling StartDebateCommand: {e}")
            return CommandResult(False, error=str(e))


class ExecuteTaskCommandHandler(CommandHandler):
    """执行任务命令处理器"""
    
    def __init__(self, execute_task_use_case):
        self.execute_task_use_case = execute_task_use_case
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def handle(self, command: ExecuteTaskCommand) -> CommandResult:
        """处理执行任务命令"""
        try:
            result = await self.execute_task_use_case.execute(task_id=command.task_id)
            
            return CommandResult(result.success, result.data, result.error)
            
        except Exception as e:
            self.logger.error(f"Error handling ExecuteTaskCommand: {e}")
            return CommandResult(False, error=str(e))


class CommandBus:
    """命令总线"""
    
    def __init__(self):
        self.handlers: dict[type, CommandHandler] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def register_handler(self, command_type: type, handler: CommandHandler):
        """注册命令处理器"""
        self.handlers[command_type] = handler
        self.logger.info(f"Registered handler for {command_type.__name__}")
    
    async def dispatch(self, command: BaseCommand) -> CommandResult:
        """分发命令"""
        command_type = type(command)
        
        if command_type not in self.handlers:
            error_msg = f"No handler registered for {command_type.__name__}"
            self.logger.error(error_msg)
            return CommandResult(False, error=error_msg)
        
        handler = self.handlers[command_type]
        
        try:
            self.logger.info(f"Dispatching {command_type.__name__} with ID {command.command_id}")
            result = await handler.handle(command)
            self.logger.info(f"Command {command.command_id} executed successfully")
            return result
            
        except Exception as e:
            error_msg = f"Error executing command {command.command_id}: {str(e)}"
            self.logger.error(error_msg)
            return CommandResult(False, error=error_msg)
    
    def get_registered_commands(self) -> list[str]:
        """获取已注册的命令类型"""
        return [handler_type.__name__ for handler_type in self.handlers.keys()]


class CommandDispatcher:
    """命令分发器"""
    
    def __init__(self, command_bus: CommandBus, use_case_factory):
        self.command_bus = command_bus
        self.use_case_factory = use_case_factory
        self._setup_handlers()
    
    def _setup_handlers(self):
        """设置命令处理器"""
        # 注册所有命令处理器
        self.command_bus.register_handler(
            CreateUserCommand,
            CreateUserCommandHandler(self.use_case_factory.create_user_use_case())
        )
        
        self.command_bus.register_handler(
            CreateSessionCommand,
            CreateSessionCommandHandler(self.use_case_factory.create_session_use_case())
        )
        
        self.command_bus.register_handler(
            CreateTaskCommand,
            CreateTaskCommandHandler(self.use_case_factory.create_task_use_case())
        )
        
        self.command_bus.register_handler(
            ProcessMessageCommand,
            ProcessMessageCommandHandler(self.use_case_factory.process_message_use_case())
        )
        
        self.command_bus.register_handler(
            StartDebateCommand,
            StartDebateCommandHandler(self.use_case_factory.start_debate_use_case())
        )
        
        self.command_bus.register_handler(
            ExecuteTaskCommand,
            ExecuteTaskCommandHandler(self.use_case_factory.execute_task_use_case())
        )
    
    async def dispatch_command(self, command: BaseCommand) -> CommandResult:
        """分发命令"""
        return await self.command_bus.dispatch(command)
    
    async def create_user(self, user_id: str, username: str, email: str, 
                         preferred_entrance: EntranceType, 
                         preferences: dict[str, Any] = None) -> CommandResult:
        """创建用户"""
        command = CreateUserCommand(
            command_id=f"create_user_{user_id}",
            user_id=user_id,
            username=username,
            email=email,
            preferred_entrance=preferred_entrance,
            preferences=preferences or {}
        )
        
        return await self.dispatch_command(command)
    
    async def create_session(self, user_id: str, context: dict[str, Any] = None) -> CommandResult:
        """创建会话"""
        command = CreateSessionCommand(
            command_id=f"create_session_{user_id}",
            user_id=user_id,
            context=context or {}
        )
        
        return await self.dispatch_command(command)
    
    async def create_task(self, session_id: str, content: str, intent_type: IntentType,
                         priority: TaskPriority = None, context: dict[str, Any] = None) -> CommandResult:
        """创建任务"""
        command = CreateTaskCommand(
            command_id=f"create_task_{session_id}",
            session_id=session_id,
            content=content,
            intent_type=intent_type,
            priority=priority or TaskPriority("normal"),
            context=context or {}
        )
        
        return await self.dispatch_command(command)
    
    async def process_message(self, session_id: str, content: str, sender: str,
                             message_intent: MessageIntent = None, context: dict[str, Any] = None) -> CommandResult:
        """处理消息"""
        command = ProcessMessageCommand(
            command_id=f"process_message_{session_id}",
            session_id=session_id,
            content=content,
            sender=sender,
            message_intent=message_intent or MessageIntent.COMMENT,
            context=context or {}
        )
        
        return await self.dispatch_command(command)
    
    async def start_debate(self, session_id: str, topic: str, participants: list[str]) -> CommandResult:
        """开始辩论"""
        command = StartDebateCommand(
            command_id=f"start_debate_{session_id}",
            session_id=session_id,
            topic=topic,
            participants=participants
        )
        
        return await self.dispatch_command(command)
    
    async def execute_task(self, task_id: str) -> CommandResult:
        """执行任务"""
        command = ExecuteTaskCommand(
            command_id=f"execute_task_{task_id}",
            task_id=task_id
        )
        
        return await self.dispatch_command(command)
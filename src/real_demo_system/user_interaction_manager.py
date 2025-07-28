"""
用户交互管理器

处理真实用户输入，提供交互式演示体验，支持实时参数调整。
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class InteractionType(Enum):
    """交互类型"""
    INPUT_REQUEST = "input_request"
    PARAMETER_ADJUSTMENT = "parameter_adjustment"
    CHOICE_SELECTION = "choice_selection"
    CONFIRMATION = "confirmation"
    FEEDBACK = "feedback"


class InteractionStatus(Enum):
    """交互状态"""
    PENDING = "pending"
    WAITING_USER = "waiting_user"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class InteractionRequest:
    """交互请求"""
    request_id: str
    interaction_type: InteractionType
    title: str
    description: str
    options: Optional[Dict[str, Any]]
    required: bool
    timeout_seconds: Optional[int]
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['interaction_type'] = self.interaction_type.value
        data['created_at'] = self.created_at.isoformat()
        return data


@dataclass
class InteractionResponse:
    """交互响应"""
    request_id: str
    response_data: Any
    response_time: datetime
    user_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['response_time'] = self.response_time.isoformat()
        return data


@dataclass
class InteractionSession:
    """交互会话"""
    session_id: str
    user_id: Optional[str]
    demo_session_id: Optional[str]
    active_requests: Dict[str, InteractionRequest]
    completed_interactions: List[Dict[str, Any]]
    session_context: Dict[str, Any]
    created_at: datetime
    last_activity: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['last_activity'] = self.last_activity.isoformat()
        data['active_requests'] = {k: v.to_dict() for k, v in self.active_requests.items()}
        return data


class UserInteractionManager:
    """
    用户交互管理器
    
    处理用户输入、参数调整和交互式演示体验。
    """
    
    def __init__(self):
        """初始化用户交互管理器"""
        self.interaction_sessions: Dict[str, InteractionSession] = {}
        self.pending_requests: Dict[str, InteractionRequest] = {}
        self.response_handlers: Dict[str, Callable] = {}
        self.event_subscribers: List[Callable] = []
        
        # 交互超时管理
        self.timeout_tasks: Dict[str, asyncio.Task] = {}
        
        logger.info("UserInteractionManager initialized")
    
    def create_interaction_session(
        self,
        user_id: Optional[str] = None,
        demo_session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        创建交互会话
        
        Args:
            user_id: 用户ID
            demo_session_id: 关联的演示会话ID
            context: 会话上下文
            
        Returns:
            会话ID
        """
        session_id = str(uuid.uuid4())
        
        session = InteractionSession(
            session_id=session_id,
            user_id=user_id,
            demo_session_id=demo_session_id,
            active_requests={},
            completed_interactions=[],
            session_context=context or {},
            created_at=datetime.now(),
            last_activity=datetime.now()
        )
        
        self.interaction_sessions[session_id] = session
        
        logger.info(f"Created interaction session: {session_id}")
        return session_id
    
    async def request_user_input(
        self,
        session_id: str,
        title: str,
        description: str,
        input_type: str = "text",
        validation_rules: Optional[Dict[str, Any]] = None,
        default_value: Any = None,
        required: bool = True,
        timeout_seconds: Optional[int] = 300
    ) -> str:
        """
        请求用户输入
        
        Args:
            session_id: 会话ID
            title: 输入标题
            description: 输入描述
            input_type: 输入类型 (text, number, boolean, choice)
            validation_rules: 验证规则
            default_value: 默认值
            required: 是否必需
            timeout_seconds: 超时时间（秒）
            
        Returns:
            请求ID
        """
        if session_id not in self.interaction_sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        request_id = str(uuid.uuid4())
        
        options = {
            "input_type": input_type,
            "validation_rules": validation_rules,
            "default_value": default_value
        }
        
        request = InteractionRequest(
            request_id=request_id,
            interaction_type=InteractionType.INPUT_REQUEST,
            title=title,
            description=description,
            options=options,
            required=required,
            timeout_seconds=timeout_seconds,
            created_at=datetime.now()
        )
        
        # 添加到会话和全局待处理请求
        session = self.interaction_sessions[session_id]
        session.active_requests[request_id] = request
        session.last_activity = datetime.now()
        self.pending_requests[request_id] = request
        
        # 设置超时处理
        if timeout_seconds:
            timeout_task = asyncio.create_task(
                self._handle_request_timeout(request_id, timeout_seconds)
            )
            self.timeout_tasks[request_id] = timeout_task
        
        # 通知事件订阅者
        await self._emit_event("input_requested", {
            "session_id": session_id,
            "request_id": request_id,
            "request": request.to_dict()
        })
        
        logger.info(f"Requested user input: {request_id}")
        return request_id
    
    async def request_parameter_adjustment(
        self,
        session_id: str,
        parameter_name: str,
        current_value: Any,
        parameter_type: str,
        description: str,
        allowed_values: Optional[List[Any]] = None,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        timeout_seconds: Optional[int] = 180
    ) -> str:
        """
        请求参数调整
        
        Args:
            session_id: 会话ID
            parameter_name: 参数名称
            current_value: 当前值
            parameter_type: 参数类型
            description: 参数描述
            allowed_values: 允许的值列表
            min_value: 最小值
            max_value: 最大值
            timeout_seconds: 超时时间
            
        Returns:
            请求ID
        """
        if session_id not in self.interaction_sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        request_id = str(uuid.uuid4())
        
        options = {
            "parameter_name": parameter_name,
            "current_value": current_value,
            "parameter_type": parameter_type,
            "allowed_values": allowed_values,
            "min_value": min_value,
            "max_value": max_value
        }
        
        request = InteractionRequest(
            request_id=request_id,
            interaction_type=InteractionType.PARAMETER_ADJUSTMENT,
            title=f"调整参数: {parameter_name}",
            description=description,
            options=options,
            required=False,
            timeout_seconds=timeout_seconds,
            created_at=datetime.now()
        )
        
        # 添加到会话和全局待处理请求
        session = self.interaction_sessions[session_id]
        session.active_requests[request_id] = request
        session.last_activity = datetime.now()
        self.pending_requests[request_id] = request
        
        # 设置超时处理
        if timeout_seconds:
            timeout_task = asyncio.create_task(
                self._handle_request_timeout(request_id, timeout_seconds)
            )
            self.timeout_tasks[request_id] = timeout_task
        
        # 通知事件订阅者
        await self._emit_event("parameter_adjustment_requested", {
            "session_id": session_id,
            "request_id": request_id,
            "request": request.to_dict()
        })
        
        logger.info(f"Requested parameter adjustment: {request_id}")
        return request_id
    
    async def request_choice_selection(
        self,
        session_id: str,
        title: str,
        description: str,
        choices: List[Dict[str, Any]],
        allow_multiple: bool = False,
        required: bool = True,
        timeout_seconds: Optional[int] = 120
    ) -> str:
        """
        请求选择
        
        Args:
            session_id: 会话ID
            title: 选择标题
            description: 选择描述
            choices: 选择项列表
            allow_multiple: 是否允许多选
            required: 是否必需
            timeout_seconds: 超时时间
            
        Returns:
            请求ID
        """
        if session_id not in self.interaction_sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        request_id = str(uuid.uuid4())
        
        options = {
            "choices": choices,
            "allow_multiple": allow_multiple
        }
        
        request = InteractionRequest(
            request_id=request_id,
            interaction_type=InteractionType.CHOICE_SELECTION,
            title=title,
            description=description,
            options=options,
            required=required,
            timeout_seconds=timeout_seconds,
            created_at=datetime.now()
        )
        
        # 添加到会话和全局待处理请求
        session = self.interaction_sessions[session_id]
        session.active_requests[request_id] = request
        session.last_activity = datetime.now()
        self.pending_requests[request_id] = request
        
        # 设置超时处理
        if timeout_seconds:
            timeout_task = asyncio.create_task(
                self._handle_request_timeout(request_id, timeout_seconds)
            )
            self.timeout_tasks[request_id] = timeout_task
        
        # 通知事件订阅者
        await self._emit_event("choice_requested", {
            "session_id": session_id,
            "request_id": request_id,
            "request": request.to_dict()
        })
        
        logger.info(f"Requested choice selection: {request_id}")
        return request_id
    
    async def request_confirmation(
        self,
        session_id: str,
        title: str,
        description: str,
        default_choice: bool = False,
        timeout_seconds: Optional[int] = 60
    ) -> str:
        """
        请求确认
        
        Args:
            session_id: 会话ID
            title: 确认标题
            description: 确认描述
            default_choice: 默认选择
            timeout_seconds: 超时时间
            
        Returns:
            请求ID
        """
        if session_id not in self.interaction_sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        request_id = str(uuid.uuid4())
        
        options = {
            "default_choice": default_choice
        }
        
        request = InteractionRequest(
            request_id=request_id,
            interaction_type=InteractionType.CONFIRMATION,
            title=title,
            description=description,
            options=options,
            required=True,
            timeout_seconds=timeout_seconds,
            created_at=datetime.now()
        )
        
        # 添加到会话和全局待处理请求
        session = self.interaction_sessions[session_id]
        session.active_requests[request_id] = request
        session.last_activity = datetime.now()
        self.pending_requests[request_id] = request
        
        # 设置超时处理
        if timeout_seconds:
            timeout_task = asyncio.create_task(
                self._handle_request_timeout(request_id, timeout_seconds)
            )
            self.timeout_tasks[request_id] = timeout_task
        
        # 通知事件订阅者
        await self._emit_event("confirmation_requested", {
            "session_id": session_id,
            "request_id": request_id,
            "request": request.to_dict()
        })
        
        logger.info(f"Requested confirmation: {request_id}")
        return request_id
    
    async def submit_response(
        self,
        request_id: str,
        response_data: Any,
        user_id: Optional[str] = None
    ) -> bool:
        """
        提交响应
        
        Args:
            request_id: 请求ID
            response_data: 响应数据
            user_id: 用户ID
            
        Returns:
            是否成功
        """
        if request_id not in self.pending_requests:
            logger.warning(f"Request not found or already completed: {request_id}")
            return False
        
        request = self.pending_requests[request_id]
        
        # 验证响应数据
        validation_result = self._validate_response(request, response_data)
        if not validation_result["valid"]:
            logger.warning(f"Response validation failed: {validation_result['errors']}")
            return False
        
        # 创建响应对象
        response = InteractionResponse(
            request_id=request_id,
            response_data=response_data,
            response_time=datetime.now(),
            user_id=user_id
        )
        
        # 找到对应的会话
        session_id = None
        for sid, session in self.interaction_sessions.items():
            if request_id in session.active_requests:
                session_id = sid
                break
        
        if session_id:
            session = self.interaction_sessions[session_id]
            
            # 移动请求到已完成列表
            completed_interaction = {
                "request": request.to_dict(),
                "response": response.to_dict(),
                "status": InteractionStatus.COMPLETED.value
            }
            session.completed_interactions.append(completed_interaction)
            
            # 从活跃请求中移除
            del session.active_requests[request_id]
            session.last_activity = datetime.now()
        
        # 从全局待处理请求中移除
        del self.pending_requests[request_id]
        
        # 取消超时任务
        if request_id in self.timeout_tasks:
            self.timeout_tasks[request_id].cancel()
            del self.timeout_tasks[request_id]
        
        # 调用响应处理器
        if request_id in self.response_handlers:
            try:
                handler = self.response_handlers[request_id]
                if asyncio.iscoroutinefunction(handler):
                    await handler(response)
                else:
                    handler(response)
                del self.response_handlers[request_id]
            except Exception as e:
                logger.error(f"Error in response handler: {e}")
        
        # 通知事件订阅者
        await self._emit_event("response_submitted", {
            "session_id": session_id,
            "request_id": request_id,
            "response": response.to_dict()
        })
        
        logger.info(f"Response submitted for request: {request_id}")
        return True
    
    def _validate_response(self, request: InteractionRequest, response_data: Any) -> Dict[str, Any]:
        """验证响应数据"""
        errors = []
        
        if request.interaction_type == InteractionType.INPUT_REQUEST:
            options = request.options or {}
            input_type = options.get("input_type", "text")
            validation_rules = options.get("validation_rules", {})
            
            # 类型验证
            if input_type == "text" and not isinstance(response_data, str):
                errors.append("Response must be a string")
            elif input_type == "number" and not isinstance(response_data, (int, float)):
                errors.append("Response must be a number")
            elif input_type == "boolean" and not isinstance(response_data, bool):
                errors.append("Response must be a boolean")
            
            # 规则验证
            if isinstance(response_data, str):
                if "min_length" in validation_rules and len(response_data) < validation_rules["min_length"]:
                    errors.append(f"Response too short (min: {validation_rules['min_length']})")
                if "max_length" in validation_rules and len(response_data) > validation_rules["max_length"]:
                    errors.append(f"Response too long (max: {validation_rules['max_length']})")
            
            if isinstance(response_data, (int, float)):
                if "min_value" in validation_rules and response_data < validation_rules["min_value"]:
                    errors.append(f"Response too small (min: {validation_rules['min_value']})")
                if "max_value" in validation_rules and response_data > validation_rules["max_value"]:
                    errors.append(f"Response too large (max: {validation_rules['max_value']})")
        
        elif request.interaction_type == InteractionType.CHOICE_SELECTION:
            options = request.options or {}
            choices = options.get("choices", [])
            allow_multiple = options.get("allow_multiple", False)
            
            if allow_multiple:
                if not isinstance(response_data, list):
                    errors.append("Response must be a list for multiple choice")
                else:
                    valid_choice_ids = [choice.get("id") for choice in choices]
                    for choice_id in response_data:
                        if choice_id not in valid_choice_ids:
                            errors.append(f"Invalid choice: {choice_id}")
            else:
                valid_choice_ids = [choice.get("id") for choice in choices]
                if response_data not in valid_choice_ids:
                    errors.append(f"Invalid choice: {response_data}")
        
        elif request.interaction_type == InteractionType.CONFIRMATION:
            if not isinstance(response_data, bool):
                errors.append("Response must be a boolean for confirmation")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    async def _handle_request_timeout(self, request_id: str, timeout_seconds: int):
        """处理请求超时"""
        await asyncio.sleep(timeout_seconds)
        
        if request_id in self.pending_requests:
            request = self.pending_requests[request_id]
            
            # 找到对应的会话
            session_id = None
            for sid, session in self.interaction_sessions.items():
                if request_id in session.active_requests:
                    session_id = sid
                    break
            
            if session_id:
                session = self.interaction_sessions[session_id]
                
                # 移动请求到已完成列表（超时状态）
                completed_interaction = {
                    "request": request.to_dict(),
                    "response": None,
                    "status": InteractionStatus.TIMEOUT.value
                }
                session.completed_interactions.append(completed_interaction)
                
                # 从活跃请求中移除
                del session.active_requests[request_id]
                session.last_activity = datetime.now()
            
            # 从全局待处理请求中移除
            del self.pending_requests[request_id]
            
            # 移除超时任务
            if request_id in self.timeout_tasks:
                del self.timeout_tasks[request_id]
            
            # 通知事件订阅者
            await self._emit_event("request_timeout", {
                "session_id": session_id,
                "request_id": request_id
            })
            
            logger.warning(f"Request timeout: {request_id}")
    
    def set_response_handler(self, request_id: str, handler: Callable):
        """设置响应处理器"""
        self.response_handlers[request_id] = handler
    
    def get_pending_requests(self, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取待处理请求"""
        if session_id:
            session = self.interaction_sessions.get(session_id)
            if session:
                return [request.to_dict() for request in session.active_requests.values()]
            return []
        else:
            return [request.to_dict() for request in self.pending_requests.values()]
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话状态"""
        session = self.interaction_sessions.get(session_id)
        if not session:
            return None
        
        return session.to_dict()
    
    def cancel_request(self, request_id: str) -> bool:
        """取消请求"""
        if request_id not in self.pending_requests:
            return False
        
        request = self.pending_requests[request_id]
        
        # 找到对应的会话
        session_id = None
        for sid, session in self.interaction_sessions.items():
            if request_id in session.active_requests:
                session_id = sid
                break
        
        if session_id:
            session = self.interaction_sessions[session_id]
            
            # 移动请求到已完成列表（取消状态）
            completed_interaction = {
                "request": request.to_dict(),
                "response": None,
                "status": InteractionStatus.CANCELLED.value
            }
            session.completed_interactions.append(completed_interaction)
            
            # 从活跃请求中移除
            del session.active_requests[request_id]
            session.last_activity = datetime.now()
        
        # 从全局待处理请求中移除
        del self.pending_requests[request_id]
        
        # 取消超时任务
        if request_id in self.timeout_tasks:
            self.timeout_tasks[request_id].cancel()
            del self.timeout_tasks[request_id]
        
        logger.info(f"Request cancelled: {request_id}")
        return True
    
    async def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """发送事件"""
        event = {
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        # 通知订阅者
        for subscriber in self.event_subscribers:
            try:
                if asyncio.iscoroutinefunction(subscriber):
                    await subscriber(event)
                else:
                    subscriber(event)
            except Exception as e:
                logger.error(f"Error notifying subscriber: {e}")
    
    def subscribe(self, callback: Callable):
        """订阅交互事件"""
        self.event_subscribers.append(callback)
        logger.info(f"New interaction subscriber added, total: {len(self.event_subscribers)}")
    
    def unsubscribe(self, callback: Callable):
        """取消订阅"""
        if callback in self.event_subscribers:
            self.event_subscribers.remove(callback)
            logger.info(f"Interaction subscriber removed, total: {len(self.event_subscribers)}")
    
    def get_interaction_statistics(self) -> Dict[str, Any]:
        """获取交互统计信息"""
        total_sessions = len(self.interaction_sessions)
        total_pending = len(self.pending_requests)
        
        # 统计交互类型分布
        type_distribution = {}
        status_distribution = {}
        
        for session in self.interaction_sessions.values():
            for interaction in session.completed_interactions:
                interaction_type = interaction["request"]["interaction_type"]
                status = interaction["status"]
                
                type_distribution[interaction_type] = type_distribution.get(interaction_type, 0) + 1
                status_distribution[status] = status_distribution.get(status, 0) + 1
        
        # 计算完成率
        total_completed = status_distribution.get("completed", 0)
        total_interactions = sum(status_distribution.values())
        completion_rate = total_completed / total_interactions if total_interactions > 0 else 0
        
        return {
            "total_sessions": total_sessions,
            "pending_requests": total_pending,
            "interaction_distribution": {
                "by_type": type_distribution,
                "by_status": status_distribution
            },
            "completion_rate": completion_rate,
            "timestamp": datetime.now().isoformat()
        }
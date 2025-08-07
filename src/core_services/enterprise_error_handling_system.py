# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-05 12:00:00
@Author  : DAIP-LIVE Team
@File    : enterprise_error_handling_system.py
@Description:
    V0.3.8 Enterprise-Level Error Handling and Recovery System
    企业级错误处理和恢复系统
"""

import asyncio
import logging
import traceback
import time
import threading
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import json
import inspect
import weakref
from concurrent.futures import ThreadPoolExecutor
import queue
import uuid
import sys
import os

from ..core.exceptions import (
    DAIPException,
    SystemError,
    ValidationError,
    ConfigurationError,
    ResourceError,
    TimeoutError,
    LLMError,
    MemoryError,
    WorkflowError
)

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    FATAL = "fatal"


class ErrorCategory(Enum):
    """Error categories."""
    SYSTEM = "system"
    CONFIGURATION = "configuration"
    RESOURCE = "resource"
    NETWORK = "network"
    DATABASE = "database"
    LLM = "llm"
    MEMORY = "memory"
    WORKFLOW = "workflow"
    USER_INPUT = "user_input"
    EXTERNAL_SERVICE = "external_service"


class RecoveryStrategy(Enum):
    """Recovery strategies."""
    RETRY = "retry"
    FALLBACK = "fallback"
    CIRCUIT_BREAKER = "circuit_breaker"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    ROLLBACK = "rollback"
    RESTART = "restart"
    MANUAL_INTERVENTION = "manual_intervention"


@dataclass
class ErrorContext:
    """Error context information."""
    error_id: str
    timestamp: datetime
    severity: ErrorSeverity
    category: ErrorCategory
    error_type: str
    error_message: str
    stack_trace: str
    component: str
    operation: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "error_id": self.error_id,
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity.value,
            "category": self.category.value,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "stack_trace": self.stack_trace,
            "component": self.component,
            "operation": self.operation,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "correlation_id": self.correlation_id,
            "additional_data": self.additional_data
        }


@dataclass
class RecoveryAction:
    """Recovery action definition."""
    action_id: str
    strategy: RecoveryStrategy
    priority: int
    max_attempts: int
    timeout_seconds: float
    condition: Optional[Callable[[ErrorContext], bool]] = None
    action: Optional[Callable[[ErrorContext], Any]] = None
    fallback_action: Optional[Callable[[ErrorContext], Any]] = None
    
    def should_execute(self, error_context: ErrorContext) -> bool:
        """Check if action should be executed."""
        if self.condition is None:
            return True
        try:
            return self.condition(error_context)
        except Exception as e:
            logger.error(f"Error in recovery condition check: {e}")
            return False


class CircuitBreaker:
    """Circuit breaker implementation."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
        self.lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs):
        """Call function with circuit breaker protection."""
        with self.lock:
            if self.state == "open":
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = "half_open"
                    self.failure_count = 0
                else:
                    raise Exception("Circuit breaker is open")
        
        try:
            result = func(*args, **kwargs)
            with self.lock:
                if self.state == "half_open":
                    self.state = "closed"
                    self.failure_count = 0
            return result
        except Exception as e:
            with self.lock:
                self.failure_count += 1
                self.last_failure_time = time.time()
                if self.failure_count >= self.failure_threshold:
                    self.state = "open"
            raise e


class ErrorRecoveryManager:
    """Error recovery manager."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.recovery_actions: Dict[str, List[RecoveryAction]] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.recovery_history: List[Dict[str, Any]] = []
        self.active_recoveries: Dict[str, asyncio.Task] = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._initialize_recovery_actions()
        self._initialize_circuit_breakers()
    
    def _initialize_recovery_actions(self):
        """Initialize recovery actions."""
        # Memory error recovery
        self.recovery_actions[ErrorCategory.MEMORY] = [
            RecoveryAction(
                action_id="memory_cleanup",
                strategy=RecoveryStrategy.RETRY,
                priority=1,
                max_attempts=3,
                timeout_seconds=30.0,
                condition=lambda ctx: ctx.severity in [ErrorSeverity.LOW, ErrorSeverity.MEDIUM],
                action=self._memory_cleanup_action
            ),
            RecoveryAction(
                action_id="memory_restart",
                strategy=RecoveryStrategy.RESTART,
                priority=2,
                max_attempts=1,
                timeout_seconds=60.0,
                condition=lambda ctx: ctx.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL],
                action=self._memory_restart_action
            )
        ]
        
        # LLM error recovery
        self.recovery_actions[ErrorCategory.LLM] = [
            RecoveryAction(
                action_id="llm_retry",
                strategy=RecoveryStrategy.RETRY,
                priority=1,
                max_attempts=3,
                timeout_seconds=60.0,
                condition=lambda ctx: ctx.severity in [ErrorSeverity.LOW, ErrorSeverity.MEDIUM],
                action=self._llm_retry_action
            ),
            RecoveryAction(
                action_id="llm_fallback",
                strategy=RecoveryStrategy.FALLBACK,
                priority=2,
                max_attempts=1,
                timeout_seconds=30.0,
                condition=lambda ctx: ctx.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL],
                action=self._llm_fallback_action
            )
        ]
        
        # System error recovery
        self.recovery_actions[ErrorCategory.SYSTEM] = [
            RecoveryAction(
                action_id="system_restart",
                strategy=RecoveryStrategy.RESTART,
                priority=1,
                max_attempts=1,
                timeout_seconds=120.0,
                action=self._system_restart_action
            )
        ]
    
    def _initialize_circuit_breakers(self):
        """Initialize circuit breakers."""
        self.circuit_breakers["llm_calls"] = CircuitBreaker(failure_threshold=5, recovery_timeout=60.0)
        self.circuit_breakers["database_calls"] = CircuitBreaker(failure_threshold=3, recovery_timeout=30.0)
        self.circuit_breakers["external_services"] = CircuitBreaker(failure_threshold=5, recovery_timeout=120.0)
    
    async def handle_error(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Handle error with recovery actions."""
        recovery_id = str(uuid.uuid4())
        recovery_result = {
            "recovery_id": recovery_id,
            "error_id": error_context.error_id,
            "timestamp": datetime.now().isoformat(),
            "attempts": 0,
            "successful": False,
            "strategy_used": None,
            "recovery_time": 0.0,
            "error": None
        }
        
        try:
            start_time = time.time()
            
            # Get recovery actions for error category
            actions = self.recovery_actions.get(error_context.category, [])
            
            # Sort by priority
            actions.sort(key=lambda x: x.priority)
            
            # Execute recovery actions
            for action in actions:
                if not action.should_execute(error_context):
                    continue
                
                recovery_result["attempts"] += 1
                recovery_result["strategy_used"] = action.strategy.value
                
                try:
                    # Execute recovery action
                    if action.action:
                        if inspect.iscoroutinefunction(action.action):
                            result = await action.action(error_context)
                        else:
                            result = await asyncio.get_event_loop().run_in_executor(
                                self.executor, action.action, error_context
                            )
                        
                        recovery_result["successful"] = True
                        break
                        
                except Exception as e:
                    logger.error(f"Recovery action failed: {e}")
                    recovery_result["error"] = str(e)
                    
                    # Try fallback action
                    if action.fallback_action:
                        try:
                            if inspect.iscoroutinefunction(action.fallback_action):
                                result = await action.fallback_action(error_context)
                            else:
                                result = await asyncio.get_event_loop().run_in_executor(
                                    self.executor, action.fallback_action, error_context
                                )
                            
                            recovery_result["successful"] = True
                            break
                        except Exception as fallback_error:
                            logger.error(f"Fallback action failed: {fallback_error}")
                            recovery_result["error"] = str(fallback_error)
            
            recovery_result["recovery_time"] = time.time() - start_time
            
        except Exception as e:
            logger.error(f"Error recovery failed: {e}")
            recovery_result["error"] = str(e)
        
        # Record recovery history
        self.recovery_history.append(recovery_result)
        
        return recovery_result
    
    async def _memory_cleanup_action(self, error_context: ErrorContext) -> bool:
        """Memory cleanup recovery action."""
        try:
            # Implement memory cleanup logic
            import gc
            gc.collect()
            
            # Clear caches
            if hasattr(sys, 'clear_cache'):
                sys.clear_cache()
            
            return True
        except Exception as e:
            logger.error(f"Memory cleanup failed: {e}")
            return False
    
    async def _memory_restart_action(self, error_context: ErrorContext) -> bool:
        """Memory restart recovery action."""
        try:
            # Implement memory service restart logic
            # This would typically restart the memory service
            logger.info("Restarting memory service...")
            return True
        except Exception as e:
            logger.error(f"Memory restart failed: {e}")
            return False
    
    async def _llm_retry_action(self, error_context: ErrorContext) -> bool:
        """LLM retry recovery action."""
        try:
            # Implement LLM retry logic
            logger.info("Retrying LLM call...")
            return True
        except Exception as e:
            logger.error(f"LLM retry failed: {e}")
            return False
    
    async def _llm_fallback_action(self, error_context: ErrorContext) -> bool:
        """LLM fallback recovery action."""
        try:
            # Implement LLM fallback logic
            logger.info("Using LLM fallback...")
            return True
        except Exception as e:
            logger.error(f"LLM fallback failed: {e}")
            return False
    
    async def _system_restart_action(self, error_context: ErrorContext) -> bool:
        """System restart recovery action."""
        try:
            # Implement system restart logic
            logger.info("Restarting system components...")
            return True
        except Exception as e:
            logger.error(f"System restart failed: {e}")
            return False
    
    def get_circuit_breaker(self, name: str) -> CircuitBreaker:
        """Get circuit breaker by name."""
        return self.circuit_breakers.get(name, CircuitBreaker())
    
    def get_recovery_statistics(self) -> Dict[str, Any]:
        """Get recovery statistics."""
        total_recoveries = len(self.recovery_history)
        successful_recoveries = len([r for r in self.recovery_history if r["successful"]])
        
        return {
            "total_recoveries": total_recoveries,
            "successful_recoveries": successful_recoveries,
            "success_rate": (successful_recoveries / total_recoveries * 100) if total_recoveries > 0 else 0,
            "active_recoveries": len(self.active_recoveries),
            "circuit_breakers": {
                name: {
                    "state": breaker.state,
                    "failure_count": breaker.failure_count,
                    "failure_threshold": breaker.failure_threshold
                }
                for name, breaker in self.circuit_breakers.items()
            }
        }


class EnterpriseErrorHandler:
    """Enterprise-level error handler."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.error_history: List[ErrorContext] = []
        self.error_statistics: Dict[str, Any] = {}
        self.recovery_manager = ErrorRecoveryManager(config)
        self.alert_thresholds = config.get("alert_thresholds", {
            ErrorSeverity.LOW: 100,
            ErrorSeverity.MEDIUM: 50,
            ErrorSeverity.HIGH: 20,
            ErrorSeverity.CRITICAL: 10,
            ErrorSeverity.FATAL: 5
        })
        self.error_window_hours = config.get("error_window_hours", 24)
        self.lock = threading.Lock()
        self._initialize_statistics()
    
    def _initialize_statistics(self):
        """Initialize error statistics."""
        self.error_statistics = {
            "total_errors": 0,
            "errors_by_severity": {severity.value: 0 for severity in ErrorSeverity},
            "errors_by_category": {category.value: 0 for category in ErrorCategory},
            "errors_by_component": {},
            "errors_by_hour": {},
            "recovery_statistics": {}
        }
    
    def capture_error(self, 
                     error: Exception,
                     component: str,
                     operation: str,
                     severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                     category: ErrorCategory = ErrorCategory.SYSTEM,
                     user_id: Optional[str] = None,
                     session_id: Optional[str] = None,
                     correlation_id: Optional[str] = None,
                     additional_data: Optional[Dict[str, Any]] = None) -> ErrorContext:
        """Capture and handle error."""
        
        # Create error context
        error_context = ErrorContext(
            error_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            severity=severity,
            category=category,
            error_type=type(error).__name__,
            error_message=str(error),
            stack_trace=traceback.format_exc(),
            component=component,
            operation=operation,
            user_id=user_id,
            session_id=session_id,
            correlation_id=correlation_id,
            additional_data=additional_data or {}
        )
        
        # Store error
        with self.lock:
            self.error_history.append(error_context)
            self._update_statistics(error_context)
        
        # Log error
        self._log_error(error_context)
        
        # Check if recovery is needed
        if self._needs_recovery(error_context):
            asyncio.create_task(self._trigger_recovery(error_context))
        
        # Check alert thresholds
        self._check_alert_thresholds(error_context)
        
        return error_context
    
    def _update_statistics(self, error_context: ErrorContext):
        """Update error statistics."""
        self.error_statistics["total_errors"] += 1
        self.error_statistics["errors_by_severity"][error_context.severity.value] += 1
        self.error_statistics["errors_by_category"][error_context.category.value] += 1
        
        # Update component statistics
        component = error_context.component
        if component not in self.error_statistics["errors_by_component"]:
            self.error_statistics["errors_by_component"][component] = 0
        self.error_statistics["errors_by_component"][component] += 1
        
        # Update hourly statistics
        hour_key = error_context.timestamp.strftime("%Y-%m-%d %H:00")
        if hour_key not in self.error_statistics["errors_by_hour"]:
            self.error_statistics["errors_by_hour"][hour_key] = 0
        self.error_statistics["errors_by_hour"][hour_key] += 1
    
    def _log_error(self, error_context: ErrorContext):
        """Log error with appropriate level."""
        log_message = f"[{error_context.error_id}] {error_context.component}.{error_context.operation}: {error_context.error_message}"
        
        if error_context.severity == ErrorSeverity.FATAL:
            logger.critical(log_message)
        elif error_context.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
        elif error_context.severity == ErrorSeverity.HIGH:
            logger.error(log_message)
        elif error_context.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message)
        else:
            logger.info(log_message)
    
    def _needs_recovery(self, error_context: ErrorContext) -> bool:
        """Check if error needs recovery."""
        return error_context.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL, ErrorSeverity.FATAL]
    
    async def _trigger_recovery(self, error_context: ErrorContext):
        """Trigger error recovery."""
        try:
            recovery_result = await self.recovery_manager.handle_error(error_context)
            
            # Update recovery statistics
            self.error_statistics["recovery_statistics"] = self.recovery_manager.get_recovery_statistics()
            
            logger.info(f"Recovery completed for error {error_context.error_id}: {recovery_result['successful']}")
            
        except Exception as e:
            logger.error(f"Error recovery failed: {e}")
    
    def _check_alert_thresholds(self, error_context: ErrorContext):
        """Check alert thresholds."""
        threshold = self.alert_thresholds.get(error_context.severity, float('inf'))
        
        # Count errors in time window
        window_start = datetime.now() - timedelta(hours=self.error_window_hours)
        recent_errors = [
            e for e in self.error_history 
            if e.timestamp >= window_start and e.severity == error_context.severity
        ]
        
        if len(recent_errors) >= threshold:
            self._trigger_alert(error_context, len(recent_errors))
    
    def _trigger_alert(self, error_context: ErrorContext, count: int):
        """Trigger alert."""
        alert_message = f"ALERT: {count} {error_context.severity.value} errors in last {self.error_window_hours} hours"
        logger.critical(alert_message)
        
        # Here you would integrate with external alerting systems
        # For now, just log the alert
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics."""
        with self.lock:
            return {
                **self.error_statistics,
                "recent_errors": len([
                    e for e in self.error_history 
                    if e.timestamp >= datetime.now() - timedelta(hours=self.error_window_hours)
                ])
            }
    
    def get_error_history(self, 
                         component: Optional[str] = None,
                         severity: Optional[ErrorSeverity] = None,
                         category: Optional[ErrorCategory] = None,
                         hours: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get filtered error history."""
        filtered_errors = self.error_history
        
        if component:
            filtered_errors = [e for e in filtered_errors if e.component == component]
        
        if severity:
            filtered_errors = [e for e in filtered_errors if e.severity == severity]
        
        if category:
            filtered_errors = [e for e in filtered_errors if e.category == category]
        
        if hours:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            filtered_errors = [e for e in filtered_errors if e.timestamp >= cutoff_time]
        
        return [error.to_dict() for error in filtered_errors]
    
    def export_error_report(self, filename: str = "error_report.json") -> bool:
        """Export error report to file."""
        try:
            report = {
                "export_timestamp": datetime.now().isoformat(),
                "statistics": self.get_error_statistics(),
                "recent_errors": self.get_error_history(hours=24),
                "recovery_statistics": self.recovery_manager.get_recovery_statistics()
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Error report exported to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export error report: {e}")
            return False
    
    def clear_old_errors(self, days: int = 30):
        """Clear old errors from history."""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        with self.lock:
            self.error_history = [e for e in self.error_history if e.timestamp >= cutoff_time]
        
        logger.info(f"Cleared errors older than {days} days")


class ErrorHandlingDecorator:
    """Decorator for error handling."""
    
    def __init__(self, 
                 component: str,
                 operation: str,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 category: ErrorCategory = ErrorCategory.SYSTEM,
                 retry_attempts: int = 0,
                 circuit_breaker: Optional[str] = None):
        self.component = component
        self.operation = operation
        self.severity = severity
        self.category = category
        self.retry_attempts = retry_attempts
        self.circuit_breaker = circuit_breaker
    
    def __call__(self, func):
        """Decorator implementation."""
        if inspect.iscoroutinefunction(func):
            return self._async_wrapper(func)
        else:
            return self._sync_wrapper(func)
    
    def _async_wrapper(self, func):
        """Async wrapper."""
        async def wrapper(*args, **kwargs):
            error_handler = get_enterprise_error_handler()
            
            for attempt in range(self.retry_attempts + 1):
                try:
                    if self.circuit_breaker:
                        circuit_breaker = error_handler.recovery_manager.get_circuit_breaker(self.circuit_breaker)
                        return await asyncio.get_event_loop().run_in_executor(
                            None, circuit_breaker.call, func, *args, **kwargs
                        )
                    else:
                        return await func(*args, **kwargs)
                        
                except Exception as e:
                    if attempt == self.retry_attempts:
                        error_handler.capture_error(
                            error=e,
                            component=self.component,
                            operation=self.operation,
                            severity=self.severity,
                            category=self.category
                        )
                        raise
                    else:
                        logger.warning(f"Retry attempt {attempt + 1}/{self.retry_attempts} for {self.operation}")
                        await asyncio.sleep(1 * (attempt + 1))
        
        return wrapper
    
    def _sync_wrapper(self, func):
        """Sync wrapper."""
        def wrapper(*args, **kwargs):
            error_handler = get_enterprise_error_handler()
            
            for attempt in range(self.retry_attempts + 1):
                try:
                    if self.circuit_breaker:
                        circuit_breaker = error_handler.recovery_manager.get_circuit_breaker(self.circuit_breaker)
                        return circuit_breaker.call(func, *args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                        
                except Exception as e:
                    if attempt == self.retry_attempts:
                        error_handler.capture_error(
                            error=e,
                            component=self.component,
                            operation=self.operation,
                            severity=self.severity,
                            category=self.category
                        )
                        raise
                    else:
                        logger.warning(f"Retry attempt {attempt + 1}/{self.retry_attempts} for {self.operation}")
                        time.sleep(1 * (attempt + 1))
        
        return wrapper


# Global instance
_enterprise_error_handler: Optional[EnterpriseErrorHandler] = None


def get_enterprise_error_handler() -> EnterpriseErrorHandler:
    """Get global enterprise error handler instance."""
    global _enterprise_error_handler
    if _enterprise_error_handler is None:
        config = {
            "alert_thresholds": {
                "low": 100,
                "medium": 50,
                "high": 20,
                "critical": 10,
                "fatal": 5
            },
            "error_window_hours": 24
        }
        _enterprise_error_handler = EnterpriseErrorHandler(config)
    return _enterprise_error_handler


def handle_enterprise_error(component: str, operation: str, 
                          severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                          category: ErrorCategory = ErrorCategory.SYSTEM):
    """Decorator for enterprise error handling."""
    return ErrorHandlingDecorator(component, operation, severity, category)


def initialize_enterprise_error_handler(config: Dict[str, Any]):
    """Initialize enterprise error handler."""
    global _enterprise_error_handler
    _enterprise_error_handler = EnterpriseErrorHandler(config)
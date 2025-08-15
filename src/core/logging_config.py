"""@Time    : 2025-08-06 10:30:00
@Author  : DAIP-LIVE Team
@File    : logging_config.py
@Description:
    Comprehensive logging configuration for DAIP backend.
    Supports structured logging, multiple outputs, and log rotation.
"""

import json
import logging
import logging.handlers
import sys
import traceback
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = "INFO"
    file_path: str = "./logs/daip.log"
    max_size: str = "10MB"
    backup_count: int = 5
    format_string: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    console_level: str = "INFO"
    file_level: str = "DEBUG"
    enable_file_logging: bool = True
    enable_console_logging: bool = True
    enable_structured_logging: bool = True
    enable_json_logging: bool = False
    log_request_details: bool = True
    log_performance_metrics: bool = True
    log_error_stack_traces: bool = True


class StructuredFormatter(logging.Formatter):
    """结构化日志格式化器"""
    
    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt, datefmt, style)
        self.fmt = fmt
    
    def format(self, record):
        """格式化日志记录"""
        # 创建基础日志字典
        log_dict = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # 添加异常信息
        if record.exc_info:
            log_dict["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # 添加额外字段
        if hasattr(record, 'extra_fields'):
            log_dict.update(record.extra_fields)
        
        # 添加性能指标
        if hasattr(record, 'performance_metrics'):
            log_dict["performance"] = record.performance_metrics
        
        # 添加请求详情
        if hasattr(record, 'request_details'):
            log_dict["request"] = record.request_details
        
        return json.dumps(log_dict, ensure_ascii=False, default=str)


class PerformanceLogFilter(logging.Filter):
    """性能日志过滤器"""
    
    def __init__(self):
        super().__init__()
        self.performance_metrics = {}
    
    def filter(self, record):
        """过滤并添加性能指标"""
        # 添加性能指标到日志记录
        if hasattr(record, 'performance_metrics'):
            record.performance_metrics = self.performance_metrics.copy()
        
        return True
    
    def update_metrics(self, metrics: dict[str, Any]):
        """更新性能指标"""
        self.performance_metrics.update(metrics)


class RequestLogFilter(logging.Filter):
    """请求日志过滤器"""
    
    def __init__(self):
        super().__init__()
        self.request_details = {}
    
    def filter(self, record):
        """过滤并添加请求详情"""
        # 添加请求详情到日志记录
        if hasattr(record, 'request_details'):
            record.request_details = self.request_details.copy()
        
        return True
    
    def update_request_details(self, details: dict[str, Any]):
        """更新请求详情"""
        self.request_details.update(details)


class DAIPLogger:
    """DAIP日志管理器"""
    
    def __init__(self, config: LoggingConfig):
        self.config = config
        self.loggers = {}
        self.performance_filter = PerformanceLogFilter()
        self.request_filter = RequestLogFilter()
        
        # 创建日志目录
        if config.enable_file_logging:
            log_dir = Path(config.file_path).parent
            log_dir.mkdir(parents=True, exist_ok=True)
    
    def get_logger(self, name: str) -> logging.Logger:
        """获取日志记录器"""
        if name in self.loggers:
            return self.loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, self.config.level.upper()))
        
        # 清除现有处理器
        logger.handlers.clear()
        
        # 添加过滤器
        logger.addFilter(self.performance_filter)
        logger.addFilter(self.request_filter)
        
        # 控制台处理器
        if self.config.enable_console_logging:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, self.config.console_level.upper()))
            
            if self.config.enable_json_logging:
                console_formatter = StructuredFormatter()
            else:
                console_formatter = logging.Formatter(
                    self.config.format_string,
                    datefmt=self.config.date_format
                )
            
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
        
        # 文件处理器
        if self.config.enable_file_logging:
            # 解析文件大小
            max_bytes = self._parse_size(self.config.max_size)
            
            file_handler = logging.handlers.RotatingFileHandler(
                self.config.file_path,
                maxBytes=max_bytes,
                backupCount=self.config.backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(getattr(logging, self.config.file_level.upper()))
            
            if self.config.enable_json_logging:
                file_formatter = StructuredFormatter()
            else:
                file_formatter = logging.Formatter(
                    self.config.format_string,
                    datefmt=self.config.date_format
                )
            
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        # 缓存日志记录器
        self.loggers[name] = logger
        
        return logger
    
    def _parse_size(self, size_str: str) -> int:
        """解析大小字符串"""
        size_str = size_str.upper()
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)
    
    def update_performance_metrics(self, metrics: dict[str, Any]):
        """更新性能指标"""
        self.performance_filter.update_metrics(metrics)
    
    def update_request_details(self, details: dict[str, Any]):
        """更新请求详情"""
        self.request_filter.update_request_details(details)
    
    def log_performance_metrics(self, logger_name: str, metrics: dict[str, Any]):
        """记录性能指标"""
        logger = self.get_logger(logger_name)
        
        # 创建自定义日志记录
        record = logging.LogRecord(
            name=logger_name,
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Performance metrics",
            args=(),
            exc_info=None
        )
        
        record.performance_metrics = metrics
        
        # 处理日志记录
        for handler in logger.handlers:
            if handler.level <= logging.INFO:
                handler.emit(record)
    
    def log_request_details(self, logger_name: str, details: dict[str, Any]):
        """记录请求详情"""
        logger = self.get_logger(logger_name)
        
        # 创建自定义日志记录
        record = logging.LogRecord(
            name=logger_name,
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Request details",
            args=(),
            exc_info=None
        )
        
        record.request_details = details
        
        # 处理日志记录
        for handler in logger.handlers:
            if handler.level <= logging.INFO:
                handler.emit(record)
    
    def set_context(self, context: dict[str, Any]):
        """设置日志上下文"""
        self.update_performance_metrics(context.get("performance_metrics", {}))
        self.update_request_details(context.get("request_details", {}))
    
    def clear_context(self):
        """清除日志上下文"""
        self.performance_filter.performance_metrics = {}
        self.request_filter.request_details = {}


# 全局日志管理器实例
_logger_manager: Optional[DAIPLogger] = None


def get_logger_manager(config: LoggingConfig = None) -> DAIPLogger:
    """获取日志管理器实例"""
    global _logger_manager
    
    if _logger_manager is None:
        if config is None:
            config = LoggingConfig()
        _logger_manager = DAIPLogger(config)
    
    return _logger_manager


def get_logger(name: str = "daip") -> logging.Logger:
    """获取日志记录器的便捷函数"""
    manager = get_logger_manager()
    return manager.get_logger(name)


def setup_logging(config: LoggingConfig = None):
    """设置日志配置"""
    manager = get_logger_manager(config)
    
    # 设置根日志记录器
    root_logger = manager.get_logger("daip")
    
    # 配置第三方库日志级别
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("redis").setLevel(logging.WARNING)
    
    return root_logger


def log_performance_metrics(metrics: dict[str, Any], logger_name: str = "daip.performance"):
    """记录性能指标的便捷函数"""
    manager = get_logger_manager()
    manager.log_performance_metrics(logger_name, metrics)


def log_request_details(details: dict[str, Any], logger_name: str = "daip.requests"):
    """记录请求详情的便捷函数"""
    manager = get_logger_manager()
    manager.log_request_details(logger_name, details)


def set_log_context(context: dict[str, Any]):
    """设置日志上下文的便捷函数"""
    manager = get_logger_manager()
    manager.set_context(context)


def clear_log_context():
    """清除日志上下文的便捷函数"""
    manager = get_logger_manager()
    manager.clear_context()


class RequestLogger:
    """请求日志记录器"""
    
    def __init__(self, logger_name: str = "daip.requests"):
        self.logger = get_logger(logger_name)
        self.manager = get_logger_manager()
    
    def log_request(self, method: str, url: str, headers: dict[str, str] = None, 
                   body: Any = None, client_ip: str = None):
        """记录请求"""
        details = {
            "method": method,
            "url": url,
            "headers": headers or {},
            "client_ip": client_ip,
            "timestamp": datetime.now().isoformat()
        }
        
        if body is not None:
            details["body"] = str(body)
        
        self.manager.log_request_details(self.logger.name, details)
    
    def log_response(self, status_code: int, response_time: float, 
                    response_size: int = None, error: str = None):
        """记录响应"""
        details = {
            "status_code": status_code,
            "response_time": response_time,
            "response_size": response_size,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        
        self.manager.log_request_details(self.logger.name, details)


class PerformanceLogger:
    """性能日志记录器"""
    
    def __init__(self, logger_name: str = "daip.performance"):
        self.logger = get_logger(logger_name)
        self.manager = get_logger_manager()
    
    def log_operation(self, operation: str, duration: float, 
                     memory_usage: int = None, cpu_usage: float = None,
                     additional_metrics: dict[str, Any] = None):
        """记录操作性能"""
        metrics = {
            "operation": operation,
            "duration": duration,
            "memory_usage": memory_usage,
            "cpu_usage": cpu_usage,
            "timestamp": datetime.now().isoformat()
        }
        
        if additional_metrics:
            metrics.update(additional_metrics)
        
        self.manager.log_performance_metrics(self.logger.name, metrics)
    
    def log_database_query(self, query: str, duration: float, 
                          rows_affected: int = None):
        """记录数据库查询性能"""
        metrics = {
            "query_type": "database",
            "query": query,
            "duration": duration,
            "rows_affected": rows_affected,
            "timestamp": datetime.now().isoformat()
        }
        
        self.manager.log_performance_metrics(self.logger.name, metrics)
    
    def log_llm_call(self, model: str, prompt_tokens: int, 
                    completion_tokens: int, duration: float):
        """记录LLM调用性能"""
        metrics = {
            "operation": "llm_call",
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        
        self.manager.log_performance_metrics(self.logger.name, metrics)
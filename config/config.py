"""@Time    : 2025-08-06 10:30:00
@Author  : DAIP-LIVE Team
@File    : config.py
@Description:
    Configuration management for DAIP backend.
    Handles environment variables, configuration loading, and validation.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseSettings, Field, validator


@dataclass
class DatabaseConfig:
    """数据库配置"""
    url: str = "postgresql+asyncpg://daip:daip@localhost:5432/daip_db"
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False


@dataclass
class RedisConfig:
    """Redis配置"""
    url: str = "redis://localhost:6379/0"
    connection_pool_max_connections: int = 20
    connection_pool_timeout: int = 30
    socket_timeout: int = 30
    socket_connect_timeout: int = 30
    retry_on_timeout: bool = True
    health_check_interval: int = 30
    default_ttl: int = 3600
    session_ttl: int = 86400
    cache_ttl: int = 1800


@dataclass
class VectorStoreConfig:
    """向量存储配置"""
    persist_directory: str = "./data/vector_store"
    collection_name: str = "daip_knowledge"
    enable_persistence: bool = True
    max_results: int = 10
    similarity_threshold: float = 0.7
    enable_cache: bool = True
    batch_size: int = 100
    search_timeout: int = 30


@dataclass
class OllamaConfig:
    """Ollama配置"""
    base_url: str = "http://localhost:11434"
    model: str = "llama3.2:latest"
    embedding_model: str = "nomic-embed-text"
    timeout: int = 300
    retry_attempts: int = 3
    retry_delay: int = 1
    enable_streaming: bool = True
    enable_tool_use: bool = True
    max_concurrent_requests: int = 10
    request_queue_size: int = 100


@dataclass
class SecurityConfig:
    """安全配置"""
    secret_key: str = "your-secret-key-change-this-in-production"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60
    algorithm: str = "HS256"
    enable_cors: bool = True
    cors_origins: list[str] = field(default_factory=lambda: [
        "http://localhost:3000",
        "http://localhost:8080", 
        "http://localhost:5173"
    ])
    trusted_hosts: list[str] = field(default_factory=lambda: ["localhost", "127.0.0.1"])


@dataclass
class SessionConfig:
    """会话配置"""
    max_duration_hours: int = 24
    max_tasks_per_session: int = 50
    max_messages_per_session: int = 1000
    enable_persistence: bool = True
    auto_cleanup_enabled: bool = True
    cleanup_interval_minutes: int = 60
    enable_event_logging: bool = True
    max_event_history: int = 1000


@dataclass
class TaskConfig:
    """任务配置"""
    max_concurrent_tasks: int = 10
    max_queue_size: int = 100
    task_timeout_seconds: int = 1800
    enable_priority_queue: bool = True
    enable_resource_management: bool = True
    enable_retry_mechanism: bool = True
    max_retries: int = 3
    retry_delay_seconds: int = 60
    enable_event_logging: bool = True
    max_event_history: int = 5000


@dataclass
class WebSocketConfig:
    """WebSocket配置"""
    connection_timeout_minutes: int = 30
    ping_interval_seconds: int = 30
    max_connections_per_user: int = 5
    max_connections_per_session: int = 10
    enable_broadcasting: bool = True
    enable_authentication: bool = True
    max_message_size: int = 1024 * 1024  # 1MB


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


@dataclass
class PerformanceConfig:
    """性能配置"""
    max_workers: int = 4
    max_requests_per_worker: int = 1000
    request_timeout_seconds: int = 300
    enable_metrics: bool = True
    metrics_port: int = 9090
    health_check_interval_seconds: int = 30
    enable_caching: bool = True
    cache_ttl: int = 300


@dataclass
class FeatureConfig:
    """功能配置"""
    enable_vector_search: bool = True
    enable_caching: bool = True
    enable_streaming: bool = True
    enable_tool_use: bool = True
    enable_retry_mechanism: bool = True
    enable_websocket: bool = True
    enable_metrics: bool = True
    enable_health_check: bool = True
    enable_swagger: bool = True
    enable_redoc: bool = True
    auto_reload: bool = True


@dataclass
class DevelopmentConfig:
    """开发配置"""
    development_mode: bool = False
    debug: bool = False
    testing: bool = False
    environment: str = "production"
    log_level: str = "INFO"
    enable_swagger_ui: bool = True
    enable_re_doc: bool = True
    auto_reload: bool = False


class Settings(BaseSettings):
    """应用设置"""
    
    # 基础配置
    app_name: str = Field("DAIP Backend", env="APP_NAME")
    app_version: str = Field("1.0.0", env="APP_VERSION")
    debug: bool = Field(False, env="DEBUG")
    
    # 数据库配置
    database_url: str = Field("postgresql+asyncpg://daip:daip@localhost:5432/daip_db", env="DATABASE_URL")
    
    # Redis配置
    redis_url: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    
    # 向量存储配置
    vector_store_persist_directory: str = Field("./data/vector_store", env="VECTOR_STORE_PERSIST_DIRECTORY")
    vector_store_collection_name: str = Field("daip_knowledge", env="VECTOR_STORE_COLLECTION_NAME")
    
    # Ollama配置
    ollama_base_url: str = Field("http://localhost:11434", env="OLLAMA_BASE_URL")
    ollama_model: str = Field("llama3.2:latest", env="OLLAMA_MODEL")
    ollama_embedding_model: str = Field("nomic-embed-text", env="OLLAMA_EMBEDDING_MODEL")
    
    # 安全配置
    secret_key: str = Field("your-secret-key-change-this-in-production", env="SECRET_KEY")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_minutes: int = Field(60, env="REFRESH_TOKEN_EXPIRE_MINUTES")
    
    # CORS配置
    cors_origins: str = Field("http://localhost:3000,http://localhost:8080,http://localhost:5173", env="CORS_ORIGINS")
    
    # 会话配置
    session_max_duration_hours: int = Field(24, env="SESSION_MAX_DURATION_HOURS")
    session_max_tasks: int = Field(50, env="SESSION_MAX_TASKS")
    session_max_messages: int = Field(1000, env="SESSION_MAX_MESSAGES")
    
    # 任务配置
    task_max_concurrent: int = Field(10, env="TASK_MAX_CONCURRENT")
    task_max_queue_size: int = Field(100, env="TASK_MAX_QUEUE_SIZE")
    task_timeout_seconds: int = Field(1800, env="TASK_TIMEOUT_SECONDS")
    
    # WebSocket配置
    websocket_connection_timeout_minutes: int = Field(30, env="WEBSOCKET_CONNECTION_TIMEOUT_MINUTES")
    websocket_ping_interval_seconds: int = Field(30, env="WEBSOCKET_PING_INTERVAL_SECONDS")
    websocket_max_connections_per_user: int = Field(5, env="WEBSOCKET_MAX_CONNECTIONS_PER_USER")
    
    # 性能配置
    max_workers: int = Field(4, env="MAX_WORKERS")
    max_requests_per_worker: int = Field(1000, env="MAX_REQUESTS_PER_WORKER")
    request_timeout_seconds: int = Field(300, env="REQUEST_TIMEOUT_SECONDS")
    
    # 监控配置
    enable_metrics: bool = Field(True, env="ENABLE_METRICS")
    metrics_port: int = Field(9090, env="METRICS_PORT")
    health_check_interval_seconds: int = Field(30, env="HEALTH_CHECK_INTERVAL_SECONDS")
    
    # 功能标志
    enable_vector_search: bool = Field(True, env="ENABLE_VECTOR_SEARCH")
    enable_caching: bool = Field(True, env="ENABLE_CACHING")
    enable_streaming: bool = Field(True, env="ENABLE_STREAMING")
    enable_tool_use: bool = Field(True, env="ENABLE_TOOL_USE")
    enable_retry_mechanism: bool = Field(True, env="ENABLE_RETRY_MECHANISM")
    
    # 开发配置
    development_mode: bool = Field(False, env="DEVELOPMENT_MODE")
    enable_swagger: bool = Field(True, env="ENABLE_SWAGGER")
    enable_redoc: bool = Field(True, env="ENABLE_REDOC")
    auto_reload: bool = Field(True, env="AUTO_RELOAD")
    
    # 日志配置
    log_file: str = Field("./logs/daip.log", env="LOG_FILE")
    log_max_size: str = Field("10MB", env="LOG_MAX_SIZE")
    log_backup_count: int = Field(5, env="LOG_BACKUP_COUNT")
    log_level_console: str = Field("INFO", env="LOG_LEVEL_CONSOLE")
    log_level_file: str = Field("DEBUG", env="LOG_LEVEL_FILE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @validator('cors_origins')
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        if v == "your-secret-key-change-this-in-production":
            raise ValueError("Please change the default secret key in production")
        return v
    
    def to_database_config(self) -> DatabaseConfig:
        """转换为数据库配置"""
        return DatabaseConfig(
            url=self.database_url,
            echo=self.debug
        )
    
    def to_redis_config(self) -> RedisConfig:
        """转换为Redis配置"""
        return RedisConfig(
            url=self.redis_url
        )
    
    def to_vector_store_config(self) -> VectorStoreConfig:
        """转换为向量存储配置"""
        return VectorStoreConfig(
            persist_directory=self.vector_store_persist_directory,
            collection_name=self.vector_store_collection_name,
            enable_persistence=True
        )
    
    def to_ollama_config(self) -> OllamaConfig:
        """转换为Ollama配置"""
        return OllamaConfig(
            base_url=self.ollama_base_url,
            model=self.ollama_model,
            embedding_model=self.ollama_embedding_model
        )
    
    def to_security_config(self) -> SecurityConfig:
        """转换为安全配置"""
        return SecurityConfig(
            secret_key=self.secret_key,
            access_token_expire_minutes=self.access_token_expire_minutes,
            refresh_token_expire_minutes=self.refresh_token_expire_minutes,
            cors_origins=self.cors_origins
        )
    
    def to_session_config(self) -> SessionConfig:
        """转换为会话配置"""
        return SessionConfig(
            max_duration_hours=self.session_max_duration_hours,
            max_tasks_per_session=self.session_max_tasks,
            max_messages_per_session=self.session_max_messages
        )
    
    def to_task_config(self) -> TaskConfig:
        """转换为任务配置"""
        return TaskConfig(
            max_concurrent_tasks=self.task_max_concurrent,
            max_queue_size=self.task_max_queue_size,
            task_timeout_seconds=self.task_timeout_seconds
        )
    
    def to_websocket_config(self) -> WebSocketConfig:
        """转换为WebSocket配置"""
        return WebSocketConfig(
            connection_timeout_minutes=self.websocket_connection_timeout_minutes,
            ping_interval_seconds=self.websocket_ping_interval_seconds,
            max_connections_per_user=self.websocket_max_connections_per_user
        )
    
    def to_logging_config(self) -> LoggingConfig:
        """转换为日志配置"""
        return LoggingConfig(
            level=self.log_level_console,
            file_path=self.log_file,
            max_size=self.log_max_size,
            backup_count=self.log_backup_count,
            console_level=self.log_level_console,
            file_level=self.log_level_file
        )
    
    def to_performance_config(self) -> PerformanceConfig:
        """转换为性能配置"""
        return PerformanceConfig(
            max_workers=self.max_workers,
            max_requests_per_worker=self.max_requests_per_worker,
            request_timeout_seconds=self.request_timeout_seconds,
            enable_metrics=self.enable_metrics,
            metrics_port=self.metrics_port,
            health_check_interval_seconds=self.health_check_interval_seconds
        )
    
    def to_feature_config(self) -> FeatureConfig:
        """转换为功能配置"""
        return FeatureConfig(
            enable_vector_search=self.enable_vector_search,
            enable_caching=self.enable_caching,
            enable_streaming=self.enable_streaming,
            enable_tool_use=self.enable_tool_use,
            enable_retry_mechanism=self.enable_retry_mechanism,
            enable_websocket=True,
            enable_metrics=self.enable_metrics,
            enable_health_check=True,
            enable_swagger=self.enable_swagger,
            enable_redoc=self.enable_redoc,
            auto_reload=self.auto_reload
        )
    
    def to_development_config(self) -> DevelopmentConfig:
        """转换为开发配置"""
        return DevelopmentConfig(
            development_mode=self.development_mode,
            debug=self.debug,
            testing=False,
            environment="development" if self.debug else "production",
            log_level=self.log_level_console,
            enable_swagger_ui=self.enable_swagger,
            enable_re_doc=self.enable_redoc,
            auto_reload=self.auto_reload
        )


# 全局配置实例
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """获取设置实例"""
    global _settings
    
    if _settings is None:
        _settings = Settings()
    
    return _settings


def load_config_from_file(config_path: str) -> Settings:
    """从文件加载配置"""
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_file, encoding='utf-8') as f:
        config_data = json.load(f)
    
    return Settings(**config_data)


def save_config_to_file(settings: Settings, config_path: str):
    """保存配置到文件"""
    config_file = Path(config_path)
    
    # 确保目录存在
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(settings.dict(), f, indent=2, ensure_ascii=False)


def validate_config(settings: Settings) -> list[str]:
    """验证配置"""
    errors = []
    
    # 验证必需的配置项
    if not settings.secret_key or settings.secret_key == "your-secret-key-change-this-in-production":
        errors.append("SECRET_KEY must be set and changed from default value")
    
    # 验证数据库URL
    if not settings.database_url:
        errors.append("DATABASE_URL must be set")
    
    # 验证Redis URL
    if not settings.redis_url:
        errors.append("REDIS_URL must be set")
    
    # 验证Ollama配置
    if not settings.ollama_base_url:
        errors.append("OLLAMA_BASE_URL must be set")
    
    # 验证超时配置
    if settings.request_timeout_seconds <= 0:
        errors.append("REQUEST_TIMEOUT_SECONDS must be positive")
    
    if settings.task_timeout_seconds <= 0:
        errors.append("TASK_TIMEOUT_SECONDS must be positive")
    
    # 验证连接数配置
    if settings.max_workers <= 0:
        errors.append("MAX_WORKERS must be positive")
    
    if settings.task_max_concurrent <= 0:
        errors.append("TASK_MAX_CONCURRENT must be positive")
    
    # 验证TTL配置
    if settings.session_max_duration_hours <= 0:
        errors.append("SESSION_MAX_DURATION_HOURS must be positive")
    
    return errors


def get_config_summary(settings: Settings) -> dict[str, Any]:
    """获取配置摘要"""
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": "development" if settings.debug else "production",
        "debug": settings.debug,
        "database_url": settings.database_url.split('@')[-1] if '@' in settings.database_url else "localhost",
        "redis_url": settings.redis_url.split('@')[-1] if '@' in settings.redis_url else "localhost",
        "ollama_base_url": settings.ollama_base_url,
        "cors_origins": len(settings.cors_origins),
        "max_workers": settings.max_workers,
        "task_max_concurrent": settings.task_max_concurrent,
        "features": {
            "vector_search": settings.enable_vector_search,
            "caching": settings.enable_caching,
            "streaming": settings.enable_streaming,
            "tool_use": settings.enable_tool_use,
            "websocket": True,
            "metrics": settings.enable_metrics,
            "swagger": settings.enable_swagger,
            "redoc": settings.enable_redoc
        }
    }


def create_default_config_file(config_path: str = "config/default.json"):
    """创建默认配置文件"""
    default_settings = Settings()
    
    config_data = {
        "app_name": default_settings.app_name,
        "app_version": default_settings.app_version,
        "debug": default_settings.debug,
        "database_url": default_settings.database_url,
        "redis_url": default_settings.redis_url,
        "vector_store_persist_directory": default_settings.vector_store_persist_directory,
        "vector_store_collection_name": default_settings.vector_store_collection_name,
        "ollama_base_url": default_settings.ollama_base_url,
        "ollama_model": default_settings.ollama_model,
        "ollama_embedding_model": default_settings.ollama_embedding_model,
        "secret_key": default_settings.secret_key,
        "access_token_expire_minutes": default_settings.access_token_expire_minutes,
        "refresh_token_expire_minutes": default_settings.refresh_token_expire_minutes,
        "cors_origins": default_settings.cors_origins,
        "session_max_duration_hours": default_settings.session_max_duration_hours,
        "session_max_tasks": default_settings.session_max_tasks,
        "session_max_messages": default_settings.session_max_messages,
        "task_max_concurrent": default_settings.task_max_concurrent,
        "task_max_queue_size": default_settings.task_max_queue_size,
        "task_timeout_seconds": default_settings.task_timeout_seconds,
        "websocket_connection_timeout_minutes": default_settings.websocket_connection_timeout_minutes,
        "websocket_ping_interval_seconds": default_settings.websocket_ping_interval_seconds,
        "websocket_max_connections_per_user": default_settings.websocket_max_connections_per_user,
        "max_workers": default_settings.max_workers,
        "max_requests_per_worker": default_settings.max_requests_per_worker,
        "request_timeout_seconds": default_settings.request_timeout_seconds,
        "enable_metrics": default_settings.enable_metrics,
        "metrics_port": default_settings.metrics_port,
        "health_check_interval_seconds": default_settings.health_check_interval_seconds,
        "enable_vector_search": default_settings.enable_vector_search,
        "enable_caching": default_settings.enable_caching,
        "enable_streaming": default_settings.enable_streaming,
        "enable_tool_use": default_settings.enable_tool_use,
        "enable_retry_mechanism": default_settings.enable_retry_mechanism,
        "development_mode": default_settings.development_mode,
        "enable_swagger": default_settings.enable_swagger,
        "enable_redoc": default_settings.enable_redoc,
        "auto_reload": default_settings.auto_reload,
        "log_file": default_settings.log_file,
        "log_max_size": default_settings.log_max_size,
        "log_backup_count": default_settings.log_backup_count,
        "log_level_console": default_settings.log_level_console,
        "log_level_file": default_settings.log_level_file
    }
    
    save_config_to_file(Settings(**config_data), config_path)
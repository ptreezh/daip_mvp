"""
系统配置管理
处理环境变量、配置文件和系统设置
"""

import os
from typing import Optional, Dict, Any
from pydantic import BaseSettings, Field
from pathlib import Path


class DatabaseConfig(BaseSettings):
    """数据库配置"""
    host: str = Field(default="localhost", env="DB_HOST")
    port: int = Field(default=5432, env="DB_PORT")
    database: str = Field(default="daip_live", env="DB_NAME")
    username: str = Field(default="postgres", env="DB_USER")
    password: str = Field(default="", env="DB_PASSWORD")
    pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    
    @property
    def url(self) -> str:
        """获取数据库连接URL"""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


class RedisConfig(BaseSettings):
    """Redis配置"""
    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    database: int = Field(default=0, env="REDIS_DB")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    max_connections: int = Field(default=20, env="REDIS_MAX_CONNECTIONS")
    
    @property
    def url(self) -> str:
        """获取Redis连接URL"""
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.database}"


class LLMConfig(BaseSettings):
    """LLM配置"""
    default_provider: str = Field(default="openai", env="LLM_PROVIDER")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_base_url: Optional[str] = Field(default=None, env="OPENAI_BASE_URL")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    
    # 模型配置
    default_model: str = Field(default="gpt-4", env="DEFAULT_MODEL")
    max_tokens: int = Field(default=4000, env="MAX_TOKENS")
    temperature: float = Field(default=0.7, env="TEMPERATURE")
    
    # 速率限制
    requests_per_minute: int = Field(default=60, env="REQUESTS_PER_MINUTE")
    tokens_per_minute: int = Field(default=100000, env="TOKENS_PER_MINUTE")


class SystemConfig(BaseSettings):
    """系统配置"""
    # 基础设置
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    secret_key: str = Field(default="dev-secret-key", env="SECRET_KEY")
    
    # 服务器设置
    host: str = Field(default="127.0.0.1", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=1, env="WORKERS")
    
    # 文件路径
    data_dir: Path = Field(default=Path("data"), env="DATA_DIR")
    logs_dir: Path = Field(default=Path("logs"), env="LOGS_DIR")
    models_dir: Path = Field(default=Path("models"), env="MODELS_DIR")
    
    # 功能开关
    enable_analytics: bool = Field(default=True, env="ENABLE_ANALYTICS")
    enable_caching: bool = Field(default=True, env="ENABLE_CACHING")
    enable_monitoring: bool = Field(default=True, env="ENABLE_MONITORING")
    
    # 性能设置
    max_concurrent_workflows: int = Field(default=10, env="MAX_CONCURRENT_WORKFLOWS")
    workflow_timeout: int = Field(default=3600, env="WORKFLOW_TIMEOUT")  # 秒
    memory_retention_days: int = Field(default=30, env="MEMORY_RETENTION_DAYS")
    
    # 透明度设置
    transparency_level: str = Field(default="moderate", env="TRANSPARENCY_LEVEL")
    log_llm_calls: bool = Field(default=True, env="LOG_LLM_CALLS")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class AppConfig:
    """应用配置管理器"""
    
    def __init__(self):
        self.system = SystemConfig()
        self.database = DatabaseConfig()
        self.redis = RedisConfig()
        self.llm = LLMConfig()
        
        # 确保必要的目录存在
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        directories = [
            self.system.data_dir,
            self.system.logs_dir,
            self.system.models_dir,
            self.system.data_dir / "wiki",
            self.system.data_dir / "memory",
            self.system.data_dir / "workflows",
            self.system.data_dir / "sessions"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_llm_config(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """获取LLM配置"""
        provider = provider or self.llm.default_provider
        
        config = {
            "provider": provider,
            "model": self.llm.default_model,
            "max_tokens": self.llm.max_tokens,
            "temperature": self.llm.temperature,
            "requests_per_minute": self.llm.requests_per_minute,
            "tokens_per_minute": self.llm.tokens_per_minute
        }
        
        if provider == "openai":
            config.update({
                "api_key": self.llm.openai_api_key,
                "base_url": self.llm.openai_base_url
            })
        elif provider == "anthropic":
            config.update({
                "api_key": self.llm.anthropic_api_key
            })
        elif provider == "ollama":
            config.update({
                "base_url": self.llm.ollama_base_url
            })
        
        return config
    
    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        return {
            "url": self.database.url,
            "pool_size": self.database.pool_size,
            "max_overflow": self.database.max_overflow
        }
    
    def get_redis_config(self) -> Dict[str, Any]:
        """获取Redis配置"""
        return {
            "url": self.redis.url,
            "max_connections": self.redis.max_connections
        }
    
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.system.debug
    
    def is_production(self) -> bool:
        """是否为生产环境"""
        return not self.system.debug


# 全局配置实例
config = AppConfig()


def get_config() -> AppConfig:
    """获取配置实例"""
    return config


def reload_config():
    """重新加载配置"""
    global config
    config = AppConfig()
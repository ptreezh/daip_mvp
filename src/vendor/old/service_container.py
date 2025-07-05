"""服务容器和依赖注入系统
实现解耦架构，统一管理所有服务组件
"""

import logging
import os
from pathlib import Path
from typing import Any, Optional, TypeVar

# 自动加载 .env 文件
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from src.expert_library import ExpertLibrary
from src.interfaces import (
    IChatService,
    IMemoryService,
    IModelService,
    IRecommendationService,
    IRoleService,
)
from src.lightweight_memory_service import LightweightMemoryService
from src.model_monitor import ModelMonitor
from src.multi_model_adapter import MultiModelManager
from src.multi_role_chat import MultiRoleChatEngine
from src.role_memory_bank import RoleMemoryBank
from src.unified_services import (
    UnifiedChatService,
    UnifiedMemoryService,
    UnifiedModelService,
    UnifiedRecommendationService,
    UnifiedRoleService,
)
from src.utils import load_config

T = TypeVar("T")


class ServiceContainer:
    """服务容器 - 管理所有服务的生命周期和依赖关系"""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or load_config()
        self.services: dict[str, Any] = {}
        self.singletons: dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)

        # 初始化基础配置
        self._init_config()

        # 注册服务
        self._register_services()

    def _init_config(self):
        """初始化配置"""
        default_config = {
            "data_dir": "data",
            "memory_bank_dir": "data/memory_banks",
            "roles_dir": "roles",
            "default_model": "ollama",
            "ollama_base_url": "http://localhost:11434",
            "ollama_model": "gemma3:latest",
        }

        # 合并配置
        for key, value in default_config.items():
            if key not in self.config:
                self.config[key] = value

    def _register_services(self):
        """注册所有服务"""
        # 注册基础组件（单例）
        self.register_singleton("memory_bank", self._create_memory_bank)
        self.register_singleton("expert_library", self._create_expert_library)
        self.register_singleton("model_manager", self._create_model_manager)
        self.register_singleton("chat_engine", self._create_chat_engine)
        self.register_singleton("model_monitor", self._create_model_monitor)

        # 注册统一服务（单例）
        self.register_singleton("memory_service", self._create_memory_service)
        self.register_singleton(
            "lightweight_memory_service",
            self._create_lightweight_memory_service,
        )
        self.register_singleton("role_service", self._create_role_service)
        self.register_singleton(
            "recommendation_service",
            self._create_recommendation_service,
        )
        self.register_singleton("model_service", self._create_model_service)
        self.register_singleton("chat_service", self._create_chat_service)

    def register_singleton(self, name: str, factory_func):
        """注册单例服务"""
        self.services[name] = factory_func

    def register_transient(self, name: str, factory_func):
        """注册瞬态服务"""
        self.services[name] = factory_func

    def get(self, service_name: str) -> Any:
        """获取服务实例"""
        if service_name in self.singletons:
            return self.singletons[service_name]

        if service_name not in self.services:
            raise ValueError(f"Service '{service_name}' not registered")

        # 创建服务实例
        factory_func = self.services[service_name]
        instance = factory_func()

        # 缓存单例
        self.singletons[service_name] = instance

        self.logger.info(f"Created service instance: {service_name}")
        return instance

    def get_memory_service(self) -> IMemoryService:
        """获取记忆服务"""
        return self.get("memory_service")

    def get_role_service(self) -> IRoleService:
        """获取角色服务"""
        return self.get("role_service")

    def get_recommendation_service(self) -> IRecommendationService:
        """获取推荐服务"""
        return self.get("recommendation_service")

    def get_chat_service(self) -> IChatService:
        """获取聊天服务"""
        return self.get("chat_service")

    def get_model_service(self) -> IModelService:
        """获取模型服务"""
        return self.get("model_service")

    def get_model_monitor(self) -> ModelMonitor:
        """获取模型监控服务"""
        return self.get("model_monitor")

    # 基础组件工厂方法
    def _create_memory_bank(self) -> RoleMemoryBank:
        """创建记忆银行"""
        return RoleMemoryBank(data_dir=self.config["memory_bank_dir"])

    def _create_expert_library(self) -> ExpertLibrary:
        """创建专家库"""
        expert_library = ExpertLibrary()

        # 加载专家数据
        roles_dir = Path(self.config["roles_dir"])
        if roles_dir.exists():
            try:
                expert_library.load_experts_from_directory(str(roles_dir))
                self.logger.info(f"Loaded experts from {roles_dir}")
            except Exception as e:
                self.logger.warning(f"Failed to load experts: {e}")

        return expert_library

    def _create_model_manager(self) -> MultiModelManager:
        """创建模型管理器"""
        memory_bank = self.get("memory_bank")
        model_manager = MultiModelManager(memory_bank)

        # 设置默认模型
        try:
            if self.config["default_model"] == "ollama":
                model_manager.setup_ollama(
                    base_url=self.config["ollama_base_url"],
                    model_name=self.config["ollama_model"],
                    is_default=True,
                )
                self.logger.info("Setup Ollama as default model")
        except Exception as e:
            self.logger.warning(f"Failed to setup default model: {e}")

        # 自动注册云模型适配器
        try:
            # OpenAI
            openai_key = (
                self.config.get("openai_api_key")
                or self.config.get("OPENAI_API_KEY")
                or os.getenv("OPENAI_API_KEY")
            )
            openai_model = self.config.get("openai_model", "gpt-3.5-turbo")
            if openai_key:
                model_manager.setup_openai(
                    api_key=openai_key,
                    model_name=openai_model,
                    is_default=False,
                )
                self.logger.info("Registered adapter: openai")
            # Anthropic
            anthropic_key = (
                self.config.get("anthropic_api_key")
                or self.config.get("ANTHROPIC_API_KEY")
                or os.getenv("ANTHROPIC_API_KEY")
            )
            anthropic_model = self.config.get(
                "anthropic_model",
                "claude-3-sonnet-20240229",
            )
            if anthropic_key:
                model_manager.setup_anthropic(
                    api_key=anthropic_key,
                    model_name=anthropic_model,
                    is_default=False,
                )
                self.logger.info("Registered adapter: anthropic")
            # SiliconFlow
            siliconflow_key = self.config.get("siliconflow_api_key") or os.getenv(
                "SILICONFLOW_API_KEY",
            )
            siliconflow_model = self.config.get(
                "siliconflow_model",
                "internlm/internlm2_5-7b-chat",
            )
            if siliconflow_key:
                model_manager.setup_siliconflow(
                    api_key=siliconflow_key,
                    model_name=siliconflow_model,
                    is_default=False,
                )
                self.logger.info("Registered adapter: siliconflow")
        except Exception as e:
            self.logger.warning(f"Failed to auto-register cloud adapters: {e}")

        return model_manager

    def _create_chat_engine(self) -> MultiRoleChatEngine:
        """创建聊天引擎"""
        expert_library = self.get("expert_library")
        return MultiRoleChatEngine(expert_library, self.config["default_model"])

    def _create_model_monitor(self) -> ModelMonitor:
        """创建模型监控服务"""
        return ModelMonitor(self.config)

    # 统一服务工厂方法
    def _create_memory_service(self) -> UnifiedMemoryService:
        """创建统一记忆服务"""
        memory_bank = self.get("memory_bank")
        return UnifiedMemoryService(memory_bank)

    def _create_role_service(self) -> UnifiedRoleService:
        """创建统一角色服务"""
        expert_library = self.get("expert_library")
        memory_service = self.get("memory_service")
        return UnifiedRoleService(expert_library, memory_service)

    def _create_recommendation_service(self) -> UnifiedRecommendationService:
        """创建统一推荐服务"""
        role_service = self.get("role_service")
        chat_engine = self.get("chat_engine")
        return UnifiedRecommendationService(role_service, chat_engine)

    def _create_model_service(self) -> UnifiedModelService:
        """创建统一模型服务"""
        model_manager = self.get("model_manager")
        memory_service = self.get("memory_service")
        return UnifiedModelService(model_manager, memory_service)

    def _create_chat_service(self) -> UnifiedChatService:
        """创建统一聊天服务"""
        chat_engine = self.get("chat_engine")
        memory_service = self.get("memory_service")
        model_service = self.get("model_service")
        return UnifiedChatService(chat_engine, memory_service, model_service)

    def _create_lightweight_memory_service(self) -> LightweightMemoryService:
        """创建轻量级记忆服务"""
        enable_redis = self.config.get("enable_redis_cache", False)
        redis_url = self.config.get("redis_url", "redis://localhost:6379")
        data_dir = self.config.get("lightweight_memory_dir", "data/lightweight_memory")

        return LightweightMemoryService(
            data_dir=data_dir,
            enable_redis=enable_redis,
            redis_url=redis_url,
        )

    def setup_models(self, model_configs: dict[str, dict[str, Any]]):
        """批量设置模型"""
        model_service = self.get_model_service()

        for model_name, config in model_configs.items():
            try:
                success = model_service.setup_model(model_name, config)
                if success:
                    self.logger.info(f"Successfully setup model: {model_name}")
                else:
                    self.logger.warning(f"Failed to setup model: {model_name}")
            except Exception as e:
                self.logger.error(f"Error setting up model {model_name}: {e}")

    def get_system_status(self) -> dict[str, Any]:
        """获取系统状态"""
        status = {
            "services": {},
            "config": self.config,
            "initialized_services": list(self.singletons.keys()),
        }

        # 检查各服务状态
        try:
            memory_service = self.get_memory_service()
            status["services"]["memory"] = {"status": "active"}
        except Exception as e:
            status["services"]["memory"] = {"status": "error", "error": str(e)}

        try:
            role_service = self.get_role_service()
            all_roles = role_service.get_all_roles(limit=1)
            status["services"]["roles"] = {
                "status": "active",
                "roles_available": len(all_roles) > 0,
            }
        except Exception as e:
            status["services"]["roles"] = {"status": "error", "error": str(e)}

        try:
            model_service = self.get_model_service()
            available_models = model_service.get_available_models()
            status["services"]["models"] = {
                "status": "active",
                "available_models": available_models,
            }
        except Exception as e:
            status["services"]["models"] = {"status": "error", "error": str(e)}

        return status

    def cleanup(self):
        """清理资源"""
        for service_name, service in self.singletons.items():
            try:
                if hasattr(service, "close"):
                    service.close()
                    self.logger.info(f"Cleaned up service: {service_name}")
            except Exception as e:
                self.logger.error(f"Error cleaning up service {service_name}: {e}")

        self.singletons.clear()


# 全局服务容器实例
_container: Optional[ServiceContainer] = None


def get_container(config: Optional[dict[str, Any]] = None) -> ServiceContainer:
    """获取全局服务容器"""
    global _container
    if _container is None:
        _container = ServiceContainer(config)
    return _container


def setup_container(config: dict[str, Any]) -> ServiceContainer:
    """设置全局服务容器"""
    global _container
    _container = ServiceContainer(config)
    return _container


def get_memory_service() -> IMemoryService:
    """快捷方法：获取记忆服务"""
    return get_container().get_memory_service()


def get_role_service() -> IRoleService:
    """快捷方法：获取角色服务"""
    return get_container().get_role_service()


def get_chat_service() -> IChatService:
    """快捷方法：获取聊天服务"""
    return get_container().get_chat_service()


def get_model_service() -> IModelService:
    """快捷方法：获取模型服务"""
    return get_container().get_model_service()


def get_recommendation_service() -> IRecommendationService:
    """快捷方法：获取推荐服务"""
    return get_container().get_recommendation_service()


def get_lightweight_memory_service() -> LightweightMemoryService:
    """快捷方法：获取轻量级记忆服务"""
    return get_container().get_lightweight_memory_service()

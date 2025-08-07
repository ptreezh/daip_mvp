# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-05 15:40:00
@Author  : DAIP-LIVE Team
@File    : graceful_degradation.py
@Description:
    Graceful degradation system for handling service failures gracefully.
"""

import logging
import time
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    FALLBACK = "fallback"


@dataclass
class ServiceHealth:
    """Health information for a service"""
    name: str
    status: ServiceStatus
    last_check: float
    error_message: Optional[str] = None
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    fallback_available: bool = True


@dataclass
class ServiceConfig:
    """Configuration for a service"""
    name: str
    is_critical: bool = False
    startup_timeout: float = 30.0
    health_check_interval: float = 60.0
    fallback_service: Optional[str] = None
    graceful_degradation_enabled: bool = True


class FallbackService:
    """Base class for fallback services"""
    
    def __init__(self, name: str):
        self.name = name
        self.is_fallback = True
    
    def get_capabilities(self) -> List[str]:
        """Get list of available capabilities in fallback mode"""
        return []
    
    def execute(self, operation: str, *args, **kwargs) -> Any:
        """Execute an operation in fallback mode"""
        raise NotImplementedError(f"Fallback operation '{operation}' not implemented")


class GracefulAppState:
    """Application state with graceful degradation capabilities"""
    
    def __init__(self):
        logger.info("🔄 Initializing application with graceful degradation...")
        
        # Service configurations
        self.service_configs = self._define_service_configs()
        
        # Service health tracking
        self.service_health: Dict[str, ServiceHealth] = {}
        
        # Service instances (both real and fallback)
        self.services: Dict[str, Any] = {}
        self.fallback_services: Dict[str, FallbackService] = {}
        
        # Performance metrics
        self.startup_time = time.time()
        self.initialization_errors: List[str] = []
        
        # Initialize services with graceful degradation
        self._initialize_services()
        
        logger.info("✅ Application initialized with graceful degradation")
    
    def _define_service_configs(self) -> Dict[str, ServiceConfig]:
        """Define service configurations"""
        return {
            # Critical services (must work, but can have fallbacks)
            "llm_interface": ServiceConfig(
                name="llm_interface",
                is_critical=True,
                fallback_service="mock_llm",
                graceful_degradation_enabled=True
            ),
            "memory_service": ServiceConfig(
                name="memory_service",
                is_critical=True,
                fallback_service="in_memory_memory",
                graceful_degradation_enabled=True
            ),
            "wiki_service": ServiceConfig(
                name="wiki_service",
                is_critical=True,
                fallback_service="simple_wiki",
                graceful_degradation_enabled=True
            ),
            "token_management_service": ServiceConfig(
                name="token_management_service",
                is_critical=True,
                fallback_service="simple_token_manager",
                graceful_degradation_enabled=True
            ),
            
            # Important but non-critical services
            "synthesis_engine": ServiceConfig(
                name="synthesis_engine",
                is_critical=False,
                graceful_degradation_enabled=True
            ),
            "expert_service": ServiceConfig(
                name="expert_service",
                is_critical=False,
                graceful_degradation_enabled=True
            ),
            "task_manager": ServiceConfig(
                name="task_manager",
                is_critical=False,
                graceful_degradation_enabled=True
            ),
            
            # Optional services
            "enhanced_memory_management": ServiceConfig(
                name="enhanced_memory_management",
                is_critical=False,
                graceful_degradation_enabled=True
            ),
            "knowledge_visualization": ServiceConfig(
                name="knowledge_visualization",
                is_critical=False,
                graceful_degradation_enabled=True
            ),
            
            # Scenario services
            "expert_consultation_scenario": ServiceConfig(
                name="expert_consultation_scenario",
                is_critical=False,
                graceful_degradation_enabled=True
            ),
            "academic_research_scenario": ServiceConfig(
                name="academic_research_scenario",
                is_critical=False,
                graceful_degradation_enabled=True
            ),
            "industry_analysis_scenario": ServiceConfig(
                name="industry_analysis_scenario",
                is_critical=False,
                graceful_degradation_enabled=True
            ),
        }
    
    def _initialize_services(self):
        """Initialize all services with graceful degradation"""
        # Initialize fallback services first
        self._initialize_fallback_services()
        
        # Initialize critical services
        self._initialize_critical_services()
        
        # Initialize non-critical services
        self._initialize_non_critical_services()
        
        # Initialize optional services
        self._initialize_optional_services()
    
    def _initialize_fallback_services(self):
        """Initialize fallback services"""
        logger.info("🛟 Initializing fallback services...")
        
        # Mock LLM fallback
        self.fallback_services["mock_llm"] = MockLLMFallback()
        
        # In-memory memory fallback
        self.fallback_services["in_memory_memory"] = InMemoryMemoryFallback()
        
        # Simple wiki fallback
        self.fallback_services["simple_wiki"] = SimpleWikiFallback()
        
        # Simple token manager fallback
        self.fallback_services["simple_token_manager"] = SimpleTokenManagerFallback()
        
        logger.info(f"✅ Initialized {len(self.fallback_services)} fallback services")
    
    def _initialize_critical_services(self):
        """Initialize critical services with fallback support"""
        logger.info("🔧 Initializing critical services...")
        
        critical_services = [
            ("config", self._initialize_config),
            ("llm_interface", self._initialize_llm_interface),
            ("memory_service", self._initialize_memory_service),
            ("wiki_service", self._initialize_wiki_service),
            ("token_management_service", self._initialize_token_management_service),
        ]
        
        for service_name, init_func in critical_services:
            self._initialize_service_with_fallback(service_name, init_func, is_critical=True)
    
    def _initialize_non_critical_services(self):
        """Initialize non-critical services"""
        logger.info("⚙️ Initializing non-critical services...")
        
        non_critical_services = [
            ("synthesis_engine", self._initialize_synthesis_engine),
            ("expert_service", self._initialize_expert_service),
            ("task_manager", self._initialize_task_manager),
        ]
        
        for service_name, init_func in non_critical_services:
            self._initialize_service_with_fallback(service_name, init_func, is_critical=False)
    
    def _initialize_optional_services(self):
        """Initialize optional services"""
        logger.info("🔍 Initializing optional services...")
        
        optional_services = [
            ("enhanced_memory_management", self._initialize_enhanced_memory_management),
            ("knowledge_visualization", self._initialize_knowledge_visualization),
            ("expert_consultation_scenario", self._initialize_expert_consultation_scenario),
            ("academic_research_scenario", self._initialize_academic_research_scenario),
            ("industry_analysis_scenario", self._initialize_industry_analysis_scenario),
        ]
        
        for service_name, init_func in optional_services:
            self._initialize_service_with_fallback(service_name, init_func, is_critical=False)
    
    def _initialize_service_with_fallback(self, service_name: str, init_func: Callable, is_critical: bool):
        """Initialize a service with fallback support"""
        config = self.service_configs.get(service_name)
        if not config:
            logger.warning(f"No configuration found for service: {service_name}")
            return
        
        start_time = time.time()
        
        try:
            service_instance = init_func()
            init_time = time.time() - start_time
            
            self.services[service_name] = service_instance
            self.service_health[service_name] = ServiceHealth(
                name=service_name,
                status=ServiceStatus.HEALTHY,
                last_check=time.time(),
                performance_metrics={"init_time": init_time},
                fallback_available=config.fallback_service is not None
            )
            
            logger.info(f"✅ {service_name} initialized successfully ({init_time:.3f}s)")
            
        except Exception as e:
            init_time = time.time() - start_time
            error_message = str(e)
            
            if config.fallback_service and config.fallback_service in self.fallback_services:
                # Use fallback service
                fallback_service = self.fallback_services[config.fallback_service]
                self.services[service_name] = fallback_service
                
                self.service_health[service_name] = ServiceHealth(
                    name=service_name,
                    status=ServiceStatus.FALLBACK,
                    last_check=time.time(),
                    error_message=error_message,
                    performance_metrics={"init_time": init_time},
                    fallback_available=True
                )
                
                logger.warning(f"⚠️ {service_name} failed, using fallback ({init_time:.3f}s): {error_message}")
                
            elif config.graceful_degradation_enabled and not is_critical:
                # Service is unavailable but not critical
                self.service_health[service_name] = ServiceHealth(
                    name=service_name,
                    status=ServiceStatus.UNAVAILABLE,
                    last_check=time.time(),
                    error_message=error_message,
                    performance_metrics={"init_time": init_time},
                    fallback_available=False
                )
                
                logger.warning(f"❌ {service_name} unavailable ({init_time:.3f}s): {error_message}")
                
            else:
                # Critical service failure
                self.initialization_errors.append(f"Critical service {service_name} failed: {error_message}")
                
                self.service_health[service_name] = ServiceHealth(
                    name=service_name,
                    status=ServiceStatus.UNAVAILABLE,
                    last_check=time.time(),
                    error_message=error_message,
                    performance_metrics={"init_time": init_time},
                    fallback_available=False
                )
                
                if is_critical:
                    logger.error(f"🚨 Critical service {service_name} failed: {error_message}")
                else:
                    logger.warning(f"❌ Service {service_name} failed: {error_message}")
    
    def get_service(self, service_name: str) -> Any:
        """Get a service instance, with fallback support"""
        if service_name in self.services:
            service = self.services[service_name]
            
            # Check if it's a fallback service and log appropriately
            if hasattr(service, 'is_fallback') and service.is_fallback:
                logger.info(f"🛟 Using fallback service for {service_name}")
            
            return service
        else:
            logger.warning(f"Service {service_name} not found")
            return None
    
    def get_service_health(self, service_name: str) -> Optional[ServiceHealth]:
        """Get health information for a service"""
        return self.service_health.get(service_name)
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        healthy_count = sum(1 for health in self.service_health.values() if health.status == ServiceStatus.HEALTHY)
        fallback_count = sum(1 for health in self.service_health.values() if health.status == ServiceStatus.FALLBACK)
        unavailable_count = sum(1 for health in self.service_health.values() if health.status == ServiceStatus.UNAVAILABLE)
        
        total_services = len(self.service_health)
        
        # Determine overall status
        if healthy_count == total_services:
            overall_status = "healthy"
        elif healthy_count + fallback_count == total_services:
            overall_status = "degraded"
        elif self.initialization_errors:
            overall_status = "critical"
        else:
            overall_status = "unhealthy"
        
        return {
            "status": overall_status,
            "total_services": total_services,
            "healthy_services": healthy_count,
            "fallback_services": fallback_count,
            "unavailable_services": unavailable_count,
            "initialization_errors": self.initialization_errors,
            "startup_time": time.time() - self.startup_time,
            "services": {
                name: {
                    "status": health.status.value,
                    "error_message": health.error_message,
                    "fallback_available": health.fallback_available,
                    "performance_metrics": health.performance_metrics
                }
                for name, health in self.service_health.items()
            }
        }
    
    # Service initialization methods
    def _initialize_config(self):
        """Initialize configuration"""
        from src.config import settings
        return settings
    
    def _initialize_llm_interface(self):
        """Initialize LLM interface"""
        from src.kernel.llm_interface import LLMFactory, LLMConfig
        from src.config import settings
        
        config = LLMConfig(
            provider=settings.llm.provider,
            model=settings.llm.ollama.generation_model,
            base_url=settings.llm.ollama.host
        )
        
        # Get token management service if available
        token_service = self.get_service("token_management_service")
        return LLMFactory.create(config=config, token_service=token_service)
    
    def _initialize_memory_service(self):
        """Initialize memory service"""
        from src.core_services.memory_service import MemoryService
        import os
        
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        data_dir = os.path.join(base_dir, "data", "memory_banks")
        
        return MemoryService(data_dir=data_dir)
    
    def _initialize_wiki_service(self):
        """Initialize wiki service"""
        from src.core_services.wiki_service import WikiService
        import os
        
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        wiki_dir = os.path.join(base_dir, "data", "wiki")
        
        return WikiService(wiki_directory=wiki_dir)
    
    def _initialize_token_management_service(self):
        """Initialize token management service"""
        from src.core_services.token_management_service import TokenManagementService
        from src.config import settings
        
        return TokenManagementService(settings.token_management)
    
    def _initialize_synthesis_engine(self):
        """Initialize synthesis engine"""
        from src.core_services.synthesis_engine import SynthesisEngine
        
        llm_interface = self.get_service("llm_interface")
        if llm_interface and not hasattr(llm_interface, 'is_fallback'):
            return SynthesisEngine(llm_interface=llm_interface)
        else:
            raise Exception("LLM interface not available for synthesis engine")
    
    def _initialize_expert_service(self):
        """Initialize expert service"""
        from src.core_services.expert_service import ExpertService
        
        return ExpertService(self)
    
    def _initialize_task_manager(self):
        """Initialize task manager"""
        from src.core_services.task_manager import TaskManager
        import os
        
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        task_dir = os.path.join(base_dir, "data", "tasks")
        
        return TaskManager(task_directory=task_dir)
    
    def _initialize_enhanced_memory_management(self):
        """Initialize enhanced memory management"""
        from src.core_services.enhanced_memory_management import EnhancedMemoryManagement
        
        memory_service = self.get_service("memory_service")
        if memory_service and not hasattr(memory_service, 'is_fallback'):
            return EnhancedMemoryManagement(memory_service)
        else:
            raise Exception("Memory service not available for enhanced memory management")
    
    def _initialize_knowledge_visualization(self):
        """Initialize knowledge visualization"""
        from src.core_services.knowledge_visualization_engine import KnowledgeVisualizationEngine
        
        memory_service = self.get_service("memory_service")
        if memory_service and not hasattr(memory_service, 'is_fallback'):
            return KnowledgeVisualizationEngine(memory_service)
        else:
            raise Exception("Memory service not available for knowledge visualization")
    
    def _initialize_expert_consultation_scenario(self):
        """Initialize expert consultation scenario"""
        from src.core_services.expert_consultation_scenario import ExpertConsultationScenario
        
        return ExpertConsultationScenario(self)
    
    def _initialize_academic_research_scenario(self):
        """Initialize academic research scenario"""
        from src.core_services.academic_research_scenario import AcademicResearchScenario
        
        return AcademicResearchScenario(self)
    
    def _initialize_industry_analysis_scenario(self):
        """Initialize industry analysis scenario"""
        from src.core_services.industry_analysis_scenario import IndustryAnalysisScenario
        
        return IndustryAnalysisScenario(self)


# Fallback service implementations
class MockLLMFallback(FallbackService):
    """Mock LLM fallback service"""
    
    def __init__(self):
        super().__init__("mock_llm")
    
    def get_capabilities(self) -> List[str]:
        return ["text_generation", "basic_analysis", "simple_responses"]
    
    def generate_response(self, prompt: str) -> str:
        return f"[FALLBACK] Mock response for: {prompt[:100]}..."
    
    def execute(self, operation: str, *args, **kwargs) -> Any:
        if operation == "generate_response":
            return self.generate_response(args[0])
        else:
            raise NotImplementedError(f"Mock LLM operation '{operation}' not implemented")


class InMemoryMemoryFallback(FallbackService):
    """In-memory memory fallback service"""
    
    def __init__(self):
        super().__init__("in_memory_memory")
        self.memory_storage = {}
    
    def get_capabilities(self) -> List[str]:
        return ["basic_storage", "simple_retrieval", "temporary_memory"]
    
    def store(self, key: str, value: Any):
        self.memory_storage[key] = value
    
    def retrieve(self, key: str) -> Any:
        return self.memory_storage.get(key)
    
    def execute(self, operation: str, *args, **kwargs) -> Any:
        if operation == "store":
            self.store(args[0], args[1])
        elif operation == "retrieve":
            return self.retrieve(args[0])
        else:
            raise NotImplementedError(f"In-memory memory operation '{operation}' not implemented")


class SimpleWikiFallback(FallbackService):
    """Simple wiki fallback service"""
    
    def __init__(self):
        super().__init__("simple_wiki")
        self.wiki_pages = {}
    
    def get_capabilities(self) -> List[str]:
        return ["basic_wiki", "simple_pages", "temporary_storage"]
    
    def create_page(self, title: str, content: str):
        self.wiki_pages[title] = content
    
    def get_page(self, title: str) -> Optional[str]:
        return self.wiki_pages.get(title)
    
    def execute(self, operation: str, *args, **kwargs) -> Any:
        if operation == "create_page":
            self.create_page(args[0], args[1])
        elif operation == "get_page":
            return self.get_page(args[0])
        else:
            raise NotImplementedError(f"Simple wiki operation '{operation}' not implemented")


class SimpleTokenManagerFallback(FallbackService):
    """Simple token manager fallback service"""
    
    def __init__(self):
        super().__init__("simple_token_manager")
        self.token_count = 0
        self.max_tokens = 1000000
    
    def get_capabilities(self) -> List[str]:
        return ["basic_tracking", "simple_limits", "token_counting"]
    
    def use_tokens(self, amount: int):
        self.token_count += amount
    
    def get_token_count(self) -> int:
        return self.token_count
    
    def execute(self, operation: str, *args, **kwargs) -> Any:
        if operation == "use_tokens":
            self.use_tokens(args[0])
        elif operation == "get_token_count":
            return self.get_token_count()
        else:
            raise NotImplementedError(f"Simple token manager operation '{operation}' not implemented")


if __name__ == "__main__":
    # Test the graceful degradation system
    import logging
    
    logging.basicConfig(level=logging.INFO)
    
    print("Testing Graceful Degradation System")
    print("=" * 50)
    
    try:
        app_state = GracefulAppState()
        
        health = app_state.get_system_health()
        print(f"\nSystem Status: {health['status'].upper()}")
        print(f"Healthy Services: {health['healthy_services']}/{health['total_services']}")
        print(f"Fallback Services: {health['fallback_services']}")
        print(f"Unavailable Services: {health['unavailable_services']}")
        print(f"Startup Time: {health['startup_time']:.3f}s")
        
        if health['initialization_errors']:
            print("\nInitialization Errors:")
            for error in health['initialization_errors']:
                print(f"  - {error}")
        
        print("\nService Health Details:")
        for service_name, service_info in health['services'].items():
            status_icon = "✅" if service_info['status'] == 'healthy' else "⚠️" if service_info['status'] == 'fallback' else "❌"
            print(f"  {status_icon} {service_name}: {service_info['status']}")
            if service_info['error_message']:
                print(f"     Error: {service_info['error_message']}")
        
    except Exception as e:
        print(f"Error testing graceful degradation: {e}")
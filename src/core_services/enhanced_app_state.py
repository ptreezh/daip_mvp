# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-05 16:00:00
@Author  : DAIP-LIVE Team
@File    : enhanced_app_state.py
@Description:
    Enhanced application state with UX improvements (health checks, graceful degradation, etc.).
"""

import logging
import time
from typing import Any, Optional
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import UX enhancement modules
from src.core_services.import_health_checker import ImportHealthChecker, validate_imports_on_startup
from src.core_services.user_friendly_errors import ErrorHandler, create_error_context, safe_import
from src.core_services.graceful_degradation import GracefulAppState
from src.core_services.startup_progress import StartupProgressTracker, startup_step, optional_startup_step
from src.core_services.self_healing_system import get_self_healing_system, auto_recover

logger = logging.getLogger(__name__)


class EnhancedAppState(GracefulAppState):
    """
    Enhanced application state with comprehensive UX improvements.
    Inherits from GracefulAppState and adds UX features.
    """
    
    def __init__(self, enable_ux_features: bool = True):
        self.enable_ux_features = enable_ux_features
        self.import_health_checker = ImportHealthChecker()
        self.error_handler = ErrorHandler()
        self.self_healing_system = get_self_healing_system()
        self.startup_tracker = None
        
        logger.info("🚀 Initializing Enhanced Application State with UX improvements...")
        
        # Initialize with UX features if enabled
        if self.enable_ux_features:
            self._initialize_with_ux_features()
        else:
            # Fallback to basic initialization
            super().__init__()
        
        logger.info("✅ Enhanced Application State initialization complete")
    
    def _initialize_with_ux_features(self):
        """Initialize with UX features enabled"""
        # Create startup progress tracker
        self.startup_tracker = StartupProgressTracker(
            enable_progress_bar=True,
            enable_logging=True
        )
        
        # Start progress tracking
        self.startup_tracker.start_progress_bar()
        
        try:
            # Phase 1: Pre-initialization with health checks
            self._phase_pre_initialization()
            
            # Phase 2: Critical services with enhanced error handling
            self._phase_critical_services()
            
            # Phase 3: Core services with graceful degradation
            self._phase_core_services()
            
            # Phase 4: Optional services with fallback support
            self._phase_optional_services()
            
            # Phase 5: Finalization with health validation
            self._phase_finalization()
            
        except Exception as e:
            # Use self-healing system to attempt recovery
            context = create_error_context(
                component="EnhancedAppState",
                operation="Initialization",
                user_action="Starting the DAIP-LIVE application with UX features"
            )
            
            user_friendly_error = self.error_handler.handle_error(e, context)
            
            # Log the error and attempt recovery
            logger.error(f"🚨 Enhanced initialization failed: {user_friendly_error}")
            
            # Attempt self-healing
            issue = self.self_healing_system.detect_issue(
                "initialization_error",
                "EnhancedAppState",
                str(e),
                "critical"
            )
            
            if not issue.resolved:
                # Fall back to basic initialization
                logger.warning("⚠️ Falling back to basic initialization...")
                super().__init__()
        
        finally:
            # Stop progress tracking
            if self.startup_tracker:
                self.startup_tracker.stop_progress_bar_thread()
                self.startup_tracker.print_startup_summary()
    
    @startup_step("configuration_loading")
    def _phase_pre_initialization(self):
        """Phase 1: Pre-initialization with import health checks"""
        logger.info("🔍 Phase 1: Pre-initialization and health checks")
        
        # Validate all critical imports
        import_success, import_results = self.import_health_checker.validate_all_imports()
        
        if not import_success:
            # Get user-friendly error message
            self.import_health_checker.raise_if_critical_failures()
        
        # Initialize basic configuration and paths
        self._initialize_basic_config()
        
        logger.info("✅ Pre-initialization complete")
    
    @startup_step("critical_services")
    def _phase_critical_services(self):
        """Phase 2: Critical services initialization"""
        logger.info("⚡ Phase 2: Critical services initialization")
        
        # Initialize critical services with enhanced error handling
        critical_services = [
            ("token_management_service", self._initialize_token_management_with_ux),
            ("llm_interface", self._initialize_llm_interface_with_ux),
            ("memory_service", self._initialize_memory_service_with_ux),
            ("wiki_service", self._initialize_wiki_service_with_ux),
        ]
        
        for service_name, init_func in critical_services:
            try:
                self.startup_tracker.start_step(service_name)
                init_func()
                self.startup_tracker.complete_step(service_name, success=True)
            except Exception as e:
                self.startup_tracker.complete_step(service_name, success=False, error_message=str(e))
                raise
        
        logger.info("✅ Critical services initialization complete")
    
    @startup_step("core_services")
    def _phase_core_services(self):
        """Phase 3: Core services initialization"""
        logger.info("🔧 Phase 3: Core services initialization")
        
        # Initialize core services with graceful degradation
        core_services = [
            ("synthesis_engine", self._initialize_synthesis_engine_with_ux),
            ("expert_service", self._initialize_expert_service_with_ux),
            ("task_manager", self._initialize_task_manager_with_ux),
        ]
        
        for service_name, init_func in core_services:
            try:
                self.startup_tracker.start_step(service_name)
                result = init_func()
                if result is not None:
                    self.startup_tracker.complete_step(service_name, success=True)
                else:
                    self.startup_tracker.skip_step(service_name, "Service not available")
            except Exception as e:
                self.startup_tracker.complete_step(service_name, success=False, error_message=str(e))
                # Continue with other services (graceful degradation)
                logger.warning(f"⚠️ Core service {service_name} failed, continuing...")
        
        logger.info("✅ Core services initialization complete")
    
    @optional_startup_step("optional_services")
    def _phase_optional_services(self):
        """Phase 4: Optional services initialization"""
        logger.info("🔍 Phase 4: Optional services initialization")
        
        # Initialize optional services with fallback support
        optional_services = [
            ("enhanced_memory_management", self._initialize_enhanced_memory_with_ux),
            ("knowledge_visualization", self._initialize_knowledge_visualization_with_ux),
            ("role_definitions", self._initialize_role_definitions_with_ux),
        ]
        
        for service_name, init_func in optional_services:
            try:
                self.startup_tracker.start_step(service_name)
                result = init_func()
                if result is not None:
                    self.startup_tracker.complete_step(service_name, success=True)
                else:
                    self.startup_tracker.skip_step(service_name, "Service not available")
            except Exception as e:
                self.startup_tracker.skip_step(service_name, reason=str(e))
        
        logger.info("✅ Optional services initialization complete")
    
    @startup_step("finalization")
    def _phase_finalization(self):
        """Phase 5: Finalization and health validation"""
        logger.info("✅ Phase 5: Finalization and health validation")
        
        # Perform final health check
        self._perform_final_health_check()
        
        # Log startup summary
        self._log_startup_summary()
        
        logger.info("✅ Finalization complete")
    
    def _initialize_basic_config(self):
        """Initialize basic configuration with UX error handling"""
        try:
            from src.config import settings
            self.settings = settings
            
            # Set up basic paths
            self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            self.roles_dir = os.path.join(self.base_dir, "roles")
            self.data_dir = os.path.join(self.base_dir, "data")
            
            # Create directories
            os.makedirs(self.roles_dir, exist_ok=True)
            os.makedirs(self.data_dir, exist_ok=True)
            
        except Exception as e:
            context = create_error_context(
                component="Configuration",
                operation="Basic configuration loading",
                user_action="Loading system configuration"
            )
            user_friendly_error = self.error_handler.handle_error(e, context)
            raise user_friendly_error
    
    @auto_recover
    def _initialize_token_management_with_ux(self):
        """Initialize token management service with UX features"""
        try:
            from src.core_services.token_management_service import TokenManagementService
            
            service = TokenManagementService(self.settings.token_management)
            self.services["token_management_service"] = service
            
            logger.info("✅ Token management service initialized with UX features")
            
        except Exception as e:
            context = create_error_context(
                component="TokenManagementService",
                operation="Service initialization",
                user_action="Starting token management service"
            )
            user_friendly_error = self.error_handler.handle_error(e, context)
            raise user_friendly_error
    
    @auto_recover
    def _initialize_llm_interface_with_ux(self):
        """Initialize LLM interface with UX features"""
        try:
            from src.kernel.llm_interface import LLMFactory, LLMConfig
            
            config = LLMConfig(
                provider=self.settings.llm.provider,
                model=self.settings.llm.ollama.generation_model,
                base_url=self.settings.llm.ollama.host
            )
            
            # Get token management service if available
            token_service = self.get_service("token_management_service")
            
            service = LLMFactory.create(config=config, token_service=token_service)
            self.services["llm_interface"] = service
            
            logger.info("✅ LLM interface initialized with UX features")
            
        except Exception as e:
            context = create_error_context(
                component="LLMInterface",
                operation="Service initialization",
                user_action="Starting LLM interface"
            )
            user_friendly_error = self.error_handler.handle_error(e, context)
            raise user_friendly_error
    
    @auto_recover
    def _initialize_memory_service_with_ux(self):
        """Initialize memory service with UX features"""
        try:
            from src.core_services.memory_service import MemoryService
            
            data_dir = os.path.join(self.data_dir, "memory_banks")
            service = MemoryService(data_dir=data_dir)
            self.services["memory_service"] = service
            
            logger.info("✅ Memory service initialized with UX features")
            
        except Exception as e:
            context = create_error_context(
                component="MemoryService",
                operation="Service initialization",
                user_action="Starting memory service"
            )
            user_friendly_error = self.error_handler.handle_error(e, context)
            raise user_friendly_error
    
    @auto_recover
    def _initialize_wiki_service_with_ux(self):
        """Initialize wiki service with UX features"""
        try:
            from src.core_services.wiki_service import WikiService
            
            wiki_dir = os.path.join(self.data_dir, "wiki")
            service = WikiService(wiki_directory=wiki_dir)
            self.services["wiki_service"] = service
            
            logger.info("✅ Wiki service initialized with UX features")
            
        except Exception as e:
            context = create_error_context(
                component="WikiService",
                operation="Service initialization",
                user_action="Starting wiki service"
            )
            user_friendly_error = self.error_handler.handle_error(e, context)
            raise user_friendly_error
    
    def _initialize_synthesis_engine_with_ux(self):
        """Initialize synthesis engine with UX features"""
        try:
            from src.core_services.synthesis_engine import SynthesisEngine
            
            llm_interface = self.get_service("llm_interface")
            if llm_interface and not hasattr(llm_interface, 'is_fallback'):
                service = SynthesisEngine(llm_interface=llm_interface)
                self.services["synthesis_engine"] = service
                return service
            else:
                logger.warning("⚠️ LLM interface not available for synthesis engine")
                return None
                
        except Exception as e:
            logger.warning(f"⚠️ Synthesis engine initialization failed: {e}")
            return None
    
    def _initialize_expert_service_with_ux(self):
        """Initialize expert service with UX features"""
        try:
            from src.core_services.expert_service import ExpertService
            
            service = ExpertService(self)
            self.services["expert_service"] = service
            return service
            
        except Exception as e:
            logger.warning(f"⚠️ Expert service initialization failed: {e}")
            return None
    
    def _initialize_task_manager_with_ux(self):
        """Initialize task manager with UX features"""
        try:
            from src.core_services.task_manager import TaskManager
            
            task_dir = os.path.join(self.data_dir, "tasks")
            service = TaskManager(task_directory=task_dir)
            self.services["task_manager"] = service
            return service
            
        except Exception as e:
            logger.warning(f"⚠️ Task manager initialization failed: {e}")
            return None
    
    def _initialize_enhanced_memory_with_ux(self):
        """Initialize enhanced memory management with UX features"""
        try:
            from src.core_services.enhanced_memory_management import EnhancedMemoryManagement
            
            memory_service = self.get_service("memory_service")
            if memory_service and not hasattr(memory_service, 'is_fallback'):
                service = EnhancedMemoryManagement(memory_service)
                self.services["enhanced_memory_management"] = service
                return service
            else:
                logger.warning("⚠️ Memory service not available for enhanced memory management")
                return None
                
        except Exception as e:
            logger.warning(f"⚠️ Enhanced memory management initialization failed: {e}")
            return None
    
    def _initialize_knowledge_visualization_with_ux(self):
        """Initialize knowledge visualization with UX features"""
        try:
            from src.core_services.knowledge_visualization_engine import KnowledgeVisualizationEngine
            
            memory_service = self.get_service("memory_service")
            if memory_service and not hasattr(memory_service, 'is_fallback'):
                service = KnowledgeVisualizationEngine(memory_service)
                self.services["knowledge_visualization"] = service
                return service
            else:
                logger.warning("⚠️ Memory service not available for knowledge visualization")
                return None
                
        except Exception as e:
            logger.warning(f"⚠️ Knowledge visualization initialization failed: {e}")
            return None
    
    def _initialize_role_definitions_with_ux(self):
        """Initialize role definitions with UX features"""
        try:
            # Load role definitions
            import glob
            import json
            
            role_files = glob.glob(os.path.join(self.roles_dir, "*.json"))
            loaded_roles = 0
            
            for role_file in role_files:
                try:
                    with open(role_file, 'r', encoding='utf-8') as f:
                        role_data = json.load(f)
                    loaded_roles += 1
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load role file {role_file}: {e}")
            
            logger.info(f"✅ Loaded {loaded_roles} role definitions")
            return loaded_roles
            
        except Exception as e:
            logger.warning(f"⚠️ Role definitions initialization failed: {e}")
            return None
    
    def _perform_final_health_check(self):
        """Perform final health check"""
        logger.info("🔍 Performing final health check...")
        
        # Check import health
        import_health = self.import_health_checker.get_health_summary()
        logger.info(f"📊 Import health: {import_health['status']}")
        
        # Check self-healing system
        healing_health = self.self_healing_system.get_system_health()
        logger.info(f"🔧 Self-healing health: {healing_health['successful_recoveries']}/{healing_health['recovery_attempts']} recoveries")
        
        # Check service health
        service_health = self.get_system_health()
        logger.info(f"⚙️ Service health: {service_health['status']}")
        
        # Log any issues
        if import_health['status'] != 'healthy':
            logger.warning("⚠️ Import health issues detected")
        
        if service_health['status'] != 'healthy':
            logger.warning("⚠️ Service health issues detected")
        
        logger.info("✅ Final health check complete")
    
    def _log_startup_summary(self):
        """Log startup summary"""
        startup_time = time.time() - self.startup_tracker.progress.start_time if self.startup_tracker else 0
        
        logger.info("🎉 DAIP-LIVE Startup Summary")
        logger.info("=" * 50)
        logger.info(f"⏱️ Total startup time: {startup_time:.2f}s")
        logger.info(f"✅ UX features enabled: {self.enable_ux_features}")
        logger.info(f"🔧 Self-healing enabled: {self.self_healing_system.healing_enabled}")
        logger.info(f"📊 Services available: {len([s for s in self.services.values() if s is not None])}")
        
        if self.startup_tracker:
            summary = self.startup_tracker.get_progress_summary()
            logger.info(f"📈 Startup progress: {summary['completed_steps']}/{summary['total_steps']} steps")
        
        logger.info("=" * 50)
    
    def get_enhanced_system_status(self) -> Dict[str, Any]:
        """Get enhanced system status with UX information"""
        base_status = self.get_system_health()
        
        # Add UX-specific information
        enhanced_status = {
            **base_status,
            "ux_features": {
                "enabled": self.enable_ux_features,
                "import_health": self.import_health_checker.get_health_summary(),
                "self_healing": self.self_healing_system.get_system_health(),
                "startup_progress": self.startup_tracker.get_progress_summary() if self.startup_tracker else None
            },
            "user_experience": {
                "graceful_degradation_enabled": True,
                "error_handling_enhanced": True,
                "startup_feedback_enabled": True,
                "auto_recovery_enabled": self.self_healing_system.auto_recovery
            }
        }
        
        return enhanced_status
    
    def get_user_friendly_status(self) -> str:
        """Get a user-friendly status message"""
        status = self.get_enhanced_system_status()
        
        if status["status"] == "healthy":
            return "🟢 System is running normally with all UX features enabled"
        elif status["status"] == "degraded":
            return "🟡 System is running in degraded mode with some UX features limited"
        elif status["status"] == "critical":
            return "🔴 System has critical issues but basic functionality is maintained"
        else:
            return "🔴 System is experiencing issues and may have limited functionality"


# Convenience function for creating enhanced app state
def create_enhanced_app_state(enable_ux_features: bool = True) -> EnhancedAppState:
    """Create an enhanced application state instance"""
    return EnhancedAppState(enable_ux_features=enable_ux_features)


if __name__ == "__main__":
    # Test the enhanced application state
    import logging
    
    logging.basicConfig(level=logging.INFO)
    
    print("Testing Enhanced Application State")
    print("=" * 50)
    
    try:
        app_state = create_enhanced_app_state(enable_ux_features=True)
        
        # Get system status
        status = app_state.get_enhanced_system_status()
        print(f"\nSystem Status: {status['status'].upper()}")
        print(f"UX Features: {'Enabled' if status['ux_features']['enabled'] else 'Disabled'}")
        print(f"Self-Healing: {'Enabled' if status['ux_features']['self_healing']['self_healing_enabled'] else 'Disabled'}")
        
        # Get user-friendly status
        user_status = app_state.get_user_friendly_status()
        print(f"\nUser Status: {user_status}")
        
        print("\n✅ Enhanced application state test completed successfully!")
        
    except Exception as e:
        print(f"❌ Enhanced application state test failed: {e}")
        import traceback
        traceback.print_exc()
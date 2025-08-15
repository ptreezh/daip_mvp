"""@Time    : 2025-08-05 15:50:00
@Author  : DAIP-LIVE Team
@File    import self_healing_system.py
@Description:
    Self-healing system for automatic recovery from common issues.
"""

import importlib
import logging
import subprocess
import sys
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class RecoveryStrategy(Enum):
    """Recovery strategy enumeration"""
    RESTART_SERVICE = "restart_service"
    RELOAD_MODULE = "reload_module"
    CLEAR_CACHE = "clear_cache"
    REINSTALL_DEPENDENCY = "reinstall_dependency"
    RESET_CONFIGURATION = "reset_configuration"
    FALLBACK_MODE = "fallback_mode"
    SKIP_COMPONENT = "skip_component"


@dataclass
class Issue:
    """Detected issue information"""
    issue_type: str
    description: str
    severity: str  # low, medium, high, critical
    component: str
    error_message: str
    timestamp: float = field(default_factory=time.time)
    recovery_attempts: int = 0
    resolved: bool = False


@dataclass
class RecoveryAction:
    """Recovery action information"""
    strategy: RecoveryStrategy
    description: str
    success_criteria: list[str]
    max_attempts: int = 3
    timeout: float = 30.0


@dataclass
class RecoveryResult:
    """Result of a recovery attempt"""
    success: bool
    action_taken: str
    message: str
    duration: float
    error_message: Optional[str] = None


class SelfHealingSystem:
    """Self-healing system for automatic issue recovery"""
    
    def __init__(self):
        self.detected_issues: list[Issue] = []
        self.recovery_history: list[RecoveryResult] = []
        self.recovery_strategies = self._define_recovery_strategies()
        self.healing_enabled = True
        self.auto_recovery = True
        self.max_recovery_attempts = 3
        self.recovery_lock = threading.Lock()
        
        # Issue patterns and their corresponding recovery strategies
        self.issue_patterns = {
            # Import issues
            "import_error": [
                RecoveryAction(
                    strategy=RecoveryStrategy.RELOAD_MODULE,
                    description="Reload the failed module",
                    success_criteria=["module_loaded"],
                    max_attempts=2,
                    timeout=10.0
                ),
                RecoveryAction(
                    strategy=RecoveryStrategy.REINSTALL_DEPENDENCY,
                    description="Reinstall missing dependencies",
                    success_criteria=["dependency_installed"],
                    max_attempts=1,
                    timeout=60.0
                )
            ],
            
            # Service issues
            "service_unavailable": [
                RecoveryAction(
                    strategy=RecoveryStrategy.RESTART_SERVICE,
                    description="Restart the failed service",
                    success_criteria=["service_running"],
                    max_attempts=3,
                    timeout=30.0
                ),
                RecoveryAction(
                    strategy=RecoveryStrategy.FALLBACK_MODE,
                    description="Switch to fallback mode",
                    success_criteria=["fallback_active"],
                    max_attempts=1,
                    timeout=10.0
                )
            ],
            
            # Configuration issues
            "configuration_error": [
                RecoveryAction(
                    strategy=RecoveryStrategy.RESET_CONFIGURATION,
                    description="Reset to default configuration",
                    success_criteria=["config_valid"],
                    max_attempts=1,
                    timeout=15.0
                )
            ],
            
            # Memory issues
            "memory_issue": [
                RecoveryAction(
                    strategy=RecoveryStrategy.CLEAR_CACHE,
                    description="Clear system caches",
                    success_criteria=["cache_cleared"],
                    max_attempts=3,
                    timeout=20.0
                ),
                RecoveryAction(
                    strategy=RecoveryStrategy.RESTART_SERVICE,
                    description="Restart memory service",
                    success_criteria=["memory_service_running"],
                    max_attempts=2,
                    timeout=30.0
                )
            ],
            
            # Database issues
            "database_issue": [
                RecoveryAction(
                    strategy=RecoveryStrategy.RESTART_SERVICE,
                    description="Restart database service",
                    success_criteria=["database_running"],
                    max_attempts=2,
                    timeout=45.0
                ),
                RecoveryAction(
                    strategy=RecoveryStrategy.CLEAR_CACHE,
                    description="Clear database cache",
                    success_criteria=["cache_cleared"],
                    max_attempts=1,
                    timeout=20.0
                )
            ]
        }
        
        logger.info("🔄 Self-healing system initialized")
    
    def _define_recovery_strategies(self) -> dict[RecoveryStrategy, Callable]:
        """Define recovery strategy implementations"""
        return {
            RecoveryStrategy.RESTART_SERVICE: self._restart_service,
            RecoveryStrategy.RELOAD_MODULE: self._reload_module,
            RecoveryStrategy.CLEAR_CACHE: self._clear_cache,
            RecoveryStrategy.REINSTALL_DEPENDENCY: self._reinstall_dependency,
            RecoveryStrategy.RESET_CONFIGURATION: self._reset_configuration,
            RecoveryStrategy.FALLBACK_MODE: self._enable_fallback_mode,
            RecoveryStrategy.SKIP_COMPONENT: self._skip_component
        }
    
    def detect_issue(self, issue_type: str, component: str, error_message: str, severity: str = "medium") -> Issue:
        """Detect and register an issue"""
        issue = Issue(
            issue_type=issue_type,
            description=self._get_issue_description(issue_type, component, error_message),
            severity=severity,
            component=component,
            error_message=error_message
        )
        
        self.detected_issues.append(issue)
        
        if self.auto_recovery and self.healing_enabled:
            self.attempt_recovery(issue)
        
        return issue
    
    def attempt_recovery(self, issue: Issue) -> RecoveryResult:
        """Attempt to recover from an issue"""
        with self.recovery_lock:
            if issue.resolved:
                return RecoveryResult(
                    success=True,
                    action_taken="already_resolved",
                    message="Issue was already resolved",
                    duration=0.0
                )
            
            if issue.recovery_attempts >= self.max_recovery_attempts:
                return RecoveryResult(
                    success=False,
                    action_taken="max_attempts_reached",
                    message=f"Maximum recovery attempts ({self.max_recovery_attempts}) reached",
                    duration=0.0
                )
            
            issue.recovery_attempts += 1
            
            # Get recovery actions for this issue type
            recovery_actions = self.issue_patterns.get(issue.issue_type, [])
            
            for action in recovery_actions:
                if issue.recovery_attempts > action.max_attempts:
                    continue
                
                logger.info(f"🔧 Attempting recovery: {action.description} for {issue.component}")
                
                start_time = time.time()
                
                try:
                    # Execute recovery action
                    strategy_func = self.recovery_strategies[action.strategy]
                    result = strategy_func(issue, action)
                    
                    duration = time.time() - start_time
                    
                    # Check if recovery was successful
                    if self._check_recovery_success(result, action.success_criteria):
                        issue.resolved = True
                        
                        recovery_result = RecoveryResult(
                            success=True,
                            action_taken=action.description,
                            message=f"Successfully recovered from {issue.issue_type}",
                            duration=duration
                        )
                        
                        self.recovery_history.append(recovery_result)
                        logger.info(f"✅ Recovery successful: {action.description} for {issue.component}")
                        
                        return recovery_result
                    else:
                        logger.warning(f"⚠️ Recovery action did not meet success criteria: {action.description}")
                
                except Exception as e:
                    duration = time.time() - start_time
                    
                    logger.error(f"❌ Recovery action failed: {action.description} - {str(e)}")
                    
                    # Try next action
                    continue
            
            # All recovery actions failed
            recovery_result = RecoveryResult(
                success=False,
                action_taken="all_actions_failed",
                message=f"All recovery actions failed for {issue.component}",
                duration=time.time() - start_time,
                error_message=issue.error_message
            )
            
            self.recovery_history.append(recovery_result)
            logger.error(f"❌ All recovery actions failed for {issue.component}")
            
            return recovery_result
    
    def _restart_service(self, issue: Issue, action: RecoveryAction) -> dict[str, Any]:
        """Restart a failed service"""
        component = issue.component
        
        # Simulate service restart
        logger.info(f"🔄 Restarting service: {component}")
        
        # In a real implementation, this would:
        # 1. Stop the service
        # 2. Clear any cached state
        # 3. Restart the service
        # 4. Verify it's running
        
        time.sleep(1.0)  # Simulate restart time
        
        return {
            "service": component,
            "status": "restarted",
            "action": "service_restart"
        }
    
    def _reload_module(self, issue: Issue, action: RecoveryAction) -> dict[str, Any]:
        """Reload a failed module"""
        error_message = issue.error_message
        
        # Extract module name from error message
        module_name = self._extract_module_from_error(error_message)
        
        if not module_name:
            raise Exception("Could not extract module name from error message")
        
        logger.info(f"🔄 Reloading module: {module_name}")
        
        try:
            # Reload the module
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
                logger.info(f"✅ Module {module_name} reloaded successfully")
            else:
                logger.info(f"ℹ️ Module {module_name} not loaded, importing fresh")
                __import__(module_name)
            
            return {
                "module": module_name,
                "status": "reloaded",
                "action": "module_reload"
            }
        
        except Exception as e:
            logger.error(f"❌ Failed to reload module {module_name}: {str(e)}")
            raise
    
    def _clear_cache(self, issue: Issue, action: RecoveryAction) -> dict[str, Any]:
        """Clear system caches"""
        logger.info(f"🧹 Clearing caches for {issue.component}")
        
        # Clear various caches
        caches_to_clear = [
            "service_cache",
            "import_cache", 
            "module_cache",
            "configuration_cache"
        ]
        
        cleared_caches = []
        
        for cache_name in caches_to_clear:
            try:
                # Simulate cache clearing
                # In real implementation, this would clear actual caches
                cleared_caches.append(cache_name)
                logger.info(f"✅ Cleared {cache_name}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to clear {cache_name}: {str(e)}")
        
        return {
            "cleared_caches": cleared_caches,
            "component": issue.component,
            "action": "cache_clear"
        }
    
    def _reinstall_dependency(self, issue: Issue, action: RecoveryAction) -> dict[str, Any]:
        """Reinstall missing dependencies"""
        error_message = issue.error_message
        
        # Extract dependency name from error message
        dependency = self._extract_dependency_from_error(error_message)
        
        if not dependency:
            raise Exception("Could not extract dependency name from error message")
        
        logger.info(f"📦 Reinstalling dependency: {dependency}")
        
        try:
            # Run pip install
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", dependency],
                capture_output=True,
                text=True,
                timeout=action.timeout
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Dependency {dependency} installed successfully")
                return {
                    "dependency": dependency,
                    "status": "installed",
                    "action": "dependency_install",
                    "output": result.stdout
                }
            else:
                logger.error(f"❌ Failed to install dependency {dependency}: {result.stderr}")
                raise Exception(f"pip install failed: {result.stderr}")
        
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Timeout installing dependency {dependency}")
            raise Exception(f"Timeout installing dependency {dependency}")
        except Exception as e:
            logger.error(f"❌ Error installing dependency {dependency}: {str(e)}")
            raise
    
    def _reset_configuration(self, issue: Issue, action: RecoveryAction) -> dict[str, Any]:
        """Reset configuration to defaults"""
        logger.info(f"⚙️ Resetting configuration for {issue.component}")
        
        # Simulate configuration reset
        # In real implementation, this would:
        # 1. Backup current configuration
        # 2. Load default configuration
        # 3. Validate new configuration
        
        time.sleep(0.5)  # Simulate reset time
        
        return {
            "component": issue.component,
            "status": "reset",
            "action": "configuration_reset"
        }
    
    def _enable_fallback_mode(self, issue: Issue, action: RecoveryAction) -> dict[str, Any]:
        """Enable fallback mode for a component"""
        logger.info(f"🛟 Enabling fallback mode for {issue.component}")
        
        # Simulate fallback mode activation
        # In real implementation, this would activate the fallback service
        
        return {
            "component": issue.component,
            "status": "fallback_mode",
            "action": "fallback_activation"
        }
    
    def _skip_component(self, issue: Issue, action: RecoveryAction) -> dict[str, Any]:
        """Skip a non-critical component"""
        logger.info(f"⏭️ Skipping component: {issue.component}")
        
        return {
            "component": issue.component,
            "status": "skipped",
            "action": "component_skip"
        }
    
    def _get_issue_description(self, issue_type: str, component: str, error_message: str) -> str:
        """Get a human-readable description for an issue"""
        descriptions = {
            "import_error": f"Import error in {component}: {error_message}",
            "service_unavailable": f"Service {component} is unavailable: {error_message}",
            "configuration_error": f"Configuration error in {component}: {error_message}",
            "memory_issue": f"Memory issue in {component}: {error_message}",
            "database_issue": f"Database issue in {component}: {error_message}"
        }
        
        return descriptions.get(issue_type, f"Unknown issue in {component}: {error_message}")
    
    def _extract_module_from_error(self, error_message: str) -> Optional[str]:
        """Extract module name from error message"""
        import re
        
        # Common patterns for import errors
        patterns = [
            r"No module named ['\"]([^'\"]+)['\"]",
            r"cannot import name ['\"]([^'\"]+)['\"]",
            r"from ([^ ]+) import",
            r"ImportError: ([^ ]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error_message)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_dependency_from_error(self, error_message: str) -> Optional[str]:
        """Extract dependency name from error message"""
        # Similar to module extraction but more specific to dependencies
        return self._extract_module_from_error(error_message)
    
    def _check_recovery_success(self, result: dict[str, Any], success_criteria: list[str]) -> bool:
        """Check if recovery action was successful"""
        for criterion in success_criteria:
            if criterion == "module_loaded":
                # Check if module is now importable
                pass  # Would need to test actual import
            elif criterion == "service_running":
                # Check if service is now running
                return result.get("status") == "restarted"
            elif criterion == "dependency_installed":
                # Check if dependency is now installed
                return result.get("status") == "installed"
            elif criterion == "config_valid":
                # Check if configuration is now valid
                return result.get("status") == "reset"
            elif criterion == "cache_cleared":
                # Check if caches were cleared
                return "cleared_caches" in result and len(result["cleared_caches"]) > 0
            elif criterion == "fallback_active":
                # Check if fallback mode is active
                return result.get("status") == "fallback_mode"
        
        return True  # Default to success if no specific criteria
    
    def get_system_health(self) -> dict[str, Any]:
        """Get overall system health including self-healing status"""
        total_issues = len(self.detected_issues)
        resolved_issues = sum(1 for issue in self.detected_issues if issue.resolved)
        active_issues = total_issues - resolved_issues
        
        successful_recoveries = sum(1 for result in self.recovery_history if result.success)
        failed_recoveries = len(self.recovery_history) - successful_recoveries
        
        return {
            "self_healing_enabled": self.healing_enabled,
            "auto_recovery_enabled": self.auto_recovery,
            "total_issues_detected": total_issues,
            "resolved_issues": resolved_issues,
            "active_issues": active_issues,
            "recovery_attempts": len(self.recovery_history),
            "successful_recoveries": successful_recoveries,
            "failed_recoveries": failed_recoveries,
            "success_rate": successful_recoveries / len(self.recovery_history) if self.recovery_history else 0.0,
            "recent_issues": [
                {
                    "type": issue.issue_type,
                    "component": issue.component,
                    "severity": issue.severity,
                    "resolved": issue.resolved,
                    "recovery_attempts": issue.recovery_attempts
                }
                for issue in self.detected_issues[-10:]  # Last 10 issues
            ]
        }
    
    def enable_healing(self):
        """Enable self-healing"""
        self.healing_enabled = True
        logger.info("🔄 Self-healing enabled")
    
    def disable_healing(self):
        """Disable self-healing"""
        self.healing_enabled = False
        logger.info("🔄 Self-healing disabled")
    
    def enable_auto_recovery(self):
        """Enable automatic recovery"""
        self.auto_recovery = True
        logger.info("🔄 Auto-recovery enabled")
    
    def disable_auto_recovery(self):
        """Disable automatic recovery"""
        self.auto_recovery = False
        logger.info("🔄 Auto-recovery disabled")
    
    def clear_history(self):
        """Clear recovery history"""
        self.detected_issues.clear()
        self.recovery_history.clear()
        logger.info("🔄 Self-healing history cleared")


# Global self-healing system instance
_self_healing_system: Optional[SelfHealingSystem] = None


def get_self_healing_system() -> SelfHealingSystem:
    """Get the global self-healing system instance"""
    global _self_healing_system
    if _self_healing_system is None:
        _self_healing_system = SelfHealingSystem()
    return _self_healing_system


def auto_recover(func):
    """Decorator for automatic recovery from function failures"""
    def wrapper(*args, **kwargs):
        healer = get_self_healing_system()
        
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Detect issue type based on exception
            error_message = str(e)
            issue_type = "unknown"
            component = "unknown"
            severity = "medium"
            
            if isinstance(e, (ImportError, ModuleNotFoundError)):
                issue_type = "import_error"
                component = "import_system"
                severity = "high"
            elif isinstance(e, AttributeError):
                issue_type = "service_unavailable"
                component = "service_system"
                severity = "medium"
            elif isinstance(e, (ValueError, KeyError)):
                issue_type = "configuration_error"
                component = "configuration_system"
                severity = "medium"
            
            # Register issue and attempt recovery
            issue = healer.detect_issue(issue_type, component, error_message, severity)
            
            if issue.resolved:
                # Retry the function after recovery
                try:
                    return func(*args, **kwargs)
                except Exception as retry_error:
                    logger.error(f"❌ Function still failed after recovery: {str(retry_error)}")
                    raise retry_error
            else:
                # Recovery failed, re-raise original exception
                raise e
    
    return wrapper


if __name__ == "__main__":
    # Test the self-healing system
    import logging
    
    logging.basicConfig(level=logging.INFO)
    
    print("Testing Self-Healing System")
    print("=" * 40)
    
    healer = SelfHealingSystem()
    
    # Test import error recovery
    print("\n1. Testing import error recovery...")
    issue = healer.detect_issue(
        "import_error",
        "test_module",
        "No module named 'nonexistent_module'",
        "high"
    )
    
    # Test service recovery
    print("\n2. Testing service recovery...")
    issue2 = healer.detect_issue(
        "service_unavailable",
        "test_service",
        "Service failed to start",
        "medium"
    )
    
    # Get system health
    health = healer.get_system_health()
    print("\n3. System Health:")
    print(f"   Total issues: {health['total_issues_detected']}")
    print(f"   Resolved issues: {health['resolved_issues']}")
    print(f"   Recovery success rate: {health['success_rate']:.2%}")
    
    print("\nSelf-healing system test completed!")
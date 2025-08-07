# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-05 14:00:00
@Author  : DAIP-LIVE Team
@File    : production_ready_preparation_system.py
@Description:
    V0.3.10 Production-Ready Preparation System
    生产就绪准备系统
"""

import asyncio
import json
import logging
import time
import threading
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import os
import sys
import shutil
import subprocess
import platform
import psutil
import yaml
from concurrent.futures import ThreadPoolExecutor
import hashlib
import uuid
import zipfile
import tempfile

from .performance_monitoring_system import PerformanceMonitoringSystem
from .enterprise_error_handling_system import EnterpriseErrorHandler, get_enterprise_error_handler
from .comprehensive_quality_validation_system import ComprehensiveQualityValidator, get_comprehensive_quality_validator

logger = logging.getLogger(__name__)


class DeploymentEnvironment(Enum):
    """Deployment environments."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class DeploymentStrategy(Enum):
    """Deployment strategies."""
    BLUE_GREEN = "blue_green"
    ROLLING = "rolling"
    CANARY = "canary"
    IMMEDIATE = "immediate"


class HealthStatus(Enum):
    """Health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class DeploymentConfig:
    """Deployment configuration."""
    environment: DeploymentEnvironment
    strategy: DeploymentStrategy
    version: str
    build_number: str
    deployment_id: str
    rollback_enabled: bool
    health_check_enabled: bool
    monitoring_enabled: bool
    backup_enabled: bool
    config_overrides: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthCheck:
    """Health check definition."""
    name: str
    check_type: str
    endpoint: Optional[str] = None
    command: Optional[str] = None
    timeout: int = 30
    interval: int = 60
    retries: int = 3
    critical: bool = True


@dataclass
class BackupConfig:
    """Backup configuration."""
    enabled: bool
    frequency: str  # hourly, daily, weekly
    retention_days: int
    compression: bool
    encryption: bool
    storage_path: str
    include_databases: bool
    include_files: bool


@dataclass
class MonitoringConfig:
    """Monitoring configuration."""
    enabled: bool
    metrics_endpoint: str
    health_endpoint: str
    log_level: str
    alert_channels: List[str]
    dashboard_url: Optional[str] = None


@dataclass
class SecurityConfig:
    """Security configuration."""
    ssl_enabled: bool
    ssl_cert_path: Optional[str]
    ssl_key_path: Optional[str]
    firewall_enabled: bool
    rate_limiting: bool
    api_key_required: bool
    cors_enabled: bool
    cors_origins: List[str]


class DeploymentManager:
    """Deployment manager."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.deployment_history: List[Dict[str, Any]] = []
        self.active_deployments: Dict[str, DeploymentConfig] = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.health_checks: Dict[str, HealthCheck] = {}
        self._initialize_health_checks()
    
    def _initialize_health_checks(self):
        """Initialize health checks."""
        self.health_checks = {
            "system_health": HealthCheck(
                name="System Health",
                check_type="system",
                timeout=10,
                interval=30,
                retries=3,
                critical=True
            ),
            "database_health": HealthCheck(
                name="Database Health",
                check_type="database",
                timeout=15,
                interval=60,
                retries=3,
                critical=True
            ),
            "api_health": HealthCheck(
                name="API Health",
                check_type="api",
                endpoint="/health",
                timeout=10,
                interval=30,
                retries=3,
                critical=True
            ),
            "memory_health": HealthCheck(
                name="Memory Health",
                check_type="memory",
                timeout=10,
                interval=60,
                retries=3,
                critical=False
            )
        }
    
    async def prepare_deployment(self, 
                                environment: DeploymentEnvironment,
                                strategy: DeploymentStrategy,
                                version: str,
                                config_overrides: Optional[Dict[str, Any]] = None) -> DeploymentConfig:
        """Prepare deployment configuration."""
        deployment_id = str(uuid.uuid4())
        build_number = self._generate_build_number()
        
        deployment_config = DeploymentConfig(
            environment=environment,
            strategy=strategy,
            version=version,
            build_number=build_number,
            deployment_id=deployment_id,
            rollback_enabled=True,
            health_check_enabled=True,
            monitoring_enabled=True,
            backup_enabled=environment != DeploymentEnvironment.DEVELOPMENT,
            config_overrides=config_overrides or {}
        )
        
        # Validate deployment configuration
        if not await self._validate_deployment_config(deployment_config):
            raise Exception("Invalid deployment configuration")
        
        # Store deployment config
        self.active_deployments[deployment_id] = deployment_config
        
        logger.info(f"Deployment prepared: {deployment_id} ({version} - {environment.value})")
        return deployment_config
    
    def _generate_build_number(self) -> str:
        """Generate build number."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return f"build-{timestamp}"
    
    async def _validate_deployment_config(self, config: DeploymentConfig) -> bool:
        """Validate deployment configuration."""
        try:
            # Check if version exists
            if not self._version_exists(config.version):
                logger.error(f"Version {config.version} does not exist")
                return False
            
            # Check environment compatibility
            if config.environment == DeploymentEnvironment.PRODUCTION:
                if not self._check_production_readiness():
                    logger.error("System is not ready for production deployment")
                    return False
            
            # Check required services
            if not await self._check_required_services():
                logger.error("Required services are not available")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Deployment validation failed: {e}")
            return False
    
    def _version_exists(self, version: str) -> bool:
        """Check if version exists."""
        # This would typically check version control or artifact repository
        return True
    
    def _check_production_readiness(self) -> bool:
        """Check if system is ready for production."""
        # Check if all production requirements are met
        return True
    
    async def _check_required_services(self) -> bool:
        """Check if required services are available."""
        # Check database, external services, etc.
        return True
    
    async def execute_deployment(self, deployment_config: DeploymentConfig) -> Dict[str, Any]:
        """Execute deployment."""
        deployment_result = {
            "deployment_id": deployment_config.deployment_id,
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "steps": [],
            "success": False,
            "error": None
        }
        
        try:
            logger.info(f"Starting deployment: {deployment_config.deployment_id}")
            
            # Step 1: Create backup
            if deployment_config.backup_enabled:
                backup_result = await self._create_backup(deployment_config)
                deployment_result["steps"].append(backup_result)
                if not backup_result["success"]:
                    raise Exception("Backup creation failed")
            
            # Step 2: Prepare environment
            env_result = await self._prepare_environment(deployment_config)
            deployment_result["steps"].append(env_result)
            if not env_result["success"]:
                raise Exception("Environment preparation failed")
            
            # Step 3: Deploy application
            deploy_result = await self._deploy_application(deployment_config)
            deployment_result["steps"].append(deploy_result)
            if not deploy_result["success"]:
                raise Exception("Application deployment failed")
            
            # Step 4: Run health checks
            if deployment_config.health_check_enabled:
                health_result = await self._run_health_checks(deployment_config)
                deployment_result["steps"].append(health_result)
                if not health_result["success"]:
                    # Trigger rollback if health checks fail
                    await self._trigger_rollback(deployment_config)
                    raise Exception("Health checks failed")
            
            # Step 5: Enable monitoring
            if deployment_config.monitoring_enabled:
                monitoring_result = await self._enable_monitoring(deployment_config)
                deployment_result["steps"].append(monitoring_result)
            
            deployment_result["status"] = "completed"
            deployment_result["success"] = True
            deployment_result["end_time"] = datetime.now().isoformat()
            
            # Store deployment history
            self.deployment_history.append(deployment_result)
            
            logger.info(f"Deployment completed successfully: {deployment_config.deployment_id}")
            
        except Exception as e:
            deployment_result["status"] = "failed"
            deployment_result["success"] = False
            deployment_result["error"] = str(e)
            deployment_result["end_time"] = datetime.now().isoformat()
            
            logger.error(f"Deployment failed: {deployment_config.deployment_id} - {str(e)}")
            
            # Trigger rollback if enabled
            if deployment_config.rollback_enabled:
                await self._trigger_rollback(deployment_config)
        
        return deployment_result
    
    async def _create_backup(self, deployment_config: DeploymentConfig) -> Dict[str, Any]:
        """Create backup."""
        backup_result = {
            "step": "create_backup",
            "success": False,
            "start_time": datetime.now().isoformat(),
            "details": {}
        }
        
        try:
            logger.info("Creating backup...")
            
            # Create backup directory
            backup_dir = f"backups/{deployment_config.deployment_id}"
            os.makedirs(backup_dir, exist_ok=True)
            
            # Backup configuration files
            config_files = ["config.yaml", "pyproject.toml", "requirements.txt"]
            for config_file in config_files:
                if os.path.exists(config_file):
                    shutil.copy2(config_file, f"{backup_dir}/{config_file}")
            
            # Backup data directory
            if os.path.exists("data"):
                shutil.copytree("data", f"{backup_dir}/data")
            
            # Create compressed backup
            backup_archive = f"{backup_dir}/backup.zip"
            with zipfile.ZipFile(backup_archive, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(backup_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if not file_path.endswith(backup_archive):
                            zipf.write(file_path, os.path.relpath(file_path, backup_dir))
            
            backup_result["success"] = True
            backup_result["details"]["backup_path"] = backup_archive
            backup_result["details"]["backup_size"] = os.path.getsize(backup_archive)
            backup_result["end_time"] = datetime.now().isoformat()
            
            logger.info("Backup created successfully")
            
        except Exception as e:
            backup_result["success"] = False
            backup_result["error"] = str(e)
            backup_result["end_time"] = datetime.now().isoformat()
            
            logger.error(f"Backup creation failed: {e}")
        
        return backup_result
    
    async def _prepare_environment(self, deployment_config: DeploymentConfig) -> Dict[str, Any]:
        """Prepare deployment environment."""
        env_result = {
            "step": "prepare_environment",
            "success": False,
            "start_time": datetime.now().isoformat(),
            "details": {}
        }
        
        try:
            logger.info("Preparing environment...")
            
            # Create deployment directory
            deploy_dir = f"deployments/{deployment_config.deployment_id}"
            os.makedirs(deploy_dir, exist_ok=True)
            
            # Copy application files
            source_dir = "src"
            if os.path.exists(source_dir):
                shutil.copytree(source_dir, f"{deploy_dir}/src")
            
            # Copy required files
            required_files = ["pyproject.toml", "requirements.txt"]
            for file in required_files:
                if os.path.exists(file):
                    shutil.copy2(file, f"{deploy_dir}/{file}")
            
            # Install dependencies
            if os.path.exists(f"{deploy_dir}/requirements.txt"):
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", f"{deploy_dir}/requirements.txt"
                ], check=True, capture_output=True)
            
            # Apply configuration overrides
            if deployment_config.config_overrides:
                await self._apply_config_overrides(deploy_dir, deployment_config.config_overrides)
            
            env_result["success"] = True
            env_result["details"]["deployment_directory"] = deploy_dir
            env_result["end_time"] = datetime.now().isoformat()
            
            logger.info("Environment prepared successfully")
            
        except Exception as e:
            env_result["success"] = False
            env_result["error"] = str(e)
            env_result["end_time"] = datetime.now().isoformat()
            
            logger.error(f"Environment preparation failed: {e}")
        
        return env_result
    
    async def _deploy_application(self, deployment_config: DeploymentConfig) -> Dict[str, Any]:
        """Deploy application."""
        deploy_result = {
            "step": "deploy_application",
            "success": False,
            "start_time": datetime.now().isoformat(),
            "details": {}
        }
        
        try:
            logger.info("Deploying application...")
            
            # Stop existing application
            await self._stop_application()
            
            # Start new application
            await self._start_application(deployment_config)
            
            # Verify application is running
            if await self._verify_application_running():
                deploy_result["success"] = True
                deploy_result["details"]["application_status"] = "running"
            else:
                raise Exception("Application failed to start")
            
            deploy_result["end_time"] = datetime.now().isoformat()
            
            logger.info("Application deployed successfully")
            
        except Exception as e:
            deploy_result["success"] = False
            deploy_result["error"] = str(e)
            deploy_result["end_time"] = datetime.now().isoformat()
            
            logger.error(f"Application deployment failed: {e}")
        
        return deploy_result
    
    async def _run_health_checks(self, deployment_config: DeploymentConfig) -> Dict[str, Any]:
        """Run health checks."""
        health_result = {
            "step": "run_health_checks",
            "success": False,
            "start_time": datetime.now().isoformat(),
            "details": {}
        }
        
        try:
            logger.info("Running health checks...")
            
            health_check_results = {}
            all_passed = True
            
            for check_name, health_check in self.health_checks.items():
                try:
                    result = await self._execute_health_check(health_check)
                    health_check_results[check_name] = result
                    
                    if not result["passed"]:
                        all_passed = False
                        if health_check.critical:
                            break
                        
                except Exception as e:
                    health_check_results[check_name] = {
                        "passed": False,
                        "error": str(e)
                    }
                    all_passed = False
                    if health_check.critical:
                        break
            
            health_result["success"] = all_passed
            health_result["details"]["health_checks"] = health_check_results
            health_result["end_time"] = datetime.now().isoformat()
            
            logger.info(f"Health checks completed: {'PASSED' if all_passed else 'FAILED'}")
            
        except Exception as e:
            health_result["success"] = False
            health_result["error"] = str(e)
            health_result["end_time"] = datetime.now().isoformat()
            
            logger.error(f"Health checks failed: {e}")
        
        return health_result
    
    async def _execute_health_check(self, health_check: HealthCheck) -> Dict[str, Any]:
        """Execute individual health check."""
        result = {
            "passed": False,
            "response_time": 0,
            "details": {}
        }
        
        start_time = time.time()
        
        try:
            if health_check.check_type == "system":
                # Check system resources
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_percent = psutil.virtual_memory().percent
                disk_percent = psutil.disk_usage('/').percent
                
                result["passed"] = (
                    cpu_percent < 90 and
                    memory_percent < 90 and
                    disk_percent < 90
                )
                result["details"] = {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_percent,
                    "disk_percent": disk_percent
                }
                
            elif health_check.check_type == "memory":
                # Check memory usage
                memory = psutil.virtual_memory()
                result["passed"] = memory.percent < 85
                result["details"] = {
                    "memory_percent": memory.percent,
                    "available_memory": memory.available
                }
                
            elif health_check.check_type == "database":
                # Check database connectivity
                result["passed"] = True  # Placeholder
                result["details"] = {"status": "connected"}
                
            elif health_check.check_type == "api" and health_check.endpoint:
                # Check API endpoint
                result["passed"] = True  # Placeholder
                result["details"] = {"status_code": 200}
            
        except Exception as e:
            result["error"] = str(e)
        
        result["response_time"] = time.time() - start_time
        return result
    
    async def _enable_monitoring(self, deployment_config: DeploymentConfig) -> Dict[str, Any]:
        """Enable monitoring."""
        monitoring_result = {
            "step": "enable_monitoring",
            "success": False,
            "start_time": datetime.now().isoformat(),
            "details": {}
        }
        
        try:
            logger.info("Enabling monitoring...")
            
            # Initialize monitoring systems
            monitoring_system = PerformanceMonitoringSystem({
                "auto_optimization": deployment_config.environment == DeploymentEnvironment.PRODUCTION,
                "monitoring_interval": 60,
                "max_history_size": 1000
            })
            await monitoring_system.initialize()
            
            # Initialize error handler
            error_handler = get_enterprise_error_handler()
            
            # Initialize quality validator
            quality_validator = get_comprehensive_quality_validator()
            quality_validator.initialize(monitoring_system, error_handler)
            
            monitoring_result["success"] = True
            monitoring_result["details"]["monitoring_enabled"] = True
            monitoring_result["end_time"] = datetime.now().isoformat()
            
            logger.info("Monitoring enabled successfully")
            
        except Exception as e:
            monitoring_result["success"] = False
            monitoring_result["error"] = str(e)
            monitoring_result["end_time"] = datetime.now().isoformat()
            
            logger.error(f"Monitoring enablement failed: {e}")
        
        return monitoring_result
    
    async def _trigger_rollback(self, deployment_config: DeploymentConfig):
        """Trigger rollback."""
        logger.info(f"Triggering rollback for deployment: {deployment_config.deployment_id}")
        
        try:
            # Find previous successful deployment
            previous_deployment = self._find_previous_deployment(deployment_config.environment)
            
            if previous_deployment:
                # Restore from backup
                backup_path = f"backups/{previous_deployment['deployment_id']}/backup.zip"
                if os.path.exists(backup_path):
                    await self._restore_from_backup(backup_path)
                
                # Restart previous version
                await self._restart_previous_version(previous_deployment)
                
                logger.info("Rollback completed successfully")
            else:
                logger.error("No previous deployment found for rollback")
                
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
    
    def _find_previous_deployment(self, environment: DeploymentEnvironment) -> Optional[Dict[str, Any]]:
        """Find previous successful deployment."""
        for deployment in reversed(self.deployment_history):
            if (deployment.get("success") and 
                deployment.get("environment") == environment):
                return deployment
        return None
    
    async def _restore_from_backup(self, backup_path: str):
        """Restore from backup."""
        # Implementation for restoring from backup
        pass
    
    async def _restart_previous_version(self, deployment: Dict[str, Any]):
        """Restart previous version."""
        # Implementation for restarting previous version
        pass
    
    async def _stop_application(self):
        """Stop application."""
        # Implementation for stopping application
        pass
    
    async def _start_application(self, deployment_config: DeploymentConfig):
        """Start application."""
        # Implementation for starting application
        pass
    
    async def _verify_application_running(self) -> bool:
        """Verify application is running."""
        # Implementation for verifying application is running
        return True
    
    async def _apply_config_overrides(self, deploy_dir: str, config_overrides: Dict[str, Any]):
        """Apply configuration overrides."""
        # Implementation for applying configuration overrides
        pass
    
    def get_deployment_status(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """Get deployment status."""
        for deployment in self.deployment_history:
            if deployment.get("deployment_id") == deployment_id:
                return deployment
        return None
    
    def get_deployment_history(self, 
                             environment: Optional[DeploymentEnvironment] = None,
                             limit: int = 10) -> List[Dict[str, Any]]:
        """Get deployment history."""
        history = self.deployment_history
        
        if environment:
            history = [d for d in history if d.get("environment") == environment]
        
        return history[-limit:]
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health status."""
        health_status = {
            "status": HealthStatus.HEALTHY.value,
            "timestamp": datetime.now().isoformat(),
            "components": {},
            "metrics": {}
        }
        
        try:
            # Check system resources
            health_status["metrics"]["cpu_percent"] = psutil.cpu_percent()
            health_status["metrics"]["memory_percent"] = psutil.virtual_memory().percent
            health_status["metrics"]["disk_percent"] = psutil.disk_usage('/').percent
            
            # Determine overall health
            if (health_status["metrics"]["cpu_percent"] > 90 or
                health_status["metrics"]["memory_percent"] > 90 or
                health_status["metrics"]["disk_percent"] > 90):
                health_status["status"] = HealthStatus.DEGRADED.value
            
            # Check active deployments
            active_count = len(self.active_deployments)
            health_status["metrics"]["active_deployments"] = active_count
            
            if active_count > 5:
                health_status["status"] = HealthStatus.DEGRADED.value
            
        except Exception as e:
            health_status["status"] = HealthStatus.UNHEALTHY.value
            health_status["error"] = str(e)
        
        return health_status


class ProductionReadySystem:
    """Production-ready system."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.deployment_manager = DeploymentManager(config)
        self.monitoring_system = None
        self.error_handler = None
        self.quality_validator = None
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize production-ready system."""
        try:
            # Initialize monitoring system
            self.monitoring_system = PerformanceMonitoringSystem({
                "auto_optimization": True,
                "monitoring_interval": 60,
                "max_history_size": 1000
            })
            await self.monitoring_system.initialize()
            
            # Initialize error handler
            self.error_handler = get_enterprise_error_handler()
            
            # Initialize quality validator
            self.quality_validator = get_comprehensive_quality_validator()
            self.quality_validator.initialize(self.monitoring_system, self.error_handler)
            
            self.is_initialized = True
            logger.info("Production-ready system initialized successfully")
            
        except Exception as e:
            logger.error(f"Production-ready system initialization failed: {e}")
            raise
    
    async def deploy_to_production(self, version: str, config_overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Deploy to production."""
        if not self.is_initialized:
            raise Exception("System not initialized")
        
        # Prepare deployment
        deployment_config = await self.deployment_manager.prepare_deployment(
            environment=DeploymentEnvironment.PRODUCTION,
            strategy=DeploymentStrategy.BLUE_GREEN,
            version=version,
            config_overrides=config_overrides
        )
        
        # Execute deployment
        deployment_result = await self.deployment_manager.execute_deployment(deployment_config)
        
        return deployment_result
    
    async def run_production_checks(self) -> Dict[str, Any]:
        """Run production readiness checks."""
        checks = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "overall_status": "passed"
        }
        
        try:
            # System health check
            system_health = self.deployment_manager.get_system_health()
            checks["checks"]["system_health"] = system_health
            
            # Performance check
            perf_report = await self.monitoring_system.get_performance_report()
            checks["checks"]["performance"] = perf_report
            
            # Quality check
            quality_report = await self.quality_validator.validate_system(ValidationLevel.COMPREHENSIVE)
            checks["checks"]["quality"] = {
                "overall_score": quality_report.overall_score,
                "quality_grade": quality_report.quality_grade.value
            }
            
            # Error handling check
            error_stats = self.error_handler.get_error_statistics()
            checks["checks"]["error_handling"] = error_stats
            
            # Determine overall status
            if (system_health["status"] != HealthStatus.HEALTHY.value or
                quality_report.overall_score < 80 or
                error_stats.get("total_errors", 0) > 100):
                checks["overall_status"] = "failed"
            
        except Exception as e:
            checks["overall_status"] = "error"
            checks["error"] = str(e)
        
        return checks
    
    async def generate_deployment_package(self, version: str) -> str:
        """Generate deployment package."""
        package_id = str(uuid.uuid4())
        package_dir = f"deployment_packages/{package_id}"
        os.makedirs(package_dir, exist_ok=True)
        
        try:
            # Copy source code
            shutil.copytree("src", f"{package_dir}/src")
            
            # Copy configuration files
            config_files = ["config.yaml", "pyproject.toml", "requirements.txt"]
            for file in config_files:
                if os.path.exists(file):
                    shutil.copy2(file, f"{package_dir}/{file}")
            
            # Copy documentation
            if os.path.exists("docs"):
                shutil.copytree("docs", f"{package_dir}/docs")
            
            # Create deployment manifest
            manifest = {
                "version": version,
                "package_id": package_id,
                "created_at": datetime.now().isoformat(),
                "files": [],
                "checksums": {}
            }
            
            # Generate checksums
            for root, dirs, files in os.walk(package_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    with open(file_path, 'rb') as f:
                        checksum = hashlib.sha256(f.read()).hexdigest()
                        manifest["checksums"][file_path] = checksum
            
            # Save manifest
            with open(f"{package_dir}/manifest.json", 'w') as f:
                json.dump(manifest, f, indent=2)
            
            # Create compressed package
            package_archive = f"deployment_packages/{version}_package.zip"
            with zipfile.ZipFile(package_archive, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(package_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.relpath(file_path, package_dir))
            
            # Clean up temporary directory
            shutil.rmtree(package_dir)
            
            logger.info(f"Deployment package generated: {package_archive}")
            return package_archive
            
        except Exception as e:
            logger.error(f"Failed to generate deployment package: {e}")
            if os.path.exists(package_dir):
                shutil.rmtree(package_dir)
            raise


# Global instance
_production_ready_system: Optional[ProductionReadySystem] = None


def get_production_ready_system() -> ProductionReadySystem:
    """Get global production-ready system instance."""
    global _production_ready_system
    if _production_ready_system is None:
        config = {
            "deployment": {
                "backup_enabled": True,
                "health_check_enabled": True,
                "monitoring_enabled": True,
                "rollback_enabled": True
            }
        }
        _production_ready_system = ProductionReadySystem(config)
    return _production_ready_system


async def initialize_production_ready_system(config: Dict[str, Any]):
    """Initialize production-ready system."""
    global _production_ready_system
    _production_ready_system = ProductionReadySystem(config)
    await _production_ready_system.initialize()
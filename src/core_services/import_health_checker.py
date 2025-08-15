"""@Time    : 2025-08-05 15:30:00
@Author  : DAIP-LIVE Team
@File    : import_health_checker.py
@Description:
    Import health checking module for validating critical imports during startup.
"""

import logging
import time
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ImportCheckResult:
    """Result of an import check"""
    import_path: str
    success: bool
    error_message: Optional[str] = None
    check_time: float = 0.0
    is_critical: bool = True


class ImportHealthChecker:
    """Validates critical imports during startup"""
    
    def __init__(self):
        self.critical_imports = [
            {
                "path": "src.config",
                "name": "settings",
                "description": "Configuration settings",
                "is_critical": True
            },
            {
                "path": "src.kernel.llm_interface", 
                "name": "LLMFactory",
                "description": "LLM interface factory",
                "is_critical": True
            },
            {
                "path": "src.core_services.token_management_service",
                "name": "TokenManagementService", 
                "description": "Token management service",
                "is_critical": True
            },
            {
                "path": "src.unified_tool_manager",
                "name": "UnifiedToolManager",
                "description": "Unified tool manager",
                "is_critical": True
            },
            {
                "path": "src.core_services.memory_service",
                "name": "MemoryService",
                "description": "Memory service",
                "is_critical": True
            },
            {
                "path": "src.core_services.wiki_service", 
                "name": "WikiService",
                "description": "Wiki service",
                "is_critical": True
            },
            {
                "path": "src.core_services.synthesis_engine",
                "name": "SynthesisEngine",
                "description": "Synthesis engine",
                "is_critical": True
            },
            {
                "path": "src.core_services.expert_service",
                "name": "ExpertService",
                "description": "Expert service",
                "is_critical": True
            },
            {
                "path": "src.core_services.task_manager",
                "name": "TaskManager",
                "description": "Task manager",
                "is_critical": True
            },
            {
                "path": "src.core_services.user_profile_service",
                "name": "UserProfileService",
                "description": "User profile service",
                "is_critical": True
            },
            {
                "path": "src.core_services.session_management_service",
                "name": "SessionManagementService", 
                "description": "Session management service",
                "is_critical": True
            },
            {
                "path": "src.core_services.universal_context_service",
                "name": "UniversalContextService",
                "description": "Universal context service",
                "is_critical": True
            },
            {
                "path": "src.core_services.expert_consultation_scenario",
                "name": "ConsultationPriority",
                "description": "Expert consultation priority enum",
                "is_critical": True
            },
            {
                "path": "src.core_services.academic_research_scenario",
                "name": "AcademicResearchScenario",
                "description": "Academic research scenario",
                "is_critical": True
            },
            {
                "path": "src.core_services.industry_analysis_scenario", 
                "name": "IndustryAnalysisScenario",
                "description": "Industry analysis scenario",
                "is_critical": True
            }
        ]
        
        self.optional_imports = [
            {
                "path": "src.core_services.enhanced_memory_management",
                "name": "EnhancedMemoryManagement",
                "description": "Enhanced memory management",
                "is_critical": False
            },
            {
                "path": "src.core_services.knowledge_visualization_engine",
                "name": "KnowledgeVisualizationEngine",
                "description": "Knowledge visualization engine",
                "is_critical": False
            }
        ]
        
        self.results: list[ImportCheckResult] = []
    
    def check_import(self, import_config: dict) -> ImportCheckResult:
        """Check a single import"""
        start_time = time.time()
        
        try:
            module = __import__(import_config["path"], fromlist=[import_config["name"]])
            getattr(module, import_config["name"])
            
            check_time = time.time() - start_time
            return ImportCheckResult(
                import_path=f"{import_config['path']}.{import_config['name']}",
                success=True,
                check_time=check_time,
                is_critical=import_config["is_critical"]
            )
            
        except (ImportError, AttributeError) as e:
            check_time = time.time() - start_time
            return ImportCheckResult(
                import_path=f"{import_config['path']}.{import_config['name']}",
                success=False,
                error_message=str(e),
                check_time=check_time,
                is_critical=import_config["is_critical"]
            )
    
    def validate_all_imports(self) -> tuple[bool, list[ImportCheckResult]]:
        """Validate all imports and return overall status"""
        logger.info("🔍 Starting import health check...")
        
        self.results = []
        
        # Check critical imports first
        for import_config in self.critical_imports:
            result = self.check_import(import_config)
            self.results.append(result)
            
            if result.success:
                logger.info(f"✅ {result.import_path} ({result.check_time:.3f}s)")
            else:
                logger.error(f"❌ {result.import_path}: {result.error_message}")
        
        # Check optional imports
        for import_config in self.optional_imports:
            result = self.check_import(import_config)
            self.results.append(result)
            
            if result.success:
                logger.info(f"✅ {result.import_path} (optional) ({result.check_time:.3f}s)")
            else:
                logger.warning(f"⚠️ {result.import_path} (optional): {result.error_message}")
        
        # Determine overall status
        critical_failures = [r for r in self.results if not r.success and r.is_critical]
        overall_success = len(critical_failures) == 0
        
        total_time = sum(r.check_time for r in self.results)
        logger.info(f"📊 Import health check completed in {total_time:.3f}s")
        
        return overall_success, self.results
    
    def get_health_summary(self) -> dict:
        """Get a summary of import health status"""
        if not self.results:
            return {"status": "not_checked", "message": "Import health check not performed"}
        
        critical_results = [r for r in self.results if r.is_critical]
        optional_results = [r for r in self.results if not r.is_critical]
        
        critical_success = sum(1 for r in critical_results if r.success)
        optional_success = sum(1 for r in optional_results if r.success)
        
        critical_failures = [r for r in critical_results if not r.success]
        optional_failures = [r for r in optional_results if not r.success]
        
        total_time = sum(r.check_time for r in self.results)
        
        return {
            "status": "healthy" if len(critical_failures) == 0 else "unhealthy",
            "critical_imports": {
                "total": len(critical_results),
                "successful": critical_success,
                "failed": len(critical_failures),
                "failures": [
                    {
                        "import_path": r.import_path,
                        "error": r.error_message,
                        "description": next(
                            (item["description"] for item in self.critical_imports + self.optional_imports 
                             if f"{item['path']}.{item['name']}" == r.import_path),
                            "Unknown component"
                        )
                    }
                    for r in critical_failures
                ]
            },
            "optional_imports": {
                "total": len(optional_results),
                "successful": optional_success,
                "failed": len(optional_failures),
                "failures": [
                    {
                        "import_path": r.import_path,
                        "error": r.error_message,
                        "description": next(
                            (item["description"] for item in self.critical_imports + self.optional_imports 
                             if f"{item['path']}.{item['name']}" == r.import_path),
                            "Unknown component"
                        )
                    }
                    for r in optional_failures
                ]
            },
            "performance": {
                "total_check_time": total_time,
                "average_check_time": total_time / len(self.results) if self.results else 0,
                "slowest_import": max(self.results, key=lambda r: r.check_time).import_path if self.results else None
            }
        }
    
    def raise_if_critical_failures(self):
        """Raise exception if there are critical import failures"""
        critical_failures = [r for r in self.results if not r.success and r.is_critical]
        
        if critical_failures:
            error_message = self._format_critical_failure_message(critical_failures)
            raise ImportError(error_message)
    
    def _format_critical_failure_message(self, failures: list[ImportCheckResult]) -> str:
        """Format a user-friendly error message for critical failures"""
        message = [
            "❌ Critical Import Failures Detected",
            "",
            "The following required components could not be imported:",
            ""
        ]
        
        for failure in failures:
            description = next(
                (item["description"] for item in self.critical_imports + self.optional_imports 
                 if f"{item['path']}.{item['name']}" == failure.import_path),
                "Unknown component"
            )
            message.append(f"📦 {description}")
            message.append(f"   Import: {failure.import_path}")
            message.append(f"   Error: {failure.error_message}")
            message.append("")
        
        message.extend([
            "💡 Troubleshooting Steps:",
            "1. Check installation: pip install -e .",
            "2. Verify dependencies: pip install -r requirements.txt", 
            "3. Run system check: python -c 'from src.app_state import AppState; AppState()'",
            "4. Check Python path: export PYTHONPATH=$PYTHONPATH:$(pwd)",
            ""
        ])
        
        return "\n".join(message)


def validate_imports_on_startup() -> bool:
    """Convenience function to validate imports during startup"""
    checker = ImportHealthChecker()
    success, results = checker.validate_all_imports()
    
    if not success:
        checker.raise_if_critical_failures()
    
    return success


if __name__ == "__main__":
    # Test the import health checker
    logging.basicConfig(level=logging.INFO)
    
    checker = ImportHealthChecker()
    success, results = checker.validate_all_imports()
    
    print("\n" + "="*60)
    print("IMPORT HEALTH CHECK SUMMARY")
    print("="*60)
    
    summary = checker.get_health_summary()
    print(f"Status: {summary['status'].upper()}")
    print(f"Critical Imports: {summary['critical_imports']['successful']}/{summary['critical_imports']['total']}")
    print(f"Optional Imports: {summary['optional_imports']['successful']}/{summary['optional_imports']['total']}")
    print(f"Total Check Time: {summary['performance']['total_check_time']:.3f}s")
    
    if summary['critical_imports']['failures']:
        print("\nCRITICAL FAILURES:")
        for failure in summary['critical_imports']['failures']:
            print(f"  - {failure['import_path']}: {failure['error']}")
    
    if summary['optional_imports']['failures']:
        print("\nOPTIONAL FAILURES:")
        for failure in summary['optional_imports']['failures']:
            print(f"  - {failure['import_path']}: {failure['error']}")
    
    print("\n" + "="*60)
# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-05 15:35:00
@Author  : DAIP-LIVE Team
@File    : user_friendly_errors.py
@Description:
    User-friendly error messages and exception handling for the DAIP-LIVE system.
"""

import logging
import sys
import traceback
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ErrorSolution:
    """Solution for a specific error type"""
    description: str
    steps: List[str]
    common_causes: List[str]
    severity: str = "medium"  # low, medium, high, critical


@dataclass
class ErrorContext:
    """Context information for error handling"""
    component: str
    operation: str
    user_action: str
    additional_info: Dict[str, Any]


class UserFriendlyImportError(Exception):
    """User-friendly ImportError with helpful suggestions"""
    
    def __init__(self, original_error: Exception, context: ErrorContext):
        self.original_error = original_error
        self.context = context
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        """Format a user-friendly error message"""
        solutions = self._get_solutions()
        
        message = [
            f"❌ {self._get_error_title()}",
            "",
            f"**Component**: {self.context.component}",
            f"**Operation**: {self.context.operation}",
            f"**What you were trying to do**: {self.context.user_action}",
            "",
            "**Technical Details**:",
            f"   Error Type: {type(self.original_error).__name__}",
            f"   Error Message: {str(self.original_error)}",
            "",
        ]
        
        if solutions:
            message.extend([
                "**💡 Solutions**:",
                ""
            ])
            for i, solution in enumerate(solutions, 1):
                message.append(f"{i}. {solution.description}")
                for step in solution.steps:
                    message.append(f"   • {step}")
                if solution.common_causes:
                    message.append(f"   Common causes: {', '.join(solution.common_causes)}")
                message.append("")
        
        message.extend([
            "**🔧 General Troubleshooting**:",
            "   • Check system logs for more details",
            "   • Verify all dependencies are installed",
            "   • Ensure Python path is correctly set",
            "   • Try restarting the application",
            "",
            "**📞 Need Help?**:",
            "   • Check the documentation: docs/README.md",
            "   • Run diagnostic: python test_critical_imports.py",
            "   • Report issues if problem persists",
        ])
        
        return "\n".join(message)
    
    def _get_error_title(self) -> str:
        """Get a descriptive title for the error"""
        error_type = type(self.original_error).__name__
        
        if error_type == "ImportError":
            return "Missing System Component"
        elif error_type == "AttributeError":
            return "Component Configuration Error"
        elif error_type == "ModuleNotFoundError":
            return "Missing Python Module"
        else:
            return "System Initialization Error"
    
    def _get_solutions(self) -> List[ErrorSolution]:
        """Get relevant solutions based on the error type"""
        error_type = type(self.original_error).__name__
        error_msg = str(self.original_error).lower()
        
        solutions = []
        
        if error_type == "ImportError" or error_type == "ModuleNotFoundError":
            if "prioritylevel" in error_msg:
                solutions.append(ErrorSolution(
                    description="Fix PriorityLevel import issue",
                    steps=[
                        "Check expert_consultation_scenario.py for correct enum name",
                        "Use ConsultationPriority instead of PriorityLevel",
                        "Verify enum values are correctly defined"
                    ],
                    common_causes=["Enum name change", "Import statement typo"],
                    severity="high"
                ))
            
            if "token_management_service" in error_msg:
                solutions.append(ErrorSolution(
                    description="Fix TokenManagementService import",
                    steps=[
                        "Verify token_management_service.py exists",
                        "Check import statement in app_state.py",
                        "Ensure module is in Python path"
                    ],
                    common_causes=["Missing file", "Import path error"],
                    severity="high"
                ))
            
            solutions.append(ErrorSolution(
                description="General import fix",
                steps=[
                    "Run: pip install -e .",
                    "Check Python path: export PYTHONPATH=$PYTHONPATH:$(pwd)",
                    "Verify all files exist in correct locations",
                    "Check for syntax errors in imported modules"
                ],
                common_causes=["Installation incomplete", "Path issues", "File missing"],
                severity="medium"
            ))
        
        elif error_type == "AttributeError":
            if "_lock" in error_msg:
                solutions.append(ErrorSolution(
                    description="Fix initialization order issue",
                    steps=[
                        "Move _lock initialization before template initialization",
                        "Check __init__ method order in automated_report_generator.py",
                        "Ensure all attributes are initialized before use"
                    ],
                    common_causes=["Initialization order", "Missing attribute"],
                    severity="high"
                ))
            
            solutions.append(ErrorSolution(
                description="Fix attribute access issue",
                steps=[
                    "Check class definition for missing attributes",
                    "Verify property decorators are correct",
                    "Ensure proper inheritance and method overriding"
                ],
                common_causes=["Missing attribute", "Property configuration", "Inheritance issue"],
                severity="medium"
            ))
        
        # Add general solutions
        solutions.append(ErrorSolution(
            description="System diagnostic and repair",
            steps=[
                "Run import health check: python -c 'from src.core_services.import_health_checker import validate_imports_on_startup; validate_imports_on_startup()'",
                "Check system logs for detailed error information",
                "Try restarting the application",
                "If all else fails, reinstall dependencies"
            ],
            common_causes=["System state corruption", "Dependency conflict"],
            severity="low"
        ))
        
        return solutions


class UserFriendlyConfigError(Exception):
    """User-friendly configuration error"""
    
    def __init__(self, original_error: Exception, context: ErrorContext):
        self.original_error = original_error
        self.context = context
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        """Format a user-friendly configuration error message"""
        message = [
            f"⚙️ Configuration Error: {self.context.component}",
            "",
            f"**Issue**: {str(self.original_error)}",
            f"**Context**: {self.context.operation}",
            "",
            "**💡 Configuration Solutions**:",
            "   1. Check config.yaml file exists and is valid",
            "   2. Verify all required fields are present",
            "   3. Check file permissions and path",
            "   4. Run: python -c 'from src.config import settings; print(settings)'",
            "",
            "**🔧 Common Configuration Issues**:",
            "   • Missing config.yaml file",
            "   • Invalid YAML syntax",
            "   • Missing required configuration fields",
            "   • Incorrect file paths",
        ]
        
        return "\n".join(message)


class UserFriendlyServiceError(Exception):
    """User-friendly service error"""
    
    def __init__(self, original_error: Exception, context: ErrorContext):
        self.original_error = original_error
        self.context = context
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        """Format a user-friendly service error message"""
        message = [
            f"🔧 Service Error: {self.context.component}",
            "",
            f"**Service**: {self.context.component}",
            f"**Operation**: {self.context.operation}",
            f"**Error**: {str(self.original_error)}",
            "",
            "**💡 Service Solutions**:",
            "   1. Check if the service is properly initialized",
            "   2. Verify all dependencies are available",
            "   3. Check service logs for more details",
            "   4. Try restarting the specific service",
            "",
            "**🔧 Common Service Issues**:",
            "   • Service not initialized properly",
            "   • Dependency service unavailable",
            "   • Resource constraints (memory, disk space)",
            "   • Network connectivity issues",
        ]
        
        return "\n".join(message)


class ErrorHandler:
    """Centralized error handling with user-friendly messages"""
    
    def __init__(self):
        self.error_handlers = {
            ImportError: self._handle_import_error,
            ModuleNotFoundError: self._handle_import_error,
            AttributeError: self._handle_attribute_error,
            ValueError: self._handle_value_error,
            KeyError: self._handle_key_error,
            TypeError: self._handle_type_error,
            RuntimeError: self._handle_runtime_error,
        }
    
    def handle_error(self, error: Exception, context: ErrorContext) -> Exception:
        """Handle an exception and return a user-friendly version"""
        error_type = type(error)
        
        if error_type in self.error_handlers:
            return self.error_handlers[error_type](error, context)
        else:
            return self._handle_generic_error(error, context)
    
    def _handle_import_error(self, error: Exception, context: ErrorContext) -> Exception:
        """Handle ImportError and ModuleNotFoundError"""
        return UserFriendlyImportError(error, context)
    
    def _handle_attribute_error(self, error: Exception, context: ErrorContext) -> Exception:
        """Handle AttributeError"""
        return UserFriendlyImportError(error, context)  # Treat similar to import errors
    
    def _handle_value_error(self, error: Exception, context: ErrorContext) -> Exception:
        """Handle ValueError"""
        return UserFriendlyServiceError(error, context)
    
    def _handle_key_error(self, error: Exception, context: ErrorContext) -> Exception:
        """Handle KeyError"""
        return UserFriendlyConfigError(error, context)
    
    def _handle_type_error(self, error: Exception, context: ErrorContext) -> Exception:
        """Handle TypeError"""
        return UserFriendlyServiceError(error, context)
    
    def _handle_runtime_error(self, error: Exception, context: ErrorContext) -> Exception:
        """Handle RuntimeError"""
        return UserFriendlyServiceError(error, context)
    
    def _handle_generic_error(self, error: Exception, context: ErrorContext) -> Exception:
        """Handle any other type of error"""
        # Create a generic user-friendly error
        message = [
            f"❌ Unexpected Error: {self.context.component}",
            "",
            f"**Component**: {self.context.component}",
            f"**Operation**: {self.context.operation}",
            f"**Error Type**: {type(error).__name__}",
            f"**Error Message**: {str(error)}",
            "",
            "**💡 Solutions**:",
            "   1. Check system logs for more details",
            "   2. Try restarting the application",
            "   3. Verify all services are running",
            "   4. Contact support if the problem persists",
        ]
        
        return Exception("\n".join(message))


def create_error_context(
    component: str,
    operation: str,
    user_action: str,
    additional_info: Optional[Dict[str, Any]] = None
) -> ErrorContext:
    """Create an error context for better error messages"""
    return ErrorContext(
        component=component,
        operation=operation,
        user_action=user_action,
        additional_info=additional_info or {}
    )


def safe_import(module_path: str, class_name: str, context: ErrorContext) -> Any:
    """Safely import a module with user-friendly error handling"""
    error_handler = ErrorHandler()
    
    try:
        module = __import__(module_path, fromlist=[class_name])
        return getattr(module, class_name)
    except Exception as e:
        user_friendly_error = error_handler.handle_error(e, context)
        raise user_friendly_error from e


if __name__ == "__main__":
    # Test the user-friendly error handling
    import logging
    
    logging.basicConfig(level=logging.INFO)
    
    # Test import error handling
    context = create_error_context(
        component="AppState",
        operation="Initialization",
        user_action="Starting the DAIP-LIVE application"
    )
    
    try:
        # This should fail and show a user-friendly error
        result = safe_import("nonexistent.module", "NonExistentClass", context)
    except Exception as e:
        print("User-friendly error message:")
        print("=" * 60)
        print(e)
        print("=" * 60)
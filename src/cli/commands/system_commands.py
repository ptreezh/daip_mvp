"""
System health check command for the DAIP CLI.
"""

import asyncio
import importlib.util
import logging

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Initialize console and logger
console = Console()
logger = logging.getLogger(__name__)

# Check for required dependencies
MISSING_DEPENDENCIES = []
REQUIRED_MODULES = [
    'aiosqlite',
    'chromadb',
    'tiktoken',
    'frontmatter'  # Module name for python-frontmatter package
]

for module in REQUIRED_MODULES:
    if importlib.util.find_spec(module) is None:
        MISSING_DEPENDENCIES.append(module)

# Only import if dependencies are available
if not MISSING_DEPENDENCIES:
    from src.app_state import AppState
    from src.models import DebateConfig
    from src.protocols.debate_protocol import DebateProtocol
    from src.domain.entities import UserMessage


def check_system_health():
    """Check system health and return status information."""
    health_info = {}

    # 1. Configuration Loading Check
    try:
        from src.config import settings
        health_info["configuration"] = {"status": "✅ Loaded", "details": f"Log Level: {settings.log_level}"}
    except Exception as e:
        health_info["configuration"] = {"status": "❌ Failed", "details": f"Error loading config: {str(e)}"}

    # 2. LLM Configuration Check
    try:
        if health_info["configuration"]["status"] == "✅ Loaded" and hasattr(settings, 'llm') and settings.llm.provider:
            llm_details = f"Provider: {settings.llm.provider}"
            if hasattr(settings.llm, 'ollama') and hasattr(settings.llm.ollama, 'generation_model'):
                llm_details += f", Model: {settings.llm.ollama.generation_model}"
            health_info["llm_provider"] = {"status": "✅ Configured", "details": llm_details}
        else:
            health_info["llm_provider"] = {"status": "⚠️  Not configured", "details": "No LLM provider configured or config not loaded"}
    except Exception as e:
        health_info["llm_provider"] = {"status": "❌ Error", "details": f"LLM config error: {str(e)}"}

    # 3. Vector Store Configuration Check
    try:
        if health_info["configuration"]["status"] == "✅ Loaded" and hasattr(settings, 'vector_store') and hasattr(settings.vector_store, 'chroma_db_path'):
            health_info["vector_store"] = {"status": "✅ Configured", "details": f"Path: {settings.vector_store.chroma_db_path}"}
        else:
            health_info["vector_store"] = {"status": "⚠️  Not configured", "details": "Vector store path not set or config not loaded"}
    except Exception as e:
        health_info["vector_store"] = {"status": "❌ Error", "details": f"Vector store config error: {str(e)}"}

    # 4. Dependencies Check
    if MISSING_DEPENDENCIES:
        health_info["dependencies"] = {
            "status": "❌ Missing dependencies",
            "details": f"{len(MISSING_DEPENDENCIES)} packages missing: {', '.join(MISSING_DEPENDENCIES)}"
        }
    else:
        health_info["dependencies"] = {"status": "✅ Ready", "details": "All required modules installed"}

    # 5. Service Initialization Check (AppState)
    try:
        # Only attempt if dependencies are met
        if health_info["dependencies"]["status"] == "✅ Ready":
            app_state = AppState()
            health_info["core_services"] = {"status": "✅ Initialized", "details": "Core services (AppState) initialized"}
        else:
            health_info["core_services"] = {"status": "⚠️  Skipped", "details": "Dependencies missing, skipping service init"}
    except Exception as e:
        health_info["core_services"] = {"status": "❌ Error", "details": f"Service initialization error: {str(e)}"}

    # 6. Role Manager Check
    try:
        from src.core_services.role_manager import RoleManager
        role_manager = RoleManager()
        role_count = len(role_manager.list_roles())
        health_info["role_manager"] = {"status": "✅ Ready", "details": f"{role_count} roles loaded"}
    except Exception as e:
        health_info["role_manager"] = {"status": "❌ Error", "details": f"Role manager error: {str(e)}"}

    # 7. Wiki Service Check
    try:
        from src.core_services.wiki_service import WikiService
        wiki_service = WikiService()
        health_info["wiki_service"] = {"status": "✅ Ready", "details": "Wiki service initialized"}
    except Exception as e:
        health_info["wiki_service"] = {"status": "❌ Error", "details": f"Wiki service error: {str(e)}"}

    return health_info
import asyncio
import glob
import json
import logging
import os
import random
import sys
import time
import uuid
from typing import Any, Optional

import chromadb
import numpy as np

# Ensure the project root is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 延迟加载的服务模块
_service_cache = {}

def _import_service(module_path: str, class_name: str):
    """动态导入服务类"""
    key = f"{module_path}.{class_name}"
    if key not in _service_cache:
        try:
            module = __import__(module_path, fromlist=[class_name])
            service_class = getattr(module, class_name)
            _service_cache[key] = service_class
        except ImportError as e:
            logger.error(f"Failed to import {module_path}.{class_name}: {e}")
            raise
    return _service_cache[key]


logger = logging.getLogger(__name__)


class AppState:
    """
    A central state manager for the FastAPI application.
    It holds shared resources like database connections, models,
    and application-wide caches.
    """

    def __init__(self):
        logger.info("Initializing application state...")

        # --- Paths and Directories ---
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.roles_dir = os.path.join(self.base_dir, "roles")
        self.user_roles_file = os.path.join(self.roles_dir, "user_defined_roles.json")
        self.chat_log_dir = os.path.join(self.base_dir, "data")
        self.chat_log_file = os.path.join(self.chat_log_dir, "chat_logs.jsonl")
        self.vector_db_path = os.path.join(self.base_dir, "data", "role_vector_db")
        self.user_defined_dir = os.path.join(self.roles_dir, "user_defined")

        os.makedirs(self.roles_dir, exist_ok=True)
        os.makedirs(self.chat_log_dir, exist_ok=True)
        os.makedirs(self.user_defined_dir, exist_ok=True)

        # --- Caches and In-memory Storage ---
        self.parsing_tasks: dict[str, dict[str, Any]] = {}
        self.all_roles_details: dict[str, dict[str, str]] = {}
        self.tasks_db: dict[str, Any] = {}  # For collaborative tasks
        self.chat_engines: dict[str, Any] = {} # Simplified for now

        # --- Mock Data (for collaboration features) ---
        self.collaboration_users = []
        self.collaboration_projects = []
        self.collaboration_permissions = []

        # --- Vector DB Initialization ---
        self.chroma_client = chromadb.PersistentClient(path=self.vector_db_path)
        try:
            self.role_collection = self.chroma_client.get_collection("roles")
            logger.info("✅ Loaded existing role collection from ChromaDB.")
        except Exception:  # Catch any exception when collection doesn't exist
            self.role_collection = self.chroma_client.create_collection(name="roles")
            logger.info("✅ Created new role collection in ChromaDB.")

        # --- Kernel and Core Services Initialization ---
        # This is the correct, centralized way to do it.

        # 1. Foundational Components
        # Load configuration and initialize token management
        from src.config import settings
        from src.kernel.llm_interface import LLMFactory, LLMConfig
        
        # Import token management service
        from src.core_services.token_management_service import TokenManagementService
        
        # Initialize token management service
        self.token_management_service = TokenManagementService(settings.token_management)
        
        # Create LLM configuration from settings
        default_llm_config = LLMConfig(
            provider=settings.llm.provider,
            model=settings.llm.ollama.generation_model,
            base_url=settings.llm.ollama.host
        )
        self.fact_confidence_threshold = 0.75  # Configurable threshold
        
        # Create LLM interface with token management
        self.llm_interface = LLMFactory.create(config=default_llm_config, token_service=self.token_management_service)
        
        # Import and initialize unified tool manager
        from src.unified_tool_manager import UnifiedToolManager
        
        # Simple tool configuration
        tool_config = {
            "task_creation": {"enabled": True},
            "file_operations": {"enabled": True},
            "web_search": {"enabled": False},
            "code_execution": {"enabled": False}
        }
        self._unified_tool_manager = UnifiedToolManager(config=tool_config)

        # Import core services
        from src.core_services.memory_service import MemoryService
        from src.core_services.wiki_service import WikiService
        from src.core_services.synthesis_engine import SynthesisEngine
        from src.core_services.expert_service import ExpertService
        from src.core_services.task_manager import TaskManager
        from src.core_services.forum_service import ForumService

        # 2. Core Services (no dependencies or only foundational ones)
        self._memory_service = MemoryService(data_dir=os.path.join(self.base_dir, "data", "memory_banks"))
        self._wiki_service = WikiService(wiki_directory=os.path.join(self.base_dir, "data", "wiki"))
        self._task_manager = TaskManager(task_directory=os.path.join(self.base_dir, "data", "tasks"))
        self._synthesis_engine = SynthesisEngine(llm_interface=self.llm_interface)
        self._expert_service = ExpertService(self) # Passes self to access app_state properties
        self._forum_service = ForumService()
        
        # Import user profile and session management services
        from src.core_services.user_profile_service import UserProfileService
        from src.core_services.session_management_service import SessionManagementService
        
        # Initialize user profile and session management services
        self._user_profile_service = UserProfileService(
            data_dir=os.path.join(self.base_dir, settings.user_profile.data_dir)
        )
        self._session_management_service = SessionManagementService(
            user_profile_service=self._user_profile_service,
            auth_data_dir=os.path.join(self.base_dir, settings.session.auth_data_dir),
            session_expiry_minutes=settings.session.session_expiry_minutes
        )
        
        # Import universal context service
        from src.core_services.universal_context_service import UniversalContextService
        
        # Initialize universal context service (depends on token and memory services)
        self._universal_context_service = UniversalContextService(
            token_service=self.token_management_service,
            memory_service=self._memory_service
        )
        # Import fact extraction service
        from src.core_services.fact_extraction_service import FactExtractionService
        
        self._fact_extraction_service = FactExtractionService(
            llm_interface=self.llm_interface,
            memory_service=self._memory_service,
            confidence_threshold=self.fact_confidence_threshold,
        )
        
        # Import Human User Intelligence Layer services
        from src.core_services.intent_analysis_service import BasicIntentAnalysisService
        from src.core_services.personal_context_service import BasicPersonalContextService
        from src.core_services.prompt_optimization_service import BasicPromptOptimizationService
        
        # Initialize Human User Intelligence Layer services
        self._intent_analysis_service = BasicIntentAnalysisService(
            user_profile_service=self._user_profile_service,
            llm_interface=self.llm_interface
        )
        
        self._personal_context_service = BasicPersonalContextService(
            user_profile_service=self._user_profile_service,
            memory_service=self._memory_service
        )
        
        self._prompt_optimization_service = BasicPromptOptimizationService(
            intent_service=self._intent_analysis_service,
            personal_context_service=self._personal_context_service,
            llm_interface=self.llm_interface
        )

        # 3. Kernel Components that depend on Core Services
        # Create an Ollama client for InteractionManager
        import ollama
        from src.kernel.interaction_manager import InteractionManager
        
        ollama_client = ollama.AsyncClient(host=default_llm_config.base_url)
        self._interaction_manager = InteractionManager(
            client=ollama_client,
            model=default_llm_config.model
        )

        # 4. High-level Services that depend on other services
        # Note: These services are not critical for basic functionality
        # from src.protocols.protocol_service import ProtocolService
        # from src.collaboration.collaboration_service import CollaborationService
        # self.protocol_service = ProtocolService(self)
        # self.collaboration_service = CollaborationService(self)
        
        # 延迟加载的服务实例
        self._service_instances = {}
        
        # --- Startup Logic ---
        self.load_all_roles()
        logger.info("Application state initialized successfully.")

    def _initialize_schema_library(self):
        # This is a placeholder. In a real scenario, you would import and instantiate
        # your SchemaLibrary class here, similar to ExpertLibrary.
        class MockSchemaLibrary:
            def __init__(self):
                self.schemas = []
                self.schema_categories = {}
            def _extract_tags_from_schema(self, content): return []
        return MockSchemaLibrary()

    def get_text_embedding(self, text: str) -> list[float]:
        """Generates text embedding using a local Ollama model."""
        try:
            import requests

            # Load from environment variables with fallbacks
            embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text:latest")
            ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            url = f"{ollama_base_url}/api/embeddings"
            payload = {"model": embedding_model, "prompt": text}

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()["embedding"]
        except Exception as e:
            logger.warning(f"Error generating embedding with Ollama: {e}. Falling back to random vector.")
            np.random.seed(abs(hash(text)) % (2**32))
            return (np.random.rand(768) * 2 - 1).tolist()

    def load_all_roles(self):
        """Loads all role definitions from JSON files into memory."""
        roles_cache = {}
        role_files = glob.glob(os.path.join(self.roles_dir, "**", "*.json"), recursive=True)
        for role_file in role_files:
            try:
                with open(role_file, encoding="utf-8") as f:
                    content = json.load(f)
                    if os.path.basename(role_file) == "user_defined_roles.json":
                        if isinstance(content, list):
                            for role_data in content:
                                if isinstance(role_data, dict) and "name" in role_data:
                                    if "description" in role_data and "desc" not in role_data:
                                        role_data["desc"] = role_data["description"]
                                    if "desc" in role_data:
                                        roles_cache[role_data["name"]] = role_data
                    else:
                        if isinstance(content, dict) and "name" in content:
                            if "description" in content and "desc" not in content:
                                content["desc"] = content["description"]
                            if "desc" in content:
                                roles_cache[content["name"]] = content
            except (OSError, json.JSONDecodeError, TypeError) as e:
                logger.warning(f"Could not read or parse role file {role_file}: {e}")
        self.all_roles_details = roles_cache
        logger.info(f"Loaded {len(self.all_roles_details)} role definitions.")

    def build_role_embeddings(self):
        """Generates and caches embeddings for all loaded roles."""
        if not self.all_roles_details:
            self.load_all_roles()
        logger.info("Building role embeddings...")
        for name, info in self.all_roles_details.items():
            text_to_embed = f"{info.get('desc', '')} {name} {' '.join(info.get('tags', []))}"
            info["embedding"] = self.get_text_embedding(text_to_embed)
            self.upsert_role_to_vector_db(info)
        logger.info("Role embeddings built and stored in vector DB.")

    def upsert_role_to_vector_db(self, role: dict):
        """Upserts a role's data and embedding into the vector database."""
        if "name" not in role or "embedding" not in role:
            return

        doc_id = role["name"]
        embedding = role["embedding"]
        # Storing the full role dict as a JSON string in the document metadata
        document_content = json.dumps(role, ensure_ascii=False)

        self.role_collection.upsert(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[document_content]
        )

    def search_roles_by_vector(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Searches for the most relevant roles based on a query vector."""
        query_embedding = self.get_text_embedding(query)
        results = self.role_collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        if not results or not results.get("documents"):
            return []

        roles = [json.loads(doc) for doc in results["documents"][0]]
        scores = results.get("distances", [[]])[0]

        return [{"role": r, "score": float(s)} for r, s in zip(roles, scores)]

    async def call_llm_simulation(self, role_name: str, topic: str, history: list) -> str:
        """Simulates an LLM call with a role-playing prompt."""
        await asyncio.sleep(random.uniform(0.5, 1.5))  # Simulate network latency

        role_details = self.all_roles_details.get(role_name, {"desc": "A generic participant"})
        role_desc = role_details.get("desc", "No description available.")

        history_summary = "\n".join([f"- {msg.sender_name}: {msg.content}" for msg in history])

        prompt_for_llm = f"""### Role-play Simulation ###
Role: {role_name}
Description: {role_desc}
Topic: {topic}
History:
{history_summary}

Task: As {role_name}, provide a response to the last message.
"""

        last_user_message = history[-1].content if history else ""
        simulated_response = f"Ah, speaking as **{role_name}**... "
        if len(last_user_message) < 20:
            simulated_response += f'Regarding "{last_user_message}", that is an interesting point. From my perspective, we should also consider the implications on a broader scale. 🤔'
        else:
            simulated_response += f'On the topic of "{last_user_message[:25]}...", my expertise suggests a different approach. Have you thought about the long-term effects? Let\'s brainstorm.'

        simulated_response += "\n\n*(This is a simulated LLM response for demonstration.)*"
        logger.info(f"Simulated LLM call for role '{role_name}'.")
        return simulated_response

    def load_wiki_content(self, entry: str) -> str:
        path = f"wiki_entries/{entry}.json"
        if not os.path.exists(path):
            return ""
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("content", "")

    def save_wiki_version(self, entry: str, content: str, editor: str, timestamp: Optional[str] = None):
        path = f"wiki_entries/{entry}.json"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {"content": "", "history": []}
        data["content"] = content
        data["history"].append(
            {
                "version": max([v.get("version", 0) for v in data["history"]], default=0) + 1,
                "content": content,
                "editor": editor,
                "timestamp": timestamp or time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # 延迟加载属性
    @property
    def chat_service(self):
        """延迟加载聊天服务"""
        if 'chat_service' not in self._service_instances:
            try:
                ChatService = _import_service('src.core_services.chat_service', 'ChatService')
                self._service_instances['chat_service'] = ChatService(self)
            except Exception as e:
                logger.error(f"Failed to initialize ChatService: {e}")
                self._service_instances['chat_service'] = None
        return self._service_instances['chat_service']

    @property
    def document_service(self):
        """延迟加载文档服务"""
        if 'document_service' not in self._service_instances:
            try:
                DocumentService = _import_service('src.core_services.document_service', 'DocumentService')
                self._service_instances['document_service'] = DocumentService(self)
            except Exception as e:
                logger.warning(f"DocumentService initialization failed: {e}. Continuing without document processing.")
                self._service_instances['document_service'] = None
        return self._service_instances['document_service']

    @property
    def tool_service(self):
        """延迟加载工具服务"""
        if 'tool_service' not in self._service_instances:
            try:
                FileToolsService = _import_service('src.core_services.tool_service', 'FileToolsService')
                self._service_instances['tool_service'] = FileToolsService()
            except Exception as e:
                logger.error(f"Failed to initialize FileToolsService: {e}")
                self._service_instances['tool_service'] = None
        return self._service_instances['tool_service']

    @property
    def memory_tool_service(self):
        """延迟加载内存工具服务"""
        if 'memory_tool_service' not in self._service_instances:
            try:
                MemoryToolsService = _import_service('src.core_services.tool_service', 'MemoryToolsService')
                self._service_instances['memory_tool_service'] = MemoryToolsService(self)
            except Exception as e:
                logger.error(f"Failed to initialize MemoryToolsService: {e}")
                self._service_instances['memory_tool_service'] = None
        return self._service_instances['memory_tool_service']

    @property
    def virtual_team_service(self):
        """延迟加载虚拟团队服务"""
        if 'virtual_team_service' not in self._service_instances:
            try:
                VirtualTeamService = _import_service('src.core_services.virtual_team_service', 'VirtualTeamService')
                self._service_instances['virtual_team_service'] = VirtualTeamService(self, self.memory_tool_service)
            except Exception as e:
                logger.warning(f"VirtualTeamService initialization failed: {e}. Continuing without virtual team functionality.")
                self._service_instances['virtual_team_service'] = None
        return self._service_instances['virtual_team_service']

    @property
    def fact_validation_service(self):
        """延迟加载事实验证服务"""
        if 'fact_validation_service' not in self._service_instances:
            try:
                FactValidationService = _import_service('src.core_services.fact_validation_service', 'FactValidationService')
                self._service_instances['fact_validation_service'] = FactValidationService(self)
            except Exception as e:
                logger.error(f"Failed to initialize FactValidationService: {e}")
                self._service_instances['fact_validation_service'] = None
        return self._service_instances['fact_validation_service']

    @property
    def fact_extraction_service(self):
        """延迟加载事实提取服务"""
        if 'fact_extraction_service' not in self._service_instances:
            try:
                FactExtractionService = _import_service('src.core_services.fact_extraction_service', 'FactExtractionService')
                self._service_instances['fact_extraction_service'] = FactExtractionService(self)
            except Exception as e:
                logger.error(f"Failed to initialize FactExtractionService: {e}")
                self._service_instances['fact_extraction_service'] = None
        return self._service_instances['fact_extraction_service']

    @property
    def expert_service(self):
        """延迟加载专家服务"""
        if 'expert_service' not in self._service_instances:
            try:
                ExpertService = _import_service('src.core_services.expert_service', 'ExpertService')
                self._service_instances['expert_service'] = ExpertService(self)
            except Exception as e:
                logger.error(f"Failed to initialize ExpertService: {e}")
                self._service_instances['expert_service'] = None
        return self._service_instances['expert_service']

    @property
    def intent_analysis_service(self):
        """延迟加载意图分析服务"""
        if 'intent_analysis_service' not in self._service_instances:
            try:
                BasicIntentAnalysisService = _import_service('src.core_services.intent_analysis_service', 'BasicIntentAnalysisService')
                self._service_instances['intent_analysis_service'] = BasicIntentAnalysisService(self)
            except Exception as e:
                logger.error(f"Failed to initialize IntentAnalysisService: {e}")
                self._service_instances['intent_analysis_service'] = None
        return self._service_instances['intent_analysis_service']

    @property
    def memory_service(self):
        """延迟加载内存服务"""
        if 'memory_service' not in self._service_instances:
            try:
                MemoryService = _import_service('src.core_services.memory_service', 'MemoryService')
                self._service_instances['memory_service'] = MemoryService(self)
            except Exception as e:
                logger.error(f"Failed to initialize MemoryService: {e}")
                self._service_instances['memory_service'] = None
        return self._service_instances['memory_service']

    @property
    def personal_context_service(self):
        """延迟加载个人上下文服务"""
        if 'personal_context_service' not in self._service_instances:
            try:
                BasicPersonalContextService = _import_service('src.core_services.personal_context_service', 'BasicPersonalContextService')
                self._service_instances['personal_context_service'] = BasicPersonalContextService(self)
            except Exception as e:
                logger.error(f"Failed to initialize PersonalContextService: {e}")
                self._service_instances['personal_context_service'] = None
        return self._service_instances['personal_context_service']

    @property
    def prompt_optimization_service(self):
        """延迟加载提示优化服务"""
        if 'prompt_optimization_service' not in self._service_instances:
            try:
                BasicPromptOptimizationService = _import_service('src.core_services.prompt_optimization_service', 'BasicPromptOptimizationService')
                self._service_instances['prompt_optimization_service'] = BasicPromptOptimizationService(self)
            except Exception as e:
                logger.error(f"Failed to initialize PromptOptimizationService: {e}")
                self._service_instances['prompt_optimization_service'] = None
        return self._service_instances['prompt_optimization_service']

    @property
    def synthesis_engine(self):
        """延迟加载合成引擎"""
        if 'synthesis_engine' not in self._service_instances:
            try:
                SynthesisEngine = _import_service('src.core_services.synthesis_engine', 'SynthesisEngine')
                self._service_instances['synthesis_engine'] = SynthesisEngine(self)
            except Exception as e:
                logger.error(f"Failed to initialize SynthesisEngine: {e}")
                self._service_instances['synthesis_engine'] = None
        return self._service_instances['synthesis_engine']

    @property
    def task_manager(self):
        """延迟加载任务管理器"""
        if 'task_manager' not in self._service_instances:
            try:
                TaskManager = _import_service('src.core_services.task_manager', 'TaskManager')
                self._service_instances['task_manager'] = TaskManager(self)
            except Exception as e:
                logger.error(f"Failed to initialize TaskManager: {e}")
                self._service_instances['task_manager'] = None
        return self._service_instances['task_manager']

    @property
    def universal_context_service(self):
        """延迟加载通用上下文服务"""
        if 'universal_context_service' not in self._service_instances:
            try:
                UniversalContextService = _import_service('src.core_services.universal_context_service', 'UniversalContextService')
                self._service_instances['universal_context_service'] = UniversalContextService(self)
            except Exception as e:
                logger.error(f"Failed to initialize UniversalContextService: {e}")
                self._service_instances['universal_context_service'] = None
        return self._service_instances['universal_context_service']

    @property
    def user_profile_service(self):
        """延迟加载用户档案服务"""
        if 'user_profile_service' not in self._service_instances:
            try:
                UserProfileService = _import_service('src.core_services.user_profile_service', 'UserProfileService')
                self._service_instances['user_profile_service'] = UserProfileService(self)
            except Exception as e:
                logger.error(f"Failed to initialize UserProfileService: {e}")
                self._service_instances['user_profile_service'] = None
        return self._service_instances['user_profile_service']

    @property
    def session_management_service(self):
        """延迟加载会话管理服务"""
        if 'session_management_service' not in self._service_instances:
            try:
                SessionManagementService = _import_service('src.core_services.session_management_service', 'SessionManagementService')
                self._service_instances['session_management_service'] = SessionManagementService(self)
            except Exception as e:
                logger.error(f"Failed to initialize SessionManagementService: {e}")
                self._service_instances['session_management_service'] = None
        return self._service_instances['session_management_service']

    @property
    def wiki_service(self):
        """延迟加载Wiki服务"""
        if 'wiki_service' not in self._service_instances:
            try:
                WikiService = _import_service('src.core_services.wiki_service', 'WikiService')
                self._service_instances['wiki_service'] = WikiService(self)
            except Exception as e:
                logger.error(f"Failed to initialize WikiService: {e}")
                self._service_instances['wiki_service'] = None
        return self._service_instances['wiki_service']

    @property
    def forum_service(self):
        """延迟加载Forum服务"""
        if 'forum_service' not in self._service_instances:
            try:
                # Use the already initialized instance if available
                if hasattr(self, '_forum_service') and self._forum_service is not None:
                    self._service_instances['forum_service'] = self._forum_service
                else:
                    ForumService = _import_service('src.core_services.forum_service', 'ForumService')
                    self._service_instances['forum_service'] = ForumService()
            except Exception as e:
                logger.error(f"Failed to initialize ForumService: {e}")
                self._service_instances['forum_service'] = None
        return self._service_instances['forum_service']

    @property
    def interaction_manager(self):
        """延迟加载交互管理器"""
        if 'interaction_manager' not in self._service_instances:
            try:
                InteractionManager = _import_service('src.kernel.interaction_manager', 'InteractionManager')
                self._service_instances['interaction_manager'] = InteractionManager(self)
            except Exception as e:
                logger.error(f"Failed to initialize InteractionManager: {e}")
                self._service_instances['interaction_manager'] = None
        return self._service_instances['interaction_manager']

    @property
    def unified_tool_manager(self):
        """延迟加载统一工具管理器"""
        if 'unified_tool_manager' not in self._service_instances:
            try:
                # Use the already initialized instance if available
                if hasattr(self, '_unified_tool_manager') and self._unified_tool_manager is not None:
                    self._service_instances['unified_tool_manager'] = self._unified_tool_manager
                else:
                    UnifiedToolManager = _import_service('src.unified_tool_manager', 'UnifiedToolManager')
                    self._service_instances['unified_tool_manager'] = UnifiedToolManager(self)
            except Exception as e:
                logger.error(f"Failed to initialize UnifiedToolManager: {e}")
                self._service_instances['unified_tool_manager'] = None
        return self._service_instances['unified_tool_manager']

    @property
    def multi_agent_collaboration_system(self):
        """延迟加载多智能体协作系统"""
        if 'multi_agent_collaboration_system' not in self._service_instances:
            try:
                MultiAgentCollaborationSystem = _import_service('src.core_services.multi_agent_collaboration_system', 'MultiAgentCollaborationSystem')
                self._service_instances['multi_agent_collaboration_system'] = MultiAgentCollaborationSystem()
            except Exception as e:
                logger.error(f"Failed to initialize MultiAgentCollaborationSystem: {e}")
                self._service_instances['multi_agent_collaboration_system'] = None
        return self._service_instances['multi_agent_collaboration_system']

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

from src.core_services.chat_service import ChatService
from src.core_services.collaboration_service import CollaborationService
from src.core_services.document_service import DocumentService
from src.core_services.expert_service import ExpertService
from src.core_services.fact_validation_service import FactValidationService
from src.core_services.fact_extraction_service import FactExtractionService
from src.core_services.memory_service import MemoryService
from src.core_services.protocol_service import ProtocolService
from src.core_services.synthesis_engine import SynthesisEngine
from src.core_services.task_manager import TaskManager
from src.core_services.token_management_service import TokenManagementService
from src.core_services.universal_context_service import UniversalContextService
from src.core_services.tool_service import FileToolsService, MemoryToolsService
from src.core_services.virtual_team_service import VirtualTeamService
from src.core_services.wiki_service import WikiService
from src.kernel.interaction_manager import InteractionManager
from src.kernel.llm_interface import LLMInterface, LLMConfig  # Assuming a default config mechanism
from src.tool_config import tool_config
from src.unified_tool_manager import UnifiedToolManager


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
        self.unified_tool_manager = UnifiedToolManager(config=tool_config.to_dict())

        # 2. Core Services (no dependencies or only foundational ones)
        self.memory_service = MemoryService(data_dir=os.path.join(self.base_dir, "data", "memory_banks"))
        self.wiki_service = WikiService(wiki_directory=os.path.join(self.base_dir, "data", "wiki"))
        self.task_manager = TaskManager(task_directory=os.path.join(self.base_dir, "data", "tasks"))
        self.synthesis_engine = SynthesisEngine(llm_interface=self.llm_interface)
        self.expert_service = ExpertService(self) # Passes self to access app_state properties
        
        # Initialize universal context service (depends on token and memory services)
        self.universal_context_service = UniversalContextService(
            token_service=self.token_management_service,
            memory_service=self.memory_service
        )
        self.fact_extraction_service = FactExtractionService(
            llm_interface=self.llm_interface,
            memory_service=self.memory_service,
            confidence_threshold=self.fact_confidence_threshold,
        )

        # 3. Kernel Components that depend on Core Services
        # Create an Ollama client for InteractionManager
        import ollama
        ollama_client = ollama.AsyncClient(host=default_llm_config.base_url)
        self.interaction_manager = InteractionManager(
            client=ollama_client,
            model=default_llm_config.model
        )

        # 4. High-level Services that depend on other services
        self.protocol_service = ProtocolService(self)
        self.collaboration_service = CollaborationService(self)
        
        # Try to initialize DocumentService, but don't fail if it's not available
        try:
            self.document_service = DocumentService(self)
        except Exception as e:
            logger.warning(f"DocumentService initialization failed: {e}. Continuing without document processing.")
            self.document_service = None
            
        self.chat_service = ChatService(self)
        self.tool_service = FileToolsService() # Assuming it's simple
        self.memory_tool_service = MemoryToolsService(self)
        
        # Try to initialize VirtualTeamService, but don't fail if it's not available
        try:
            self.virtual_team_service = VirtualTeamService(self, self.memory_tool_service)
        except Exception as e:
            logger.warning(f"VirtualTeamService initialization failed: {e}. Continuing without virtual team functionality.")
            self.virtual_team_service = None
            
        self.fact_validation_service = FactValidationService(self)

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

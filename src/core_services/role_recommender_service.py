"""@Time    : 2024-07-18 14:00:00
@Author  : DAIP-LIVE Team
@File    : role_recommender_service.py
@Description:
    A service to recommend roles based on semantic similarity to a topic.
"""
import logging
from typing import TYPE_CHECKING

import chromadb

if TYPE_CHECKING:
    from src.core_services.role_manager import RoleManager
    from src.kernel.llm_interface import LLMInterface


class RoleRecommenderService:
    """Manages role recommendations using a vector database.
    """

    def __init__(
        self,
        role_manager: "RoleManager",
        llm_interface: "LLMInterface",
        db_path: str = "data/chroma_db",
        collection_name: str = "roles",
    ):
        """Initializes the service.

        Args:
            role_manager: The service to get role definitions from.
            llm_interface: The service to generate text embeddings.
            db_path: The file path for the persistent ChromaDB.
            collection_name: The name of the ChromaDB collection.
        """
        self.role_manager = role_manager
        self.llm_interface = llm_interface
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(name=self.collection_name)
        logging.info(
            f"RoleRecommenderService initialized with DB path: {db_path} and collection '{collection_name}'."
        )

    def build_index(self, force_rebuild: bool = False) -> None:
        """Builds or updates the vector index for all roles.

        Args:
            force_rebuild: If True, clears the existing index before building.
        """
        if force_rebuild:
            logging.info(f"Forcing rebuild of role index '{self.collection_name}'.")
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.get_or_create_collection(name=self.collection_name)

        if self.collection.count() > 0 and not force_rebuild:
            logging.info("Role index already exists. Skipping build.")
            return

        logging.info("Building role vector index...")
        roles = self.role_manager.list_roles()
        if not roles:
            logging.warning("No roles found to build index.")
            return

        documents = []
        metadatas = []
        ids = []

        for role in roles:
            # Create a rich text document for embedding
            doc_text = f"Role: {role.name}. Description: {role.description}. Capabilities: {', '.join(role.capabilities)}"
            documents.append(doc_text)
            metadatas.append({"id": role.id, "name": role.name, "description": role.description})
            ids.append(role.id)

        embeddings = self.llm_interface.get_embeddings(documents)
        self.collection.add(embeddings=embeddings, documents=documents, metadatas=metadatas, ids=ids)
        logging.info(f"Successfully built index for {self.collection.count()} roles.")

    def recommend_roles(self, topic: str, top_k: int = 3) -> list[dict]:
        """Recommends roles based on a topic."""
        logging.info(f"Recommending {top_k} roles for topic: '{topic}'")
        query_embedding = self.llm_interface.get_embedding(topic)
        results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)
        
        # The results['metadatas'][0] will be a list of dictionaries, each representing a recommended role's metadata.
        # We need to convert these back into Role objects using the RoleManager.
        recommended_role_ids = [m['id'] for m in results['metadatas'][0]] if results and results['metadatas'] else []
        
        # Fetch the full Role objects using the RoleManager
        recommended_roles = [self.role_manager.get_role_by_id(role_id) for role_id in recommended_role_ids]
        
        # Filter out any None values if a role couldn't be found (e.g., if file was deleted)
        return [role for role in recommended_roles if role is not None]

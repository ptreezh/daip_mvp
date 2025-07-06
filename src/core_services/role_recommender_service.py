# -*- coding: utf-8 -*-
"""
@Time    : 2024-07-18 14:00:00
@Author  : DAIP-LIVE Team
@File    : role_recommender_service.py
@Description:
    A service to recommend roles based on semantic similarity to a topic.
"""
import logging
from typing import Dict, List, TYPE_CHECKING

import chromadb

if TYPE_CHECKING:
    from src.core_services.role_manager import Role, RoleManager
    from src.kernel.llm_interface import LLMInterface


class RoleRecommenderService:
    """
    Manages role recommendations using a vector database.
    """

    def __init__(
        self,
        role_manager: "RoleManager",
        llm_interface: "LLMInterface",
        db_path: str = "data/chroma_db",
        collection_name: str = "roles",
    ):
        """
        Initializes the service.

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
        """
        Builds or updates the vector index for all roles.

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
            doc_text = f"Role: {role['name']}. Description: {role['desc']}. Tags: {', '.join(role.get('tags', []))}"
            documents.append(doc_text)
            metadatas.append({"name": role['name'], "desc": role['desc']})
            ids.append(role['name'])

        embeddings = self.llm_interface.get_embeddings(documents)
        self.collection.add(embeddings=embeddings, documents=documents, metadatas=metadatas, ids=ids)
        logging.info(f"Successfully built index for {self.collection.count()} roles.")

    def recommend_roles(self, topic: str, top_k: int = 3) -> List[Dict]:
        """Recommends roles based on a topic."""
        logging.info(f"Recommending {top_k} roles for topic: '{topic}'")
        query_embedding = self.llm_interface.get_embedding(topic)
        results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)
        
        return results['metadatas'][0] if results and results['metadatas'] else []
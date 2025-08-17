"""@Time    : 2025-07-03 17:38:24
@Author  : DAIP-LIVE Team
@File    : wiki_service.py
@Description:
    Provides a versioned knowledge base (Wiki) service.
"""

import json
import logging
import os
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional

import chromadb
import ollama
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class EditStatus(Enum):
    """Defines the status of an edit proposal."""

    PROPOSED = "proposed"
    APPLIED = "applied"
    REJECTED = "rejected"


@dataclass
class WikiEntryMetadata:
    """Stores metadata for a wiki entry in entry.json."""

    entry_name: str
    creator: str
    created_at: str
    last_editor: str
    last_modified: str
    tags: list[str]
    category: str
    versions: list[str]


@dataclass
class WikiVersion:
    """Represents a specific version of a wiki entry."""

    entry_name: str
    version: str
    author: str
    timestamp: str
    content: str
    change_summary: str


@dataclass
class WikiProposal:
    """Represents an edit proposal for a wiki entry."""

    proposal_id: str
    entry_name: str
    author: str
    timestamp: str
    base_version: str
    new_content: str
    change_summary: str
    status: EditStatus


class WikiService:
    """Handles the creation, versioning, and retrieval of wiki entries.
    """

    def __init__(self, wiki_directory: str = "daip_mvp_project/memory_bank/wiki/"):
        """Initializes the WikiService."""
        """
        Args:
            wiki_directory (str): The path to the directory for storing wiki files.
        """
        self._wiki_directory = Path(wiki_directory)
        os.makedirs(self._wiki_directory, exist_ok=True)
        # Initialize ChromaDB client for vector search
        vector_db_path = str(self._wiki_directory.parent / "vector_index")
        self.vector_client = chromadb.PersistentClient(path=vector_db_path)
        self.embedding_model = "nomic-embed-text"  # Recommended embedding model for Ollama
        self.chroma_collection = self.vector_client.get_or_create_collection(name="wiki_entries")
        logging.info(f"ChromaDB client initialized at '{vector_db_path}'.")
        logging.info(f"WikiService initialized. Wiki directory: {self._wiki_directory}")

    def _get_entry_path(self, entry_name: str) -> Path:
        """Returns the Path object for a given entry's directory."""
        return self._wiki_directory / entry_name

    def _read_entry_metadata(self, entry_name: str) -> Optional[WikiEntryMetadata]:
        """Reads and returns the WikiEntryMetadata object from entry.json."""
        entry_path = self._get_entry_path(entry_name)
        metadata_file = entry_path / "entry.json"
        if not metadata_file.exists():
            return None
        try:
            data = json.loads(metadata_file.read_text(encoding="utf-8"))
            return WikiEntryMetadata(**data)
        except (json.JSONDecodeError, TypeError) as e:
            logging.error(f"Error reading metadata for '{entry_name}': {e}")
            return None

    def _write_entry_metadata(
        self, entry_name: str, metadata: WikiEntryMetadata
    ) -> None:
        """Writes the WikiEntryMetadata object to entry.json."""
        entry_path = self._get_entry_path(entry_name)
        metadata_file = entry_path / "entry.json"
        try:
            metadata_file.write_text(
                json.dumps(asdict(metadata), indent=4), encoding="utf-8"
            )
        except Exception as e:
            logging.error(f"Error writing metadata for '{entry_name}': {e}")

    def _get_latest_version(self, metadata: WikiEntryMetadata) -> str:
        """Returns the latest version string from metadata."""
        # Assuming semantic versioning can be sorted lexicographically for simplicity
        return sorted(metadata.versions, reverse=True)[0]

    def _update_vector_index(self, entry_name: str, content: str):
        """Generates embedding and upserts the document into the vector index."""
        try:
            logging.info(f"Updating vector index for entry: {entry_name}")
            response = ollama.embeddings(model=self.embedding_model, prompt=content)
            embedding = response["embedding"]
            self.chroma_collection.upsert(
                ids=[entry_name],
                embeddings=[embedding],
                documents=[content]  # Store the full content for easy retrieval
            )
            logging.info(f"Successfully updated vector index for {entry_name}.")
        except Exception as e:
            logging.error(f"Failed to update vector index for {entry_name}: {e}")

    def _calculate_next_version(self, current_version: str) -> str:
        """Calculates the next minor version string."""
        parts = current_version.split(".")
        try:
            parts[-1] = str(int(parts[-1]) + 1)
            return ".".join(parts)
        except (ValueError, IndexError):
            # Fallback for non-standard versioning
            return f"{current_version}-next"

    def create_entry(
        self, entry_name: str, content: str, author_role: str, tags: list[str], category: str
    ) -> Optional[WikiVersion]:
        """Creates a new wiki entry and persists it to the file system.

        Args:
            entry_name (str): The name of the new entry.
            content (str): The initial content of the entry.
            author_role (str): The role of the author creating the entry.
            tags (List[str]): A list of tags for the entry.
            category (str): The category of the entry.

        Returns:
            Optional[WikiVersion]: The newly created WikiVersion object, or None if it fails.

        """
        logging.info(f"Creating new wiki entry: '{entry_name}' by '{author_role}'.")
        entry_dir = self._get_entry_path(entry_name)
        if entry_dir.exists():
            logging.warning(
                f"Wiki entry '{entry_name}' already exists. Creation aborted."
            )
            return None

        try:
            versions_dir = entry_dir / "versions"
            proposals_dir = entry_dir / "proposals"
            os.makedirs(versions_dir)
            os.makedirs(proposals_dir)

            initial_version = "1.0.0"
            timestamp = datetime.now().isoformat()

            # Create the first version file with YAML front matter
            version_metadata = {
                "version": initial_version,
                "author": author_role,
                "timestamp": timestamp,
                "change_summary": "Initial creation.",
            }
            version_content = f"---\n{yaml.dump(version_metadata)}---\n\n{content}"
            (versions_dir / f"{initial_version}.md").write_text(
                version_content, encoding="utf-8"
            )

            # Create the main entry metadata file
            entry_metadata = WikiEntryMetadata(
                entry_name=entry_name,
                creator=author_role,
                created_at=timestamp,
                last_editor=author_role,
                last_modified=timestamp,
                tags=tags,
                category=category,
                versions=[initial_version],
            )
            self._write_entry_metadata(entry_name, entry_metadata)

            # Update the vector index with the new entry
            self._update_vector_index(entry_name, content)

            logging.info(f"Successfully created wiki entry '{entry_name}'.")
            return WikiVersion(
                entry_name=entry_name,
                version=initial_version,
                author=author_role,
                timestamp=timestamp,
                content=content,
                change_summary="Initial creation.",
            )
        except Exception as e:
            logging.error(f"Failed to create wiki entry '{entry_name}': {e}")
            return None

    def get_entry(
        self, entry_name: str, version: Optional[str] = None
    ) -> Optional[WikiVersion]:
        """Retrieves a wiki entry by its name from the file system.

        Args:
            entry_name (str): The name of the entry to retrieve.
            version (Optional[str]): The specific version to retrieve. If None, gets the latest.

        Returns:
            Optional[WikiVersion]: The WikiVersion object if found, otherwise None.

        """
        logging.info(
            f"Retrieving wiki entry: '{entry_name}' (Version: {version or 'latest'})."
        )
        entry_dir = self._get_entry_path(entry_name)
        if not entry_dir.is_dir():
            logging.warning(f"Wiki entry '{entry_name}' not found.")
            return None

        try:
            if not version:
                metadata = self._read_entry_metadata(entry_name)
                if not metadata:
                    return None
                version = self._get_latest_version(metadata)

            file_to_read = entry_dir / "versions" / f"{version}.md"
            if not file_to_read.is_file():
                logging.warning(f"Wiki entry file not found: {file_to_read}")
                return None

            full_content = file_to_read.read_text(encoding="utf-8")

            # Parse YAML front matter and content
            parts = full_content.split("---", 2)
            if len(parts) < 3:
                logging.warning(f"Could not parse YAML front matter in {file_to_read}")
                return None

            front_matter = yaml.safe_load(parts[1])
            content = parts[2].strip()

            return WikiVersion(
                entry_name=entry_name,
                version=front_matter.get("version", version),
                author=front_matter.get("author", "Unknown"),
                timestamp=front_matter.get("timestamp", "Unknown"),
                content=content,
                change_summary=front_matter.get("change_summary", ""),
            )
        except Exception as e:
            logging.error(f"Failed to read wiki entry '{entry_name}': {e}")
            return None

    def propose_edit(
        self, entry_name: str, new_content: str, author_role: str, change_summary: str
    ) -> Optional[str]:
        """Proposes an edit to an existing wiki entry by creating a proposal file.

        Args:
            entry_name (str): The name of the entry to edit.
            new_content (str): The proposed new content.
            author_role (str): The role of the author proposing the edit.
            change_summary (str): A summary of the changes.

        Returns:
            Optional[str]: The proposal ID if successful, otherwise None.

        """
        entry_dir = self._get_entry_path(entry_name)
        if not entry_dir.is_dir():
            logging.warning(
                f"Cannot propose edit for non-existent wiki entry: '{entry_name}'."
            )
            return None

        try:
            metadata = self._read_entry_metadata(entry_name)
            if not metadata:
                return None
            base_version = self._get_latest_version(metadata)

            proposal_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()

            proposal = WikiProposal(
                proposal_id=proposal_id,
                entry_name=entry_name,
                author=author_role,
                timestamp=timestamp,
                base_version=base_version,
                new_content=new_content,
                change_summary=change_summary,
                status=EditStatus.PROPOSED,
            )

            proposals_dir = entry_dir / "proposals"
            proposal_file = proposals_dir / f"{proposal_id}.json"

            # Convert Enum to string for JSON serialization
            proposal_dict = asdict(proposal)
            proposal_dict["status"] = proposal.status.value

            proposal_file.write_text(
                json.dumps(proposal_dict, indent=4), encoding="utf-8"
            )

            logging.info(
                f"Successfully created edit proposal '{proposal_id}' for entry '{entry_name}'."
            )
            return proposal_id
        except Exception as e:
            logging.error(f"Failed to create edit proposal for '{entry_name}': {e}")
            return None

    def _apply_proposal(self, entry_name: str, proposal_id: str) -> bool:
        """Applies an accepted proposal, creating a new version of the wiki entry.

        Args:
            entry_name (str): The name of the entry the proposal belongs to.
            proposal_id (str): The ID of the proposal to apply.

        Returns:
            bool: True if the proposal was applied successfully, False otherwise.

        """
        logging.info(f"Attempting to apply proposal '{proposal_id}' to '{entry_name}'.")
        entry_dir = self._get_entry_path(entry_name)
        proposal_file = entry_dir / "proposals" / f"{proposal_id}.json"

        if not proposal_file.exists():
            logging.error(f"Proposal file not found: {proposal_file}")
            return False

        try:
            # Load proposal and metadata
            proposal_data = json.loads(proposal_file.read_text(encoding="utf-8"))
            # Convert status string from JSON back to Enum before instantiation
            proposal_data["status"] = EditStatus(proposal_data["status"])
            proposal = WikiProposal(**proposal_data)
            metadata = self._read_entry_metadata(entry_name)
            if not metadata:
                return False

            # Calculate new version and create new version file
            new_version = self._calculate_next_version(proposal.base_version)
            timestamp = datetime.now().isoformat()
            version_metadata = {
                "version": new_version,
                "author": proposal.author,
                "timestamp": timestamp,
                "change_summary": proposal.change_summary,
            }
            version_content = f"---\n{yaml.dump(version_metadata)}---\n\n{proposal.new_content}"
            (entry_dir / "versions" / f"{new_version}.md").write_text(
                version_content, encoding="utf-8"
            )

            # Update the vector index with the new content
            self._update_vector_index(entry_name, proposal.new_content)

            # Update entry metadata
            metadata.versions.append(new_version)
            metadata.last_editor = proposal.author
            metadata.last_modified = timestamp
            self._write_entry_metadata(entry_name, metadata)

            # Update proposal status
            proposal.status = EditStatus.APPLIED
            proposal_dict = asdict(proposal)
            proposal_dict["status"] = proposal.status.value
            proposal_file.write_text(json.dumps(proposal_dict, indent=4), encoding="utf-8")

            logging.info(
                f"Successfully applied proposal '{proposal_id}' as version '{new_version}'."
            )
            return True
        except Exception as e:
            logging.error(f"Failed to apply proposal '{proposal_id}': {e}")
            return False

    def search(self, query: str, top_k: int = 3) -> List[str]:
        """Performs a semantic search using a vector index.

        Args:
            query (str): The search query.
            top_k (int): The maximum number of results to return.

        Returns:
            List[str]: A list of content snippets from matching entries, ranked by semantic similarity.

        """
        logging.info(f"Performing semantic search for query: '{query}'")
        if not query.strip():
            return []

        try:
            query_embedding = ollama.embeddings(model=self.embedding_model, prompt=query)["embedding"]

            results = self.chroma_collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )

            retrieved_docs = results.get('documents', [[]])[0]
            retrieved_ids = results.get('ids', [[]])[0]

            snippets = [
                f"[{doc_id}]: {doc_content[:250]}..."
                for doc_id, doc_content in zip(retrieved_ids, retrieved_docs, strict=False)
            ]
            return snippets

        except Exception as e:
            logging.error(f"Semantic search failed: {e}")
            return []

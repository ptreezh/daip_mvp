"""@Time    : 2025-07-03 17:38:24
@Author  : DAIP-LIVE Team
@File    : wiki_service.py
@Description:
    Provides a versioned knowledge base (Wiki) service.
"""

import json
import logging
import os
import shutil
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any

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

    def _create_new_version(self, entry_name: str, content: str, author_role: str, change_summary: str) -> Optional[WikiVersion]:
        """Creates a new version of an existing wiki entry.
        
        Args:
            entry_name (str): The name of the entry.
            content (str): The content of the new version.
            author_role (str): The role of the author creating the version.
            change_summary (str): A summary of the changes.
            
        Returns:
            Optional[WikiVersion]: The newly created WikiVersion object, or None if it fails.
        """
        try:
            # Read existing metadata
            metadata = self._read_entry_metadata(entry_name)
            if not metadata:
                logging.error(f"Cannot create new version for '{entry_name}': metadata not found")
                return None
            
            # Calculate next version
            latest_version = self._get_latest_version(metadata)
            new_version = self._calculate_next_version(latest_version)
            
            # Create new version file
            entry_dir = self._get_entry_path(entry_name)
            versions_dir = entry_dir / "versions"
            
            timestamp = datetime.now().isoformat()
            version_metadata = {
                "version": new_version,
                "author": author_role,
                "timestamp": timestamp,
                "change_summary": change_summary,
            }
            version_content = f"---\n{yaml.dump(version_metadata)}---\n\n{content}"
            (versions_dir / f"{new_version}.md").write_text(
                version_content, encoding="utf-8"
            )
            
            # Update metadata
            metadata.versions.append(new_version)
            metadata.last_editor = author_role
            metadata.last_modified = timestamp
            self._write_entry_metadata(entry_name, metadata)
            
            # Update vector index
            self._update_vector_index(entry_name, content)
            
            logging.info(f"Successfully created new version '{new_version}' for wiki entry '{entry_name}'.")
            return WikiVersion(
                entry_name=entry_name,
                version=new_version,
                author=author_role,
                timestamp=timestamp,
                content=content,
                change_summary=change_summary,
            )
        except Exception as e:
            logging.error(f"Failed to create new version for wiki entry '{entry_name}': {e}")
            return None

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
            # If entry already exists, create a new version
            logging.info(f"Wiki entry '{entry_name}' already exists. Creating new version.")
            return self._create_new_version(entry_name, content, author_role, "New version created")

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

    def approve(self, entry_name: str, proposal_id: str) -> bool:
        """Approves an edit proposal and applies it to create a new version.
        
        Args:
            entry_name (str): The name of the wiki entry.
            proposal_id (str): The ID of the proposal to approve.
            
        Returns:
            bool: True if the proposal was approved and applied successfully, False otherwise.
        """
        logging.info(f"Attempting to approve proposal '{proposal_id}' for entry '{entry_name}'.")
        
        # Validate input
        if not entry_name or not proposal_id:
            logging.error("Entry name and proposal ID must be provided.")
            return False
            
        entry_dir = self._get_entry_path(entry_name)
        if not entry_dir.is_dir():
            logging.error(f"Wiki entry '{entry_name}' does not exist.")
            return False
            
        proposal_file = entry_dir / "proposals" / f"{proposal_id}.json"
        if not proposal_file.exists():
            logging.error(f"Proposal '{proposal_id}' not found for entry '{entry_name}'.")
            return False
            
        try:
            # Load proposal to check its status
            proposal_data = json.loads(proposal_file.read_text(encoding="utf-8"))
            proposal_status = EditStatus(proposal_data.get("status"))
            
            if proposal_status == EditStatus.APPLIED:
                logging.warning(f"Proposal '{proposal_id}' is already applied.")
                return True
            elif proposal_status == EditStatus.REJECTED:
                logging.error(f"Cannot approve rejected proposal '{proposal_id}'.")
                return False
            elif proposal_status != EditStatus.PROPOSED:
                logging.error(f"Invalid proposal status '{proposal_status.value}' for approval.")
                return False
                
            # Apply the proposal
            success = self._apply_proposal(entry_name, proposal_id)
            if success:
                logging.info(f"Successfully approved and applied proposal '{proposal_id}' for entry '{entry_name}'.")
            else:
                logging.error(f"Failed to apply proposal '{proposal_id}' for entry '{entry_name}'.")
            return success
            
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse proposal file '{proposal_file}': {e}")
            return False
        except Exception as e:
            logging.error(f"Failed to approve proposal '{proposal_id}' for entry '{entry_name}': {e}")
            return False

    def reject(self, entry_name: str, proposal_id: str) -> bool:
        """Rejects an edit proposal.
        
        Args:
            entry_name (str): The name of the wiki entry.
            proposal_id (str): The ID of the proposal to reject.
            
        Returns:
            bool: True if the proposal was rejected successfully, False otherwise.
        """
        logging.info(f"Attempting to reject proposal '{proposal_id}' for entry '{entry_name}'.")
        
        # Validate input
        if not entry_name or not proposal_id:
            logging.error("Entry name and proposal ID must be provided.")
            return False
            
        entry_dir = self._get_entry_path(entry_name)
        if not entry_dir.is_dir():
            logging.error(f"Wiki entry '{entry_name}' does not exist.")
            return False
            
        proposal_file = entry_dir / "proposals" / f"{proposal_id}.json"
        if not proposal_file.exists():
            logging.error(f"Proposal '{proposal_id}' not found for entry '{entry_name}'.")
            return False
            
        try:
            # Load proposal to check its status
            proposal_data = json.loads(proposal_file.read_text(encoding="utf-8"))
            proposal_status = EditStatus(proposal_data.get("status"))
            
            if proposal_status == EditStatus.APPLIED:
                logging.error(f"Cannot reject applied proposal '{proposal_id}'.")
                return False
            elif proposal_status == EditStatus.REJECTED:
                logging.warning(f"Proposal '{proposal_id}' is already rejected.")
                return True
            elif proposal_status != EditStatus.PROPOSED:
                logging.error(f"Invalid proposal status '{proposal_status.value}' for rejection.")
                return False
                
            # Update proposal status to REJECTED
            proposal_data["status"] = EditStatus.REJECTED.value
            proposal_file.write_text(json.dumps(proposal_data, indent=4), encoding="utf-8")
            
            logging.info(f"Successfully rejected proposal '{proposal_id}' for entry '{entry_name}'.")
            return True
            
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse proposal file '{proposal_file}': {e}")
            return False
        except Exception as e:
            logging.error(f"Failed to reject proposal '{proposal_id}' for entry '{entry_name}': {e}")
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

    def list_all_entries(self) -> List[str]:
        """List all wiki entry names.
        
        Returns:
            List[str]: A list of all entry names.
        """
        try:
            if not self._wiki_directory.exists():
                return []
            
            entries = []
            for entry_dir in self._wiki_directory.iterdir():
                if entry_dir.is_dir():
                    metadata = self._read_entry_metadata(entry_dir.name)
                    if metadata:
                        entries.append(entry_dir.name)
            
            return sorted(entries)
        except Exception as e:
            logging.error(f"Failed to list entries: {e}")
            return []

    def get_entry_statistics(self, entry_name: str) -> Dict[str, Any]:
        """Get statistics about a wiki entry.
        
        Args:
            entry_name (str): The name of the entry.
            
        Returns:
            Dict[str, Any]: Statistics about the entry.
        """
        try:
            metadata = self._read_entry_metadata(entry_name)
            if not metadata:
                return {}
            
            return {
                "entry_name": entry_name,
                "total_versions": len(metadata.versions),
                "creator": metadata.creator,
                "created_at": metadata.created_at,
                "last_editor": metadata.last_editor,
                "last_modified": metadata.last_modified,
                "tags": metadata.tags,
                "category": metadata.category,
                "latest_version": self._get_latest_version(metadata),
                "total_proposals": len(self._get_entry_proposals(entry_name))
            }
        except Exception as e:
            logging.error(f"Failed to get entry statistics: {e}")
            return {}

    def _get_entry_proposals(self, entry_name: str) -> List[WikiProposal]:
        """Get all proposals for an entry.
        
        Args:
            entry_name (str): The name of the entry.
            
        Returns:
            List[WikiProposal]: List of proposals.
        """
        proposals = []
        proposals_dir = self._get_entry_path(entry_name) / "proposals"
        
        if not proposals_dir.exists():
            return proposals
        
        try:
            for proposal_file in proposals_dir.glob("*.json"):
                try:
                    proposal_data = json.loads(proposal_file.read_text(encoding="utf-8"))
                    proposal_data["status"] = EditStatus(proposal_data["status"])
                    proposals.append(WikiProposal(**proposal_data))
                except Exception as e:
                    logging.warning(f"Failed to read proposal {proposal_file}: {e}")
            
            return sorted(proposals, key=lambda p: p.timestamp, reverse=True)
        except Exception as e:
            logging.error(f"Failed to get entry proposals: {e}")
            return []

    def list_pending_proposals(self) -> List[Dict[str, Any]]:
        """List all pending proposals across all wiki entries.
        
        Returns:
            List[Dict[str, Any]]: List of pending proposals with entry name and proposal details.
        """
        pending_proposals = []
        try:
            # Get all wiki entries
            entries = self.list_all_entries()
            
            # Iterate through each entry to get its proposals
            for entry_name in entries:
                proposals = self._get_entry_proposals(entry_name)
                
                # Filter for pending proposals and add to the list
                for proposal in proposals:
                    if proposal.status == EditStatus.PROPOSED:
                        pending_proposals.append({
                            "entry_name": entry_name,
                            "proposal_id": proposal.proposal_id,
                            "author": proposal.author,
                            "timestamp": proposal.timestamp,
                            "change_summary": proposal.change_summary
                        })
            
            # Sort by timestamp (newest first)
            return sorted(pending_proposals, key=lambda p: p["timestamp"], reverse=True)
        except Exception as e:
            logging.error(f"Failed to list pending proposals: {e}")
            return []

    def export_entry(self, entry_name: str, output_path: str, format: str = "json") -> bool:
        """Export a wiki entry to a file.
        
        Args:
            entry_name (str): The name of the entry to export.
            output_path (str): The path to export to.
            format (str): Export format ("json" or "markdown").
            
        Returns:
            bool: True if export was successful, False otherwise.
        """
        try:
            metadata = self._read_entry_metadata(entry_name)
            if not metadata:
                return False
            
            output_file = Path(output_path)
            
            if format.lower() == "json":
                # Export as JSON with all versions
                export_data = {
                    "metadata": asdict(metadata),
                    "versions": []
                }
                
                for version in metadata.versions:
                    version_file = self._get_entry_path(entry_name) / "versions" / f"{version}.md"
                    if version_file.exists():
                        full_content = version_file.read_text(encoding="utf-8")
                        parts = full_content.split("---", 2)
                        if len(parts) >= 3:
                            front_matter = yaml.safe_load(parts[1])
                            content = parts[2].strip()
                            export_data["versions"].append({
                                "version": version,
                                "front_matter": front_matter,
                                "content": content
                            })
                
                output_file.write_text(json.dumps(export_data, indent=2, ensure_ascii=False), encoding="utf-8")
                
            elif format.lower() == "markdown":
                # Export as markdown (latest version only)
                latest_version = self.get_entry(entry_name)
                if not latest_version:
                    return False
                
                markdown_content = f"""# {entry_name}

**Author:** {latest_version.author}  
**Created:** {metadata.created_at}  
**Last Modified:** {metadata.last_modified}  
**Version:** {latest_version.version}  
**Tags:** {', '.join(metadata.tags) if metadata.tags else 'None'}  
**Category:** {metadata.category}

---

{latest_version.content}
"""
                output_file.write_text(markdown_content, encoding="utf-8")
                
            else:
                logging.error(f"Unsupported export format: {format}")
                return False
            
            logging.info(f"Successfully exported entry '{entry_name}' to {output_path}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to export entry '{entry_name}': {e}")
            return False

    def import_entry_from_json(self, json_path: str, overwrite: bool = False) -> bool:
        """Import a wiki entry from a JSON file.
        
        Args:
            json_path (str): Path to the JSON file to import.
            overwrite (bool): Whether to overwrite if entry already exists.
            
        Returns:
            bool: True if import was successful, False otherwise.
        """
        try:
            json_file = Path(json_path)
            if not json_file.exists():
                logging.error(f"JSON file not found: {json_path}")
                return False
            
            import_data = json.loads(json_file.read_text(encoding="utf-8"))
            
            if "metadata" not in import_data:
                logging.error("Invalid import format: missing metadata")
                return False
            
            metadata = import_data["metadata"]
            entry_name = metadata["entry_name"]
            
            # Check if entry already exists
            entry_path = self._get_entry_path(entry_name)
            if entry_path.exists() and not overwrite:
                logging.error(f"Entry '{entry_name}' already exists and overwrite is False")
                return False
            
            # If overwriting, delete existing entry first
            if entry_path.exists() and overwrite:
                shutil.rmtree(entry_path)
            
            # Create entry directory structure
            versions_dir = entry_path / "versions"
            proposals_dir = entry_path / "proposals"
            os.makedirs(versions_dir, exist_ok=True)
            os.makedirs(proposals_dir, exist_ok=True)
            
            # Write metadata
            entry_metadata = WikiEntryMetadata(**metadata)
            self._write_entry_metadata(entry_name, entry_metadata)
            
            # Import versions
            if "versions" in import_data:
                for version_data in import_data["versions"]:
                    version = version_data["version"]
                    front_matter = version_data["front_matter"]
                    content = version_data["content"]
                    
                    version_content = f"---\n{yaml.dump(front_matter)}---\n\n{content}"
                    (versions_dir / f"{version}.md").write_text(version_content, encoding="utf-8")
            
            # Update vector index with the latest content
            if import_data.get("versions"):
                latest_content = import_data["versions"][-1]["content"]
                self._update_vector_index(entry_name, latest_content)
            
            logging.info(f"Successfully imported entry '{entry_name}' from {json_path}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to import entry from {json_path}: {e}")
            return False

    def delete_entry(self, entry_name: str, backup: bool = True) -> bool:
        """Delete a wiki entry.
        
        Args:
            entry_name (str): The name of the entry to delete.
            backup (bool): Whether to create a backup before deletion.
            
        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            entry_path = self._get_entry_path(entry_name)
            if not entry_path.exists():
                logging.warning(f"Entry '{entry_name}' does not exist")
                return False
            
            # Create backup if requested
            if backup:
                backup_path = self._wiki_directory / "backups" / f"{entry_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                backup_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure backup directory exists
                if backup_path.parent.exists():
                    shutil.copytree(entry_path, backup_path)
                    logging.info(f"Created backup at {backup_path}")
            
            # Remove from vector index
            try:
                self.chroma_collection.delete(ids=[entry_name])
                logging.info(f"Removed entry '{entry_name}' from vector index")
            except Exception as e:
                logging.warning(f"Failed to remove from vector index: {e}")
            
            # Delete the entry directory
            shutil.rmtree(entry_path)
            logging.info(f"Successfully deleted entry '{entry_name}'")
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to delete entry '{entry_name}': {e}")
            return False

    def compare_versions(self, entry_name: str, version1: str, version2: str) -> Dict[str, Any]:
        """Compare two versions of a wiki entry.
        
        Args:
            entry_name (str): The name of the entry.
            version1 (str): First version to compare.
            version2 (str): Second version to compare.
            
        Returns:
            Dict[str, Any]: Comparison result.
        """
        try:
            v1 = self.get_entry(entry_name, version1)
            v2 = self.get_entry(entry_name, version2)
            
            if not v1 or not v2:
                return {"error": "One or both versions not found"}
            
            # Simple text comparison (could be enhanced with diff algorithms)
            lines1 = v1.content.splitlines()
            lines2 = v2.content.splitlines()
            
            added = []
            removed = []
            
            # Simple line-by-line comparison
            for line in lines2:
                if line not in lines1:
                    added.append(line)
            
            for line in lines1:
                if line not in lines2:
                    removed.append(line)
            
            return {
                "entry_name": entry_name,
                "version1": {
                    "version": version1,
                    "author": v1.author,
                    "timestamp": v1.timestamp,
                    "content_length": len(v1.content)
                },
                "version2": {
                    "version": version2,
                    "author": v2.author,
                    "timestamp": v2.timestamp,
                    "content_length": len(v2.content)
                },
                "changes": {
                    "added_lines": len(added),
                    "removed_lines": len(removed),
                    "added_preview": added[:5] if added else [],
                    "removed_preview": removed[:5] if removed else []
                }
            }
            
        except Exception as e:
            logging.error(f"Failed to compare versions: {e}")
            return {"error": str(e)}

    def _import_debate_components(self):
        """Import the necessary components for debate engine integration.
        
        This method is separated to make it easier to mock in tests.
        """
        try:
            from src.debate_system.multi_role_dialogue_engine import MultiRoleDialogueEngine
            from src.core_services.role_manager import RoleManager
            from src.core_services.integrated_llm_manager import IntegratedLLMManager
            from src.core_services.memory_agent import MemAgent
            from src.debate_system.participant_management import ParticipantManager
            
            return {
                "MultiRoleDialogueEngine": MultiRoleDialogueEngine,
                "RoleManager": RoleManager,
                "IntegratedLLMManager": IntegratedLLMManager,
                "MemAgent": MemAgent,
                "ParticipantManager": ParticipantManager
            }
        except ImportError as e:
            # Re-raise the exception to be handled by the caller
            raise e

    def initiate_collaborative_edit(self, topic: str, initiator_role: str = "system") -> Dict[str, Any]:
        """Initiate a collaborative editing session using the debate engine.
        
        Args:
            topic (str): The topic to debate and create/edit wiki content for.
            initiator_role (str): The role that initiated the collaboration.
            
        Returns:
            Dict[str, Any]: Result of the collaborative editing initiation.
        """
        try:
            # Import the necessary components for debate engine integration
            components = self._import_debate_components()
            
            # For now, we'll return a placeholder result
            # In a full implementation, this would integrate with the debate engine
            return {
                "status": "initiated",
                "topic": topic,
                "initiator": initiator_role,
                "session_id": f"collab_{topic.replace(' ', '_')}_{int(datetime.now().timestamp())}",
                "message": "Collaborative editing session initiated successfully"
            }
            
        except ImportError as e:
            logging.error(f"Failed to import debate components: {e}")
            return {"error": f"Missing dependency: {str(e)}"}
        except Exception as e:
            logging.error(f"Failed to initiate collaborative editing: {e}")
            return {"error": str(e)}

"""Session Adapter for the SSKG.

This module implements the storage adapter for conversation states and session data.
"""

import json
from datetime import datetime
from typing import Any, Optional

try:
    from src.core_services.enhanced_sskg_manager import KnowledgeQuery, NodeType
except ImportError:
    # For testing purposes
    from enum import Enum

    class NodeType(str, Enum):
        SESSION = "session"

    class KnowledgeQuery:
        pass

from .base import StorageAdapter


class SessionAdapter(StorageAdapter):
    """Storage adapter for conversation states and session data.
    
    This adapter manages the storage and retrieval of session states,
    conversation history, and context information.
    """
<<<<<<< HEAD

    def store(self, session_data: Dict[str, Any], **kwargs) -> str:
=======
    
    def store(self, session_data: dict[str, Any], **kwargs) -> str:
>>>>>>> feature/core-services-refactor
        """Store session data in the SSKG.
        
        Args:
            session_data: Dictionary containing session information
                - session_id: Unique identifier for the session
                - state: Session state
                - metadata: Additional metadata
            **kwargs: Additional parameters
            
        Returns:
            ID of the stored session node

        """
        session_id = session_data.get("session_id")
        if not session_id:
            raise ValueError("session_id is required for session storage")

        # Get session state
        state = session_data.get("state", {})

        # Create session metadata
        session_metadata = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "adapter_type": "session"
        }

        # Add additional metadata if provided
        if "metadata" in session_data:
            session_metadata.update(session_data["metadata"])

        # Check if session already exists
        existing_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.SESSION],
            metadata_filters={"session_id": session_id, "adapter_type": "session"},
            limit=1
        ))

        if existing_nodes:
            # Update existing node
            existing_node = existing_nodes[0]
            updated_metadata = dict(existing_node.metadata)
            updated_metadata["updated_at"] = datetime.now().isoformat()

            # Add additional metadata if provided
            if "metadata" in session_data:
                updated_metadata.update(session_data["metadata"])

            self.sskg_manager.update_node(existing_node.id, {
                "content": json.dumps(state),
                "metadata": updated_metadata
            })

            session_node_id = existing_node.id
            self.logger.info(f"Updated session {session_id}")
        else:
            # Create new node
            session_node_id = self._create_node(
                node_type=NodeType.SESSION,
                content=json.dumps(state),
                confidence=1.0,
                metadata=session_metadata
            )
            self.logger.info(f"Created session {session_id}")

        return session_node_id
<<<<<<< HEAD

    def retrieve(self, session_id: str, **kwargs) -> Optional[Dict[str, Any]]:
=======
    
    def retrieve(self, session_id: str, **kwargs) -> Optional[dict[str, Any]]:
>>>>>>> feature/core-services-refactor
        """Retrieve session data from the SSKG.
        
        Args:
            session_id: ID of the session to retrieve
            **kwargs: Additional parameters
            
        Returns:
            Session data dictionary or None if not found

        """
        # Find session node
        session_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.SESSION],
            metadata_filters={"session_id": session_id, "adapter_type": "session"},
            limit=1
        ))

        if not session_nodes:
            return None

        session_node = session_nodes[0]

        # Parse session state
        try:
            state = json.loads(session_node.content)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse session state for session {session_id}")
            state = {}

        # Extract metadata
        metadata = dict(session_node.metadata)

        # Remove adapter-specific metadata
        metadata.pop("adapter_type", None)

        return {
            "session_id": session_id,
            "state": state,
            "metadata": metadata
        }
<<<<<<< HEAD

    def update(self, session_id: str, session_data: Dict[str, Any], **kwargs) -> bool:
=======
    
    def update(self, session_id: str, session_data: dict[str, Any], **kwargs) -> bool:
>>>>>>> feature/core-services-refactor
        """Update session data in the SSKG.
        
        Args:
            session_id: ID of the session to update
            session_data: Updated session data
            **kwargs: Additional parameters
            
        Returns:
            True if update was successful, False otherwise

        """
        # Find session node
        session_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.SESSION],
            metadata_filters={"session_id": session_id, "adapter_type": "session"},
            limit=1
        ))

        if not session_nodes:
            return False

        session_node = session_nodes[0]

        # Update session metadata
        updated_metadata = dict(session_node.metadata)
        updated_metadata["updated_at"] = datetime.now().isoformat()

        # Add additional metadata if provided
        if "metadata" in session_data:
            updated_metadata.update(session_data["metadata"])

        # Update content if state is provided
        updated_content = session_node.content
        if "state" in session_data:
            updated_content = json.dumps(session_data["state"])

        # Update session node
        success = self.sskg_manager.update_node(session_node.id, {
            "content": updated_content,
            "metadata": updated_metadata
        })

        if success:
            self.logger.info(f"Updated session {session_id}")

        return success

    def delete(self, session_id: str, **kwargs) -> bool:
        """Delete session data from the SSKG.
        
        Args:
            session_id: ID of the session to delete
            **kwargs: Additional parameters
            
        Returns:
            True if deletion was successful, False otherwise

        """
        # Find session node
        session_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.SESSION],
            metadata_filters={"session_id": session_id, "adapter_type": "session"},
            limit=1
        ))

        if not session_nodes:
            return False

        session_node = session_nodes[0]

        # Delete session node
        success = self.sskg_manager.delete_node(session_node.id)

        if success:
            self.logger.info(f"Deleted session {session_id}")

        return success
<<<<<<< HEAD

    def list_all(self, **kwargs) -> List[str]:
=======
    
    def list_all(self, **kwargs) -> list[str]:
>>>>>>> feature/core-services-refactor
        """List all session IDs.
        
        Args:
            **kwargs: Additional parameters
                - user_id: Filter by user ID
                - from_date: Filter by creation date (ISO format)
                - to_date: Filter by creation date (ISO format)
            
        Returns:
            List of session IDs

        """
        # Build metadata filters
        metadata_filters = {"adapter_type": "session"}

        # Filter by user ID if provided
        user_id = kwargs.get("user_id")
        if user_id:
            metadata_filters["user_id"] = user_id

        # Query sessions
        session_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.SESSION],
            metadata_filters=metadata_filters,
            limit=1000
        ))

        # Filter by date if provided
        from_date = kwargs.get("from_date")
        to_date = kwargs.get("to_date")

        if from_date or to_date:
            filtered_nodes = []
            for node in session_nodes:
                created_at = node.metadata.get("created_at", "")
                if not created_at:
                    continue

                if from_date and created_at < from_date:
                    continue

                if to_date and created_at > to_date:
                    continue

                filtered_nodes.append(node)

            session_nodes = filtered_nodes

        return [node.metadata.get("session_id", "") for node in session_nodes if node.metadata.get("session_id")]

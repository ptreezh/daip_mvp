"""
Storage layer for the Semantic Structured Knowledge Graph (SSKG).

This module implements the storage backend for the SSKG system,
providing persistent storage and retrieval of knowledge facts, memories,
and other entities.
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from .models import (
    KnowledgeFact, KnowledgeRelation, KnowledgeQuery,
    Memory, MemoryQuery, WikiPage, SessionState, ProjectState,
    SearchResult, SSKGStats, RelationType, MemoryType
)


class SSKGStorage:
    """
    Storage backend for the SSKG system using SQLite.
    
    This class provides persistent storage for all SSKG entities including
    knowledge facts, memories, wiki pages, sessions, and projects.
    """
    
    def __init__(self, db_path: str = "sskg.db"):
        """
        Initialize the SSKG storage system.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Knowledge facts table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_facts (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    source TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    last_updated TEXT NOT NULL,
                    version INTEGER NOT NULL DEFAULT 1,
                    domain TEXT,
                    topic TEXT,
                    keywords TEXT,  -- JSON array
                    validation_status TEXT DEFAULT 'unvalidated',
                    validation_history TEXT,  -- JSON array
                    access_count INTEGER DEFAULT 0,
                    last_accessed TEXT,
                    metadata TEXT,  -- JSON object
                    tags TEXT  -- JSON array
                )
            """)
            
            # Knowledge relations table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_relations (
                    id TEXT PRIMARY KEY,
                    source_fact_id TEXT NOT NULL,
                    target_fact_id TEXT NOT NULL,
                    relation_type TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    evidence TEXT,  -- JSON array
                    metadata TEXT,  -- JSON object
                    created_at TEXT NOT NULL,
                    created_by TEXT,
                    FOREIGN KEY (source_fact_id) REFERENCES knowledge_facts (id),
                    FOREIGN KEY (target_fact_id) REFERENCES knowledge_facts (id)
                )
            """)
            
            # Memories table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    owner_id TEXT NOT NULL,
                    importance REAL NOT NULL,
                    relevance_context TEXT,
                    timestamp TEXT NOT NULL,
                    last_accessed TEXT NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    related_memories TEXT,  -- JSON array
                    associated_facts TEXT,  -- JSON array
                    context TEXT,  -- JSON object
                    metadata TEXT,  -- JSON object
                    tags TEXT  -- JSON array
                )
            """)
            
            # Wiki pages table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS wiki_pages (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    version INTEGER NOT NULL DEFAULT 1,
                    created_by TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_updated TEXT NOT NULL,
                    contributors TEXT,  -- JSON array
                    category TEXT,
                    tags TEXT,  -- JSON array
                    linked_pages TEXT,  -- JSON array
                    associated_facts TEXT,  -- JSON array
                    view_count INTEGER DEFAULT 0,
                    last_viewed TEXT,
                    metadata TEXT  -- JSON object
                )
            """)
            
            # Session states table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS session_states (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    state_data TEXT NOT NULL,  -- JSON object
                    context TEXT,  -- JSON object
                    created_at TEXT NOT NULL,
                    last_updated TEXT NOT NULL,
                    expires_at TEXT,
                    active_roles TEXT,  -- JSON array
                    conversation_history TEXT,  -- JSON array
                    metadata TEXT  -- JSON object
                )
            """)
            
            # Project states table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS project_states (
                    project_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    config TEXT,  -- JSON object
                    settings TEXT,  -- JSON object
                    created_at TEXT NOT NULL,
                    last_updated TEXT NOT NULL,
                    participants TEXT,  -- JSON array
                    associated_sessions TEXT,  -- JSON array
                    resources TEXT,  -- JSON object
                    artifacts TEXT,  -- JSON array
                    metadata TEXT,  -- JSON object
                    tags TEXT  -- JSON array
                )
            """)
            
            # Create indexes for better performance
            self._create_indexes(conn)
            
            conn.commit()
    
    def _create_indexes(self, conn: sqlite3.Connection) -> None:
        """Create database indexes for better query performance."""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_facts_content ON knowledge_facts(content)",
            "CREATE INDEX IF NOT EXISTS idx_facts_source ON knowledge_facts(source)",
            "CREATE INDEX IF NOT EXISTS idx_facts_domain ON knowledge_facts(domain)",
            "CREATE INDEX IF NOT EXISTS idx_facts_confidence ON knowledge_facts(confidence)",
            "CREATE INDEX IF NOT EXISTS idx_facts_timestamp ON knowledge_facts(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_relations_source ON knowledge_relations(source_fact_id)",
            "CREATE INDEX IF NOT EXISTS idx_relations_target ON knowledge_relations(target_fact_id)",
            "CREATE INDEX IF NOT EXISTS idx_relations_type ON knowledge_relations(relation_type)",
            "CREATE INDEX IF NOT EXISTS idx_memories_owner ON memories(owner_id)",
            "CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type)",
            "CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance)",
            "CREATE INDEX IF NOT EXISTS idx_wiki_title ON wiki_pages(title)",
            "CREATE INDEX IF NOT EXISTS idx_wiki_category ON wiki_pages(category)"
        ]
        
        for index_sql in indexes:
            conn.execute(index_sql)    

    def store_fact(self, fact: KnowledgeFact) -> str:
        """
        Store a knowledge fact in the database.
        
        Args:
            fact: Knowledge fact to store
            
        Returns:
            ID of the stored fact
        """
        if not fact.id:
            import uuid
            fact.id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO knowledge_facts (
                    id, content, source, confidence, timestamp, last_updated, version,
                    domain, topic, keywords, validation_status, validation_history,
                    access_count, last_accessed, metadata, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fact.id, fact.content, fact.source, fact.confidence,
                fact.timestamp.isoformat(), fact.last_updated.isoformat(), fact.version,
                fact.domain, fact.topic, json.dumps(fact.keywords),
                fact.validation_status, json.dumps(fact.validation_history),
                fact.access_count, 
                fact.last_accessed.isoformat() if fact.last_accessed else None,
                json.dumps(fact.metadata), json.dumps(fact.tags)
            ))
            
            # Store relations
            for relation in fact.relations:
                if not relation.id:
                    import uuid
                    relation.id = str(uuid.uuid4())
                
                conn.execute("""
                    INSERT OR REPLACE INTO knowledge_relations (
                        id, source_fact_id, target_fact_id, relation_type, confidence,
                        evidence, metadata, created_at, created_by
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    relation.id, fact.id, relation.target_fact_id, relation.relation_type.value,
                    relation.confidence, json.dumps(relation.evidence),
                    json.dumps(relation.metadata), relation.created_at.isoformat(),
                    relation.created_by
                ))
            
            conn.commit()
        
        return fact.id
    
    def retrieve_fact(self, fact_id: str) -> Optional[KnowledgeFact]:
        """
        Retrieve a knowledge fact by ID.
        
        Args:
            fact_id: ID of the fact to retrieve
            
        Returns:
            Knowledge fact or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Get the fact
            cursor = conn.execute("""
                SELECT * FROM knowledge_facts WHERE id = ?
            """, (fact_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Get relations
            relations_cursor = conn.execute("""
                SELECT * FROM knowledge_relations WHERE source_fact_id = ?
            """, (fact_id,))
            
            relations = []
            for rel_row in relations_cursor.fetchall():
                relations.append(KnowledgeRelation(
                    id=rel_row['id'],
                    relation_type=RelationType(rel_row['relation_type']),
                    target_fact_id=rel_row['target_fact_id'],
                    confidence=rel_row['confidence'],
                    evidence=json.loads(rel_row['evidence'] or '[]'),
                    metadata=json.loads(rel_row['metadata'] or '{}'),
                    created_at=datetime.fromisoformat(rel_row['created_at']),
                    created_by=rel_row['created_by']
                ))
            
            # Create fact object
            fact = KnowledgeFact(
                id=row['id'],
                content=row['content'],
                source=row['source'],
                confidence=row['confidence'],
                timestamp=datetime.fromisoformat(row['timestamp']),
                last_updated=datetime.fromisoformat(row['last_updated']),
                version=row['version'],
                domain=row['domain'],
                topic=row['topic'],
                keywords=json.loads(row['keywords'] or '[]'),
                relations=relations,
                validation_status=row['validation_status'],
                validation_history=json.loads(row['validation_history'] or '[]'),
                access_count=row['access_count'],
                last_accessed=datetime.fromisoformat(row['last_accessed']) if row['last_accessed'] else None,
                metadata=json.loads(row['metadata'] or '{}'),
                tags=json.loads(row['tags'] or '[]')
            )
            
            # Mark as accessed
            fact.mark_accessed()
            self._update_fact_access(fact_id, fact.access_count, fact.last_accessed)
            
            return fact
    
    def _update_fact_access(self, fact_id: str, access_count: int, last_accessed: datetime) -> None:
        """Update fact access statistics."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE knowledge_facts 
                SET access_count = ?, last_accessed = ?
                WHERE id = ?
            """, (access_count, last_accessed.isoformat(), fact_id))
            conn.commit()
    
    def search_facts(self, query: KnowledgeQuery) -> List[KnowledgeFact]:
        """
        Search for knowledge facts based on query criteria.
        
        Args:
            query: Search query specification
            
        Returns:
            List of matching knowledge facts
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Build WHERE clause
            where_conditions = []
            params = []
            
            if query.content:
                where_conditions.append("content LIKE ?")
                params.append(f"%{query.content}%")
            
            if query.source:
                where_conditions.append("source = ?")
                params.append(query.source)
            
            if query.domain:
                where_conditions.append("domain = ?")
                params.append(query.domain)
            
            if query.topic:
                where_conditions.append("topic = ?")
                params.append(query.topic)
            
            if query.min_confidence > 0:
                where_conditions.append("confidence >= ?")
                params.append(query.min_confidence)
            
            if query.max_confidence < 1:
                where_conditions.append("confidence <= ?")
                params.append(query.max_confidence)
            
            if query.validation_status:
                where_conditions.append("validation_status = ?")
                params.append(query.validation_status)
            
            if query.time_range:
                where_conditions.append("timestamp BETWEEN ? AND ?")
                params.extend([query.time_range[0].isoformat(), query.time_range[1].isoformat()])
            
            if query.updated_since:
                where_conditions.append("last_updated >= ?")
                params.append(query.updated_since.isoformat())
            
            # Build ORDER BY clause
            order_by = "timestamp DESC"  # Default ordering
            if query.sort_by == "confidence":
                order_by = f"confidence {query.sort_order.upper()}"
            elif query.sort_by == "access_count":
                order_by = f"access_count {query.sort_order.upper()}"
            
            # Build final query
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            sql = f"""
                SELECT * FROM knowledge_facts 
                WHERE {where_clause}
                ORDER BY {order_by}
                LIMIT ? OFFSET ?
            """
            params.extend([query.limit, query.offset])
            
            cursor = conn.execute(sql, params)
            facts = []
            
            for row in cursor.fetchall():
                # Get relations for this fact
                relations_cursor = conn.execute("""
                    SELECT * FROM knowledge_relations WHERE source_fact_id = ?
                """, (row['id'],))
                
                relations = []
                for rel_row in relations_cursor.fetchall():
                    relations.append(KnowledgeRelation(
                        id=rel_row['id'],
                        relation_type=RelationType(rel_row['relation_type']),
                        target_fact_id=rel_row['target_fact_id'],
                        confidence=rel_row['confidence'],
                        evidence=json.loads(rel_row['evidence'] or '[]'),
                        metadata=json.loads(rel_row['metadata'] or '{}'),
                        created_at=datetime.fromisoformat(rel_row['created_at']),
                        created_by=rel_row['created_by']
                    ))
                
                fact = KnowledgeFact(
                    id=row['id'],
                    content=row['content'],
                    source=row['source'],
                    confidence=row['confidence'],
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    last_updated=datetime.fromisoformat(row['last_updated']),
                    version=row['version'],
                    domain=row['domain'],
                    topic=row['topic'],
                    keywords=json.loads(row['keywords'] or '[]'),
                    relations=relations,
                    validation_status=row['validation_status'],
                    validation_history=json.loads(row['validation_history'] or '[]'),
                    access_count=row['access_count'],
                    last_accessed=datetime.fromisoformat(row['last_accessed']) if row['last_accessed'] else None,
                    metadata=json.loads(row['metadata'] or '{}'),
                    tags=json.loads(row['tags'] or '[]')
                )
                
                facts.append(fact)
            
            return facts    

    def delete_fact(self, fact_id: str) -> bool:
        """
        Delete a knowledge fact and its relations.
        
        Args:
            fact_id: ID of the fact to delete
            
        Returns:
            True if deletion was successful
        """
        with sqlite3.connect(self.db_path) as conn:
            # Delete relations first (foreign key constraints)
            conn.execute("DELETE FROM knowledge_relations WHERE source_fact_id = ? OR target_fact_id = ?", 
                        (fact_id, fact_id))
            
            # Delete the fact
            cursor = conn.execute("DELETE FROM knowledge_facts WHERE id = ?", (fact_id,))
            conn.commit()
            
            return cursor.rowcount > 0
    
    def store_memory(self, memory: Memory) -> str:
        """
        Store a memory item.
        
        Args:
            memory: Memory to store
            
        Returns:
            ID of the stored memory
        """
        if not memory.id:
            import uuid
            memory.id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO memories (
                    id, content, memory_type, owner_id, importance, relevance_context,
                    timestamp, last_accessed, access_count, related_memories,
                    associated_facts, context, metadata, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                memory.id, memory.content, memory.memory_type.value, memory.owner_id,
                memory.importance, memory.relevance_context,
                memory.timestamp.isoformat(), memory.last_accessed.isoformat(),
                memory.access_count, json.dumps(memory.related_memories),
                json.dumps(memory.associated_facts), json.dumps(memory.context),
                json.dumps(memory.metadata), json.dumps(memory.tags)
            ))
            conn.commit()
        
        return memory.id
    
    def search_memories(self, query: MemoryQuery) -> List[Memory]:
        """
        Search for memories based on query criteria.
        
        Args:
            query: Memory query specification
            
        Returns:
            List of matching memories
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Build WHERE clause
            where_conditions = []
            params = []
            
            if query.content:
                where_conditions.append("content LIKE ?")
                params.append(f"%{query.content}%")
            
            if query.memory_type:
                where_conditions.append("memory_type = ?")
                params.append(query.memory_type.value)
            
            if query.owner_id:
                where_conditions.append("owner_id = ?")
                params.append(query.owner_id)
            
            if query.min_importance > 0:
                where_conditions.append("importance >= ?")
                params.append(query.min_importance)
            
            if query.time_range:
                where_conditions.append("timestamp BETWEEN ? AND ?")
                params.extend([query.time_range[0].isoformat(), query.time_range[1].isoformat()])
            
            # Build ORDER BY clause
            order_by = "timestamp DESC"  # Default ordering
            if query.sort_by == "importance":
                order_by = f"importance {query.sort_order.upper()}"
            elif query.sort_by == "access_count":
                order_by = f"access_count {query.sort_order.upper()}"
            
            # Build final query
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            sql = f"""
                SELECT * FROM memories 
                WHERE {where_clause}
                ORDER BY {order_by}
                LIMIT ? OFFSET ?
            """
            params.extend([query.limit, query.offset])
            
            cursor = conn.execute(sql, params)
            memories = []
            
            for row in cursor.fetchall():
                memory = Memory(
                    id=row['id'],
                    content=row['content'],
                    memory_type=MemoryType(row['memory_type']),
                    owner_id=row['owner_id'],
                    importance=row['importance'],
                    relevance_context=row['relevance_context'],
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    last_accessed=datetime.fromisoformat(row['last_accessed']),
                    access_count=row['access_count'],
                    related_memories=json.loads(row['related_memories'] or '[]'),
                    associated_facts=json.loads(row['associated_facts'] or '[]'),
                    context=json.loads(row['context'] or '{}'),
                    metadata=json.loads(row['metadata'] or '{}'),
                    tags=json.loads(row['tags'] or '[]')
                )
                memories.append(memory)
            
            return memories
    
    def store_wiki_page(self, page: WikiPage) -> bool:
        """
        Store a wiki page.
        
        Args:
            page: Wiki page to store
            
        Returns:
            True if storage was successful
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO wiki_pages (
                    id, title, content, version, created_by, created_at, last_updated,
                    contributors, category, tags, linked_pages, associated_facts,
                    view_count, last_viewed, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                page.id, page.title, page.content, page.version,
                page.created_by, page.created_at.isoformat(), page.last_updated.isoformat(),
                json.dumps(page.contributors), page.category, json.dumps(page.tags),
                json.dumps(page.linked_pages), json.dumps(page.associated_facts),
                page.view_count, 
                page.last_viewed.isoformat() if page.last_viewed else None,
                json.dumps(page.metadata)
            ))
            conn.commit()
            return True
    
    def retrieve_wiki_page(self, page_id: str) -> Optional[WikiPage]:
        """
        Retrieve a wiki page by ID.
        
        Args:
            page_id: ID of the page to retrieve
            
        Returns:
            Wiki page or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute("SELECT * FROM wiki_pages WHERE id = ?", (page_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            page = WikiPage(
                id=row['id'],
                title=row['title'],
                content=row['content'],
                version=row['version'],
                created_by=row['created_by'],
                created_at=datetime.fromisoformat(row['created_at']),
                last_updated=datetime.fromisoformat(row['last_updated']),
                contributors=json.loads(row['contributors'] or '[]'),
                category=row['category'],
                tags=json.loads(row['tags'] or '[]'),
                linked_pages=json.loads(row['linked_pages'] or '[]'),
                associated_facts=json.loads(row['associated_facts'] or '[]'),
                view_count=row['view_count'],
                last_viewed=datetime.fromisoformat(row['last_viewed']) if row['last_viewed'] else None,
                metadata=json.loads(row['metadata'] or '{}')
            )
            
            # Mark as viewed
            page.mark_viewed()
            self._update_page_view(page_id, page.view_count, page.last_viewed)
            
            return page
    
    def _update_page_view(self, page_id: str, view_count: int, last_viewed: datetime) -> None:
        """Update page view statistics."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE wiki_pages 
                SET view_count = ?, last_viewed = ?
                WHERE id = ?
            """, (view_count, last_viewed.isoformat(), page_id))
            conn.commit()
    
    def store_session_state(self, session: SessionState) -> bool:
        """
        Store session state.
        
        Args:
            session: Session state to store
            
        Returns:
            True if storage was successful
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO session_states (
                    session_id, user_id, state_data, context, created_at, last_updated,
                    expires_at, active_roles, conversation_history, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session.session_id, session.user_id,
                json.dumps(session.state_data), json.dumps(session.context),
                session.created_at.isoformat(), session.last_updated.isoformat(),
                session.expires_at.isoformat() if session.expires_at else None,
                json.dumps(session.active_roles), json.dumps(session.conversation_history),
                json.dumps(session.metadata)
            ))
            conn.commit()
            return True
    
    def retrieve_session_state(self, session_id: str) -> Optional[SessionState]:
        """
        Retrieve session state by ID.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session state or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute("SELECT * FROM session_states WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return SessionState(
                session_id=row['session_id'],
                user_id=row['user_id'],
                state_data=json.loads(row['state_data'] or '{}'),
                context=json.loads(row['context'] or '{}'),
                created_at=datetime.fromisoformat(row['created_at']),
                last_updated=datetime.fromisoformat(row['last_updated']),
                expires_at=datetime.fromisoformat(row['expires_at']) if row['expires_at'] else None,
                active_roles=json.loads(row['active_roles'] or '[]'),
                conversation_history=json.loads(row['conversation_history'] or '[]'),
                metadata=json.loads(row['metadata'] or '{}')
            )
    
    def store_project_state(self, project: ProjectState) -> bool:
        """
        Store project state.
        
        Args:
            project: Project state to store
            
        Returns:
            True if storage was successful
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO project_states (
                    project_id, name, description, config, settings, created_at, last_updated,
                    participants, associated_sessions, resources, artifacts, metadata, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project.project_id, project.name, project.description,
                json.dumps(project.config), json.dumps(project.settings),
                project.created_at.isoformat(), project.last_updated.isoformat(),
                json.dumps(project.participants), json.dumps(project.associated_sessions),
                json.dumps(project.resources), json.dumps(project.artifacts),
                json.dumps(project.metadata), json.dumps(project.tags)
            ))
            conn.commit()
            return True
    
    def retrieve_project_state(self, project_id: str) -> Optional[ProjectState]:
        """
        Retrieve project state by ID.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project state or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute("SELECT * FROM project_states WHERE project_id = ?", (project_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return ProjectState(
                project_id=row['project_id'],
                name=row['name'],
                description=row['description'],
                config=json.loads(row['config'] or '{}'),
                settings=json.loads(row['settings'] or '{}'),
                created_at=datetime.fromisoformat(row['created_at']),
                last_updated=datetime.fromisoformat(row['last_updated']),
                participants=json.loads(row['participants'] or '[]'),
                associated_sessions=json.loads(row['associated_sessions'] or '[]'),
                resources=json.loads(row['resources'] or '{}'),
                artifacts=json.loads(row['artifacts'] or '[]'),
                metadata=json.loads(row['metadata'] or '{}'),
                tags=json.loads(row['tags'] or '[]')
            )
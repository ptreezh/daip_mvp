"""
Debate history tracking service with proper async patterns.
"""
import asyncio
import json
import sqlite3
import threading
from datetime import datetime
from typing import List, Optional


from daip_live.core.models import (
    DebateTurnCompleteEvent, 
    DebateStartEvent, 
    DebateCompleteEvent
)
from daip_live.tui_v1.models.debate_view import (
    DebateHistoryView, 
    DebateParticipantView, 
    DebateTurnView
)


class DebateHistoryTracker:
    """Service to track and manage debate history for visualization."""
    
    def __init__(self, db_path: str = ":memory:"):
        # Use file-based database for persistence across thread boundaries
        import tempfile
        import os
        
        # Handle case where db_path is None (happens when config is not loaded)
        if db_path is None or db_path == ":memory:":
            # Use a temporary file for persistence across thread calls
            self.db_path = os.path.join(tempfile.gettempdir(), "daip_debate_history.db")
        else:
            self.db_path = db_path
        
        # Use single threading lock for all database operations to avoid async/threading issues
        self._db_lock = threading.Lock()
        self._init_database()

    def _init_database(self):
        """Initialize the database tables for debate history storage."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create debate sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS debate_sessions (
                    session_id TEXT PRIMARY KEY,
                    topic TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    total_rounds INTEGER DEFAULT 1,
                    current_round INTEGER DEFAULT 0,
                    participants TEXT,  -- JSON string of participants
                    summary TEXT,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP
                )
            """)
            
            # Create debate turns table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS debate_turns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    participant_name TEXT NOT NULL,
                    round_number INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    turn_in_round INTEGER NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES debate_sessions (session_id)
                )
            """)
            
            conn.commit()

    async def start_tracking(self, start_event: DebateStartEvent) -> DebateHistoryView:
        """Start tracking a new debate session."""
        loop = asyncio.get_event_loop()
        
        def db_operation():
            with self._db_lock:  # Use threading lock for database operations
                # Create participant views
                participants = []
                for i, name in enumerate(start_event.roles):
                    participants.append(DebateParticipantView(
                        name=name,
                        turn_order=i,
                        color=f"#{(i*0x111111) % 0xFFFFFF:06x}" if i < 16 else "#FFFFFF"  # Generate different colors
                    ))
                
                # Create history view
                history_view = DebateHistoryView(
                    session_id=start_event.session_id,
                    topic=start_event.topic,
                    participants=participants,
                    total_rounds=start_event.rounds,
                    current_round=0
                )
                
                # Store in database
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Convert participants to JSON
                    participants_json = json.dumps([
                        {"name": p.name, "turn_order": p.turn_order, "color": p.color} 
                        for p in participants
                    ])
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO debate_sessions 
                        (session_id, topic, status, total_rounds, current_round, participants, start_time)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        start_event.session_id,
                        start_event.topic,
                        "active",
                        start_event.rounds,
                        0,
                        participants_json,
                        datetime.now().isoformat()
                    ))
                    
                    conn.commit()
                
                return history_view
        
        # Run database operation in thread pool to avoid blocking the event loop
        return await loop.run_in_executor(None, db_operation)

    async def add_turn(self, turn_event: DebateTurnCompleteEvent) -> Optional[DebateHistoryView]:
        """Add a turn to the debate history."""
        loop = asyncio.get_event_loop()
        
        def db_operation():
            with self._db_lock:  # Use threading lock for database operations
                # Add the turn to database
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO debate_turns 
                        (session_id, participant_name, round_number, content, turn_in_round)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        turn_event.session_id,
                        turn_event.participant,
                        turn_event.round_number,
                        turn_event.content_preview,
                        1  # We'll update this properly later
                    ))
                    
                    # Update current round in sessions table
                    cursor.execute("""
                        UPDATE debate_sessions SET current_round = ?
                        WHERE session_id = ?
                    """, (turn_event.round_number, turn_event.session_id))
                    
                    conn.commit()
                
                # Now read back the full history to return updated view
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Get debate session
                    cursor.execute("""
                        SELECT session_id, topic, status, total_rounds, current_round, 
                               participants, summary, start_time, end_time
                        FROM debate_sessions WHERE session_id = ?
                    """, (turn_event.session_id,))
                    
                    row = cursor.fetchone()
                    if not row:
                        return None
                    
                    session_id, topic, status, total_rounds, current_round, participants_json, summary, start_time, end_time = row
                    
                    # Parse participants from JSON
                    try:
                        participants_data = json.loads(participants_json or "[]")
                        participants = [
                            DebateParticipantView(
                                name=p["name"],
                                turn_order=p.get("turn_order", 0),
                                color=p.get("color", "#FFFFFF")
                            ) for p in participants_data
                        ]
                    except json.JSONDecodeError:
                        participants = []
                    
                    # Get all turns for this session
                    cursor.execute("""
                        SELECT participant_name, content, round_number, turn_in_round, timestamp
                        FROM debate_turns 
                        WHERE session_id = ?
                        ORDER BY round_number, turn_in_round
                    """, (turn_event.session_id,))
                    
                    turns_rows = cursor.fetchall()
                    turns = [
                        DebateTurnView(
                            participant_name=row[0],
                            content=row[1],
                            round_number=row[2],
                            turn_in_round=row[3],
                            timestamp=row[4],
                            color=next((p.color for p in participants if p.name == row[0]), "#FFFFFF")
                        ) for row in turns_rows
                    ]
                    
                    # Create history view
                    debate_history_view = DebateHistoryView(
                        session_id=session_id,
                        topic=topic,
                        participants=participants,
                        turns=turns,
                        total_rounds=total_rounds,
                        current_round=current_round,
                        status=status,
                        created_at=datetime.fromisoformat(start_time) if start_time else datetime.now(),
                        end_time=datetime.fromisoformat(end_time) if end_time else None
                    )
                    
                    if summary:
                        debate_history_view.summary = summary
                    
                    return debate_history_view
        
        # Run database operation in thread pool to avoid blocking the event loop
        return await loop.run_in_executor(None, db_operation)

    async def complete_debate(self, complete_event: DebateCompleteEvent) -> Optional[DebateHistoryView]:
        """Mark a debate as completed."""
        loop = asyncio.get_event_loop()
        
        def db_operation():
            with self._db_lock:  # Use threading lock for database operations
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        UPDATE debate_sessions 
                        SET status = ?, summary = ?, end_time = ?
                        WHERE session_id = ?
                    """, (
                        "completed",
                        complete_event.summary,
                        datetime.now().isoformat(),
                        complete_event.session_id
                    ))
                    
                    conn.commit()
            
            # After updating DB, read the updated record
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT session_id, topic, status, total_rounds, current_round, 
                           participants, summary, start_time, end_time
                    FROM debate_sessions WHERE session_id = ?
                """, (complete_event.session_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                session_id, topic, status, total_rounds, current_round, participants_json, summary, start_time, end_time = row
                
                # Parse participants from JSON
                try:
                    participants_data = json.loads(participants_json or "[]")
                    participants = [
                        DebateParticipantView(
                            name=p["name"],
                            turn_order=p.get("turn_order", 0),
                            color=p.get("color", "#FFFFFF")
                        ) for p in participants_data
                    ]
                except json.JSONDecodeError:
                    participants = []
                
                # Get all turns for this session
                cursor.execute("""
                    SELECT participant_name, content, round_number, turn_in_round, timestamp
                    FROM debate_turns 
                    WHERE session_id = ?
                    ORDER BY round_number, turn_in_round
                """, (complete_event.session_id,))
                
                turns_rows = cursor.fetchall()
                turns = [
                    DebateTurnView(
                        participant_name=row[0],
                        content=row[1],
                        round_number=row[2],
                        turn_in_round=row[3],
                        timestamp=row[4],
                        color=next((p.color for p in participants if p.name == row[0]), "#FFFFFF")
                    ) for row in turns_rows
                ]
                
                # Create history view
                debate_history_view = DebateHistoryView(
                    session_id=session_id,
                    topic=topic,
                    participants=participants,
                    turns=turns,
                    total_rounds=total_rounds,
                    current_round=current_round,
                    status=status,
                    created_at=datetime.fromisoformat(start_time) if start_time else datetime.now(),
                    end_time=datetime.fromisoformat(end_time) if end_time else None
                )
                
                if summary:
                    debate_history_view.summary = summary
                
                return debate_history_view
        
        # Run database operation in thread pool to avoid blocking the event loop
        return await loop.run_in_executor(None, db_operation)

    async def get_history(self, session_id: str) -> Optional[DebateHistoryView]:
        """Get the history for a specific debate session."""
        loop = asyncio.get_event_loop()
        
        def db_operation():
            with self._db_lock:  # Use threading lock for database operations
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Get debate session
                    cursor.execute("""
                        SELECT session_id, topic, status, total_rounds, current_round, 
                               participants, summary, start_time, end_time
                        FROM debate_sessions WHERE session_id = ?
                    """, (session_id,))
                    
                    row = cursor.fetchone()
                    if not row:
                        return None
                    
                    session_id_val, topic, status, total_rounds, current_round, participants_json, summary, start_time, end_time = row
                    
                    # Parse participants from JSON
                    try:
                        participants_data = json.loads(participants_json or "[]")
                        participants = [
                            DebateParticipantView(
                                name=p["name"],
                                turn_order=p.get("turn_order", 0),
                                color=p.get("color", "#FFFFFF")
                            ) for p in participants_data
                        ]
                    except json.JSONDecodeError:
                        participants = []
                    
                    # Get all turns for this session
                    cursor.execute("""
                        SELECT participant_name, content, round_number, turn_in_round, timestamp
                        FROM debate_turns 
                        WHERE session_id = ?
                        ORDER BY round_number, turn_in_round
                    """, (session_id,))
                    
                    turns_rows = cursor.fetchall()
                    turns = [
                        DebateTurnView(
                            participant_name=row[0],
                            content=row[1],
                            round_number=row[2],
                            turn_in_round=row[3],
                            timestamp=row[4],
                            color=next((p.color for p in participants if p.name == row[0]), "#FFFFFF")
                        ) for row in turns_rows
                    ]
                    
                    # Create history view
                    debate_history_view = DebateHistoryView(
                        session_id=session_id_val,
                        topic=topic,
                        participants=participants,
                        turns=turns,
                        total_rounds=total_rounds,
                        current_round=current_round,
                        status=status,
                        created_at=datetime.fromisoformat(start_time) if start_time else datetime.now(),
                        end_time=datetime.fromisoformat(end_time) if end_time else None
                    )
                    
                    if summary:
                        debate_history_view.summary = summary
                    
                    return debate_history_view
        
        # Run database operation in thread pool to avoid blocking the event loop
        return await loop.run_in_executor(None, db_operation)

    async def get_all_histories(self) -> List[DebateHistoryView]:
        """Get all tracked debate histories."""
        loop = asyncio.get_event_loop()
        
        def db_operation():
            with self._db_lock:  # Use threading lock for database operations
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Get all debate sessions
                    cursor.execute("""
                        SELECT session_id, topic, status, total_rounds, current_round, 
                               participants, summary, start_time, end_time
                        FROM debate_sessions
                        ORDER BY start_time DESC
                    """)
                    
                    rows = cursor.fetchall()
                    
                    histories = []
                    for row in rows:
                        session_id, topic, status, total_rounds, current_round, participants_json, summary, start_time, end_time = row
                        
                        # Parse participants from JSON
                        try:
                            participants_data = json.loads(participants_json or "[]")
                            participants = [
                                DebateParticipantView(
                                    name=p["name"],
                                    turn_order=p.get("turn_order", 0),
                                    color=p.get("color", "#FFFFFF")
                                ) for p in participants_data
                            ]
                        except json.JSONDecodeError:
                            participants = []
                        
                        # Get all turns for this session
                        cursor.execute("""
                            SELECT participant_name, content, round_number, turn_in_round, timestamp
                            FROM debate_turns 
                            WHERE session_id = ?
                            ORDER BY round_number, turn_in_round
                        """, (session_id,))
                        
                        turns_rows = cursor.fetchall()
                        turns = [
                            DebateTurnView(
                                participant_name=row[0],
                                content=row[1],
                                round_number=row[2],
                                turn_in_round=row[3],
                                timestamp=row[4],
                                color=next((p.color for p in participants if p.name == row[0]), "#FFFFFF")
                            ) for row in turns_rows
                        ]
                        
                        # Create history view
                        debate_history_view = DebateHistoryView(
                            session_id=session_id,
                            topic=topic,
                            participants=participants,
                            turns=turns,
                            total_rounds=total_rounds,
                            current_round=current_round,
                            status=status,
                            created_at=datetime.fromisoformat(start_time) if start_time else datetime.now(),
                            end_time=datetime.fromisoformat(end_time) if end_time else None
                        )
                        
                        if summary:
                            debate_history_view.summary = summary
                        
                        histories.append(debate_history_view)
                    
                    return histories
        
        # Run database operation in thread pool to avoid blocking the event loop
        return await loop.run_in_executor(None, db_operation)

    async def clear_history(self, session_id: str) -> bool:
        """Clear history for a specific debate session."""
        loop = asyncio.get_event_loop()
        
        def db_operation():
            with self._db_lock:  # Use threading lock for database operations
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Delete turns first (due to foreign key constraint)
                    cursor.execute("DELETE FROM debate_turns WHERE session_id = ?", (session_id,))
                    
                    # Delete session
                    cursor.execute("DELETE FROM debate_sessions WHERE session_id = ?", (session_id,))
                    
                    conn.commit()
                    
                    # Return True if any rows were affected
                    return cursor.rowcount > 0
        
        # Run database operation in thread pool to avoid blocking the event loop
        return await loop.run_in_executor(None, db_operation)
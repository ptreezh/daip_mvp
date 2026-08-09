"""Enhanced debate view models for TUI visualization."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DebateParticipantView(BaseModel):
    """Represents a debate participant with visual styling information."""

    name: str
    color: str = Field(default="#87CEEB")  # Light blue as default
    symbol: str = Field(default="👤")
    turn_order: int = Field(default=0)


class DebateTurnView(BaseModel):
    """Represents a single turn in the debate with styling."""

    participant_name: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    round_number: int
    turn_in_round: int
    color: str = Field(default="#FFFFFF")  # Default white text


class DebateHistoryView(BaseModel):
    """Represents the complete history of a debate session."""

    session_id: str
    topic: str
    participants: list[DebateParticipantView]
    turns: list[DebateTurnView] = Field(default_factory=list)
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_rounds: int = Field(default=0)
    current_round: int = Field(default=0)
    status: str = Field(default="active")  # active, completed, paused
    summary: Optional[str] = None  # Summary of the debate


class EnhancedDebateView(BaseModel):
    """Enhanced visual representation of a debate in progress."""

    session_id: str
    topic: str
    participants: list[DebateParticipantView]
    current_turn: Optional[str] = None
    current_round: int = Field(default=1)
    total_rounds: int = Field(default=3)
    history: list[DebateTurnView] = Field(default_factory=list)
    start_time: datetime = Field(default_factory=datetime.now)
    status: str = Field(default="active")  # active, completed, paused
    color_scheme: dict = Field(default_factory=dict)
    summary: Optional[str] = None  # Summary of the debate

    def __init__(self, **data):
        super().__init__(**data)
        # Set default color scheme if not provided
        if not self.color_scheme:
            self.color_scheme = {
                "background": "#1E1E1E",
                "text": "#FFFFFF",
                "highlight": "#FFD700",
                "participant_colors": self._get_default_participant_colors(),
            }

    def _get_default_participant_colors(self) -> dict:
        """Generate default colors for participants."""
        colors = [
            "#87CEEB",  # Light blue
            "#98FB98",  # Pale green
            "#FFB6C1",  # Light pink
            "#DDA0DD",  # Plum
            "#F0E68C",  # Khaki
            "#FFA07A",  # Light salmon
        ]
        return {
            p.name: colors[i % len(colors)] for i, p in enumerate(self.participants)
        }

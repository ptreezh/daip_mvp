"""API documentation enhancements for DAIP-LIVE.

This module provides OpenAPI/Swagger documentation specifications,
request/response schemas, and examples for all API endpoints.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# ============================================================================
# Request/Response Schemas with Documentation
# ============================================================================

class SessionCreateRequest(BaseModel):
    """Request schema for creating a new session.

    Attributes:
        goal: The primary objective or task for this session
        session_type: Type of session (chat, workflow, debate). Defaults to 'workflow'
        participant_ids: List of participant identifiers. Defaults to ['agent', 'user']
    """

    goal: str = Field(
        ...,
        description="The primary objective or task for this session",
        examples=["Analyze market trends for AI adoption", "Debate the pros and cons of remote work"]
    )
    session_type: str = Field(
        default="workflow",
        description="Type of session: chat, workflow, or debate"
    )
    participant_ids: List[str] = Field(
        default=["agent", "user"],
        description="List of participant identifiers"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "goal": "Analyze market trends for AI adoption in 2024",
                    "session_type": "workflow",
                    "participant_ids": ["agent", "user"]
                }
            ]
        }
    }


class SessionResponse(BaseModel):
    """Response schema for session data."""

    session_id: str = Field(..., description="Unique session identifier")
    session_type: str = Field(..., description="Type of session")
    goal: str = Field(..., description="Session objective or goal")
    participant_ids: List[str] = Field(..., description="Participant identifiers")
    created_at: datetime = Field(..., description="Session creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    status: Optional[str] = Field(None, description="Current session status")


class HealthCheckResponse(BaseModel):
    """Response schema for health check endpoint."""

    status: str = Field(
        ...,
        description="System health status: healthy, degraded, or unhealthy"
    )
    timestamp: datetime = Field(..., description="Health check timestamp")
    version: str = Field(..., description="Application version")
    uptime_seconds: Optional[float] = Field(None, description="Server uptime in seconds")
    components: Optional[Dict[str, str]] = Field(
        None,
        description="Health status of individual components"
    )


class RoleInfoResponse(BaseModel):
    """Response schema for role information."""

    name: str = Field(..., description="Role name")
    description: str = Field(..., description="Role description")
    system_prompt: str = Field(..., description="System prompt for this role")
    model: Optional[str] = Field(None, description="Assigned model for this role")
    capabilities: Optional[List[str]] = Field(
        None,
        description="List of capabilities for this role"
    )


class KnowledgeStatusResponse(BaseModel):
    """Response schema for knowledge base status."""

    status: str = Field(..., description="Knowledge base status")
    last_sync: datetime = Field(..., description="Last synchronization timestamp")
    total_documents: int = Field(..., description="Total number of documents")
    index_size: Optional[int] = Field(None, description="Size of the vector index")
    embedding_dimension: Optional[int] = Field(None, description="Embedding vector dimension")


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    error: str = Field(..., description="Error type or code")
    message: str = Field(..., description="Human-readable error message")
    detail: Optional[str] = Field(None, description="Additional error details")
    timestamp: datetime = Field(..., description="Error timestamp")


# ============================================================================
# API Tags and Metadata
# ============================================================================

API_TAGS = [
    {
        "name": "sessions",
        "description": "Session management operations. Create, list, retrieve, and delete user sessions."
    },
    {
        "name": "health",
        "description": "System health and status monitoring endpoints."
    },
    {
        "name": "roles",
        "description": "Role management operations. List available agent roles and their configurations."
    },
    {
        "name": "knowledge",
        "description": "Knowledge base operations. Check status and manage documents."
    },
    {
        "name": "websocket",
        "description": "WebSocket endpoints for real-time agent communication."
    }
]


# ============================================================================
# OpenAPI Specification
# ============================================================================

OPENAPI_SPEC = {
    "openapi": "3.1.0",
    "info": {
        "title": "DAIP-LIVE API",
        "version": "1.0.0",
        "description": """
## DAIP-LIVE (Dynamic AI-driven Project-execution LIVE System)

A sophisticated AI-powered project execution system combining:
- Multi-agent debate system
- Knowledge management with vector search
- Natural language intent recognition
- Real-time WebSocket communication

### Authentication

Currently, DAIP-LIVE runs as a local application without external authentication.
For production deployments, implement API key or OAuth authentication.

### Rate Limiting

No rate limiting is currently enforced for local deployments.
        """,
        "contact": {
            "name": "DAIP-LIVE Team",
        },
        "license": {
            "name": "MIT"
        }
    },
    "servers": [
        {
            "url": "http://localhost:8000",
            "description": "Local development server"
        },
        {
            "url": "http://localhost:8080",
            "description": "Alternative local port"
        }
    ],
    "tags": API_TAGS,
    "paths": {
        # Sessions
        "/api/sessions": {
            "post": {
                "tags": ["sessions"],
                "summary": "Create a new session",
                "description": "Creates a new session with the specified goal and configuration.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/SessionCreateRequest"}
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Session created successfully",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/SessionResponse"}
                            }
                        }
                    },
                    "400": {
                        "description": "Invalid request parameters",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        }
                    }
                }
            },
            "get": {
                "tags": ["sessions"],
                "summary": "List all sessions",
                "description": "Retrieves a list of all existing sessions.",
                "responses": {
                    "200": {
                        "description": "List of sessions",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/SessionResponse"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/sessions/{session_id}": {
            "get": {
                "tags": ["sessions"],
                "summary": "Get a specific session",
                "description": "Retrieves details of a specific session by ID.",
                "parameters": [
                    {
                        "name": "session_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Session identifier"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Session details",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/SessionResponse"}
                            }
                        }
                    },
                    "404": {
                        "description": "Session not found",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        }
                    }
                }
            },
            "delete": {
                "tags": ["sessions"],
                "summary": "Delete a session",
                "description": "Deletes a specific session by ID.",
                "parameters": [
                    {
                        "name": "session_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Session identifier"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Session deleted successfully"
                    },
                    "404": {
                        "description": "Session not found",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        }
                    }
                }
            }
        },
        # Health
        "/api/health": {
            "get": {
                "tags": ["health"],
                "summary": "Health check",
                "description": "Returns the current health status of the system.",
                "responses": {
                    "200": {
                        "description": "System health status",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/HealthCheckResponse"}
                            }
                        }
                    }
                }
            }
        },
        # Roles
        "/api/roles": {
            "get": {
                "tags": ["roles"],
                "summary": "List available roles",
                "description": "Retrieves a list of all available agent roles with their configurations.",
                "responses": {
                    "200": {
                        "description": "List of roles",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/RoleInfoResponse"}
                                }
                            }
                        }
                    }
                }
            }
        },
        # Knowledge
        "/api/knowledge/status": {
            "get": {
                "tags": ["knowledge"],
                "summary": "Get knowledge base status",
                "description": "Retrieves the current status and statistics of the knowledge base.",
                "responses": {
                    "200": {
                        "description": "Knowledge base status",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/KnowledgeStatusResponse"}
                            }
                        }
                    }
                }
            }
        },
        # WebSocket
        "/ws/sessions/{session_id}": {
            "get": {
                "tags": ["websocket"],
                "summary": "WebSocket endpoint for session",
                "description": """
Establishes a WebSocket connection for real-time agent communication.

### Connection Flow
1. Connect to the WebSocket with a valid session_id
2. Receive real-time events from the agent executor
3. Send user input via JSON messages

### Event Types
- `step_complete`: Agent completed an execution step
- `error`: An error occurred during execution
- `user_input_required`: Agent needs additional user input
                """,
                "parameters": [
                    {
                        "name": "session_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Session identifier"
                    }
                ]
            }
        }
    },
    "components": {
        "schemas": {
            "SessionCreateRequest": {
                "type": "object",
                "properties": {
                    "goal": {"type": "string"},
                    "session_type": {"type": "string", "default": "workflow"},
                    "participant_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["agent", "user"]
                    }
                },
                "required": ["goal"]
            },
            "SessionResponse": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "session_type": {"type": "string"},
                    "goal": {"type": "string"},
                    "participant_ids": {"type": "array", "items": {"type": "string"}},
                    "created_at": {"type": "string", "format": "date-time"},
                    "updated_at": {"type": "string", "format": "date-time"},
                    "status": {"type": "string"}
                }
            },
            "HealthCheckResponse": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "timestamp": {"type": "string", "format": "date-time"},
                    "version": {"type": "string"},
                    "uptime_seconds": {"type": "number"},
                    "components": {
                        "type": "object",
                        "additionalProperties": {"type": "string"}
                    }
                }
            },
            "RoleInfoResponse": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "system_prompt": {"type": "string"},
                    "model": {"type": "string"},
                    "capabilities": {"type": "array", "items": {"type": "string"}}
                }
            },
            "KnowledgeStatusResponse": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "last_sync": {"type": "string", "format": "date-time"},
                    "total_documents": {"type": "integer"},
                    "index_size": {"type": "integer"},
                    "embedding_dimension": {"type": "integer"}
                }
            },
            "ErrorResponse": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                    "message": {"type": "string"},
                    "detail": {"type": "string"},
                    "timestamp": {"type": "string", "format": "date-time"}
                },
                "required": ["error", "message", "timestamp"]
            }
        }
    }
}


# ============================================================================
# Utility Functions
# ============================================================================

def get_openapi_spec() -> Dict[str, Any]:
    """Returns the complete OpenAPI specification."""
    return OPENAPI_SPEC


def register_api_docs(app):
    """Registers API documentation enhancements to a FastAPI app.

    Args:
        app: FastAPI application instance
    """
    # Set OpenAPI metadata
    app.openapi = lambda: OPENAPI_SPEC

    # Add tags
    app.tags = API_TAGS

    return app

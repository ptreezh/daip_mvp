import logging
from typing import Optional

from fastapi import APIRouter

from src.api.dependencies import AppStateDep

router = APIRouter(
    prefix="/schemas",
    tags=["Schema Management"],
)

logger = logging.getLogger(__name__)


@router.get("/")
async def list_schemas(
    state: AppStateDep,
    domain: Optional[str] = None,
    search: Optional[str] = None,
):
    """List all available schemas, with optional filtering."""
    # This is a mock implementation based on the AppState placeholder
    schemas = state.schema_library.schemas
    if domain:
        schemas = [s for s in schemas if s.get("domain") == domain]
    if search:
        search_lower = search.lower()
        schemas = [s for s in schemas if search_lower in s.get("name", "").lower()]

    return {"schemas": schemas, "total": len(schemas)}


@router.get("/domains")
async def get_schema_domains(state: AppStateDep):
    """Get all available schema domains."""
    return {"domains": state.schema_library.schema_categories}

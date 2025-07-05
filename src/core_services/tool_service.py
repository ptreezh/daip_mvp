import logging
from typing import Any, Dict, List

from src.app_state import AppState
from src.models import MemoryEntryRequest

logger = logging.getLogger(__name__)


class FileToolsService:
    """A simple wrapper for file system tools for dependency injection."""

    def read_file(self, path: str
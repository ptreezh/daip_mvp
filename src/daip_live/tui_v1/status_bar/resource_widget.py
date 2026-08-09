"""
System Resource Widget for newP6 TUI Status Bar

Displays system resource usage (CPU, Memory, etc.).
"""

import logging
from typing import Optional

try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

from .status_widget import StatusWidget

logger = logging.getLogger(__name__)


class SystemResourceWidget(StatusWidget):
    """Widget for displaying system resource usage"""

    def __init__(self):
        super().__init__("system_resources", "Resources")

    async def refresh(self) -> None:
        """Refresh system resource information"""
        try:
            if PSUTIL_AVAILABLE:
                # Get CPU usage
                cpu_percent = psutil.cpu_percent(interval=0.1)

                # Get memory usage
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                memory_used_gb = memory.used / (1024**3)
                memory_total_gb = memory.total / (1024**3)

                # Format resource information
                resource_text = f"CPU {cpu_percent:.1f}% | Mem {memory_percent:.1f}% ({memory_used_gb:.1f}GB/{memory_total_gb:.1f}GB)"  # noqa: E501
                self.update_value(resource_text)
            else:
                # Fallback when psutil is not available
                self.update_value("CPU N/A | Mem N/A (psutil not installed)")
        except Exception as e:
            logger.error(f"Error refreshing system resources: {e}")
            self.update_value("Resources Error")

    def get_cpu_usage(self) -> Optional[float]:
        """Get current CPU usage percentage"""
        try:
            if PSUTIL_AVAILABLE:
                return psutil.cpu_percent(interval=0.1)
        except Exception as e:
            logger.error(f"Error getting CPU usage: {e}")
        return None

    def get_memory_usage(self) -> Optional[dict]:
        """Get current memory usage information"""
        try:
            if PSUTIL_AVAILABLE:
                memory = psutil.virtual_memory()
                return {
                    "percent": memory.percent,
                    "used_gb": memory.used / (1024**3),
                    "total_gb": memory.total / (1024**3),
                    "available_gb": memory.available / (1024**3),
                }
        except Exception as e:
            logger.error(f"Error getting memory usage: {e}")
        return None

    def is_psutil_available(self) -> bool:
        """Check if psutil is available"""
        return PSUTIL_AVAILABLE

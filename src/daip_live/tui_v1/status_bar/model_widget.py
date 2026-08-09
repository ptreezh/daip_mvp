"""
Model Status Widget for newP6 TUI Status Bar

Displays current AI model status and information.
"""

import logging
from typing import Any, Optional

from .status_widget import StatusWidget

logger = logging.getLogger(__name__)


class ModelStatusWidget(StatusWidget):
    """Widget for displaying AI model status"""

    def __init__(self, model_service: Optional[Any] = None):
        super().__init__("model_status", "Model")
        self.model_service = model_service

    async def refresh(self) -> None:
        """Refresh model status"""
        try:
            if self.model_service and hasattr(self.model_service, "get_current_model"):
                model_info = await self.model_service.get_current_model()
                if model_info:
                    status_text = f"{model_info.get('name', 'Unknown')} ({model_info.get('status', 'Unknown')})"  # noqa: E501
                    self.update_value(status_text)
                else:
                    self.update_value("No Active Model")
            else:
                # Fallback status when service is not available
                self.update_value("No Model Service")
        except Exception as e:
            logger.error(f"Error refreshing model status: {e}")
            self.update_value("Model Error")

    def set_model_service(self, model_service: Any) -> None:
        """Set the model service"""
        self.model_service = model_service

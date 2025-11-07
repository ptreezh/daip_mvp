"""
Status Bar Component

This module provides the StatusBarComponent class as specified in the newP6
architecture requirements. The status bar component handles status display,
progress indicators, and system information functionality.

Based on newP6 specification requirements for status management.
"""

from typing import Any, Dict, Optional, List
from textual.widgets import Static, ProgressBar, Label
from textual.containers import Horizontal, Vertical
from datetime import datetime

from .base import TUIComponent


class StatusBarComponent(TUIComponent):
    """
    Status bar component for newP6 TUI architecture.

    This class provides status display and system information functionality as
    specified in the newP6 architecture requirements.

    Features:
    - Status text display
    - Progress indicators
    - System information display
    - Time display
    - Performance metrics
    - Component status monitoring
    """

    def __init__(
        self,
        component_id: Optional[str] = None,
        show_progress: bool = False,
        show_time: bool = True,
        show_system_info: bool = True,
        refresh_interval: int = 1
    ):
        """
        Initialize the status bar component.

        Args:
            component_id: Optional unique identifier (should be "status_bar" for compatibility)
            show_progress: Whether to show progress bar
            show_time: Whether to show current time
            show_system_info: Whether to show system information
            refresh_interval: Refresh interval in seconds
        """
        super().__init__(component_id)

        # Status bar configuration
        self.update_state(
            show_progress=show_progress,
            show_time=show_time,
            show_system_info=show_system_info,
            refresh_interval=refresh_interval,
            status_text="Ready",
            progress_value=0.0,
            progress_total=100.0,
            system_info={},
            current_time=None,
            performance_metrics={},
            component_statuses={},
            alerts=[],
            last_update=None
        )

    def render(self):
        """
        Render the status bar component as a widget.

        Returns:
            Widget: The rendered status bar widget
        """
        container = Horizontal()
        container.styles.height = 3  # Fixed height for status bar
        container.id = self.component_id

        # Create child widgets list
        children = []

        # Status text
        status_text = self.state.get('status_text', 'Ready')
        status_label = Label(f"Status: {status_text}")
        children.append(status_label)

        # Current time (if enabled)
        if self.state.get('show_time', True):
            current_time = self.state.get('current_time')
            if current_time:
                time_label = Label(f"Time: {current_time}")
                children.append(time_label)

        # Alerts
        alerts = self.state.get('alerts', [])
        if alerts:
            alert_count = len(alerts)
            alert_label = Label(f"Alerts: {alert_count}")
            children.append(alert_label)

        # System info (if enabled)
        if self.state.get('show_system_info', True):
            system_info = self.state.get('system_info', {})
            if system_info:
                info_parts = []
                if system_info.get('cpu_percent'):
                    info_parts.append(f"CPU: {system_info['cpu_percent']:.1f}%")
                if system_info.get('memory_percent'):
                    info_parts.append(f"Mem: {system_info['memory_percent']:.1f}%")
                if info_parts:
                    info_label = Label(" | ".join(info_parts))
                    children.append(info_label)

        # Set children for container
        container._compose_children = lambda: children

        return container

    async def mount(self) -> None:
        """Mount the status bar component."""
        self._set_mounted(True)

        # Initialize time display
        self.update_state(current_time=self._get_current_time())

        # Start refresh loop
        if self.state.get('refresh_interval', 1) > 0:
            self._start_refresh_loop()

    def update_state(self, **kwargs) -> None:
        """
        Update the component's internal state.

        Args:
            **kwargs: Key-value pairs of state updates
        """
        super().update_state(**kwargs)

    def handle_event(self, event: Any) -> None:
        """
        Handle an event passed to this component.

        Args:
            event: The event to handle
        """
        # Handle status-specific events
        if hasattr(event, 'event_type'):
            if event.event_type.value == 'status_update':
                self.set_status(event.data.get('text', ''))
            elif event.event_type.value == 'progress_update':
                self.update_progress(
                    event.data.get('value', 0),
                    event.data.get('total', 100)
                )
            elif event.event_type.value == 'system_info_update':
                self.update_system_info(event.data)
            elif event.event_type.value == 'alert':
                self.add_alert(
                    event.data.get('message', ''),
                    event.data.get('level', 'info')
                )

    def set_status(self, status_text: str) -> None:
        """
        Set the status text.

        Args:
            status_text: The status text to display
        """
        self.update_state(
            status_text=status_text,
            last_update=self._get_current_timestamp()
        )

    def update_progress(self, value: float, total: Optional[float] = None) -> None:
        """
        Update the progress indicator.

        Args:
            value: Current progress value
            total: Total progress value (uses current total if None)
        """
        updates = {'progress_value': value}
        if total:
            updates['progress_total'] = total

        self.update_state(**updates)

    def set_progress_complete(self) -> None:
        """Set progress to complete."""
        total = self.state.get('progress_total', 100)
        self.update_progress(total, total)
        self.set_status("Complete")

    def reset_progress(self) -> None:
        """Reset progress to zero."""
        self.update_progress(0.0)

    def update_system_info(self, system_info: Dict[str, Any]) -> None:
        """
        Update system information.

        Args:
            system_info: Dictionary with system metrics
        """
        current_info = self.state.get('system_info', {})
        current_info.update(system_info)
        self.update_state(system_info=current_info)

    def update_performance_metrics(self, metrics: Dict[str, Any]) -> None:
        """
        Update performance metrics.

        Args:
            metrics: Dictionary with performance metrics
        """
        current_metrics = self.state.get('performance_metrics', {})
        current_metrics.update(metrics)
        self.update_state(performance_metrics=current_metrics)

    def add_alert(self, message: str, level: str = 'info') -> None:
        """
        Add an alert to the status bar.

        Args:
            message: Alert message
            level: Alert level ('info', 'warning', 'error', 'success')
        """
        alerts = self.state.get('alerts', [])
        alert = {
            'message': message,
            'level': level,
            'timestamp': self._get_current_timestamp()
        }
        alerts.append(alert)

        # Keep only recent alerts (last 10)
        if len(alerts) > 10:
            alerts = alerts[-10:]

        self.update_state(alerts=alerts)

        # Update status text for important alerts
        if level in ['error', 'warning']:
            self.set_status(f"{level.upper()}: {message}")

    def clear_alerts(self) -> None:
        """Clear all alerts."""
        self.update_state(alerts=[])

    def set_component_status(self, component_id: str, status: str) -> None:
        """
        Set the status of a specific component.

        Args:
            component_id: ID of the component
            status: Status of the component
        """
        component_statuses = self.state.get('component_statuses', {})
        component_statuses[component_id] = {
            'status': status,
            'timestamp': self._get_current_timestamp()
        }
        self.update_state(component_statuses=component_statuses)

    def show_progress_bar(self, show: bool) -> None:
        """
        Show or hide the progress bar.

        Args:
            show: Whether to show the progress bar
        """
        self.update_state(show_progress=show)

    def show_time(self, show: bool) -> None:
        """
        Show or hide the time display.

        Args:
            show: Whether to show the time
        """
        self.update_state(show_time=show)

    def show_system_info(self, show: bool) -> None:
        """
        Show or hide system information.

        Args:
            show: Whether to show system information
        """
        self.update_state(show_system_info=show)

    def set_refresh_interval(self, interval: int) -> None:
        """
        Set the refresh interval.

        Args:
            interval: Refresh interval in seconds
        """
        self.update_state(refresh_interval=interval)

    def get_status_text(self) -> str:
        """
        Get the current status text.

        Returns:
            str: Current status text
        """
        return self.state.get('status_text', '')

    def get_progress_value(self) -> float:
        """
        Get the current progress value.

        Returns:
            float: Current progress value
        """
        return self.state.get('progress_value', 0.0)

    def get_progress_percentage(self) -> float:
        """
        Get the progress as a percentage.

        Returns:
            float: Progress percentage (0-100)
        """
        value = self.state.get('progress_value', 0.0)
        total = self.state.get('progress_total', 100.0)
        return (value / total * 100) if total > 0 else 0.0

    def get_alerts(self) -> List[Dict[str, Any]]:
        """
        Get current alerts.

        Returns:
            List[Dict[str, Any]]: List of alerts
        """
        return self.state.get('alerts', [])

    def get_system_info(self) -> Dict[str, Any]:
        """
        Get current system information.

        Returns:
            Dict[str, Any]: System information
        """
        return self.state.get('system_info', {})

    def get_component_statuses(self) -> Dict[str, Any]:
        """
        Get component statuses.

        Returns:
            Dict[str, Any]: Component statuses
        """
        return self.state.get('component_statuses', {})

    def _start_refresh_loop(self) -> None:
        """Start the background refresh loop."""
        # This would be implemented with asyncio.create_task
        # For now, we'll just update time once
        self.update_state(current_time=self._get_current_time())

    def _get_current_time(self) -> str:
        """
        Get current time as formatted string.

        Returns:
            str: Current time
        """
        return datetime.now().strftime("%H:%M:%S")

    def _get_current_timestamp(self) -> str:
        """
        Get current timestamp as string.

        Returns:
            str: Current timestamp
        """
        return datetime.now().isoformat()

    def update_time(self) -> None:
        """Update the current time display."""
        self.update_state(current_time=self._get_current_time())

    def set_error_status(self, error_message: str) -> None:
        """
        Set an error status with alert.

        Args:
            error_message: Error message to display
        """
        self.add_alert(error_message, 'error')
        self.set_status(f"Error: {error_message}")

    def set_warning_status(self, warning_message: str) -> None:
        """
        Set a warning status with alert.

        Args:
            warning_message: Warning message to display
        """
        self.add_alert(warning_message, 'warning')
        self.set_status(f"Warning: {warning_message}")

    def set_success_status(self, success_message: str) -> None:
        """
        Set a success status with alert.

        Args:
            success_message: Success message to display
        """
        self.add_alert(success_message, 'success')
        self.set_status(success_message)

    def indicate_activity(self, activity_text: str) -> None:
        """
        Indicate that an activity is in progress.

        Args:
            activity_text: Description of the activity
        """
        self.set_status(f"Working: {activity_text}")

    def indicate_idle(self) -> None:
        """Indicate that the system is idle."""
        self.set_status("Ready")
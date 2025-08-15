"""@Time    : 2025-07-24 20:30:00
@Author  : DAIP-LIVE Team
@File    : transparency_controller.py
@Description:
    Transparency controller that manages result presentation and user feedback.
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

from .feedback_collector import FeedbackCollector, WorkflowFeedback
from .progress_monitor import ProgressMonitor
from .result_formatter import ResultFormatter

logger = logging.getLogger(__name__)


class TransparencyController:
    """Controller for managing result presentation and transparency features.
    
    This class implements the requirements for task 9.3:
    - Multiple output format handlers
    - Traceability and reasoning exposure
    - User feedback and validation mechanisms
    """
    
    def __init__(self):
        """Initialize the transparency controller."""
        self.console = Console()
        self.result_formatter = ResultFormatter()
        self.feedback_collector = FeedbackCollector()
        self.progress_monitor = ProgressMonitor()
        
        # Configuration
        self.default_transparency_level = "moderate"
        self.default_output_format = "json"
        self.auto_collect_feedback = True
        self.save_results_to_file = False
        self.results_directory = Path("results")
    
    def present_workflow_result(
        self,
        result: dict[str, Any],
        execution_id: str,
        workflow_type: str,
        output_format: str = None,
        transparency_level: str = None,
        save_to_file: bool = None,
        collect_feedback: bool = None,
        user_id: Optional[str] = None
    ) -> Optional[WorkflowFeedback]:
        """Present workflow result with configurable transparency and collect feedback.
        
        Args:
            result: The workflow result to present
            execution_id: Unique execution identifier
            workflow_type: Type of workflow (e.g., "critical-review", "multi-perspective")
            output_format: Output format ("json", "markdown", "html", etc.)
            transparency_level: Transparency level ("minimal", "moderate", "detailed")
            save_to_file: Whether to save result to file
            collect_feedback: Whether to collect user feedback
            user_id: Optional user identifier
            
        Returns:
            WorkflowFeedback if feedback was collected, None otherwise
        """
        # Use defaults if not specified
        output_format = output_format or self.default_output_format
        transparency_level = transparency_level or self.default_transparency_level
        save_to_file = save_to_file if save_to_file is not None else self.save_results_to_file
        collect_feedback = collect_feedback if collect_feedback is not None else self.auto_collect_feedback
        
        try:
            # Display result with appropriate transparency
            self._display_result_with_transparency(result, transparency_level)
            
            # Format and optionally save result
            formatted_result = self._format_and_save_result(
                result, execution_id, output_format, save_to_file
            )
            
            # Collect feedback if requested
            feedback = None
            if collect_feedback:
                feedback = self._collect_user_feedback(
                    result, execution_id, workflow_type, user_id
                )
            
            return feedback
            
        except Exception as e:
            logger.error(f"Error presenting workflow result: {e}")
            self.console.print(f"[red]Error presenting result: {e}[/red]")
            return None
    
    def present_with_traceability(
        self,
        result: dict[str, Any],
        execution_id: str,
        include_reasoning: bool = True,
        include_confidence: bool = True,
        include_sources: bool = True,
        output_format: str = "json"
    ) -> str:
        """Present result with enhanced traceability information.
        
        Args:
            result: The workflow result
            execution_id: Unique execution identifier
            include_reasoning: Include reasoning trace
            include_confidence: Include confidence analysis
            include_sources: Include source attribution
            output_format: Output format for the traceable result
            
        Returns:
            Formatted result with traceability information
        """
        try:
            # Format with traceability
            traceable_result = self.result_formatter.format_with_traceability(
                result,
                format_type=output_format,
                include_reasoning=include_reasoning,
                include_confidence=include_confidence,
                include_sources=include_sources
            )
            
            # Display traceability information
            self.console.print(Panel(
                "[green]Enhanced Traceability Report Generated[/green]",
                title="Traceability",
                border_style="green"
            ))
            
            if include_reasoning:
                self.console.print("✅ Reasoning trace included")
            if include_confidence:
                self.console.print("✅ Confidence analysis included")
            if include_sources:
                self.console.print("✅ Source attribution included")
            
            return traceable_result
            
        except Exception as e:
            logger.error(f"Error generating traceability report: {e}")
            self.console.print(f"[red]Error generating traceability report: {e}[/red]")
            return self.result_formatter.format_as_json(result)
    
    def validate_result_quality(
        self,
        result: dict[str, Any],
        validation_criteria: dict[str, Any] = None,
        user_id: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Validate result quality and return validation results.
        
        Args:
            result: The workflow result to validate
            validation_criteria: Criteria for validation
            user_id: Optional user identifier
            
        Returns:
            List of validation results
        """
        try:
            validation_results = self.feedback_collector.validate_result_elements(
                result, validation_criteria, user_id
            )
            
            # Display validation summary
            self._display_validation_summary(validation_results)
            
            return [v.model_dump() for v in validation_results]
            
        except Exception as e:
            logger.error(f"Error validating result quality: {e}")
            self.console.print(f"[red]Error validating result: {e}[/red]")
            return []
    
    def export_result(
        self,
        result: dict[str, Any],
        execution_id: str,
        format_type: str,
        include_traceability: bool = False,
        output_path: Optional[str] = None
    ) -> str:
        """Export result in specified format.
        
        Args:
            result: The workflow result to export
            execution_id: Unique execution identifier
            format_type: Export format
            include_traceability: Include traceability information
            output_path: Optional output file path
            
        Returns:
            Formatted result string or file path if saved
        """
        try:
            # Format result
            if include_traceability:
                formatted_result = self.result_formatter.format_with_traceability(
                    result, format_type
                )
            else:
                formatted_result = self.result_formatter.format_result(result, format_type)
            
            # Save to file if path provided
            if output_path:
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text(formatted_result, encoding='utf-8')
                
                self.console.print(f"[green]Result exported to: {output_file}[/green]")
                return str(output_file)
            
            return formatted_result
            
        except Exception as e:
            logger.error(f"Error exporting result: {e}")
            self.console.print(f"[red]Error exporting result: {e}[/red]")
            return ""
    
    def get_feedback_summary(self, execution_id: str) -> Optional[dict[str, Any]]:
        """Get feedback summary for a specific execution."""
        try:
            if execution_id in self.feedback_collector.feedback_storage:
                feedback = self.feedback_collector.feedback_storage[execution_id]
                return {
                    "execution_id": execution_id,
                    "workflow_type": feedback.workflow_type,
                    "overall_rating": feedback.overall_rating,
                    "overall_satisfaction": feedback.overall_satisfaction,
                    "feedback_items_count": len(feedback.feedback_items),
                    "improvement_suggestions_count": len(feedback.improvement_suggestions),
                    "timestamp": feedback.timestamp.isoformat()
                }
            return None
        except Exception as e:
            logger.error(f"Error getting feedback summary: {e}")
            return None
    
    def configure_transparency(
        self,
        transparency_level: str = "moderate",
        output_format: str = "json",
        auto_collect_feedback: bool = True,
        save_results: bool = False,
        results_directory: str = "results"
    ) -> None:
        """Configure transparency settings."""
        self.default_transparency_level = transparency_level
        self.default_output_format = output_format
        self.auto_collect_feedback = auto_collect_feedback
        self.save_results_to_file = save_results
        self.results_directory = Path(results_directory)
        
        self.console.print(Panel(
            f"[green]Transparency Configuration Updated[/green]\n\n"
            f"Transparency Level: {transparency_level}\n"
            f"Output Format: {output_format}\n"
            f"Auto Collect Feedback: {auto_collect_feedback}\n"
            f"Save Results: {save_results}\n"
            f"Results Directory: {results_directory}",
            title="Configuration",
            border_style="blue"
        ))
    
    def get_supported_formats(self) -> list[str]:
        """Get list of supported output formats."""
        return self.result_formatter.get_supported_formats()
    
    def get_transparency_levels(self) -> list[str]:
        """Get list of supported transparency levels."""
        return ["minimal", "moderate", "detailed"]
    
    def _display_result_with_transparency(
        self,
        result: dict[str, Any],
        transparency_level: str
    ) -> None:
        """Display result with specified transparency level."""
        self.result_formatter.display_with_transparency(
            result, self.console, transparency_level
        )
    
    def _format_and_save_result(
        self,
        result: dict[str, Any],
        execution_id: str,
        output_format: str,
        save_to_file: bool
    ) -> str:
        """Format result and optionally save to file."""
        formatted_result = self.result_formatter.format_result(result, output_format)
        
        if save_to_file:
            # Create results directory if it doesn't exist
            self.results_directory.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"result_{execution_id}_{timestamp}.{output_format}"
            filepath = self.results_directory / filename
            
            # Save file
            filepath.write_text(formatted_result, encoding='utf-8')
            
            self.console.print(f"[green]Result saved to: {filepath}[/green]")
        
        return formatted_result
    
    def _collect_user_feedback(
        self,
        result: dict[str, Any],
        execution_id: str,
        workflow_type: str,
        user_id: Optional[str]
    ) -> Optional[WorkflowFeedback]:
        """Collect user feedback on the result."""
        try:
            # Ask if user wants to provide feedback
            if not Confirm.ask("\nWould you like to provide feedback on this result?"):
                return None
            
            # Collect feedback
            feedback = self.feedback_collector.collect_workflow_feedback(
                result, execution_id, workflow_type, interactive=True, user_id=user_id
            )
            
            # Display feedback summary
            self.feedback_collector.display_feedback_summary(feedback)
            
            return feedback
            
        except Exception as e:
            logger.error(f"Error collecting user feedback: {e}")
            self.console.print(f"[red]Error collecting feedback: {e}[/red]")
            return None
    
    def _display_validation_summary(self, validation_results: list[Any]) -> None:
        """Display validation results summary."""
        if not validation_results:
            self.console.print("[yellow]No validation results to display[/yellow]")
            return
        
        self.console.print(Panel(
            "[blue]Validation Results Summary[/blue]",
            title="Validation",
            border_style="blue"
        ))
        
        valid_count = sum(1 for v in validation_results if v.is_valid)
        invalid_count = len(validation_results) - valid_count
        
        self.console.print(f"[green]Valid Elements:[/green] {valid_count}")
        self.console.print(f"[red]Invalid Elements:[/red] {invalid_count}")
        
        # Show invalid elements
        if invalid_count > 0:
            self.console.print("\n[red]Invalid Elements:[/red]")
            for validation in validation_results:
                if not validation.is_valid:
                    self.console.print(f"  - {validation.element_id}: {validation.validation_reason}")
    
    def create_transparency_report(
        self,
        result: dict[str, Any],
        execution_id: str,
        workflow_type: str,
        include_all_details: bool = True
    ) -> dict[str, Any]:
        """Create a comprehensive transparency report.
        
        Args:
            result: The workflow result
            execution_id: Unique execution identifier
            workflow_type: Type of workflow
            include_all_details: Include all available transparency details
            
        Returns:
            Comprehensive transparency report
        """
        report = {
            "execution_id": execution_id,
            "workflow_type": workflow_type,
            "generated_at": datetime.now().isoformat(),
            "transparency_level": "comprehensive",
            "original_result": result
        }
        
        if include_all_details:
            # Add reasoning trace
            report["reasoning_trace"] = self.result_formatter._extract_reasoning_trace(result)
            
            # Add confidence analysis
            report["confidence_analysis"] = self.result_formatter._extract_confidence_analysis(result)
            
            # Add source attribution
            report["source_attribution"] = self.result_formatter._extract_source_attribution(result)
            
            # Add validation results if available
            validation_results = self.feedback_collector.validate_result_elements(result)
            report["validation_results"] = [v.model_dump() for v in validation_results]
            
            # Add feedback if available
            if execution_id in self.feedback_collector.feedback_storage:
                feedback = self.feedback_collector.feedback_storage[execution_id]
                report["user_feedback"] = feedback.model_dump()
        
        return report
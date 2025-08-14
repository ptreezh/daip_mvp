"""@Time    : 2025-07-24 20:00:00
@Author  : DAIP-LIVE Team
@File    : feedback_collector.py
@Description:
    User feedback collection and validation mechanisms for workflow results.
"""
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

logger = logging.getLogger(__name__)


class FeedbackType(str, Enum):
    """Types of feedback that can be collected."""

    RATING = "rating"
    VALIDATION = "validation"
    CORRECTION = "correction"
    SUGGESTION = "suggestion"
    QUALITY_ASSESSMENT = "quality_assessment"


class FeedbackItem(BaseModel):
    """Model for a single feedback item."""

    id: str
    feedback_type: FeedbackType
    target_element: str  # What the feedback is about (fact_id, synthesis, etc.)
    rating: Optional[int] = Field(None, ge=1, le=5)
    validation_result: Optional[bool] = None
    correction_text: Optional[str] = None
    suggestion_text: Optional[str] = None
    quality_scores: Dict[str, float] = Field(default_factory=dict)
    comments: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)
    user_id: Optional[str] = None


class WorkflowFeedback(BaseModel):
    """Model for complete workflow feedback."""

    execution_id: str
    workflow_type: str
    overall_rating: Optional[int] = Field(None, ge=1, le=5)
    overall_satisfaction: Optional[bool] = None
    feedback_items: List[FeedbackItem] = Field(default_factory=list)
    general_comments: str = ""
    improvement_suggestions: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
    user_id: Optional[str] = None


class ValidationResult(BaseModel):
    """Model for validation results."""

    element_id: str
    is_valid: bool
    confidence: float = Field(ge=0.0, le=1.0)
    validation_reason: str
    suggested_correction: Optional[str] = None
    validator_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class FeedbackCollector:
    """Collect and manage user feedback on workflow results."""

    def __init__(self):
        """Initialize the feedback collector."""
        self.console = Console()
        self.feedback_storage: Dict[str, WorkflowFeedback] = {}
        self.validation_callbacks: List[Callable[[ValidationResult], None]] = []

    def collect_workflow_feedback(
        self,
        result: Dict[str, Any],
        execution_id: str,
        workflow_type: str,
        interactive: bool = True,
        user_id: Optional[str] = None
    ) -> WorkflowFeedback:
        """Collect comprehensive feedback on workflow results."""
        feedback = WorkflowFeedback(
            execution_id=execution_id,
            workflow_type=workflow_type,
            user_id=user_id
        )

        if interactive:
            self._collect_interactive_feedback(result, feedback)
        else:
            # For non-interactive mode, create basic feedback structure
            feedback.feedback_items = self._create_default_feedback_items(result)

        # Store feedback
        self.feedback_storage[execution_id] = feedback

        return feedback

    def validate_result_elements(
        self,
        result: Dict[str, Any],
        validation_criteria: Dict[str, Any] = None,
        user_id: Optional[str] = None
    ) -> List[ValidationResult]:
        """Validate specific elements of the workflow result."""
        validation_results = []

        # Validate credibility scores if present
        if "credibility_scores" in result:
            for fact_id, score in result["credibility_scores"].items():
                validation = self._validate_credibility_score(
                    fact_id, score, validation_criteria, user_id
                )
                validation_results.append(validation)

        # Validate synthesis quality if present
        if "synthesis" in result:
            validation = self._validate_synthesis_quality(
                result["synthesis"], validation_criteria, user_id
            )
            validation_results.append(validation)

        # Validate fact accuracy if present
        if "extracted_facts" in result:
            for fact in result["extracted_facts"]:
                if isinstance(fact, dict) and "id" in fact:
                    validation = self._validate_fact_accuracy(
                        fact, validation_criteria, user_id
                    )
                    validation_results.append(validation)

        # Notify validation callbacks
        for validation in validation_results:
            for callback in self.validation_callbacks:
                try:
                    callback(validation)
                except Exception as e:
                    logger.error(f"Validation callback failed: {e}")

        return validation_results

    def collect_fact_validation(
        self,
        facts: List[Dict[str, Any]],
        interactive: bool = True
    ) -> List[FeedbackItem]:
        """Collect validation feedback for extracted facts."""
        feedback_items = []

        if not facts:
            return feedback_items

        if interactive:
            self.console.print("\n[blue]Fact Validation[/blue]")
            self.console.print("Please validate the following extracted facts:")

            for i, fact in enumerate(facts, 1):
                fact_id = fact.get("id", f"fact_{i}")
                fact_content = fact.get("content", "Unknown fact")

                self.console.print(f"\n[cyan]Fact {i}:[/cyan] {fact_content}")

                # Get validation
                is_valid = Confirm.ask("Is this fact accurate?")

                feedback_item = FeedbackItem(
                    id=f"validation_{fact_id}",
                    feedback_type=FeedbackType.VALIDATION,
                    target_element=fact_id,
                    validation_result=is_valid,
                    comments=Prompt.ask("Comments (optional)", default="")
                )

                # If invalid, ask for correction
                if not is_valid:
                    correction = Prompt.ask("Suggested correction (optional)", default="")
                    if correction:
                        feedback_item.correction_text = correction

                feedback_items.append(feedback_item)
        else:
            # Create default validation items for non-interactive mode
            for i, fact in enumerate(facts, 1):
                fact_id = fact.get("id", f"fact_{i}")
                feedback_item = FeedbackItem(
                    id=f"validation_{fact_id}",
                    feedback_type=FeedbackType.VALIDATION,
                    target_element=fact_id,
                    validation_result=None,  # Requires manual validation
                    comments="Requires manual validation"
                )
                feedback_items.append(feedback_item)

        return feedback_items

    def collect_quality_assessment(
        self,
        result: Dict[str, Any],
        assessment_criteria: List[str] = None,
        interactive: bool = True
    ) -> FeedbackItem:
        """Collect quality assessment feedback."""
        if assessment_criteria is None:
            assessment_criteria = [
                "accuracy", "completeness", "clarity", "usefulness", "relevance"
            ]

        quality_scores = {}

        if interactive:
            self.console.print("\n[blue]Quality Assessment[/blue]")
            self.console.print("Please rate the following aspects (1-5 scale):")

            for criterion in assessment_criteria:
                score = IntPrompt.ask(
                    f"Rate {criterion}",
                    choices=["1", "2", "3", "4", "5"],
                    default="3"
                )
                quality_scores[criterion] = float(score)
        else:
            # Default neutral scores for non-interactive mode
            quality_scores = dict.fromkeys(assessment_criteria, 3.0)

        feedback_item = FeedbackItem(
            id=f"quality_assessment_{datetime.now().timestamp()}",
            feedback_type=FeedbackType.QUALITY_ASSESSMENT,
            target_element="overall_result",
            quality_scores=quality_scores,
            comments=Prompt.ask("Additional comments", default="") if interactive else ""
        )

        return feedback_item

    def collect_improvement_suggestions(
        self,
        result: Dict[str, Any],
        interactive: bool = True
    ) -> List[str]:
        """Collect suggestions for improvement."""
        suggestions = []

        if interactive:
            self.console.print("\n[blue]Improvement Suggestions[/blue]")

            while True:
                suggestion = Prompt.ask(
                    "Enter improvement suggestion (or press Enter to finish)",
                    default=""
                )

                if not suggestion:
                    break

                suggestions.append(suggestion)

        return suggestions

    def display_feedback_summary(self, feedback: WorkflowFeedback) -> None:
        """Display a summary of collected feedback."""
        self.console.print(Panel(
            f"[green]Feedback Summary for {feedback.execution_id}[/green]",
            title="Feedback Summary",
            border_style="green"
        ))

        # Overall rating
        if feedback.overall_rating:
            self.console.print(f"[blue]Overall Rating:[/blue] {feedback.overall_rating}/5")

        if feedback.overall_satisfaction is not None:
            satisfaction = "✅ Satisfied" if feedback.overall_satisfaction else "❌ Not Satisfied"
            self.console.print(f"[blue]Overall Satisfaction:[/blue] {satisfaction}")

        # Feedback items summary
        if feedback.feedback_items:
            table = Table(title="Feedback Items")
            table.add_column("Type", style="cyan")
            table.add_column("Target", style="magenta")
            table.add_column("Result", style="green")
            table.add_column("Comments", style="yellow")

            for item in feedback.feedback_items:
                result_text = ""
                if item.rating:
                    result_text = f"{item.rating}/5"
                elif item.validation_result is not None:
                    result_text = "✅ Valid" if item.validation_result else "❌ Invalid"
                elif item.quality_scores:
                    avg_score = sum(item.quality_scores.values()) / len(item.quality_scores)
                    result_text = f"{avg_score:.1f}/5"

                table.add_row(
                    item.feedback_type.value,
                    item.target_element,
                    result_text,
                    item.comments[:50] + "..." if len(item.comments) > 50 else item.comments
                )

            self.console.print(table)

        # Improvement suggestions
        if feedback.improvement_suggestions:
            self.console.print("\n[blue]Improvement Suggestions:[/blue]")
            for i, suggestion in enumerate(feedback.improvement_suggestions, 1):
                self.console.print(f"  {i}. {suggestion}")

        # General comments
        if feedback.general_comments:
            self.console.print(f"\n[blue]General Comments:[/blue] {feedback.general_comments}")

    def export_feedback(
        self,
        execution_id: str,
        format_type: str = "json"
    ) -> str:
        """Export feedback data in specified format."""
        if execution_id not in self.feedback_storage:
            raise ValueError(f"No feedback found for execution {execution_id}")

        feedback = self.feedback_storage[execution_id]

        if format_type == "json":
            return feedback.model_dump_json(indent=2)
        elif format_type == "csv":
            return self._export_feedback_csv(feedback)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")

    def get_feedback_statistics(self) -> Dict[str, Any]:
        """Get statistics about collected feedback."""
        if not self.feedback_storage:
            return {"total_feedback": 0}

        total_feedback = len(self.feedback_storage)

        # Calculate average ratings
        ratings = [f.overall_rating for f in self.feedback_storage.values() if f.overall_rating]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0

        # Count satisfaction
        satisfactions = [f.overall_satisfaction for f in self.feedback_storage.values() if f.overall_satisfaction is not None]
        satisfaction_rate = sum(satisfactions) / len(satisfactions) if satisfactions else 0

        # Count feedback types
        feedback_type_counts = {}
        for feedback in self.feedback_storage.values():
            for item in feedback.feedback_items:
                feedback_type = item.feedback_type.value
                feedback_type_counts[feedback_type] = feedback_type_counts.get(feedback_type, 0) + 1

        return {
            "total_feedback": total_feedback,
            "average_rating": avg_rating,
            "satisfaction_rate": satisfaction_rate,
            "feedback_type_counts": feedback_type_counts
        }

    def add_validation_callback(self, callback: Callable[[ValidationResult], None]) -> None:
        """Add a callback for validation results."""
        self.validation_callbacks.append(callback)

    def remove_validation_callback(self, callback: Callable[[ValidationResult], None]) -> None:
        """Remove a validation callback."""
        try:
            self.validation_callbacks.remove(callback)
        except ValueError:
            pass

    def _collect_interactive_feedback(
        self,
        result: Dict[str, Any],
        feedback: WorkflowFeedback
    ) -> None:
        """Collect feedback interactively from the user."""
        self.console.print(Panel(
            "[blue]Workflow Feedback Collection[/blue]",
            title="Feedback",
            border_style="blue"
        ))

        # Overall rating
        feedback.overall_rating = IntPrompt.ask(
            "Overall rating (1-5)",
            choices=["1", "2", "3", "4", "5"],
            default="3"
        )

        # Overall satisfaction
        feedback.overall_satisfaction = Confirm.ask("Are you satisfied with the results?")

        # Collect specific feedback items
        if "credibility_scores" in result and result["credibility_scores"]:
            if Confirm.ask("Would you like to provide feedback on credibility scores?"):
                feedback.feedback_items.extend(
                    self._collect_credibility_feedback(result["credibility_scores"])
                )

        if "synthesis" in result:
            if Confirm.ask("Would you like to provide feedback on the synthesis?"):
                feedback.feedback_items.append(
                    self._collect_synthesis_feedback(result["synthesis"])
                )

        if "extracted_facts" in result:
            if Confirm.ask("Would you like to validate extracted facts?"):
                feedback.feedback_items.extend(
                    self.collect_fact_validation(result["extracted_facts"])
                )

        # Quality assessment
        if Confirm.ask("Would you like to provide a quality assessment?"):
            feedback.feedback_items.append(
                self.collect_quality_assessment(result)
            )

        # Improvement suggestions
        feedback.improvement_suggestions = self.collect_improvement_suggestions(result)

        # General comments
        feedback.general_comments = Prompt.ask("General comments (optional)", default="")

    def _create_default_feedback_items(self, result: Dict[str, Any]) -> List[FeedbackItem]:
        """Create default feedback items for non-interactive mode."""
        items = []

        # Create placeholder items for key result elements
        if "credibility_scores" in result:
            for fact_id in result["credibility_scores"].keys():
                items.append(FeedbackItem(
                    id=f"credibility_{fact_id}",
                    feedback_type=FeedbackType.RATING,
                    target_element=fact_id,
                    comments="Requires manual review"
                ))

        if "synthesis" in result:
            items.append(FeedbackItem(
                id="synthesis_feedback",
                feedback_type=FeedbackType.QUALITY_ASSESSMENT,
                target_element="synthesis",
                comments="Requires manual review"
            ))

        return items

    def _collect_credibility_feedback(self, credibility_scores: Dict[str, float]) -> List[FeedbackItem]:
        """Collect feedback on credibility scores."""
        feedback_items = []

        self.console.print("\n[blue]Credibility Score Feedback[/blue]")

        for fact_id, score in credibility_scores.items():
            self.console.print(f"\n[cyan]Fact {fact_id}:[/cyan] Credibility Score = {score:.3f}")

            rating = IntPrompt.ask(
                "Rate the accuracy of this credibility assessment (1-5)",
                choices=["1", "2", "3", "4", "5"],
                default="3"
            )

            comments = Prompt.ask("Comments on this assessment (optional)", default="")

            feedback_items.append(FeedbackItem(
                id=f"credibility_{fact_id}",
                feedback_type=FeedbackType.RATING,
                target_element=fact_id,
                rating=rating,
                comments=comments
            ))

        return feedback_items

    def _collect_synthesis_feedback(self, synthesis: str) -> FeedbackItem:
        """Collect feedback on synthesis quality."""
        self.console.print("\n[blue]Synthesis Feedback[/blue]")
        self.console.print(Panel(synthesis, title="Synthesis", border_style="cyan"))

        rating = IntPrompt.ask(
            "Rate the synthesis quality (1-5)",
            choices=["1", "2", "3", "4", "5"],
            default="3"
        )

        comments = Prompt.ask("Comments on the synthesis (optional)", default="")

        return FeedbackItem(
            id="synthesis_feedback",
            feedback_type=FeedbackType.RATING,
            target_element="synthesis",
            rating=rating,
            comments=comments
        )

    def _validate_credibility_score(
        self,
        fact_id: str,
        score: float,
        criteria: Dict[str, Any] = None,
        user_id: Optional[str] = None
    ) -> ValidationResult:
        """Validate a credibility score."""
        # Simple validation logic - can be enhanced
        is_valid = True
        confidence = 0.8
        reason = "Credibility score within acceptable range"

        if criteria:
            min_score = criteria.get("min_credibility", 0.0)
            max_score = criteria.get("max_credibility", 1.0)

            if score < min_score or score > max_score:
                is_valid = False
                confidence = 0.9
                reason = f"Credibility score {score:.3f} outside acceptable range [{min_score}, {max_score}]"

        return ValidationResult(
            element_id=fact_id,
            is_valid=is_valid,
            confidence=confidence,
            validation_reason=reason,
            validator_id=user_id
        )

    def _validate_synthesis_quality(
        self,
        synthesis: str,
        criteria: Dict[str, Any] = None,
        user_id: Optional[str] = None
    ) -> ValidationResult:
        """Validate synthesis quality."""
        # Simple validation logic - can be enhanced
        is_valid = True
        confidence = 0.7
        reason = "Synthesis appears to be well-formed"

        if len(synthesis) < 50:
            is_valid = False
            confidence = 0.9
            reason = "Synthesis too short to be meaningful"

        if criteria:
            min_length = criteria.get("min_synthesis_length", 50)
            if len(synthesis) < min_length:
                is_valid = False
                confidence = 0.9
                reason = f"Synthesis length {len(synthesis)} below minimum {min_length}"

        return ValidationResult(
            element_id="synthesis",
            is_valid=is_valid,
            confidence=confidence,
            validation_reason=reason,
            validator_id=user_id
        )

    def _validate_fact_accuracy(
        self,
        fact: Dict[str, Any],
        criteria: Dict[str, Any] = None,
        user_id: Optional[str] = None
    ) -> ValidationResult:
        """Validate fact accuracy."""
        fact_id = fact.get("id", "unknown")
        confidence_score = fact.get("confidence", 0.0)

        # Simple validation based on confidence
        is_valid = confidence_score >= 0.5
        confidence = confidence_score
        reason = f"Fact confidence {confidence_score:.3f} {'meets' if is_valid else 'below'} threshold"

        if criteria:
            min_confidence = criteria.get("min_fact_confidence", 0.5)
            is_valid = confidence_score >= min_confidence
            reason = f"Fact confidence {confidence_score:.3f} {'meets' if is_valid else 'below'} threshold {min_confidence}"

        return ValidationResult(
            element_id=fact_id,
            is_valid=is_valid,
            confidence=confidence,
            validation_reason=reason,
            validator_id=user_id
        )

    def _export_feedback_csv(self, feedback: WorkflowFeedback) -> str:
        """Export feedback as CSV format."""
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "Execution ID", "Workflow Type", "Overall Rating", "Overall Satisfaction",
            "Feedback Type", "Target Element", "Rating", "Validation Result",
            "Comments", "Timestamp"
        ])

        # Data rows
        for item in feedback.feedback_items:
            writer.writerow([
                feedback.execution_id,
                feedback.workflow_type,
                feedback.overall_rating,
                feedback.overall_satisfaction,
                item.feedback_type.value,
                item.target_element,
                item.rating,
                item.validation_result,
                item.comments,
                item.timestamp.isoformat()
            ])

        return output.getvalue()

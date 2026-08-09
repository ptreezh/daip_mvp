"""
Main intent parser for comprehensive intent recognition system.
Uses pattern matching to detect user intentions across all system commands.
"""

import re
from typing import Any, Optional

from daip_live.intent_recognition.models.intent_result import (
    DebateHistoryIntent,
    DocumentConversionIntent,
    IntentRecognitionResult,
    IntentType,
    ModelManagementIntent,
    PaperDownloadIntent,
    RoleManagementIntent,
    SessionManagementIntent,
    WikiManagementIntent,
)
from daip_live.intent_recognition.patterns import (
    DEBATE_HISTORY_PATTERNS,
    DOCUMENT_CONVERSION_PATTERNS,
    MODEL_MANAGEMENT_PATTERNS,
    PAPER_DOWNLOAD_PATTERNS,
    ROLE_MANAGEMENT_PATTERNS,
    SESSION_MANAGEMENT_PATTERNS,
    WIKI_MANAGEMENT_PATTERNS,
)


class IntentParser:
    """Main intent parser for recognizing user intents across all system commands."""

    def __init__(self):
        # Combined all patterns for unified matching
        self.all_patterns = {
            IntentType.DEBATE_HISTORY: DEBATE_HISTORY_PATTERNS,
            IntentType.DOCUMENT_CONVERSION: DOCUMENT_CONVERSION_PATTERNS,
            IntentType.WIKI_MANAGEMENT: WIKI_MANAGEMENT_PATTERNS,
            IntentType.PAPER_DOWNLOAD: PAPER_DOWNLOAD_PATTERNS,
            IntentType.SESSION_MANAGEMENT: SESSION_MANAGEMENT_PATTERNS,
            IntentType.ROLE_MANAGEMENT: ROLE_MANAGEMENT_PATTERNS,
            IntentType.MODEL_MANAGEMENT: MODEL_MANAGEMENT_PATTERNS,
        }

    def recognize_intent(self, user_input: str) -> list[IntentRecognitionResult]:
        """Recognize intents in user input with confidence scoring."""
        results = []
        user_input_lower = user_input.lower().strip()

        # Check all intent types
        for intent_type, patterns_by_action in self.all_patterns.items():
            for action, pattern_list in patterns_by_action.items():
                for pattern in pattern_list:
                    matches = re.search(pattern, user_input_lower, re.IGNORECASE)
                    if matches:
                        # Calculate confidence based on match quality
                        confidence = self._calculate_confidence(
                            pattern, user_input_lower, matches
                        )

                        # Extract parameters from match groups
                        parameters = self._extract_parameters(matches, action)

                        result = IntentRecognitionResult(
                            intent_type=intent_type,
                            confidence=confidence,
                            matched_pattern=pattern,
                            extracted_parameters=parameters,
                            matched_text=matches.group(0) if matches else None,
                        )

                        results.append(result)

        # Sort by confidence and return best matches
        results.sort(key=lambda x: x.confidence, reverse=True)
        return results

    def _calculate_confidence(self, pattern: str, input_text: str, match_obj) -> float:
        """Calculate confidence score for a pattern match."""
        # Base confidence on pattern specificity
        base_confidence = 0.7  # Base confidence for any match

        # Adjust based on pattern complexity (more specific patterns get higher confidence)  # noqa: E501
        if len(pattern) > 20:  # More specific patterns
            base_confidence += 0.2
        elif len(pattern) > 10:
            base_confidence += 0.1

        # Adjust based on match length relative to input
        match_length = len(match_obj.group(0)) if match_obj else 0
        if input_text:
            match_ratio = match_length / len(input_text)
            if 0.3 <= match_ratio <= 0.8:  # Good proportion of input
                base_confidence += 0.1

        # Cap at 1.0
        return min(base_confidence, 1.0)

    def _extract_parameters(self, matches, action: str) -> dict[str, Any]:
        """Extract parameters from regex matches."""
        params = {}

        # For patterns with capture groups
        if matches.groups():
            groups = matches.groups()
            if action in ["show_specific_debate", "view_specific_session"]:
                if len(groups) >= 1:
                    params["session_id"] = groups[0]
            elif action in ["download_paper", "search_paper"]:
                if len(groups) >= 1:
                    params["query"] = groups[0]
            elif action in ["show_role", "list_models", "switch_model"]:
                if len(groups) >= 1:
                    params["identifier"] = groups[0]
            elif action in ["convert"]:
                # Pattern might have two captures: "from" and "to" formats
                if len(groups) == 2:
                    params["source_format"] = groups[0]
                    params["target_format"] = groups[1]
                elif len(groups) == 1:
                    params["target_format"] = groups[0]

        return params

    def create_intent_object(self, result: IntentRecognitionResult) -> Optional[Any]:
        """Create appropriate intent object based on recognition result."""
        if not result.should_execute_automatically:
            return None  # Don't create intent object for low confidence

        if result.intent_type == IntentType.DEBATE_HISTORY:
            # Determine action based on extracted parameters
            if "session_id" in result.extracted_parameters:
                action = "view"
            elif result.matched_pattern in DEBATE_HISTORY_PATTERNS["search_debates"]:
                action = "search"
            elif (
                result.matched_pattern
                in DEBATE_HISTORY_PATTERNS["show_specific_debate"]
            ):
                action = "view"
            else:
                action = "list"

            return DebateHistoryIntent(
                action=action,
                session_id=result.extracted_parameters.get("session_id"),
                topic=result.extracted_parameters.get("topic"),
            )

        elif result.intent_type == IntentType.DOCUMENT_CONVERSION:
            action = "convert"  # Default to conversion
            return DocumentConversionIntent(
                action=action,
                source_format=result.extracted_parameters.get("source_format"),
                target_format=result.extracted_parameters.get("target_format"),
                file_path=result.extracted_parameters.get("file_path"),
            )

        elif result.intent_type == IntentType.WIKI_MANAGEMENT:
            # Determine action from pattern matching
            if result.matched_pattern in WIKI_MANAGEMENT_PATTERNS["create_wiki"]:
                action = "create"
            elif result.matched_pattern in WIKI_MANAGEMENT_PATTERNS["list_wiki"]:
                action = "list"
            elif result.matched_pattern in WIKI_MANAGEMENT_PATTERNS["export_wiki"]:
                action = "export"
            elif result.matched_pattern in WIKI_MANAGEMENT_PATTERNS["search_wiki"]:
                action = "search"
            else:
                action = "list"  # Default

            return WikiManagementIntent(
                action=action,
                page_title=result.extracted_parameters.get("page_title"),
                search_query=result.extracted_parameters.get("search_query"),
            )

        elif result.intent_type == IntentType.PAPER_DOWNLOAD:
            if result.matched_pattern in PAPER_DOWNLOAD_PATTERNS["list_papers"]:
                action = "list"
            else:
                action = "download"

            return PaperDownloadIntent(
                action=action,
                query=result.extracted_parameters.get("query"),
                source=result.extracted_parameters.get("source", "arxiv"),
            )

        elif result.intent_type == IntentType.SESSION_MANAGEMENT:
            if (
                result.matched_pattern
                in SESSION_MANAGEMENT_PATTERNS["view_specific_session"]
            ):
                action = "view"
            elif (
                result.matched_pattern in SESSION_MANAGEMENT_PATTERNS["clear_sessions"]
            ):
                action = "clear"
            else:
                action = "list"

            return SessionManagementIntent(
                action=action, session_id=result.extracted_parameters.get("session_id")
            )

        elif result.intent_type == IntentType.ROLE_MANAGEMENT:
            if result.matched_pattern in ROLE_MANAGEMENT_PATTERNS.get(
                "view_role", []
            ) or result.matched_pattern in ROLE_MANAGEMENT_PATTERNS.get(
                "list_roles", []
            ):
                action = (
                    "view"
                    if result.matched_pattern
                    in ROLE_MANAGEMENT_PATTERNS.get("view_role", [])
                    else "list"
                )
            else:
                action = "list"

            return RoleManagementIntent(
                action=action,
                role_name=result.extracted_parameters.get(
                    "identifier"
                ),  # Using identifier from extract_parameters
            )

        elif result.intent_type == IntentType.MODEL_MANAGEMENT:
            if result.matched_pattern in MODEL_MANAGEMENT_PATTERNS.get(
                "switch_model", []
            ):
                action = "switch"
            else:
                action = "list"

            return ModelManagementIntent(
                action=action,
                model_name=result.extracted_parameters.get(
                    "identifier"
                ),  # Using identifier from extract_parameters
            )

        return None


class EnhancedIntentParser(IntentParser):
    """Enhanced intent parser with additional context-aware matching."""

    def __init__(self, context: Optional[dict[str, Any]] = None):
        super().__init__()
        self.context = context or {}

    def recognize_intent_with_context(
        self, user_input: str
    ) -> list[IntentRecognitionResult]:
        """Recognize intents considering additional context information."""
        base_results = self.recognize_intent(user_input)

        # Apply context-based adjustments
        adjusted_results = []
        for result in base_results:
            # Adjust confidence based on context
            adjusted_confidence = result.confidence
            if self._context_suggests_intent(result.intent_type):
                adjusted_confidence = min(adjusted_confidence + 0.1, 1.0)

            adjusted_result = IntentRecognitionResult(
                intent_type=result.intent_type,
                confidence=adjusted_confidence,
                matched_pattern=result.matched_pattern,
                extracted_parameters=result.extracted_parameters,
                matched_text=result.matched_text,
                detected_at=result.detected_at,
            )
            adjusted_results.append(adjusted_result)

        # Sort by adjusted confidence
        adjusted_results.sort(key=lambda x: x.confidence, reverse=True)
        return adjusted_results

    def _context_suggests_intent(self, intent_type: IntentType) -> bool:
        """Check if current context suggests a particular intent."""
        # Look for context clues in recent conversation or session
        context_clues = self.context.get("recent_topics", [])
        if intent_type == IntentType.DEBATE_HISTORY:
            return any(
                "debate" in topic.lower() or "history" in topic.lower()
                for topic in context_clues
            )
        elif intent_type == IntentType.WIKI_MANAGEMENT:
            return any(
                "wiki" in topic.lower() or "knowledge" in topic.lower()
                for topic in context_clues
            )
        elif intent_type == IntentType.PAPER_DOWNLOAD:
            return any(
                "paper" in topic.lower()
                or "research" in topic.lower()
                or "article" in topic.lower()
                for topic in context_clues
            )
        elif intent_type == IntentType.SESSION_MANAGEMENT:
            return any(
                "session" in topic.lower() or "history" in topic.lower()
                for topic in context_clues
            )

        return False

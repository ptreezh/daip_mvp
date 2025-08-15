#!/usr/bin/env python3
"""Collective Intelligence Manager

This module orchestrates the collective intelligence emergence process,
integrating cognitive diversity evaluation, advanced consensus algorithms,
and emergent insight detection to facilitate true collective intelligence.

Requirements: 11.4, 11.5, 11.8, 11.10
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from .advanced_consensus_algorithms import ConsensusInput, ConsensusResult
from .cognitive_diversity_evaluator import CognitiveDiversityEvaluator
from .consensus_algorithm_selector import ConsensusAlgorithmSelector
from .emergent_insight_detector import EmergentInsight, EmergentInsightDetector


@dataclass
class CollectiveIntelligenceSession:
    """Represents a collective intelligence session."""
    session_id: str
    participants: list[str]
    topic: str
    start_time: datetime
    end_time: Optional[datetime] = None
    diversity_score: Optional[float] = None
    consensus_results: list[ConsensusResult] = None
    emergent_insights: list[EmergentInsight] = None
    intelligence_emergence_score: Optional[float] = None


class CollectiveIntelligenceManager:
    """Manages collective intelligence emergence processes.
    
    This class orchestrates the interaction between cognitive diversity evaluation,
    consensus algorithms, and emergent insight detection to facilitate the
    emergence of collective intelligence that transcends individual capabilities.
    """
    
    def __init__(self):
        """Initialize the collective intelligence manager."""
        self.logger = logging.getLogger("collective_intelligence_manager")
        
        # Initialize component managers
        self.diversity_evaluator = CognitiveDiversityEvaluator()
        self.algorithm_selector = ConsensusAlgorithmSelector()
        self.insight_detector = EmergentInsightDetector()
        
        # Session management
        self.active_sessions: dict[str, CollectiveIntelligenceSession] = {}
        self.session_history: list[CollectiveIntelligenceSession] = []
        
        # Performance tracking
        self.emergence_metrics: dict[str, list[float]] = {
            "diversity_scores": [],
            "consensus_confidence": [],
            "insight_counts": [],
            "intelligence_emergence": []
        }
        
        self.logger.info("Collective Intelligence Manager initialized")
    
    def start_collective_intelligence_session(
        self,
        session_id: str,
        participants: list[str],
        topic: str,
        participant_profiles: dict[str, dict[str, Any]]
    ) -> CollectiveIntelligenceSession:
        """Start a new collective intelligence session.
        
        Args:
            session_id: Unique identifier for the session
            participants: List of participant IDs
            topic: Topic for the collective intelligence session
            participant_profiles: Cognitive profiles of participants
            
        Returns:
            CollectiveIntelligenceSession object
        """
        self.logger.info(f"Starting collective intelligence session '{session_id}' with {len(participants)} participants")
        
        # Evaluate initial diversity
        diversity_score = self.diversity_evaluator.calculate_group_diversity(
            participant_profiles, session_id
        )
        
        # Create session
        session = CollectiveIntelligenceSession(
            session_id=session_id,
            participants=participants,
            topic=topic,
            start_time=datetime.now(),
            diversity_score=diversity_score.overall_score,
            consensus_results=[],
            emergent_insights=[]
        )
        
        self.active_sessions[session_id] = session
        
        self.logger.info(f"Session '{session_id}' started with diversity score: {diversity_score.overall_score:.3f}")
        return session
    
    def process_collective_input(
        self,
        session_id: str,
        inputs: list[ConsensusInput],
        context: Optional[dict[str, Any]] = None
    ) -> tuple[ConsensusResult, list[EmergentInsight]]:
        """Process collective input to generate consensus and detect emergent insights.
        
        Args:
            session_id: Session identifier
            inputs: List of consensus inputs from participants
            context: Additional context for processing
            
        Returns:
            Tuple of (consensus result, emergent insights)
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session '{session_id}' not found")
        
        session = self.active_sessions[session_id]
        self.logger.info(f"Processing collective input for session '{session_id}' with {len(inputs)} inputs")
        
        # Select appropriate consensus algorithm
        algorithm_type = self.algorithm_selector.select_algorithm(inputs, context)
        self.logger.info(f"Selected consensus algorithm: {algorithm_type.value}")
        
        # Create algorithm instance with optimized parameters
        selection_context = self.algorithm_selector._analyze_context(inputs, context)
        algorithm = self.algorithm_selector.create_algorithm_instance(algorithm_type, selection_context)
        
        # Calculate consensus
        consensus_result = algorithm.calculate_consensus(inputs, context)
        
        # Detect emergent insights
        source_positions = [input_item.position for input_item in inputs if isinstance(input_item.position, str)]
        contributing_agents = [input_item.agent_id for input_item in inputs]
        
        emergent_insights = self.insight_detector.detect_emergent_insights(
            str(consensus_result.consensus_value),
            source_positions,
            contributing_agents,
            context
        )
        
        # Update session
        session.consensus_results.append(consensus_result)
        session.emergent_insights.extend(emergent_insights)
        
        # Record algorithm performance
        self.algorithm_selector.record_algorithm_performance(
            algorithm_type,
            consensus_result,
            selection_context
        )
        
        # Update metrics
        self._update_emergence_metrics(session, consensus_result, emergent_insights)
        
        self.logger.info(f"Generated consensus with confidence {consensus_result.confidence_level:.3f} "
                        f"and detected {len(emergent_insights)} emergent insights")
        
        return consensus_result, emergent_insights
    
    def evaluate_intelligence_emergence(
        self,
        session_id: str
    ) -> dict[str, Any]:
        """Evaluate the level of collective intelligence emergence in a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary containing emergence evaluation metrics
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session '{session_id}' not found")
        
        session = self.active_sessions[session_id]
        self.logger.info(f"Evaluating intelligence emergence for session '{session_id}'")
        
        # Calculate emergence metrics
        emergence_evaluation = {
            "session_id": session_id,
            "participant_count": len(session.participants),
            "diversity_score": session.diversity_score,
            "consensus_rounds": len(session.consensus_results),
            "total_insights": len(session.emergent_insights),
            "intelligence_emergence_score": 0.0,
            "emergence_indicators": {},
            "quality_metrics": {},
            "temporal_analysis": {}
        }
        
        # Analyze consensus quality
        if session.consensus_results:
            consensus_confidences = [result.confidence_level for result in session.consensus_results]
            consensus_diversities = [result.diversity_score for result in session.consensus_results]
            
            emergence_evaluation["quality_metrics"] = {
                "avg_consensus_confidence": sum(consensus_confidences) / len(consensus_confidences),
                "avg_consensus_diversity": sum(consensus_diversities) / len(consensus_diversities),
                "confidence_trend": self._calculate_trend(consensus_confidences),
                "diversity_preservation": sum(consensus_diversities) / len(consensus_diversities)
            }
        
        # Analyze emergent insights
        if session.emergent_insights:
            insight_scores = [insight.emergence_score for insight in session.emergent_insights]
            novelty_scores = [insight.novelty_score for insight in session.emergent_insights]
            
            emergence_evaluation["emergence_indicators"] = {
                "insight_density": len(session.emergent_insights) / max(len(session.consensus_results), 1),
                "avg_emergence_score": sum(insight_scores) / len(insight_scores),
                "avg_novelty_score": sum(novelty_scores) / len(novelty_scores),
                "insight_types": self._analyze_insight_types(session.emergent_insights),
                "emergence_patterns": self._analyze_emergence_patterns(session.emergent_insights)
            }
        
        # Calculate overall intelligence emergence score
        intelligence_score = self._calculate_intelligence_emergence_score(emergence_evaluation)
        emergence_evaluation["intelligence_emergence_score"] = intelligence_score
        
        # Update session
        session.intelligence_emergence_score = intelligence_score
        
        self.logger.info(f"Intelligence emergence score for session '{session_id}': {intelligence_score:.3f}")
        return emergence_evaluation
    
    def end_collective_intelligence_session(
        self,
        session_id: str
    ) -> CollectiveIntelligenceSession:
        """End a collective intelligence session and generate final report.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Completed session object
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session '{session_id}' not found")
        
        session = self.active_sessions[session_id]
        session.end_time = datetime.now()
        
        # Final evaluation
        final_evaluation = self.evaluate_intelligence_emergence(session_id)
        
        # Move to history
        self.session_history.append(session)
        del self.active_sessions[session_id]
        
        self.logger.info(f"Session '{session_id}' ended with intelligence emergence score: "
                        f"{session.intelligence_emergence_score:.3f}")
        
        return session
    
    def get_collective_intelligence_report(
        self,
        session_id: str
    ) -> dict[str, Any]:
        """Generate a comprehensive collective intelligence report.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Comprehensive report dictionary
        """
        # Find session in active or history
        session = None
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
        else:
            for hist_session in self.session_history:
                if hist_session.session_id == session_id:
                    session = hist_session
                    break
        
        if not session:
            raise ValueError(f"Session '{session_id}' not found")
        
        # Generate comprehensive report
        report = {
            "session_info": {
                "session_id": session.session_id,
                "topic": session.topic,
                "participants": session.participants,
                "duration": (session.end_time - session.start_time).total_seconds() / 3600 if session.end_time else None,
                "status": "completed" if session.end_time else "active"
            },
            "diversity_analysis": {
                "initial_diversity_score": session.diversity_score,
                "participant_count": len(session.participants),
                "diversity_category": self._categorize_diversity(session.diversity_score)
            },
            "consensus_analysis": {
                "total_consensus_rounds": len(session.consensus_results),
                "consensus_summary": self._summarize_consensus_results(session.consensus_results),
                "algorithm_usage": self._analyze_algorithm_usage(session.consensus_results)
            },
            "insight_analysis": {
                "total_insights": len(session.emergent_insights),
                "insight_breakdown": self._analyze_insight_types(session.emergent_insights),
                "emergence_patterns": self._analyze_emergence_patterns(session.emergent_insights),
                "top_insights": self._get_top_insights(session.emergent_insights, 5)
            },
            "intelligence_emergence": {
                "emergence_score": session.intelligence_emergence_score,
                "emergence_category": self._categorize_emergence(session.intelligence_emergence_score),
                "key_indicators": self._identify_key_emergence_indicators(session)
            },
            "recommendations": self._generate_recommendations(session)
        }
        
        return report
    
    def _update_emergence_metrics(
        self,
        session: CollectiveIntelligenceSession,
        consensus_result: ConsensusResult,
        emergent_insights: list[EmergentInsight]
    ) -> None:
        """Update emergence metrics."""
        self.emergence_metrics["diversity_scores"].append(session.diversity_score or 0.0)
        self.emergence_metrics["consensus_confidence"].append(consensus_result.confidence_level)
        self.emergence_metrics["insight_counts"].append(len(emergent_insights))
        
        # Calculate intelligence emergence for this round
        intelligence_score = self._calculate_round_intelligence_score(
            session.diversity_score or 0.0,
            consensus_result.confidence_level,
            len(emergent_insights)
        )
        self.emergence_metrics["intelligence_emergence"].append(intelligence_score)
    
    def _calculate_trend(self, values: list[float]) -> str:
        """Calculate trend direction for a list of values."""
        if len(values) < 2:
            return "stable"
        
        # Simple linear trend
        x = list(range(len(values)))
        slope = sum((x[i] - sum(x)/len(x)) * (values[i] - sum(values)/len(values)) for i in range(len(values)))
        slope /= sum((x[i] - sum(x)/len(x))**2 for i in range(len(values)))
        
        if slope > 0.01:
            return "increasing"
        elif slope < -0.01:
            return "decreasing"
        else:
            return "stable"
    
    def _analyze_insight_types(self, insights: list[EmergentInsight]) -> dict[str, int]:
        """Analyze the types of emergent insights."""
        type_counts = {}
        for insight in insights:
            insight_type = insight.insight_type.value
            type_counts[insight_type] = type_counts.get(insight_type, 0) + 1
        return type_counts
    
    def _analyze_emergence_patterns(self, insights: list[EmergentInsight]) -> dict[str, int]:
        """Analyze emergence patterns in insights."""
        pattern_counts = {}
        for insight in insights:
            pattern = insight.emergence_pattern.value
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        return pattern_counts
    
    def _calculate_intelligence_emergence_score(self, evaluation: dict[str, Any]) -> float:
        """Calculate overall intelligence emergence score."""
        score = 0.0
        
        # Diversity contribution (20%)
        diversity_score = evaluation.get("diversity_score", 0.0)
        score += diversity_score * 0.2
        
        # Consensus quality contribution (30%)
        quality_metrics = evaluation.get("quality_metrics", {})
        if quality_metrics:
            consensus_quality = (
                quality_metrics.get("avg_consensus_confidence", 0.0) * 0.6 +
                quality_metrics.get("avg_consensus_diversity", 0.0) * 0.4
            )
            score += consensus_quality * 0.3
        
        # Insight emergence contribution (50%)
        emergence_indicators = evaluation.get("emergence_indicators", {})
        if emergence_indicators:
            insight_quality = (
                min(emergence_indicators.get("insight_density", 0.0), 1.0) * 0.3 +
                emergence_indicators.get("avg_emergence_score", 0.0) * 0.4 +
                emergence_indicators.get("avg_novelty_score", 0.0) * 0.3
            )
            score += insight_quality * 0.5
        
        return min(score, 1.0)
    
    def _calculate_round_intelligence_score(
        self,
        diversity_score: float,
        consensus_confidence: float,
        insight_count: int
    ) -> float:
        """Calculate intelligence score for a single round."""
        # Normalize insight count
        normalized_insight_count = min(insight_count / 3.0, 1.0)
        
        # Weighted combination
        score = (
            diversity_score * 0.3 +
            consensus_confidence * 0.4 +
            normalized_insight_count * 0.3
        )
        
        return min(score, 1.0)
    
    def _summarize_consensus_results(self, results: list[ConsensusResult]) -> dict[str, Any]:
        """Summarize consensus results."""
        if not results:
            return {}
        
        confidences = [result.confidence_level for result in results]
        diversities = [result.diversity_score for result in results]
        
        return {
            "avg_confidence": sum(confidences) / len(confidences),
            "min_confidence": min(confidences),
            "max_confidence": max(confidences),
            "avg_diversity": sum(diversities) / len(diversities),
            "confidence_trend": self._calculate_trend(confidences)
        }
    
    def _analyze_algorithm_usage(self, results: list[ConsensusResult]) -> dict[str, int]:
        """Analyze which algorithms were used."""
        algorithm_counts = {}
        for result in results:
            algorithm = result.algorithm_used.value
            algorithm_counts[algorithm] = algorithm_counts.get(algorithm, 0) + 1
        return algorithm_counts
    
    def _get_top_insights(self, insights: list[EmergentInsight], count: int) -> list[dict[str, Any]]:
        """Get top insights by emergence score."""
        sorted_insights = sorted(insights, key=lambda x: x.emergence_score, reverse=True)
        
        return [
            {
                "content": insight.content,
                "type": insight.insight_type.value,
                "emergence_score": insight.emergence_score,
                "novelty_score": insight.novelty_score
            }
            for insight in sorted_insights[:count]
        ]
    
    def _categorize_diversity(self, diversity_score: Optional[float]) -> str:
        """Categorize diversity level."""
        if diversity_score is None:
            return "unknown"
        elif diversity_score < 0.3:
            return "low"
        elif diversity_score < 0.7:
            return "medium"
        else:
            return "high"
    
    def _categorize_emergence(self, emergence_score: Optional[float]) -> str:
        """Categorize intelligence emergence level."""
        if emergence_score is None:
            return "unknown"
        elif emergence_score < 0.4:
            return "minimal"
        elif emergence_score < 0.7:
            return "moderate"
        else:
            return "strong"
    
    def _identify_key_emergence_indicators(self, session: CollectiveIntelligenceSession) -> list[str]:
        """Identify key indicators of intelligence emergence."""
        indicators = []
        
        if session.diversity_score and session.diversity_score > 0.7:
            indicators.append("High cognitive diversity among participants")
        
        if session.consensus_results:
            avg_confidence = sum(r.confidence_level for r in session.consensus_results) / len(session.consensus_results)
            if avg_confidence > 0.8:
                indicators.append("High consensus confidence levels")
        
        if len(session.emergent_insights) > len(session.consensus_results):
            indicators.append("High insight generation rate")
        
        if session.emergent_insights:
            avg_novelty = sum(i.novelty_score for i in session.emergent_insights) / len(session.emergent_insights)
            if avg_novelty > 0.7:
                indicators.append("High novelty in generated insights")
        
        return indicators
    
    def _generate_recommendations(self, session: CollectiveIntelligenceSession) -> list[str]:
        """Generate recommendations for improving collective intelligence."""
        recommendations = []
        
        if session.diversity_score and session.diversity_score < 0.5:
            recommendations.append("Increase cognitive diversity by including participants with different reasoning styles and backgrounds")
        
        if session.consensus_results:
            avg_confidence = sum(r.confidence_level for r in session.consensus_results) / len(session.consensus_results)
            if avg_confidence < 0.6:
                recommendations.append("Improve consensus quality by providing more structured discussion frameworks")
        
        if len(session.emergent_insights) < len(session.consensus_results) * 0.5:
            recommendations.append("Encourage more creative and synthetic thinking to generate emergent insights")
        
        if len(session.participants) < 5:
            recommendations.append("Consider including more participants to increase perspective diversity")
        
        return recommendations
    
    def get_system_performance_metrics(self) -> dict[str, Any]:
        """Get overall system performance metrics."""
        return {
            "active_sessions": len(self.active_sessions),
            "completed_sessions": len(self.session_history),
            "average_metrics": {
                "diversity_score": sum(self.emergence_metrics["diversity_scores"]) / len(self.emergence_metrics["diversity_scores"]) if self.emergence_metrics["diversity_scores"] else 0,
                "consensus_confidence": sum(self.emergence_metrics["consensus_confidence"]) / len(self.emergence_metrics["consensus_confidence"]) if self.emergence_metrics["consensus_confidence"] else 0,
                "insight_count": sum(self.emergence_metrics["insight_counts"]) / len(self.emergence_metrics["insight_counts"]) if self.emergence_metrics["insight_counts"] else 0,
                "intelligence_emergence": sum(self.emergence_metrics["intelligence_emergence"]) / len(self.emergence_metrics["intelligence_emergence"]) if self.emergence_metrics["intelligence_emergence"] else 0
            },
            "trends": {
                "diversity": self._calculate_trend(self.emergence_metrics["diversity_scores"]),
                "consensus": self._calculate_trend(self.emergence_metrics["consensus_confidence"]),
                "insights": self._calculate_trend(self.emergence_metrics["insight_counts"]),
                "emergence": self._calculate_trend(self.emergence_metrics["intelligence_emergence"])
            }
        }
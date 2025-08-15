#!/usr/bin/env python3
"""Emergent Insight Detector

This module implements sophisticated algorithms for detecting emergent insights
that arise from collective intelligence processes, identifying patterns of
knowledge creation that transcend individual contributions.

Requirements: 11.5, 11.8, 11.10
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class InsightType(str, Enum):
    """Types of emergent insights."""
    SYNTHESIS_EMERGENCE = "synthesis_emergence"
    CONTRADICTION_RESOLUTION = "contradiction_resolution"
    NOVEL_CONCEPT_CREATION = "novel_concept_creation"
    PATTERN_DISCOVERY = "pattern_discovery"
    PERSPECTIVE_INTEGRATION = "perspective_integration"
    KNOWLEDGE_BRIDGING = "knowledge_bridging"
    CREATIVE_LEAP = "creative_leap"


class EmergencePattern(str, Enum):
    """Patterns of emergence."""
    ADDITIVE = "additive"  # Sum of parts
    SYNERGISTIC = "synergistic"  # Greater than sum of parts
    TRANSFORMATIVE = "transformative"  # Qualitatively different
    DIALECTICAL = "dialectical"  # Thesis + antithesis = synthesis


@dataclass
class InsightCandidate:
    """A candidate emergent insight."""
    content: str
    insight_type: InsightType
    emergence_pattern: EmergencePattern
    emergence_score: float
    contributing_agents: list[str]
    source_positions: list[str]
    novelty_score: float
    coherence_score: float
    evidence_strength: float


class EmergentInsight(BaseModel):
    """Validated emergent insight."""
    insight_id: str
    content: str
    insight_type: InsightType
    emergence_pattern: EmergencePattern
    emergence_score: float = Field(ge=0.0, le=1.0)
    novelty_score: float = Field(ge=0.0, le=1.0)
    coherence_score: float = Field(ge=0.0, le=1.0)
    evidence_strength: float = Field(ge=0.0, le=1.0)
    contributing_agents: list[str]
    source_positions: list[str]
    synthesis_trace: dict[str, Any]
    validation_score: float = Field(ge=0.0, le=1.0)
    timestamp: datetime


class ConceptExtractor:
    """Extracts concepts and relationships from text."""
    
    def __init__(self):
        self.logger = logging.getLogger("concept_extractor")
        
        # Common concept patterns
        self.concept_patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Proper nouns
            r'\b(?:the\s+)?[a-z]+(?:\s+[a-z]+)*(?:\s+of\s+[a-z]+(?:\s+[a-z]+)*)*\b',  # Noun phrases
            r'\b[a-z]+ing\b',  # Gerunds
            r'\b[a-z]+tion\b',  # Abstract nouns ending in -tion
            r'\b[a-z]+ness\b',  # Abstract nouns ending in -ness
        ]
        
        # Relationship indicators
        self.relationship_patterns = [
            r'\bcauses?\b', r'\bleads?\s+to\b', r'\bresults?\s+in\b',
            r'\binfluences?\b', r'\baffects?\b', r'\bimpacts?\b',
            r'\brelates?\s+to\b', r'\bconnects?\s+to\b', r'\bassociates?\s+with\b',
            r'\bdepends?\s+on\b', r'\brequires?\b', r'\benables?\b'
        ]
    
    def extract_concepts(self, text: str) -> set[str]:
        """Extract concepts from text."""
        concepts = set()
        
        # Clean text
        cleaned_text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Extract using patterns
        for pattern in self.concept_patterns:
            matches = re.findall(pattern, cleaned_text)
            concepts.update(match.strip() for match in matches if len(match.strip()) > 2)
        
        # Filter out common words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        concepts = {concept for concept in concepts if concept not in stop_words}
        
        return concepts
    
    def extract_relationships(self, text: str) -> list[tuple[str, str, str]]:
        """Extract relationships from text (subject, relation, object)."""
        relationships = []
        
        # Simple relationship extraction
        sentences = re.split(r'[.!?]', text)
        
        for sentence in sentences:
            sentence = sentence.strip().lower()
            if not sentence:
                continue
            
            for pattern in self.relationship_patterns:
                matches = re.search(pattern, sentence)
                if matches:
                    # Extract subject and object around the relationship
                    relation = matches.group()
                    before = sentence[:matches.start()].strip()
                    after = sentence[matches.end():].strip()
                    
                    if before and after:
                        # Extract last noun phrase before and first noun phrase after
                        subject = self._extract_last_noun_phrase(before)
                        obj = self._extract_first_noun_phrase(after)
                        
                        if subject and obj:
                            relationships.append((subject, relation, obj))
        
        return relationships
    
    def _extract_last_noun_phrase(self, text: str) -> Optional[str]:
        """Extract the last noun phrase from text."""
        words = text.split()
        if not words:
            return None
        
        # Simple heuristic: take last 1-3 words
        if len(words) >= 3:
            return ' '.join(words[-3:])
        elif len(words) >= 2:
            return ' '.join(words[-2:])
        else:
            return words[-1]
    
    def _extract_first_noun_phrase(self, text: str) -> Optional[str]:
        """Extract the first noun phrase from text."""
        words = text.split()
        if not words:
            return None
        
        # Simple heuristic: take first 1-3 words
        if len(words) >= 3:
            return ' '.join(words[:3])
        elif len(words) >= 2:
            return ' '.join(words[:2])
        else:
            return words[0]


class NoveltyDetector:
    """Detects novelty in concepts and ideas."""
    
    def __init__(self):
        self.logger = logging.getLogger("novelty_detector")
        self.concept_extractor = ConceptExtractor()
        self.known_concepts: set[str] = set()
        self.concept_frequencies: dict[str, int] = {}
    
    def update_knowledge_base(self, texts: list[str]) -> None:
        """Update the knowledge base with new texts."""
        for text in texts:
            concepts = self.concept_extractor.extract_concepts(text)
            self.known_concepts.update(concepts)
            
            for concept in concepts:
                self.concept_frequencies[concept] = self.concept_frequencies.get(concept, 0) + 1
    
    def calculate_novelty_score(self, text: str, source_texts: list[str]) -> float:
        """Calculate novelty score of text compared to source texts."""
        # Extract concepts from the text
        text_concepts = self.concept_extractor.extract_concepts(text)
        
        # Extract concepts from source texts
        source_concepts = set()
        for source_text in source_texts:
            source_concepts.update(self.concept_extractor.extract_concepts(source_text))
        
        if not text_concepts:
            return 0.0
        
        # Calculate novelty metrics
        novel_concepts = text_concepts - source_concepts
        novelty_ratio = len(novel_concepts) / len(text_concepts)
        
        # Calculate concept rarity (inverse frequency)
        rarity_scores = []
        for concept in text_concepts:
            frequency = self.concept_frequencies.get(concept, 0)
            rarity = 1.0 / (1.0 + frequency)  # Higher rarity for less frequent concepts
            rarity_scores.append(rarity)
        
        avg_rarity = sum(rarity_scores) / len(rarity_scores) if rarity_scores else 0.0
        
        # Combine novelty ratio and rarity
        novelty_score = 0.7 * novelty_ratio + 0.3 * avg_rarity
        
        return min(novelty_score, 1.0)
    
    def detect_novel_combinations(
        self,
        text: str,
        source_texts: list[str]
    ) -> list[tuple[str, float]]:
        """Detect novel combinations of known concepts."""
        text_concepts = self.concept_extractor.extract_concepts(text)
        source_concepts = set()
        
        for source_text in source_texts:
            source_concepts.update(self.concept_extractor.extract_concepts(source_text))
        
        # Find concept pairs in the text
        text_concept_list = list(text_concepts)
        novel_combinations = []
        
        for i in range(len(text_concept_list)):
            for j in range(i + 1, len(text_concept_list)):
                concept1, concept2 = text_concept_list[i], text_concept_list[j]
                
                # Check if this combination appeared in source texts
                combination_found = False
                for source_text in source_texts:
                    if concept1 in source_text and concept2 in source_text:
                        combination_found = True
                        break
                
                if not combination_found:
                    # Novel combination
                    combination = f"{concept1} + {concept2}"
                    novelty_score = self._calculate_combination_novelty(concept1, concept2)
                    novel_combinations.append((combination, novelty_score))
        
        return novel_combinations
    
    def _calculate_combination_novelty(self, concept1: str, concept2: str) -> float:
        """Calculate novelty score for a concept combination."""
        # Simple heuristic based on concept frequencies
        freq1 = self.concept_frequencies.get(concept1, 0)
        freq2 = self.concept_frequencies.get(concept2, 0)
        
        # Lower frequencies indicate higher novelty
        novelty1 = 1.0 / (1.0 + freq1)
        novelty2 = 1.0 / (1.0 + freq2)
        
        return (novelty1 + novelty2) / 2.0


class CoherenceAnalyzer:
    """Analyzes coherence and consistency of insights."""
    
    def __init__(self):
        self.logger = logging.getLogger("coherence_analyzer")
        self.concept_extractor = ConceptExtractor()
    
    def calculate_coherence_score(
        self,
        text: str,
        source_texts: list[str]
    ) -> float:
        """Calculate coherence score of text."""
        # Extract concepts and relationships
        text_concepts = self.concept_extractor.extract_concepts(text)
        text_relationships = self.concept_extractor.extract_relationships(text)
        
        if not text_concepts:
            return 0.0
        
        # Calculate internal coherence
        internal_coherence = self._calculate_internal_coherence(text_concepts, text_relationships)
        
        # Calculate coherence with source texts
        source_coherence = self._calculate_source_coherence(text, source_texts)
        
        # Combine scores
        coherence_score = 0.6 * internal_coherence + 0.4 * source_coherence
        
        return min(coherence_score, 1.0)
    
    def _calculate_internal_coherence(
        self,
        concepts: set[str],
        relationships: list[tuple[str, str, str]]
    ) -> float:
        """Calculate internal coherence of concepts and relationships."""
        if not concepts:
            return 0.0
        
        # Check how many concepts are connected by relationships
        connected_concepts = set()
        for subject, relation, obj in relationships:
            connected_concepts.add(subject)
            connected_concepts.add(obj)
        
        # Coherence is higher when more concepts are connected
        connection_ratio = len(connected_concepts) / len(concepts)
        
        # Also consider relationship density
        max_relationships = len(concepts) * (len(concepts) - 1) / 2
        relationship_density = len(relationships) / max_relationships if max_relationships > 0 else 0
        
        return 0.7 * connection_ratio + 0.3 * relationship_density
    
    def _calculate_source_coherence(self, text: str, source_texts: list[str]) -> float:
        """Calculate coherence with source texts."""
        if not source_texts:
            return 0.5  # Neutral score when no sources
        
        text_concepts = self.concept_extractor.extract_concepts(text)
        
        coherence_scores = []
        for source_text in source_texts:
            source_concepts = self.concept_extractor.extract_concepts(source_text)
            
            # Calculate concept overlap
            if text_concepts and source_concepts:
                overlap = len(text_concepts & source_concepts)
                union = len(text_concepts | source_concepts)
                jaccard_similarity = overlap / union if union > 0 else 0
                coherence_scores.append(jaccard_similarity)
        
        return sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0.5


class EmergentInsightDetector:
    """Main class for detecting emergent insights."""
    
    def __init__(self):
        self.logger = logging.getLogger("emergent_insight_detector")
        self.concept_extractor = ConceptExtractor()
        self.novelty_detector = NoveltyDetector()
        self.coherence_analyzer = CoherenceAnalyzer()
        
        # Thresholds for insight detection
        self.emergence_threshold = 0.6
        self.novelty_threshold = 0.4
        self.coherence_threshold = 0.5
        self.evidence_threshold = 0.3
    
    def detect_emergent_insights(
        self,
        consensus_result: str,
        source_positions: list[str],
        contributing_agents: list[str],
        context: Optional[dict[str, Any]] = None
    ) -> list[EmergentInsight]:
        """Detect emergent insights from consensus process."""
        self.logger.info(f"Detecting emergent insights from consensus with {len(source_positions)} source positions")
        
        # Update knowledge base
        self.novelty_detector.update_knowledge_base(source_positions)
        
        # Generate insight candidates
        candidates = self._generate_insight_candidates(
            consensus_result,
            source_positions,
            contributing_agents,
            context
        )
        
        # Validate and filter candidates
        validated_insights = []
        for candidate in candidates:
            if self._validate_insight_candidate(candidate):
                insight = self._create_emergent_insight(candidate)
                validated_insights.append(insight)
        
        self.logger.info(f"Detected {len(validated_insights)} emergent insights")
        return validated_insights
    
    def _generate_insight_candidates(
        self,
        consensus_result: str,
        source_positions: list[str],
        contributing_agents: list[str],
        context: Optional[dict[str, Any]] = None
    ) -> list[InsightCandidate]:
        """Generate insight candidates."""
        candidates = []
        
        # Detect synthesis emergence
        synthesis_candidates = self._detect_synthesis_emergence(
            consensus_result, source_positions, contributing_agents
        )
        candidates.extend(synthesis_candidates)
        
        # Detect contradiction resolution
        resolution_candidates = self._detect_contradiction_resolution(
            consensus_result, source_positions, contributing_agents
        )
        candidates.extend(resolution_candidates)
        
        # Detect novel concept creation
        concept_candidates = self._detect_novel_concept_creation(
            consensus_result, source_positions, contributing_agents
        )
        candidates.extend(concept_candidates)
        
        # Detect pattern discovery
        pattern_candidates = self._detect_pattern_discovery(
            consensus_result, source_positions, contributing_agents
        )
        candidates.extend(pattern_candidates)
        
        return candidates
    
    def _detect_synthesis_emergence(
        self,
        consensus_result: str,
        source_positions: list[str],
        contributing_agents: list[str]
    ) -> list[InsightCandidate]:
        """Detect synthesis emergence insights."""
        candidates = []
        
        # Calculate novelty score
        novelty_score = self.novelty_detector.calculate_novelty_score(
            consensus_result, source_positions
        )
        
        # Calculate coherence score
        coherence_score = self.coherence_analyzer.calculate_coherence_score(
            consensus_result, source_positions
        )
        
        # Check for synthesis patterns
        if novelty_score > 0.3 and coherence_score > 0.4:
            # Determine emergence pattern
            emergence_pattern = self._determine_emergence_pattern(
                consensus_result, source_positions
            )
            
            # Calculate emergence score
            emergence_score = self._calculate_emergence_score(
                consensus_result, source_positions, emergence_pattern
            )
            
            if emergence_score > 0.5:
                candidate = InsightCandidate(
                    content=f"Synthesis insight: {consensus_result}",
                    insight_type=InsightType.SYNTHESIS_EMERGENCE,
                    emergence_pattern=emergence_pattern,
                    emergence_score=emergence_score,
                    contributing_agents=contributing_agents,
                    source_positions=source_positions,
                    novelty_score=novelty_score,
                    coherence_score=coherence_score,
                    evidence_strength=self._calculate_evidence_strength(
                        consensus_result, source_positions
                    )
                )
                candidates.append(candidate)
        
        return candidates
    
    def _detect_contradiction_resolution(
        self,
        consensus_result: str,
        source_positions: list[str],
        contributing_agents: list[str]
    ) -> list[InsightCandidate]:
        """Detect contradiction resolution insights."""
        candidates = []
        
        # Find contradictory positions
        contradictions = self._find_contradictions(source_positions)
        
        if contradictions:
            # Check if consensus resolves contradictions
            resolution_score = self._calculate_resolution_score(
                consensus_result, contradictions
            )
            
            if resolution_score > 0.6:
                candidate = InsightCandidate(
                    content=f"Contradiction resolution: {consensus_result}",
                    insight_type=InsightType.CONTRADICTION_RESOLUTION,
                    emergence_pattern=EmergencePattern.DIALECTICAL,
                    emergence_score=resolution_score,
                    contributing_agents=contributing_agents,
                    source_positions=source_positions,
                    novelty_score=0.7,  # Resolutions are inherently novel
                    coherence_score=self.coherence_analyzer.calculate_coherence_score(
                        consensus_result, source_positions
                    ),
                    evidence_strength=len(contradictions) / len(source_positions)
                )
                candidates.append(candidate)
        
        return candidates
    
    def _detect_novel_concept_creation(
        self,
        consensus_result: str,
        source_positions: list[str],
        contributing_agents: list[str]
    ) -> list[InsightCandidate]:
        """Detect novel concept creation insights."""
        candidates = []
        
        # Detect novel combinations
        novel_combinations = self.novelty_detector.detect_novel_combinations(
            consensus_result, source_positions
        )
        
        for combination, novelty_score in novel_combinations:
            if novelty_score > 0.6:
                candidate = InsightCandidate(
                    content=f"Novel concept: {combination}",
                    insight_type=InsightType.NOVEL_CONCEPT_CREATION,
                    emergence_pattern=EmergencePattern.SYNERGISTIC,
                    emergence_score=novelty_score,
                    contributing_agents=contributing_agents,
                    source_positions=source_positions,
                    novelty_score=novelty_score,
                    coherence_score=0.7,  # Novel concepts may have lower coherence initially
                    evidence_strength=0.5
                )
                candidates.append(candidate)
        
        return candidates
    
    def _detect_pattern_discovery(
        self,
        consensus_result: str,
        source_positions: list[str],
        contributing_agents: list[str]
    ) -> list[InsightCandidate]:
        """Detect pattern discovery insights."""
        candidates = []
        
        # Look for pattern-indicating words
        pattern_indicators = [
            'pattern', 'trend', 'relationship', 'connection', 'correlation',
            'structure', 'framework', 'system', 'principle', 'rule'
        ]
        
        consensus_lower = consensus_result.lower()
        pattern_score = sum(1 for indicator in pattern_indicators if indicator in consensus_lower)
        pattern_score = min(pattern_score / len(pattern_indicators), 1.0)
        
        if pattern_score > 0.3:
            # Extract relationships to validate pattern
            relationships = self.concept_extractor.extract_relationships(consensus_result)
            
            if relationships:
                emergence_score = min(pattern_score + len(relationships) * 0.1, 1.0)
                
                candidate = InsightCandidate(
                    content=f"Pattern discovery: {consensus_result}",
                    insight_type=InsightType.PATTERN_DISCOVERY,
                    emergence_pattern=EmergencePattern.SYNERGISTIC,
                    emergence_score=emergence_score,
                    contributing_agents=contributing_agents,
                    source_positions=source_positions,
                    novelty_score=self.novelty_detector.calculate_novelty_score(
                        consensus_result, source_positions
                    ),
                    coherence_score=self.coherence_analyzer.calculate_coherence_score(
                        consensus_result, source_positions
                    ),
                    evidence_strength=len(relationships) / 10.0  # Normalize by expected max
                )
                candidates.append(candidate)
        
        return candidates
    
    def _determine_emergence_pattern(
        self,
        consensus_result: str,
        source_positions: list[str]
    ) -> EmergencePattern:
        """Determine the pattern of emergence."""
        # Simple heuristics for pattern determination
        consensus_concepts = self.concept_extractor.extract_concepts(consensus_result)
        source_concepts = set()
        
        for position in source_positions:
            source_concepts.update(self.concept_extractor.extract_concepts(position))
        
        # Calculate concept overlap and novelty
        overlap_ratio = len(consensus_concepts & source_concepts) / len(consensus_concepts) if consensus_concepts else 0
        novel_ratio = len(consensus_concepts - source_concepts) / len(consensus_concepts) if consensus_concepts else 0
        
        # Determine pattern based on ratios
        if novel_ratio > 0.7:
            return EmergencePattern.TRANSFORMATIVE
        elif novel_ratio > 0.4:
            return EmergencePattern.SYNERGISTIC
        elif self._has_contradiction_resolution(consensus_result, source_positions):
            return EmergencePattern.DIALECTICAL
        else:
            return EmergencePattern.ADDITIVE
    
    def _has_contradiction_resolution(self, consensus_result: str, source_positions: list[str]) -> bool:
        """Check if consensus resolves contradictions."""
        contradictions = self._find_contradictions(source_positions)
        return len(contradictions) > 0
    
    def _calculate_emergence_score(
        self,
        consensus_result: str,
        source_positions: list[str],
        emergence_pattern: EmergencePattern
    ) -> float:
        """Calculate emergence score."""
        base_score = 0.5
        
        # Pattern-specific scoring
        if emergence_pattern == EmergencePattern.TRANSFORMATIVE:
            base_score = 0.9
        elif emergence_pattern == EmergencePattern.SYNERGISTIC:
            base_score = 0.8
        elif emergence_pattern == EmergencePattern.DIALECTICAL:
            base_score = 0.7
        else:  # ADDITIVE
            base_score = 0.6
        
        # Adjust based on novelty and coherence
        novelty_score = self.novelty_detector.calculate_novelty_score(
            consensus_result, source_positions
        )
        coherence_score = self.coherence_analyzer.calculate_coherence_score(
            consensus_result, source_positions
        )
        
        # Weighted combination
        emergence_score = 0.5 * base_score + 0.3 * novelty_score + 0.2 * coherence_score
        
        return min(emergence_score, 1.0)
    
    def _find_contradictions(self, source_positions: list[str]) -> list[tuple[str, str]]:
        """Find contradictory positions."""
        contradictions = []
        
        # Simple contradiction detection based on opposing keywords
        opposing_pairs = [
            ('agree', 'disagree'), ('support', 'oppose'), ('yes', 'no'),
            ('true', 'false'), ('positive', 'negative'), ('good', 'bad'),
            ('increase', 'decrease'), ('more', 'less'), ('higher', 'lower')
        ]
        
        for i, pos1 in enumerate(source_positions):
            for j, pos2 in enumerate(source_positions[i+1:], i+1):
                pos1_lower = pos1.lower()
                pos2_lower = pos2.lower()
                
                for pair in opposing_pairs:
                    if (pair[0] in pos1_lower and pair[1] in pos2_lower) or \
                       (pair[1] in pos1_lower and pair[0] in pos2_lower):
                        contradictions.append((pos1, pos2))
                        break
        
        return contradictions
    
    def _calculate_resolution_score(
        self,
        consensus_result: str,
        contradictions: list[tuple[str, str]]
    ) -> float:
        """Calculate how well consensus resolves contradictions."""
        if not contradictions:
            return 0.0
        
        resolution_indicators = [
            'balance', 'compromise', 'middle ground', 'synthesis',
            'integration', 'reconcile', 'resolve', 'bridge'
        ]
        
        consensus_lower = consensus_result.lower()
        resolution_score = sum(1 for indicator in resolution_indicators if indicator in consensus_lower)
        resolution_score = min(resolution_score / len(resolution_indicators), 1.0)
        
        # Boost score based on number of contradictions addressed
        contradiction_factor = min(len(contradictions) / 3.0, 1.0)
        
        return min(resolution_score + contradiction_factor * 0.3, 1.0)
    
    def _calculate_evidence_strength(
        self,
        consensus_result: str,
        source_positions: list[str]
    ) -> float:
        """Calculate evidence strength for the insight."""
        # Evidence strength based on source diversity and consensus coherence
        source_diversity = len(set(source_positions)) / len(source_positions) if source_positions else 0
        
        coherence_score = self.coherence_analyzer.calculate_coherence_score(
            consensus_result, source_positions
        )
        
        return (source_diversity + coherence_score) / 2.0
    
    def _validate_insight_candidate(self, candidate: InsightCandidate) -> bool:
        """Validate an insight candidate."""
        # Check thresholds
        if candidate.emergence_score < self.emergence_threshold:
            return False
        
        if candidate.novelty_score < self.novelty_threshold:
            return False
        
        if candidate.coherence_score < self.coherence_threshold:
            return False
        
        if candidate.evidence_strength < self.evidence_threshold:
            return False
        
        return True
    
    def _create_emergent_insight(self, candidate: InsightCandidate) -> EmergentInsight:
        """Create an EmergentInsight from a validated candidate."""
        insight_id = f"{candidate.insight_type.value}_{datetime.now().timestamp()}"
        
        # Calculate validation score
        validation_score = (
            candidate.emergence_score * 0.4 +
            candidate.novelty_score * 0.3 +
            candidate.coherence_score * 0.2 +
            candidate.evidence_strength * 0.1
        )
        
        return EmergentInsight(
            insight_id=insight_id,
            content=candidate.content,
            insight_type=candidate.insight_type,
            emergence_pattern=candidate.emergence_pattern,
            emergence_score=candidate.emergence_score,
            novelty_score=candidate.novelty_score,
            coherence_score=candidate.coherence_score,
            evidence_strength=candidate.evidence_strength,
            contributing_agents=candidate.contributing_agents,
            source_positions=candidate.source_positions,
            synthesis_trace={
                "emergence_pattern": candidate.emergence_pattern.value,
                "detection_method": "automated_analysis",
                "thresholds_met": {
                    "emergence": candidate.emergence_score >= self.emergence_threshold,
                    "novelty": candidate.novelty_score >= self.novelty_threshold,
                    "coherence": candidate.coherence_score >= self.coherence_threshold,
                    "evidence": candidate.evidence_strength >= self.evidence_threshold
                }
            },
            validation_score=validation_score,
            timestamp=datetime.now()
        )
    
    def set_detection_thresholds(
        self,
        emergence_threshold: float = None,
        novelty_threshold: float = None,
        coherence_threshold: float = None,
        evidence_threshold: float = None
    ) -> None:
        """Set detection thresholds."""
        if emergence_threshold is not None:
            self.emergence_threshold = emergence_threshold
        if novelty_threshold is not None:
            self.novelty_threshold = novelty_threshold
        if coherence_threshold is not None:
            self.coherence_threshold = coherence_threshold
        if evidence_threshold is not None:
            self.evidence_threshold = evidence_threshold
        
        self.logger.info(f"Updated detection thresholds: emergence={self.emergence_threshold}, "
                        f"novelty={self.novelty_threshold}, coherence={self.coherence_threshold}, "
                        f"evidence={self.evidence_threshold}")
    
    def get_insight_statistics(self) -> dict[str, Any]:
        """Get statistics about insight detection."""
        return {
            "thresholds": {
                "emergence": self.emergence_threshold,
                "novelty": self.novelty_threshold,
                "coherence": self.coherence_threshold,
                "evidence": self.evidence_threshold
            },
            "known_concepts": len(self.novelty_detector.known_concepts),
            "concept_frequencies": len(self.novelty_detector.concept_frequencies)
        }
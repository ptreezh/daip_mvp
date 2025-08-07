"""
@Time: 2025-08-04
@Author: Claude Code
@File: perspective_conflict_detector.py
@Description: Advanced perspective conflict detector for V0.3.6 with multiple detection strategies
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
from collections import defaultdict, deque
import uuid
import re
from concurrent.futures import ThreadPoolExecutor

from .multi_perspective_generator import Perspective, PerspectiveConflict, PerspectiveType

logger = logging.getLogger(__name__)


class ConflictSeverity(Enum):
    """Severity levels for perspective conflicts"""
    LOW = 0.3          # Minor differences, easily resolvable
    MEDIUM = 0.6       # Significant differences requiring attention
    HIGH = 0.8         # Major conflicts that impact synthesis
    CRITICAL = 1.0     # Fundamental contradictions that must be resolved


class ConflictCategory(Enum):
    """Categories of perspective conflicts"""
    SEMANTIC = "semantic"           # Meaning and terminology conflicts
    FACTUAL = "factual"             # Factual claim contradictions
    VALUE_BASED = "value_based"      # Value and priority conflicts
    METHODICAL = "methodical"       # Methodological approach conflicts
    TEMPORAL = "temporal"           # Timeline and timing conflicts
    RESOURCE = "resource"            # Resource allocation conflicts
    STAKEHOLDER = "stakeholder"      # Stakeholder impact conflicts
    SCOPE = "scope"                 # Scope and boundary conflicts


class DetectionStrategy(Enum):
    """Strategies for conflict detection"""
    KEYWORD_BASED = "keyword_based"        # Simple keyword matching
    SEMANTIC_SIMILARITY = "semantic_similarity"  # Advanced semantic analysis
    SENTIMENT_ANALYSIS = "sentiment_analysis"    # Sentiment contradiction
    FACT_EXTRACTION = "fact_extraction"          # Fact consistency checking
    LOGICAL_CONTRADICTION = "logical_contradiction"  # Logic-based contradiction
    CONTEXTUAL_ANALYSIS = "contextual_analysis"    # Context-aware conflict detection


@dataclass
class ConflictPattern:
    """Represents a conflict pattern for detection"""
    pattern_id: str
    name: str
    description: str
    category: ConflictCategory
    detection_strategy: DetectionStrategy
    keywords: List[str]
    antonyms: List[str]
    severity_range: Tuple[float, float]
    context_rules: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert pattern to dictionary"""
        return {
            'pattern_id': self.pattern_id,
            'name': self.name,
            'description': self.description,
            'category': self.category.value,
            'detection_strategy': self.detection_strategy.value,
            'keywords': self.keywords,
            'antonyms': self.antonyms,
            'severity_range': self.severity_range,
            'context_rules': self.context_rules
        }


@dataclass
class ConflictEvidence:
    """Evidence supporting a conflict detection"""
    evidence_id: str
    conflict_id: str
    evidence_type: str
    content: str
    source_perspective: str
    confidence: float
    location: Dict[str, Any]  # Position in text
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert evidence to dictionary"""
        return {
            'evidence_id': self.evidence_id,
            'conflict_id': self.conflict_id,
            'evidence_type': self.evidence_type,
            'content': self.content,
            'source_perspective': self.source_perspective,
            'confidence': self.confidence,
            'location': self.location,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class ConflictDetectionResult:
    """Result of conflict detection analysis"""
    analysis_id: str
    perspective_count: int
    conflicts_detected: List[PerspectiveConflict]
    evidence_collected: List[ConflictEvidence]
    detection_time: float
    strategies_used: List[DetectionStrategy]
    confidence_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            'analysis_id': self.analysis_id,
            'perspective_count': self.perspective_count,
            'conflicts_detected': [c.to_dict() for c in self.conflicts_detected],
            'evidence_collected': [e.to_dict() for e in self.evidence_collected],
            'detection_time': self.detection_time,
            'strategies_used': [s.value for s in self.strategies_used],
            'confidence_score': self.confidence_score,
            'metadata': self.metadata
        }


class PerspectiveConflictDetector:
    """
    Advanced perspective conflict detector with multiple detection strategies
    Identifies and categorizes conflicts between different perspectives
    """
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        
        # Conflict patterns
        self.conflict_patterns: Dict[str, ConflictPattern] = {}
        self._initialize_conflict_patterns()
        
        # Detection strategies
        self.detection_strategies: Dict[DetectionStrategy, Callable] = {}
        self._initialize_detection_strategies()
        
        # Performance tracking
        self.detection_times: Dict[str, List[float]] = defaultdict(list)
        self.conflict_statistics: Dict[str, Dict] = defaultdict(dict)
        
        # Graceful degradation settings
        self.max_detection_time = 30.0  # seconds per strategy
        self.fallback_threshold = 0.3
        
        # Background processing
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._running = False
        self._lock = threading.Lock()
        
        # Configuration
        self.min_confidence_threshold = 0.5
        self.max_evidence_per_conflict = 5
        
    async def start(self) -> None:
        """Start the conflict detector"""
        self._running = True
        logger.info("Perspective conflict detector started")
        
    async def stop(self) -> None:
        """Stop the conflict detector"""
        self._running = False
        self.executor.shutdown(wait=True)
        logger.info("Perspective conflict detector stopped")
        
    async def detect_conflicts(self,
                              perspectives: List[Perspective],
                              strategies: List[DetectionStrategy] = None) -> ConflictDetectionResult:
        """Detect conflicts using specified strategies"""
        try:
            start_time = time.time()
            
            if len(perspectives) < 2:
                return ConflictDetectionResult(
                    analysis_id=str(uuid.uuid4()),
                    perspective_count=len(perspectives),
                    conflicts_detected=[],
                    evidence_collected=[],
                    detection_time=0.0,
                    strategies_used=[],
                    confidence_score=0.0,
                    metadata={'error': 'Insufficient perspectives for conflict detection'}
                )
                
            # Use all strategies if none specified
            detection_strategies = strategies or list(DetectionStrategy)
            
            # Initialize result
            analysis_id = str(uuid.uuid4())
            all_conflicts = []
            all_evidence = []
            
            # Apply each detection strategy
            for strategy in detection_strategies:
                try:
                    strategy_result = await self._apply_detection_strategy(
                        strategy, perspectives, analysis_id
                    )
                    
                    if strategy_result:
                        all_conflicts.extend(strategy_result['conflicts'])
                        all_evidence.extend(strategy_result['evidence'])
                        
                except Exception as e:
                    logger.error(f"Error applying {strategy.value} strategy: {e}")
                    # Graceful degradation: continue with other strategies
                    continue
                    
            # Merge similar conflicts
            merged_conflicts = await self._merge_similar_conflicts(all_conflicts)
            
            # Calculate confidence score
            confidence_score = self._calculate_detection_confidence(
                merged_conflicts, all_evidence, detection_strategies
            )
            
            detection_time = time.time() - start_time
            self.detection_times['conflict_detection'].append(detection_time)
            
            # Update statistics
            self._update_conflict_statistics(merged_conflicts)
            
            result = ConflictDetectionResult(
                analysis_id=analysis_id,
                perspective_count=len(perspectives),
                conflicts_detected=merged_conflicts,
                evidence_collected=all_evidence,
                detection_time=detection_time,
                strategies_used=detection_strategies,
                confidence_score=confidence_score,
                metadata={
                    'strategies_attempted': len(detection_strategies),
                    'strategies_successful': len([s for s in detection_strategies if s in self.detection_strategies]),
                    'total_evidence': len(all_evidence),
                    'unique_conflicts': len(merged_conflicts)
                }
            )
            
            logger.info(f"Detected {len(merged_conflicts)} conflicts in {detection_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error detecting conflicts: {e}")
            # Graceful degradation: return basic result
            return await self._generate_basic_detection_result(perspectives)
            
    async def analyze_conflict_severity(self,
                                       conflict: PerspectiveConflict,
                                       perspectives: List[Perspective]) -> float:
        """Analyze the severity of a specific conflict"""
        try:
            # Get conflicting perspectives
            conflicting_perspectives = [
                p for p in perspectives if p.perspective_id in conflict.perspective_ids
            ]
            
            if len(conflicting_perspectives) != 2:
                return 0.5  # Default severity
                
            persp1, persp2 = conflicting_perspectives
            
            # Analyze severity factors
            severity_factors = []
            
            # 1. Content divergence
            content_divergence = self._calculate_content_divergence(persp1.content, persp2.content)
            severity_factors.append(content_divergence)
            
            # 2. Confidence contradiction
            confidence_diff = abs(persp1.confidence - persp2.confidence)
            severity_factors.append(confidence_diff)
            
            # 3. Weight significance
            weight_factor = (persp1.weight + persp2.weight) / 2
            severity_factors.append(weight_factor)
            
            # 4. Category severity
            category_severity = self._get_category_severity(conflict.conflict_type)
            severity_factors.append(category_severity)
            
            # Calculate weighted severity
            severity = (
                content_divergence * 0.4 +
                confidence_diff * 0.2 +
                weight_factor * 0.2 +
                category_severity * 0.2
            )
            
            return min(max(severity, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error analyzing conflict severity: {e}")
            return 0.5
            
    async def suggest_conflict_resolution(self,
                                         conflict: PerspectiveConflict,
                                         perspectives: List[Perspective]) -> List[str]:
        """Suggest resolution strategies for a conflict"""
        try:
            resolutions = []
            
            # Get conflicting perspectives
            conflicting_perspectives = [
                p for p in perspectives if p.perspective_id in conflict.perspective_ids
            ]
            
            if len(conflicting_perspectives) != 2:
                return ["Unable to suggest resolution: insufficient perspective information"]
                
            persp1, persp2 = conflicting_perspectives
            
            # Category-specific resolutions
            if conflict.conflict_type == "semantic_contradiction":
                resolutions.extend([
                    "Clarify terminology and definitions",
                    "Establish common vocabulary",
                    "Create glossary of terms"
                ])
            elif conflict.conflict_type == "factual_disagreement":
                resolutions.extend([
                    "Verify facts with reliable sources",
                    "Consult subject matter experts",
                    "Conduct additional research"
                ])
            elif conflict.conflict_type == "value_conflict":
                resolutions.extend([
                    "Identify shared values and goals",
                    "Acknowledge different value priorities",
                    "Find compromise solutions"
                ])
            elif conflict.conflict_type == "methodological_disagreement":
                resolutions.extend([
                    "Compare strengths of each approach",
                    "Consider hybrid methodology",
                    "Define decision criteria"
                ])
                
            # General resolutions
            resolutions.extend([
                "Seek additional perspectives to break tie",
                "Use weighted voting based on perspective confidence",
                "Defer decision pending more information"
            ])
            
            return resolutions[:5]  # Top 5 suggestions
            
        except Exception as e:
            logger.error(f"Error suggesting conflict resolution: {e}")
            return ["General conflict resolution approach recommended"]
            
    async def get_conflict_patterns(self,
                                  category: ConflictCategory = None) -> List[Dict[str, Any]]:
        """Get available conflict patterns"""
        try:
            patterns = list(self.conflict_patterns.values())
            
            if category:
                patterns = [p for p in patterns if p.category == category]
                
            return [pattern.to_dict() for pattern in patterns]
            
        except Exception as e:
            logger.error(f"Error getting conflict patterns: {e}")
            return []
            
    async def get_detection_statistics(self) -> Dict[str, Any]:
        """Get detection statistics"""
        try:
            with self._lock:
                total_detections = len(self.detection_times['conflict_detection'])
                avg_detection_time = (
                    sum(self.detection_times['conflict_detection']) / total_detections
                    if total_detections > 0 else 0.0
                )
                
            return {
                'total_detections': total_detections,
                'avg_detection_time': avg_detection_time,
                'available_patterns': len(self.conflict_patterns),
                'available_strategies': len(self.detection_strategies),
                'conflict_statistics': dict(self.conflict_statistics),
                'system_running': self._running
            }
            
        except Exception as e:
            logger.error(f"Error getting detection statistics: {e}")
            return {}
            
    # Private methods for detection strategies
    async def _apply_detection_strategy(self,
                                      strategy: DetectionStrategy,
                                      perspectives: List[Perspective],
                                      analysis_id: str) -> Optional[Dict[str, Any]]:
        """Apply a specific detection strategy"""
        try:
            start_time = time.time()
            
            # Check timeout
            if time.time() - start_time > self.max_detection_time:
                logger.warning(f"Strategy {strategy.value} timeout")
                return None
                
            # Apply strategy
            if strategy in self.detection_strategies:
                conflicts, evidence = await self.detection_strategies[strategy](perspectives, analysis_id)
                
                return {
                    'conflicts': conflicts,
                    'evidence': evidence,
                    'strategy': strategy,
                    'execution_time': time.time() - start_time
                }
                
            return None
            
        except Exception as e:
            logger.error(f"Error applying {strategy.value} strategy: {e}")
            return None
            
    async def _keyword_based_detection(self,
                                     perspectives: List[Perspective],
                                     analysis_id: str) -> Tuple[List[PerspectiveConflict], List[ConflictEvidence]]:
        """Keyword-based conflict detection"""
        try:
            conflicts = []
            evidence = []
            
            # Check each pair of perspectives
            for i, persp1 in enumerate(perspectives):
                for persp2 in perspectives[i+1:]:
                    # Find conflicting keyword pairs
                    keyword_conflicts = await self._find_keyword_conflicts(persp1, persp2)
                    
                    if keyword_conflicts:
                        # Create conflict
                        conflict = PerspectiveConflict(
                            conflict_id=str(uuid.uuid4()),
                            perspective_ids=[persp1.perspective_id, persp2.perspective_id],
                            conflict_type="keyword_contradiction",
                            description=f"Keyword conflicts found: {keyword_conflicts}",
                            severity=len(keyword_conflicts) * 0.2,
                            detected_at=datetime.now(),
                            resolution_suggestions=[
                                "Clarify terminology",
                                "Establish common definitions",
                                "Contextualize keyword usage"
                            ]
                        )
                        conflicts.append(conflict)
                        
                        # Create evidence
                        for keyword_pair in keyword_conflicts[:3]:  # Limit evidence
                            evidence_item = ConflictEvidence(
                                evidence_id=str(uuid.uuid4()),
                                conflict_id=conflict.conflict_id,
                                evidence_type="keyword_contradiction",
                                content=f"Contradictory keywords: {keyword_pair}",
                                source_perspective=f"{persp1.perspective_type.value} vs {persp2.perspective_type.value}",
                                confidence=0.7,
                                location={'type': 'keyword', 'keywords': keyword_pair},
                                timestamp=datetime.now()
                            )
                            evidence.append(evidence_item)
                            
            return conflicts, evidence
            
        except Exception as e:
            logger.error(f"Error in keyword-based detection: {e}")
            return [], []
            
    async def _semantic_similarity_detection(self,
                                           perspectives: List[Perspective],
                                           analysis_id: str) -> Tuple[List[PerspectiveConflict], List[ConflictEvidence]]:
        """Semantic similarity-based conflict detection"""
        try:
            conflicts = []
            evidence = []
            
            # Check each pair of perspectives
            for i, persp1 in enumerate(perspectives):
                for persp2 in perspectives[i+1:]:
                    # Calculate semantic similarity
                    similarity = await self._calculate_semantic_similarity(persp1.content, persp2.content)
                    
                    # Low similarity indicates potential conflict
                    if similarity < 0.3:  # Threshold for conflict
                        severity = 1.0 - similarity
                        
                        conflict = PerspectiveConflict(
                            conflict_id=str(uuid.uuid4()),
                            perspective_ids=[persp1.perspective_id, persp2.perspective_id],
                            conflict_type="semantic_divergence",
                            description=f"Low semantic similarity: {similarity:.2f}",
                            severity=severity,
                            detected_at=datetime.now(),
                            resolution_suggestions=[
                                "Identify common ground",
                                "Bridge semantic gaps",
                                "Find shared concepts"
                            ]
                        )
                        conflicts.append(conflict)
                        
                        # Create evidence
                        evidence_item = ConflictEvidence(
                            evidence_id=str(uuid.uuid4()),
                            conflict_id=conflict.conflict_id,
                            evidence_type="semantic_divergence",
                            content=f"Semantic similarity score: {similarity:.2f}",
                            source_perspective=f"{persp1.perspective_type.value} vs {persp2.perspective_type.value}",
                            confidence=0.8,
                            location={'type': 'semantic', 'similarity': similarity},
                            timestamp=datetime.now()
                        )
                        evidence.append(evidence_item)
                        
            return conflicts, evidence
            
        except Exception as e:
            logger.error(f"Error in semantic similarity detection: {e}")
            return [], []
            
    async def _sentiment_analysis_detection(self,
                                          perspectives: List[Perspective],
                                          analysis_id: str) -> Tuple[List[PerspectiveConflict], List[ConflictEvidence]]:
        """Sentiment analysis-based conflict detection"""
        try:
            conflicts = []
            evidence = []
            
            # Check each pair of perspectives
            for i, persp1 in enumerate(perspectives):
                for persp2 in perspectives[i+1:]:
                    # Analyze sentiment
                    sentiment1 = await self._analyze_sentiment(persp1.content)
                    sentiment2 = await self._analyze_sentiment(persp2.content)
                    
                    # Check for sentiment contradiction
                    if self._is_sentiment_contradiction(sentiment1, sentiment2):
                        severity = abs(sentiment1['score'] - sentiment2['score'])
                        
                        conflict = PerspectiveConflict(
                            conflict_id=str(uuid.uuid4()),
                            perspective_ids=[persp1.perspective_id, persp2.perspective_id],
                            conflict_type="sentiment_contradiction",
                            description=f"Sentiment contradiction: {sentiment1['label']} vs {sentiment2['label']}",
                            severity=severity,
                            detected_at=datetime.now(),
                            resolution_suggestions=[
                                "Acknowledge different emotional responses",
                                "Consider contextual factors",
                                "Balance emotional and rational aspects"
                            ]
                        )
                        conflicts.append(conflict)
                        
                        # Create evidence
                        evidence_item = ConflictEvidence(
                            evidence_id=str(uuid.uuid4()),
                            conflict_id=conflict.conflict_id,
                            evidence_type="sentiment_contradiction",
                            content=f"Sentiment scores: {sentiment1['label']}({sentiment1['score']:.2f}) vs {sentiment2['label']}({sentiment2['score']:.2f})",
                            source_perspective=f"{persp1.perspective_type.value} vs {persp2.perspective_type.value}",
                            confidence=0.6,
                            location={'type': 'sentiment', 'scores': [sentiment1, sentiment2]},
                            timestamp=datetime.now()
                        )
                        evidence.append(evidence_item)
                        
            return conflicts, evidence
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis detection: {e}")
            return [], []
            
    async def _fact_extraction_detection(self,
                                        perspectives: List[Perspective],
                                        analysis_id: str) -> Tuple[List[PerspectiveConflict], List[ConflictEvidence]]:
        """Fact extraction-based conflict detection"""
        try:
            conflicts = []
            evidence = []
            
            # Extract facts from each perspective
            perspective_facts = {}
            for perspective in perspectives:
                facts = await self._extract_facts(perspective.content)
                perspective_facts[perspective.perspective_id] = facts
                
            # Check for factual contradictions
            for i, persp1 in enumerate(perspectives):
                for persp2 in perspectives[i+1:]:
                    facts1 = perspective_facts[persp1.perspective_id]
                    facts2 = perspective_facts[persp2.perspective_id]
                    
                    contradictions = await self._find_factual_contradictions(facts1, facts2)
                    
                    if contradictions:
                        severity = len(contradictions) * 0.3
                        
                        conflict = PerspectiveConflict(
                            conflict_id=str(uuid.uuid4()),
                            perspective_ids=[persp1.perspective_id, persp2.perspective_id],
                            conflict_type="factual_contradiction",
                            description=f"Factual contradictions found: {len(contradictions)}",
                            severity=severity,
                            detected_at=datetime.now(),
                            resolution_suggestions=[
                                "Verify facts with authoritative sources",
                                "Consult domain experts",
                                "Resolve factual discrepancies"
                            ]
                        )
                        conflicts.append(conflict)
                        
                        # Create evidence
                        for contradiction in contradictions[:2]:
                            evidence_item = ConflictEvidence(
                                evidence_id=str(uuid.uuid4()),
                                conflict_id=conflict.conflict_id,
                                evidence_type="factual_contradiction",
                                content=f"Factual contradiction: {contradiction}",
                                source_perspective=f"{persp1.perspective_type.value} vs {persp2.perspective_type.value}",
                                confidence=0.8,
                                location={'type': 'factual', 'contradiction': contradiction},
                                timestamp=datetime.now()
                            )
                            evidence.append(evidence_item)
                            
            return conflicts, evidence
            
        except Exception as e:
            logger.error(f"Error in fact extraction detection: {e}")
            return [], []
            
    async def _logical_contradiction_detection(self,
                                              perspectives: List[Perspective],
                                              analysis_id: str) -> Tuple[List[PerspectiveConflict], List[ConflictEvidence]]:
        """Logical contradiction detection"""
        try:
            conflicts = []
            evidence = []
            
            # Check each pair of perspectives
            for i, persp1 in enumerate(perspectives):
                for persp2 in perspectives[i+1:]:
                    # Check for logical contradictions
                    contradictions = await self._find_logical_contradictions(persp1.content, persp2.content)
                    
                    if contradictions:
                        severity = len(contradictions) * 0.4
                        
                        conflict = PerspectiveConflict(
                            conflict_id=str(uuid.uuid4()),
                            perspective_ids=[persp1.perspective_id, persp2.perspective_id],
                            conflict_type="logical_contradiction",
                            description=f"Logical contradictions found: {len(contradictions)}",
                            severity=severity,
                            detected_at=datetime.now(),
                            resolution_suggestions=[
                                "Examine logical premises",
                                "Check for hidden assumptions",
                                "Resolve logical inconsistencies"
                            ]
                        )
                        conflicts.append(conflict)
                        
                        # Create evidence
                        for contradiction in contradictions[:2]:
                            evidence_item = ConflictEvidence(
                                evidence_id=str(uuid.uuid4()),
                                conflict_id=conflict.conflict_id,
                                evidence_type="logical_contradiction",
                                content=f"Logical contradiction: {contradiction}",
                                source_perspective=f"{persp1.perspective_type.value} vs {persp2.perspective_type.value}",
                                confidence=0.9,
                                location={'type': 'logical', 'contradiction': contradiction},
                                timestamp=datetime.now()
                            )
                            evidence.append(evidence_item)
                            
            return conflicts, evidence
            
        except Exception as e:
            logger.error(f"Error in logical contradiction detection: {e}")
            return [], []
            
    async def _contextual_analysis_detection(self,
                                           perspectives: List[Perspective],
                                           analysis_id: str) -> Tuple[List[PerspectiveConflict], List[ConflictEvidence]]:
        """Contextual analysis-based conflict detection"""
        try:
            conflicts = []
            evidence = []
            
            # Analyze contextual factors
            for i, persp1 in enumerate(perspectives):
                for persp2 in perspectives[i+1:]:
                    # Check contextual conflicts
                    contextual_conflicts = await self._analyze_contextual_conflicts(persp1, persp2)
                    
                    if contextual_conflicts:
                        severity = sum(c['severity'] for c in contextual_conflicts) / len(contextual_conflicts)
                        
                        conflict = PerspectiveConflict(
                            conflict_id=str(uuid.uuid4()),
                            perspective_ids=[persp1.perspective_id, persp2.perspective_id],
                            conflict_type="contextual_conflict",
                            description=f"Contextual conflicts found: {len(contextual_conflicts)}",
                            severity=severity,
                            detected_at=datetime.now(),
                            resolution_suggestions=[
                                "Consider different contexts",
                                "Acknowledge contextual factors",
                                "Adapt to specific scenarios"
                            ]
                        )
                        conflicts.append(conflict)
                        
                        # Create evidence
                        for ctx_conflict in contextual_conflicts[:2]:
                            evidence_item = ConflictEvidence(
                                evidence_id=str(uuid.uuid4()),
                                conflict_id=conflict.conflict_id,
                                evidence_type="contextual_conflict",
                                content=f"Contextual conflict: {ctx_conflict['description']}",
                                source_perspective=f"{persp1.perspective_type.value} vs {persp2.perspective_type.value}",
                                confidence=ctx_conflict['confidence'],
                                location={'type': 'contextual', 'factors': ctx_conflict['factors']},
                                timestamp=datetime.now()
                            )
                            evidence.append(evidence_item)
                            
            return conflicts, evidence
            
        except Exception as e:
            logger.error(f"Error in contextual analysis detection: {e}")
            return [], []
            
    # Helper methods
    async def _find_keyword_conflicts(self,
                                    persp1: Perspective,
                                    persp2: Perspective) -> List[Tuple[str, str]]:
        """Find conflicting keyword pairs between perspectives"""
        try:
            conflicts = []
            
            # Define antonym pairs
            antonym_pairs = [
                ('effective', 'ineffective'),
                ('beneficial', 'harmful'),
                ('necessary', 'unnecessary'),
                ('appropriate', 'inappropriate'),
                ('successful', 'unsuccessful'),
                ('efficient', 'inefficient'),
                ('reliable', 'unreliable'),
                ('sustainable', 'unsustainable'),
                ('ethical', 'unethical'),
                ('legal', 'illegal')
            ]
            
            content1 = persp1.content.lower()
            content2 = persp2.content.lower()
            
            # Check for antonym pairs
            for word1, word2 in antonym_pairs:
                if (word1 in content1 and word2 in content2) or \
                   (word2 in content1 and word1 in content2):
                    conflicts.append((word1, word2))
                    
            return conflicts
            
        except Exception as e:
            logger.error(f"Error finding keyword conflicts: {e}")
            return []
            
    async def _calculate_semantic_similarity(self,
                                           content1: str,
                                           content2: str) -> float:
        """Calculate semantic similarity between two contents"""
        try:
            # Simple word-based similarity (would use embeddings in production)
            words1 = set(content1.lower().split())
            words2 = set(content2.lower().split())
            
            if not words1 or not words2:
                return 0.0
                
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            # Jaccard similarity
            similarity = len(intersection) / len(union) if union else 0.0
            
            return similarity
            
        except Exception as e:
            logger.error(f"Error calculating semantic similarity: {e}")
            return 0.5
            
    async def _analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """Analyze sentiment of content"""
        try:
            # Simple sentiment analysis (would use NLP model in production)
            positive_words = ['good', 'great', 'excellent', 'beneficial', 'effective', 'successful']
            negative_words = ['bad', 'poor', 'terrible', 'harmful', 'ineffective', 'unsuccessful']
            
            content_lower = content.lower()
            
            positive_count = sum(1 for word in positive_words if word in content_lower)
            negative_count = sum(1 for word in negative_words if word in content_lower)
            
            total_sentiment_words = positive_count + negative_count
            
            if total_sentiment_words == 0:
                return {'label': 'neutral', 'score': 0.0}
                
            sentiment_score = (positive_count - negative_count) / total_sentiment_words
            
            if sentiment_score > 0.1:
                label = 'positive'
            elif sentiment_score < -0.1:
                label = 'negative'
            else:
                label = 'neutral'
                
            return {'label': label, 'score': abs(sentiment_score)}
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {'label': 'neutral', 'score': 0.0}
            
    def _is_sentiment_contradiction(self,
                                   sentiment1: Dict[str, Any],
                                   sentiment2: Dict[str, Any]) -> bool:
        """Check if two sentiments are contradictory"""
        try:
            # Direct contradiction
            if (sentiment1['label'] == 'positive' and sentiment2['label'] == 'negative') or \
               (sentiment1['label'] == 'negative' and sentiment2['label'] == 'positive'):
                return True
                
            # Strong neutral vs strong sentiment
            if (sentiment1['label'] == 'neutral' and sentiment2['score'] > 0.5) or \
               (sentiment2['label'] == 'neutral' and sentiment1['score'] > 0.5):
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error checking sentiment contradiction: {e}")
            return False
            
    async def _extract_facts(self, content: str) -> List[Dict[str, Any]]:
        """Extract facts from content"""
        try:
            # Simple fact extraction (would use NLP in production)
            facts = []
            
            # Look for factual statements
            sentences = content.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 20:  # Minimum length for factual statement
                    # Simple heuristics for factual statements
                    factual_indicators = ['is', 'are', 'was', 'were', 'has', 'have', 'can', 'will', 'should']
                    if any(indicator in sentence.lower() for indicator in factual_indicators):
                        facts.append({
                            'statement': sentence,
                            'confidence': 0.6,
                            'type': 'heuristic'
                        })
                        
            return facts
            
        except Exception as e:
            logger.error(f"Error extracting facts: {e}")
            return []
            
    async def _find_factual_contradictions(self,
                                          facts1: List[Dict[str, Any]],
                                          facts2: List[Dict[str, Any]]) -> List[str]:
        """Find contradictions between fact sets"""
        try:
            contradictions = []
            
            # Simple contradiction detection
            for fact1 in facts1:
                for fact2 in facts2:
                    if self._is_factual_contradiction(fact1['statement'], fact2['statement']):
                        contradictions.append(f"{fact1['statement']} vs {fact2['statement']}")
                        
            return contradictions
            
        except Exception as e:
            logger.error(f"Error finding factual contradictions: {e}")
            return []
            
    def _is_factual_contradiction(self, statement1: str, statement2: str) -> bool:
        """Check if two factual statements contradict"""
        try:
            # Simple contradiction detection
            contradiction_words = [
                ('not', ''), ('no', ''), ('never', ''), ('none', ''),
                ('all', 'some'), ('every', 'some'), ('always', 'sometimes')
            ]
            
            stmt1_lower = statement1.lower()
            stmt2_lower = statement2.lower()
            
            for word1, word2 in contradiction_words:
                if word1 in stmt1_lower and word2 in stmt2_lower:
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error checking factual contradiction: {e}")
            return False
            
    async def _find_logical_contradictions(self,
                                          content1: str,
                                          content2: str) -> List[str]:
        """Find logical contradictions between contents"""
        try:
            contradictions = []
            
            # Look for logical connectors
            logical_patterns = [
                (r'if.*then.*', r'if.*not.*then.*'),
                (r'all.*are.*', r'some.*are not.*'),
                (r'every.*has.*', r'some.*do not have.*'),
                (r'always.*', r'sometimes.*not.*'),
                (r'necessary.*', r'unnecessary.*')
            ]
            
            for pattern1, pattern2 in logical_patterns:
                if (re.search(pattern1, content1, re.IGNORECASE) and 
                    re.search(pattern2, content2, re.IGNORECASE)) or \
                   (re.search(pattern1, content2, re.IGNORECASE) and 
                    re.search(pattern2, content1, re.IGNORECASE)):
                    contradictions.append(f"Logical pattern contradiction: {pattern1} vs {pattern2}")
                    
            return contradictions
            
        except Exception as e:
            logger.error(f"Error finding logical contradictions: {e}")
            return []
            
    async def _analyze_contextual_conflicts(self,
                                          persp1: Perspective,
                                          persp2: Perspective) -> List[Dict[str, Any]]:
        """Analyze contextual conflicts between perspectives"""
        try:
            conflicts = []
            
            # Check perspective type conflicts
            type_conflicts = self._check_perspective_type_conflicts(persp1.perspective_type, persp2.perspective_type)
            conflicts.extend(type_conflicts)
            
            # Check weight conflicts
            if abs(persp1.weight - persp2.weight) > 0.3:
                conflicts.append({
                    'description': 'Significant weight difference',
                    'severity': 0.4,
                    'confidence': 0.7,
                    'factors': ['weight_difference']
                })
                
            # Check confidence conflicts
            if abs(persp1.confidence - persp2.confidence) > 0.4:
                conflicts.append({
                    'description': 'Significant confidence difference',
                    'severity': 0.3,
                    'confidence': 0.6,
                    'factors': ['confidence_difference']
                })
                
            return conflicts
            
        except Exception as e:
            logger.error(f"Error analyzing contextual conflicts: {e}")
            return []
            
    def _check_perspective_type_conflicts(self,
                                         type1: PerspectiveType,
                                         type2: PerspectiveType) -> List[Dict[str, Any]]:
        """Check for perspective type conflicts"""
        try:
            conflicts = []
            
            # Define conflicting perspective type pairs
            conflicting_pairs = [
                (PerspectiveType.BUSINESS, PerspectiveType.ETHICAL),
                (PerspectiveType.FINANCIAL, PerspectiveType.ENVIRONMENTAL),
                (PerspectiveType.TECHNICAL, PerspectiveType.USER_EXPERIENCE),
                (PerspectiveType.LEGAL, PerspectiveType.INNOVATION)
            ]
            
            if (type1, type2) in conflicting_pairs or (type2, type1) in conflicting_pairs:
                conflicts.append({
                    'description': f'Natural tension between {type1.value} and {type2.value} perspectives',
                    'severity': 0.5,
                    'confidence': 0.8,
                    'factors': ['perspective_type_conflict']
                })
                
            return conflicts
            
        except Exception as e:
            logger.error(f"Error checking perspective type conflicts: {e}")
            return []
            
    async def _merge_similar_conflicts(self,
                                      conflicts: List[PerspectiveConflict]) -> List[PerspectiveConflict]:
        """Merge similar conflicts to avoid duplicates"""
        try:
            if not conflicts:
                return []
                
            merged = []
            processed = set()
            
            for i, conflict1 in enumerate(conflicts):
                if i in processed:
                    continue
                    
                # Find similar conflicts
                similar_conflicts = [conflict1]
                for j, conflict2 in enumerate(conflicts[i+1:], i+1):
                    if j in processed:
                        continue
                        
                    if self._are_conflicts_similar(conflict1, conflict2):
                        similar_conflicts.append(conflict2)
                        processed.add(j)
                        
                # Merge conflicts
                if len(similar_conflicts) == 1:
                    merged.append(conflict1)
                else:
                    merged_conflict = await self._merge_conflict_group(similar_conflicts)
                    merged.append(merged_conflict)
                    
                processed.add(i)
                
            return merged
            
        except Exception as e:
            logger.error(f"Error merging similar conflicts: {e}")
            return conflicts
            
    def _are_conflicts_similar(self,
                              conflict1: PerspectiveConflict,
                              conflict2: PerspectiveConflict) -> bool:
        """Check if two conflicts are similar"""
        try:
            # Check conflict type
            if conflict1.conflict_type != conflict2.conflict_type:
                return False
                
            # Check perspective overlap
            perspective_overlap = set(conflict1.perspective_ids) & set(conflict2.perspective_ids)
            if len(perspective_overlap) != 2:
                return False
                
            # Check description similarity
            desc_similarity = self._calculate_text_similarity(
                conflict1.description, conflict2.description
            )
            
            return desc_similarity > 0.7
            
        except Exception as e:
            logger.error(f"Error checking conflict similarity: {e}")
            return False
            
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        try:
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            if not words1 or not words2:
                return 0.0
                
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union) if union else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating text similarity: {e}")
            return 0.0
            
    async def _merge_conflict_group(self,
                                   conflicts: List[PerspectiveConflict]) -> PerspectiveConflict:
        """Merge a group of similar conflicts"""
        try:
            # Use the first conflict as base
            base_conflict = conflicts[0]
            
            # Combine perspective IDs
            all_perspective_ids = set()
            for conflict in conflicts:
                all_perspective_ids.update(conflict.perspective_ids)
                
            # Calculate average severity
            avg_severity = sum(c.severity for c in conflicts) / len(conflicts)
            
            # Combine resolution suggestions
            all_suggestions = set()
            for conflict in conflicts:
                all_suggestions.update(conflict.resolution_suggestions)
                
            # Create merged conflict
            merged_conflict = PerspectiveConflict(
                conflict_id=str(uuid.uuid4()),
                perspective_ids=list(all_perspective_ids),
                conflict_type=base_conflict.conflict_type,
                description=f"Merged conflict: {base_conflict.description}",
                severity=avg_severity,
                detected_at=datetime.now(),
                resolution_suggestions=list(all_suggestions)
            )
            
            return merged_conflict
            
        except Exception as e:
            logger.error(f"Error merging conflict group: {e}")
            return conflicts[0]
            
    def _calculate_detection_confidence(self,
                                       conflicts: List[PerspectiveConflict],
                                       evidence: List[ConflictEvidence],
                                       strategies: List[DetectionStrategy]) -> float:
        """Calculate confidence score for detection result"""
        try:
            if not conflicts:
                return 0.0
                
            # Base confidence from evidence
            evidence_confidence = sum(e.confidence for e in evidence) / len(evidence) if evidence else 0.5
            
            # Strategy diversity factor
            strategy_diversity = len(strategies) / len(DetectionStrategy)
            
            # Conflict severity factor
            avg_severity = sum(c.severity for c in conflicts) / len(conflicts)
            
            # Calculate final confidence
            confidence = (
                evidence_confidence * 0.5 +
                strategy_diversity * 0.3 +
                avg_severity * 0.2
            )
            
            return min(max(confidence, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating detection confidence: {e}")
            return 0.5
            
    def _calculate_content_divergence(self,
                                    content1: str,
                                    content2: str) -> float:
        """Calculate content divergence between two perspectives"""
        try:
            # Simple divergence calculation
            words1 = set(content1.lower().split())
            words2 = set(content2.lower().split())
            
            if not words1 or not words2:
                return 1.0
                
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            similarity = len(intersection) / len(union) if union else 0.0
            divergence = 1.0 - similarity
            
            return divergence
            
        except Exception as e:
            logger.error(f"Error calculating content divergence: {e}")
            return 0.5
            
    def _get_category_severity(self, category: str) -> float:
        """Get severity weight for conflict category"""
        try:
            severity_weights = {
                'semantic_contradiction': 0.7,
                'factual_disagreement': 0.8,
                'value_conflict': 0.9,
                'methodological_disagreement': 0.6,
                'sentiment_contradiction': 0.4,
                'logical_contradiction': 0.9,
                'contextual_conflict': 0.5,
                'keyword_contradiction': 0.3
            }
            
            return severity_weights.get(category, 0.5)
            
        except Exception as e:
            logger.error(f"Error getting category severity: {e}")
            return 0.5
            
    def _update_conflict_statistics(self, conflicts: List[PerspectiveConflict]) -> None:
        """Update conflict statistics"""
        try:
            for conflict in conflicts:
                conflict_type = conflict.conflict_type
                if conflict_type not in self.conflict_statistics:
                    self.conflict_statistics[conflict_type] = {
                        'count': 0,
                        'avg_severity': 0.0,
                        'total_severity': 0.0
                    }
                    
                stats = self.conflict_statistics[conflict_type]
                stats['count'] += 1
                stats['total_severity'] += conflict.severity
                stats['avg_severity'] = stats['total_severity'] / stats['count']
                
        except Exception as e:
            logger.error(f"Error updating conflict statistics: {e}")
            
    async def _generate_basic_detection_result(self,
                                             perspectives: List[Perspective]) -> ConflictDetectionResult:
        """Generate basic detection result for graceful degradation"""
        try:
            return ConflictDetectionResult(
                analysis_id=str(uuid.uuid4()),
                perspective_count=len(perspectives),
                conflicts_detected=[],
                evidence_collected=[],
                detection_time=0.0,
                strategies_used=[],
                confidence_score=0.0,
                metadata={'fallback': True, 'error': 'Detection failed'}
            )
            
        except Exception as e:
            logger.error(f"Error generating basic detection result: {e}")
            raise
            
    def _initialize_conflict_patterns(self) -> None:
        """Initialize conflict detection patterns"""
        try:
            # Semantic conflict patterns
            self.conflict_patterns['semantic_1'] = ConflictPattern(
                pattern_id='semantic_1',
                name='Terminology Conflict',
                description='Conflicting terminology and definitions',
                category=ConflictCategory.SEMANTIC,
                detection_strategy=DetectionStrategy.KEYWORD_BASED,
                keywords=['definition', 'meaning', 'concept', 'term'],
                antonyms=['different', 'contradictory', 'opposing'],
                severity_range=(0.3, 0.7),
                context_rules={'domain_specific': True}
            )
            
            # Factual conflict patterns
            self.conflict_patterns['factual_1'] = ConflictPattern(
                pattern_id='factual_1',
                name='Factual Disagreement',
                description='Contradictory factual claims',
                category=ConflictCategory.FACTUAL,
                detection_strategy=DetectionStrategy.FACT_EXTRACTION,
                keywords=['fact', 'data', 'evidence', 'research'],
                antonyms=['contradicts', 'disproves', 'refutes'],
                severity_range=(0.5, 0.9),
                context_rules={'verifiable': True}
            )
            
            # Value conflict patterns
            self.conflict_patterns['value_1'] = ConflictPattern(
                pattern_id='value_1',
                name='Value Priority Conflict',
                description='Different value priorities and preferences',
                category=ConflictCategory.VALUE_BASED,
                detection_strategy=DetectionStrategy.SENTIMENT_ANALYSIS,
                keywords=['important', 'priority', 'value', 'preference'],
                antonyms=['unimportant', 'secondary', 'low_priority'],
                severity_range=(0.4, 0.8),
                context_rules={'subjective': True}
            )
            
            logger.info(f"Initialized {len(self.conflict_patterns)} conflict patterns")
            
        except Exception as e:
            logger.error(f"Error initializing conflict patterns: {e}")
            
    def _initialize_detection_strategies(self) -> None:
        """Initialize detection strategies"""
        try:
            self.detection_strategies[DetectionStrategy.KEYWORD_BASED] = self._keyword_based_detection
            self.detection_strategies[DetectionStrategy.SEMANTIC_SIMILARITY] = self._semantic_similarity_detection
            self.detection_strategies[DetectionStrategy.SENTIMENT_ANALYSIS] = self._sentiment_analysis_detection
            self.detection_strategies[DetectionStrategy.FACT_EXTRACTION] = self._fact_extraction_detection
            self.detection_strategies[DetectionStrategy.LOGICAL_CONTRADICTION] = self._logical_contradiction_detection
            self.detection_strategies[DetectionStrategy.CONTEXTUAL_ANALYSIS] = self._contextual_analysis_detection
            
            logger.info(f"Initialized {len(self.detection_strategies)} detection strategies")
            
        except Exception as e:
            logger.error(f"Error initializing detection strategies: {e}"


# Singleton instance for global use
perspective_conflict_detector = None

def get_perspective_conflict_detector(max_workers: int = 4) -> PerspectiveConflictDetector:
    """Get or create perspective conflict detector instance"""
    global perspective_conflict_detector
    if perspective_conflict_detector is None:
        perspective_conflict_detector = PerspectiveConflictDetector(max_workers)
    return perspective_conflict_detector
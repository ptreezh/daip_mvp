"""@Time: 2025-08-04
@Author: Claude Code
@File: multi_perspective_generator.py
@Description: Multi-perspective intelligent generator for V0.3.6 with graceful degradation
"""

import json
import logging
import threading
import time
import uuid
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from ..core_services.enhanced_sskg_manager import EnhancedSSKGManager
from ..core_services.memory_agent import MemAgent
from ..core_services.smart_reviewer_allocator import SmartReviewerAllocator

logger = logging.getLogger(__name__)


class PerspectiveType(Enum):
    """Types of perspectives for synthesis"""
    TECHNICAL = "technical"           # 技术视角
    BUSINESS = "business"             # 业务视角
    ETHICAL = "ethical"              # 伦理视角
    USER_EXPERIENCE = "user_experience"  # 用户体验视角
    FINANCIAL = "financial"          # 财务视角
    LEGAL = "legal"                 # 法律视角
    ENVIRONMENTAL = "environmental"  # 环境视角
    SOCIAL = "social"               # 社会视角
    INNOVATION = "innovation"       # 创新视角
    RISK = "risk"                   # 风险视角


class PerspectiveWeight(Enum):
    """Weight categories for perspectives"""
    CRITICAL = 1.0      # 关键视角
    HIGH = 0.8          # 高权重
    MEDIUM = 0.6        # 中等权重
    LOW = 0.4           # 低权重
    MINIMAL = 0.2       # 最小权重


class SynthesisStrategy(Enum):
    """Strategies for multi-perspective synthesis"""
    WEIGHTED_AVERAGE = "weighted_average"      # 加权平均
    CONSENSUS_BUILDING = "consensus_building"  # 共识构建
    CONFLICT_RESOLUTION = "conflict_resolution"  # 冲突解决
    HIERARCHICAL = "hierarchical"              # 层次化
    ADAPTIVE = "adaptive"                      # 自适应


@dataclass
class Perspective:
    """Represents a single perspective in the synthesis process"""
    perspective_id: str
    perspective_type: PerspectiveType
    title: str
    description: str
    content: str
    author_id: str
    confidence: float
    weight: float
    created_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)
    related_perspectives: list[str] = field(default_factory=list)
    supporting_evidence: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert perspective to dictionary"""
        return {
            'perspective_id': self.perspective_id,
            'perspective_type': self.perspective_type.value,
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'author_id': self.author_id,
            'confidence': self.confidence,
            'weight': self.weight,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata,
            'related_perspectives': self.related_perspectives,
            'supporting_evidence': self.supporting_evidence
        }


@dataclass
class PerspectiveConflict:
    """Represents a conflict between perspectives"""
    conflict_id: str
    perspective_ids: list[str]
    conflict_type: str
    description: str
    severity: float  # 0.0 to 1.0
    detected_at: datetime
    resolution_suggestions: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert conflict to dictionary"""
        return {
            'conflict_id': self.conflict_id,
            'perspective_ids': self.perspective_ids,
            'conflict_type': self.conflict_type,
            'description': self.description,
            'severity': self.severity,
            'detected_at': self.detected_at.isoformat(),
            'resolution_suggestions': self.resolution_suggestions,
            'metadata': self.metadata
        }


@dataclass
class SynthesisResult:
    """Result of multi-perspective synthesis"""
    synthesis_id: str
    topic: str
    perspectives: list[Perspective]
    conflicts: list[PerspectiveConflict]
    synthesized_content: str
    consensus_score: float
    confidence_score: float
    synthesis_strategy: SynthesisStrategy
    created_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert synthesis result to dictionary"""
        return {
            'synthesis_id': self.synthesis_id,
            'topic': self.topic,
            'perspectives': [p.to_dict() for p in self.perspectives],
            'conflicts': [c.to_dict() for c in self.conflicts],
            'synthesized_content': self.synthesized_content,
            'consensus_score': self.consensus_score,
            'confidence_score': self.confidence_score,
            'synthesis_strategy': self.synthesis_strategy.value,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata
        }


class MultiPerspectiveGenerator:
    """Multi-perspective intelligent generator with graceful degradation
    Generates and synthesizes multiple perspectives on complex topics
    """
    
    def __init__(self, sskg_manager: EnhancedSSKGManager,
                 memory_agent: MemAgent,
                 allocator: SmartReviewerAllocator):
        self.sskg_manager = sskg_manager
        self.memory_agent = memory_agent
        self.allocator = allocator
        
        # Perspective generation
        self.perspective_templates: dict[PerspectiveType, dict[str, Any]] = {}
        self.perspective_weights: dict[PerspectiveType, float] = {}
        self._initialize_perspective_templates()
        
        # Active synthesis sessions
        self.active_syntheses: dict[str, SynthesisResult] = {}
        self.synthesis_history: deque = deque(maxlen=1000)
        
        # Conflict detection
        self.conflict_detectors: dict[str, Callable] = {}
        self.conflict_history: list[PerspectiveConflict] = []
        
        # Performance tracking
        self.generation_times: dict[str, list[float]] = defaultdict(list)
        self.synthesis_times: dict[str, list[float]] = defaultdict(list)
        
        # Graceful degradation settings
        self.max_generation_time = 60.0  # seconds
        self.max_synthesis_time = 120.0  # seconds
        self.fallback_content_length = 500  # characters
        
        # Background processing
        self._running = False
        self._lock = threading.Lock()
        
        # Event handlers
        self.perspective_handlers: dict[str, Callable] = {}
        self.synthesis_handlers: dict[str, Callable] = {}
        
        # Configuration
        self.min_confidence_threshold = 0.6
        self.max_perspectives_per_topic = 10
        self.default_synthesis_strategy = SynthesisStrategy.ADAPTIVE
        
    async def start(self) -> None:
        """Start the multi-perspective generator"""
        self._running = True
        logger.info("Multi-perspective generator started")
        
        # Initialize conflict detectors
        await self._initialize_conflict_detectors()
        
    async def stop(self) -> None:
        """Stop the multi-perspective generator"""
        self._running = False
        logger.info("Multi-perspective generator stopped")
        
    async def generate_perspectives(self,
                                   topic: str,
                                   perspective_types: list[PerspectiveType],
                                   context: dict[str, Any] = None) -> list[Perspective]:
        """Generate multiple perspectives on a topic"""
        try:
            start_time = time.time()
            
            if len(perspective_types) > self.max_perspectives_per_topic:
                logger.warning(f"Too many perspective types requested, limiting to {self.max_perspectives_per_topic}")
                perspective_types = perspective_types[:self.max_perspectives_per_topic]
            
            perspectives = []
            
            # Generate each perspective type
            for perspective_type in perspective_types:
                try:
                    perspective = await self._generate_single_perspective(
                        topic, perspective_type, context or {}
                    )
                    
                    if perspective and perspective.confidence >= self.min_confidence_threshold:
                        perspectives.append(perspective)
                        
                except Exception as e:
                    logger.error(f"Error generating {perspective_type.value} perspective: {e}")
                    # Graceful degradation: continue with other perspectives
                    continue
                    
            # Check timeout
            generation_time = time.time() - start_time
            if generation_time > self.max_generation_time:
                logger.warning(f"Perspective generation timeout: {generation_time:.2f}s")
                # Return partial results
                return perspectives[:len(perspectives)//2]
                
            self.generation_times['perspective_generation'].append(generation_time)
            
            logger.info(f"Generated {len(perspectives)} perspectives in {generation_time:.2f}s")
            return perspectives
            
        except Exception as e:
            logger.error(f"Error generating perspectives: {e}")
            # Graceful degradation: return basic perspectives
            return await self._generate_basic_perspectives(topic, perspective_types)
            
    async def synthesize_perspectives(self,
                                   topic: str,
                                   perspectives: list[Perspective],
                                   strategy: SynthesisStrategy = None) -> SynthesisResult:
        """Synthesize multiple perspectives into a unified result"""
        try:
            start_time = time.time()
            
            if not perspectives:
                raise ValueError("No perspectives provided for synthesis")
                
            # Use default strategy if none specified
            synthesis_strategy = strategy or self.default_synthesis_strategy
            
            # Detect conflicts
            conflicts = await self._detect_perspective_conflicts(perspectives)
            
            # Apply synthesis strategy
            if synthesis_strategy == SynthesisStrategy.WEIGHTED_AVERAGE:
                synthesized_content = await self._weighted_average_synthesis(perspectives)
            elif synthesis_strategy == SynthesisStrategy.CONSENSUS_BUILDING:
                synthesized_content = await self._consensus_building_synthesis(perspectives)
            elif synthesis_strategy == SynthesisStrategy.CONFLICT_RESOLUTION:
                synthesized_content = await self._conflict_resolution_synthesis(perspectives, conflicts)
            elif synthesis_strategy == SynthesisStrategy.HIERARCHICAL:
                synthesized_content = await self._hierarchical_synthesis(perspectives)
            elif synthesis_strategy == SynthesisStrategy.ADAPTIVE:
                synthesized_content = await self._adaptive_synthesis(perspectives, conflicts)
            else:
                synthesized_content = await self._weighted_average_synthesis(perspectives)
                
            # Calculate scores
            consensus_score = self._calculate_consensus_score(perspectives)
            confidence_score = self._calculate_confidence_score(perspectives, synthesized_content)
            
            # Create synthesis result
            synthesis_id = str(uuid.uuid4())
            result = SynthesisResult(
                synthesis_id=synthesis_id,
                topic=topic,
                perspectives=perspectives,
                conflicts=conflicts,
                synthesized_content=synthesized_content,
                consensus_score=consensus_score,
                confidence_score=confidence_score,
                synthesis_strategy=synthesis_strategy,
                created_at=datetime.now(),
                metadata={
                    'perspective_count': len(perspectives),
                    'conflict_count': len(conflicts),
                    'generation_time': time.time() - start_time
                }
            )
            
            # Store result
            with self._lock:
                self.active_syntheses[synthesis_id] = result
                self.synthesis_history.append(result)
                
            synthesis_time = time.time() - start_time
            self.synthesis_times['perspective_synthesis'].append(synthesis_time)
            
            logger.info(f"Synthesized perspectives in {synthesis_time:.2f}s (consensus: {consensus_score:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Error synthesizing perspectives: {e}")
            # Graceful degradation: return basic synthesis
            return await self._generate_basic_synthesis(topic, perspectives)
            
    async def get_perspective_suggestions(self,
                                       topic: str,
                                       existing_perspectives: list[Perspective] = None) -> list[PerspectiveType]:
        """Suggest relevant perspective types for a topic"""
        try:
            suggestions = []
            
            # Analyze topic keywords
            topic_keywords = self._extract_keywords(topic)
            
            # Match perspective types based on keywords
            for perspective_type in PerspectiveType:
                relevance_score = self._calculate_perspective_relevance(
                    topic_keywords, perspective_type
                )
                
                if relevance_score > 0.5:  # Minimum relevance threshold
                    suggestions.append((perspective_type, relevance_score))
                    
            # Remove existing perspectives
            if existing_perspectives:
                existing_types = {p.perspective_type for p in existing_perspectives}
                suggestions = [
                    (ptype, score) for ptype, score in suggestions
                    if ptype not in existing_types
                ]
                
            # Sort by relevance and return
            suggestions.sort(key=lambda x: x[1], reverse=True)
            
            return [ptype for ptype, _ in suggestions[:5]]  # Top 5 suggestions
            
        except Exception as e:
            logger.error(f"Error getting perspective suggestions: {e}")
            # Return default suggestions
            return [PerspectiveType.TECHNICAL, PerspectiveType.BUSINESS]
            
    async def get_synthesis_history(self,
                                  limit: int = 50,
                                  perspective_type: PerspectiveType = None) -> list[dict[str, Any]]:
        """Get synthesis history with optional filtering"""
        try:
            with self._lock:
                history = list(self.synthesis_history)
                
            # Filter by perspective type if specified
            if perspective_type:
                history = [
                    result for result in history
                    if any(p.perspective_type == perspective_type for p in result.perspectives)
                ]
                
            # Convert to dictionaries and limit
            history_dicts = [result.to_dict() for result in history[-limit:]]
            
            return history_dicts
            
        except Exception as e:
            logger.error(f"Error getting synthesis history: {e}")
            return []
            
    async def get_system_stats(self) -> dict[str, Any]:
        """Get system statistics"""
        try:
            with self._lock:
                active_syntheses = len(self.active_syntheses)
                history_size = len(self.synthesis_history)
                conflict_count = len(self.conflict_history)
                
            # Calculate average times
            avg_generation_time = (
                sum(self.generation_times['perspective_generation']) / 
                len(self.generation_times['perspective_generation'])
                if self.generation_times['perspective_generation'] else 0.0
            )
            
            avg_synthesis_time = (
                sum(self.synthesis_times['perspective_synthesis']) / 
                len(self.synthesis_times['perspective_synthesis'])
                if self.synthesis_times['perspective_synthesis'] else 0.0
            )
            
            return {
                'active_syntheses': active_syntheses,
                'history_size': history_size,
                'conflict_count': conflict_count,
                'avg_generation_time': avg_generation_time,
                'avg_synthesis_time': avg_synthesis_time,
                'available_perspective_types': len(PerspectiveType),
                'system_running': self._running,
                'min_confidence_threshold': self.min_confidence_threshold
            }
            
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {}
            
    # Private methods for perspective generation
    async def _generate_single_perspective(self,
                                         topic: str,
                                         perspective_type: PerspectiveType,
                                         context: dict[str, Any]) -> Optional[Perspective]:
        """Generate a single perspective"""
        try:
            # Get perspective template
            template = self.perspective_templates.get(perspective_type)
            if not template:
                logger.warning(f"No template found for {perspective_type.value}")
                return None
                
            # Get relevant knowledge from SSKG
            knowledge = await self._get_relevant_knowledge(topic, perspective_type)
            
            # Generate perspective content
            content = await self._generate_perspective_content(
                topic, perspective_type, template, knowledge, context
            )
            
            # Calculate confidence
            confidence = self._calculate_perspective_confidence(
                content, knowledge, perspective_type
            )
            
            # Get weight
            weight = self.perspective_weights.get(perspective_type, 0.5)
            
            # Create perspective
            perspective = Perspective(
                perspective_id=str(uuid.uuid4()),
                perspective_type=perspective_type,
                title=f"{perspective_type.value.title()} Perspective on {topic}",
                description=template.get('description', ''),
                content=content,
                author_id='system',
                confidence=confidence,
                weight=weight,
                created_at=datetime.now(),
                metadata={
                    'knowledge_sources': len(knowledge),
                    'template_used': template.get('name', 'default'),
                    'context': context
                }
            )
            
            return perspective
            
        except Exception as e:
            logger.error(f"Error generating {perspective_type.value} perspective: {e}")
            return None
            
    async def _get_relevant_knowledge(self,
                                    topic: str,
                                    perspective_type: PerspectiveType) -> list[dict[str, Any]]:
        """Get relevant knowledge from SSKG for perspective generation"""
        try:
            # Query SSKG for relevant knowledge
            query = f"{topic} {perspective_type.value}"
            
            # This would integrate with the actual SSKG manager
            # For now, return mock knowledge
            return [
                {
                    'id': f'knowledge_{i}',
                    'content': f'Relevant knowledge about {topic} from {perspective_type.value} perspective',
                    'source': 'sskg',
                    'relevance_score': 0.8 - (i * 0.1)
                }
                for i in range(3)
            ]
            
        except Exception as e:
            logger.error(f"Error getting relevant knowledge: {e}")
            return []
            
    async def _generate_perspective_content(self,
                                         topic: str,
                                         perspective_type: PerspectiveType,
                                         template: dict[str, Any],
                                         knowledge: list[dict[str, Any]],
                                         context: dict[str, Any]) -> str:
        """Generate perspective content using template and knowledge"""
        try:
            # Build prompt using template
            prompt_template = template.get('prompt_template', '')
            
            # Format prompt with topic and knowledge
            knowledge_text = '\n'.join([k['content'] for k in knowledge])
            
            prompt = prompt_template.format(
                topic=topic,
                knowledge=knowledge_text,
                context=json.dumps(context, indent=2)
            )
            
            # In a real implementation, this would use LLM to generate content
            # For now, generate template-based content
            content = f"""
## {perspective_type.value.title()} Perspective on {topic}

### Analysis Framework
Using {template.get('name', 'standard')} analysis framework for {perspective_type.value} evaluation.

### Key Considerations
{template.get('key_considerations', 'Standard considerations apply.')}

### Relevant Knowledge
{knowledge_text}

### Context Integration
Considering the provided context: {context.get('domain', 'general domain')}.

### Perspective Summary
This {perspective_type.value} perspective provides insights into {topic} 
from the viewpoint of {template.get('viewpoint', 'standard analysis')}.
"""
            
            return content.strip()
            
        except Exception as e:
            logger.error(f"Error generating perspective content: {e}")
            return f"Error generating {perspective_type.value} perspective content."
            
    def _calculate_perspective_confidence(self,
                                        content: str,
                                        knowledge: list[dict[str, Any]],
                                        perspective_type: PerspectiveType) -> float:
        """Calculate confidence score for a perspective"""
        try:
            # Base confidence from knowledge quality
            knowledge_confidence = sum(k.get('relevance_score', 0.5) for k in knowledge) / len(knowledge) if knowledge else 0.5
            
            # Content length factor
            length_factor = min(len(content) / 1000, 1.0)  # Normalize to 1000 characters
            
            # Perspective type confidence adjustment
            type_confidence = {
                PerspectiveType.TECHNICAL: 0.9,
                PerspectiveType.BUSINESS: 0.8,
                PerspectiveType.ETHICAL: 0.7,
                PerspectiveType.USER_EXPERIENCE: 0.8,
                PerspectiveType.FINANCIAL: 0.8,
                PerspectiveType.LEGAL: 0.9,
                PerspectiveType.ENVIRONMENTAL: 0.7,
                PerspectiveType.SOCIAL: 0.7,
                PerspectiveType.INNOVATION: 0.6,
                PerspectiveType.RISK: 0.8
            }.get(perspective_type, 0.7)
            
            # Calculate final confidence
            confidence = (knowledge_confidence * 0.4 + length_factor * 0.3 + type_confidence * 0.3)
            
            return min(max(confidence, 0.0), 1.0)  # Clamp to [0, 1]
            
        except Exception as e:
            logger.error(f"Error calculating perspective confidence: {e}")
            return 0.5
            
    # Private methods for synthesis
    async def _detect_perspective_conflicts(self,
                                           perspectives: list[Perspective]) -> list[PerspectiveConflict]:
        """Detect conflicts between perspectives"""
        try:
            conflicts = []
            
            # Check each pair of perspectives
            for i, persp1 in enumerate(perspectives):
                for persp2 in perspectives[i+1:]:
                    conflict = await self._check_perspective_conflict(persp1, persp2)
                    if conflict:
                        conflicts.append(conflict)
                        
            return conflicts
            
        except Exception as e:
            logger.error(f"Error detecting perspective conflicts: {e}")
            return []
            
    async def _check_perspective_conflict(self,
                                        persp1: Perspective,
                                        persp2: Perspective) -> Optional[PerspectiveConflict]:
        """Check for conflict between two perspectives"""
        try:
            # Simple conflict detection based on content analysis
            # In a real implementation, this would use more sophisticated NLP
            
            content1 = persp1.content.lower()
            content2 = persp2.content.lower()
            
            # Check for contradictory keywords
            contradiction_pairs = [
                ('should', 'should not'),
                ('necessary', 'unnecessary'),
                ('beneficial', 'harmful'),
                ('effective', 'ineffective'),
                ('appropriate', 'inappropriate')
            ]
            
            contradictions = []
            for pos_word, neg_word in contradiction_pairs:
                if (pos_word in content1 and neg_word in content2) or \
                   (neg_word in content1 and pos_word in content2):
                    contradictions.append((pos_word, neg_word))
                    
            if contradictions:
                return PerspectiveConflict(
                    conflict_id=str(uuid.uuid4()),
                    perspective_ids=[persp1.perspective_id, persp2.perspective_id],
                    conflict_type="semantic_contradiction",
                    description=f"Contradictory terms found: {contradictions}",
                    severity=len(contradictions) * 0.2,  # Severity based on number of contradictions
                    detected_at=datetime.now(),
                    resolution_suggestions=[
                        "Analyze the context of each contradictory statement",
                        "Consider if both perspectives can be valid in different contexts",
                        "Seek additional information to resolve the contradiction"
                    ]
                )
                
            return None
            
        except Exception as e:
            logger.error(f"Error checking perspective conflict: {e}")
            return None
            
    async def _weighted_average_synthesis(self, perspectives: list[Perspective]) -> str:
        """Synthesize using weighted average approach"""
        try:
            # Calculate total weight
            total_weight = sum(p.weight for p in perspectives)
            
            if total_weight == 0:
                return "No valid perspectives for synthesis."
                
            # Generate weighted synthesis
            synthesis_parts = []
            
            for perspective in perspectives:
                weight_ratio = perspective.weight / total_weight
                section = f"""
### {perspective.title} (Weight: {weight_ratio:.2f})
{perspective.content}

Confidence: {perspective.confidence:.2f}
"""
                synthesis_parts.append(section)
                
            synthesis = f"""# Multi-Perspective Synthesis

This synthesis combines {len(perspectives)} perspectives using weighted averaging based on perspective confidence and relevance.

## Individual Perspectives

{"".join(synthesis_parts)}

## Synthesis Summary
The perspectives above provide complementary insights into the topic. Each perspective contributes according to its calculated weight and confidence.
"""
            
            return synthesis
            
        except Exception as e:
            logger.error(f"Error in weighted average synthesis: {e}")
            return "Error in weighted average synthesis."
            
    async def _consensus_building_synthesis(self, perspectives: list[Perspective]) -> str:
        """Synthesize using consensus building approach"""
        try:
            # Find common themes
            common_themes = await self._extract_common_themes(perspectives)
            
            # Identify areas of agreement
            agreements = await self._identify_agreements(perspectives)
            
            # Generate consensus synthesis
            synthesis = f"""# Consensus-Based Synthesis

This synthesis builds consensus among {len(perspectives)} perspectives by identifying common ground and areas of agreement.

## Common Themes
{chr(10).join(f"- {theme}" for theme in common_themes)}

## Areas of Agreement
{chr(10).join(f"- {agreement}" for agreement in agreements)}

## Consensus Summary
Based on the analysis of all perspectives, the following consensus emerges:

The perspectives share significant common ground on key aspects of the topic. While individual viewpoints may differ in emphasis or approach, there is substantial agreement on fundamental principles and conclusions.

## Diverse Insights
Beyond the consensus, each perspective brings unique insights:
"""
            
            for perspective in perspectives:
                synthesis += f"""
- **{perspective.perspective_type.value.title()}**: {perspective.description}
"""
                
            return synthesis
            
        except Exception as e:
            logger.error(f"Error in consensus building synthesis: {e}")
            return "Error in consensus building synthesis."
            
    async def _conflict_resolution_synthesis(self,
                                           perspectives: list[Perspective],
                                           conflicts: list[PerspectiveConflict]) -> str:
        """Synthesize with explicit conflict resolution"""
        try:
            synthesis = f"""# Conflict-Resolution Synthesis

This synthesis explicitly addresses and resolves conflicts among {len(perspectives)} perspectives.

## Identified Conflicts
"""
            
            for conflict in conflicts:
                synthesis += f"""
### Conflict: {conflict.conflict_type}
- **Severity**: {conflict.severity:.2f}
- **Description**: {conflict.description}
- **Resolution Suggestions**: {', '.join(conflict.resolution_suggestions)}
"""
                
            synthesis += """

## Conflict Resolution
The following resolutions address the identified conflicts:
"""
            
            for conflict in conflicts:
                resolution = await self._generate_conflict_resolution(conflict, perspectives)
                synthesis += f"""
### {conflict.conflict_type.title()} Resolution
{resolution}
"""
                
            synthesis += """

## Integrated Perspective
After resolving conflicts, the integrated perspective emerges:
"""
            
            for perspective in perspectives:
                synthesis += f"""
- **{perspective.perspective_type.value.title()}**: {perspective.description[:100]}...
"""
                
            return synthesis
            
        except Exception as e:
            logger.error(f"Error in conflict resolution synthesis: {e}")
            return "Error in conflict resolution synthesis."
            
    async def _hierarchical_synthesis(self, perspectives: list[Perspective]) -> str:
        """Synthesize using hierarchical approach"""
        try:
            # Sort perspectives by weight (hierarchy)
            sorted_perspectives = sorted(perspectives, key=lambda p: p.weight, reverse=True)
            
            synthesis = f"""# Hierarchical Synthesis

This synthesis organizes {len(perspectives)} perspectives hierarchically based on their relevance and importance.

## Primary Perspective
"""
            
            # Primary perspective (highest weight)
            primary = sorted_perspectives[0]
            synthesis += f"""
### {primary.perspective_type.value.title()} (Primary)
{primary.content}

**Weight**: {primary.weight:.2f}, **Confidence**: {primary.confidence:.2f}
"""
            
            if len(sorted_perspectives) > 1:
                synthesis += "\n## Secondary Perspectives\n"
                
                # Secondary perspectives
                for perspective in sorted_perspectives[1:]:
                    synthesis += f"""
### {perspective.perspective_type.value.title()} (Secondary)
{perspective.content[:500]}...

**Weight**: {perspective.weight:.2f}, **Confidence**: {perspective.confidence:.2f}
"""
                    
            synthesis += """

## Hierarchical Integration
The hierarchical approach gives primary consideration to the most relevant perspective while incorporating valuable insights from secondary viewpoints.
"""
            
            return synthesis
            
        except Exception as e:
            logger.error(f"Error in hierarchical synthesis: {e}")
            return "Error in hierarchical synthesis."
            
    async def _adaptive_synthesis(self,
                                perspectives: list[Perspective],
                                conflicts: list[PerspectiveConflict]) -> str:
        """Synthesize using adaptive approach"""
        try:
            # Choose strategy based on context
            if conflicts:
                # Use conflict resolution if conflicts exist
                return await self._conflict_resolution_synthesis(perspectives, conflicts)
            elif len(perspectives) <= 3:
                # Use consensus building for small groups
                return await self._consensus_building_synthesis(perspectives)
            else:
                # Use hierarchical for larger groups
                return await self._hierarchical_synthesis(perspectives)
                
        except Exception as e:
            logger.error(f"Error in adaptive synthesis: {e}")
            return "Error in adaptive synthesis."
            
    # Helper methods
    def _calculate_consensus_score(self, perspectives: list[Perspective]) -> float:
        """Calculate consensus score among perspectives"""
        try:
            if len(perspectives) <= 1:
                return 1.0
                
            # Simple consensus calculation based on confidence similarity
            confidences = [p.confidence for p in perspectives]
            avg_confidence = sum(confidences) / len(confidences)
            
            # Calculate variance
            variance = sum((c - avg_confidence) ** 2 for c in confidences) / len(confidences)
            
            # Convert variance to consensus score (lower variance = higher consensus)
            consensus = max(0.0, 1.0 - variance)
            
            return consensus
            
        except Exception as e:
            logger.error(f"Error calculating consensus score: {e}")
            return 0.5
            
    def _calculate_confidence_score(self,
                                  perspectives: list[Perspective],
                                  synthesized_content: str) -> float:
        """Calculate confidence score for synthesis result"""
        try:
            # Base confidence from perspective confidences
            perspective_confidence = sum(p.confidence * p.weight for p in perspectives)
            perspective_confidence /= sum(p.weight for p in perspectives)
            
            # Content length factor
            length_factor = min(len(synthesized_content) / 2000, 1.0)
            
            # Perspective count factor
            count_factor = min(len(perspectives) / 5, 1.0)
            
            # Calculate final confidence
            confidence = (perspective_confidence * 0.5 + length_factor * 0.3 + count_factor * 0.2)
            
            return min(max(confidence, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating confidence score: {e}")
            return 0.5
            
    def _extract_keywords(self, text: str) -> list[str]:
        """Extract keywords from text"""
        # Simple keyword extraction
        words = text.lower().split()
        keywords = [word for word in words if len(word) > 3]
        return list(set(keywords))[:10]  # Top 10 unique keywords
        
    def _calculate_perspective_relevance(self,
                                       keywords: list[str],
                                       perspective_type: PerspectiveType) -> float:
        """Calculate relevance of perspective type to topic keywords"""
        try:
            # Define relevance mappings
            relevance_keywords = {
                PerspectiveType.TECHNICAL: ['technical', 'technology', 'system', 'implementation', 'architecture'],
                PerspectiveType.BUSINESS: ['business', 'market', 'revenue', 'cost', 'strategy'],
                PerspectiveType.ETHICAL: ['ethical', 'moral', 'responsibility', 'impact', 'values'],
                PerspectiveType.USER_EXPERIENCE: ['user', 'experience', 'interface', 'usability', 'design'],
                PerspectiveType.FINANCIAL: ['financial', 'budget', 'investment', 'cost', 'profit'],
                PerspectiveType.LEGAL: ['legal', 'compliance', 'regulation', 'law', 'contract'],
                PerspectiveType.ENVIRONMENTAL: ['environmental', 'sustainability', 'climate', 'green', 'ecology'],
                PerspectiveType.SOCIAL: ['social', 'community', 'society', 'cultural', 'impact'],
                PerspectiveType.INNOVATION: ['innovation', 'innovation', 'creative', 'new', 'breakthrough'],
                PerspectiveType.RISK: ['risk', 'security', 'safety', 'threat', 'vulnerability']
            }
            
            # Calculate relevance based on keyword overlap
            relevant_keywords = relevance_keywords.get(perspective_type, [])
            overlap = len(set(keywords) & set(relevant_keywords))
            
            relevance = overlap / len(relevant_keywords) if relevant_keywords else 0.0
            return min(relevance, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating perspective relevance: {e}")
            return 0.5
            
    async def _extract_common_themes(self, perspectives: list[Perspective]) -> list[str]:
        """Extract common themes from perspectives"""
        try:
            # Simple theme extraction
            all_content = ' '.join([p.content.lower() for p in perspectives])
            keywords = self._extract_keywords(all_content)
            
            # Return top themes
            return keywords[:5]
            
        except Exception as e:
            logger.error(f"Error extracting common themes: {e}")
            return []
            
    async def _identify_agreements(self, perspectives: list[Perspective]) -> list[str]:
        """Identify areas of agreement among perspectives"""
        try:
            # Simple agreement detection
            agreements = []
            
            # Look for common positive sentiment words
            positive_words = ['effective', 'beneficial', 'important', 'valuable', 'successful']
            
            for word in positive_words:
                count = sum(1 for p in perspectives if word in p.content.lower())
                if count >= len(perspectives) / 2:  # Majority agreement
                    agreements.append(f"General agreement on {word} aspects")
                    
            return agreements
            
        except Exception as e:
            logger.error(f"Error identifying agreements: {e}")
            return []
            
    async def _generate_conflict_resolution(self,
                                          conflict: PerspectiveConflict,
                                          perspectives: list[Perspective]) -> str:
        """Generate resolution for a specific conflict"""
        try:
            # Find the conflicting perspectives
            conflicting_perspectives = [
                p for p in perspectives if p.perspective_id in conflict.perspective_ids
            ]
            
            if len(conflicting_perspectives) != 2:
                return "Unable to resolve conflict: missing perspective information."
                
            persp1, persp2 = conflicting_perspectives
            
            resolution = f"""
The conflict between {persp1.perspective_type.value} and {persp2.perspective_type.value} perspectives can be resolved by:

1. **Contextual Differentiation**: Each perspective may be valid in different contexts or scenarios
2. **Complementary Insights**: The perspectives may address different aspects of the topic
3. **Integrated Approach**: Both perspectives can contribute to a comprehensive understanding

**Resolution**: The contradiction is resolved by recognizing that both perspectives offer valuable insights that can be integrated rather than treated as mutually exclusive.
"""
            
            return resolution
            
        except Exception as e:
            logger.error(f"Error generating conflict resolution: {e}")
            return "Error generating conflict resolution."
            
    async def _generate_basic_perspectives(self,
                                         topic: str,
                                         perspective_types: list[PerspectiveType]) -> list[Perspective]:
        """Generate basic perspectives for graceful degradation"""
        try:
            perspectives = []
            
            for perspective_type in perspective_types[:2]:  # Limit to 2 basic perspectives
                perspective = Perspective(
                    perspective_id=str(uuid.uuid4()),
                    perspective_type=perspective_type,
                    title=f"Basic {perspective_type.value.title()} Perspective",
                    description=f"Basic analysis from {perspective_type.value} viewpoint",
                    content=f"Basic {perspective_type.value} perspective on {topic}.",
                    author_id='system',
                    confidence=0.6,
                    weight=0.5,
                    created_at=datetime.now(),
                    metadata={'fallback': True}
                )
                perspectives.append(perspective)
                
            return perspectives
            
        except Exception as e:
            logger.error(f"Error generating basic perspectives: {e}")
            return []
            
    async def _generate_basic_synthesis(self,
                                       topic: str,
                                       perspectives: list[Perspective]) -> SynthesisResult:
        """Generate basic synthesis for graceful degradation"""
        try:
            basic_content = f"Basic synthesis of {len(perspectives)} perspectives on {topic}."
            
            return SynthesisResult(
                synthesis_id=str(uuid.uuid4()),
                topic=topic,
                perspectives=perspectives,
                conflicts=[],
                synthesized_content=basic_content,
                consensus_score=0.5,
                confidence_score=0.5,
                synthesis_strategy=SynthesisStrategy.WEIGHTED_AVERAGE,
                created_at=datetime.now(),
                metadata={'fallback': True}
            )
            
        except Exception as e:
            logger.error(f"Error generating basic synthesis: {e}")
            raise
            
    async def _initialize_conflict_detectors(self) -> None:
        """Initialize conflict detection algorithms"""
        try:
            # Register conflict detectors
            self.conflict_detectors['semantic'] = self._detect_semantic_conflicts
            self.conflict_detectors['sentiment'] = self._detect_sentiment_conflicts
            self.conflict_detectors['factual'] = self._detect_factual_conflicts
            
            logger.info(f"Initialized {len(self.conflict_detectors)} conflict detectors")
            
        except Exception as e:
            logger.error(f"Error initializing conflict detectors: {e}")
            
    def _initialize_perspective_templates(self) -> None:
        """Initialize perspective templates"""
        try:
            # Technical perspective template
            self.perspective_templates[PerspectiveType.TECHNICAL] = {
                'name': 'Technical Analysis',
                'description': 'Focuses on technical implementation, architecture, and feasibility',
                'key_considerations': ['Technical feasibility', 'Implementation complexity', 'Scalability', 'Maintainability'],
                'prompt_template': '''
Analyze the topic "{topic}" from a technical perspective.

Knowledge Base:
{knowledge}

Context:
{context}

Provide a comprehensive technical analysis covering:
- Technical feasibility and implementation approach
- System architecture and design considerations
- Scalability and performance implications
- Maintenance and operational requirements
- Technical risks and mitigation strategies
'''
            }
            
            # Business perspective template
            self.perspective_templates[PerspectiveType.BUSINESS] = {
                'name': 'Business Analysis',
                'description': 'Focuses on business value, market impact, and strategic alignment',
                'key_considerations': ['Business value', 'Market opportunity', 'Competitive advantage', 'ROI'],
                'prompt_template': '''
Analyze the topic "{topic}" from a business perspective.

Knowledge Base:
{knowledge}

Context:
{context}

Provide a comprehensive business analysis covering:
- Business value proposition and benefits
- Market opportunity and competitive landscape
- Return on investment and cost-benefit analysis
- Strategic alignment and business impact
- Market risks and business challenges
'''
            }
            
            # Ethical perspective template
            self.perspective_templates[PerspectiveType.ETHICAL] = {
                'name': 'Ethical Analysis',
                'description': 'Focuses on ethical implications, moral considerations, and social responsibility',
                'key_considerations': ['Ethical implications', 'Social responsibility', 'Fairness and equity', 'Transparency'],
                'prompt_template': '''
Analyze the topic "{topic}" from an ethical perspective.

Knowledge Base:
{knowledge}

Context:
{context}

Provide a comprehensive ethical analysis covering:
- Ethical implications and moral considerations
- Social responsibility and stakeholder impact
- Fairness, equity, and accessibility concerns
- Transparency and accountability requirements
- Ethical risks and mitigation strategies
'''
            }
            
            # Set default weights
            self.perspective_weights = {
                PerspectiveType.TECHNICAL: 0.8,
                PerspectiveType.BUSINESS: 0.8,
                PerspectiveType.ETHICAL: 0.7,
                PerspectiveType.USER_EXPERIENCE: 0.7,
                PerspectiveType.FINANCIAL: 0.8,
                PerspectiveType.LEGAL: 0.9,
                PerspectiveType.ENVIRONMENTAL: 0.6,
                PerspectiveType.SOCIAL: 0.6,
                PerspectiveType.INNOVATION: 0.7,
                PerspectiveType.RISK: 0.8
            }
            
            logger.info(f"Initialized {len(self.perspective_templates)} perspective templates")
            
        except Exception as e:
            logger.error(f"Error initializing perspective templates: {e}")
            
    # Conflict detection methods
    async def _detect_semantic_conflicts(self,
                                        perspectives: list[Perspective]) -> list[PerspectiveConflict]:
        """Detect semantic conflicts between perspectives"""
        # This would implement more sophisticated semantic analysis
        return []
        
    async def _detect_sentiment_conflicts(self,
                                         perspectives: list[Perspective]) -> list[PerspectiveConflict]:
        """Detect sentiment conflicts between perspectives"""
        # This would implement sentiment analysis
        return []
        
    async def _detect_factual_conflicts(self,
                                       perspectives: list[Perspective]) -> list[PerspectiveConflict]:
        """Detect factual conflicts between perspectives"""
        # This would implement fact-checking and consistency analysis
        return []


# Singleton instance for global use
multi_perspective_generator = None

def get_multi_perspective_generator(sskg_manager: EnhancedSSKGManager,
                                   memory_agent: MemAgent,
                                   allocator: SmartReviewerAllocator) -> MultiPerspectiveGenerator:
    """Get or create multi-perspective generator instance"""
    global multi_perspective_generator
    if multi_perspective_generator is None:
        multi_perspective_generator = MultiPerspectiveGenerator(sskg_manager, memory_agent, allocator)
    return multi_perspective_generator
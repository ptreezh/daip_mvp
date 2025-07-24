# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-24 16:30:00
@Author  : DAIP-LIVE Team
@File    : viewpoint_collection_node.py
@Description:
    ViewpointCollectionNode for Multi-perspective Synthesis Workflow.
"""
import logging
from datetime import datetime
from typing import Any, Dict, List

from ..base import InstitutionalPrimitive, ExecutionContext
from .models import ExpertViewpoint, ViewpointCollection

logger = logging.getLogger(__name__)


class ViewpointCollectionNode(InstitutionalPrimitive):
    """
    观点收集节点 - Gathers all expert perspectives with analysis of conflicts and consensus.
    
    Collects all expert viewpoints and analyzes them for conflicts, consensus areas,
    and coverage to prepare for synthesis.
    """
    
    def __init__(self, primitive_id: str, config: Dict[str, Any] = None):
        super().__init__(primitive_id, config)
        self.min_viewpoints = config.get("min_viewpoints", 2) if config else 2
        self.conflict_threshold = config.get("conflict_threshold", 0.3) if config else 0.3
        self.consensus_threshold = config.get("consensus_threshold", 0.7) if config else 0.7
        self.analyze_coverage = config.get("analyze_coverage", True) if config else True
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """
        Execute viewpoint collection and analysis.
        
        Args:
            inputs: Should contain 'viewpoints' to collect and analyze
            context: Execution context
            
        Returns:
            Analyzed viewpoint collection
        """
        context.mark_started()
        
        try:
            # Get viewpoints from inputs or workflow state
            viewpoints_data = inputs.get("viewpoints") or context.state.get("viewpoints", [])
            topic = inputs.get("topic") or context.state.get("topic", "Unknown topic")
            
            if not viewpoints_data:
                raise ValueError("Viewpoints are required for collection")
            
            if len(viewpoints_data) < self.min_viewpoints:
                logger.warning(f"Only {len(viewpoints_data)} viewpoints available, minimum is {self.min_viewpoints}")
            
            # Convert to ExpertViewpoint objects
            viewpoints = [ExpertViewpoint(**data) for data in viewpoints_data]
            
            # Analyze conflicts
            conflicts = self._analyze_conflicts(viewpoints)
            
            # Identify consensus areas
            consensus_areas = self._identify_consensus_areas(viewpoints)
            
            # Analyze coverage
            coverage_analysis = {}
            if self.analyze_coverage:
                coverage_analysis = self._analyze_coverage(viewpoints, topic)
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(viewpoints, conflicts, consensus_areas, coverage_analysis)
            
            # Create ViewpointCollection
            collection = ViewpointCollection(
                topic=topic,
                viewpoints=viewpoints,
                conflicts=conflicts,
                consensus_areas=consensus_areas,
                coverage_analysis=coverage_analysis,
                quality_score=quality_score,
                metadata={
                    "collection_timestamp": datetime.now().isoformat(),
                    "viewpoint_count": len(viewpoints),
                    "perspectives": list(set(vp.metadata.get("perspective", "Unknown") for vp in viewpoints))
                }
            )
            
            # Store in workflow state
            context.state["viewpoint_collection"] = collection.model_dump()
            
            context.mark_completed()
            
            return {
                "collection": collection.model_dump(),
                "viewpoint_count": len(viewpoints),
                "conflict_count": len(conflicts),
                "consensus_count": len(consensus_areas),
                "quality_score": quality_score,
                "success": True
            }
            
        except Exception as e:
            context.mark_failed()
            logger.error(f"ViewpointCollectionNode execution failed: {e}")
            return {
                "collection": {},
                "viewpoint_count": 0,
                "conflict_count": 0,
                "consensus_count": 0,
                "quality_score": 0.0,
                "success": False,
                "error": str(e)
            }
    
    def _analyze_conflicts(self, viewpoints: List[ExpertViewpoint]) -> List[Dict[str, Any]]:
        """Analyze conflicts between viewpoints."""
        conflicts = []
        
        # Compare viewpoints pairwise
        for i, vp1 in enumerate(viewpoints):
            for j, vp2 in enumerate(viewpoints[i+1:], i+1):
                # Check for conflicting viewpoints
                conflict_score = self._calculate_conflict_score(vp1, vp2)
                
                if conflict_score >= self.conflict_threshold:
                    conflict = {
                        "viewpoint_1": {
                            "expert_id": vp1.expert_id,
                            "expert_name": vp1.expert_name,
                            "perspective": vp1.metadata.get("perspective", "Unknown"),
                            "viewpoint_summary": vp1.viewpoint[:200] + "..." if len(vp1.viewpoint) > 200 else vp1.viewpoint
                        },
                        "viewpoint_2": {
                            "expert_id": vp2.expert_id,
                            "expert_name": vp2.expert_name,
                            "perspective": vp2.metadata.get("perspective", "Unknown"),
                            "viewpoint_summary": vp2.viewpoint[:200] + "..." if len(vp2.viewpoint) > 200 else vp2.viewpoint
                        },
                        "conflict_score": conflict_score,
                        "conflict_type": self._identify_conflict_type(vp1, vp2),
                        "description": f"Conflict between {vp1.expert_name} and {vp2.expert_name} on {vp1.metadata.get('perspective', 'Unknown')} vs {vp2.metadata.get('perspective', 'Unknown')} perspectives"
                    }
                    conflicts.append(conflict)
        
        return conflicts
    
    def _calculate_conflict_score(self, vp1: ExpertViewpoint, vp2: ExpertViewpoint) -> float:
        """Calculate conflict score between two viewpoints."""
        # Simple heuristic based on opposing keywords and confidence differences
        opposing_keywords = [
            ("增加", "减少"), ("提高", "降低"), ("有利", "不利"),
            ("积极", "消极"), ("正面", "负面"), ("支持", "反对"),
            ("同意", "不同意"), ("赞成", "反对"), ("好", "坏")
        ]
        
        conflict_indicators = 0
        total_indicators = len(opposing_keywords)
        
        for pos_word, neg_word in opposing_keywords:
            if pos_word in vp1.viewpoint and neg_word in vp2.viewpoint:
                conflict_indicators += 1
            elif neg_word in vp1.viewpoint and pos_word in vp2.viewpoint:
                conflict_indicators += 1
        
        # Base conflict score from keyword analysis
        keyword_score = conflict_indicators / total_indicators if total_indicators > 0 else 0
        
        # Adjust based on confidence levels (high confidence + disagreement = higher conflict)
        confidence_factor = (vp1.confidence + vp2.confidence) / 2
        
        # Different perspectives naturally have some conflict
        perspective_factor = 0.2 if vp1.metadata.get("perspective") != vp2.metadata.get("perspective") else 0
        
        return min(keyword_score * confidence_factor + perspective_factor, 1.0)
    
    def _identify_conflict_type(self, vp1: ExpertViewpoint, vp2: ExpertViewpoint) -> str:
        """Identify the type of conflict between viewpoints."""
        if vp1.metadata.get("perspective") != vp2.metadata.get("perspective"):
            return "perspective_difference"
        elif abs(vp1.confidence - vp2.confidence) > 0.3:
            return "confidence_difference"
        else:
            return "content_disagreement"
    
    def _identify_consensus_areas(self, viewpoints: List[ExpertViewpoint]) -> List[str]:
        """Identify areas of consensus among viewpoints."""
        consensus_areas = []
        
        # Look for common themes and agreements
        common_keywords = self._extract_common_keywords(viewpoints)
        
        # Identify consensus based on common keywords and similar confidence levels
        for keyword in common_keywords:
            supporting_viewpoints = [
                vp for vp in viewpoints 
                if keyword in vp.viewpoint.lower() and vp.confidence >= self.consensus_threshold
            ]
            
            if len(supporting_viewpoints) >= len(viewpoints) * 0.6:  # 60% agreement threshold
                consensus_areas.append(f"关于'{keyword}'的共识：多数专家认同相关观点")
        
        # Look for explicit agreements in supporting evidence
        evidence_consensus = self._find_evidence_consensus(viewpoints)
        consensus_areas.extend(evidence_consensus)
        
        return consensus_areas[:5]  # Limit to top 5 consensus areas
    
    def _extract_common_keywords(self, viewpoints: List[ExpertViewpoint]) -> List[str]:
        """Extract common keywords from viewpoints."""
        # Simple keyword extraction - in practice would use more sophisticated NLP
        important_keywords = [
            "技术", "发展", "影响", "变化", "机会", "挑战", "需要", "重要",
            "增长", "创新", "效率", "质量", "安全", "风险", "政策", "教育",
            "社会", "经济", "环境", "文化", "伦理", "法律", "管理", "合作"
        ]
        
        keyword_counts = {}
        for keyword in important_keywords:
            count = sum(1 for vp in viewpoints if keyword in vp.viewpoint)
            if count >= 2:  # At least 2 viewpoints mention it
                keyword_counts[keyword] = count
        
        # Return keywords sorted by frequency
        return sorted(keyword_counts.keys(), key=lambda k: keyword_counts[k], reverse=True)[:10]
    
    def _find_evidence_consensus(self, viewpoints: List[ExpertViewpoint]) -> List[str]:
        """Find consensus in supporting evidence."""
        evidence_consensus = []
        
        # Collect all evidence
        all_evidence = []
        for vp in viewpoints:
            all_evidence.extend(vp.supporting_evidence)
        
        # Find evidence mentioned by multiple experts
        evidence_counts = {}
        for evidence in all_evidence:
            # Simple similarity check - in practice would use semantic similarity
            similar_count = sum(1 for other_evidence in all_evidence if self._evidence_similarity(evidence, other_evidence) > 0.7)
            if similar_count >= 2:
                evidence_counts[evidence] = similar_count
        
        # Convert to consensus statements
        for evidence, count in sorted(evidence_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
            evidence_consensus.append(f"多位专家都提到了：{evidence}")
        
        return evidence_consensus
    
    def _evidence_similarity(self, evidence1: str, evidence2: str) -> float:
        """Calculate similarity between two pieces of evidence."""
        # Simple word overlap similarity
        words1 = set(evidence1.lower().split())
        words2 = set(evidence2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _analyze_coverage(self, viewpoints: List[ExpertViewpoint], topic: str) -> Dict[str, Any]:
        """Analyze coverage of the topic by viewpoints."""
        coverage_analysis = {
            "perspectives_covered": [],
            "expertise_areas_covered": [],
            "potential_gaps": [],
            "coverage_score": 0.0
        }
        
        # Analyze perspectives covered
        perspectives = set()
        expertise_areas = set()
        
        for vp in viewpoints:
            perspective = vp.metadata.get("perspective", "Unknown")
            perspectives.add(perspective)
            expertise_areas.update(vp.expertise_areas)
        
        coverage_analysis["perspectives_covered"] = list(perspectives)
        coverage_analysis["expertise_areas_covered"] = list(expertise_areas)
        
        # Identify potential gaps
        expected_perspectives = ["经济", "社会", "技术", "伦理", "政治", "环境", "文化", "法律"]
        missing_perspectives = [p for p in expected_perspectives if p not in perspectives]
        
        if missing_perspectives:
            coverage_analysis["potential_gaps"] = [f"缺少{p}视角的分析" for p in missing_perspectives[:3]]
        
        # Calculate coverage score
        coverage_score = len(perspectives) / len(expected_perspectives)
        coverage_analysis["coverage_score"] = min(coverage_score, 1.0)
        
        return coverage_analysis
    
    def _calculate_quality_score(
        self, 
        viewpoints: List[ExpertViewpoint], 
        conflicts: List[Dict[str, Any]], 
        consensus_areas: List[str],
        coverage_analysis: Dict[str, Any]
    ) -> float:
        """Calculate overall quality score for the viewpoint collection."""
        if not viewpoints:
            return 0.0
        
        # Diversity score (more perspectives = better)
        perspectives = set(vp.metadata.get("perspective", "Unknown") for vp in viewpoints)
        diversity_score = min(len(perspectives) / 4, 1.0)  # Normalize to max 4 perspectives
        
        # Confidence score (average confidence of all viewpoints)
        confidence_score = sum(vp.confidence for vp in viewpoints) / len(viewpoints)
        
        # Evidence score (viewpoints with more evidence are better)
        evidence_score = sum(min(len(vp.supporting_evidence) / 3, 1.0) for vp in viewpoints) / len(viewpoints)
        
        # Conflict balance score (some conflict is good, too much is bad)
        conflict_ratio = len(conflicts) / max(len(viewpoints) * (len(viewpoints) - 1) / 2, 1)
        conflict_score = 1.0 - abs(conflict_ratio - 0.3)  # Optimal conflict ratio around 0.3
        
        # Consensus score (having some consensus is good)
        consensus_score = min(len(consensus_areas) / 3, 1.0)  # Normalize to max 3 consensus areas
        
        # Coverage score
        coverage_score = coverage_analysis.get("coverage_score", 0.5)
        
        # Weighted average
        quality_score = (
            diversity_score * 0.2 +
            confidence_score * 0.2 +
            evidence_score * 0.15 +
            conflict_score * 0.15 +
            consensus_score * 0.15 +
            coverage_score * 0.15
        )
        
        return quality_score
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Return input schema for the viewpoint collection node."""
        return {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Original topic"
                },
                "viewpoints": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of expert viewpoints to collect and analyze"
                }
            },
            "required": ["viewpoints"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Return output schema for the viewpoint collection node."""
        return {
            "type": "object",
            "properties": {
                "collection": {
                    "type": "object",
                    "description": "Analyzed viewpoint collection"
                },
                "viewpoint_count": {
                    "type": "integer",
                    "description": "Number of viewpoints collected"
                },
                "conflict_count": {
                    "type": "integer",
                    "description": "Number of conflicts identified"
                },
                "consensus_count": {
                    "type": "integer",
                    "description": "Number of consensus areas identified"
                },
                "quality_score": {
                    "type": "number",
                    "description": "Overall quality score of the collection"
                },
                "success": {
                    "type": "boolean",
                    "description": "Whether collection was successful"
                }
            },
            "required": ["collection", "viewpoint_count", "quality_score", "success"]
        }
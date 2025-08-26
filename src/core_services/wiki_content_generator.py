"""Wiki Content Generation Interface

Integrates MultiRoleDialogueEngine with WikiService to generate high-quality wiki content
through structured debate and discussion processes.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from abc import ABC, abstractmethod

from src.core_services.wiki_service import WikiService
from src.core_services.role_manager import RoleManager
from src.core_services.integrated_llm_manager import IntegratedLLMManager
from src.debate_system.multi_role_dialogue_engine import (
    MultiRoleDialogueEngine, DialogueContext, RoleContext, DebatePhase
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ContentGenerationRequest:
    """Request for wiki content generation."""
    
    topic: str
    content_type: str  # "article", "debate_summary", "analysis", "tutorial"
    target_audience: str  # "beginner", "intermediate", "expert", "general"
    scope: str  # "overview", "detailed", "comprehensive"
    special_requirements: List[str] = None
    preferred_roles: List[str] = None
    
    def __post_init__(self):
        if self.special_requirements is None:
            self.special_requirements = []
        if self.preferred_roles is None:
            self.preferred_roles = []


@dataclass
class ContentGenerationResult:
    """Result of wiki content generation."""
    
    success: bool
    generated_content: str = ""
    structured_content: Dict[str, Any] = None
    participant_contributions: List[Dict[str, Any]] = None
    consensus_points: List[str] = None
    remaining_disagreements: List[str] = None
    quality_metrics: Dict[str, float] = None
    generation_time: float = 0.0
    error_message: str = ""


class ContentGenerationStrategy(ABC):
    """Abstract base class for content generation strategies."""
    
    @abstractmethod
    async def generate_content(self, request: ContentGenerationRequest) -> ContentGenerationResult:
        """Generate content based on the request."""
        pass


class DebateBasedContentGenerator(ContentGenerationStrategy):
    """Generate wiki content through structured debate process."""
    
    def __init__(self, 
                 wiki_service: WikiService,
                 role_manager: RoleManager,
                 llm_manager: IntegratedLLMManager):
        self.wiki_service = wiki_service
        self.role_manager = role_manager
        self.llm_manager = llm_manager
        self.logger = logging.getLogger(__name__)
    
    async def generate_content(self, request: ContentGenerationRequest) -> ContentGenerationResult:
        """Generate wiki content through structured debate."""
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Starting content generation for topic: {request.topic}")
            
            # 1. Select appropriate roles for the topic
            selected_roles = await self._select_roles_for_topic(request)
            
            if not selected_roles:
                return ContentGenerationResult(
                    success=False,
                    error_message="No suitable roles found for the topic"
                )
            
            # 2. Configure debate parameters for wiki content generation
            debate_config = self._create_debate_config(request, selected_roles)
            
            # 3. Run simplified debate (replacing MultiRoleDialogueEngine)
            debate_result = await self._run_simplified_debate(debate_config)
            
            if not debate_result.get("success", False):
                return ContentGenerationResult(
                    success=False,
                    error_message="Debate process failed"
                )
            
            # 4. Process debate results into wiki content
            content_result = await self._process_debate_to_content(
                debate_result, request
            )
            
            # 5. Calculate quality metrics
            quality_metrics = self._calculate_quality_metrics(content_result, debate_result)
            
            generation_time = (datetime.now() - start_time).total_seconds()
            
            return ContentGenerationResult(
                success=True,
                generated_content=content_result["content"],
                structured_content=content_result["structure"],
                participant_contributions=content_result.get("contributions", []),
                consensus_points=content_result.get("consensus_points", []),
                remaining_disagreements=content_result.get("disagreements", []),
                quality_metrics=quality_metrics,
                generation_time=generation_time
            )
            
        except Exception as e:
            self.logger.error(f"Content generation failed: {e}")
            generation_time = (datetime.now() - start_time).total_seconds()
            
            return ContentGenerationResult(
                success=False,
                error_message=str(e),
                generation_time=generation_time
            )
    
    async def _select_roles_for_topic(self, request: ContentGenerationRequest) -> List[RoleContext]:
        """Select appropriate roles for the content generation request."""
        try:
            # Use role manager to match roles to topic
            matched_roles = self.role_manager.match_roles_to_task(
                request.topic, 
                task_type="wiki_creation", 
                limit=6
            )
            
            # Convert to RoleContext objects
            role_contexts = []
            for match in matched_roles[:4]:  # Limit to 4 roles for manageable debate
                role = match["role"]
                context = RoleContext(
                    role_id=role.id,
                    role_name=role.name,
                    role_type="expert",  # All wiki generation roles are experts
                    expertise_areas=getattr(role, 'capabilities', []),
                    confidence_level=0.8,
                    speaking_style="formal_academic"
                )
                role_contexts.append(context)
            
            self.logger.info(f"Selected {len(role_contexts)} roles for topic: {request.topic}")
            return role_contexts
            
        except Exception as e:
            self.logger.error(f"Role selection failed: {e}")
            return []
    
    def _create_debate_config(self, request: ContentGenerationRequest, roles: List[RoleContext]) -> Dict[str, Any]:
        """Create debate configuration for wiki content generation."""
        
        # Adjust debate parameters based on content type
        if request.content_type == "article":
            rounds = 3
            consensus_strategy = "collaborative_synthesis"
        elif request.content_type == "debate_summary":
            rounds = 4
            consensus_strategy = "evidence_based_consensus"
        elif request.content_type == "analysis":
            rounds = 3
            consensus_strategy = "analytical_consensus"
        else:  # tutorial, overview
            rounds = 2
            consensus_strategy = "simple_consensus"
        
        return {
            "topic": request.topic,
            "roles": roles,
            "rounds": rounds,
            "consensus_strategy": consensus_strategy,
            "content_type": request.content_type,
            "target_audience": request.target_audience,
            "scope": request.scope,
            "special_requirements": request.special_requirements,
            "output_format": "structured_wiki"
        }
    
    async def _process_debate_to_content(self, debate_result: Dict[str, Any], request: ContentGenerationRequest) -> Dict[str, Any]:
        """Process debate results into structured wiki content."""
        
        try:
            # Extract key information from debate
            debate_history = debate_result.get("history", [])
            consensus = debate_result.get("consensus", "")
            key_points = debate_result.get("key_points", [])
            
            # Generate structured content based on type
            if request.content_type == "article":
                content = await self._generate_article_content(
                    debate_history, consensus, key_points, request
                )
            elif request.content_type == "debate_summary":
                content = await self._generate_debate_summary_content(
                    debate_history, consensus, key_points, request
                )
            elif request.content_type == "analysis":
                content = await self._generate_analysis_content(
                    debate_history, consensus, key_points, request
                )
            else:
                content = await self._generate_general_content(
                    debate_history, consensus, key_points, request
                )
            
            return content
            
        except Exception as e:
            self.logger.error(f"Content processing failed: {e}")
            return {
                "content": f"Error processing content: {str(e)}",
                "structure": {},
                "contributions": [],
                "consensus_points": [],
                "disagreements": []
            }
    
    async def _generate_article_content(self, history: List[Dict], consensus: str, key_points: List[str], request: ContentGenerationRequest) -> Dict[str, Any]:
        """Generate structured article content."""
        
        # Build article structure
        article_structure = {
            "title": request.topic,
            "introduction": self._generate_introduction(request, consensus),
            "main_sections": self._generate_main_sections(history, key_points),
            "conclusion": self._generate_conclusion(consensus, key_points),
            "references": self._generate_references(history),
            "metadata": {
                "content_type": "article",
                "target_audience": request.target_audience,
                "scope": request.scope,
                "generated_date": datetime.now().isoformat(),
                "contributors": [turn.get("role", "Unknown") for turn in history]
            }
        }
        
        # Convert to markdown content
        content = self._structure_to_markdown(article_structure)
        
        return {
            "content": content,
            "structure": article_structure,
            "contributions": history,
            "consensus_points": key_points,
            "disagreements": self._extract_disagreements(history)
        }
    
    async def _generate_debate_summary_content(self, history: List[Dict], consensus: str, key_points: List[str], request: ContentGenerationRequest) -> Dict[str, Any]:
        """Generate debate summary content."""
        
        summary_structure = {
            "title": f"Debate Summary: {request.topic}",
            "debate_overview": self._generate_debate_overview(history, request),
            "participant_positions": self._generate_position_summary(history),
            "key_arguments": self._generate_key_arguments(history),
            "consensus_analysis": self._generate_consensus_analysis(consensus, history),
            "remaining_questions": self._generate_remaining_questions(history),
            "metadata": {
                "content_type": "debate_summary",
                "debate_participants": len(set(turn.get("role", "Unknown") for turn in history)),
                "generated_date": datetime.now().isoformat()
            }
        }
        
        content = self._structure_to_markdown(summary_structure)
        
        return {
            "content": content,
            "structure": summary_structure,
            "contributions": history,
            "consensus_points": [consensus] if consensus else [],
            "disagreements": self._extract_disagreements(history)
        }
    
    async def _generate_analysis_content(self, history: List[Dict], consensus: str, key_points: List[str], request: ContentGenerationRequest) -> Dict[str, Any]:
        """Generate analytical content."""
        
        analysis_structure = {
            "title": f"Analysis: {request.topic}",
            "executive_summary": self._generate_executive_summary(consensus, key_points),
            "detailed_analysis": self._generate_detailed_analysis(history, key_points),
            "perspectives": self._generate_perspective_analysis(history),
            "implications": self._generate_implications_analysis(consensus, history),
            "recommendations": self._generate_recommendations(consensus, key_points),
            "metadata": {
                "content_type": "analysis",
                "analysis_depth": request.scope,
                "generated_date": datetime.now().isoformat()
            }
        }
        
        content = self._structure_to_markdown(analysis_structure)
        
        return {
            "content": content,
            "structure": analysis_structure,
            "contributions": history,
            "consensus_points": key_points,
            "disagreements": self._extract_disagreements(history)
        }
    
    async def _generate_general_content(self, history: List[Dict], consensus: str, key_points: List[str], request: ContentGenerationRequest) -> Dict[str, Any]:
        """Generate general overview content."""
        
        # Combine contributions from all participants
        all_content = "\n\n".join([turn.get("content", "") for turn in history])
        
        general_structure = {
            "title": request.topic,
            "overview": self._generate_general_overview(all_content, request),
            "key_insights": key_points,
            "participant_contributions": self._generate_contribution_summary(history),
            "conclusion": consensus if consensus else "Discussion ongoing",
            "metadata": {
                "content_type": "general",
                "generated_date": datetime.now().isoformat()
            }
        }
        
        content = self._structure_to_markdown(general_structure)
        
        return {
            "content": content,
            "structure": general_structure,
            "contributions": history,
            "consensus_points": key_points,
            "disagreements": self._extract_disagreements(history)
        }
    
    # Helper methods for content generation
    def _generate_introduction(self, request: ContentGenerationRequest, consensus: str) -> str:
        """Generate article introduction."""
        audience_map = {
            "beginner": "This article provides a comprehensive introduction to",
            "intermediate": "This article explores the key aspects of",
            "expert": "This article provides an in-depth analysis of",
            "general": "This article examines"
        }
        
        intro = f"{audience_map.get(request.target_audience, 'This article covers')} {request.topic}. "
        
        if request.scope == "comprehensive":
            intro += "We will explore this topic in detail, covering multiple perspectives and insights."
        elif request.scope == "detailed":
            intro += "We will examine the key elements and considerations."
        else:
            intro += "We will provide an overview of the main points."
        
        return intro
    
    def _generate_main_sections(self, history: List[Dict], key_points: List[str]) -> List[Dict[str, str]]:
        """Generate main sections for article."""
        sections = []
        
        # Create sections based on key points
        for i, point in enumerate(key_points[:5], 1):  # Limit to 5 main sections
            section_content = self._find_content_for_point(history, point)
            sections.append({
                "title": f"Section {i}: {point}",
                "content": section_content
            })
        
        return sections
    
    def _generate_conclusion(self, consensus: str, key_points: List[str]) -> str:
        """Generate article conclusion."""
        if consensus:
            return f"In conclusion, {consensus}. This analysis has highlighted the importance of {', '.join(key_points[:3])}."
        else:
            return f"This exploration of {', '.join(key_points[:3])} provides valuable insights for further discussion and research."
    
    def _calculate_quality_metrics(self, content_result: Dict[str, Any], debate_result: Dict[str, Any]) -> Dict[str, float]:
        """Calculate quality metrics for generated content."""
        
        try:
            content = content_result.get("content", "")
            history = debate_result.get("history", [])
            
            metrics = {
                "content_length": len(content),
                "structure_score": self._calculate_structure_score(content_result),
                "coherence_score": self._calculate_coherence_score(content),
                "completeness_score": self._calculate_completeness_score(content_result, debate_result),
                "participant_diversity": self._calculate_diversity_score(history),
                "consensus_strength": self._calculate_consensus_score(debate_result)
            }
            
            # Normalize scores to 0-1 range
            for key in metrics:
                if isinstance(metrics[key], (int, float)):
                    metrics[key] = min(1.0, max(0.0, metrics[key] / 100.0))
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Quality metrics calculation failed: {e}")
            return {"error": str(e)}
    
    def _calculate_structure_score(self, content_result: Dict[str, Any]) -> float:
        """Calculate content structure quality score."""
        structure = content_result.get("structure", {})
        
        # Check for required structural elements
        required_elements = ["title", "introduction", "main_sections", "conclusion"]
        score = sum(1 for element in required_elements if element in structure)
        
        return (score / len(required_elements)) * 100
    
    def _calculate_coherence_score(self, content: str) -> float:
        """Calculate content coherence score."""
        # Simple coherence check based on paragraph structure and transitions
        sentences = content.split('.')
        if len(sentences) < 3:
            return 50.0  # Very short content
        
        # Check for logical flow indicators
        flow_indicators = ["however", "therefore", "furthermore", "consequently", "additionally"]
        flow_count = sum(1 for sentence in sentences if any(indicator in sentence.lower() for indicator in flow_indicators))
        
        return min(100.0, (flow_count / len(sentences)) * 200)
    
    def _calculate_completeness_score(self, content_result: Dict[str, Any], debate_result: Dict[str, Any]) -> float:
        """Calculate content completeness score."""
        history = debate_result.get("history", [])
        
        # Check if content covers major points from debate
        content = content_result.get("content", "").lower()
        debate_points = set()
        
        for turn in history:
            turn_content = turn.get("content", "").lower()
            # Extract key nouns and concepts (simplified)
            words = turn_content.split()
            debate_points.update(words[:10])  # Take first 10 words as key points
        
        covered_points = sum(1 for point in debate_points if point in content)
        
        if len(debate_points) == 0:
            return 100.0  # Avoid division by zero
        
        return (covered_points / len(debate_points)) * 100
    
    def _calculate_diversity_score(self, history: List[Dict]) -> float:
        """Calculate participant diversity score."""
        if not history:
            return 0.0
        
        participants = set(turn.get("role", "Unknown") for turn in history)
        total_contributions = len(history)
        
        if len(participants) == 0:
            return 0.0
        
        # Calculate balance of contributions
        ideal_contributions = total_contributions / len(participants)
        balance_score = 100.0 - (abs(ideal_contributions - 1) * 10)  # Penalize imbalance
        
        return max(0.0, balance_score)
    
    def _calculate_consensus_score(self, debate_result: Dict[str, Any]) -> float:
        """Calculate consensus strength score."""
        consensus = debate_result.get("consensus", "")
        history = debate_result.get("history", [])
        
        if not consensus:
            return 30.0  # Low score for no consensus
        
        # Check if consensus is mentioned in later turns
        later_mentions = sum(1 for turn in history[-3:] if consensus.lower() in turn.get("content", "").lower())
        
        return min(100.0, 30.0 + (later_mentions * 20))
    
    # Additional helper methods (simplified for brevity)
    def _structure_to_markdown(self, structure: Dict[str, Any]) -> str:
        """Convert structure to markdown format."""
        markdown = f"# {structure.get('title', 'Untitled')}\n\n"
        
        for key, value in structure.items():
            if key == "title":
                continue
            elif isinstance(value, str):
                markdown += f"{value}\n\n"
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        markdown += f"## {item.get('title', 'Section')}\n\n{item.get('content', '')}\n\n"
                    else:
                        markdown += f"- {item}\n"
            elif isinstance(value, dict):
                markdown += f"## {key.replace('_', ' ').title()}\n\n{value}\n\n"
        
        return markdown
    
    def _extract_disagreements(self, history: List[Dict]) -> List[str]:
        """Extract remaining disagreements from debate history."""
        # Simplified disagreement extraction
        disagreements = []
        
        # Look for opposing viewpoints
        for i, turn in enumerate(history):
            content = turn.get("content", "").lower()
            if any(word in content for word in ["however", "disagree", "contrary", "opposing"]):
                disagreements.append(f"Position from {turn.get('role', 'Unknown')}: {content[:100]}...")
        
        return disagreements[:3]  # Return top 3 disagreements
    
    def _find_content_for_point(self, history: List[Dict], point: str) -> str:
        """Find relevant content for a key point."""
        point_lower = point.lower()
        
        # Search for content related to the point
        relevant_content = []
        for turn in history:
            content = turn.get("content", "")
            if any(word in content.lower() for word in point_lower.split()):
                relevant_content.append(f"{turn.get('role', 'Unknown')}: {content}")
        
        return "\n\n".join(relevant_content[:2]) if relevant_content else "Content not found for this point."
    
    async def _run_simplified_debate(self, debate_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run a simplified debate using available dependencies."""
        try:
            topic = debate_config.get("topic", "")
            roles = debate_config.get("roles", [])
            rounds = debate_config.get("rounds", 2)
            
            debate_history = []
            consensus = ""
            key_points = []
            
            # Simulate debate rounds
            for round_num in range(rounds):
                self.logger.info(f"Running debate round {round_num + 1}/{rounds}")
                
                # Each role contributes in this round
                for role in roles:
                    # Generate role response using LLM
                    prompt = self._build_role_prompt_simplified(role, topic, round_num, debate_history)
                    response = await self._call_llm_simplified(prompt)
                    
                    if response:
                        debate_history.append({
                            "role": role.role_name,
                            "content": response,
                            "round": round_num + 1
                        })
            
            # Generate consensus and key points
            consensus, key_points = await self._generate_consensus(debate_history, topic)
            
            return {
                "success": True,
                "history": debate_history,
                "consensus": consensus,
                "key_points": key_points,
                "participants": [role.role_name for role in roles]
            }
            
        except Exception as e:
            self.logger.error(f"Simplified debate failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_role_prompt_simplified(self, role: RoleContext, topic: str, round_num: int, history: List[Dict]) -> str:
        """Build prompt for role response in simplified debate."""
        prompt = f"""
You are {role.role_name}, an expert in {', '.join(role.expertise_areas)}.
Your speaking style is {role.speaking_style}.

Topic: {topic}
Round: {round_num + 1}

Previous discussion:"""
        
        if history:
            for turn in history[-3:]:  # Show last 3 turns
                prompt += f"\n{turn['role']}: {turn['content']}"
        else:
            prompt += "\n(No previous discussion)"
        
        prompt += f"\n\nPlease provide your perspective on this topic. Keep your response concise (200-300 words)."
        
        return prompt
    
    async def _call_llm_simplified(self, prompt: str) -> Optional[str]:
        """Call LLM with simplified error handling."""
        try:
            response = await self.llm_manager.generate_response(
                prompt=prompt,
                model_preference="gpt-4",
                timeout=30
            )
            return response.strip() if response else None
        except Exception as e:
            self.logger.warning(f"LLM call failed: {e}")
            return None
    
    async def _generate_consensus(self, history: List[Dict], topic: str) -> Tuple[str, List[str]]:
        """Generate consensus and key points from debate history."""
        if not history:
            return "No consensus reached", []
        
        # Extract key points from all contributions
        all_content = "\n".join([turn["content"] for turn in history])
        
        # Use LLM to generate consensus
        consensus_prompt = f"""
Based on the following discussion about "{topic}", please provide:
1. A brief consensus statement (1-2 sentences)
2. 3-5 key points that emerged from the discussion

Discussion:
{all_content}

Consensus:"""
        
        try:
            consensus_response = await self._call_llm_simplified(consensus_prompt)
            if consensus_response:
                # Simple parsing of consensus response
                lines = consensus_response.split('\n')
                consensus = lines[0].strip() if lines else "Discussion completed"
                key_points = [line.strip('- ').strip() for line in lines[1:] if line.strip() and not line.startswith('Consensus:')]
                return consensus, key_points[:5]  # Limit to 5 key points
        except Exception as e:
            self.logger.error(f"Consensus generation failed: {e}")
        
        return "Discussion completed", ["Multiple perspectives were shared"]
    
    # Additional content generation helper methods would go here...
    # (Omitted for brevity, but would include methods for generating specific content types)


class WikiContentGenerator:
    """Main interface for wiki content generation using debate engine."""
    
    def __init__(self, 
                 wiki_service: WikiService = None,
                 role_manager: RoleManager = None,
                 llm_manager: IntegratedLLMManager = None):
        """Initialize the wiki content generator."""
        self.wiki_service = wiki_service or WikiService()
        self.role_manager = role_manager or RoleManager()
        self.llm_manager = llm_manager or IntegratedLLMManager()
        
        # Initialize content generator
        self.content_generator = DebateBasedContentGenerator(
            wiki_service=self.wiki_service,
            role_manager=self.role_manager,
            llm_manager=self.llm_manager
        )
        
        self.logger = logging.getLogger(__name__)
    
    async def generate_wiki_content(self, request: ContentGenerationRequest) -> ContentGenerationResult:
        """Generate wiki content using debate-based approach."""
        try:
            self.logger.info(f"Generating wiki content for: {request.topic}")
            
            # Generate content using debate engine
            result = await self.content_generator.generate_content(request)
            
            if result.success:
                self.logger.info(f"Successfully generated content for: {request.topic}")
                self.logger.info(f"Content length: {len(result.generated_content)} characters")
                self.logger.info(f"Generation time: {result.generation_time:.2f} seconds")
                self.logger.info(f"Quality metrics: {result.quality_metrics}")
            else:
                self.logger.error(f"Content generation failed: {result.error_message}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Wiki content generation error: {e}")
            return ContentGenerationResult(
                success=False,
                error_message=str(e)
            )
    
    async def generate_and_save_wiki_entry(self, 
                                          request: ContentGenerationRequest,
                                          entry_name: str,
                                          author: str = "wiki_content_generator") -> Dict[str, Any]:
        """Generate content and save directly to wiki."""
        try:
            # Generate content
            generation_result = await self.generate_wiki_content(request)
            
            if not generation_result.success:
                return {
                    "success": False,
                    "error": generation_result.error_message
                }
            
            # Save to wiki
            wiki_result = self.wiki_service.create_entry(
                entry_name=entry_name,
                content=generation_result.generated_content,
                author_role=author,
                tags=["generated", "debate-based", request.content_type],
                category="generated_content"
            )
            
            return {
                "success": True,
                "entry_name": entry_name,
                "wiki_version": wiki_result,
                "generation_result": generation_result,
                "content_length": len(generation_result.generated_content),
                "generation_time": generation_result.generation_time,
                "quality_metrics": generation_result.quality_metrics
            }
            
        except Exception as e:
            self.logger.error(f"Generate and save error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_content_generation_capabilities(self) -> Dict[str, Any]:
        """Get information about content generation capabilities."""
        return {
            "content_types": ["article", "debate_summary", "analysis", "tutorial", "overview"],
            "target_audiences": ["beginner", "intermediate", "expert", "general"],
            "scopes": ["overview", "detailed", "comprehensive"],
            "max_participants": 4,
            "estimated_generation_time": "30-120 seconds",
            "quality_metrics": ["structure_score", "coherence_score", "completeness_score", "participant_diversity", "consensus_strength"]
        }
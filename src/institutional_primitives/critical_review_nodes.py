"""@Time    : 2025-07-23 13:00:00
@Author  : DAIP-LIVE Team
@File    : critical_review_nodes.py
@Description:
    Implementation of institutional primitive nodes for the Critical Review Workflow.
    These nodes implement systematic fact validation through multi-role review processes.
"""
import asyncio
import logging
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from src.institutional_primitives.base import ExecutionContext, InstitutionalPrimitive
from src.institutional_primitives.consensus_node import ConsensusNode
from src.institutional_primitives.revision_node import RevisionNode

# Service imports will be resolved at runtime through the execution context
# from src.core_services.fact_extraction_service import FactExtractionService
# from src.core_services.fact_validation_service import FactValidationService
# from src.core_services.wiki_service import WikiService
# from src.core_services.synthesis_engine import SynthesisEngine
# from src.kernel.enhanced_llm_interface import EnhancedLLMInterface

logger = logging.getLogger(__name__)


class ExtractedFact(BaseModel):
    """Model for extracted facts."""
    id: str
    content: str
    confidence: float = Field(ge=0.0, le=1.0)
    source_location: str
    fact_type: str = "general"  # general, numerical, temporal, causal
    metadata: dict[str, Any] = Field(default_factory=dict)


class Evidence(BaseModel):
    """Model for evidence supporting or challenging facts."""
    content: str
    source: str
    credibility: float = Field(ge=0.0, le=1.0)
    evidence_type: str  # "supporting", "challenging", "neutral"
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvidenceReport(BaseModel):
    """Model for evidence reports on specific facts."""
    fact_id: str
    supporting_evidence: list[Evidence] = Field(default_factory=list)
    challenging_evidence: list[Evidence] = Field(default_factory=list)
    neutral_evidence: list[Evidence] = Field(default_factory=list)
    overall_assessment: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    reviewer_id: str
    review_timestamp: datetime = Field(default_factory=datetime.now)


class ReviewResult(BaseModel):
    """Model for complete review results."""
    original_content: str
    extracted_facts: list[ExtractedFact] = Field(default_factory=list)
    evidence_reports: list[EvidenceReport] = Field(default_factory=list)
    credibility_scores: dict[str, float] = Field(default_factory=dict)
    revised_content: Optional[str] = None
    validation_summary: str
    review_metadata: dict[str, Any] = Field(default_factory=dict)


class GenerationNode(InstitutionalPrimitive):
    """生成节点 - Captures initial AI role output with full context and metadata.
    
    This node serves as the entry point for the Critical Review Workflow,
    capturing the original content that needs to be fact-checked.
    """
    
    def __init__(self, primitive_id: str, config: dict[str, Any] = None):
        super().__init__(primitive_id, config)
        self.role_name = config.get("role_name", "创作者") if config else "创作者"
        self.capture_metadata = config.get("capture_metadata", True) if config else True
    
    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
        """Execute content generation and capture.
        
        Args:
            inputs: Should contain 'prompt' and optionally 'role_context'
            context: Execution context
            
        Returns:
            Generated content with metadata
        """
        context.mark_started()
        
        try:
            # Extract inputs
            prompt = inputs.get("prompt", "")
            role_context = inputs.get("role_context", "")
            
            if not prompt:
                raise ValueError("Prompt is required for content generation")
            
            # Get LLM interface from services
            llm_interface = context.services.get("llm_interface")
            if not llm_interface:
                raise ValueError("LLM interface not available in execution context")
            
            # Prepare generation context
            generation_context = f"Role: {self.role_name}\n"
            if role_context:
                generation_context += f"Context: {role_context}\n"
            generation_context += f"Task: {prompt}"
            
            # Generate content
            messages = [{"role": "user", "content": generation_context}]
            response = await llm_interface.generate(messages)
            
            generated_content = response.get("content", "")
            
            # Capture metadata if enabled
            metadata = {}
            if self.capture_metadata:
                metadata = {
                    "role_name": self.role_name,
                    "generation_timestamp": datetime.now().isoformat(),
                    "prompt": prompt,
                    "role_context": role_context,
                    "model_info": response.get("model", "unknown"),
                    "token_usage": response.get("usage", {}),
                    "generation_id": f"gen_{context.execution_id}_{context.node_id}"
                }
            
            # Store in workflow state for downstream nodes
            context.state["original_content"] = generated_content
            context.state["generation_metadata"] = metadata
            
            context.mark_completed()
            
            return {
                "content": generated_content,
                "metadata": metadata,
                "success": True
            }
            
        except Exception as e:
            context.mark_failed()
            logger.error(f"GenerationNode execution failed: {e}")
            return {
                "content": "",
                "metadata": {},
                "success": False,
                "error": str(e)
            }
    
    def get_input_schema(self) -> dict[str, Any]:
        """Return input schema for the generation node."""
        return {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The prompt for content generation"
                },
                "role_context": {
                    "type": "string",
                    "description": "Additional context for the role"
                }
            },
            "required": ["prompt"]
        }
    
    def get_output_schema(self) -> dict[str, Any]:
        """Return output schema for the generation node."""
        return {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "Generated content"
                },
                "metadata": {
                    "type": "object",
                    "description": "Generation metadata"
                },
                "success": {
                    "type": "boolean",
                    "description": "Whether generation was successful"
                },
                "error": {
                    "type": "string",
                    "description": "Error message if generation failed"
                }
            },
            "required": ["content", "success"]
        }


class FactExtractionNode(InstitutionalPrimitive):
    """事实提取节点 - Extracts verifiable factual assertions from content.
    
    Uses FactExtractionService to identify all verifiable factual assertions
    from the generated content for subsequent validation.
    """
    
    def __init__(self, primitive_id: str, config: dict[str, Any] = None):
        super().__init__(primitive_id, config)
        self.min_confidence = config.get("min_confidence", 0.5) if config else 0.5
        self.max_facts = config.get("max_facts", 20) if config else 20
    
    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
        """Execute fact extraction from content.
        
        Args:
            inputs: Should contain 'content' to extract facts from
            context: Execution context
            
        Returns:
            List of extracted facts
        """
        context.mark_started()
        
        try:
            # Get content from inputs or workflow state
            content = inputs.get("content") or context.state.get("original_content", "")
            
            if not content:
                raise ValueError("Content is required for fact extraction")
            
            # Get fact extraction service
            fact_service = context.services.get("fact_extraction_service")
            if not fact_service:
                raise ValueError("Fact extraction service not available")
            
            # Extract facts
            raw_facts = await fact_service.extract_facts(content)
            
            # Convert to ExtractedFact objects
            extracted_facts = []
            for i, fact in enumerate(raw_facts[:self.max_facts]):
                if fact.get("confidence", 0) >= self.min_confidence:
                    extracted_fact = ExtractedFact(
                        id=f"fact_{context.execution_id}_{i}",
                        content=fact.get("content", ""),
                        confidence=fact.get("confidence", 0.5),
                        source_location=fact.get("location", "unknown"),
                        fact_type=fact.get("type", "general"),
                        metadata={
                            "extraction_method": fact.get("method", "llm"),
                            "extraction_timestamp": datetime.now().isoformat(),
                            "source_content_hash": hash(content)
                        }
                    )
                    extracted_facts.append(extracted_fact)
            
            # Store in workflow state
            context.state["extracted_facts"] = [fact.model_dump() for fact in extracted_facts]
            
            context.mark_completed()
            
            return {
                "facts": [fact.model_dump() for fact in extracted_facts],
                "fact_count": len(extracted_facts),
                "success": True
            }
            
        except Exception as e:
            context.mark_failed()
            logger.error(f"FactExtractionNode execution failed: {e}")
            return {
                "facts": [],
                "fact_count": 0,
                "success": False,
                "error": str(e)
            }
    
    def get_input_schema(self) -> dict[str, Any]:
        """Return input schema for the fact extraction node."""
        return {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "Content to extract facts from"
                }
            },
            "required": ["content"]
        }
    
    def get_output_schema(self) -> dict[str, Any]:
        """Return output schema for the fact extraction node."""
        return {
            "type": "object",
            "properties": {
                "facts": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of extracted facts"
                },
                "fact_count": {
                    "type": "integer",
                    "description": "Number of facts extracted"
                },
                "success": {
                    "type": "boolean",
                    "description": "Whether extraction was successful"
                }
            },
            "required": ["facts", "fact_count", "success"]
        }


class ParallelReviewNode(InstitutionalPrimitive):
    """并行审查节点 - Executes parallel review with multiple specialized roles.
    
    Implements fan-out pattern to simultaneously deploy challenger and validator roles
    for comprehensive fact review from multiple perspectives.
    """
    
    def __init__(self, primitive_id: str, config: dict[str, Any] = None):
        super().__init__(primitive_id, config)
        self.reviewer_roles = config.get("reviewer_roles", ["批判者", "验证者"]) if config else ["批判者", "验证者"]
        self.max_parallel_reviews = config.get("max_parallel_reviews", 5) if config else 5
    
    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
        """Execute parallel review of extracted facts.
        
        Args:
            inputs: Should contain 'facts' to review
            context: Execution context
            
        Returns:
            Evidence reports from all reviewers
        """
        context.mark_started()
        
        try:
            # Get facts from inputs or workflow state
            facts_data = inputs.get("facts") or context.state.get("extracted_facts", [])
            
            if not facts_data:
                raise ValueError("Facts are required for parallel review")
            
            # Convert to ExtractedFact objects
            facts = [ExtractedFact(**fact_data) for fact_data in facts_data]
            
            # Get services
            llm_interface = context.services.get("llm_interface")
            wiki_service = context.services.get("wiki_service")
            
            if not llm_interface:
                raise ValueError("LLM interface not available")
            
            # Create review tasks for each fact and reviewer combination
            review_tasks = []
            for fact in facts[:self.max_parallel_reviews]:
                for role in self.reviewer_roles:
                    task = self._create_review_task(fact, role, llm_interface, wiki_service, context)
                    review_tasks.append(task)
            
            # Execute all reviews in parallel
            review_results = await asyncio.gather(*review_tasks, return_exceptions=True)
            
            # Process results
            evidence_reports = []
            for result in review_results:
                if isinstance(result, EvidenceReport):
                    evidence_reports.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"Review task failed: {result}")
            
            # Store in workflow state
            context.state["evidence_reports"] = [report.model_dump() for report in evidence_reports]
            
            context.mark_completed()
            
            return {
                "evidence_reports": [report.model_dump() for report in evidence_reports],
                "review_count": len(evidence_reports),
                "success": True
            }
            
        except Exception as e:
            context.mark_failed()
            logger.error(f"ParallelReviewNode execution failed: {e}")
            return {
                "evidence_reports": [],
                "review_count": 0,
                "success": False,
                "error": str(e)
            }
    
    async def _create_review_task(
        self,
        fact: ExtractedFact,
        reviewer_role: str,
        llm_interface,
        wiki_service,
        context: ExecutionContext
    ) -> EvidenceReport:
        """Create and execute a single review task."""
        try:
            # Prepare review prompt based on role
            if reviewer_role == "批判者":
                prompt = f"""作为一个批判性思维专家，请仔细审查以下事实声明：

事实声明：{fact.content}

请从以下角度进行批判性分析：
1. 寻找可能的反驳证据
2. 识别逻辑漏洞或不一致之处
3. 考虑替代解释或观点
4. 评估证据的可靠性

请提供具体的挑战性证据和分析。"""
            
            else:  # 验证者
                prompt = f"""作为一个事实验证专家，请验证以下事实声明：

事实声明：{fact.content}

请从以下角度进行验证：
1. 寻找支持性证据和来源
2. 验证数据的准确性
3. 确认信息的时效性
4. 评估来源的权威性

请提供具体的支持性证据和验证结果。"""
            
            # Get background knowledge from wiki and SSKG if available
            background_info = ""
            if wiki_service:
                try:
                    related_pages = await wiki_service.search_pages(fact.content, limit=3)
                    if related_pages:
                        background_info = f"\n\n背景信息：\n{related_pages[0].get('content', '')[:500]}..."
                except Exception as e:
                    logger.warning(f"Failed to get background info from wiki: {e}")
            
            # Get related facts from SSKG
            sskg_manager = context.services.get("sskg_manager")
            if sskg_manager:
                try:
                    # Search for related facts in SSKG
                    related_facts = await sskg_manager.search_knowledge(
                        query=fact.content,
                        filters={"min_confidence": 0.6},
                        limit=3
                    )
                    if related_facts:
                        sskg_info = "\n\n相关已验证事实：\n"
                        for related_fact in related_facts:
                            sskg_info += f"- {related_fact.get('content', '')} (可信度: {related_fact.get('confidence', 0):.2f})\n"
                        background_info += sskg_info
                except Exception as e:
                    logger.warning(f"Failed to get related facts from SSKG: {e}")
            
            # Get relevant memories from MemAgent
            mem_agent = context.services.get("mem_agent")
            if mem_agent:
                try:
                    relevant_memories = await mem_agent.retrieve_memories(
                        context=fact.content,
                        limit=2
                    )
                    if relevant_memories:
                        memory_info = "\n\n相关记忆：\n"
                        for memory in relevant_memories:
                            memory_info += f"- {memory.get('content', '')[:200]}...\n"
                        background_info += memory_info
                except Exception as e:
                    logger.warning(f"Failed to get relevant memories: {e}")
            
            full_prompt = prompt + background_info
            
            # Generate review
            messages = [{"role": "user", "content": full_prompt}]
            response = await llm_interface.generate(messages)
            
            review_content = response.get("content", "")
            
            # Parse review content to extract evidence
            # This is a simplified implementation - in practice would use more sophisticated parsing
            evidence_list = []
            if reviewer_role == "批判者":
                evidence_list.append(Evidence(
                    content=review_content,
                    source=f"{reviewer_role}_review",
                    credibility=0.7,
                    evidence_type="challenging"
                ))
            else:
                evidence_list.append(Evidence(
                    content=review_content,
                    source=f"{reviewer_role}_review",
                    credibility=0.8,
                    evidence_type="supporting"
                ))
            
            # Create evidence report
            report = EvidenceReport(
                fact_id=fact.id,
                supporting_evidence=evidence_list if reviewer_role == "验证者" else [],
                challenging_evidence=evidence_list if reviewer_role == "批判者" else [],
                overall_assessment=review_content[:200] + "..." if len(review_content) > 200 else review_content,
                confidence_score=0.75,
                reviewer_id=reviewer_role
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Review task failed for fact {fact.id} by {reviewer_role}: {e}")
            # Return empty report on failure
            return EvidenceReport(
                fact_id=fact.id,
                overall_assessment=f"Review failed: {str(e)}",
                confidence_score=0.0,
                reviewer_id=reviewer_role
            )
    
    def get_input_schema(self) -> dict[str, Any]:
        """Return input schema for the parallel review node."""
        return {
            "type": "object",
            "properties": {
                "facts": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of facts to review"
                }
            },
            "required": ["facts"]
        }
    
    def get_output_schema(self) -> dict[str, Any]:
        """Return output schema for the parallel review node."""
        return {
            "type": "object",
            "properties": {
                "evidence_reports": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of evidence reports from reviewers"
                },
                "review_count": {
                    "type": "integer",
                    "description": "Number of reviews completed"
                },
                "success": {
                    "type": "boolean",
                    "description": "Whether review was successful"
                }
            },
            "required": ["evidence_reports", "review_count", "success"]
        }


class EvidenceAggregationNode(InstitutionalPrimitive):
    """证据汇总节点 - Aggregates evidence from parallel reviews using fan-in pattern.
    
    Collects all positive and negative evidence with source attribution
    and prepares comprehensive evidence summaries for consensus calculation.
    """
    
    def __init__(self, primitive_id: str, config: dict[str, Any] = None):
        super().__init__(primitive_id, config)
        self.min_evidence_threshold = config.get("min_evidence_threshold", 1) if config else 1
        self.weight_by_credibility = config.get("weight_by_credibility", True) if config else True
    
    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
        """Execute evidence aggregation from parallel reviews.
        
        Args:
            inputs: Should contain 'evidence_reports' from parallel reviews
            context: Execution context
            
        Returns:
            Aggregated evidence summary for each fact
        """
        context.mark_started()
        
        try:
            # Get evidence reports from inputs or workflow state
            reports_data = inputs.get("evidence_reports") or context.state.get("evidence_reports", [])
            
            if not reports_data:
                raise ValueError("Evidence reports are required for aggregation")
            
            # Convert to EvidenceReport objects
            reports = [EvidenceReport(**report_data) for report_data in reports_data]
            
            # Group reports by fact ID
            fact_evidence = {}
            for report in reports:
                if report.fact_id not in fact_evidence:
                    fact_evidence[report.fact_id] = {
                        "supporting": [],
                        "challenging": [],
                        "neutral": [],
                        "reviewers": []
                    }
                
                fact_evidence[report.fact_id]["supporting"].extend(report.supporting_evidence)
                fact_evidence[report.fact_id]["challenging"].extend(report.challenging_evidence)
                fact_evidence[report.fact_id]["neutral"].extend(report.neutral_evidence)
                fact_evidence[report.fact_id]["reviewers"].append(report.reviewer_id)
            
            # Create aggregated evidence summaries
            aggregated_evidence = {}
            for fact_id, evidence in fact_evidence.items():
                # Calculate evidence scores
                supporting_score = self._calculate_evidence_score(evidence["supporting"])
                challenging_score = self._calculate_evidence_score(evidence["challenging"])
                neutral_score = self._calculate_evidence_score(evidence["neutral"])
                
                # Calculate overall credibility
                total_evidence = len(evidence["supporting"]) + len(evidence["challenging"]) + len(evidence["neutral"])
                if total_evidence >= self.min_evidence_threshold:
                    # Simple credibility calculation based on evidence balance
                    if supporting_score > challenging_score:
                        credibility = min(0.5 + (supporting_score - challenging_score) * 0.5, 1.0)
                    elif challenging_score > supporting_score:
                        credibility = max(0.5 - (challenging_score - supporting_score) * 0.5, 0.0)
                    else:
                        credibility = 0.5  # Neutral when evidence is balanced
                else:
                    # For single evidence items, use the evidence score directly
                    if supporting_score > 0:
                        credibility = min(0.5 + supporting_score * 0.3, 1.0)
                    elif challenging_score > 0:
                        credibility = max(0.5 - challenging_score * 0.3, 0.0)
                    else:
                        credibility = 0.3  # Low credibility when no evidence
                
                aggregated_evidence[fact_id] = {
                    "fact_id": fact_id,
                    "supporting_count": len(evidence["supporting"]),
                    "challenging_count": len(evidence["challenging"]),
                    "neutral_count": len(evidence["neutral"]),
                    "supporting_score": supporting_score,
                    "challenging_score": challenging_score,
                    "neutral_score": neutral_score,
                    "credibility_score": credibility,
                    "reviewers": evidence["reviewers"],
                    "evidence_summary": self._create_evidence_summary(evidence),
                    "aggregation_timestamp": datetime.now().isoformat()
                }
            
            # Store in workflow state
            context.state["aggregated_evidence"] = aggregated_evidence
            
            context.mark_completed()
            
            return {
                "aggregated_evidence": aggregated_evidence,
                "facts_processed": len(aggregated_evidence),
                "success": True
            }
            
        except Exception as e:
            context.mark_failed()
            logger.error(f"EvidenceAggregationNode execution failed: {e}")
            return {
                "aggregated_evidence": {},
                "facts_processed": 0,
                "success": False,
                "error": str(e)
            }
    
    def _calculate_evidence_score(self, evidence_list: list[Evidence]) -> float:
        """Calculate weighted evidence score."""
        if not evidence_list:
            return 0.0
        
        if self.weight_by_credibility:
            total_score = sum(evidence.credibility for evidence in evidence_list)
            return total_score / len(evidence_list)
        else:
            return len(evidence_list) * 0.2  # Simple count-based scoring
    
    def _create_evidence_summary(self, evidence: dict[str, list]) -> str:
        """Create a human-readable evidence summary."""
        summary_parts = []
        
        if evidence["supporting"]:
            summary_parts.append(f"支持性证据 ({len(evidence['supporting'])}项)")
        
        if evidence["challenging"]:
            summary_parts.append(f"质疑性证据 ({len(evidence['challenging'])}项)")
        
        if evidence["neutral"]:
            summary_parts.append(f"中性证据 ({len(evidence['neutral'])}项)")
        
        if not summary_parts:
            return "无足够证据"
        
        return "，".join(summary_parts) + f"，由{len(set(evidence.get('reviewers', [])))}位审查者提供"
    
    def get_input_schema(self) -> dict[str, Any]:
        """Return input schema for the evidence aggregation node."""
        return {
            "type": "object",
            "properties": {
                "evidence_reports": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of evidence reports from parallel reviews"
                }
            },
            "required": ["evidence_reports"]
        }
    
    def get_output_schema(self) -> dict[str, Any]:
        """Return output schema for the evidence aggregation node."""
        return {
            "type": "object",
            "properties": {
                "aggregated_evidence": {
                    "type": "object",
                    "description": "Aggregated evidence for each fact"
                },
                "facts_processed": {
                    "type": "integer",
                    "description": "Number of facts processed"
                },
                "success": {
                    "type": "boolean",
                    "description": "Whether aggregation was successful"
                }
            },
            "required": ["aggregated_evidence", "facts_processed", "success"]
        }


# ConsensusNode and RevisionNode are imported from their respective files
# No need to reimplement them here


class CriticalReviewWorkflow:
    """批判性审查工作流 - Orchestrates the complete critical review process.
    
    This class coordinates all the critical review nodes to implement the
    systematic fact validation workflow described in the design document.
    """
    
    def __init__(self, config: dict[str, Any] = None):
        self.config = config or {}
        self.credibility_threshold = self.config.get("credibility_threshold", 0.7)
        self.max_revision_cycles = self.config.get("max_revision_cycles", 3)
        self.enable_performance_monitoring = self.config.get("enable_performance_monitoring", True)
        self.enable_sskg_integration = self.config.get("enable_sskg_integration", True)
        self.enable_conflict_detection = self.config.get("enable_conflict_detection", True)
        
    async def execute_critical_review(
        self,
        content: str,
        topic: str,
        roles: list[str],
        context: ExecutionContext
    ) -> ReviewResult:
        """Execute the complete critical review workflow.
        
        Args:
            content: Original content to review
            topic: Topic context for the review
            roles: List of reviewer roles to use
            context: Execution context
            
        Returns:
            Complete review result with all evidence and revisions
        """
        try:
            # Initialize workflow state and performance monitoring
            start_time = datetime.now()
            workflow_state = {
                "original_content": content,
                "topic": topic,
                "reviewer_roles": roles,
                "revision_cycle": 0,
                "start_time": start_time.isoformat(),
                "performance_metrics": {}
            }
            context.state.update(workflow_state)
            
            # Step 1: Generation Node (if content is not already generated)
            if not content:
                generation_node = GenerationNode("generation", self.config.get("generation", {}))
                gen_result = await generation_node.execute(
                    {"prompt": topic}, context
                )
                if not gen_result.get("success"):
                    raise ValueError(f"Content generation failed: {gen_result.get('error')}")
                content = gen_result["content"]
                context.state["original_content"] = content
            
            # Step 2: Fact Extraction Node
            fact_extraction_node = FactExtractionNode("fact_extraction", self.config.get("fact_extraction", {}))
            fact_result = await fact_extraction_node.execute(
                {"content": content}, context
            )
            if not fact_result.get("success"):
                raise ValueError(f"Fact extraction failed: {fact_result.get('error')}")
            
            # Step 3: Parallel Review Node
            review_config = self.config.get("parallel_review", {})
            review_config["reviewer_roles"] = roles
            parallel_review_node = ParallelReviewNode("parallel_review", review_config)
            review_result = await parallel_review_node.execute(
                {"facts": fact_result["facts"]}, context
            )
            if not review_result.get("success"):
                raise ValueError(f"Parallel review failed: {review_result.get('error')}")
            
            # Step 4: Evidence Aggregation Node
            aggregation_node = EvidenceAggregationNode("evidence_aggregation", self.config.get("evidence_aggregation", {}))
            agg_result = await aggregation_node.execute(
                {"evidence_reports": review_result["evidence_reports"]}, context
            )
            if not agg_result.get("success"):
                raise ValueError(f"Evidence aggregation failed: {agg_result.get('error')}")
            
            # Step 5: Consensus Node
            consensus_node = ConsensusNode("consensus", self.config.get("consensus", {}))
            consensus_result = await consensus_node.execute(
                {"aggregated_evidence": agg_result["aggregated_evidence"]}, context
            )
            if not consensus_result.get("success"):
                raise ValueError(f"Consensus calculation failed: {consensus_result.get('error')}")
            
            # Step 6: Revision Node (if needed)
            revised_content = content
            credibility_scores = consensus_result.get("credibility_scores", {})
            low_credibility_facts = [
                fact_id for fact_id, score in credibility_scores.items()
                if score < self.credibility_threshold
            ]
            
            if low_credibility_facts and context.state.get("revision_cycle", 0) < self.max_revision_cycles:
                revision_node = RevisionNode("revision", self.config.get("revision", {}))
                revision_result = await revision_node.execute({
                    "content": content,
                    "low_credibility_facts": low_credibility_facts,
                    "evidence_reports": review_result["evidence_reports"]
                }, context)
                
                if revision_result.get("success"):
                    revised_content = revision_result.get("revised_content", content)
                    context.state["revision_cycle"] = context.state.get("revision_cycle", 0) + 1
            
            # Store results in SSKG if enabled
            if self.enable_sskg_integration:
                await self._store_review_results_in_sskg(context, {
                    "original_content": content,
                    "revised_content": revised_content,
                    "facts": fact_result["facts"],
                    "evidence_reports": review_result["evidence_reports"],
                    "credibility_scores": credibility_scores
                })
            
            # Calculate performance metrics
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            performance_metrics = {
                "total_execution_time": execution_time,
                "facts_processed": len(fact_result["facts"]),
                "evidence_reports_generated": len(review_result["evidence_reports"]),
                "average_credibility": sum(credibility_scores.values()) / len(credibility_scores) if credibility_scores else 0.0,
                "revision_cycles": context.state.get("revision_cycle", 0),
                "throughput_facts_per_second": len(fact_result["facts"]) / execution_time if execution_time > 0 else 0
            }
            
            # Create final review result
            review_result_obj = ReviewResult(
                original_content=content,
                extracted_facts=[ExtractedFact(**fact) for fact in fact_result["facts"]],
                evidence_reports=[EvidenceReport(**report) for report in review_result["evidence_reports"]],
                credibility_scores=credibility_scores,
                revised_content=revised_content if revised_content != content else None,
                validation_summary=self._create_validation_summary(credibility_scores, low_credibility_facts),
                review_metadata={
                    "workflow_execution_id": context.execution_id,
                    "reviewer_roles": roles,
                    "revision_cycles": context.state.get("revision_cycle", 0),
                    "completion_timestamp": end_time.isoformat(),
                    "performance_metrics": performance_metrics,
                    "conflict_resolutions": context.state.get("conflict_resolutions", []),
                    "sskg_integration_enabled": self.enable_sskg_integration,
                    "conflict_detection_enabled": self.enable_conflict_detection
                }
            )
            
            return review_result_obj
            
        except Exception as e:
            logger.error(f"Critical review workflow failed: {e}")
            raise
    
    async def _store_review_results_in_sskg(self, context: ExecutionContext, results: dict[str, Any]):
        """Store review results in SSKG for future reference."""
        try:
            sskg_manager = context.services.get("sskg_manager")
            if not sskg_manager:
                logger.warning("SSKG manager not available, skipping result storage")
                return
            
            # Store validated facts with proper KnowledgeFact structure
            for fact_data in results["facts"]:
                fact_id = fact_data["id"]
                credibility = results["credibility_scores"].get(fact_id, 0.5)
                
                # Create KnowledgeFact object according to design spec
                from pydantic import BaseModel
                
                class KnowledgeFact(BaseModel):
                    id: Optional[str] = None
                    content: str
                    source: str
                    confidence: float = Field(ge=0.0, le=1.0)
                    timestamp: datetime = Field(default_factory=datetime.now)
                    metadata: dict[str, Any] = Field(default_factory=dict)
                    relations: list[dict[str, Any]] = Field(default_factory=list)
                    version: int = 1
                
                knowledge_fact = KnowledgeFact(
                    content=fact_data["content"],
                    source=f"critical_review_{context.execution_id}",
                    confidence=credibility,
                    metadata={
                        "review_type": "critical_review",
                        "original_confidence": fact_data.get("confidence", 0.5),
                        "review_timestamp": datetime.now().isoformat(),
                        "workflow_id": context.execution_id,
                        "fact_type": fact_data.get("fact_type", "general"),
                        "source_location": fact_data.get("source_location", "unknown"),
                        "evidence_count": len([
                            report for report in results["evidence_reports"]
                            if report.get("fact_id") == fact_id
                        ])
                    }
                )
                
                # Store fact in SSKG
                stored_fact_id = await sskg_manager.store_fact(knowledge_fact)
                
                # Store evidence relationships
                for evidence_report in results["evidence_reports"]:
                    if evidence_report.get("fact_id") == fact_id:
                        # Create evidence as related facts
                        for evidence in evidence_report.get("supporting_evidence", []):
                            evidence_fact = KnowledgeFact(
                                content=evidence.get("content", ""),
                                source=evidence.get("source", "unknown"),
                                confidence=evidence.get("credibility", 0.5),
                                metadata={
                                    "evidence_type": "supporting",
                                    "related_fact_id": stored_fact_id,
                                    "review_workflow_id": context.execution_id
                                }
                            )
                            await sskg_manager.store_fact(evidence_fact)
                        
                        for evidence in evidence_report.get("challenging_evidence", []):
                            evidence_fact = KnowledgeFact(
                                content=evidence.get("content", ""),
                                source=evidence.get("source", "unknown"),
                                confidence=evidence.get("credibility", 0.5),
                                metadata={
                                    "evidence_type": "challenging",
                                    "related_fact_id": stored_fact_id,
                                    "review_workflow_id": context.execution_id
                                }
                            )
                            await sskg_manager.store_fact(evidence_fact)
            
            # Check for conflicts with existing knowledge if enabled
            if self.enable_conflict_detection:
                await self._detect_and_resolve_conflicts(sskg_manager, results, context)
            
            # Store workflow execution metadata
            workflow_memory = {
                "content": f"Critical review workflow completed for content: {results['original_content'][:100]}...",
                "memory_type": "procedural",
                "owner_id": f"workflow_{context.execution_id}",
                "importance": 0.8,
                "metadata": {
                    "workflow_type": "critical_review",
                    "execution_id": context.execution_id,
                    "facts_processed": len(results["facts"]),
                    "average_credibility": sum(results["credibility_scores"].values()) / len(results["credibility_scores"]) if results["credibility_scores"] else 0.0,
                    "completion_timestamp": datetime.now().isoformat()
                }
            }
            
            await sskg_manager.store_memory(workflow_memory, "procedural")
            
        except Exception as e:
            logger.error(f"Failed to store review results in SSKG: {e}")
    
    async def _detect_and_resolve_conflicts(self, sskg_manager, results: dict[str, Any], context: ExecutionContext):
        """Detect and resolve conflicts with existing knowledge in SSKG."""
        try:
            conflicting_facts = []
            
            for fact_data in results["facts"]:
                fact_content = fact_data["content"]
                credibility = results["credibility_scores"].get(fact_data["id"], 0.5)
                
                # Search for potentially conflicting facts
                existing_facts = await sskg_manager.search_knowledge(
                    query=fact_content,
                    filters={"min_confidence": 0.5},
                    limit=5
                )
                
                # Simple conflict detection based on content similarity and contradictory indicators
                for existing_fact in existing_facts:
                    existing_content = existing_fact.get("content", "")
                    existing_confidence = existing_fact.get("confidence", 0.5)
                    
                    # Check for potential conflicts (this is a simplified approach)
                    if self._are_facts_conflicting(fact_content, existing_content):
                        conflicting_facts.append({
                            "new_fact": fact_data,
                            "new_credibility": credibility,
                            "existing_fact": existing_fact,
                            "existing_credibility": existing_confidence
                        })
            
            # Resolve conflicts if any found
            if conflicting_facts:
                for conflict in conflicting_facts:
                    resolution = await sskg_manager.resolve_conflicts([
                        conflict["new_fact"]["id"],
                        conflict["existing_fact"]["id"]
                    ])
                    
                    logger.info(f"Resolved conflict between facts: {resolution.get('resolution_strategy', 'unknown')}")
                    
                    # Store conflict resolution in workflow metadata
                    context.state.setdefault("conflict_resolutions", []).append({
                        "new_fact_id": conflict["new_fact"]["id"],
                        "existing_fact_id": conflict["existing_fact"]["id"],
                        "resolution": resolution.get("resolution_strategy", "unknown"),
                        "timestamp": datetime.now().isoformat()
                    })
            
        except Exception as e:
            logger.error(f"Failed to detect/resolve conflicts: {e}")
    
    def _are_facts_conflicting(self, fact1: str, fact2: str) -> bool:
        """Simple conflict detection between two facts.
        In a production system, this would use more sophisticated NLP techniques.
        """
        # Simple keyword-based conflict detection
        conflict_indicators = [
            ("是", "不是"), ("有", "没有"), ("能", "不能"), ("会", "不会"),
            ("正确", "错误"), ("真", "假"), ("存在", "不存在")
        ]
        
        fact1_lower = fact1.lower()
        fact2_lower = fact2.lower()
        
        for positive, negative in conflict_indicators:
            if (positive in fact1_lower and negative in fact2_lower) or \
               (negative in fact1_lower and positive in fact2_lower):
                return True
        
        return False
    
    def _create_validation_summary(self, credibility_scores: dict[str, float], low_credibility_facts: list[str]) -> str:
        """Create a human-readable validation summary."""
        total_facts = len(credibility_scores)
        high_credibility_facts = total_facts - len(low_credibility_facts)
        
        if total_facts == 0:
            return "未发现可验证的事实声明"
        
        avg_credibility = sum(credibility_scores.values()) / total_facts
        
        summary = f"验证了{total_facts}个事实声明，"
        summary += f"其中{high_credibility_facts}个具有高可信度，"
        summary += f"{len(low_credibility_facts)}个需要进一步验证。"
        summary += f"平均可信度评分：{avg_credibility:.2f}"
        
        if low_credibility_facts:
            summary += "。低可信度事实已标记为需要修订。"
        
        return summary


class CriticalReviewNodeRegistry:
    """Registry for critical review workflow nodes."""
    
    @staticmethod
    def get_all_nodes() -> dict[str, type]:
        """Get all available critical review nodes."""
        return {
            "generation": GenerationNode,
            "fact_extraction": FactExtractionNode,
            "parallel_review": ParallelReviewNode,
            "evidence_aggregation": EvidenceAggregationNode,
            "consensus": ConsensusNode,
            "revision": RevisionNode
        }
    
    @staticmethod
    def create_node(node_type: str, node_id: str, config: dict[str, Any] = None):
        """Create a node instance by type."""
        nodes = CriticalReviewNodeRegistry.get_all_nodes()
        if node_type not in nodes:
            raise ValueError(f"Unknown node type: {node_type}")
        
        return nodes[node_type](node_id, config)


# Export all nodes for easy import
__all__ = [
    'ExtractedFact',
    'Evidence', 
    'EvidenceReport',
    'ReviewResult',
    'GenerationNode',
    'FactExtractionNode',
    'ParallelReviewNode',
    'EvidenceAggregationNode',
    'CriticalReviewWorkflow',
    'CriticalReviewNodeRegistry'
]
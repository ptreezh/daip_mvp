# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-24 11:00:00
@Author  : DAIP-LIVE Team
@File    : critical_review_example.py
@Description:
    Example script demonstrating the use of the Critical Review Workflow.
"""
import asyncio
import logging
from typing import Dict, Any

from src.workflows.critical_review_workflow import CriticalReviewWorkflow
from src.core_services.llm_interface import EnhancedLLMInterface
from src.core_services.fact_extraction_service import FactExtractionService
from src.core_services.wiki_service import WikiService
from src.core_services.synthesis_engine import SynthesisEngine


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def setup_services() -> Dict[str, Any]:
    """
    Set up and initialize required services.
    
    Returns:
        Dictionary of service instances
    """
    # Initialize services
    llm_interface = EnhancedLLMInterface()
    fact_extraction_service = FactExtractionService()
    wiki_service = WikiService()
    synthesis_engine = SynthesisEngine()
    
    # Return services dictionary
    return {
        "llm_interface": llm_interface,
        "fact_extraction_service": fact_extraction_service,
        "wiki_service": wiki_service,
        "synthesis_engine": synthesis_engine
    }


async def run_critical_review_example():
    """Run a complete Critical Review Workflow example."""
    logger.info("Setting up services...")
    services = await setup_services()
    
    # Configure workflow
    workflow_config = {
        "generation": {
            "role_name": "AI科技专家"
        },
        "fact_extraction": {
            "min_confidence": 0.6,
            "max_facts": 15
        },
        "parallel_review": {
            "reviewer_roles": ["批判者", "验证者", "专家顾问"],
            "max_parallel_reviews": 10
        },
        "consensus": {
            "consensus_method": "synthesis",
            "credibility_threshold": 0.7
        }
    }
    
    # Create prompt
    prompt = """请提供一篇关于量子计算最新进展的简短介绍，包括：
1. 量子计算的基本原理
2. 最新的技术突破
3. 主要的量子计算公司和他们的成就
4. 量子计算的未来发展方向"""
    
    role_context = "你是一位量子计算领域的专家，熟悉该领域的最新研究进展和技术动态。"
    
    logger.info("Creating Critical Review Workflow...")
    workflow = CriticalReviewWorkflow("quantum_computing_review", workflow_config)
    
    logger.info("Executing Critical Review Workflow...")
    result = await workflow.execute(prompt, role_context, services)
    
    if result["success"]:
        logger.info("Workflow completed successfully!")
        
        logger.info("\n=== Original Content ===\n")
        logger.info(result["original_content"])
        
        if result["revision_needed"]:
            logger.info("\n=== Revision Summary ===\n")
            logger.info(result["revision_summary"])
            
            logger.info("\n=== Revised Content ===\n")
            logger.info(result["final_content"])
        else:
            logger.info("\n=== No Revision Needed ===\n")
            logger.info(result["revision_summary"])
        
        logger.info("\n=== Workflow Statistics ===\n")
        logger.info(f"Facts Extracted: {result['facts_extracted']}")
        logger.info(f"Facts Reviewed: {result['facts_reviewed']}")
        logger.info(f"Facts Needing Revision: {result['facts_needing_revision']}")
    else:
        logger.error(f"Workflow failed: {result['error']}")
        if "error_details" in result:
            logger.error(f"Error details: {result['error_details']}")


if __name__ == "__main__":
    asyncio.run(run_critical_review_example())
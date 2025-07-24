"""
Example usage of the Institutional Primitives Workflow Engine.

This script demonstrates how to define and execute workflows using the
Institutional Primitives Workflow Engine.
"""

import asyncio
import logging
from typing import Any, Dict

from src.institutional_primitives.base import ExecutionContext, InstitutionalPrimitive
from src.institutional_primitives.registry import PrimitiveRegistry
from src.institutional_primitives.workflow_engine import (
    WorkflowDefinition,
    WorkflowEdge,
    WorkflowEngine,
    WorkflowNode
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


# Define some example primitives
class GenerationPrimitive(InstitutionalPrimitive):
    """
    Primitive for generating content using an AI role.
    """
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """Execute the primitive."""
        topic = inputs.get("topic", "general topic")
        role = inputs.get("role", "assistant")
        
        # In a real implementation, this would call an LLM service
        content = f"Generated content about {topic} as {role}."
        
        return {
            "content": content,
            "role": role,
            "topic": topic
        }
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "topic": {"type": "string"},
                "role": {"type": "string"}
            }
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "content": {"type": "string"},
                "role": {"type": "string"},
                "topic": {"type": "string"}
            },
            "required": ["content", "role", "topic"]
        }


class FactExtractionPrimitive(InstitutionalPrimitive):
    """
    Primitive for extracting facts from content.
    """
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """Execute the primitive."""
        content = inputs.get("content", "")
        
        # In a real implementation, this would use a fact extraction service
        facts = [
            f"Fact 1 from {content[:20]}...",
            f"Fact 2 from {content[:20]}...",
            f"Fact 3 from {content[:20]}..."
        ]
        
        return {
            "facts": facts,
            "source_content": content
        }
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "content": {"type": "string"}
            },
            "required": ["content"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "facts": {"type": "array", "items": {"type": "string"}},
                "source_content": {"type": "string"}
            },
            "required": ["facts", "source_content"]
        }


class ValidationPrimitive(InstitutionalPrimitive):
    """
    Primitive for validating facts.
    """
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """Execute the primitive."""
        facts = inputs.get("facts", [])
        
        # In a real implementation, this would use a validation service
        validated_facts = []
        for fact in facts:
            validated_facts.append({
                "fact": fact,
                "is_valid": True,
                "confidence": 0.95,
                "evidence": f"Evidence for {fact}"
            })
        
        return {
            "validated_facts": validated_facts
        }
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "facts": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["facts"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "validated_facts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "fact": {"type": "string"},
                            "is_valid": {"type": "boolean"},
                            "confidence": {"type": "number"},
                            "evidence": {"type": "string"}
                        }
                    }
                }
            },
            "required": ["validated_facts"]
        }


class SynthesisPrimitive(InstitutionalPrimitive):
    """
    Primitive for synthesizing validated facts into a report.
    """
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """Execute the primitive."""
        validated_facts = inputs.get("validated_facts", [])
        
        # In a real implementation, this would use a synthesis service
        valid_facts = [item["fact"] for item in validated_facts if item["is_valid"]]
        report = f"Synthesis report based on {len(valid_facts)} validated facts:\n"
        report += "\n".join(f"- {fact}" for fact in valid_facts)
        
        return {
            "report": report,
            "fact_count": len(valid_facts)
        }
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "validated_facts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "fact": {"type": "string"},
                            "is_valid": {"type": "boolean"},
                            "confidence": {"type": "number"},
                            "evidence": {"type": "string"}
                        }
                    }
                }
            },
            "required": ["validated_facts"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "report": {"type": "string"},
                "fact_count": {"type": "integer"}
            },
            "required": ["report", "fact_count"]
        }


async def main():
    """Run the example."""
    # Create primitive registry
    registry = PrimitiveRegistry()
    registry.register_primitive("generation", GenerationPrimitive)
    registry.register_primitive("fact_extraction", FactExtractionPrimitive)
    registry.register_primitive("validation", ValidationPrimitive)
    registry.register_primitive("synthesis", SynthesisPrimitive)
    
    # Create workflow engine
    engine = WorkflowEngine(primitive_registry=registry)
    
    # Define a critical review workflow
    critical_review_workflow = WorkflowDefinition(
        id="critical_review",
        name="Critical Review Workflow",
        description="A workflow for critical review of generated content",
        nodes=[
            WorkflowNode(id="generate", type="generation"),
            WorkflowNode(id="extract_facts", type="fact_extraction"),
            WorkflowNode(id="validate_facts", type="validation"),
            WorkflowNode(id="synthesize", type="synthesis")
        ],
        edges=[
            WorkflowEdge(from_node="generate", to_node="extract_facts"),
            WorkflowEdge(from_node="extract_facts", to_node="validate_facts"),
            WorkflowEdge(from_node="validate_facts", to_node="synthesize")
        ]
    )
    
    # Execute the workflow
    print("Executing Critical Review Workflow...")
    result = await engine.execute_workflow(
        critical_review_workflow,
        {
            "topic": "artificial intelligence",
            "role": "AI researcher"
        }
    )
    
    # Print results
    print("\nWorkflow Execution Results:")
    print(f"Status: {result.status}")
    print(f"Execution ID: {result.execution_id}")
    print("\nOutputs:")
    for key, value in result.outputs.items():
        print(f"  {key}: {value}")
    
    print("\nExecution Trace:")
    for i, step in enumerate(result.execution_trace.steps):
        print(f"  Step {i+1}: {step.node_id} ({step.node_type}) - {step.status}")
        print(f"    Duration: {step.duration_ms:.2f}ms")
    
    print("\nMetrics:")
    for key, value in result.metrics.items():
        if key == "node_type_counts":
            print(f"  {key}:")
            for node_type, count in value.items():
                print(f"    {node_type}: {count}")
        else:
            print(f"  {key}: {value}")


if __name__ == "__main__":
    asyncio.run(main())
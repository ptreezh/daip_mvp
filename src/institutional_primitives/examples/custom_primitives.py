"""@Time    : 2025-07-25 05:30:00
@Author  : DAIP-LIVE Team
@File    : custom_primitives.py
@Description:
    Example custom primitives demonstrating the plugin interface system.
"""
import asyncio
from datetime import datetime
from typing import Any, Dict

from ..base import ExecutionContext
from ..plugin_interface import CustomPrimitiveBase, PluginInterface, PluginMetadata
from ..service_adapters import (
    AdapterCapability,
    ServiceAdapter,
    ServiceAdapterMetadata,
    ServiceRequest,
    ServiceResponse,
    ServiceType,
)


class SentimentAnalysisPrimitive(CustomPrimitiveBase):
    """Example custom primitive for sentiment analysis."""

    def get_primitive_type(self) -> str:
        return "sentiment_analysis"

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to analyze for sentiment"
                },
                "language": {
                    "type": "string",
                    "default": "en",
                    "description": "Language of the text"
                }
            },
            "required": ["text"]
        }

    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "sentiment": {
                    "type": "string",
                    "enum": ["positive", "negative", "neutral"],
                    "description": "Detected sentiment"
                },
                "confidence": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "Confidence score"
                },
                "details": {
                    "type": "object",
                    "description": "Detailed analysis results"
                }
            },
            "required": ["sentiment", "confidence"]
        }

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """Execute sentiment analysis."""
        text = inputs.get("text", "")
        language = inputs.get("language", "en")

        # Simulate sentiment analysis (in real implementation, would use ML model)
        await asyncio.sleep(0.1)  # Simulate processing time

        # Simple keyword-based sentiment analysis for demo
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic"]
        negative_words = ["bad", "terrible", "awful", "horrible", "disappointing", "poor"]

        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count:
            sentiment = "positive"
            confidence = min(0.9, 0.5 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = min(0.9, 0.5 + (negative_count - positive_count) * 0.1)
        else:
            sentiment = "neutral"
            confidence = 0.5

        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "details": {
                "positive_indicators": positive_count,
                "negative_indicators": negative_count,
                "text_length": len(text),
                "language": language,
                "processing_time": 0.1
            }
        }


class DataTransformationPrimitive(CustomPrimitiveBase):
    """Example custom primitive for data transformation."""

    def get_primitive_type(self) -> str:
        return "data_transformation"

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "description": "Data to transform"
                },
                "transformation": {
                    "type": "string",
                    "enum": ["filter", "map", "reduce", "sort"],
                    "description": "Type of transformation to apply"
                },
                "parameters": {
                    "type": "object",
                    "description": "Parameters for the transformation"
                }
            },
            "required": ["data", "transformation"]
        }

    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "transformed_data": {
                    "description": "Transformed data"
                },
                "metadata": {
                    "type": "object",
                    "description": "Transformation metadata"
                }
            },
            "required": ["transformed_data"]
        }

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """Execute data transformation."""
        data = inputs.get("data", [])
        transformation = inputs.get("transformation", "filter")
        parameters = inputs.get("parameters", {})

        # Simulate processing time
        await asyncio.sleep(0.05)

        transformed_data = data.copy()

        if transformation == "filter":
            # Filter data based on criteria
            criteria = parameters.get("criteria", {})
            if criteria:
                # Simple filtering example
                key = criteria.get("key")
                value = criteria.get("value")
                if key and value is not None:
                    transformed_data = [item for item in data if isinstance(item, dict) and item.get(key) == value]

        elif transformation == "map":
            # Transform each item
            field = parameters.get("field")
            operation = parameters.get("operation", "identity")
            if field and operation == "uppercase":
                transformed_data = [
                    {**item, field: str(item.get(field, "")).upper()} if isinstance(item, dict) else item
                    for item in data
                ]

        elif transformation == "sort":
            # Sort data
            key = parameters.get("key")
            reverse = parameters.get("reverse", False)
            if key:
                transformed_data = sorted(data, key=lambda x: x.get(key, 0) if isinstance(x, dict) else x, reverse=reverse)

        elif transformation == "reduce":
            # Reduce data to a single value
            operation = parameters.get("operation", "sum")
            if operation == "sum" and all(isinstance(x, (int, float)) for x in data):
                transformed_data = sum(data)
            elif operation == "count":
                transformed_data = len(data)

        return {
            "transformed_data": transformed_data,
            "metadata": {
                "original_count": len(data),
                "transformed_count": len(transformed_data) if isinstance(transformed_data, list) else 1,
                "transformation": transformation,
                "parameters": parameters
            }
        }


class MockExternalServiceAdapter(ServiceAdapter):
    """Mock external service adapter for demonstration."""

    def get_metadata(self) -> ServiceAdapterMetadata:
        return ServiceAdapterMetadata(
            name="mock_external_service",
            version="1.0.0",
            service_type=ServiceType.CUSTOM,
            capabilities=[AdapterCapability.READ, AdapterCapability.QUERY],
            description="Mock external service for demonstration",
            author="DAIP-LIVE Team",
            configuration_schema={
                "type": "object",
                "properties": {
                    "api_key": {"type": "string"},
                    "endpoint": {"type": "string"}
                },
                "required": ["endpoint"]
            }
        )

    async def initialize(self) -> bool:
        """Initialize the mock service."""
        # Simulate initialization
        await asyncio.sleep(0.1)
        return True

    async def cleanup(self) -> None:
        """Clean up the mock service."""
        # Simulate cleanup
        await asyncio.sleep(0.05)

    async def health_check(self) -> bool:
        """Check service health."""
        # Simulate health check
        await asyncio.sleep(0.02)
        return True

    async def execute_request(self, request: ServiceRequest) -> ServiceResponse:
        """Execute a service request."""
        start_time = datetime.now()

        # Simulate processing
        await asyncio.sleep(0.1)

        if request.operation == "query_data":
            # Mock data query
            query = request.parameters.get("query", "")
            mock_data = [
                {"id": 1, "name": "Item 1", "value": 100},
                {"id": 2, "name": "Item 2", "value": 200},
                {"id": 3, "name": "Item 3", "value": 150}
            ]

            # Simple filtering
            if query:
                filtered_data = [item for item in mock_data if query.lower() in item["name"].lower()]
            else:
                filtered_data = mock_data

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds() * 1000

            return ServiceResponse(
                request_id=request.request_id,
                success=True,
                data=filtered_data,
                metadata={"query": query, "result_count": len(filtered_data)},
                duration_ms=duration
            )

        else:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds() * 1000

            return ServiceResponse(
                request_id=request.request_id,
                success=False,
                error=f"Unknown operation: {request.operation}",
                duration_ms=duration
            )


class ExampleCustomPrimitivesPlugin(PluginInterface):
    """Example plugin providing custom primitives."""

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="example_custom_primitives",
            version="1.0.0",
            author="DAIP-LIVE Team",
            description="Example plugin demonstrating custom primitives and service adapters",
            dependencies=[],
            primitive_types=["sentiment_analysis", "data_transformation"],
            service_adapters=["mock_external_service"]
        )

    def get_primitive_classes(self) -> Dict[str, type]:
        return {
            "sentiment_analysis": SentimentAnalysisPrimitive,
            "data_transformation": DataTransformationPrimitive
        }

    def get_service_adapters(self) -> Dict[str, Any]:
        return {
            "mock_external_service": MockExternalServiceAdapter
        }

    def initialize(self, context: Dict[str, Any]) -> bool:
        """Initialize the plugin."""
        # Plugin-specific initialization
        return True

    def cleanup(self) -> None:
        """Clean up plugin resources."""
        # Plugin-specific cleanup
        pass

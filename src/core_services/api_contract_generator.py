"""@Time    : 2025-08-06 09:15:00
@Author  : DAIP-LIVE Team
@File    : api_contract_generator.py
@Description:
    API Contract Generator and Documentation System
    Generates comprehensive API documentation with clear contracts for DAIP-LIVE services.
"""

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import yaml

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HTTPMethod(Enum):
    """HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class ParameterLocation(Enum):
    """Parameter location types."""
    PATH = "path"
    QUERY = "query"
    HEADER = "header"
    BODY = "body"


class DataType(Enum):
    """Data types for API parameters."""
    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


@dataclass
class APIParameter:
    """API parameter definition."""
    name: str
    type: DataType
    location: ParameterLocation
    required: bool = True
    description: str = ""
    default: Any = None
    example: Any = None
    format: Optional[str] = None
    enum: Optional[list[str]] = None
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    pattern: Optional[str] = None


@dataclass
class APIResponse:
    """API response definition."""
    status_code: int
    description: str
    content_type: str = "application/json"
    schema: Optional[dict[str, Any]] = None
    example: Optional[dict[str, Any]] = None
    headers: Optional[list[dict[str, Any]]] = None


@dataclass
class APIEndpoint:
    """API endpoint definition."""
    path: str
    method: HTTPMethod
    summary: str
    description: str
    parameters: list[APIParameter] = field(default_factory=list)
    responses: list[APIResponse] = field(default_factory=list)
    request_body: Optional[dict[str, Any]] = None
    tags: list[str] = field(default_factory=list)
    security: Optional[list[dict[str, Any]]] = None
    deprecated: bool = False


@dataclass
class APIService:
    """API service definition."""
    name: str
    version: str
    description: str
    base_url: str
    endpoints: list[APIEndpoint] = field(default_factory=list)
    common_parameters: list[APIParameter] = field(default_factory=list)
    security_schemes: Optional[dict[str, Any]] = None
    servers: list[dict[str, Any]] = field(default_factory=list)


class APIContractGenerator:
    """API contract generator and documentation system."""
    
    def __init__(self):
        self.services: dict[str, APIService] = {}
        self.contracts: dict[str, dict[str, Any]] = {}
        logger.info("API Contract Generator initialized")
    
    def register_service(self, service: APIService):
        """Register an API service."""
        self.services[service.name] = service
        logger.info(f"API service registered: {service.name}")
    
    def generate_openapi_spec(self, service_name: str) -> dict[str, Any]:
        """Generate OpenAPI specification for a service."""
        if service_name not in self.services:
            raise ValueError(f"Service not found: {service_name}")
        
        service = self.services[service_name]
        
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": service.name,
                "version": service.version,
                "description": service.description
            },
            "servers": service.servers,
            "paths": {},
            "components": {
                "securitySchemes": service.security_schemes or {}
            }
        }
        
        # Convert endpoints to OpenAPI format
        for endpoint in service.endpoints:
            path_spec = {
                endpoint.method.value.lower(): {
                    "summary": endpoint.summary,
                    "description": endpoint.description,
                    "tags": endpoint.tags,
                    "parameters": [self._param_to_openapi(param) for param in endpoint.parameters],
                    "responses": {str(resp.status_code): self._response_to_openapi(resp) for resp in endpoint.responses}
                }
            }
            
            if endpoint.request_body:
                path_spec[endpoint.method.value.lower()]["requestBody"] = endpoint.request_body
            
            if endpoint.security:
                path_spec[endpoint.method.value.lower()]["security"] = endpoint.security
            
            if endpoint.deprecated:
                path_spec[endpoint.method.value.lower()]["deprecated"] = True
            
            if endpoint.path not in spec["paths"]:
                spec["paths"][endpoint.path] = {}
            
            spec["paths"][endpoint.path].update(path_spec)
        
        return spec
    
    def generate_postman_collection(self, service_name: str) -> dict[str, Any]:
        """Generate Postman collection for a service."""
        if service_name not in self.services:
            raise ValueError(f"Service not found: {service_name}")
        
        service = self.services[service_name]
        
        collection = {
            "info": {
                "name": f"{service.name} API",
                "description": service.description,
                "version": service.version
            },
            "item": []
        }
        
        for endpoint in service.endpoints:
            item = {
                "name": endpoint.summary,
                "request": {
                    "method": endpoint.method.value,
                    "header": [],
                    "url": {
                        "raw": f"{service.base_url}{endpoint.path}",
                        "host": [service.base_url.replace("http://", "").replace("https://", "")],
                        "path": endpoint.path.lstrip("/").split("/")
                    }
                }
            }
            
            # Add parameters
            for param in endpoint.parameters:
                if param.location == ParameterLocation.QUERY:
                    item["request"]["url"]["query"] = item["request"]["url"].get("query", [])
                    item["request"]["url"]["query"].append({
                        "key": param.name,
                        "value": str(param.example or param.default or ""),
                        "description": param.description
                    })
                elif param.location == ParameterLocation.HEADER:
                    item["request"]["header"].append({
                        "key": param.name,
                        "value": str(param.example or param.default or ""),
                        "description": param.description
                    })
            
            # Add request body
            if endpoint.request_body:
                item["request"]["body"] = {
                    "mode": "raw",
                    "raw": json.dumps(endpoint.request_body.get("example", {}), indent=2),
                    "options": {
                        "raw": {
                            "language": "json"
                        }
                    }
                }
            
            # Add response examples
            if endpoint.responses:
                item["response"] = []
                for resp in endpoint.responses:
                    item["response"].append({
                        "name": f"{resp.status_code} {resp.description}",
                        "originalRequest": item["request"],
                        "status": "OK",
                        "code": resp.status_code,
                        "body": json.dumps(resp.example or {}, indent=2)
                    })
            
            collection["item"].append(item)
        
        return collection
    
    def _param_to_openapi(self, param: APIParameter) -> dict[str, Any]:
        """Convert API parameter to OpenAPI format."""
        openapi_param = {
            "name": param.name,
            "in": param.location.value,
            "description": param.description,
            "required": param.required,
            "schema": {"type": param.type.value}
        }
        
        if param.default is not None:
            openapi_param["schema"]["default"] = param.default
        
        if param.example is not None:
            openapi_param["example"] = param.example
        
        if param.format:
            openapi_param["schema"]["format"] = param.format
        
        if param.enum:
            openapi_param["schema"]["enum"] = param.enum
        
        if param.minimum is not None:
            openapi_param["schema"]["minimum"] = param.minimum
        
        if param.maximum is not None:
            openapi_param["schema"]["maximum"] = param.maximum
        
        if param.pattern:
            openapi_param["schema"]["pattern"] = param.pattern
        
        return openapi_param
    
    def _response_to_openapi(self, response: APIResponse) -> dict[str, Any]:
        """Convert API response to OpenAPI format."""
        openapi_response = {
            "description": response.description
        }
        
        if response.content_type == "application/json" and response.schema:
            openapi_response["content"] = {
                "application/json": {
                    "schema": response.schema
                }
            }
            
            if response.example:
                openapi_response["content"]["application/json"]["example"] = response.example
        
        if response.headers:
            openapi_response["headers"] = {h["name"]: h for h in response.headers}
        
        return openapi_response
    
    def save_documentation(self, service_name: str, output_dir: Path):
        """Save API documentation in multiple formats."""
        if service_name not in self.services:
            raise ValueError(f"Service not found: {service_name}")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate OpenAPI spec
        openapi_spec = self.generate_openapi_spec(service_name)
        with open(output_dir / f"{service_name}_openapi.json", "w") as f:
            json.dump(openapi_spec, f, indent=2)
        
        with open(output_dir / f"{service_name}_openapi.yaml", "w") as f:
            yaml.dump(openapi_spec, f, default_flow_style=False)
        
        # Generate Postman collection
        postman_collection = self.generate_postman_collection(service_name)
        with open(output_dir / f"{service_name}_postman.json", "w") as f:
            json.dump(postman_collection, f, indent=2)
        
        # Generate HTML documentation
        html_docs = self._generate_html_docs(service_name)
        with open(output_dir / f"{service_name}_docs.html", "w") as f:
            f.write(html_docs)
        
        logger.info(f"Documentation saved for {service_name} in {output_dir}")
    
    def _generate_html_docs(self, service_name: str) -> str:
        """Generate HTML documentation."""
        service = self.services[service_name]
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{service.name} API Documentation</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #f8f9fa; padding: 20px; border-radius: 5px; }}
        .endpoint {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .method {{ padding: 4px 8px; border-radius: 3px; color: white; font-weight: bold; }}
        .get {{ background: #28a745; }}
        .post {{ background: #007bff; }}
        .put {{ background: #ffc107; color: black; }}
        .delete {{ background: #dc3545; }}
        .parameters {{ margin: 10px 0; }}
        .responses {{ margin: 10px 0; }}
        .parameter {{ margin: 5px 0; padding: 5px; background: #f8f9fa; }}
        .response {{ margin: 5px 0; padding: 5px; background: #f8f9fa; }}
        pre {{ background: #f8f9fa; padding: 10px; border-radius: 3px; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{service.name} API</h1>
        <p>Version: {service.version}</p>
        <p>{service.description}</p>
        <p>Base URL: {service.base_url}</p>
    </div>
"""
        
        for endpoint in service.endpoints:
            html += f"""
    <div class="endpoint">
        <h3><span class="method {endpoint.method.value.lower()}">{endpoint.method.value}</span> {endpoint.path}</h3>
        <p><strong>Summary:</strong> {endpoint.summary}</p>
        <p><strong>Description:</strong> {endpoint.description}</p>
"""
            
            if endpoint.parameters:
                html += """
        <div class="parameters">
            <h4>Parameters</h4>
"""
                for param in endpoint.parameters:
                    html += f"""
            <div class="parameter">
                <strong>{param.name}</strong> ({param.type.value}, {param.location.value})
                <br>Required: {param.required}
                <br>Description: {param.description}
"""
                    if param.example:
                        html += f"<br>Example: {param.example}"
                    html += "</div>"
                html += "</div>"
            
            if endpoint.responses:
                html += """
        <div class="responses">
            <h4>Responses</h4>
"""
                for resp in endpoint.responses:
                    html += f"""
            <div class="response">
                <strong>{resp.status_code}</strong> - {resp.description}
"""
                    if resp.example:
                        html += f"<pre>{json.dumps(resp.example, indent=2)}</pre>"
                    html += "</div>"
                html += "</div>"
            
            html += "</div>"
        
        html += """
</body>
</html>
"""
        return html


# DAIP-LIVE API Contracts
def create_daip_api_contracts():
    """Create API contracts for DAIP-LIVE services."""
    generator = APIContractGenerator()
    
    # Backend API Service
    backend_service = APIService(
        name="DAIP-LIVE Backend API",
        version="1.0.0",
        description="Core backend API for DAIP-LIVE intelligent collaboration platform",
        base_url="http://localhost:8002",
        servers=[
            {
                "url": "http://localhost:8002",
                "description": "Development server"
            },
            {
                "url": "https://api.daip-live.com",
                "description": "Production server"
            }
        ],
        security_schemes={
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }
    )
    
    # Health Check Endpoint
    backend_service.endpoints.append(APIEndpoint(
        path="/health",
        method=HTTPMethod.GET,
        summary="Health Check",
        description="Check the health status of the backend service",
        responses=[
            APIResponse(
                status_code=200,
                description="Service is healthy",
                example={
                    "status": "healthy",
                    "timestamp": "2025-08-06T09:15:00Z",
                    "version": "1.0.0",
                    "uptime": 3600
                }
            ),
            APIResponse(
                status_code=503,
                description="Service is unhealthy"
            )
        ],
        tags=["system"]
    ))
    
    # Scenario Execution Endpoint
    backend_service.endpoints.append(APIEndpoint(
        path="/scenarios/execute",
        method=HTTPMethod.POST,
        summary="Execute Scenario",
        description="Execute a specific scenario with given parameters",
        parameters=[
            APIParameter(
                name="scenario_type",
                type=DataType.STRING,
                location=ParameterLocation.BODY,
                required=True,
                description="Type of scenario to execute",
                enum=["expert_consultation", "academic_research", "industry_analysis"]
            ),
            APIParameter(
                name="topic",
                type=DataType.STRING,
                location=ParameterLocation.BODY,
                required=True,
                description="Topic or query for the scenario"
            ),
            APIParameter(
                name="user_preferences",
                type=DataType.OBJECT,
                location=ParameterLocation.BODY,
                required=False,
                description="User preferences and configuration"
            )
        ],
        responses=[
            APIResponse(
                status_code=200,
                description="Scenario execution successful",
                example={
                    "success": True,
                    "scenario_id": "scenario_123",
                    "result": {
                        "summary": "Scenario execution completed successfully",
                        "expert_participants": ["expert_1", "expert_2"],
                        "confidence_score": 0.85
                    }
                }
            ),
            APIResponse(
                status_code=400,
                description="Invalid request parameters"
            )
        ],
        request_body={
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "scenario_type": {"type": "string", "enum": ["expert_consultation", "academic_research", "industry_analysis"]},
                            "topic": {"type": "string"},
                            "user_preferences": {"type": "object"}
                        },
                        "required": ["scenario_type", "topic"]
                    }
                }
            },
            "example": {
                "scenario_type": "expert_consultation",
                "topic": "AI system architecture optimization",
                "user_preferences": {
                    "depth": "detailed",
                    "experts": 3
                }
            }
        },
        tags=["scenarios"]
    ))
    
    # Role Management Endpoint
    backend_service.endpoints.append(APIEndpoint(
        path="/roles",
        method=HTTPMethod.GET,
        summary="List Available Roles",
        description="Get a list of all available AI roles",
        responses=[
            APIResponse(
                status_code=200,
                description="List of roles retrieved successfully",
                example={
                    "roles": [
                        {
                            "id": "tech_expert",
                            "name": "Technology Expert",
                            "description": "Expert in technology and software development",
                            "specializations": ["AI", "Software Architecture", "System Design"]
                        }
                    ],
                    "total_count": 131
                }
            )
        ],
        tags=["roles"]
    ))
    
    # Memory Service Endpoint
    backend_service.endpoints.append(APIEndpoint(
        path="/memory/search",
        method=HTTPMethod.POST,
        summary="Search Memory",
        description="Search the knowledge memory for relevant information",
        parameters=[
            APIParameter(
                name="query",
                type=DataType.STRING,
                location=ParameterLocation.BODY,
                required=True,
                description="Search query"
            ),
            APIParameter(
                name="limit",
                type=DataType.INTEGER,
                location=ParameterLocation.BODY,
                required=False,
                description="Maximum number of results",
                default=10,
                minimum=1,
                maximum=100
            )
        ],
        responses=[
            APIResponse(
                status_code=200,
                description="Search completed successfully",
                example={
                    "results": [
                        {
                            "id": "memory_123",
                            "content": "AI system architecture best practices",
                            "relevance_score": 0.92,
                            "timestamp": "2025-08-06T09:00:00Z"
                        }
                    ],
                    "total_results": 5
                }
            )
        ],
        tags=["memory"]
    ))
    
    # Wiki Service Endpoint
    backend_service.endpoints.append(APIEndpoint(
        path="/wiki/pages",
        method=HTTPMethod.GET,
        summary="List Wiki Pages",
        description="Get a list of all wiki pages",
        parameters=[
            APIParameter(
                name="category",
                type=DataType.STRING,
                location=ParameterLocation.QUERY,
                required=False,
                description="Filter by category"
            ),
            APIParameter(
                name="limit",
                type=DataType.INTEGER,
                location=ParameterLocation.QUERY,
                required=False,
                description="Maximum number of results",
                default=20
            )
        ],
        responses=[
            APIResponse(
                status_code=200,
                description="Wiki pages retrieved successfully",
                example={
                    "pages": [
                        {
                            "id": "wiki_123",
                            "title": "System Architecture",
                            "category": "technical",
                            "last_modified": "2025-08-06T09:00:00Z",
                            "version": 3
                        }
                    ],
                    "total_pages": 45
                }
            )
        ],
        tags=["wiki"]
    ))
    
    generator.register_service(backend_service)
    
    # Web Interface Service
    web_service = APIService(
        name="DAIP-LIVE Web Interface",
        version="1.0.0",
        description="Web interface API for DAIP-LIVE platform",
        base_url="http://localhost:8001",
        servers=[
            {
                "url": "http://localhost:8001",
                "description": "Development server"
            },
            {
                "url": "https://app.daip-live.com",
                "description": "Production server"
            }
        ]
    )
    
    # Chat Interface Endpoint
    web_service.endpoints.append(APIEndpoint(
        path="/chat",
        method=HTTPMethod.POST,
        summary="Chat Interface",
        description="Process user chat input and generate response",
        parameters=[
            APIParameter(
                name="user_input",
                type=DataType.STRING,
                location=ParameterLocation.BODY,
                required=True,
                description="User input text"
            ),
            APIParameter(
                name="session_id",
                type=DataType.STRING,
                location=ParameterLocation.BODY,
                required=False,
                description="Session identifier for conversation context"
            ),
            APIParameter(
                name="user_preferences",
                type=DataType.OBJECT,
                location=ParameterLocation.BODY,
                required=False,
                description="User preferences and settings"
            )
        ],
        responses=[
            APIResponse(
                status_code=200,
                description="Chat response generated successfully",
                example={
                    "success": True,
                    "response": "I understand your question about AI system architecture. Let me help you with that...",
                    "session_id": "session_123",
                    "processing_time": 2.5
                }
            )
        ],
        tags=["chat"]
    ))
    
    # Scenario Interface Endpoint
    web_service.endpoints.append(APIEndpoint(
        path="/scenario",
        method=HTTPMethod.POST,
        summary="Execute Scenario via Web Interface",
        description="Execute a scenario through the web interface",
        parameters=[
            APIParameter(
                name="topic",
                type=DataType.STRING,
                location=ParameterLocation.BODY,
                required=True,
                description="Topic for scenario execution"
            ),
            APIParameter(
                name="scenario_type",
                type=DataType.STRING,
                location=ParameterLocation.BODY,
                required=True,
                description="Type of scenario to execute",
                enum=["expert_consultation", "academic_research", "industry_analysis"]
            )
        ],
        responses=[
            APIResponse(
                status_code=200,
                description="Scenario execution initiated",
                example={
                    "success": True,
                    "scenario_id": "scenario_456",
                    "status": "processing",
                    "estimated_completion_time": 30
                }
            )
        ],
        tags=["scenarios"]
    ))
    
    generator.register_service(web_service)
    
    return generator


if __name__ == "__main__":
    # Generate API documentation
    generator = create_daip_api_contracts()
    
    # Save documentation
    output_dir = Path("docs/api_contracts")
    generator.save_documentation("DAIP-LIVE Backend API", output_dir)
    generator.save_documentation("DAIP-LIVE Web Interface", output_dir)
    
    print("API documentation generated successfully!")
    print(f"Documentation saved to: {output_dir}")
# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-06 10:00:00
@Author  : DAIP-LIVE Team
@File    : api_gateway.py
@Description:
    API Gateway for Unified Endpoint Management
    Provides centralized routing, load balancing, authentication, and monitoring for DAIP-LIVE services.
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import aiohttp
from aiohttp import web
import jwt
import hashlib
from pathlib import Path

# Import service registry
from .service_discovery_registry import ServiceRegistry, ServiceInstance, ServiceQuery

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GatewayEventType(Enum):
    """Gateway event types."""
    REQUEST_RECEIVED = "request_received"
    REQUEST_PROCESSED = "request_processed"
    REQUEST_FAILED = "request_failed"
    AUTHENTICATION_FAILED = "authentication_failed"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    ROUTING_ERROR = "routing_error"


@dataclass
class GatewayConfig:
    """API Gateway configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    secret_key: str = "your-secret-key-here"
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600  # 1 hour
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    request_timeout: int = 30  # seconds
    enable_cors: bool = True
    enable_metrics: bool = True
    enable_auth: bool = True
    log_level: str = "INFO"


@dataclass
class RouteConfig:
    """Route configuration."""
    path: str
    method: str
    service_name: str
    service_path: str = ""
    auth_required: bool = True
    rate_limit: Optional[int] = None
    timeout: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GatewayRequest:
    """Gateway request wrapper."""
    request_id: str
    timestamp: datetime
    method: str
    path: str
    headers: Dict[str, str]
    body: Optional[Dict[str, Any]]
    client_ip: str
    user_agent: str
    user_id: Optional[str] = None


@dataclass
class GatewayResponse:
    """Gateway response wrapper."""
    request_id: str
    status_code: int
    headers: Dict[str, str]
    body: Any
    processing_time: float
    service_name: str
    error_message: Optional[str] = None


@dataclass
class GatewayMetrics:
    """Gateway metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    requests_per_second: float = 0.0
    active_connections: int = 0
    service_metrics: Dict[str, Dict[str, Any]] = field(default_factory=dict)


class RateLimiter:
    """Rate limiting implementation."""
    
    def __init__(self, requests_per_window: int, window_size: int):
        self.requests_per_window = requests_per_window
        self.window_size = window_size
        self.requests: Dict[str, List[float]] = {}
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed based on rate limit."""
        current_time = time.time()
        
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Remove old requests
        window_start = current_time - self.window_size
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > window_start
        ]
        
        # Check if within limit
        if len(self.requests[client_id]) >= self.requests_per_window:
            return False
        
        # Add current request
        self.requests[client_id].append(current_time)
        return True


class AuthenticationManager:
    """Authentication and authorization manager."""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.api_keys: Dict[str, Dict[str, Any]] = {}
    
    def generate_jwt(self, user_id: str, payload: Dict[str, Any] = None) -> str:
        """Generate JWT token."""
        current_time = datetime.utcnow()
        
        jwt_payload = {
            "user_id": user_id,
            "iat": current_time,
            "exp": current_time.timestamp() + 3600  # 1 hour expiration
        }
        
        if payload:
            jwt_payload.update(payload)
        
        return jwt.encode(jwt_payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_jwt(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None
    
    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key."""
        if api_key in self.api_keys:
            return self.api_keys[api_key]
        return None
    
    def add_api_key(self, api_key: str, user_id: str, permissions: List[str] = None):
        """Add API key."""
        self.api_keys[api_key] = {
            "user_id": user_id,
            "permissions": permissions or [],
            "created_at": datetime.utcnow().isoformat()
        }


class APIGateway:
    """API Gateway for DAIP-LIVE services."""
    
    def __init__(self, config: GatewayConfig, service_registry: ServiceRegistry):
        self.config = config
        self.service_registry = service_registry
        self.app = web.Application()
        self.rate_limiter = RateLimiter(
            config.rate_limit_requests, 
            config.rate_limit_window
        )
        self.auth_manager = AuthenticationManager(config.secret_key, config.jwt_algorithm)
        self.metrics = GatewayMetrics()
        self.event_handlers: Dict[GatewayEventType, List[Callable]] = {}
        self.routes: Dict[str, RouteConfig] = {}
        
        # Setup routes
        self._setup_routes()
        
        logger.info("API Gateway initialized")
    
    def _setup_routes(self):
        """Setup gateway routes."""
        # Health check
        self.app.router.add_get('/health', self._health_check)
        
        # Metrics
        self.app.router.add_get('/metrics', self._get_metrics)
        
        # Gateway API
        self.app.router.add_post('/auth/login', self._login)
        self.app.router.add_post('/auth/api-key', self._create_api_key)
        
        # Dynamic routing
        self.app.router.add_route('*', '/{path:.*}', self._proxy_request)
    
    def add_route(self, route_config: RouteConfig):
        """Add a route configuration."""
        route_key = f"{route_config.method.upper()}:{route_config.path}"
        self.routes[route_key] = route_config
        logger.info(f"Added route: {route_key}")
    
    def add_event_handler(self, event_type: GatewayEventType, handler: Callable):
        """Add event handler."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def _emit_event(self, event_type: GatewayEventType, data: Dict[str, Any]):
        """Emit gateway event."""
        if event_type in self.event_handlers:
            event_data = {
                "event_type": event_type.value,
                "timestamp": datetime.now().isoformat(),
                "data": data
            }
            
            for handler in self.event_handlers[event_type]:
                try:
                    handler(event_data)
                except Exception as e:
                    logger.error(f"Error in event handler: {e}")
    
    async def _health_check(self, request: web.Request) -> web.Response:
        """Gateway health check."""
        return web.json_response({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "services": self.service_registry.get_registry_stats()
        })
    
    async def _get_metrics(self, request: web.Request) -> web.Response:
        """Get gateway metrics."""
        return web.json_response(self.metrics.__dict__)
    
    async def _login(self, request: web.Request) -> web.Response:
        """User login endpoint."""
        try:
            data = await request.json()
            username = data.get("username")
            password = data.get("password")
            
            # Simple authentication (in production, use proper auth system)
            if username == "admin" and password == "admin":
                token = self.auth_manager.generate_jwt(username)
                return web.json_response({
                    "access_token": token,
                    "token_type": "bearer",
                    "expires_in": 3600
                })
            else:
                return web.json_response(
                    {"error": "Invalid credentials"},
                    status=401
                )
        except Exception as e:
            logger.error(f"Login error: {e}")
            return web.json_response(
                {"error": "Authentication failed"},
                status=500
            )
    
    async def _create_api_key(self, request: web.Request) -> web.Response:
        """Create API key."""
        try:
            # Extract user info from JWT
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return web.json_response(
                    {"error": "Invalid authorization header"},
                    status=401
                )
            
            token = auth_header[7:]
            payload = self.auth_manager.verify_jwt(token)
            if not payload:
                return web.json_response(
                    {"error": "Invalid token"},
                    status=401
                )
            
            # Generate API key
            api_key = hashlib.sha256(f"{payload['user_id']}:{time.time()}".encode()).hexdigest()
            self.auth_manager.add_api_key(api_key, payload['user_id'])
            
            return web.json_response({
                "api_key": api_key,
                "user_id": payload['user_id']
            })
        except Exception as e:
            logger.error(f"API key creation error: {e}")
            return web.json_response(
                {"error": "Failed to create API key"},
                status=500
            )
    
    async def _handle_cors(self, request: web.Request) -> web.Response:
        """Handle CORS preflight requests."""
        return web.Response(
            status=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
    
    async def _proxy_request(self, request: web.Request) -> web.Response:
        """Proxy request to appropriate service."""
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Extract client info
        client_ip = request.remote or request.headers.get("X-Forwarded-For", "")
        user_agent = request.headers.get("User-Agent", "")
        
        # Create gateway request
        gateway_request = GatewayRequest(
            request_id=request_id,
            timestamp=datetime.now(),
            method=request.method,
            path=request.path,
            headers=dict(request.headers),
            body=None,
            client_ip=client_ip,
            user_agent=user_agent
        )
        
        try:
            # Emit request received event
            self._emit_event(GatewayEventType.REQUEST_RECEIVED, {
                "request_id": request_id,
                "method": request.method,
                "path": request.path,
                "client_ip": client_ip
            })
            
            # Parse request body
            if request.method in ["POST", "PUT", "PATCH"]:
                try:
                    gateway_request.body = await request.json()
                except:
                    gateway_request.body = await request.text()
            
            # Route request
            route_config = self._find_route(request.method, request.path)
            if not route_config:
                return web.json_response(
                    {"error": "Route not found"},
                    status=404
                )
            
            # Authentication
            if route_config.auth_required and self.config.enable_auth:
                auth_result = await self._authenticate(request)
                if not auth_result:
                    self._emit_event(GatewayEventType.AUTHENTICATION_FAILED, {
                        "request_id": request_id,
                        "path": request.path
                    })
                    return web.json_response(
                        {"error": "Authentication required"},
                        status=401
                    )
                gateway_request.user_id = auth_result.get("user_id")
            
            # Rate limiting
            client_id = f"{client_ip}:{gateway_request.user_id or 'anonymous'}"
            if not self.rate_limiter.is_allowed(client_id):
                self._emit_event(GatewayEventType.RATE_LIMIT_EXCEEDED, {
                    "request_id": request_id,
                    "client_id": client_id
                })
                return web.json_response(
                    {"error": "Rate limit exceeded"},
                    status=429
                )
            
            # Find service instance
            service_instances = self.service_registry.get_service_instances(route_config.service_name)
            if not service_instances:
                self._emit_event(GatewayEventType.ROUTING_ERROR, {
                    "request_id": request_id,
                    "error": "No service instances available",
                    "service_name": route_config.service_name
                })
                return web.json_response(
                    {"error": "Service unavailable"},
                    status=503
                )
            
            # Simple load balancing (round-robin)
            service_instance = service_instances[0]  # TODO: Implement proper load balancing
            
            # Forward request to service
            response = await self._forward_request(
                gateway_request,
                service_instance,
                route_config
            )
            
            # Update metrics
            processing_time = time.time() - start_time
            self._update_metrics(response, processing_time, route_config.service_name)
            
            # Emit request processed event
            self._emit_event(GatewayEventType.REQUEST_PROCESSED, {
                "request_id": request_id,
                "processing_time": processing_time,
                "status_code": response.status_code,
                "service_name": route_config.service_name
            })
            
            # Add CORS headers
            if self.config.enable_cors:
                response.headers.update({
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization"
                })
            
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_response = web.json_response(
                {"error": "Internal server error"},
                status=500
            )
            
            # Update metrics
            self._update_metrics(error_response, processing_time, "gateway")
            
            # Emit request failed event
            self._emit_event(GatewayEventType.REQUEST_FAILED, {
                "request_id": request_id,
                "error": str(e),
                "processing_time": processing_time
            })
            
            logger.error(f"Request processing error: {e}")
            return error_response
    
    def _find_route(self, method: str, path: str) -> Optional[RouteConfig]:
        """Find route configuration for request."""
        route_key = f"{method.upper()}:{path}"
        
        # Exact match
        if route_key in self.routes:
            return self.routes[route_key]
        
        # Pattern matching
        for route_key, route_config in self.routes.items():
            if self._path_matches(path, route_config.path):
                return route_config
        
        return None
    
    def _path_matches(self, request_path: str, route_path: str) -> bool:
        """Check if request path matches route pattern."""
        # Simple pattern matching (can be enhanced with proper regex)
        if route_path.endswith("*"):
            return request_path.startswith(route_path[:-1])
        return request_path == route_path
    
    async def _authenticate(self, request: web.Request) -> Optional[Dict[str, Any]]:
        """Authenticate request."""
        auth_header = request.headers.get("Authorization", "")
        
        # Bearer token
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            return self.auth_manager.verify_jwt(token)
        
        # API key
        elif auth_header.startswith("ApiKey "):
            api_key = auth_header[7:]
            return self.auth_manager.validate_api_key(api_key)
        
        return None
    
    async def _forward_request(self, gateway_request: GatewayRequest,
                            service_instance: ServiceInstance,
                            route_config: RouteConfig) -> web.Response:
        """Forward request to service instance."""
        service_url = f"http://{service_instance.host}:{service_instance.port}"
        target_path = route_config.service_path or gateway_request.path
        
        # Prepare headers
        headers = {}
        for key, value in gateway_request.headers.items():
            if not key.lower().startswith("x-"):
                headers[key] = value
        
        # Add gateway headers
        headers["X-Request-ID"] = gateway_request.request_id
        headers["X-Forwarded-For"] = gateway_request.client_ip
        headers["X-User-ID"] = gateway_request.user_id or ""
        
        timeout = aiohttp.ClientTimeout(total=route_config.timeout or self.config.request_timeout)
        
        async with aiohttp.ClientSession() as session:
            try:
                if gateway_request.method == "GET":
                    async with session.get(
                        f"{service_url}{target_path}",
                        headers=headers,
                        timeout=timeout
                    ) as response:
                        body = await response.text()
                        return web.Response(
                            text=body,
                            status=response.status,
                            headers=dict(response.headers)
                        )
                
                elif gateway_request.method == "POST":
                    async with session.post(
                        f"{service_url}{target_path}",
                        json=gateway_request.body,
                        headers=headers,
                        timeout=timeout
                    ) as response:
                        body = await response.text()
                        return web.Response(
                            text=body,
                            status=response.status,
                            headers=dict(response.headers)
                        )
                
                # Add other methods as needed
                else:
                    return web.json_response(
                        {"error": "Method not supported"},
                        status=405
                    )
            
            except asyncio.TimeoutError:
                return web.json_response(
                    {"error": "Service timeout"},
                    status=504
                )
            except Exception as e:
                logger.error(f"Service request error: {e}")
                return web.json_response(
                    {"error": "Service unavailable"},
                    status=503
                )
    
    def _update_metrics(self, response: web.Response, processing_time: float, service_name: str):
        """Update gateway metrics."""
        self.metrics.total_requests += 1
        
        if response.status < 400:
            self.metrics.successful_requests += 1
        else:
            self.metrics.failed_requests += 1
        
        # Update average response time
        total_time = self.metrics.average_response_time * (self.metrics.total_requests - 1)
        self.metrics.average_response_time = (total_time + processing_time) / self.metrics.total_requests
        
        # Update service metrics
        if service_name not in self.metrics.service_metrics:
            self.metrics.service_metrics[service_name] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "average_response_time": 0.0
            }
        
        service_metrics = self.metrics.service_metrics[service_name]
        service_metrics["total_requests"] += 1
        
        if response.status < 400:
            service_metrics["successful_requests"] += 1
        else:
            service_metrics["failed_requests"] += 1
        
        # Update service average response time
        total_time = service_metrics["average_response_time"] * (service_metrics["total_requests"] - 1)
        service_metrics["average_response_time"] = (total_time + processing_time) / service_metrics["total_requests"]
    
    async def start(self):
        """Start the API gateway."""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.config.host, self.config.port)
        await site.start()
        
        logger.info(f"API Gateway started on {self.config.host}:{self.config.port}")
        return runner, site


# DAIP-LIVE API Gateway Setup
def create_daip_api_gateway(service_registry: ServiceRegistry):
    """Create and configure DAIP-LIVE API Gateway."""
    config = GatewayConfig(
        host="0.0.0.0",
        port=8000,
        secret_key="daip-live-secret-key-change-in-production",
        enable_cors=True,
        enable_metrics=True,
        enable_auth=True
    )
    
    gateway = APIGateway(config, service_registry)
    
    # Add routes
    routes = [
        RouteConfig(
            path="/api/health",
            method="GET",
            service_name="backend_api",
            service_path="/health",
            auth_required=False
        ),
        RouteConfig(
            path="/api/scenarios/execute",
            method="POST",
            service_name="backend_api",
            service_path="/scenarios/execute",
            auth_required=True
        ),
        RouteConfig(
            path="/api/roles",
            method="GET",
            service_name="backend_api",
            service_path="/roles",
            auth_required=True
        ),
        RouteConfig(
            path="/api/memory/*",
            method="*",
            service_name="backend_api",
            service_path="/memory/",
            auth_required=True
        ),
        RouteConfig(
            path="/api/wiki/*",
            method="*",
            service_name="backend_api",
            service_path="/wiki/",
            auth_required=True
        ),
        RouteConfig(
            path="/chat",
            method="POST",
            service_name="web_interface",
            service_path="/chat",
            auth_required=True
        ),
        RouteConfig(
            path="/scenario",
            method="POST",
            service_name="web_interface",
            service_path="/scenario",
            auth_required=True
        )
    ]
    
    for route in routes:
        gateway.add_route(route)
    
    return gateway


if __name__ == "__main__":
    # Example usage
    async def main():
        from .service_discovery_registry import create_daip_service_registry
        
        # Create service registry
        service_registry = create_daip_service_registry()
        await service_registry.start()
        
        # Create API gateway
        gateway = create_daip_api_gateway(service_registry)
        
        # Add event handler for logging
        def log_event(event):
            print(f"[{event['timestamp']}] {event['event_type']}: {event['data']}")
        
        for event_type in GatewayEventType:
            gateway.add_event_handler(event_type, log_event)
        
        # Start gateway
        runner, site = await gateway.start()
        
        try:
            # Keep running
            while True:
                await asyncio.sleep(60)
        except KeyboardInterrupt:
            await runner.cleanup()
            await service_registry.stop()
    
    asyncio.run(main())
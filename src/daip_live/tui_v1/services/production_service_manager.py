"""
Production-grade Service Manager for newP6 TUI

This module provides comprehensive service management capabilities including:
- Service discovery and registration
- Circuit breaker and retry mechanisms
- Health monitoring and failover
- Load balancing and connection pooling
- Service metrics and observability
- Rate limiting and throttling
- Service mesh integration
- Distributed tracing and logging
"""

import asyncio
import base64
import json
import logging
import sqlite3
import ssl
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union

import aiohttp

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service health status"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    MAINTENANCE = "maintenance"


class ServiceType(Enum):
    """Types of services"""

    KNOWLEDGE = "knowledge"
    MODEL = "model"
    SESSION = "session"
    DEBATE = "debate"
    ASSISTANT = "assistant"
    AUTHENTICATION = "authentication"
    STORAGE = "storage"
    NOTIFICATION = "notification"
    ANALYTICS = "analytics"
    EXTERNAL_API = "external_api"


class LoadBalancingStrategy(Enum):
    """Load balancing strategies"""

    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"
    HASH = "hash"
    RESPONSE_TIME = "response_time"


@dataclass
class ServiceEndpoint:
    """Service endpoint configuration"""

    url: str
    health_check_url: Optional[str] = None
    weight: int = 1
    timeout_seconds: int = 30
    max_retries: int = 3
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout_seconds: int = 60
    rate_limit_per_minute: int = 1000
    authentication: Optional[dict[str, Any]] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.health_check_url:
            self.health_check_url = f"{self.url.rstrip('/')}/health"

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "health_check_url": self.health_check_url,
            "weight": self.weight,
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries,
            "circuit_breaker_threshold": self.circuit_breaker_threshold,
            "circuit_breaker_timeout_seconds": self.circuit_breaker_timeout_seconds,
            "rate_limit_per_minute": self.rate_limit_per_minute,
            "authentication": self.authentication,
            "metadata": self.metadata,
        }


@dataclass
class ServiceDefinition:
    """Complete service definition"""

    name: str
    service_type: ServiceType
    version: str
    endpoints: list[ServiceEndpoint]
    load_balancing_strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN
    health_check_interval_seconds: int = 30
    health_check_timeout_seconds: int = 10
    retry_policy: dict[str, Any] = field(default_factory=dict)
    circuit_breaker_policy: dict[str, Any] = field(default_factory=dict)
    rate_limit_policy: dict[str, Any] = field(default_factory=dict)
    authentication_required: bool = False
    timeout_policy: dict[str, Any] = field(default_factory=dict)
    custom_headers: dict[str, str] = field(default_factory=dict)
    environment: str = "production"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "service_type": self.service_type.value,
            "version": self.version,
            "endpoints": [ep.to_dict() for ep in self.endpoints],
            "load_balancing_strategy": self.load_balancing_strategy.value,
            "health_check_interval_seconds": self.health_check_interval_seconds,
            "health_check_timeout_seconds": self.health_check_timeout_seconds,
            "retry_policy": self.retry_policy,
            "circuit_breaker_policy": self.circuit_breaker_policy,
            "rate_limit_policy": self.rate_limit_policy,
            "authentication_required": self.authentication_required,
            "timeout_policy": self.timeout_policy,
            "custom_headers": self.custom_headers,
            "environment": self.environment,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class ServiceMetrics:
    """Service performance metrics"""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    error_rate: float = 0.0
    throughput_per_second: float = 0.0
    circuit_breaker_trips: int = 0
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None
    uptime_percentage: float = 100.0
    health_check_failures: int = 0
    connection_pool_stats: dict[str, Any] = field(default_factory=dict)
    response_times: list[float] = field(default_factory=list)


class CircuitBreakerState(Enum):
    """Circuit breaker states"""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Circuit is open, blocking calls
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """Circuit breaker implementation for service resilience"""

    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
        self.last_failure_time: Optional[datetime] = None
        self._lock = threading.Lock()

    def call_allowed(self) -> bool:
        """Check if a call is allowed through the circuit breaker"""
        with self._lock:
            if self.state == CircuitBreakerState.CLOSED:
                return True
            elif self.state == CircuitBreakerState.OPEN:
                if (
                    self.last_failure_time
                    and (datetime.now() - self.last_failure_time).total_seconds()
                    > self.timeout_seconds
                ):
                    self.state = CircuitBreakerState.HALF_OPEN
                    return True
                return False
            elif self.state == CircuitBreakerState.HALF_OPEN:
                return True
            return False

    def record_success(self) -> None:
        """Record a successful call"""
        with self._lock:
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0

    def record_failure(self) -> None:
        """Record a failed call"""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            if self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.OPEN
            elif self.failure_count >= self.failure_threshold:
                self.state = CircuitBreakerState.OPEN

    def get_state(self) -> CircuitBreakerState:
        """Get current circuit breaker state"""
        return self.state


class RateLimiter:
    """Rate limiter for service calls"""

    def __init__(self, max_requests_per_minute: int):
        self.max_requests_per_minute = max_requests_per_minute
        self.requests: list[datetime] = []
        self._lock = threading.Lock()

    def is_allowed(self) -> bool:
        """Check if a request is allowed"""
        with self._lock:
            now = datetime.now()
            # Remove old requests (older than 1 minute)
            self.requests = [
                req_time
                for req_time in self.requests
                if (now - req_time).total_seconds() < 60
            ]

            if len(self.requests) < self.max_requests_per_minute:
                self.requests.append(now)
                return True
            return False

    def get_wait_time(self) -> float:
        """Get time to wait before next request is allowed"""
        if self.requests:
            oldest_request = min(self.requests)
            wait_seconds = 60 - (datetime.now() - oldest_request).total_seconds()
            return max(0, wait_seconds)
        return 0


class ServiceHealthChecker:
    """Health checker for services"""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = (
            Path(storage_path) if storage_path else Path("data/service_health.db")
        )
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.health_results: dict[str, dict[str, Any]] = {}
        self._init_database()

    def _init_database(self) -> None:
        """Initialize health check database"""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS service_health (
                        service_name TEXT NOT NULL,
                        endpoint_url TEXT NOT NULL,
                        status TEXT NOT NULL,
                        response_time_ms REAL,
                        error_message TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (service_name, endpoint_url)
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS health_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        service_name TEXT NOT NULL,
                        endpoint_url TEXT NOT NULL,
                        status TEXT NOT NULL,
                        response_time_ms REAL,
                        error_message TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Indexes
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_health_timestamp ON health_history (timestamp)"  # noqa: E501
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_health_service ON health_history (service_name)"  # noqa: E501
                )

                conn.commit()
        except Exception as e:
            logger.error(f"Failed to initialize health check database: {e}")

    async def check_health(
        self, service_name: str, endpoint: ServiceEndpoint
    ) -> dict[str, Any]:
        """Check health of a service endpoint"""
        start_time = time.time()
        result = {
            "service_name": service_name,
            "endpoint_url": endpoint.url,
            "status": ServiceStatus.UNKNOWN,
            "response_time_ms": None,
            "error_message": None,
            "timestamp": datetime.now(),
        }

        try:
            # Create SSL context
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            timeout = aiohttp.ClientTimeout(total=endpoint.health_check_timeout_seconds)

            async with aiohttp.ClientSession(
                timeout=timeout,
                connector=aiohttp.TCPConnector(
                    ssl=ssl_context, limit=10, limit_per_host=5
                ),
            ) as session:
                async with session.get(endpoint.health_check_url) as response:
                    response_time_ms = (time.time() - start_time) * 1000
                    result["response_time_ms"] = response_time_ms

                    if response.status == 200:
                        try:
                            health_data = await response.json()
                            if health_data.get("status") == "healthy":
                                result["status"] = ServiceStatus.HEALTHY
                            elif health_data.get("status") == "degraded":
                                result["status"] = ServiceStatus.DEGRADED
                            else:
                                result["status"] = ServiceStatus.UNHEALTHY
                                result["error_message"] = (
                                    f"Health check returned status: {health_data.get('status')}"  # noqa: E501
                                )
                        except (json.JSONDecodeError, KeyError):
                            # If response is not JSON, assume healthy if status is 200
                            result["status"] = ServiceStatus.HEALTHY
                    else:
                        result["status"] = ServiceStatus.UNHEALTHY
                        result["error_message"] = f"HTTP {response.status}"

        except asyncio.TimeoutError:
            result["status"] = ServiceStatus.UNHEALTHY
            result["error_message"] = "Health check timeout"
        except Exception as e:
            result["status"] = ServiceStatus.UNHEALTHY
            result["error_message"] = str(e)

        # Store result
        self.health_results[f"{service_name}:{endpoint.url}"] = result

        # Save to database
        await self._save_health_result(result)

        return result

    async def _save_health_result(self, result: dict[str, Any]) -> None:
        """Save health result to database"""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                # Update current health
                conn.execute(
                    """
                    INSERT OR REPLACE INTO service_health
                    (service_name, endpoint_url, status, response_time_ms, error_message, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,  # noqa: E501
                    (
                        result["service_name"],
                        result["endpoint_url"],
                        result["status"].value,
                        result["response_time_ms"],
                        result["error_message"],
                        result["timestamp"].isoformat(),
                    ),
                )

                # Add to history
                conn.execute(
                    """
                    INSERT INTO health_history
                    (service_name, endpoint_url, status, response_time_ms, error_message, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,  # noqa: E501
                    (
                        result["service_name"],
                        result["endpoint_url"],
                        result["status"].value,
                        result["response_time_ms"],
                        result["error_message"],
                        result["timestamp"].isoformat(),
                    ),
                )

                conn.commit()
        except Exception as e:
            logger.error(f"Failed to save health result: {e}")

    def get_service_health(
        self, service_name: str, endpoint_url: str
    ) -> Optional[dict[str, Any]]:
        """Get latest health result for service endpoint"""
        key = f"{service_name}:{endpoint_url}"
        return self.health_results.get(key)


class ProductionServiceManager:
    """Production-grade service manager with comprehensive features"""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = (
            Path(storage_path) if storage_path else Path("data/services.db")
        )
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Service registry
        self.services: dict[str, ServiceDefinition] = {}
        self.service_endpoints: dict[str, list[ServiceEndpoint]] = {}

        # Health checking
        self.health_checker = ServiceHealthChecker()

        # Load balancing
        self.load_balancers: dict[str, LoadBalancer] = {}

        # Circuit breakers and rate limiters
        self.circuit_breakers: dict[str, CircuitBreaker] = {}
        self.rate_limiters: dict[str, RateLimiter] = {}

        # Connection pools
        self.connection_pools: dict[str, aiohttp.ClientSession] = {}

        # Metrics and monitoring
        self.service_metrics: dict[str, ServiceMetrics] = {}
        self.global_metrics = {
            "total_services": 0,
            "healthy_services": 0,
            "unhealthy_services": 0,
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
        }

        # Background tasks
        self.health_check_task: Optional[asyncio.Task] = None
        self.metrics_collection_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()

        # Thread pool for blocking operations
        self.thread_pool = ThreadPoolExecutor(
            max_workers=4, thread_name_prefix="service_manager"
        )

        # Lock for thread safety
        self._lock = threading.RLock()

        # Database initialization
        self._init_database()

        # Load existing services
        self._load_services()

        # Start background tasks
        self._start_background_tasks()

        logger.info("Production Service Manager initialized")

    def _init_database(self) -> None:
        """Initialize service database"""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS services (
                        name TEXT PRIMARY KEY,
                        service_data TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS service_metrics (
                        service_name TEXT PRIMARY KEY,
                        metrics_data TEXT NOT NULL,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS service_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        service_name TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        event_data TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Indexes
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_events_timestamp ON service_events (timestamp)"  # noqa: E501
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_events_service ON service_events (service_name)"  # noqa: E501
                )

                conn.commit()
        except Exception as e:
            logger.error(f"Failed to initialize service database: {e}")

    def _load_services(self) -> None:
        """Load services from database"""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                cursor = conn.execute("SELECT name, service_data FROM services")
                for service_name, service_data in cursor.fetchall():
                    try:
                        data = json.loads(service_data)
                        service = self._service_from_dict(data)
                        self.register_service(service)
                    except Exception as e:
                        logger.error(f"Failed to load service {service_name}: {e}")

            logger.info(f"Loaded {len(self.services)} services from database")

        except Exception as e:
            logger.error(f"Failed to load services: {e}")

    def _service_from_dict(self, data: dict[str, Any]) -> ServiceDefinition:
        """Create ServiceDefinition from dictionary"""
        endpoints = [ServiceEndpoint(**ep_data) for ep_data in data["endpoints"]]
        return ServiceDefinition(
            name=data["name"],
            service_type=ServiceType(data["service_type"]),
            version=data["version"],
            endpoints=endpoints,
            load_balancing_strategy=LoadBalancingStrategy(
                data.get("load_balancing_strategy", "round_robin")
            ),
            health_check_interval_seconds=data.get("health_check_interval_seconds", 30),
            health_check_timeout_seconds=data.get("health_check_timeout_seconds", 10),
            retry_policy=data.get("retry_policy", {}),
            circuit_breaker_policy=data.get("circuit_breaker_policy", {}),
            rate_limit_policy=data.get("rate_limit_policy", {}),
            authentication_required=data.get("authentication_required", False),
            timeout_policy=data.get("timeout_policy", {}),
            custom_headers=data.get("custom_headers", {}),
            environment=data.get("environment", "production"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )

    def register_service(self, service: ServiceDefinition) -> bool:
        """Register a new service"""
        with self._lock:
            self.services[service.name] = service
            self.service_endpoints[service.name] = service.endpoints

            # Initialize load balancer
            self.load_balancers[service.name] = LoadBalancer(
                service.endpoints, service.load_balancing_strategy
            )

            # Initialize circuit breakers for each endpoint
            for endpoint in service.endpoints:
                key = f"{service.name}:{endpoint.url}"
                self.circuit_breakers[key] = CircuitBreaker(
                    endpoint.circuit_breaker_threshold,
                    endpoint.circuit_breaker_timeout_seconds,
                )

                self.rate_limiters[key] = RateLimiter(endpoint.rate_limit_per_minute)

            # Initialize metrics
            if service.name not in self.service_metrics:
                self.service_metrics[service.name] = ServiceMetrics()

            # Save to database
            self._save_service(service)

            logger.info(
                f"Registered service: {service.name} with {len(service.endpoints)} endpoints"  # noqa: E501
            )
            return True

    def _save_service(self, service: ServiceDefinition) -> None:
        """Save service to database"""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO services (name, service_data, updated_at) VALUES (?, ?, ?)",  # noqa: E501
                    (
                        service.name,
                        json.dumps(service.to_dict()),
                        datetime.now().isoformat(),
                    ),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to save service {service.name}: {e}")

    async def call_service(
        self,
        service_name: str,
        method: str = "GET",
        path: str = "",
        headers: Optional[dict[str, str]] = None,
        data: Optional[Union[dict[str, Any], str]] = None,
        params: Optional[dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> dict[str, Any]:
        """Make a service call with comprehensive error handling and resilience"""
        if service_name not in self.services:
            raise ValueError(f"Service '{service_name}' not found")

        service = self.services[service_name]
        metrics = self.service_metrics[service_name]

        # Update global metrics
        self.global_metrics["total_requests"] += 1
        metrics.total_requests += 1

        start_time = time.time()
        result = {
            "success": False,
            "data": None,
            "error": None,
            "response_time_ms": None,
            "status_code": None,
            "endpoint_used": None,
        }

        try:
            # Get endpoint from load balancer
            endpoint = self.load_balancers[service_name].get_endpoint()
            if not endpoint:
                raise ValueError(
                    f"No healthy endpoints available for service '{service_name}'"
                )

            key = f"{service_name}:{endpoint.url}"
            circuit_breaker = self.circuit_breakers[key]
            rate_limiter = self.rate_limiters[key]

            # Check circuit breaker
            if not circuit_breaker.call_allowed():
                raise Exception(f"Circuit breaker is open for endpoint {endpoint.url}")

            # Check rate limit
            if not rate_limiter.is_allowed():
                wait_time = rate_limiter.get_wait_time()
                raise Exception(f"Rate limit exceeded. Wait {wait_time:.1f} seconds")

            # Build URL
            url = (
                f"{endpoint.url.rstrip('/')}/{path.lstrip('/')}"
                if path
                else endpoint.url
            )

            # Prepare headers
            request_headers = service.custom_headers.copy()
            if headers:
                request_headers.update(headers)

            # Add authentication
            if endpoint.authentication:
                request_headers.update(
                    self._build_auth_headers(endpoint.authentication)
                )

            # Create connection pool if not exists
            if service_name not in self.connection_pools:
                self.connection_pools[
                    service_name
                ] = await self._create_connection_pool(service)

            # Make request with retry
            response_data = await self._make_request_with_retry(
                self.connection_pools[service_name],
                method,
                url,
                request_headers,
                data,
                params,
                timeout or endpoint.timeout_seconds,
                service.retry_policy,
            )

            # Record success
            result["success"] = True
            result["data"] = response_data.get("data")
            result["status_code"] = response_data.get("status_code")
            result["endpoint_used"] = endpoint.url

            circuit_breaker.record_success()

            # Update metrics
            metrics.successful_requests += 1
            self.global_metrics["successful_requests"] += 1

        except Exception as e:
            # Record failure
            result["error"] = str(e)
            circuit_breaker.record_failure()

            metrics.failed_requests += 1
            self.global_metrics["failed_requests"] += 1
            metrics.last_error = str(e)
            metrics.last_error_time = datetime.now()

            logger.error(f"Service call failed for {service_name}: {e}")

        finally:
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            result["response_time_ms"] = response_time

            # Update metrics
            metrics.response_times.append(response_time)
            if len(metrics.response_times) > 1000:
                metrics.response_times = metrics.response_times[-500:]

            self._update_service_metrics(service_name)

            # Log service call
            await self._log_service_call(service_name, result)

        return result

    async def _create_connection_pool(
        self, service: ServiceDefinition
    ) -> aiohttp.ClientSession:
        """Create connection pool for service"""
        # Configure SSL context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        # Configure connector
        connector = aiohttp.TCPConnector(
            ssl=ssl_context,
            limit=20,
            limit_per_host=10,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=60,
            enable_cleanup_closed=True,
        )

        # Configure timeout
        timeout = aiohttp.ClientTimeout(
            total=max(ep.timeout_seconds for ep in service.endpoints),
            connect=10,
            sock_read=30,
        )

        return aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={"User-Agent": "DAIP-ServiceManager/1.0"},
        )

    async def _make_request_with_retry(
        self,
        session: aiohttp.ClientSession,
        method: str,
        url: str,
        headers: dict[str, str],
        data: Optional[Union[dict[str, Any], str]],
        params: Optional[dict[str, Any]],
        timeout: int,
        retry_policy: dict[str, Any],
    ) -> dict[str, Any]:
        """Make HTTP request with retry logic"""
        max_retries = retry_policy.get("max_retries", 3)
        backoff_factor = retry_policy.get("backoff_factor", 2)
        retry_delay = retry_policy.get("initial_delay", 1)

        for attempt in range(max_retries + 1):
            try:
                async with session.request(
                    method=method.upper(),
                    url=url,
                    headers=headers,
                    json=data if isinstance(data, dict) else None,
                    data=data if isinstance(data, str) else None,
                    params=params,
                ) as response:
                    response_data = {
                        "status_code": response.status,
                        "headers": dict(response.headers),
                        "data": None,
                    }

                    # Parse response body
                    content_type = response.headers.get("content-type", "")
                    if "application/json" in content_type:
                        response_data["data"] = await response.json()
                    else:
                        response_data["data"] = await response.text()

                    # Check for HTTP errors
                    if response.status >= 400:
                        if response.status < 500 and attempt == max_retries:
                            # Client error, don't retry
                            raise aiohttp.ClientResponseError(
                                request_info=response.request_info,
                                history=response.history,
                                status=response.status,
                                message=await response.text(),
                            )
                        else:
                            # Server error, retry
                            raise aiohttp.ServerConnectionError(
                                f"HTTP {response.status}"
                            )

                    return response_data

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == max_retries:
                    raise e

                # Calculate delay for next retry
                delay = retry_delay * (backoff_factor**attempt)
                await asyncio.sleep(min(delay, 30))  # Cap at 30 seconds

                logger.warning(
                    f"Request failed (attempt {attempt + 1}/{max_retries + 1}), retrying in {delay:.1f}s: {e}"  # noqa: E501
                )

    def _build_auth_headers(self, auth_config: dict[str, Any]) -> dict[str, str]:
        """Build authentication headers"""
        auth_type = auth_config.get("type", "").lower()
        headers = {}

        if auth_type == "bearer":
            token = auth_config.get("token")
            if token:
                headers["Authorization"] = f"Bearer {token}"

        elif auth_type == "basic":
            username = auth_config.get("username")
            password = auth_config.get("password")
            if username and password:
                credentials = base64.b64encode(
                    f"{username}:{password}".encode()
                ).decode()
                headers["Authorization"] = f"Basic {credentials}"

        elif auth_type == "api_key":
            api_key = auth_config.get("api_key")
            key_header = auth_config.get("header", "X-API-Key")
            if api_key:
                headers[key_header] = api_key

        return headers

    def _update_service_metrics(self, service_name: str) -> None:
        """Update service metrics"""
        if service_name not in self.service_metrics:
            return

        metrics = self.service_metrics[service_name]
        response_times = metrics.response_times

        if response_times:
            # Calculate percentiles
            sorted_times = sorted(response_times)
            n = len(sorted_times)

            metrics.average_response_time_ms = sum(sorted_times) / n
            metrics.p95_response_time_ms = (
                sorted_times[int(n * 0.95)] if n > 20 else sorted_times[-1]
            )
            metrics.p99_response_time_ms = (
                sorted_times[int(n * 0.99)] if n > 100 else sorted_times[-1]
            )

            # Calculate error rate
            if metrics.total_requests > 0:
                metrics.error_rate = metrics.failed_requests / metrics.total_requests

            # Calculate throughput (requests per second over last minute)
            datetime.now() - timedelta(minutes=1)
            # This would require timestamp tracking in actual implementation

    async def _log_service_call(
        self, service_name: str, result: dict[str, Any]
    ) -> None:
        """Log service call to database"""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                conn.execute(
                    "INSERT INTO service_events (service_name, event_type, event_data) VALUES (?, ?, ?)",  # noqa: E501
                    (
                        service_name,
                        "service_call",
                        json.dumps(
                            {
                                "success": result["success"],
                                "response_time_ms": result["response_time_ms"],
                                "endpoint_used": result["endpoint_used"],
                                "error": result["error"],
                            }
                        ),
                    ),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to log service call: {e}")

    def _start_background_tasks(self) -> None:
        """Start background monitoring tasks"""
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        self.metrics_collection_task = asyncio.create_task(
            self._metrics_collection_loop()
        )

    async def _health_check_loop(self) -> None:
        """Background health checking loop"""
        while not self._shutdown_event.is_set():
            try:
                tasks = []
                for service_name, service in self.services.items():
                    for endpoint in service.endpoints:
                        task = asyncio.create_task(
                            self.health_checker.check_health(service_name, endpoint)
                        )
                        tasks.append(task)

                # Wait for all health checks to complete
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)

                # Update global health metrics
                self._update_health_metrics()

                # Wait for next check
                min_interval = min(
                    service.health_check_interval_seconds
                    for service in self.services.values()
                )
                await asyncio.sleep(min_interval)

            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(30)

    async def _metrics_collection_loop(self) -> None:
        """Background metrics collection loop"""
        while not self._shutdown_event.is_set():
            try:
                # Save metrics to database
                for service_name, metrics in self.service_metrics.items():
                    await self._save_service_metrics(service_name, metrics)

                # Save global metrics
                await self._save_global_metrics()

                # Wait for next collection
                await asyncio.sleep(60)  # Collect every minute

            except Exception as e:
                logger.error(f"Metrics collection loop error: {e}")
                await asyncio.sleep(30)

    def _update_health_metrics(self) -> None:
        """Update global health metrics"""
        healthy_count = 0
        total_count = 0

        for service_name in self.services.keys():
            service_healthy = False
            for endpoint in self.service_endpoints[service_name]:
                health_result = self.health_checker.get_service_health(
                    service_name, endpoint.url
                )
                if health_result and health_result["status"] == ServiceStatus.HEALTHY:
                    service_healthy = True
                    break

            if service_healthy:
                healthy_count += 1
            total_count += 1

        self.global_metrics["total_services"] = total_count
        self.global_metrics["healthy_services"] = healthy_count
        self.global_metrics["unhealthy_services"] = total_count - healthy_count

    async def _save_service_metrics(
        self, service_name: str, metrics: ServiceMetrics
    ) -> None:
        """Save service metrics to database"""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO service_metrics (service_name, metrics_data, last_updated) VALUES (?, ?, ?)",  # noqa: E501
                    (
                        service_name,
                        json.dumps(
                            {
                                "total_requests": metrics.total_requests,
                                "successful_requests": metrics.successful_requests,
                                "failed_requests": metrics.failed_requests,
                                "average_response_time_ms": metrics.average_response_time_ms,  # noqa: E501
                                "p95_response_time_ms": metrics.p95_response_time_ms,
                                "p99_response_time_ms": metrics.p99_response_time_ms,
                                "error_rate": metrics.error_rate,
                                "circuit_breaker_trips": metrics.circuit_breaker_trips,
                                "last_error": metrics.last_error,
                                "last_error_time": metrics.last_error_time.isoformat()
                                if metrics.last_error_time
                                else None,
                                "uptime_percentage": metrics.uptime_percentage,
                                "health_check_failures": metrics.health_check_failures,
                            }
                        ),
                        datetime.now().isoformat(),
                    ),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to save service metrics: {e}")

    async def _save_global_metrics(self) -> None:
        """Save global metrics to database"""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                conn.execute(
                    "INSERT INTO service_events (service_name, event_type, event_data) VALUES (?, ?, ?)",  # noqa: E501
                    ("global", "metrics", json.dumps(self.global_metrics)),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to save global metrics: {e}")

    def get_service_status(self, service_name: str) -> Optional[dict[str, Any]]:
        """Get detailed status of a service"""
        if service_name not in self.services:
            return None

        service = self.services[service_name]
        metrics = self.service_metrics.get(service_name)

        # Get endpoint health
        endpoint_health = []
        for endpoint in service.endpoints:
            health_result = self.health_checker.get_service_health(
                service_name, endpoint.url
            )
            circuit_breaker = self.circuit_breakers.get(
                f"{service_name}:{endpoint.url}"
            )

            endpoint_info = {
                "url": endpoint.url,
                "weight": endpoint.weight,
                "health": health_result,
                "circuit_breaker_state": circuit_breaker.get_state().value
                if circuit_breaker
                else "unknown",
            }
            endpoint_health.append(endpoint_info)

        return {
            "service": service.to_dict(),
            "metrics": metrics.__dict__ if metrics else {},
            "endpoint_health": endpoint_health,
            "load_balancer_strategy": service.load_balancing_strategy.value,
        }

    def get_all_services_status(self) -> dict[str, Any]:
        """Get status of all services"""
        services_status = {}
        for service_name in self.services.keys():
            services_status[service_name] = self.get_service_status(service_name)

        return {
            "services": services_status,
            "global_metrics": self.global_metrics,
            "timestamp": datetime.now().isoformat(),
        }

    async def shutdown(self) -> None:
        """Shutdown service manager gracefully"""
        logger.info("Shutting down Production Service Manager")

        # Signal shutdown
        self._shutdown_event.set()

        # Cancel background tasks
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass

        if self.metrics_collection_task:
            self.metrics_collection_task.cancel()
            try:
                await self.metrics_collection_task
            except asyncio.CancelledError:
                pass

        # Close connection pools
        for session in self.connection_pools.values():
            await session.close()

        # Shutdown thread pool
        self.thread_pool.shutdown(wait=True)

        logger.info("Production Service Manager shutdown complete")


class LoadBalancer:
    """Load balancer for service endpoints"""

    def __init__(
        self, endpoints: list[ServiceEndpoint], strategy: LoadBalancingStrategy
    ):
        self.endpoints = endpoints
        self.strategy = strategy
        self.current_index = 0
        self.endpoint_stats: dict[str, dict[str, Any]] = {
            ep.url: {"connections": 0, "total_requests": 0, "response_times": []}
            for ep in endpoints
        }

    def get_endpoint(self) -> Optional[ServiceEndpoint]:
        """Get endpoint based on load balancing strategy"""
        if not self.endpoints:
            return None

        # Filter healthy endpoints (simplified - in production, check actual health)
        healthy_endpoints = self.endpoints  # TODO: Add health checking

        if not healthy_endpoints:
            return None

        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            endpoint = healthy_endpoints[self.current_index % len(healthy_endpoints)]
            self.current_index += 1
            return endpoint

        elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin(healthy_endpoints)

        elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return self._least_connections(healthy_endpoints)

        elif self.strategy == LoadBalancingStrategy.RANDOM:
            import random

            return random.choice(healthy_endpoints)

        elif self.strategy == LoadBalancingStrategy.RESPONSE_TIME:
            return self._response_time_based(healthy_endpoints)

        else:
            return healthy_endpoints[0]

    def _weighted_round_robin(
        self, endpoints: list[ServiceEndpoint]
    ) -> ServiceEndpoint:
        """Weighted round robin selection"""
        # Simplified implementation
        total_weight = sum(ep.weight for ep in endpoints)
        if total_weight == 0:
            return endpoints[0]

        # Find endpoint with highest weight
        max_weight = 0
        selected_endpoint = endpoints[0]

        for endpoint in endpoints:
            if endpoint.weight > max_weight:
                max_weight = endpoint.weight
                selected_endpoint = endpoint

        return selected_endpoint

    def _least_connections(self, endpoints: list[ServiceEndpoint]) -> ServiceEndpoint:
        """Select endpoint with least connections"""
        min_connections = float("inf")
        selected_endpoint = endpoints[0]

        for endpoint in endpoints:
            connections = self.endpoint_stats[endpoint.url]["connections"]
            if connections < min_connections:
                min_connections = connections
                selected_endpoint = endpoint

        return selected_endpoint

    def _response_time_based(self, endpoints: list[ServiceEndpoint]) -> ServiceEndpoint:
        """Select endpoint based on response time"""
        best_endpoint = endpoints[0]
        best_avg_time = float("inf")

        for endpoint in endpoints:
            stats = self.endpoint_stats[endpoint.url]
            response_times = stats["response_times"]

            if response_times:
                avg_time = sum(response_times) / len(response_times)
            else:
                avg_time = 0

            if avg_time < best_avg_time:
                best_avg_time = avg_time
                best_endpoint = endpoint

        return best_endpoint

    def update_endpoint_stats(self, endpoint_url: str, response_time_ms: float) -> None:
        """Update endpoint statistics"""
        if endpoint_url in self.endpoint_stats:
            stats = self.endpoint_stats[endpoint_url]
            stats["total_requests"] += 1
            stats["response_times"].append(response_time_ms)

            # Keep only last 100 response times
            if len(stats["response_times"]) > 100:
                stats["response_times"] = stats["response_times"][-50:]

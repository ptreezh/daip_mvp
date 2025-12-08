# 权限Ask模式健壮性设计文档

## 设计目标

实现一个**高健壮性、防死锁、容错性强**的权限Ask模式交互系统，确保在各种异常情况下系统仍能稳定运行。

## 核心设计原则

### 1. 防死锁原则
- **超时机制**：所有用户交互必须有超时保护
- **异步设计**：非阻塞的权限交互机制
- **状态监控**：实时权限状态检查和恢复
- **最大等待限制**：防止无限期等待用户响应

### 2. 容错性原则
- **优雅降级**：权限系统故障时自动降级到安全模式
- **默认安全**：所有异常情况默认拒绝权限
- **错误恢复**：异常状态能够自动恢复
- **边界保护**：输入验证和异常处理

### 3. 健壮性原则
- **资源限制**：防止资源泄露和耗尽
- **并发安全**：多线程/多进程安全
- **内存保护**：防止内存泄漏
- **性能保证**：可预测的执行时间

## 防死锁架构设计

### 1. 异步非阻塞架构

```python
class RobustPermissionManager:
    """健壮权限管理器 - 防死锁设计"""
    
    def __init__(self):
        self._permission_timeout = 30.0  # 30秒超时
        self._max_concurrent_requests = 10  # 最大并发请求
        self._pending_requests: Dict[str, asyncio.Task] = {}
        self._permission_cache: Dict[str, PermissionResponse] = {}
        self._lock = asyncio.Lock()
        
    async def request_permission(self, tool_name: str, args: Dict[str, Any]) -> PermissionResponse:
        """异步非阻塞权限请求"""
        # 1. 检查缓存（快速路径）
        cached = self._get_cached_permission(tool_name, args)
        if cached:
            return cached
            
        # 2. 检查并发限制
        if len(self._pending_requests) >= self._max_concurrent_requests:
            logger.warning(f"Permission requests exceeded limit: {self._max_concurrent_requests}")
            return PermissionResponse.DENY  # 安全降级
            
        # 3. 创建带超时的权限任务
        try:
            permission_task = asyncio.create_task(
                self._request_permission_with_timeout(tool_name, args)
            )
            
            # 4. 等待结果（带超时保护）
            response = await asyncio.wait_for(permission_task, timeout=self._permission_timeout)
            
            # 5. 缓存结果
            self._cache_permission(tool_name, args, response)
            
            return response
            
        except asyncio.TimeoutError:
            logger.warning(f"Permission request timed out for {tool_name}")
            return PermissionResponse.DENY  # 超时默认拒绝
            
        except Exception as e:
            logger.error(f"Permission request failed: {e}")
            return PermissionResponse.DENY  # 异常默认拒绝
```

### 2. 超时保护机制

```python
class TimeoutProtectedPermissionSystem:
    """超时保护的权限系统"""
    
    def __init__(self):
        self._interaction_timeout = 30.0      # 用户交互超时
        self._decision_timeout = 5.0          # 决策超时
        self._cleanup_interval = 60.0         # 清理间隔
        self._start_cleanup_task()
        
    async def _request_permission_with_timeout(self, tool_name: str, args: Dict[str, Any]) -> PermissionResponse:
        """带多重超时的权限请求"""
        
        # 第一层超时：用户交互
        try:
            user_response = await asyncio.wait_for(
                self._get_user_response(tool_name, args),
                timeout=self._interaction_timeout
            )
            
            # 第二层超时：决策处理
            decision = await asyncio.wait_for(
                self._process_permission_decision(user_response),
                timeout=self._decision_timeout
            )
            
            return decision
            
        except asyncio.TimeoutError as e:
            stage = "interaction" if "user_response" not in locals() else "decision"
            logger.warning(f"Permission {stage} timeout for {tool_name}")
            return PermissionResponse.DENY
            
    def _start_cleanup_task(self):
        """启动后台清理任务"""
        async def cleanup_expired_requests():
            while True:
                try:
                    await asyncio.sleep(self._cleanup_interval)
                    await self._cleanup_expired_permissions()
                except Exception as e:
                    logger.error(f"Cleanup task error: {e}")
                    
        asyncio.create_task(cleanup_expired_requests())
```

### 3. 状态监控和恢复

```python
class PermissionStateMonitor:
    """权限状态监控和恢复"""
    
    def __init__(self):
        self._state_check_interval = 10.0  # 状态检查间隔
        self._max_pending_time = 60.0      # 最大挂起时间
        self._orphaned_requests: Set[str] = set()
        
    async def monitor_permission_states(self):
        """监控权限状态，检测异常"""
        while True:
            try:
                await asyncio.sleep(self._state_check_interval)
                await self._check_pending_permissions()
                await self._recover_orphaned_requests()
                
            except Exception as e:
                logger.error(f"State monitor error: {e}")
                
    async def _check_pending_permissions(self):
        """检查挂起的权限请求"""
        current_time = datetime.utcnow()
        
        for request_id, request_info in self._pending_requests.items():
            pending_time = (current_time - request_info["timestamp"]).total_seconds()
            
            if pending_time > self._max_pending_time:
                logger.warning(f"Orphaned permission request: {request_id}, pending for {pending_time}s")
                self._orphaned_requests.add(request_id)
                
                # 自动恢复：拒绝超时的请求
                await self._auto_recover_permission(request_id, PermissionResponse.DENY)
```

## 容错性设计

### 1. 多级降级策略

```python
class PermissionDegradationStrategy:
    """权限降级策略"""
    
    async def handle_permission_failure(self, failure_type: str, context: Dict[str, Any]) -> PermissionResponse:
        """处理权限系统故障"""
        
        if failure_type == "user_interface_unavailable":
            # 降级1：用户界面不可用
            logger.warning("User interface unavailable, falling back to default deny")
            return PermissionResponse.DENY
            
        elif failure_type == "timeout":
            # 降级2：超时
            logger.warning("Permission request timeout, falling back to default deny")
            return PermissionResponse.DENY
            
        elif failure_type == "system_overload":
            # 降级3：系统过载
            logger.warning("System overload, using cached permissions")
            return self._get_cached_or_default_permission(context)
            
        elif failure_type == "permission_manager_error":
            # 降级4：权限管理器错误
            logger.error("Permission manager error, entering safe mode")
            return PermissionResponse.DENY
            
        else:
            # 最终降级：默认安全模式
            logger.critical(f"Unknown failure type: {failure_type}, entering safe mode")
            return PermissionResponse.DENY
```

### 2. 异常恢复机制

```python
class PermissionExceptionRecovery:
    """权限异常恢复机制"""
    
    async def safe_permission_request(self, tool_name: str, args: Dict[str, Any]) -> PermissionResponse:
        """安全的权限请求（带异常恢复）"""
        
        try:
            # 尝试正常权限请求
            return await self._normal_permission_request(tool_name, args)
            
        except asyncio.TimeoutError:
            logger.warning(f"Permission timeout for {tool_name}, using recovery")
            return await self._recover_from_timeout(tool_name, args)
            
        except PermissionSystemError as e:
            logger.error(f"Permission system error for {tool_name}: {e}")
            return await self._recover_from_system_error(tool_name, args)
            
        except Exception as e:
            logger.critical(f"Unexpected permission error for {tool_name}: {e}")
            return await self._recover_from_unknown_error(tool_name, args)
            
    async def _recover_from_timeout(self, tool_name: str, args: Dict[str, Any]) -> PermissionResponse:
        """从超时恢复"""
        # 检查是否有缓存的权限决策
        cached = self._get_cached_permission(tool_name, args)
        if cached:
            logger.info(f"Using cached permission for {tool_name} after timeout")
            return cached
            
        # 检查工具的风险等级
        risk_level = self._assess_tool_risk(tool_name, args)
        if risk_level == "low":
            logger.info(f"Low risk tool {tool_name}, granting permission after timeout")
            return PermissionResponse.GRANT
        else:
            logger.warning(f"High risk tool {tool_name}, denying permission after timeout")
            return PermissionResponse.DENY
```

### 3. 资源保护和限制

```python
class PermissionResourceProtection:
    """权限资源保护"""
    
    def __init__(self):
        self._max_memory_usage = 100 * 1024 * 1024  # 100MB
        self._max_pending_requests = 100
        self._request_memory_limit = 1024 * 1024    # 1MB per request
        self._current_memory_usage = 0
        
    async def check_resource_limits(self, tool_name: str, args: Dict[str, Any]) -> bool:
        """检查资源限制"""
        # 内存使用检查
        if self._current_memory_usage > self._max_memory_usage:
            logger.warning("Memory usage exceeded limit, denying permission")
            return False
            
        # 并发请求检查
        if len(self._pending_requests) > self._max_pending_requests:
            logger.warning("Too many pending requests, denying permission")
            return False
            
        # 单个请求大小检查
        request_size = self._calculate_request_size(tool_name, args)
        if request_size > self._request_memory_limit:
            logger.warning(f"Request size {request_size} exceeds limit, denying permission")
            return False
            
        return True
        
    def _calculate_request_size(self, tool_name: str, args: Dict[str, Any]) -> int:
        """计算请求大小"""
        import sys
        return sys.getsizeof(tool_name) + sys.getsizeof(str(args))
```

## 并发安全设计

### 1. 线程安全的权限管理

```python
import threading
import asyncio
from contextlib import asynccontextmanager

class ThreadSafePermissionManager:
    """线程安全的权限管理器"""
    
    def __init__(self):
        self._lock = threading.RLock()
        self._async_lock = asyncio.Lock()
        self._permission_cache: Dict[str, PermissionResponse] = {}
        self._pending_requests: Dict[str, Dict[str, Any]] = {}
        
    @asynccontextmanager
    async def permission_operation(self, operation_id: str):
        """权限操作的上下文管理器"""
        async with self._async_lock:
            try:
                self._acquire_operation_lock(operation_id)
                yield
            finally:
                self._release_operation_lock(operation_id)
                
    def _acquire_operation_lock(self, operation_id: str):
        """获取操作锁"""
        with self._lock:
            if operation_id in self._active_operations:
                raise PermissionOperationError(f"Operation {operation_id} already in progress")
            self._active_operations.add(operation_id)
            
    def _release_operation_lock(self, operation_id: str):
        """释放操作锁"""
        with self._lock:
            self._active_operations.discard(operation_id)
```

### 2. 异步并发控制

```python
class AsyncPermissionConcurrency:
    """异步权限并发控制"""
    
    def __init__(self):
        self._semaphore = asyncio.Semaphore(10)  # 最大并发数
        self._rate_limiter = RateLimiter(max_calls=100, time_window=60)  # 速率限制
        
    async def concurrent_permission_request(self, tool_name: str, args: Dict[str, Any]) -> PermissionResponse:
        """并发权限请求控制"""
        
        async with self._semaphore:
            # 速率限制检查
            if not await self._rate_limiter.allow_request(tool_name):
                logger.warning(f"Rate limit exceeded for {tool_name}")
                return PermissionResponse.DENY
                
            # 执行权限请求
            return await self._execute_permission_request(tool_name, args)
            
    async def _execute_permission_request(self, tool_name: str, args: Dict[str, Any]) -> PermissionResponse:
        """执行权限请求（带并发保护）"""
        try:
            # 模拟权限检查逻辑
            await asyncio.sleep(0.1)  # 模拟处理时间
            
            # 权限决策
            if self._is_low_risk_tool(tool_name):
                return PermissionResponse.GRANT
            else:
                return PermissionResponse.DENY
                
        except Exception as e:
            logger.error(f"Concurrent permission request failed: {e}")
            return PermissionResponse.DENY
```

## 性能优化

### 1. 智能缓存机制

```python
class IntelligentPermissionCache:
    """智能权限缓存"""
    
    def __init__(self):
        self._cache: Dict[str, Tuple[PermissionResponse, float]] = {}
        self._cache_ttl = 300.0  # 5分钟TTL
        self._max_cache_size = 1000
        self._cache_hits = 0
        self._cache_misses = 0
        
    def get_permission(self, tool_name: str, args: Dict[str, Any]) -> Optional[PermissionResponse]:
        """获取缓存的权限决策"""
        cache_key = self._generate_cache_key(tool_name, args)
        
        if cache_key in self._cache:
            response, timestamp = self._cache[cache_key]
            
            # 检查TTL
            if time.time() - timestamp < self._cache_ttl:
                self._cache_hits += 1
                logger.debug(f"Cache hit for {tool_name}")
                return response
            else:
                # TTL过期，删除缓存
                del self._cache[cache_key]
                
        self._cache_misses += 1
        return None
        
    def set_permission(self, tool_name: str, args: Dict[str, Any], response: PermissionResponse):
        """设置权限缓存"""
        # 缓存大小控制
        if len(self._cache) >= self._max_cache_size:
            self._evict_oldest_cache_entry()
            
        cache_key = self._generate_cache_key(tool_name, args)
        self._cache[cache_key] = (response, time.time())
        
    def _generate_cache_key(self, tool_name: str, args: Dict[str, Any]) -> str:
        """生成缓存键"""
        # 简化参数以生成稳定的缓存键
        simplified_args = self._simplify_args(args)
        return f"{tool_name}:{hash(str(simplified_args))}"
```

### 2. 异步批处理

```python
class AsyncPermissionBatchProcessor:
    """异步权限批处理器"""
    
    def __init__(self):
        self._batch_size = 10
        self._batch_timeout = 1.0
        self._pending_batch: List[Dict[str, Any]] = []
        self._batch_processor_task = None
        
    async def add_permission_request(self, tool_name: str, args: Dict[str, Any]) -> asyncio.Future:
        """添加权限请求到批处理队列"""
        future = asyncio.Future()
        
        self._pending_batch.append({
            "tool_name": tool_name,
            "args": args,
            "future": future,
            "timestamp": time.time()
        })
        
        # 启动批处理器（如果未运行）
        if self._batch_processor_task is None or self._batch_processor_task.done():
            self._batch_processor_task = asyncio.create_task(self._batch_processor())
            
        # 如果批次已满，立即处理
        if len(self._pending_batch) >= self._batch_size:
            await self._process_batch()
            
        return future
        
    async def _batch_processor(self):
        """批处理器协程"""
        while True:
            try:
                await asyncio.sleep(self._batch_timeout)
                if self._pending_batch:
                    await self._process_batch()
            except Exception as e:
                logger.error(f"Batch processor error: {e}")
```

## 监控和诊断

### 1. 健康检查

```python
class PermissionHealthChecker:
    """权限系统健康检查"""
    
    def __init__(self):
        self._health_metrics = {
            "permission_requests_total": 0,
            "permission_timeouts": 0,
            "permission_errors": 0,
            "permission_cache_hits": 0,
            "permission_cache_misses": 0,
            "permission_response_time": [],
        }
        
    def record_permission_request(self, response: PermissionResponse, response_time: float):
        """记录权限请求指标"""
        self._health_metrics["permission_requests_total"] += 1
        self._health_metrics["permission_response_time"].append(response_time)
        
        # 保持响应时间数组大小合理
        if len(self._health_metrics["permission_response_time"]) > 1000:
            self._health_metrics["permission_response_time"] = self._health_metrics["permission_response_time"][-1000:]
            
    def get_health_status(self) -> Dict[str, Any]:
        """获取系统健康状态"""
        total_requests = self._health_metrics["permission_requests_total"]
        
        if total_requests == 0:
            return {"status": "healthy", "message": "No permission requests yet"}
            
        avg_response_time = sum(self._health_metrics["permission_response_time"]) / len(self._health_metrics["permission_response_time"])
        timeout_rate = self._health_metrics["permission_timeouts"] / total_requests
        error_rate = self._health_metrics["permission_errors"] / total_requests
        
        # 健康判断逻辑
        if timeout_rate > 0.1:  # 超时率 > 10%
            return {"status": "unhealthy", "reason": f"High timeout rate: {timeout_rate:.2%}"}
        elif error_rate > 0.05:  # 错误率 > 5%
            return {"status": "unhealthy", "reason": f"High error rate: {error_rate:.2%}"}
        elif avg_response_time > 5.0:  # 平均响应时间 > 5秒
            return {"status": "degraded", "reason": f"High response time: {avg_response_time:.2f}s"}
        else:
            return {"status": "healthy", "metrics": self._health_metrics}
```

### 2. 诊断工具

```python
class PermissionDiagnostics:
    """权限系统诊断工具"""
    
    def __init__(self, permission_manager: RobustPermissionManager):
        self._manager = permission_manager
        self._diagnostic_data: List[Dict[str, Any]] = []
        
    def record_diagnostic_data(self, event_type: str, data: Dict[str, Any]):
        """记录诊断数据"""
        self._diagnostic_data.append({
            "timestamp": datetime.utcnow(),
            "event_type": event_type,
            "data": data
        })
        
        # 限制诊断数据大小
        if len(self._diagnostic_data) > 10000:
            self._diagnostic_data = self._diagnostic_data[-5000:]
            
    def generate_diagnostic_report(self) -> Dict[str, Any]:
        """生成诊断报告"""
        return {
            "timestamp": datetime.utcnow(),
            "system_status": self._manager.health_checker.get_health_status(),
            "pending_requests": len(self._manager._pending_requests),
            "cache_size": len(self._manager._permission_cache),
            "recent_diagnostic_events": self._diagnostic_data[-100:],  # 最近100条
            "recommendations": self._generate_recommendations()
        }
        
    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        health_status = self._manager.health_checker.get_health_status()
        if health_status["status"] != "healthy":
            recommendations.append(f"System health issue: {health_status.get('reason', 'Unknown')}")
            
        if len(self._manager._pending_requests) > 50:
            recommendations.append("High number of pending requests - consider increasing timeout or optimizing")
            
        if len(self._manager._permission_cache) > 500:
            recommendations.append("Large cache size - consider reducing TTL or cache size")
            
        return recommendations
```

## 配置管理

### 1. 动态配置

```python
@dataclass
class RobustPermissionConfig:
    """健壮权限配置"""
    
    # 超时配置
    interaction_timeout: float = 30.0
    decision_timeout: float = 5.0
    cleanup_interval: float = 60.0
    
    # 资源限制
    max_concurrent_requests: int = 10
    max_pending_requests: int = 100
    max_cache_size: int = 1000
    max_memory_usage: int = 100 * 1024 * 1024  # 100MB
    
    # 降级策略
    enable_auto_degradation: bool = True
    enable_cache_fallback: bool = True
    enable_risk_assessment: bool = True
    
    # 监控配置
    enable_health_monitoring: bool = True
    enable_diagnostics: bool = True
    diagnostic_data_limit: int = 10000
    
    # 安全策略
    default_response: PermissionResponse = PermissionResponse.DENY
    enable_input_validation: bool = True
    enable_audit_logging: bool = True
```

## 总结

这个健壮性设计通过以下机制确保权限Ask模式的稳定性和可靠性：

1. **防死锁**：超时机制、异步设计、状态监控
2. **容错性**：多级降级、异常恢复、默认安全
3. **健壮性**：资源保护、并发安全、性能优化
4. **可监控**：健康检查、诊断工具、配置管理

系统设计遵循"**默认安全、优雅降级、快速失败**"的原则，确保在各种异常情况下都能保持稳定运行。
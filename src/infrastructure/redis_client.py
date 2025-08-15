"""@Time    : 2025-08-06 10:30:00
@Author  : DAIP-LIVE Team
@File    : redis_client.py
@Description:
    Redis client for caching and session management.
    Handles Redis connections, caching operations, and pub/sub messaging.
"""

import asyncio
import json
import logging
from collections.abc import Callable
from datetime import datetime
from typing import Any, Optional, Set

try:
    import redis.asyncio as redis
    from redis.exceptions import ConnectionError, RedisError
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    # 创建虚拟类用于类型提示
    class Redis:
        pass

# 全局Redis管理器实例
_redis_manager: Optional['RedisManager'] = None


class RedisManager:
    """Redis管理器 - 管理Redis连接和缓存操作"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        if not REDIS_AVAILABLE:
            raise ImportError("redis package is required. Install with: pip install redis")
        
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        self.is_initialized = False
        
        # 配置参数
        self.config = {
            "connection_pool_max_connections": 20,
            "connection_pool_timeout": 30,
            "socket_timeout": 30,
            "socket_connect_timeout": 30,
            "retry_on_timeout": True,
            "health_check_interval": 30,
            "default_ttl": 3600,  # 1小时
            "session_ttl": 86400,  # 24小时
            "cache_ttl": 1800,  # 30分钟
        }
        
        # 统计信息
        self.stats = {
            "total_connections": 0,
            "active_connections": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "keys_set": 0,
            "keys_get": 0,
            "keys_deleted": 0,
            "messages_published": 0,
            "messages_received": 0,
            "start_time": datetime.now()
        }
        
        # 事件处理器
        self.event_handlers: dict[str, list[Callable]] = {}
        
        # 后台任务
        self._health_check_task: Optional[asyncio.Task] = None
        self._pubsub_task: Optional[asyncio.Task] = None
        self._is_running = False
    
    async def initialize(self):
        """初始化Redis连接"""
        if self.is_initialized:
            return
        
        try:
            # 创建Redis客户端
            self.redis_client = redis.Redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                **self.config
            )
            
            # 测试连接
            await self.redis_client.ping()
            
            # 创建pub/sub
            self.pubsub = self.redis_client.pubsub()
            
            self.is_initialized = True
            self.stats["total_connections"] += 1
            self.stats["active_connections"] += 1
            
            logging.info("Redis initialized successfully")
            
        except Exception as e:
            logging.error(f"Failed to initialize Redis: {e}")
            raise
    
    async def start(self):
        """启动Redis管理器"""
        if not self.is_initialized:
            await self.initialize()
        
        if self._is_running:
            return
        
        self._is_running = True
        
        # 启动后台任务
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        self._pubsub_task = asyncio.create_task(self._pubsub_listener())
        
        logging.info("Redis Manager started")
    
    async def stop(self):
        """停止Redis管理器"""
        if not self._is_running:
            return
        
        self._is_running = False
        
        # 取消后台任务
        if self._health_check_task:
            self._health_check_task.cancel()
        
        if self._pubsub_task:
            self._pubsub_task.cancel()
        
        # 关闭连接
        if self.pubsub:
            await self.pubsub.close()
        
        if self.redis_client:
            await self.redis_client.close()
        
        self.stats["active_connections"] -= 1
        
        logging.info("Redis Manager stopped")
    
    async def _health_check_loop(self):
        """健康检查循环"""
        while self._is_running:
            try:
                await asyncio.sleep(self.config["health_check_interval"])
                
                if self.redis_client:
                    try:
                        await self.redis_client.ping()
                    except Exception as e:
                        logging.warning(f"Redis health check failed: {e}")
                        # 尝试重新连接
                        await self._reconnect()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error in health check loop: {e}")
    
    async def _pubsub_listener(self):
        """Pub/Sub监听器"""
        if not self.pubsub:
            return
        
        try:
            # 订阅默认频道
            await self.pubsub.subscribe("daip_events", "daip_sessions", "daip_tasks")
            
            async for message in self.pubsub.listen():
                if not self._is_running:
                    break
                
                if message["type"] == "message":
                    await self._handle_pubsub_message(message)
                    self.stats["messages_received"] += 1
                    
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logging.error(f"Error in pubsub listener: {e}")
    
    async def _handle_pubsub_message(self, message: dict[str, Any]):
        """处理Pub/Sub消息"""
        try:
            channel = message["channel"]
            data = json.loads(message["data"])
            
            # 触发事件处理器
            if channel in self.event_handlers:
                for handler in self.event_handlers[channel]:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(data)
                        else:
                            handler(data)
                    except Exception as e:
                        logging.error(f"Error in pubsub handler for {channel}: {e}")
            
        except Exception as e:
            logging.error(f"Error handling pubsub message: {e}")
    
    async def _reconnect(self):
        """重新连接Redis"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            self.redis_client = redis.Redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                **self.config
            )
            
            await self.redis_client.ping()
            
            if self.pubsub:
                await self.pubsub.close()
            
            self.pubsub = self.redis_client.pubsub()
            
            logging.info("Redis reconnected successfully")
            
        except Exception as e:
            logging.error(f"Failed to reconnect Redis: {e}")
    
    # 基础操作
    async def set(self, key: str, value: Any, ttl: int = None, serialize: bool = True) -> bool:
        """设置键值"""
        if not self.redis_client:
            return False
        
        try:
            if serialize:
                value = json.dumps(value, ensure_ascii=False)
            
            result = await self.redis_client.setex(key, ttl or self.config["default_ttl"], value)
            
            if result:
                self.stats["keys_set"] += 1
            
            return result
            
        except Exception as e:
            logging.error(f"Error setting key {key}: {e}")
            return False
    
    async def get(self, key: str, deserialize: bool = True) -> Optional[Any]:
        """获取键值"""
        if not self.redis_client:
            return None
        
        try:
            value = await self.redis_client.get(key)
            
            if value is None:
                self.stats["cache_misses"] += 1
                return None
            
            self.stats["cache_hits"] += 1
            self.stats["keys_get"] += 1
            
            if deserialize:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            
            return value
            
        except Exception as e:
            logging.error(f"Error getting key {key}: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """删除键"""
        if not self.redis_client:
            return False
        
        try:
            result = await self.redis_client.delete(key)
            
            if result:
                self.stats["keys_deleted"] += 1
            
            return result > 0
            
        except Exception as e:
            logging.error(f"Error deleting key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self.redis_client:
            return False
        
        try:
            return await self.redis_client.exists(key) > 0
            
        except Exception as e:
            logging.error(f"Error checking key {key}: {e}")
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """设置键的过期时间"""
        if not self.redis_client:
            return False
        
        try:
            return await self.redis_client.expire(key, ttl)
            
        except Exception as e:
            logging.error(f"Error setting expiry for key {key}: {e}")
            return False
    
    # 会话管理
    async def save_session(self, session_id: str, session_data: dict[str, Any]) -> bool:
        """保存会话数据"""
        key = f"session:{session_id}"
        return await self.set(key, session_data, self.config["session_ttl"])
    
    async def get_session(self, session_id: str) -> Optional[dict[str, Any]]:
        """获取会话数据"""
        key = f"session:{session_id}"
        return await self.get(key)
    
    async def delete_session(self, session_id: str) -> bool:
        """删除会话数据"""
        key = f"session:{session_id}"
        return await self.delete(key)
    
    async def get_user_sessions(self, user_id: str) -> list[str]:
        """获取用户的所有会话ID"""
        pattern = "session:*"
        session_keys = await self.redis_client.keys(pattern)
        
        user_sessions = []
        for key in session_keys:
            session_data = await self.get(key)
            if session_data and session_data.get("user_id") == user_id:
                session_id = key.replace("session:", "")
                user_sessions.append(session_id)
        
        return user_sessions
    
    # 缓存管理
    async def cache_set(self, key: str, value: Any, ttl: int = None) -> bool:
        """设置缓存"""
        cache_key = f"cache:{key}"
        return await self.set(cache_key, value, ttl or self.config["cache_ttl"])
    
    async def cache_get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        cache_key = f"cache:{key}"
        return await self.get(cache_key)
    
    async def cache_delete(self, key: str) -> bool:
        """删除缓存"""
        cache_key = f"cache:{key}"
        return await self.delete(cache_key)
    
    async def cache_clear_pattern(self, pattern: str) -> int:
        """清除匹配模式的缓存"""
        if not self.redis_client:
            return 0
        
        try:
            cache_pattern = f"cache:{pattern}"
            keys = await self.redis_client.keys(cache_pattern)
            
            if keys:
                deleted_count = await self.redis_client.delete(*keys)
                self.stats["keys_deleted"] += deleted_count
                return deleted_count
            
            return 0
            
        except Exception as e:
            logging.error(f"Error clearing cache pattern {pattern}: {e}")
            return 0
    
    # 任务队列
    async def enqueue_task(self, queue_name: str, task_data: dict[str, Any]) -> bool:
        """将任务加入队列"""
        if not self.redis_client:
            return False
        
        try:
            task_json = json.dumps(task_data, ensure_ascii=False)
            result = await self.redis_client.lpush(f"queue:{queue_name}", task_json)
            
            if result:
                self.stats["keys_set"] += 1
            
            return result > 0
            
        except Exception as e:
            logging.error(f"Error enqueuing task to {queue_name}: {e}")
            return False
    
    async def dequeue_task(self, queue_name: str, timeout: int = 5) -> Optional[dict[str, Any]]:
        """从队列中取出任务"""
        if not self.redis_client:
            return None
        
        try:
            result = await self.redis_client.brpop(f"queue:{queue_name}", timeout=timeout)
            
            if result:
                _, task_json = result
                task_data = json.loads(task_json)
                self.stats["keys_get"] += 1
                return task_data
            
            return None
            
        except Exception as e:
            logging.error(f"Error dequeuing task from {queue_name}: {e}")
            return None
    
    async def get_queue_length(self, queue_name: str) -> int:
        """获取队列长度"""
        if not self.redis_client:
            return 0
        
        try:
            return await self.redis_client.llen(f"queue:{queue_name}")
            
        except Exception as e:
            logging.error(f"Error getting queue length for {queue_name}: {e}")
            return 0
    
    # Pub/Sub
    async def publish(self, channel: str, message: dict[str, Any]) -> bool:
        """发布消息"""
        if not self.redis_client:
            return False
        
        try:
            message_json = json.dumps(message, ensure_ascii=False)
            result = await self.redis_client.publish(channel, message_json)
            
            if result:
                self.stats["messages_published"] += 1
            
            return result > 0
            
        except Exception as e:
            logging.error(f"Error publishing to {channel}: {e}")
            return False
    
    async def subscribe(self, channel: str, handler: Callable):
        """订阅频道"""
        if channel not in self.event_handlers:
            self.event_handlers[channel] = []
        
        self.event_handlers[channel].append(handler)
        
        if self.pubsub:
            await self.pubsub.subscribe(channel)
    
    async def unsubscribe(self, channel: str, handler: Callable = None):
        """取消订阅频道"""
        if channel in self.event_handlers:
            if handler:
                self.event_handlers[channel].remove(handler)
            else:
                del self.event_handlers[channel]
        
        if self.pubsub:
            await self.pubsub.unsubscribe(channel)
    
    # 计数器
    async def increment_counter(self, key: str, amount: int = 1) -> int:
        """增加计数器"""
        if not self.redis_client:
            return 0
        
        try:
            counter_key = f"counter:{key}"
            result = await self.redis_client.incrby(counter_key, amount)
            
            # 设置过期时间
            await self.redis_client.expire(counter_key, self.config["default_ttl"])
            
            return result
            
        except Exception as e:
            logging.error(f"Error incrementing counter {key}: {e}")
            return 0
    
    async def get_counter(self, key: str) -> int:
        """获取计数器值"""
        if not self.redis_client:
            return 0
        
        try:
            counter_key = f"counter:{key}"
            result = await self.redis_client.get(counter_key)
            return int(result) if result else 0
            
        except Exception as e:
            logging.error(f"Error getting counter {key}: {e}")
            return 0
    
    # 集合操作
    async def add_to_set(self, key: str, value: str) -> bool:
        """添加到集合"""
        if not self.redis_client:
            return False
        
        try:
            result = await self.redis_client.sadd(f"set:{key}", value)
            return result > 0
            
        except Exception as e:
            logging.error(f"Error adding to set {key}: {e}")
            return False
    
    async def remove_from_set(self, key: str, value: str) -> bool:
        """从集合中移除"""
        if not self.redis_client:
            return False
        
        try:
            result = await self.redis_client.srem(f"set:{key}", value)
            return result > 0
            
        except Exception as e:
            logging.error(f"Error removing from set {key}: {e}")
            return False
    
    async def get_set_members(self, key: str) -> Set[str]:
        """获取集合成员"""
        if not self.redis_client:
            return set()
        
        try:
            result = await self.redis_client.smembers(f"set:{key}")
            return set(result)
            
        except Exception as e:
            logging.error(f"Error getting set members for {key}: {e}")
            return set()
    
    async def is_set_member(self, key: str, value: str) -> bool:
        """检查是否为集合成员"""
        if not self.redis_client:
            return False
        
        try:
            return await self.redis_client.sismember(f"set:{key}", value)
            
        except Exception as e:
            logging.error(f"Error checking set membership for {key}: {e}")
            return False
    
    # 统计信息
    async def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        uptime = (datetime.now() - self.stats["start_time"]).total_seconds()
        
        # 获取Redis信息
        redis_info = {}
        if self.redis_client:
            try:
                info = await self.redis_client.info()
                redis_info = {
                    "used_memory": info.get("used_memory_human", "N/A"),
                    "connected_clients": info.get("connected_clients", 0),
                    "total_commands_processed": info.get("total_commands_processed", 0),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0)
                }
            except Exception as e:
                logging.error(f"Error getting Redis info: {e}")
        
        return {
            "url": self.redis_url,
            "is_connected": self.is_initialized,
            "uptime_seconds": uptime,
            "total_connections": self.stats["total_connections"],
            "active_connections": self.stats["active_connections"],
            "cache_hits": self.stats["cache_hits"],
            "cache_misses": self.stats["cache_misses"],
            "cache_hit_rate": self.stats["cache_hits"] / (self.stats["cache_hits"] + self.stats["cache_misses"]) if (self.stats["cache_hits"] + self.stats["cache_misses"]) > 0 else 0,
            "keys_set": self.stats["keys_set"],
            "keys_get": self.stats["keys_get"],
            "keys_deleted": self.stats["keys_deleted"],
            "messages_published": self.stats["messages_published"],
            "messages_received": self.stats["messages_received"],
            "redis_info": redis_info,
            "is_running": self._is_running
        }
    
    async def health_check(self) -> dict[str, Any]:
        """健康检查"""
        try:
            if not self.redis_client:
                return {
                    "status": "disconnected",
                    "connected": False,
                    "error": "Redis client not initialized"
                }
            
            # 测试连接
            await self.redis_client.ping()
            
            # 测试基本操作
            test_key = "health_check_test"
            await self.redis_client.set(test_key, "test", ex=1)
            result = await self.redis_client.get(test_key)
            await self.redis_client.delete(test_key)
            
            if result == "test":
                return {
                    "status": "healthy",
                    "connected": True,
                    "last_check": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "connected": True,
                    "error": "Basic operation test failed",
                    "last_check": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }


async def get_redis_manager(redis_url: str = None) -> RedisManager:
    """获取Redis管理器实例"""
    global _redis_manager
    
    if _redis_manager is None:
        if redis_url is None:
            redis_url = "redis://localhost:6379/0"
        
        _redis_manager = RedisManager(redis_url)
        await _redis_manager.initialize()
    
    return _redis_manager


async def close_redis_connection():
    """关闭Redis连接"""
    global _redis_manager
    
    if _redis_manager:
        await _redis_manager.stop()
        _redis_manager = None
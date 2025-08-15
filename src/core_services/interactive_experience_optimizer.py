#!/usr/bin/env python3
"""@Time    : 2025-08-03 16:00:00
@Author  : DAIP-LIVE Team
@File    : interactive_experience_optimizer.py
@Description:
    V0.3.2 交互体验深度优化系统
    
    核心优化目标：
    - 响应性能：界面响应时间<200ms，操作反馈即时性
    - 错误处理：用户友好的错误提示、恢复建议、操作指导
    - 操作引导：新用户引导流程、功能提示、快捷操作
    - 个性化：用户偏好设置、界面定制、快捷方式
    - 前端性能：代码分割、懒加载、缓存优化
"""

import asyncio
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)

class InteractionType(Enum):
    """交互类型"""
    CLICK = "click"
    HOVER = "hover"
    FOCUS = "focus"
    SCROLL = "scroll"
    INPUT = "input"
    GESTURE = "gesture"
    VOICE = "voice"
    KEYBOARD = "keyboard"

class ResponseLevel(Enum):
    """响应级别"""
    IMMEDIATE = "immediate"  # <50ms
    FAST = "fast"           # <200ms
    NORMAL = "normal"       # <500ms
    SLOW = "slow"           # <1000ms
    TIMEOUT = "timeout"     # >1000ms

class ErrorSeverity(Enum):
    """错误严重级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class PerformanceMetric:
    """性能指标"""
    timestamp: datetime
    interaction_type: InteractionType
    response_time: float
    response_level: ResponseLevel
    user_id: str = "default"
    component: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class UserAction:
    """用户操作"""
    action_id: str
    user_id: str
    action_type: InteractionType
    target_component: str
    timestamp: datetime
    context: dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error_info: Optional[str] = None

@dataclass
class UserPreference:
    """用户偏好"""
    user_id: str
    theme: str = "professional"
    language: str = "zh-CN"
    font_size: str = "normal"
    animation_enabled: bool = True
    sound_enabled: bool = False
    shortcuts: dict[str, str] = field(default_factory=dict)
    layout_config: dict[str, Any] = field(default_factory=dict)
    updated_at: datetime = field(default_factory=datetime.now)

class InteractiveExperienceOptimizer:
    """交互体验优化器"""
    
    def __init__(self):
        # 性能监控
        self.performance_metrics: list[PerformanceMetric] = []
        self.response_time_threshold = 0.2  # 200ms
        
        # 用户行为分析
        self.user_actions: list[UserAction] = []
        self.user_preferences: dict[str, UserPreference] = {}
        
        # 错误处理
        self.error_handlers: dict[str, Callable] = {}
        self.recovery_strategies: dict[str, Callable] = {}
        
        # 操作引导
        self.tutorial_steps: list[dict[str, Any]] = []
        self.tooltip_registry: dict[str, str] = {}
        
        # 性能优化
        self.cache_manager = CacheManager()
        self.lazy_loader = LazyLoadManager()
        
        # 初始化组件
        self._initialize_optimizers()
    
    def _initialize_optimizers(self):
        """初始化优化器组件"""
        # 注册默认错误处理器
        self._register_default_error_handlers()
        
        # 注册默认恢复策略
        self._register_default_recovery_strategies()
        
        # 初始化操作指导
        self._initialize_user_guidance()
        
        # 设置性能监控
        self._setup_performance_monitoring()
    
    def _register_default_error_handlers(self):
        """注册默认错误处理器"""
        self.error_handlers.update({
            "network_error": self._handle_network_error,
            "validation_error": self._handle_validation_error,
            "permission_error": self._handle_permission_error,
            "timeout_error": self._handle_timeout_error,
            "unknown_error": self._handle_unknown_error
        })
    
    def _register_default_recovery_strategies(self):
        """注册默认恢复策略"""
        self.recovery_strategies.update({
            "retry": self._retry_strategy,
            "fallback": self._fallback_strategy,
            "refresh": self._refresh_strategy,
            "reset": self._reset_strategy,
            "guide": self._guide_strategy
        })
    
    def _initialize_user_guidance(self):
        """初始化用户指导"""
        self.tutorial_steps = [
            {
                "id": "welcome",
                "title": "欢迎使用DAIP-LIVE V0.3",
                "content": "让我们快速了解专业版的新功能",
                "target": ".professional-chat-container",
                "position": "center"
            },
            {
                "id": "scenarios",
                "title": "智能场景选择",
                "content": "选择适合您需求的协作场景，或使用智能推荐",
                "target": ".scenario-buttons",
                "position": "bottom"
            },
            {
                "id": "input",
                "title": "专业化输入",
                "content": "在这里输入您的问题，支持快捷操作和智能建议",
                "target": ".professional-input",
                "position": "top"
            },
            {
                "id": "side_panel",
                "title": "智能助手面板",
                "content": "查看会话信息、快捷操作和个性化建议",
                "target": ".professional-side-panel",
                "position": "left"
            }
        ]
        
        self.tooltip_registry = {
            "send_button": "发送消息 (Ctrl+Enter)",
            "voice_input": "语音输入 (点击并开始说话)",
            "attach_file": "添加附件 (支持拖拽)",
            "template_select": "选择消息模板",
            "new_session": "开始新对话 (Ctrl+N)",
            "export_chat": "导出对话历史 (Ctrl+E)",
            "search_history": "搜索历史记录 (Ctrl+F)",
            "settings": "个性化设置 (Ctrl+,)"
        }
    
    def _setup_performance_monitoring(self):
        """设置性能监控"""
        # 启动性能监控任务
        asyncio.create_task(self._performance_monitor_loop())
    
    async def _performance_monitor_loop(self):
        """性能监控循环"""
        while True:
            try:
                # 分析性能数据
                await self._analyze_performance_metrics()
                
                # 优化建议
                await self._generate_optimization_suggestions()
                
                # 清理旧数据
                await self._cleanup_old_metrics()
                
                # 等待下一个监控周期
                await asyncio.sleep(30)  # 30秒监控一次
                
            except Exception as e:
                logger.error(f"性能监控循环错误: {e}")
                await asyncio.sleep(60)  # 出错时延长等待时间
    
    async def record_interaction(self, 
                                interaction_type: InteractionType,
                                component: str,
                                user_id: str = "default",
                                start_time: Optional[float] = None) -> str:
        """记录交互开始"""
        if start_time is None:
            start_time = time.time()
        
        action_id = f"action_{int(start_time * 1000)}"
        
        action = UserAction(
            action_id=action_id,
            user_id=user_id,
            action_type=interaction_type,
            target_component=component,
            timestamp=datetime.now()
        )
        
        self.user_actions.append(action)
        return action_id
    
    async def complete_interaction(self,
                                  action_id: str,
                                  success: bool = True,
                                  error_info: Optional[str] = None,
                                  metadata: Optional[dict[str, Any]] = None):
        """完成交互记录"""
        # 查找对应的用户操作
        action = next((a for a in self.user_actions if a.action_id == action_id), None)
        if not action:
            logger.warning(f"未找到操作ID: {action_id}")
            return
        
        # 计算响应时间
        response_time = (datetime.now() - action.timestamp).total_seconds()
        
        # 确定响应级别
        if response_time < 0.05:
            response_level = ResponseLevel.IMMEDIATE
        elif response_time < 0.2:
            response_level = ResponseLevel.FAST
        elif response_time < 0.5:
            response_level = ResponseLevel.NORMAL
        elif response_time < 1.0:
            response_level = ResponseLevel.SLOW
        else:
            response_level = ResponseLevel.TIMEOUT
        
        # 记录性能指标
        metric = PerformanceMetric(
            timestamp=datetime.now(),
            interaction_type=action.action_type,
            response_time=response_time,
            response_level=response_level,
            user_id=action.user_id,
            component=action.target_component,
            metadata=metadata or {}
        )
        
        self.performance_metrics.append(metric)
        
        # 更新操作状态
        action.success = success
        action.error_info = error_info
        
        # 如果响应时间超过阈值，记录警告
        if response_time > self.response_time_threshold:
            logger.warning(f"响应时间超标: {response_time:.3f}s > {self.response_time_threshold}s")
            
            # 触发性能优化
            await self._trigger_performance_optimization(action, metric)
    
    async def handle_error(self,
                          error_type: str,
                          error_message: str,
                          component: str,
                          severity: ErrorSeverity = ErrorSeverity.ERROR,
                          user_id: str = "default",
                          context: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """统一错误处理"""
        error_info = {
            "error_type": error_type,
            "message": error_message,
            "component": component,
            "severity": severity.value,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "context": context or {}
        }
        
        # 记录错误
        logger.error(f"交互错误 [{severity.value}]: {error_message} in {component}")
        
        # 获取用户友好的错误信息
        user_message = self._get_user_friendly_error_message(error_type, error_message)
        
        # 获取恢复建议
        recovery_suggestions = self._get_recovery_suggestions(error_type, component)
        
        # 选择错误处理器
        handler = self.error_handlers.get(error_type, self.error_handlers["unknown_error"])
        
        # 执行错误处理
        handling_result = await handler(error_info)
        
        return {
            "user_message": user_message,
            "recovery_suggestions": recovery_suggestions,
            "handling_result": handling_result,
            "error_id": f"error_{int(time.time() * 1000)}"
        }
    
    def _get_user_friendly_error_message(self, error_type: str, error_message: str) -> str:
        """获取用户友好的错误信息"""
        friendly_messages = {
            "network_error": "网络连接出现问题，请检查您的网络设置",
            "validation_error": "输入信息有误，请检查并重新输入",
            "permission_error": "权限不足，请联系管理员或重新登录",
            "timeout_error": "操作超时，请稍后重试",
            "unknown_error": "出现了意外错误，我们正在处理中"
        }
        
        return friendly_messages.get(error_type, f"系统错误：{error_message}")
    
    def _get_recovery_suggestions(self, error_type: str, component: str) -> list[str]:
        """获取恢复建议"""
        suggestions_map = {
            "network_error": [
                "检查网络连接是否正常",
                "刷新页面重试",
                "稍后再试"
            ],
            "validation_error": [
                "检查输入格式是否正确",
                "参考示例重新输入",
                "使用模板功能"
            ],
            "permission_error": [
                "重新登录系统",
                "联系系统管理员",
                "检查账户权限"
            ],
            "timeout_error": [
                "稍后重试操作",
                "检查网络连接",
                "简化请求内容"
            ]
        }
        
        return suggestions_map.get(error_type, ["刷新页面重试", "联系技术支持"])
    
    async def _handle_network_error(self, error_info: dict[str, Any]) -> dict[str, Any]:
        """处理网络错误"""
        return {
            "action": "show_notification",
            "type": "error",
            "title": "网络连接错误",
            "message": "请检查网络连接后重试",
            "auto_retry": True,
            "retry_delay": 5
        }
    
    async def _handle_validation_error(self, error_info: dict[str, Any]) -> dict[str, Any]:
        """处理验证错误"""
        return {
            "action": "highlight_field",
            "target": error_info.get("context", {}).get("field"),
            "message": "请检查输入内容",
            "show_examples": True
        }
    
    async def _handle_permission_error(self, error_info: dict[str, Any]) -> dict[str, Any]:
        """处理权限错误"""
        return {
            "action": "show_login_prompt",
            "message": "权限不足，请重新登录",
            "redirect_after_login": True
        }
    
    async def _handle_timeout_error(self, error_info: dict[str, Any]) -> dict[str, Any]:
        """处理超时错误"""
        return {
            "action": "show_retry_dialog",
            "message": "操作超时，是否重试？",
            "auto_retry_count": 3,
            "show_progress": True
        }
    
    async def _handle_unknown_error(self, error_info: dict[str, Any]) -> dict[str, Any]:
        """处理未知错误"""
        return {
            "action": "show_fallback_ui",
            "message": "出现意外错误，已切换到安全模式",
            "report_error": True,
            "fallback_options": ["刷新页面", "返回首页", "联系支持"]
        }
    
    async def provide_user_guidance(self, 
                                   user_id: str,
                                   context: str = "initial") -> dict[str, Any]:
        """提供用户指导"""
        user_pref = self.user_preferences.get(user_id, UserPreference(user_id=user_id))
        
        # 判断是否需要显示指导
        if context == "initial" and user_id not in self.user_preferences:
            # 新用户，显示完整教程
            return {
                "show_tutorial": True,
                "tutorial_steps": self.tutorial_steps,
                "auto_start": True
            }
        elif context == "feature_discovery":
            # 功能发现指导
            return await self._get_feature_discovery_guidance(user_id)
        elif context == "error_recovery":
            # 错误恢复指导
            return await self._get_error_recovery_guidance(user_id)
        else:
            # 根据用户行为提供智能提示
            return await self._get_smart_guidance(user_id)
    
    async def _get_feature_discovery_guidance(self, user_id: str) -> dict[str, Any]:
        """获取功能发现指导"""
        # 分析用户还未使用的功能
        unused_features = await self._analyze_unused_features(user_id)
        
        return {
            "show_feature_tips": True,
            "featured_functions": unused_features[:3],  # 推荐3个功能
            "tip_style": "gentle",
            "dismissible": True
        }
    
    async def _get_error_recovery_guidance(self, user_id: str) -> dict[str, Any]:
        """获取错误恢复指导"""
        return {
            "show_help_overlay": True,
            "help_type": "recovery",
            "step_by_step": True,
            "visual_indicators": True
        }
    
    async def _get_smart_guidance(self, user_id: str) -> dict[str, Any]:
        """获取智能指导"""
        # 基于用户行为模式提供建议
        user_pattern = await self._analyze_user_pattern(user_id)
        
        if user_pattern.get("struggling_with_input"):
            return {
                "show_input_tips": True,
                "tips": [
                    "试试语音输入功能",
                    "使用模板快速开始",
                    "查看输入示例"
                ]
            }
        elif user_pattern.get("exploring_features"):
            return {
                "show_feature_tour": True,
                "tour_type": "interactive",
                "focus_areas": user_pattern.get("interest_areas", [])
            }
        else:
            return {"show_guidance": False}
    
    async def optimize_user_preferences(self, user_id: str, interaction_data: dict[str, Any]):
        """优化用户偏好"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = UserPreference(user_id=user_id)
        
        user_pref = self.user_preferences[user_id]
        
        # 分析交互数据优化偏好
        if "theme_preference" in interaction_data:
            user_pref.theme = interaction_data["theme_preference"]
        
        if "response_speed_preference" in interaction_data:
            speed_pref = interaction_data["response_speed_preference"]
            if speed_pref == "fast":
                user_pref.animation_enabled = False
            elif speed_pref == "smooth":
                user_pref.animation_enabled = True
        
        if "layout_changes" in interaction_data:
            user_pref.layout_config.update(interaction_data["layout_changes"])
        
        if "shortcuts_used" in interaction_data:
            for shortcut in interaction_data["shortcuts_used"]:
                user_pref.shortcuts[shortcut["action"]] = shortcut["key_combination"]
        
        user_pref.updated_at = datetime.now()
        
        # 持久化偏好设置
        await self._persist_user_preferences(user_id, user_pref)
    
    async def _analyze_performance_metrics(self):
        """分析性能指标"""
        if not self.performance_metrics:
            return
        
        # 最近1小时的指标
        recent_metrics = [
            m for m in self.performance_metrics
            if m.timestamp > datetime.now() - timedelta(hours=1)
        ]
        
        if not recent_metrics:
            return
        
        # 计算平均响应时间
        avg_response_time = sum(m.response_time for m in recent_metrics) / len(recent_metrics)
        
        # 分析慢响应
        slow_responses = [m for m in recent_metrics if m.response_time > self.response_time_threshold]
        
        # 记录分析结果
        logger.info(f"性能分析: 平均响应时间 {avg_response_time:.3f}s, 慢响应 {len(slow_responses)}/{len(recent_metrics)}")
        
        # 如果慢响应过多，触发优化
        if len(slow_responses) / len(recent_metrics) > 0.1:  # 超过10%
            await self._trigger_global_performance_optimization()
    
    async def _generate_optimization_suggestions(self):
        """生成优化建议"""
        # 基于性能数据生成优化建议
        suggestions = []
        
        # 分析组件性能
        component_performance = {}
        for metric in self.performance_metrics[-100:]:  # 最近100条记录
            comp = metric.component
            if comp not in component_performance:
                component_performance[comp] = []
            component_performance[comp].append(metric.response_time)
        
        for component, times in component_performance.items():
            avg_time = sum(times) / len(times)
            if avg_time > self.response_time_threshold:
                suggestions.append({
                    "type": "performance",
                    "component": component,
                    "issue": "slow_response",
                    "current_avg": avg_time,
                    "target": self.response_time_threshold,
                    "suggestions": [
                        "启用组件缓存",
                        "优化渲染逻辑",
                        "使用懒加载"
                    ]
                })
        
        if suggestions:
            logger.info(f"生成 {len(suggestions)} 个优化建议")
    
    async def _trigger_performance_optimization(self, action: UserAction, metric: PerformanceMetric):
        """触发性能优化"""
        optimization_actions = []
        
        # 根据组件类型选择优化策略
        if "input" in action.target_component.lower():
            optimization_actions.extend([
                "enable_input_debouncing",
                "cache_input_suggestions",
                "optimize_validation"
            ])
        elif "message" in action.target_component.lower():
            optimization_actions.extend([
                "enable_message_virtualization",
                "cache_message_rendering",
                "lazy_load_attachments"
            ])
        
        # 执行优化操作
        for opt_action in optimization_actions:
            await self._execute_optimization_action(opt_action, action.target_component)
    
    async def _execute_optimization_action(self, action: str, component: str):
        """执行优化操作"""
        logger.info(f"执行优化操作: {action} for {component}")
        
        if action == "enable_input_debouncing":
            # 启用输入防抖
            pass
        elif action == "cache_input_suggestions":
            # 缓存输入建议
            pass
        elif action == "enable_message_virtualization":
            # 启用消息虚拟化
            pass
        # ... 其他优化操作
    
    def get_performance_report(self) -> dict[str, Any]:
        """获取性能报告"""
        if not self.performance_metrics:
            return {"status": "no_data"}
        
        recent_metrics = [
            m for m in self.performance_metrics
            if m.timestamp > datetime.now() - timedelta(hours=24)
        ]
        
        if not recent_metrics:
            return {"status": "no_recent_data"}
        
        # 计算统计信息
        response_times = [m.response_time for m in recent_metrics]
        
        report = {
            "period": "24h",
            "total_interactions": len(recent_metrics),
            "avg_response_time": sum(response_times) / len(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "target_met_percentage": len([t for t in response_times if t < self.response_time_threshold]) / len(response_times) * 100,
            "response_level_distribution": {
                level.value: len([m for m in recent_metrics if m.response_level == level])
                for level in ResponseLevel
            },
            "component_performance": self._get_component_performance_summary(recent_metrics),
            "recommendations": self._get_performance_recommendations(recent_metrics)
        }
        
        return report
    
    def _get_component_performance_summary(self, metrics: list[PerformanceMetric]) -> dict[str, Any]:
        """获取组件性能汇总"""
        component_stats = {}
        
        for metric in metrics:
            comp = metric.component
            if comp not in component_stats:
                component_stats[comp] = []
            component_stats[comp].append(metric.response_time)
        
        summary = {}
        for comp, times in component_stats.items():
            summary[comp] = {
                "avg_response_time": sum(times) / len(times),
                "interaction_count": len(times),
                "performance_grade": self._calculate_performance_grade(times)
            }
        
        return summary
    
    def _calculate_performance_grade(self, response_times: list[float]) -> str:
        """计算性能等级"""
        avg_time = sum(response_times) / len(response_times)
        
        if avg_time < 0.1:
            return "A+"
        elif avg_time < 0.2:
            return "A"
        elif avg_time < 0.5:
            return "B"
        elif avg_time < 1.0:
            return "C"
        else:
            return "D"
    
    def _get_performance_recommendations(self, metrics: list[PerformanceMetric]) -> list[str]:
        """获取性能建议"""
        recommendations = []
        
        # 分析慢响应
        slow_responses = [m for m in metrics if m.response_time > self.response_time_threshold]
        if slow_responses:
            slow_percentage = len(slow_responses) / len(metrics) * 100
            if slow_percentage > 10:
                recommendations.append(f"有 {slow_percentage:.1f}% 的操作响应较慢，建议优化性能")
        
        # 分析组件性能
        component_times = {}
        for metric in metrics:
            comp = metric.component
            if comp not in component_times:
                component_times[comp] = []
            component_times[comp].append(metric.response_time)
        
        for comp, times in component_times.items():
            avg_time = sum(times) / len(times)
            if avg_time > self.response_time_threshold:
                recommendations.append(f"{comp} 组件响应较慢 ({avg_time:.3f}s)，建议优化")
        
        if not recommendations:
            recommendations.append("性能表现良好，继续保持！")
        
        return recommendations

class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        self.cache: dict[str, Any] = {}
        self.cache_timestamps: dict[str, datetime] = {}
        self.default_ttl = timedelta(minutes=30)
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if key not in self.cache:
            return None
        
        # 检查是否过期
        if key in self.cache_timestamps:
            if datetime.now() - self.cache_timestamps[key] > self.default_ttl:
                self.invalidate(key)
                return None
        
        return self.cache[key]
    
    def set(self, key: str, value: Any, ttl: Optional[timedelta] = None):
        """设置缓存"""
        self.cache[key] = value
        self.cache_timestamps[key] = datetime.now()
    
    def invalidate(self, key: str):
        """清除缓存"""
        self.cache.pop(key, None)
        self.cache_timestamps.pop(key, None)
    
    def clear_expired(self):
        """清除过期缓存"""
        now = datetime.now()
        expired_keys = [
            key for key, timestamp in self.cache_timestamps.items()
            if now - timestamp > self.default_ttl
        ]
        
        for key in expired_keys:
            self.invalidate(key)

class LazyLoadManager:
    """懒加载管理器"""
    
    def __init__(self):
        self.loaded_components: set = set()
        self.loading_queue: list[str] = []
    
    def register_component(self, component_id: str, load_trigger: str = "visible"):
        """注册懒加载组件"""
        if component_id not in self.loaded_components:
            self.loading_queue.append(component_id)
    
    def mark_loaded(self, component_id: str):
        """标记组件已加载"""
        self.loaded_components.add(component_id)
        if component_id in self.loading_queue:
            self.loading_queue.remove(component_id)
    
    def get_pending_loads(self) -> list[str]:
        """获取待加载组件"""
        return self.loading_queue.copy()

# 全局优化器实例
interactive_optimizer = InteractiveExperienceOptimizer()
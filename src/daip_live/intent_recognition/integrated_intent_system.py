"""
集成的意图识别系统

将上下文感知意图识别器无缝集成到现有DAIP系统中
提供统一的入口点和向后兼容性
"""

import logging
from typing import Any, Optional, Union

logger = logging.getLogger(__name__)

try:
    from .context_manager import ContextManager
    from .contextual_intent_recognizer import (
        ContextualIntent,
        ContextualIntentRecognizer,
        ConversationTurn,
    )
    from .enhanced_context_manager import EnhancedContextManager
    from .session_state import SessionState
except ImportError:
    try:
        from daip_live.intent_recognition.context_manager import ContextManager
        from daip_live.intent_recognition.contextual_intent_recognizer import (
            ContextualIntent,
            ContextualIntentRecognizer,
            ConversationTurn,
        )
        from daip_live.intent_recognition.enhanced_context_manager import (
            EnhancedContextManager,
        )
        from daip_live.intent_recognition.session_state import (
            SessionState,  # noqa: F401
        )
    except ImportError:
        # 为不同可能的模块结构提供备用导入路径
        from ..intent_recognition.context_manager import ContextManager
        from ..intent_recognition.contextual_intent_recognizer import (
            ContextualIntent,
            ContextualIntentRecognizer,
            ConversationTurn,
        )
        from ..intent_recognition.enhanced_context_manager import EnhancedContextManager

# 原有系统组件
from daip_live.agent_engine.enhanced_intent_recognizer import (  # noqa: E402
    EnhancedIntentRecognizer,
    Intent,
    IntentType,
)
from daip_live.agent_engine.services.clarification_service import (  # noqa: E402
    ClarificationService,
)

# 新增增强功能组件
try:
    from .anti_misrecognition_guard import AntiMisrecognitionGuard
    from .config_manager import ConfigManager, DynamicConfigurableIntentSystemMixin
    from .context_injector import ContextInjector
    from .context_integrator import ContextIntegrator
    from .entity_extractor import EntityExtractor
    from .error_handling import (
        IntentRecognitionErrorHandler,
        IntentRecognitionLogger,
        error_handler_decorator,
    )
    from .intent_fuser import IntentFuser
    from .intent_priority_decider import IntentPriorityDecider
    from .multi_model_context_handler import MultiModelContextReferenceHandler
    from .padatious_intent_recognizer import PadatiousEnhancedIntentRecognizer
    from .query_rewriter import QueryRewriter
    from .semantic_disambiguator import SemanticDisambiguator
except ImportError as e:
    logger.warning(f"Could not import enhanced components: {e}")
    PadatiousEnhancedIntentRecognizer = None
    ContextIntegrator = None
    QueryRewriter = None
    EntityExtractor = None
    IntentFuser = None
    AntiMisrecognitionGuard = None
    SemanticDisambiguator = None
    ContextInjector = None
    MultiModelContextReferenceHandler = None
    IntentPriorityDecider = None
    ConfigManager = None
    DynamicConfigurableIntentSystemMixin = None
    IntentRecognitionErrorHandler = None
    IntentRecognitionLogger = None
    error_handler_decorator = None

logger = logging.getLogger(__name__)


class IntegratedIntentSystem:
    """
    集成的意图识别系统

    特性：
    1. 完全向后兼容现有接口
    2. 自动启用上下文感知功能
    3. 智能槽位填充和参数推导
    4. 增强的澄清生成
    5. 详细的调试和监控信息
    6. 集成Padatious提升语义理解
    7. 防止误识别保护机制
    8. 意图优先级决策
    9. 跨模型上下文引用支持
    10. 动态配置管理
    """

    def __init__(
        self,
        enable_context_aware: bool = True,
        enable_debug: bool = False,
        enable_enhanced_features: bool = True,
        config_manager: Optional["ConfigManager"] = None,
    ):
        """
        初始化集成意图系统

        Args:
            enable_context_aware: 是否启用上下文感知功能
            enable_debug: 是否启用调试模式
            enable_enhanced_features: 是否启用增强功能（Padatious、语义消歧等）
            config_manager: 配置管理器（可选）
        """
        import time

        start_time = time.time()

        # 初始化配置管理
        if ConfigManager is not None:
            self.config_manager = config_manager or ConfigManager()
            self.config = self.config_manager.get_config()

            # 从配置获取参数，如果传入的参数为None，则使用配置值
            self.enable_context_aware = (
                enable_context_aware
                if enable_context_aware is not None
                else self.config.enable_context_aware
            )
            self.enable_debug = (
                enable_debug if enable_debug is not None else self.config.enable_debug
            )
            self.enable_enhanced_features = (
                enable_enhanced_features
                if enable_enhanced_features is not None
                else self.config.enable_enhanced_features
            )
        else:
            # 如果配置管理不可用，使用传入的参数
            self.config_manager = None
            self.config = None
            self.enable_context_aware = enable_context_aware
            self.enable_debug = enable_debug
            self.enable_enhanced_features = enable_enhanced_features

        # 性能优化配置 - 从配置或默认值获取
        self.response_time_threshold = getattr(
            self.config, "response_time_threshold", 0.1
        )  # 100ms阈值
        self.context_cache_ttl = getattr(
            self.config, "context_cache_ttl", 300
        )  # 上下文缓存5分钟
        self.intent_cache_size = getattr(
            self.config, "intent_cache_size", 1000
        )  # 意图缓存大小
        self.intent_cache = {}  # 意图识别结果缓存

        # 原有组件
        self.base_recognizer = EnhancedIntentRecognizer()
        self.clarification_service = ClarificationService()

        # 增强组件 - 只有在启用增强功能时才初始化
        self.padatious_recognizer = None
        self.context_integrator = None
        self.query_rewriter = None
        self.entity_extractor = None
        self.intent_fuser = None
        self.anti_misrecognition_guard = None
        self.semantic_disambiguator = None
        self.context_injector = None
        self.multi_model_handler = None
        self.intent_priority_decider = None

        # 初始化错误处理和日志记录机制
        if IntentRecognitionErrorHandler is not None:
            self.error_handler = IntentRecognitionErrorHandler()
        else:
            self.error_handler = None

        if IntentRecognitionLogger is not None:
            self.intent_logger = IntentRecognitionLogger()
        else:
            # 使用标准日志记录
            self.intent_logger = None

        # 性能统计优化
        self.initialization_time = time.time() - start_time
        if self.initialization_time > 2.0:  # 如果初始化时间超过2秒，记录警告
            logger.warning(
                f"System initialization took {self.initialization_time:.2f}s"
            )

        if enable_enhanced_features and all(
            [
                PadatiousEnhancedIntentRecognizer,
                ContextIntegrator,
                QueryRewriter,
                EntityExtractor,
                IntentFuser,
                AntiMisrecognitionGuard,
                SemanticDisambiguator,
                ContextInjector,
                MultiModelContextReferenceHandler,
                IntentPriorityDecider,
            ]
        ):
            try:
                # 初始化增强组件
                self.context_integrator = ContextIntegrator()
                self.entity_extractor = EntityExtractor()
                self.query_rewriter = QueryRewriter(self.entity_extractor)

                # 初始化防误识别守护器
                self.anti_misrecognition_guard = AntiMisrecognitionGuard()

                # 初始化语义消歧器
                self.semantic_disambiguator = SemanticDisambiguator()

                # 初始化意图融合器
                self.intent_fuser = IntentFuser()

                # 初始化上下文注入器
                self.context_injector = ContextInjector(self.context_integrator)

                # 初始化多模型上下文处理器
                self.multi_model_handler = MultiModelContextReferenceHandler(
                    self.context_integrator, self.entity_extractor
                )

                # 初始化意图优先级决策器
                self.intent_priority_decider = IntentPriorityDecider()

                # 初始化Padatious意图识别器
                self.padatious_recognizer = PadatiousEnhancedIntentRecognizer(
                    self.base_recognizer, self.context_integrator
                )

                logger.info(
                    "All enhanced intent recognition components initialized successfully"  # noqa: E501
                )
            except Exception as e:
                logger.error(f"Failed to initialize enhanced components: {e}")
                # 降级到基础功能
                self.enable_enhanced_features = False

        # 增强组件（如果启用上下文感知）
        if enable_context_aware:
            self.context_manager = EnhancedContextManager()
            self.contextual_recognizer = ContextualIntentRecognizer(
                self.base_recognizer
            )
        else:
            self.context_manager = ContextManager()
            self.contextual_recognizer = None

        # 性能统计
        self.recognition_stats = {
            "total_requests": 0,
            "context_aware_hits": 0,
            "slot_filling_successes": 0,
            "clarification_requests": 0,
            "inference_successes": 0,
            "enhanced_recognition_successes": 0,  # 新增增强识别成功统计
            "misrecognition_protection_hits": 0,  # 新增误识别保护统计
            "semantic_disambiguation_successes": 0,  # 新增语义消歧统计
        }

        # 配置
        self.max_conversation_history = 10
        self.confidence_threshold = 0.3
        self.auto_complete_threshold = 0.8

        logger.info(
            f"IntegratedIntentSystem initialized (context_aware={enable_context_aware}, enhanced_features={enable_enhanced_features})"  # noqa: E501
        )

    def _get_cache_key(self, user_input: str, session_id: str) -> str:
        """生成缓存键"""
        return f"{session_id}:{hash(user_input) % 10000}"

    def _get_cached_result(self, user_input: str, session_id: str):
        """从缓存获取结果"""
        if not self.intent_cache:
            return None

        cache_key = self._get_cache_key(user_input, session_id)
        cached_item = self.intent_cache.get(cache_key)

        if cached_item:
            result, timestamp = cached_item
            # 检查是否过期（暂不实现过期机制，可根据需要添加）
            return result
        return None

    def _cache_result(self, user_input: str, session_id: str, result):
        """缓存结果"""
        import time

        if len(self.intent_cache) >= self.intent_cache_size:
            # 简单的缓存清理：移除第一个项目（FIFO）
            first_key = next(iter(self.intent_cache))
            del self.intent_cache[first_key]

        cache_key = self._get_cache_key(user_input, session_id)
        self.intent_cache[cache_key] = (result, time.time())

    def recognize_intent(
        self, user_input: str, session_id: str = "default"
    ) -> Union[Intent, ContextualIntent]:
        """
        统一的意图识别入口

        Args:
            user_input: 用户输入
            session_id: 会话ID

        Returns:
            Intent 或 ContextualIntent 对象
        """
        import time

        start_time = time.time()

        self.recognition_stats["total_requests"] += 1

        # 使用增强日志记录
        if self.intent_logger:
            self.intent_logger.log_intent_recognition_start(user_input, session_id)
        elif self.enable_debug:
            logger.debug(f"Recognizing intent for session {session_id}: '{user_input}'")

        # 尝试从缓存获取结果
        cached_result = self._get_cached_result(user_input, session_id)
        if cached_result is not None:
            if self.enable_debug:
                logger.debug(f"Cache hit for session {session_id}")
            # 记录缓存命中
            if self.intent_logger:
                self.intent_logger.log_cache_operation("hit")
            return cached_result

        try:
            # 如果启用增强功能，使用增强识别流程
            if self.enable_enhanced_features and self.padatious_recognizer:
                result = self._recognize_intent_enhanced(user_input, session_id)
            else:
                # 使用原有识别流程
                result = self._recognize_intent_original(user_input, session_id)

            # 计算处理时间
            processing_time = time.time() - start_time

            # 记录性能警告（如果超过阈值）
            if processing_time > self.response_time_threshold:
                if self.intent_logger:
                    self.intent_logger.log_performance_warning(
                        "intent_recognition",
                        processing_time,
                        self.response_time_threshold,
                        session_id,
                    )
                else:
                    logger.warning(
                        f"Intent recognition took {processing_time * 1000:.2f}ms for session {session_id}"  # noqa: E501
                    )

            # 记录意图识别结果
            if self.intent_logger:
                confidence = getattr(result, "confidence", 0) if result else 0
                intent_name = (
                    getattr(result, "name", "unknown") if result else "unknown"
                )
                self.intent_logger.log_intent_recognition_result(
                    intent_name, confidence, session_id, processing_time
                )

            # 缓存结果（只缓存确定性的结果，避免缓存错误结果）
            if result and hasattr(result, "name") and result.name != "error":
                self._cache_result(user_input, session_id, result)
                # 更新缓存统计
                if hasattr(self, "cache_hits"):
                    self.cache_hits += 1
                else:
                    self.cache_hits = 1

            return result

        except Exception as e:
            # 使用错误处理器
            if self.error_handler:
                return self.error_handler.handle_error(
                    e,
                    "IntegratedIntentSystem.recognize_intent",
                    session_id,
                    user_input,
                    Intent(
                        name="error",
                        confidence=0.0,
                        parameters={"error": str(e), "original_input": user_input},
                        description="Intent recognition error",
                        intent_type=IntentType.CHAT,
                        requires_confidence_check=False,
                    ),
                )
            else:
                logger.error(f"Intent recognition failed: {e}")
                # 创建错误意图
                error_intent = Intent(
                    name="error",
                    confidence=0.0,
                    parameters={"error": str(e), "original_input": user_input},
                    description="Intent recognition error",
                    intent_type=IntentType.CHAT,
                    requires_confidence_check=False,
                )
                return error_intent

    def _recognize_intent_enhanced(
        self, user_input: str, session_id: str = "default"
    ) -> Union[Intent, ContextualIntent]:
        """
        增强的意图识别流程，集成Padatious、语义消歧、防误识别等功能
        """
        import time

        start_time = time.time()

        # 1. 获取上下文信息（使用缓存优化）
        context = {}
        if self.context_integrator:
            context = self.context_integrator.get_context_for_intent_recognition(
                session_id
            )

        current_time = time.time()
        if current_time - start_time > 0.05:  # 如果上下文获取已超过50ms，记录警告
            logger.warning(
                f"Context retrieval took {(current_time - start_time) * 1000:.2f}ms for session {session_id}"  # noqa: E501
            )

        # 2. 使用查询重写器处理输入
        processed_input = user_input
        if self.query_rewriter:
            qr_start = time.time()
            processed_input = self.query_rewriter.rewrite_query_with_context(
                user_input, session_id
            )
            qr_time = time.time() - qr_start
            if qr_time > 0.02:  # 如果查询重写超过20ms，记录警告
                logger.warning(
                    f"Query rewriting took {qr_time * 1000:.2f}ms for session {session_id}"  # noqa: E501
                )

        # 3. 获取Padatious识别结果（带超时和缓存）
        padatious_result = None
        if self.padatious_recognizer:
            try:
                p_start = time.time()
                padatious_result = self.padatious_recognizer._recognize_with_padatious(
                    processed_input, context
                )
                p_time = time.time() - p_start
                if p_time > 0.03:  # 如果Padatious识别超过30ms，记录警告
                    logger.warning(
                        f"Padatious recognition took {p_time * 1000:.2f}ms for session {session_id}"  # noqa: E501
                    )
            except Exception as e:
                logger.warning(f"Padatious recognition failed: {e}")

        # 4. 获取原有意图识别结果（并行或快速路径）
        base_intent_start = time.time()
        base_intent = self.base_recognizer.recognize_intent(user_input, session_id)
        time.time() - base_intent_start

        # 5. 融合意图结果（优化融合逻辑）
        fused_result = base_intent
        if self.intent_fuser and padatious_result:
            if time.time() - start_time < 0.07:  # 只有在还有时间预算时才进行融合
                fused_result = self.intent_fuser.fuse_intents(
                    padatious_result, base_intent, context
                )
                self.recognition_stats["enhanced_recognition_successes"] += 1

        # 6. 检查多意图候选情况并进行语义消歧（快速路径）
        if (
            self.semantic_disambiguator
            and isinstance(fused_result, list)
            and time.time() - start_time < 0.06
        ):  # 只有在时间允许时进行消歧
            # 如果有多个候选意图，进行消歧
            selected_intent = self.semantic_disambiguator.disambiguate_with_text(
                user_input, fused_result, context
            )
            self.recognition_stats["semantic_disambiguation_successes"] += 1
        else:
            selected_intent = fused_result

        # 7. 应用防误识别保护（优化的保护逻辑）
        protected_intent = selected_intent
        if self.anti_misrecognition_guard:
            # 快速检测是否需要保护
            needs_protection = self._check_if_protection_needed(
                selected_intent, context, user_input
            )
            if needs_protection and time.time() - start_time < 0.08:
                protected_intent = (
                    self.anti_misrecognition_guard.apply_antimisrecognition_protection(
                        selected_intent, context
                    )
                )
                # 检查是否应用了保护（置信度发生变化）
                if hasattr(selected_intent, "confidence") and hasattr(
                    protected_intent, "confidence"
                ):
                    if selected_intent.confidence != protected_intent.confidence:
                        self.recognition_stats["misrecognition_protection_hits"] += 1

        # 8. 应用意图优先级决策（轻量级决策）
        prioritized_intent = protected_intent
        if self.intent_priority_decider and time.time() - start_time < 0.08:
            # 将意图放入列表中以应用决策逻辑
            intent_list = [protected_intent]
            # 在问候等特定上下文中调整优先级
            adjusted_intents = (
                self.intent_priority_decider.ensure_chat_priority_in_greeting_context(
                    intent_list, user_input
                )
            )
            # 获取防误识别保护的调整（如果时间还允许）
            if time.time() - start_time < 0.09:
                priority_adjusted_intents = self.intent_priority_decider.adjust_priority_for_misrecognition_protection(  # noqa: E501
                    adjusted_intents, context
                )
                if priority_adjusted_intents:
                    prioritized_intent = priority_adjusted_intents[0]

        # 9. 使用上下文感知识别器增强（如果启用，且时间允许）
        if self.contextual_recognizer and time.time() - start_time < 0.09:
            # 创建一个增强的上下文意图
            contextual_intent = ContextualIntent(
                intent=prioritized_intent,
                conversation_context=context,
                missing_slots=[],
                filled_slots={},
                inferred_params={},
                clarification_needed=False,
                clarification_message="",
                next_step="",
                confidence_boost=0.0,
            )

            # 更新统计
            if (
                hasattr(contextual_intent, "filled_slots")
                and contextual_intent.filled_slots
            ):
                self.recognition_stats["slot_filling_successes"] += 1
            if (
                hasattr(contextual_intent, "clarification_needed")
                and contextual_intent.clarification_needed
            ):
                self.recognition_stats["clarification_requests"] += 1
            if (
                hasattr(contextual_intent, "inferred_params")
                and contextual_intent.inferred_params
            ):
                self.recognition_stats["inference_successes"] += 1
            if (
                hasattr(contextual_intent, "confidence_boost")
                and contextual_intent.confidence_boost > 0
            ):
                self.recognition_stats["context_aware_hits"] += 1

            # 记录调试信息
            if self.enable_debug:
                self._log_contextual_intent(contextual_intent, session_id)

            total_time = time.time() - start_time
            if total_time > 0.1:  # 超过100ms记录警告
                logger.warning(
                    f"Intent recognition took {total_time * 1000:.2f}ms for session {session_id}"  # noqa: E501
                )
            return contextual_intent

        # 10. 返回最终意图
        total_time = time.time() - start_time
        if self.enable_debug:
            self._log_base_intent(prioritized_intent, session_id)
        if total_time > 0.1:  # 超过100ms记录警告
            logger.warning(
                f"Intent recognition took {total_time * 1000:.2f}ms for session {session_id}"  # noqa: E501
            )

        return prioritized_intent

    def _check_if_protection_needed(
        self,
        intent: Union[Intent, ContextualIntent],
        context: dict[str, Any],
        user_input: str,
    ) -> bool:
        """
        快速检查是否需要防误识别保护
        """
        # 快速检查：是否是论文相关意图，且上下文可能表明确实是聊天意图
        if hasattr(intent, "name") and intent.name in [
            "search_papers",
            "download_paper",
        ]:
            # 检查用户输入是否包含聊天关键词
            chat_indicators = [
                "你好",
                "help",
                "啊",
                "呢",
                "呀",
                "吗",
                "为啥",
                "为什么",
                "啥",
            ]
            return any(indicator in user_input for indicator in chat_indicators)
        return False

    def _recognize_intent_original(
        self, user_input: str, session_id: str = "default"
    ) -> Union[Intent, ContextualIntent]:
        """
        原有的意图识别流程（向后兼容）
        """
        # 使用上下文感知识别器
        if self.contextual_recognizer:
            contextual_intent = self.contextual_recognizer.recognize_intent(
                user_input, session_id
            )

            # 更新统计
            if contextual_intent.filled_slots or contextual_intent.inferred_params:
                self.recognition_stats["slot_filling_successes"] += 1
            if contextual_intent.clarification_needed:
                self.recognition_stats["clarification_requests"] += 1
            if contextual_intent.inferred_params:
                self.recognition_stats["inference_successes"] += 1
            if contextual_intent.confidence_boost > 0:
                self.recognition_stats["context_aware_hits"] += 1

            # 记录调试信息
            if self.enable_debug:
                self._log_contextual_intent(contextual_intent, session_id)

            return contextual_intent

        # 回退到基础识别器
        else:
            base_intent = self.base_recognizer.recognize_intent(user_input, session_id)
            if self.enable_debug:
                self._log_base_intent(base_intent, session_id)
            return base_intent

    def start_contextual_task(
        self,
        session_id: str,
        task_type: str,
        required_params: list[str] = None,
        initial_params: dict[str, Any] = None,
    ) -> bool:
        """
        开始上下文感知的任务

        Args:
            session_id: 会话ID
            task_type: 任务类型
            required_params: 必需参数列表
            initial_params: 初始参数

        Returns:
            是否成功启动任务
        """
        if not self.enable_context_aware:
            # 回退到基础管理器
            if required_params is None:
                required_params = []
            if initial_params is None:
                initial_params = {}

            context_data = {
                "task_type": task_type,
                "required_params": required_params,
                "filled_params": initial_params,
            }
            self.context_manager.set_context(session_id, context_data)

            for param_name, param_value in initial_params.items():
                self.context_manager.add_task_parameter(
                    session_id, param_name, param_value
                )

            return True

        # 使用增强上下文管理器
        from .enhanced_context_manager import ParameterSource

        # 创建或获取对话上下文
        context = self.context_manager.get_conversation_context(session_id)
        if not context:
            topic = (
                initial_params.get("topic", "")
                or initial_params.get("title", "")
                or task_type
            )
            context = self.context_manager.create_conversation_context(
                session_id, task_type, topic
            )

        # 设置必需参数
        if required_params is None:
            required_params = []

        # 添加初始参数
        if initial_params:
            for param_name, param_value in initial_params.items():
                self.context_manager.add_parameter_with_source(
                    session_id, param_name, param_value, ParameterSource.USER_INPUT
                )

        # 尝试参数继承
        inherited_params = self.context_manager.inherit_parameters(
            session_id, task_type, required_params
        )
        for param_name, param_value in inherited_params.items():
            self.context_manager.add_parameter_with_source(
                session_id, param_name, param_value, ParameterSource.CONTEXT_INHERIT
            )

        # 同步到基础管理器
        context_data = {
            "task_type": task_type,
            "required_params": required_params,
            "filled_params": {**initial_params, **inherited_params},
        }
        self.context_manager.base_manager.set_context(session_id, context_data)

        # 如果启用了增强功能，也更新增强组件的上下文
        if self.enable_enhanced_features:
            self._update_enhanced_context(
                session_id, task_type, initial_params, inherited_params
            )

        logger.info(f"Started contextual task: {task_type} for session {session_id}")
        return True

    def _update_enhanced_context(
        self,
        session_id: str,
        task_type: str,
        initial_params: dict[str, Any],
        inherited_params: dict[str, Any],
    ):
        """
        更新增强组件的上下文信息
        """
        if not self.context_integrator:
            return

        # 更新实体提取器的上下文
        if self.entity_extractor and hasattr(self.entity_extractor, "session_manager"):
            # 这里可以通知实体提取器更新上下文
            pass

        # 更新多模型上下文处理器
        if self.multi_model_handler:
            context_data = {
                "task_type": task_type,
                "initial_params": initial_params,
                "inherited_params": inherited_params,
            }
            self.multi_model_handler.update_model_context(
                session_id, task_type, context_data
            )

    def update_context_with_enhanced_features(
        self,
        session_id: str,
        intent: Union[Intent, ContextualIntent],
        user_input: str,
        processed_result: Union[Intent, ContextualIntent] = None,
    ):
        """
        使用增强功能更新上下文信息
        """
        # 更新基础上下文
        if self.contextual_recognizer and processed_result:
            self.contextual_recognizer._update_conversation_history(
                session_id, user_input, processed_result
            )

        # 如果启用了增强功能，也更新增强组件的上下文
        if self.enable_enhanced_features and self.context_integrator:
            # 更新上下文集成器的缓存
            self.context_integrator.get_context_for_intent_recognition(session_id)

            # 更新实体提取器
            if self.entity_extractor:
                # 实体提取器会在下一次调用时自动使用更新的上下文
                pass

            # 更新多模型上下文处理器
            if self.multi_model_handler:
                # 处理跨模型引用
                self.multi_model_handler.handle_cross_model_reference(
                    user_input, getattr(intent, "name", "unknown"), session_id
                )

    def is_session_in_task(self, session_id: str) -> bool:
        """检查会话是否在任务中"""
        return self.context_manager.is_in_task(session_id)

    def set_session_manager(self, session_manager):
        """
        设置SessionManager实例以实现更好的集成
        """
        self.session_manager = session_manager
        # 同时更新组件中的引用
        if self.context_integrator:
            self.context_integrator.session_manager = session_manager
        if self.entity_extractor:
            self.entity_extractor.session_manager = session_manager
        if self.multi_model_handler and self.multi_model_handler.context_integrator:
            self.multi_model_handler.context_integrator.session_manager = (
                session_manager
            )

    def get_session_context(self, session_id: str) -> Optional[dict[str, Any]]:
        """获取会话上下文"""
        # 如果有session_manager且支持get_session_context，优先使用
        if (
            hasattr(self, "session_manager")
            and self.session_manager
            and hasattr(self.session_manager, "get_session_context")
        ):
            try:
                session_context = self.session_manager.get_session_context(session_id)
                if session_context:
                    # 合并通用会话上下文和意图识别上下文
                    context = (
                        self.context_manager.get_conversation_context(session_id)
                        if self.enable_context_aware
                        else None
                    )
                    base_context = self.context_manager.get_context(session_id)

                    result = session_context  # 从session_manager获取的基本信息
                    if context:
                        # 添加意图识别特有的信息
                        result.update(
                            {
                                "current_intent": context.current_intent,
                                "intent_history": context.intent_history,
                                "related_entities": list(context.related_entities),
                                "conversation_summary": context.conversation_summary,
                                "intent_parameters": context.get_filled_parameters(),
                            }
                        )
                    elif base_context:
                        result.update(
                            {"intent_parameters": base_context.get("filled_params", {})}
                        )

                    return result
            except Exception as e:
                logger.warning(
                    f"Failed to get session context from session_manager: {e}"
                )

        # 回退到原有逻辑
        if self.enable_context_aware:
            context = self.context_manager.get_conversation_context(session_id)
            if context:
                return {
                    "session_id": context.session_id,
                    "topic": context.topic,
                    "current_intent": context.current_intent,
                    "intent_history": context.intent_history,
                    "parameters": context.get_filled_parameters(),
                    "status": context.status.value,
                    "related_entities": list(context.related_entities),
                    "conversation_summary": context.conversation_summary,
                }

        return self.context_manager.get_context(session_id)

    def clear_session_context(self, session_id: str):
        """清除会话上下文"""
        # 如果有session_manager，也清理它的上下文
        if hasattr(self, "session_manager") and self.session_manager:
            try:
                if hasattr(self.session_manager, "end_session"):
                    self.session_manager.end_session(session_id)
            except Exception as e:
                logger.warning(f"Failed to clear session in session_manager: {e}")

        self.context_manager.clear_context(session_id)
        if self.contextual_recognizer:
            self.contextual_recognizer.clear_session_history(session_id)

        # 清理增强组件的上下文
        if self.enable_enhanced_features:
            if self.multi_model_handler:
                if session_id in self.multi_model_handler.cross_model_contexts:
                    del self.multi_model_handler.cross_model_contexts[session_id]

        logger.info(f"Cleared context for session {session_id}")

    def get_conversation_history(self, session_id: str) -> list[ConversationTurn]:
        """获取对话历史"""
        # 如果有session_manager且支持获取历史，优先使用
        if (
            hasattr(self, "session_manager")
            and self.session_manager
            and hasattr(self.session_manager, "get_session_context")
        ):
            try:
                session_context = self.session_manager.get_session_context(session_id)
                if session_context and "dialogue_history" in session_context:
                    # 将session_manager的对话历史转换为ConversationTurn格式
                    history_data = session_context["dialogue_history"]
                    turns = []
                    for item in history_data:
                        if isinstance(item, dict):
                            turn = ConversationTurn(
                                user_input=item.get("content", ""),
                                intent=None,  # 可能需要从历史中恢复意图信息
                                extracted_params=item.get("parameters", {}),
                                missing_params=[],
                                filled_params=item.get("filled_params", {}),
                                timestamp=item.get("timestamp", None),
                            )
                            turns.append(turn)
                    return turns
            except Exception as e:
                logger.warning(
                    f"Failed to get conversation history from session_manager: {e}"
                )

        # 回退到原有逻辑
        if self.contextual_recognizer:
            return self.contextual_recognizer.get_conversation_history(session_id)
        return []

    def get_session_statistics(self, session_id: str) -> Optional[dict[str, Any]]:
        """获取会话统计信息 - 增强版"""
        # 首先获取原有统计
        base_stats = (
            super().get_session_statistics(session_id)
            if hasattr(super(), "get_session_statistics")
            else {}
        )

        # 获取session_manager的统计（如果可用）
        session_stats = {}
        if hasattr(self, "session_manager") and self.session_manager:
            try:
                if hasattr(self.session_manager, "get_session_statistics"):
                    session_stats = self.session_manager.get_session_statistics(
                        session_id
                    )
            except Exception as e:
                logger.warning(
                    f"Failed to get session statistics from session_manager: {e}"
                )

        # 获取增强功能的统计
        enhanced_stats = {}
        if self.enable_enhanced_features:
            enhanced_stats = {
                "enhanced_recognition_stats": self.recognition_stats.copy(),
            }
            if self.multi_model_handler:
                enhanced_stats["cross_model_context"] = (
                    self.multi_model_handler.get_shared_context(session_id)
                )

        # 合并所有统计
        result = {**base_stats, **session_stats, **enhanced_stats}

        context_stats = {}
        if self.enable_context_aware:
            context_stats = self.context_manager.get_session_statistics(session_id)
            if context_stats:
                context_stats.update(
                    {
                        "system_stats": self.recognition_stats.copy(),
                        "context_aware_enabled": True,
                    }
                )
            else:
                context_stats = {
                    "system_stats": self.recognition_stats.copy(),
                    "context_aware_enabled": True,
                }
        else:
            context_stats = {
                "system_stats": self.recognition_stats.copy(),
                "context_aware_enabled": False,
            }

        result.update(context_stats)
        return result

    def generate_clarification_message(
        self, intent: Union[Intent, ContextualIntent], session_id: str = "default"
    ) -> Optional[str]:
        """
        生成澄清消息

        Args:
            intent: 意图对象
            session_id: 会话ID

        Returns:
            澄清消息或None
        """
        # 如果是上下文增强意图，直接使用其澄清消息
        if isinstance(intent, ContextualIntent) and intent.clarification_needed:
            return intent.clarification_message

        # 对于基础意图，使用原有澄清服务
        if isinstance(intent, Intent) and intent.requires_clarification:
            if intent.clarification_needed:
                if isinstance(intent.clarification_needed, dict):
                    return intent.clarification_needed.get("message", "")
                return str(intent.clarification_needed)

        return None

    def get_next_step_suggestion(
        self, intent: Union[Intent, ContextualIntent], session_id: str = "default"
    ) -> str:
        """
        获取下一步行动建议

        Args:
            intent: 意图对象
            session_id: 会话ID

        Returns:
            下一步行动建议
        """
        if isinstance(intent, ContextualIntent):
            return intent.next_step

        # 对于基础意图，生成基本建议
        if isinstance(intent, Intent):
            if intent.name == "start_debate":
                topic = intent.parameters.get("topic", "未指定主题")
                rounds = intent.parameters.get("rounds", 3)
                return f"准备开始关于'{topic}'的辩论，共{rounds}轮"
            elif intent.name == "create_wiki":
                title = intent.parameters.get("title", "未指定标题")
                return f"准备创建维基页面：{title}"
            elif intent.name == "search_papers":
                query = intent.parameters.get("query", "未指定查询")
                return f"准备搜索论文：{query}"
            elif intent.name == "execute_skill":
                content = intent.parameters.get("content", "未指定内容")
                return f"准备执行技能：{content}"
            else:
                return f"继续处理：{intent.description}"

        return "请提供更具体的指令"

    def is_task_complete(self, session_id: str) -> bool:
        """检查任务是否完成"""
        if not self.context_manager.is_in_task(session_id):
            return False

        # 获取任务上下文
        task_context = self.context_manager.get_context(session_id)
        if not task_context:
            return False

        # 检查是否所有必需参数都已填充
        required_params = task_context.get("required_params", [])
        filled_params = task_context.get("filled_params", {})

        return all(param in filled_params for param in required_params)

    def get_missing_parameters(self, session_id: str) -> list[str]:
        """获取缺失的参数列表"""
        if not self.context_manager.is_in_task(session_id):
            return []

        task_context = self.context_manager.get_context(session_id)
        if not task_context:
            return []

        required_params = task_context.get("required_params", [])
        filled_params = task_context.get("filled_params", {})

        return [param for param in required_params if param not in filled_params]

    def export_session_data(self, session_id: str) -> Optional[dict[str, Any]]:
        """导出会话数据"""
        data = {
            "session_id": session_id,
            "timestamp": str(
                self.context_manager.conversation_contexts.get(session_id, {}).get(
                    "last_accessed", ""
                )
            ),
            "statistics": self.get_session_statistics(session_id),
            "context": self.get_session_context(session_id),
            "conversation_history": [
                {
                    "user_input": turn.user_input,
                    "intent_name": turn.intent.name if turn.intent else None,
                    "parameters": turn.filled_params,
                    "timestamp": turn.timestamp.isoformat(),
                    "strategy_used": turn.strategy_used.value
                    if turn.strategy_used
                    else None,
                }
                for turn in self.get_conversation_history(session_id)
            ],
        }

        # 如果有session_manager，也导出其数据
        if hasattr(self, "session_manager") and self.session_manager:
            try:
                if hasattr(self.session_manager, "export_context"):
                    session_data = self.session_manager.export_context(session_id)
                    if session_data:
                        data["session_manager_data"] = session_data
            except Exception as e:
                logger.warning(
                    f"Failed to export session data from session_manager: {e}"
                )

        # 如果启用了增强功能，导出增强组件的数据
        if self.enable_enhanced_features:
            enhanced_data = {}
            if self.multi_model_handler:
                cross_model_data = self.multi_model_handler.get_shared_context(
                    session_id
                )
                if cross_model_data:
                    enhanced_data["cross_model_context"] = cross_model_data
            if enhanced_data:
                data["enhanced_features_data"] = enhanced_data

        return data

    def reset_statistics(self):
        """重置统计信息"""
        self.recognition_stats = {
            "total_requests": 0,
            "context_aware_hits": 0,
            "slot_filling_successes": 0,
            "clarification_requests": 0,
            "inference_successes": 0,
        }

    def _log_contextual_intent(self, intent: ContextualIntent, session_id: str):
        """记录上下文意图调试信息"""
        logger.debug(f"Session {session_id} contextual intent result:")
        logger.debug(f"  Intent: {intent.intent.name if intent.intent else 'None'}")
        logger.debug(
            f"  Base Confidence: {intent.intent.confidence if intent.intent else 0:.3f}"
        )
        logger.debug(f"  Context Boost: {intent.confidence_boost:.3f}")
        logger.debug(f"  Filled Slots: {list(intent.filled_slots.keys())}")
        logger.debug(f"  Missing Slots: {intent.missing_slots}")
        logger.debug(f"  Inferred Params: {list(intent.inferred_params.keys())}")
        logger.debug(f"  Clarification Needed: {intent.clarification_needed}")
        logger.debug(f"  Next Step: {intent.next_step}")

    def _log_base_intent(self, intent: Intent, session_id: str):
        """记录基础意图调试信息"""
        logger.debug(f"Session {session_id} base intent result:")
        logger.debug(f"  Intent: {intent.name}")
        logger.debug(f"  Confidence: {intent.confidence:.3f}")
        logger.debug(f"  Parameters: {list(intent.parameters.keys())}")
        logger.debug(f"  Requires Clarification: {intent.requires_clarification}")

    def get_system_info(self) -> dict[str, Any]:
        """获取系统信息"""
        return {
            "system_type": "IntegratedIntentSystem",
            "context_aware_enabled": self.enable_context_aware,
            "debug_enabled": self.enable_debug,
            "max_conversation_history": self.max_conversation_history,
            "confidence_threshold": self.confidence_threshold,
            "auto_complete_threshold": self.auto_complete_threshold,
            "statistics": self.recognition_stats.copy(),
            "active_sessions": len(self.context_manager.conversation_contexts)
            if self.enable_context_aware
            else 0,
        }

    def cleanup_expired_sessions(self):
        """清理过期会话"""
        if self.enable_context_aware:
            self.context_manager.cleanup_expired_contexts()
            logger.debug("Cleaned up expired contexts")

    def health_check(self) -> dict[str, Any]:
        """系统健康检查"""
        return {
            "status": "healthy",
            "context_aware_working": self.enable_context_aware
            and self.contextual_recognizer is not None,
            "base_recognizer_working": self.base_recognizer is not None,
            "clarification_service_working": self.clarification_service is not None,
            "active_sessions": len(self.context_manager.conversation_contexts)
            if self.enable_context_aware
            else 0,
            "total_requests_processed": self.recognition_stats["total_requests"],
            "context_aware_hit_rate": (
                self.recognition_stats["context_aware_hits"]
                / max(1, self.recognition_stats["total_requests"])
            ),
            "last_cleanup": str(self.context_manager.conversation_contexts)
            if self.enable_context_aware
            else "N/A",
        }

    def update_system_config(self, updates: dict[str, Any]) -> bool:
        """
        更新系统配置

        Args:
            updates: 配置更新字典

        Returns:
            是否更新成功
        """
        if self.config_manager is None:
            logger.warning("ConfigManager not available, cannot update configuration")
            return False

        success = self.config_manager.update_config(updates)
        if success:
            # 重新加载配置
            self.config = self.config_manager.get_config()

            # 更新系统参数以反映新的配置
            self._apply_config_to_system()

        return success

    def _apply_config_to_system(self):
        """
        将配置应用到系统参数
        """
        if self.config is None:
            return

        # 更新性能相关参数
        self.response_time_threshold = self.config.response_time_threshold
        self.context_cache_ttl = self.config.context_cache_ttl
        self.intent_cache_size = self.config.intent_cache_size

        # 更新功能启用状态
        self.enable_context_aware = self.config.enable_context_aware
        self.enable_debug = self.config.enable_debug
        self.enable_enhanced_features = self.config.enable_enhanced_features

        # 如果缓存大小发生变化，调整缓存
        if len(self.intent_cache) > self.intent_cache_size:
            # 清理多余的缓存项
            keys_to_remove = list(self.intent_cache.keys())[self.intent_cache_size :]
            for key in keys_to_remove:
                del self.intent_cache[key]

    def get_current_config(self) -> Optional[Any]:
        """
        获取当前系统配置

        Returns:
            当前配置对象或None
        """
        return self.config

    def get_config_diff(self) -> dict[str, Any]:
        """
        获取配置差异

        Returns:
            配置差异字典
        """
        if self.config_manager is None:
            return {}
        return self.config_manager.get_config_diff()

    def reset_to_default_config(self) -> bool:
        """
        重置为默认配置

        Returns:
            是否重置成功
        """
        if self.config_manager is None:
            logger.warning("ConfigManager not available, cannot reset configuration")
            return False

        success = self.config_manager.reset_to_defaults()
        if success:
            self.config = self.config_manager.get_config()
            self._apply_config_to_system()

        return success

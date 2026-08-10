"""
Enhanced Debate Manager with Model-Per-Role Support

This manager extends the base debate system to support different models for different roles,
with proper model configuration management and intelligent model selection.

现在集成了优化组件：
- OllamaInstanceManager: 单一实例分时复用
- RoleDebateSession: 角色独立会话
- LayeredMemorySystem: 分层记忆系统
"""  # noqa: E501

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # 仅类型注解，避免模块级连带加载 litellm（CLI 冷启动优化 2026-08-10）
    from daip_live.model_provider.provider import LiteLLMProvider

from daip_live.core.exceptions import ModelError
from daip_live.core.models import (
    AgentEvent,
    AgentState,
    DebateCompleteEvent,
    DebateRoundStartEvent,
    DebateStartEvent,
    DebateTurnCompleteEvent,
    DebateTurnStartEvent,
    DialogueTurn,
    ProviderConfig,
    Role,
    Session,
    ThoughtEvent,
    TokenUsageEvent,
)
from daip_live.memory.session_manager import SessionManager
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.p4_role_manager_tools.role_model_manager import (
    RoleModelManager,
    RoleModelMapping,
)
from daip_live.p8_debate_system.history_tracker import DebateHistoryTracker
from daip_live.p8_debate_system.layered_memory_system import LayeredMemorySystem
from daip_live.p8_debate_system.model_availability_checker import (
    perform_model_check,
)

# 导入新的优化组件
from daip_live.p8_debate_system.ollama_instance_manager import OllamaInstanceManager
from daip_live.p8_debate_system.role_debate_session import RoleDebateSession


class EnhancedDebateManager:
    """Enhanced debate manager with optimized architecture."""

    def __init__(
        self,
        session_manager: SessionManager,
        role_manager: RoleManager,
        role_model_manager: RoleModelManager,
        model_provider: LiteLLMProvider,
        debate_history_tracker: DebateHistoryTracker | None = None,
        use_optimized_architecture: bool = True,  # 控制是否使用优化架构
    ):
        self.session_manager = session_manager
        self.role_manager = role_manager
        self.role_model_manager = role_model_manager
        self.model_provider = model_provider
        self.debate_history_tracker = debate_history_tracker  # Optional history tracker

        # 优化架构组件
        self.use_optimized_architecture = use_optimized_architecture
        # Initialize model cache for both architectures
        self.model_cache: dict[str, LiteLLMProvider] = {}
        if use_optimized_architecture:
            self.ollama_manager = OllamaInstanceManager(shared_provider=model_provider)
            self.role_sessions: dict[str, RoleDebateSession] = {}
            self.memory_system = LayeredMemorySystem()
        else:
            # 保持原有架构的兼容性
            pass

    async def run_debate(
        self, topic: str, roles_names: list[str], num_rounds: int
    ) -> AsyncGenerator[AgentEvent, None]:
        """Runs a full debate with optimized architecture support."""
        if self.use_optimized_architecture:
            async for event in self._run_debate_optimized(
                topic, roles_names, num_rounds
            ):
                yield event
        else:
            async for event in self._run_debate_legacy(topic, roles_names, num_rounds):
                yield event

    async def _run_debate_optimized(
        self, topic: str, roles_names: list[str], num_rounds: int
    ) -> AsyncGenerator[AgentEvent, None]:
        """运行优化架构的辩论"""
        import logging

        log = logging.getLogger(__name__)
        log.info("Entering _run_debate_optimized")

        # 立即产生开始事件
        yield DebateStartEvent(
            topic=topic,
            roles=roles_names,
            rounds=num_rounds,
            session_id=f"debate_{int(asyncio.get_event_loop().time())}",
        )

        # 执行真实模型可用性检查（Phase 1 Wave 0：移除调试绕过）
        is_model_ok, check_message = await perform_model_check()
        if not is_model_ok:
            log.error(f"Model check failed: {check_message}")
            raise ModelError(f"模型可用性检查未通过: {check_message}")
        log.info(f"Model check passed: {check_message}")

        # 获取角色模型映射
        log.info("Getting role model mappings...")
        role_mappings = self.role_model_manager.get_debate_model_mappings(roles_names)
        log.info(f"Got role mappings: {role_mappings}")

        # 验证角色映射存在性：缺失/不完整必须报错，绝不静默创建默认映射
        if not role_mappings or len(role_mappings) != len(roles_names):
            error_msg = (
                f"Role mappings are invalid or incomplete. Expected {len(roles_names)}, "  # noqa: E501
                f"got {len(role_mappings) if role_mappings else 0}."
            )
            log.error(error_msg)
            raise ValueError(error_msg)

        # 校验并收集映射：任何 None/无效映射都必须报错，绝不静默创建默认映射
        valid_mappings = []
        for i, mapping in enumerate(role_mappings or []):
            role_name = roles_names[i] if i < len(roles_names) else f"role_{i}"
            if mapping is None:
                log.error(f"Missing role mapping for role: {role_name}")
                raise ValueError(f"Missing role mapping for role: {role_name}")
            if not hasattr(mapping, "role_name") or not hasattr(
                mapping, "role_model_config"
            ):
                log.error(
                    f"Invalid mapping structure for role at index {i}: {role_name}"
                )
                raise ValueError(
                    f"Invalid role mapping structure for role: {role_name}"
                )
            valid_mappings.append(mapping)

        if len(valid_mappings) != len(roles_names):
            log.error(
                f"Failed to create proper role mappings. Expected {len(roles_names)}, created {len(valid_mappings)}."  # noqa: E501
            )
            raise ValueError(
                "Could not create proper role mappings for all requested roles."
            )

        # 创建角色映射字典
        role_model_map = {mapping.role_name: mapping for mapping in valid_mappings}
        log.info(f"Created role_model_map: {role_model_map}")

        # 初始化角色会话和记忆系统
        await self._initialize_optimized_debate(topic, roles_names, role_model_map)
        log.info("Initialized optimized debate")

        # 创建传统会话以保持兼容性
        session = self.session_manager.create_session(
            goal=topic, session_type="debate", participant_ids=roles_names
        )
        log.info(f"Created session: {session.session_id}")

        # If we have a history tracker, start tracking this debate
        if self.debate_history_tracker:
            start_event = DebateStartEvent(
                topic=topic,
                roles=roles_names,
                rounds=num_rounds,
                session_id=session.session_id,  # Using the traditional session for compatibility  # noqa: E501
            )
            await self.debate_history_tracker.start_tracking(start_event)

        # 发送辩论开始事件
        try:
            model_info = [
                f"{name}→{mapping.role_model_config.model_name}"
                for name, mapping in role_model_map.items()
            ]
        except Exception as e:
            log.error(
                f"Error creating model info: {e}. Role model map: {role_model_map}"
            )
            raise ValueError(
                f"Error creating model info: {e}. Role model map: {role_model_map}"
            )
        yield DebateStartEvent(
            topic=topic,
            roles=roles_names,
            rounds=num_rounds,
            session_id=session.session_id,
        )
        yield ThoughtEvent(
            content="使用优化架构: 单一Ollama实例, 角色独立会话, 分层记忆"
        )
        yield ThoughtEvent(content=f"Role-Model mappings: {', '.join(model_info)}")
        log.info("Yielded DebateStartEvent")

        # 运行辩论轮次
        for round_num in range(1, num_rounds + 1):
            log.info(f"Starting round {round_num}")
            async for event in self._run_optimized_round(
                topic, round_num, num_rounds, roles_names, role_model_map, session
            ):
                yield event
            log.info(f"Finished round {round_num}")

        # 生成辩论总结
        log.info("Generating debate summary")
        async for event in self._generate_optimized_summary(
            topic, session, role_model_map
        ):
            yield event
        log.info("Finished generating summary")

        # Complete debate in the history tracker if available
        if self.debate_history_tracker:
            complete_event = DebateCompleteEvent(
                session_id=session.session_id, summary=session.summary
            )
            await self.debate_history_tracker.complete_debate(complete_event)

        # Complete debate in the traditional session system for compatibility
        session.status = AgentState.COMPLETED
        self.session_manager.save_session(session)

        # Yield the completion event
        yield DebateCompleteEvent(
            session_id=session.session_id, summary=session.summary
        )
        log.info("Yielded DebateCompleteEvent")

    async def _run_debate_legacy(
        self, topic: str, roles_names: list[str], num_rounds: int
    ) -> AsyncGenerator[AgentEvent, None]:
        """运行传统架构的辩论（保持兼容性）"""
        session = self.session_manager.create_session(
            goal=topic, session_type="debate", participant_ids=roles_names
        )

        # 获取角色模型映射
        role_mappings = self.role_model_manager.get_debate_model_mappings(roles_names)

        # 验证角色映射
        if not role_mappings or len(role_mappings) != len(roles_names):
            raise ValueError(
                "One or more specified roles could not be loaded with model configurations."  # noqa: E501
            )

        # 过滤掉None值并验证类型
        valid_mappings = []
        missing_roles = []

        for mapping in role_mappings:
            if mapping is None:
                missing_roles.append("unknown")
            elif not hasattr(mapping, "role_name") or not hasattr(
                mapping, "role_model_config"
            ):
                missing_roles.append(getattr(mapping, "role_name", "invalid"))
            else:
                valid_mappings.append(mapping)

        if not valid_mappings:
            raise ValueError(
                f"No valid role mappings found. Missing or invalid: {missing_roles}"
            )

        # 创建角色映射字典
        role_model_map = {mapping.role_name: mapping for mapping in valid_mappings}

        # 发送辩论开始事件
        try:
            model_info = [
                f"{name}→{mapping.role_model_config.model_name}"
                for name, mapping in role_model_map.items()
            ]
        except Exception as e:
            raise ValueError(
                f"Error creating model info: {e}. Role model map: {role_model_map}"
            )

        start_event = DebateStartEvent(
            topic=topic,
            roles=roles_names,
            rounds=num_rounds,
            session_id=session.session_id,
        )
        yield start_event

        # If we have a history tracker, start tracking this debate
        if self.debate_history_tracker:
            await self.debate_history_tracker.start_tracking(start_event)

        yield ThoughtEvent(content="使用传统架构: 多模型实例, 共享会话")
        yield ThoughtEvent(content=f"Role-Model mappings: {', '.join(model_info)}")

        # 运行辩论轮次
        for round_num in range(1, num_rounds + 1):
            yield DebateRoundStartEvent(
                round_number=round_num,
                total_rounds=num_rounds,
                session_id=session.session_id,
            )

            for role_name in roles_names:
                role = self.role_manager.get_role_by_name(role_name)
                role_mapping = role_model_map[role_name]

                # 强制切换模型
                model_name = role_mapping.role_model_config.model_name
                yield ThoughtEvent(content=f"🔄 模型切换至: {role_name} → {model_name}")

                # 确保Ollama实例管理器切换到正确的模型（即使在传统架构中）
                if hasattr(self, "ollama_manager"):
                    await self.ollama_manager._switch_model(model_name)

                turn_start_event = DebateTurnStartEvent(
                    participant=role_name,
                    round_number=round_num,
                    session_id=session.session_id,
                )
                yield turn_start_event

                # If we have a history tracker, track turn start
                if self.debate_history_tracker:
                    # Note: DebateHistoryTracker may not have specific handling for turn start events,  # noqa: E501
                    # but we can still track them for completeness
                    pass  # Skip tracking turn start as it's more for UI feedback than actual history  # noqa: E501

                yield ThoughtEvent(
                    content=f"{role_name} is preparing response using {role_mapping.role_model_config.model_name}..."  # noqa: E501
                )

                # 使用传统方法生成回复
                response_content, token_info = await self._generate_response_with_model(
                    topic=topic,
                    role=role,
                    role_mapping=role_mapping,
                    history=session.history,
                )

                turn = DialogueTurn(participant_id=role_name, content=response_content)
                session.history.append(turn)

                if token_info:
                    yield TokenUsageEvent(
                        usage_info={
                            "prompt_tokens": token_info.get("prompt_tokens", 0),
                            "completion_tokens": token_info.get("completion_tokens", 0),
                            "total_tokens": token_info.get("total_tokens", 0),
                        },
                        session_id=session.session_id,
                    )

                # Send turn complete event
                turn_event = DebateTurnCompleteEvent(
                    participant=role_name,
                    round_number=round_num,
                    content_preview=response_content,
                    session_id=session.session_id,
                )
                yield turn_event

                # If we have a history tracker, add this turn to the debate history
                if self.debate_history_tracker:
                    await self.debate_history_tracker.add_turn(turn_event)

        # 生成总结
        yield ThoughtEvent(content="Generating debate summary...")
        summary_content, token_info = await self._generate_summary_with_model(
            session.history, role_model_map
        )
        session.summary = summary_content

        if token_info:
            yield TokenUsageEvent(
                usage_info={
                    "prompt_tokens": token_info.get("prompt_tokens", 0),
                    "completion_tokens": token_info.get("completion_tokens", 0),
                    "total_tokens": token_info.get("total_tokens", 0),
                },
                session_id=session.session_id,
            )

        # Complete debate in the history tracker if available
        if self.debate_history_tracker:
            complete_event = DebateCompleteEvent(
                session_id=session.session_id, summary=summary_content
            )
            await self.debate_history_tracker.complete_debate(complete_event)

        session.status = AgentState.COMPLETED
        self.session_manager.save_session(session)

        yield DebateCompleteEvent(
            session_id=session.session_id, summary=summary_content
        )

    async def _initialize_optimized_debate(
        self,
        topic: str,
        roles_names: list[str],
        role_model_map: dict[str, RoleModelMapping],
    ):
        """初始化优化架构的辩论"""
        # 为每个角色创建独立会话
        for role_name, role_mapping in role_model_map.items():
            role = self.role_manager.get_role_by_name(role_name)

            # 检查Role对象是否存在，如果不存在则创建默认角色
            if role is None:
                # Create a default role when it doesn't exist in role manager
                from daip_live.p4_role_manager_tools.role_model_config import (
                    EnhancedRole as Role,
                )

                role = Role(
                    name=role_name,
                    persona=f"You are {role_name}, a participant in a debate about '{topic}'. Provide thoughtful, well-reasoned responses based on your role perspective.",  # noqa: E501
                    tools=[],  # Default empty tools list
                    model_configs=[],  # Empty model configs list for default role
                )

            # 检查Role对象是否有system_prompt属性，如果没有则使用空字符串
            system_prompt = getattr(role, "system_prompt", "")

            self.role_sessions[role_name] = RoleDebateSession(
                role_name=role_name,
                role_persona=getattr(
                    role,
                    "persona",
                    f"You are a participant in a debate about '{topic}'. Provide thoughtful, well-reasoned responses.",  # noqa: E501
                ),
                model_config=role_mapping.role_model_config,
                system_prompt=system_prompt,
            )

        # 添加初始共享事实到记忆系统
        self.memory_system.add_shared_fact(
            round_num=0, fact=f"Debate topic: {topic}", source="system", confidence=1.0
        )

    async def _run_optimized_round(
        self,
        topic: str,
        round_num: int,
        total_rounds: int,
        roles_names: list[str],
        role_model_map: dict[str, RoleModelMapping],
        session: Session,
    ) -> AsyncGenerator[AgentEvent, None]:
        """运行优化架构的单轮辩论"""
        yield DebateRoundStartEvent(
            round_number=round_num,
            total_rounds=total_rounds,
            session_id=session.session_id,
        )

        # 收集所有角色的论点用于跨角色记忆
        round_arguments = {}

        for role_name in roles_names:
            role_mapping = role_model_map[role_name]
            role_session = self.role_sessions[role_name]

            # 强制切换模型
            model_name = role_mapping.role_model_config.model_name
            yield ThoughtEvent(content=f"🔄 模型切换至: {role_name} → {model_name}")

            # 确保Ollama实例管理器切换到正确的模型
            await self.ollama_manager._switch_model(model_name)

            yield DebateTurnStartEvent(
                participant=role_name,
                round_number=round_num,
                session_id=session.session_id,
            )

            # 使用优化架构生成回复
            response_content, token_info = await self._generate_optimized_response(
                topic=topic,
                role_name=role_name,
                round_num=round_num,
                role_session=role_session,
                role_model_map=role_model_map,
            )

            # 保存到传统会话以保持兼容性
            turn = DialogueTurn(participant_id=role_name, content=response_content)
            session.history.append(turn)

            # 更新角色会话和记忆系统
            opponent_summary = self._create_opponent_summary(round_arguments)
            role_session.add_personal_history(
                round_num, response_content, opponent_summary
            )
            role_session.track_argument(round_num, "main", response_content, 0.8)

            # 更新分层记忆系统
            self.memory_system.update_role_memory(
                role_name, response_content, round_num, "argument"
            )

            round_arguments[role_name] = response_content

            # 发送事件
            if token_info:
                yield TokenUsageEvent(
                    usage_info={
                        "prompt_tokens": token_info.get("prompt_tokens", 0),
                        "completion_tokens": token_info.get("completion_tokens", 0),
                        "total_tokens": token_info.get("total_tokens", 0),
                    },
                    session_id=session.session_id,
                )

            # Send the turn complete event
            turn_event = DebateTurnCompleteEvent(
                participant=role_name,
                round_number=round_num,
                content_preview=response_content,
                session_id=session.session_id,
            )
            yield turn_event

            # If we have a history tracker, add this turn to the debate history
            if self.debate_history_tracker:
                await self.debate_history_tracker.add_turn(turn_event)

        # 添加轮次摘要到记忆系统
        if round_arguments:
            summary = f"Round {round_num} discussion on {topic}"
            key_points = list(round_arguments.values())
            consensus_level = 0.5  # 简化的共识计算

            self.memory_system.add_round_summary(
                round_num, summary, key_points, consensus_level
            )

    async def _generate_optimized_response(
        self,
        topic: str,
        role_name: str,
        round_num: int,
        role_session: RoleDebateSession,
        role_model_map: dict[str, RoleModelMapping],
    ) -> tuple[str, dict | None]:
        """使用优化架构生成回复"""
        # 构建上下文感知的提示词
        prompt = role_session.build_context_aware_prompt(topic, round_num)

        # 添加分层记忆系统提供的上下文
        memory_context = self.memory_system.get_compressed_context(role_name, round_num)
        if memory_context:
            prompt += f"\n\nRelevant Memory Context:\n{memory_context}"

        # 使用单一Ollama实例生成回复
        role_mapping = role_model_map[role_name]
        response_content, usage = await self.ollama_manager.generate_with_model(
            model_name=role_mapping.role_model_config.model_name,
            prompt=prompt,
            temperature=role_mapping.role_model_config.temperature,
            max_tokens=role_mapping.role_model_config.max_tokens,
            top_p=role_mapping.role_model_config.top_p,
            frequency_penalty=role_mapping.role_model_config.frequency_penalty,
            presence_penalty=role_mapping.role_model_config.presence_penalty,
        )
        # ModelError now propagates to UI layer for user-visible error handling

        # 转换usage格式以保持兼容性
        token_info = None
        if usage:
            token_info = {
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
            }

        return response_content, token_info

    async def _generate_optimized_summary(
        self, topic: str, session: Session, role_model_map: dict[str, RoleModelMapping]
    ) -> AsyncGenerator[AgentEvent, None]:
        """生成优化架构的辩论总结"""
        yield ThoughtEvent(content="使用优化架构生成辩论总结...")

        # 使用分层记忆系统获取进程摘要
        progression = self.memory_system.get_debate_progression_summary()

        # 选择最高优先级的模型用于总结
        best_mapping = max(role_model_map.values(), key=lambda m: m.priority)

        # 构建增强的总结提示词
        history_str = self._format_history(session.history)
        memory_summary = f"辩论进程: {progression['consensus_trend']}, 平均共识度: {progression['average_consensus']:.2f}"  # noqa: E501

        summary_prompt = f"""请为以下辩论提供中立的总结，识别关键论点、争议点和任何潜在的共识。

辩论主题: {topic}
{memory_summary}

辩论历史:
{history_str}

总结:"""  # noqa: E501

        # 使用单一Ollama实例生成总结
        summary_content, usage = await self.ollama_manager.generate_with_model(
            model_name=best_mapping.role_model_config.model_name,
            prompt=summary_prompt,
            temperature=0.3,  # 降低温度以获得更一致的总结
            max_tokens=best_mapping.role_model_config.max_tokens,
            top_p=best_mapping.role_model_config.top_p,
        )
        # ModelError now propagates to UI layer for user-visible error handling

        session.summary = summary_content

        # 发送token使用事件
        if usage:
            yield TokenUsageEvent(
                usage_info={
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                },
                session_id=session.session_id,
            )

        # 最后需要返回生成的摘要内容
        # 注意：_generate_optimized_summary 是一个 async generator，不会返回值，
        # 而是通过 yield 生成事件，所以不需要 return 语句

    def _create_opponent_summary(self, round_arguments: dict[str, str]) -> str:
        """创建对手论点摘要"""
        if not round_arguments:
            return "No arguments yet"

        summaries = []
        for role, argument in round_arguments.items():
            summaries.append(f"{role}: {argument[:100]}...")

        return "; ".join(summaries)

    # 以下是保持兼容性的原有方法
    async def _generate_response_with_model(
        self,
        topic: str,
        role: Role,
        role_mapping: RoleModelMapping,
        history: list[DialogueTurn],
    ) -> tuple[str, dict | None]:
        """Generate response using role-specific model configuration (legacy method)."""
        history_str = self._format_history(history)

        prompt = f"""Debate Topic: {topic}

Your Role: {role.persona}

Your Model Configuration: {role_mapping.model_config.model_name} (temperature: {role_mapping.model_config.temperature})

Conversation History:
{history_str}

Based on the history, your role persona, and your assigned model configuration, what is your next argument?"""  # noqa: E501

        # Get or create model provider for this configuration
        model_provider = self._get_model_provider_for_config(role_mapping.model_config)

        # Generate response with model-specific settings
        # 源码契约: LiteLLMProvider.generate(prompt, params) 是 async generator（provider.py:276），  # noqa: E501
        # 不支持 model=/temperature= 等 kwargs，参数放入 params dict
        params = {
            "temperature": role_mapping.model_config.temperature,
            "max_tokens": role_mapping.model_config.max_tokens,
            "top_p": role_mapping.model_config.top_p,
            "frequency_penalty": role_mapping.model_config.frequency_penalty,
            "presence_penalty": role_mapping.model_config.presence_penalty,
        }
        response_content = None
        async for chunk in model_provider.generate(prompt, params=params):
            response_content = chunk
            break

        return response_content, None

    async def _generate_summary_with_model(
        self, history: list[DialogueTurn], role_model_map: dict[str, RoleModelMapping]
    ) -> tuple[str, dict | None]:
        """Generate summary using the highest-priority model available (legacy method)."""  # noqa: E501

        # Find the highest priority model for summary generation
        best_mapping = max(role_model_map.values(), key=lambda m: m.priority)

        history_str = self._format_history(history)
        summary_prompt = f"""Please provide a neutral summary of the following debate, identifying key arguments, points of contention, and any potential consensus.

Debate Topic: (Extract from conversation)
Debate History:
{history_str}

Summary:"""  # noqa: E501

        # Get or create model provider for this configuration
        model_provider = self._get_model_provider_for_config(best_mapping.model_config)

        # Generate summary with slightly different settings for better summarization
        # 源码契约: LiteLLMProvider.generate(prompt, params) 是 async generator（provider.py:276）  # noqa: E501
        params = {
            "temperature": 0.3,  # Lower temperature for more consistent summaries
            "max_tokens": best_mapping.model_config.max_tokens,
            "top_p": best_mapping.model_config.top_p,
        }
        summary_content = None
        async for chunk in model_provider.generate(summary_prompt, params=params):
            summary_content = chunk
            break

        return summary_content, None

    def _get_model_provider_for_config(self, model_config) -> LiteLLMProvider:
        """Get or create a model provider instance for the given configuration (legacy method)."""  # noqa: E501
        from daip_live.model_provider.provider import LiteLLMProvider

        cache_key = f"{model_config.provider}_{model_config.model_name}"

        if cache_key not in self.model_cache:
            # Create a new provider instance for this model
            # 源码契约: LiteLLMProvider.__init__(config: ProviderConfig)（provider.py:17），  # noqa: E501
            # 不能传 dict
            provider_config = ProviderConfig(
                model=model_config.model_name,
                api_key=None,
                base_url=None,
                temperature=model_config.temperature,
                max_tokens=model_config.max_tokens,
            )

            # Create a temporary LiteLLMProvider for this specific model
            self.model_cache[cache_key] = LiteLLMProvider(provider_config)

        return self.model_cache[cache_key]

    def _format_history(self, history: list[DialogueTurn]) -> str:
        """Format debate history for prompt generation."""
        return "\n".join([f"{turn.participant_id}: {turn.content}" for turn in history])

    def get_debate_model_summary(self, roles_names: list[str]) -> dict[str, Any]:
        """Get a summary of model configurations for the debate."""
        role_mappings = self.role_model_manager.get_debate_model_mappings(roles_names)

        summary = {
            "topic_roles": roles_names,
            "model_assignments": {},
            "model_stats": {},
            "architecture": "optimized"
            if self.use_optimized_architecture
            else "legacy",
        }

        if self.use_optimized_architecture:
            # 添加优化架构的统计信息
            summary["optimization_stats"] = {
                "ollama_instances": 1,
                "role_sessions": len(self.role_sessions),
                "memory_entries": self.memory_system.get_memory_statistics(),
            }

        for i, mapping in enumerate(role_mappings):
            if mapping is None:
                # Handle case where role mapping is None (e.g., for non-existent roles)
                role_name = (
                    roles_names[i] if i < len(roles_names) else f"unknown_role_{i}"
                )
                # Create default assignment for None mapping
                from daip_live.p4_role_manager_tools.role_model_manager import (
                    RoleModelConfig,
                )

                default_model_config = RoleModelConfig(
                    model_name="ollama/llama3:instruct",
                    provider="ollama",
                    max_tokens=2048,
                    temperature=0.7,
                    top_p=0.9,
                    frequency_penalty=0.1,
                    presence_penalty=0.2,
                    is_primary=True,
                )

                summary["model_assignments"][role_name] = {
                    "model": default_model_config.model_name,
                    "provider": default_model_config.provider,
                    "temperature": default_model_config.temperature,
                    "max_tokens": default_model_config.max_tokens,
                }

                model_key = default_model_config.model_name
                if model_key not in summary["model_stats"]:
                    summary["model_stats"][model_key] = {
                        "provider": default_model_config.provider,
                        "usage_count": 0,
                        "roles": [],
                    }

                summary["model_stats"][model_key]["usage_count"] += 1
                summary["model_stats"][model_key]["roles"].append(role_name)
            else:
                # Normal mapping case - check if mapping has the required attributes
                if hasattr(mapping, "role_name") and hasattr(
                    mapping, "role_model_config"
                ):
                    summary["model_assignments"][mapping.role_name] = {
                        "model": mapping.role_model_config.model_name,
                        "provider": mapping.role_model_config.provider,
                        "temperature": mapping.role_model_config.temperature,
                        "max_tokens": mapping.role_model_config.max_tokens,
                    }

                    model_key = mapping.role_model_config.model_name
                    if model_key not in summary["model_stats"]:
                        summary["model_stats"][model_key] = {
                            "provider": mapping.role_model_config.provider,
                            "usage_count": 0,
                            "roles": [],
                        }

                    summary["model_stats"][model_key]["usage_count"] += 1
                    summary["model_stats"][model_key]["roles"].append(mapping.role_name)

        return summary

    def get_optimization_benefits(self) -> dict[str, Any]:
        """获取优化带来的好处"""
        if not self.use_optimized_architecture:
            return {"message": "优化架构未启用"}

        return {
            "resource_usage": {
                "ollama_instances": 1,
                "memory_efficiency": "角色独立会话减少上下文混淆",
                "model_switching": "分时复用避免资源竞争",
            },
            "memory_system": self.memory_system.get_memory_statistics(),
            "role_sessions": len(self.role_sessions),
        }

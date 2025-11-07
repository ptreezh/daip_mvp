"""
Enhanced Debate Manager with Model-Per-Role Support

This manager extends the base debate system to support different models for different roles,
with proper model configuration management and intelligent model selection.

现在集成了优化组件：
- OllamaInstanceManager: 单一实例分时复用
- RoleDebateSession: 角色独立会话
- LayeredMemorySystem: 分层记忆系统
"""

from typing import AsyncGenerator, List, Optional, Dict, Any

from daip_live.core.models import (
    AgentEvent, AgentState, DebateCompleteEvent, DebateRoundStartEvent,
    DebateStartEvent, DebateTurnCompleteEvent, DebateTurnStartEvent,
    DialogueTurn, Role, Session, ThoughtEvent, TokenUsageEvent
)
from daip_live.memory.session_manager import SessionManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager, RoleModelMapping

# 导入新的优化组件
from daip_live.p8_debate_system.ollama_instance_manager import OllamaInstanceManager
from daip_live.p8_debate_system.role_debate_session import RoleDebateSession
from daip_live.p8_debate_system.layered_memory_system import LayeredMemorySystem


class EnhancedDebateManager:
    """Enhanced debate manager with optimized architecture."""

    def __init__(
        self,
        session_manager: SessionManager,
        role_manager: RoleManager,
        role_model_manager: RoleModelManager,
        model_provider: LiteLLMProvider,
        use_optimized_architecture: bool = True  # 控制是否使用优化架构
    ):
        self.session_manager = session_manager
        self.role_manager = role_manager
        self.role_model_manager = role_model_manager
        self.model_provider = model_provider

        # 优化架构组件
        self.use_optimized_architecture = use_optimized_architecture
        # Initialize model cache for both architectures
        self.model_cache: Dict[str, LiteLLMProvider] = {}
        if use_optimized_architecture:
            self.ollama_manager = OllamaInstanceManager()
            self.role_sessions: Dict[str, RoleDebateSession] = {}
            self.memory_system = LayeredMemorySystem()
        else:
            # 保持原有架构的兼容性
            pass

    async def run_debate(
        self,
        topic: str,
        roles_names: List[str],
        num_rounds: int
    ) -> AsyncGenerator[AgentEvent, None]:
        """Runs a full debate with optimized architecture support."""
        if self.use_optimized_architecture:
            async for event in self._run_debate_optimized(topic, roles_names, num_rounds):
                yield event
        else:
            async for event in self._run_debate_legacy(topic, roles_names, num_rounds):
                yield event

    async def _run_debate_optimized(
        self,
        topic: str,
        roles_names: List[str],
        num_rounds: int
    ) -> AsyncGenerator[AgentEvent, None]:
        """运行优化架构的辩论"""
        import logging
        log = logging.getLogger(__name__)
        log.info("Entering _run_debate_optimized")
        # 获取角色模型映射
        role_mappings = self.role_model_manager.get_debate_model_mappings(roles_names)
        log.info(f"Got role mappings: {role_mappings}")

        # 验证角色映射
        if not role_mappings or len(role_mappings) != len(roles_names):
            log.error("Role mappings are invalid or incomplete.")
            raise ValueError("One or more specified roles could not be loaded with model configurations.")

        # 过滤掉None值并验证类型
        valid_mappings = []
        missing_roles = []

        for mapping in role_mappings:
            if mapping is None:
                missing_roles.append("unknown")
            elif not hasattr(mapping, 'role_name') or not hasattr(mapping, 'role_model_config'):
                missing_roles.append(getattr(mapping, 'role_name', 'invalid'))
            else:
                valid_mappings.append(mapping)

        if not valid_mappings:
            log.error(f"No valid role mappings found. Missing or invalid: {missing_roles}")
            raise ValueError(f"No valid role mappings found. Missing or invalid: {missing_roles}")

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

        # 发送辩论开始事件
        try:
            model_info = [f"{name}→{mapping.role_model_config.model_name}" for name, mapping in role_model_map.items()]
        except Exception as e:
            log.error(f"Error creating model info: {e}. Role model map: {role_model_map}")
            raise ValueError(f"Error creating model info: {e}. Role model map: {role_model_map}")
        yield DebateStartEvent(
            topic=topic,
            roles=roles_names,
            rounds=num_rounds,
            session_id=session.session_id
        )
        yield ThoughtEvent(content=f"使用优化架构: 单一Ollama实例, 角色独立会话, 分层记忆")
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
        async for event in self._generate_optimized_summary(topic, session, role_model_map):
            yield event
        log.info("Finished generating summary")

        # 完成辩论
        session.status = AgentState.COMPLETED
        self.session_manager.save_session(session)

        yield DebateCompleteEvent(
            session_id=session.session_id,
            summary=session.summary
        )
        log.info("Yielded DebateCompleteEvent")

    async def _run_debate_legacy(
        self,
        topic: str,
        roles_names: List[str],
        num_rounds: int
    ) -> AsyncGenerator[AgentEvent, None]:
        """运行传统架构的辩论（保持兼容性）"""
        session = self.session_manager.create_session(
            goal=topic, session_type="debate", participant_ids=roles_names
        )

        # 获取角色模型映射
        role_mappings = self.role_model_manager.get_debate_model_mappings(roles_names)

        # 验证角色映射
        if not role_mappings or len(role_mappings) != len(roles_names):
            raise ValueError("One or more specified roles could not be loaded with model configurations.")

        # 过滤掉None值并验证类型
        valid_mappings = []
        missing_roles = []

        for mapping in role_mappings:
            if mapping is None:
                missing_roles.append("unknown")
            elif not hasattr(mapping, 'role_name') or not hasattr(mapping, 'role_model_config'):
                missing_roles.append(getattr(mapping, 'role_name', 'invalid'))
            else:
                valid_mappings.append(mapping)

        if not valid_mappings:
            raise ValueError(f"No valid role mappings found. Missing or invalid: {missing_roles}")

        # 创建角色映射字典
        role_model_map = {mapping.role_name: mapping for mapping in valid_mappings}

        # 发送辩论开始事件
        try:
            model_info = [f"{name}→{mapping.role_model_config.model_name}" for name, mapping in role_model_map.items()]
        except Exception as e:
            raise ValueError(f"Error creating model info: {e}. Role model map: {role_model_map}")
        yield DebateStartEvent(
            topic=topic,
            roles=roles_names,
            rounds=num_rounds,
            session_id=session.session_id
        )
        yield ThoughtEvent(content=f"使用传统架构: 多模型实例, 共享会话")
        yield ThoughtEvent(content=f"Role-Model mappings: {', '.join(model_info)}")

        # 运行辩论轮次
        for round_num in range(1, num_rounds + 1):
            yield DebateRoundStartEvent(
                round_number=round_num,
                total_rounds=num_rounds,
                session_id=session.session_id
            )

            for role_name in roles_names:
                role = self.role_manager.get_role_by_name(role_name)
                role_mapping = role_model_map[role_name]

                yield DebateTurnStartEvent(
                    participant=role_name,
                    round_number=round_num,
                    session_id=session.session_id
                )
                yield ThoughtEvent(
                    content=f"{role_name} is preparing response using {role_mapping.model_config.model_name}..."
                )

                # 使用传统方法生成回复
                response_content, token_info = await self._generate_response_with_model(
                    topic=topic,
                    role=role,
                    role_mapping=role_mapping,
                    history=session.history
                )

                turn = DialogueTurn(participant_id=role_name, content=response_content)
                session.history.append(turn)

                if token_info:
                    yield TokenUsageEvent(
                        usage_info={
                            "prompt_tokens": token_info.get("prompt_tokens", 0),
                            "completion_tokens": token_info.get("completion_tokens", 0),
                            "total_tokens": token_info.get("total_tokens", 0)
                        },
                        session_id=session.session_id
                    )

                yield DebateTurnCompleteEvent(
                    participant=role_name,
                    round_number=round_num,
                    content_preview=response_content,
                    session_id=session.session_id
                )

        # 生成总结
        yield ThoughtEvent(content="Generating debate summary...")
        summary_content, token_info = await self._generate_summary_with_model(session.history, role_model_map)
        session.summary = summary_content

        if token_info:
            yield TokenUsageEvent(
                usage_info={
                    "prompt_tokens": token_info.get("prompt_tokens", 0),
                    "completion_tokens": token_info.get("completion_tokens", 0),
                    "total_tokens": token_info.get("total_tokens", 0)
                },
                session_id=session.session_id
            )

        session.status = AgentState.COMPLETED
        self.session_manager.save_session(session)

        yield DebateCompleteEvent(
            session_id=session.session_id,
            summary=summary_content
        )

    async def _initialize_optimized_debate(self, topic: str, roles_names: List[str], role_model_map: Dict[str, RoleModelMapping]):
        """初始化优化架构的辩论"""
        # 为每个角色创建独立会话
        for role_name, role_mapping in role_model_map.items():
            role = self.role_manager.get_role_by_name(role_name)

            # 检查Role对象是否有system_prompt属性，如果没有则使用空字符串
            system_prompt = getattr(role, 'system_prompt', '')

            self.role_sessions[role_name] = RoleDebateSession(
                role_name=role_name,
                role_persona=role.persona,
                model_config=role_mapping.role_model_config,
                system_prompt=system_prompt
            )

        # 添加初始共享事实到记忆系统
        self.memory_system.add_shared_fact(
            round_num=0,
            fact=f"Debate topic: {topic}",
            source="system",
            confidence=1.0
        )

    async def _run_optimized_round(
        self,
        topic: str,
        round_num: int,
        total_rounds: int,
        roles_names: List[str],
        role_model_map: Dict[str, RoleModelMapping],
        session: Session
    ) -> AsyncGenerator[AgentEvent, None]:
        """运行优化架构的单轮辩论"""
        yield DebateRoundStartEvent(
            round_number=round_num,
            total_rounds=total_rounds,
            session_id=session.session_id
        )

        # 收集所有角色的论点用于跨角色记忆
        round_arguments = {}

        for role_name in roles_names:
            role_mapping = role_model_map[role_name]
            role_session = self.role_sessions[role_name]

            yield DebateTurnStartEvent(
                participant=role_name,
                round_number=round_num,
                session_id=session.session_id
            )
            yield ThoughtEvent(
                content=f"{role_name} (模型: {role_mapping.role_model_config.model_name}) 准备回复..."
            )

            # 使用优化架构生成回复
            response_content, token_info = await self._generate_optimized_response(
                topic=topic,
                role_name=role_name,
                round_num=round_num,
                role_session=role_session,
                role_model_map=role_model_map
            )

            # 保存到传统会话以保持兼容性
            turn = DialogueTurn(participant_id=role_name, content=response_content)
            session.history.append(turn)

            # 更新角色会话和记忆系统
            opponent_summary = self._create_opponent_summary(round_arguments)
            role_session.add_personal_history(round_num, response_content, opponent_summary)
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
                        "total_tokens": token_info.get("total_tokens", 0)
                    },
                    session_id=session.session_id
                )

            yield DebateTurnCompleteEvent(
                participant=role_name,
                round_number=round_num,
                content_preview=response_content,
                session_id=session.session_id
            )

        # 添加轮次摘要到记忆系统
        if round_arguments:
            summary = f"Round {round_num} discussion on {topic}"
            key_points = list(round_arguments.values())
            consensus_level = 0.5  # 简化的共识计算

            self.memory_system.add_round_summary(round_num, summary, key_points, consensus_level)

    async def _generate_optimized_response(
        self,
        topic: str,
        role_name: str,
        round_num: int,
        role_session: RoleDebateSession,
        role_model_map: Dict[str, RoleModelMapping]
    ) -> tuple[str, Optional[dict]]:
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
            presence_penalty=role_mapping.role_model_config.presence_penalty
        )

        # 转换usage格式以保持兼容性
        token_info = None
        if usage:
            token_info = {
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0)
            }

        return response_content, token_info

    async def _generate_optimized_summary(
        self,
        topic: str,
        session: Session,
        role_model_map: Dict[str, RoleModelMapping]
    ) -> AsyncGenerator[AgentEvent, None]:
        """生成优化架构的辩论总结"""
        yield ThoughtEvent(content="使用优化架构生成辩论总结...")

        # 使用分层记忆系统获取进程摘要
        progression = self.memory_system.get_debate_progression_summary()

        # 选择最高优先级的模型用于总结
        best_mapping = max(role_model_map.values(), key=lambda m: m.priority)

        # 构建增强的总结提示词
        history_str = self._format_history(session.history)
        memory_summary = f"辩论进程: {progression['consensus_trend']}, 平均共识度: {progression['average_consensus']:.2f}"

        summary_prompt = f"""请为以下辩论提供中立的总结，识别关键论点、争议点和任何潜在的共识。

辩论主题: {topic}
{memory_summary}

辩论历史:
{history_str}

总结:"""

        # 使用单一Ollama实例生成总结
        summary_content, usage = await self.ollama_manager.generate_with_model(
            model_name=best_mapping.role_model_config.model_name,
            prompt=summary_prompt,
            temperature=0.3,  # 降低温度以获得更一致的总结
            max_tokens=best_mapping.role_model_config.max_tokens,
            top_p=best_mapping.role_model_config.top_p
        )

        session.summary = summary_content

        # 发送token使用事件
        if usage:
            yield TokenUsageEvent(
                usage_info={
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0)
                },
                session_id=session.session_id
            )

    def _create_opponent_summary(self, round_arguments: Dict[str, str]) -> str:
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
        history: List[DialogueTurn]
    ) -> tuple[str, Optional[dict]]:
        """Generate response using role-specific model configuration (legacy method)."""
        history_str = self._format_history(history)

        prompt = f"""Debate Topic: {topic}

Your Role: {role.persona}

Your Model Configuration: {role_mapping.model_config.model_name} (temperature: {role_mapping.model_config.temperature})

Conversation History:
{history_str}

Based on the history, your role persona, and your assigned model configuration, what is your next argument?"""

        # Get or create model provider for this configuration
        model_provider = self._get_model_provider_for_config(role_mapping.model_config)

        # Generate response with model-specific settings
        response_content, token_info = await model_provider.generate(
            prompt,
            model=role_mapping.model_config.model_name,
            temperature=role_mapping.model_config.temperature,
            max_tokens=role_mapping.model_config.max_tokens,
            top_p=role_mapping.model_config.top_p,
            frequency_penalty=role_mapping.model_config.frequency_penalty,
            presence_penalty=role_mapping.model_config.presence_penalty
        )

        return response_content, token_info

    async def _generate_summary_with_model(
        self,
        history: List[DialogueTurn],
        role_model_map: Dict[str, RoleModelMapping]
    ) -> tuple[str, Optional[dict]]:
        """Generate summary using the highest-priority model available (legacy method)."""

        # Find the highest priority model for summary generation
        best_mapping = max(role_model_map.values(), key=lambda m: m.priority)

        history_str = self._format_history(history)
        summary_prompt = f"""Please provide a neutral summary of the following debate, identifying key arguments, points of contention, and any potential consensus.

Debate Topic: (Extract from conversation)
Debate History:
{history_str}

Summary:"""

        # Get or create model provider for this configuration
        model_provider = self._get_model_provider_for_config(best_mapping.model_config)

        # Generate summary with slightly different settings for better summarization
        response_content, token_info = await model_provider.generate(
            summary_prompt,
            model=best_mapping.model_config.model_name,
            temperature=0.3,  # Lower temperature for more consistent summaries
            max_tokens=best_mapping.model_config.max_tokens,
            top_p=best_mapping.model_config.top_p
        )

        return response_content, token_info

    def _get_model_provider_for_config(self, model_config) -> LiteLLMProvider:
        """Get or create a model provider instance for the given configuration (legacy method)."""
        cache_key = f"{model_config.provider}_{model_config.model_name}"

        if cache_key not in self.model_cache:
            # Create a new provider instance for this model
            provider_config = {
                "model": model_config.model_name,
                "api_base": None,  # Use default
                "api_key": None,   # Use default from config
                "max_tokens": model_config.max_tokens,
                "temperature": model_config.temperature,
            }

            # Create a temporary LiteLLMProvider for this specific model
            self.model_cache[cache_key] = LiteLLMProvider(
                config={"provider_configs": {model_config.provider: provider_config}}
            )

        return self.model_cache[cache_key]

    def _format_history(self, history: List[DialogueTurn]) -> str:
        """Format debate history for prompt generation."""
        return "\n".join([f"{turn.participant_id}: {turn.content}" for turn in history])

    def get_debate_model_summary(self, roles_names: List[str]) -> Dict[str, Any]:
        """Get a summary of model configurations for the debate."""
        role_mappings = self.role_model_manager.get_debate_model_mappings(roles_names)

        summary = {
            "topic_roles": roles_names,
            "model_assignments": {},
            "model_stats": {},
            "architecture": "optimized" if self.use_optimized_architecture else "legacy"
        }

        if self.use_optimized_architecture:
            # 添加优化架构的统计信息
            summary["optimization_stats"] = {
                "ollama_instances": 1,
                "role_sessions": len(self.role_sessions),
                "memory_entries": self.memory_system.get_memory_statistics()
            }

        for mapping in role_mappings:
            summary["model_assignments"][mapping.role_name] = {
                "model": mapping.role_model_config.model_name,
                "provider": mapping.role_model_config.provider,
                "temperature": mapping.role_model_config.temperature,
                "max_tokens": mapping.role_model_config.max_tokens
            }

            model_key = mapping.role_model_config.model_name
            if model_key not in summary["model_stats"]:
                summary["model_stats"][model_key] = {
                    "provider": mapping.role_model_config.provider,
                    "usage_count": 0,
                    "roles": []
                }

            summary["model_stats"][model_key]["usage_count"] += 1
            summary["model_stats"][model_key]["roles"].append(mapping.role_name)

        return summary

    def get_optimization_benefits(self) -> Dict[str, Any]:
        """获取优化带来的好处"""
        if not self.use_optimized_architecture:
            return {"message": "优化架构未启用"}

        return {
            "resource_usage": {
                "ollama_instances": 1,
                "memory_efficiency": "角色独立会话减少上下文混淆",
                "model_switching": "分时复用避免资源竞争"
            },
            "memory_system": self.memory_system.get_memory_statistics(),
            "role_sessions": len(self.role_sessions)
        }
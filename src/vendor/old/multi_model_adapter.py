"""多模型适配器
支持不同LLM提供商的统一记忆注入接口
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

from src.constants import *
from src.role_memory_bank import RoleIdentity, RoleMemoryBank


@dataclass
class ModelResponse:
    """模型响应"""

    content: str
    role_id: str
    model_type: str
    usage_info: Optional[dict[str, Any]] = None
    metadata: Optional[dict[str, Any]] = None


class BaseModelAdapter(ABC):
    """模型适配器基类"""

    def __init__(self, memory_bank: RoleMemoryBank):
        self.memory_bank = memory_bank
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    async def generate_response(
        self,
        role_id: str,
        user_message: str,
        project_id: Optional[str] = None,
        session_id: Optional[str] = None,
        **kwargs,
    ) -> ModelResponse:
        """生成角色响应"""

    def _prepare_context(
        self,
        role_id: str,
        user_message: str,
        project_id: Optional[str] = None,
        session_id: Optional[str] = None,
        conversation_history: Optional[list[dict[str, str]]] = None,
    ) -> dict[str, Any]:
        """准备上下文"""
        return self.memory_bank.build_context_for_conversation(
            role_id=role_id,
            current_question=user_message,
            project_id=project_id,
            session_id=session_id,
            conversation_history=conversation_history,
        )

    def _save_interaction(
        self,
        role_id: str,
        user_message: str,
        response: str,
        project_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        """保存交互记忆"""
        self.memory_bank.add_dialogue_memory(
            role_id=role_id,
            user_message=user_message,
            role_response=response,
            project_id=project_id,
            session_id=session_id,
        )


class OllamaAdapter(BaseModelAdapter):
    """Ollama模型适配器"""

    def __init__(
        self,
        memory_bank: RoleMemoryBank,
        base_url: str = "http://localhost:11434",
        model_name: str = "gemma3:latest",
    ):
        super().__init__(memory_bank)
        self.base_url = base_url
        self.model_name = model_name

    async def generate_response(
        self,
        role_id: str,
        user_message: str,
        project_id: Optional[str] = None,
        session_id: Optional[str] = None,
        conversation_history: Optional[list[dict[str, str]]] = None,
        **kwargs,
    ) -> ModelResponse:
        """生成响应"""
        try:
            # 准备上下文
            context = self._prepare_context(
                role_id,
                user_message,
                project_id,
                session_id,
                conversation_history,
            )

            # 构建提示词
            prompt = context.get("prompt", "")
            if not prompt:
                # 备用提示词
                identity = context.get("role_identity")
                if identity:
                    prompt = (
                        f"你是{identity['name']}，{identity['title']}。请回答：{user_message}"
                    )
                else:
                    prompt = user_message

            # 调用Ollama API
            import aiohttp

            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "num_predict": kwargs.get("max_tokens", 2048),
                },
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result.get("response", "").strip()

                        # 保存交互记忆
                        self._save_interaction(
                            role_id,
                            user_message,
                            content,
                            project_id,
                            session_id,
                        )

                        return ModelResponse(
                            content=content,
                            role_id=role_id,
                            model_type="ollama",
                            usage_info={"model": self.model_name},
                            metadata={
                                "context_used": len(
                                    context.get("relevant_memories", []),
                                ),
                            },
                        )
                    else:
                        error_text = await response.text()
                        raise Exception(
                            f"Ollama API error: {response.status} - {error_text}",
                        )

        except Exception as e:
            self.logger.error(f"Ollama generation failed: {e}")
            return ModelResponse(
                content=f"[系统消息] 角色响应生成失败: {e!s}",
                role_id=role_id,
                model_type="ollama",
            )


class OpenAIAdapter(BaseModelAdapter):
    """OpenAI模型适配器"""

    def __init__(
        self,
        memory_bank: RoleMemoryBank,
        api_key: str,
        model_name: str = "gpt-3.5-turbo",
    ):
        super().__init__(memory_bank)
        self.api_key = api_key
        self.model_name = model_name

    async def generate_response(
        self,
        role_id: str,
        user_message: str,
        project_id: Optional[str] = None,
        session_id: Optional[str] = None,
        conversation_history: Optional[list[dict[str, str]]] = None,
        **kwargs,
    ) -> ModelResponse:
        """生成响应"""
        try:
            import openai

            # 准备上下文
            context = self._prepare_context(
                role_id,
                user_message,
                project_id,
                session_id,
                conversation_history,
            )

            # 构建消息
            messages = []

            # 系统消息（角色身份）
            identity = context.get("role_identity")
            if identity:
                system_message = (
                    f"你是{identity['name']}，{identity['title']}。{identity['background']}"
                )

                # 添加相关记忆
                memories = context.get("relevant_memories", [])
                if memories:
                    memory_text = "\n".join(
                        [f"- {m['content'][:100]}" for m in memories[:3]],
                    )
                    system_message += f"\n\n相关记忆：\n{memory_text}"

                messages.append({"role": "system", "content": system_message})

            # 用户消息
            messages.append({"role": "user", "content": user_message})

            # 调用OpenAI API
            client = openai.AsyncOpenAI(api_key=self.api_key)

            response = await client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 2048),
            )

            content = response.choices[0].message.content.strip()

            # 保存交互记忆
            self._save_interaction(
                role_id,
                user_message,
                content,
                project_id,
                session_id,
            )

            return ModelResponse(
                content=content,
                role_id=role_id,
                model_type="openai",
                usage_info={
                    "model": self.model_name,
                    "tokens": response.usage.total_tokens if response.usage else 0,
                },
                metadata={"context_used": len(context.get("relevant_memories", []))},
            )

        except Exception as e:
            self.logger.error(f"OpenAI generation failed: {e}")
            return ModelResponse(
                content=f"[系统消息] OpenAI响应生成失败: {e!s}",
                role_id=role_id,
                model_type="openai",
            )


class AnthropicAdapter(BaseModelAdapter):
    """Anthropic模型适配器"""

    def __init__(
        self,
        memory_bank: RoleMemoryBank,
        api_key: str,
        model_name: str = "claude-3-sonnet-20240229",
    ):
        super().__init__(memory_bank)
        self.api_key = api_key
        self.model_name = model_name

    async def generate_response(
        self,
        role_id: str,
        user_message: str,
        project_id: Optional[str] = None,
        session_id: Optional[str] = None,
        conversation_history: Optional[list[dict[str, str]]] = None,
        **kwargs,
    ) -> ModelResponse:
        """生成响应"""
        try:
            import anthropic

            # 准备上下文
            context = self._prepare_context(
                role_id,
                user_message,
                project_id,
                session_id,
                conversation_history,
            )

            # 构建系统提示
            system_prompt = ""
            identity = context.get("role_identity")
            if identity:
                system_prompt = (
                    f"你是{identity['name']}，{identity['title']}。{identity['background']}"
                )

                # 添加相关记忆
                memories = context.get("relevant_memories", [])
                if memories:
                    memory_text = "\n".join(
                        [f"- {m['content'][:100]}" for m in memories[:3]],
                    )
                    system_prompt += f"\n\n相关记忆：\n{memory_text}"

            # 调用Anthropic API
            client = anthropic.AsyncAnthropic(api_key=self.api_key)

            response = await client.messages.create(
                model=self.model_name,
                max_tokens=kwargs.get("max_tokens", 2048),
                temperature=kwargs.get("temperature", 0.7),
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )

            content = response.content[0].text.strip()

            # 保存交互记忆
            self._save_interaction(
                role_id,
                user_message,
                content,
                project_id,
                session_id,
            )

            return ModelResponse(
                content=content,
                role_id=role_id,
                model_type="anthropic",
                usage_info={
                    "model": self.model_name,
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
                metadata={"context_used": len(context.get("relevant_memories", []))},
            )

        except Exception as e:
            self.logger.error(f"Anthropic generation failed: {e}")
            return ModelResponse(
                content=f"[系统消息] Claude响应生成失败: {e!s}",
                role_id=role_id,
                model_type="anthropic",
            )


class SiliconFlowAdapter(BaseModelAdapter):
    """SiliconFlow模型适配器"""

    def __init__(
        self,
        memory_bank: RoleMemoryBank,
        api_key: str,
        model_name: str = "internlm/internlm2_5-7b-chat",
    ):
        super().__init__(memory_bank)
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = "https://api.siliconflow.cn/v1"

    async def generate_response(
        self,
        role_id: str,
        user_message: str,
        project_id: Optional[str] = None,
        session_id: Optional[str] = None,
        conversation_history: Optional[list[dict[str, str]]] = None,
        **kwargs,
    ) -> ModelResponse:
        """生成响应"""
        try:
            import aiohttp

            # 准备上下文
            context = self._prepare_context(
                role_id,
                user_message,
                project_id,
                session_id,
                conversation_history,
            )

            # 构建消息
            messages = []

            # 系统消息（角色身份）
            identity = context.get("role_identity")
            if identity:
                system_message = (
                    f"你是{identity['name']}，{identity['title']}。{identity['background']}"
                )

                # 添加相关记忆
                memories = context.get("relevant_memories", [])
                if memories:
                    memory_text = "\n".join(
                        [f"- {m['content'][:100]}" for m in memories[:3]],
                    )
                    system_message += f"\n\n相关记忆：\n{memory_text}"

                messages.append({"role": "system", "content": system_message})

            # 用户消息
            messages.append({"role": "user", "content": user_message})

            # 调用SiliconFlow API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2048),
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result["choices"][0]["message"]["content"].strip()

                        # 保存交互记忆
                        self._save_interaction(
                            role_id,
                            user_message,
                            content,
                            project_id,
                            session_id,
                        )

                        return ModelResponse(
                            content=content,
                            role_id=role_id,
                            model_type="siliconflow",
                            usage_info={
                                "model": self.model_name,
                                "tokens": result.get("usage", {}).get(
                                    "total_tokens",
                                    0,
                                ),
                            },
                            metadata={
                                "context_used": len(
                                    context.get("relevant_memories", []),
                                ),
                            },
                        )
                    else:
                        error_text = await response.text()
                        raise Exception(
                            f"SiliconFlow API error: {response.status} - {error_text}",
                        )

        except Exception as e:
            self.logger.error(f"SiliconFlow generation failed: {e}")
            return ModelResponse(
                content=f"[系统消息] SiliconFlow响应生成失败: {e!s}",
                role_id=role_id,
                model_type="siliconflow",
            )


class MultiModelManager:
    """多模型管理器"""

    def __init__(self, memory_bank: RoleMemoryBank):
        self.memory_bank = memory_bank
        self.adapters: dict[str, BaseModelAdapter] = {}
        self.default_adapter = None
        self.failed_adapters: set = set()  # 记录失败的适配器
        self.logger = logging.getLogger(__name__)

    def register_adapter(
        self,
        name: str,
        adapter: BaseModelAdapter,
        is_default: bool = False,
    ):
        """注册模型适配器"""
        self.adapters[name] = adapter
        if is_default or not self.default_adapter:
            self.default_adapter = adapter
        self.logger.info(f"Registered adapter: {name}")

    def setup_ollama(
        self,
        base_url: str = "http://localhost:11434",
        model_name: str = "gemma3:latest",
        is_default: bool = True,
    ):
        """设置Ollama适配器"""
        adapter = OllamaAdapter(self.memory_bank, base_url, model_name)
        self.register_adapter("ollama", adapter, is_default)

    def setup_openai(
        self,
        api_key: str,
        model_name: str = "gpt-3.5-turbo",
        is_default: bool = False,
    ):
        """设置OpenAI适配器"""
        adapter = OpenAIAdapter(self.memory_bank, api_key, model_name)
        self.register_adapter("openai", adapter, is_default)

    def setup_anthropic(
        self,
        api_key: str,
        model_name: str = "claude-3-sonnet-20240229",
        is_default: bool = False,
    ):
        """设置Anthropic适配器"""
        adapter = AnthropicAdapter(self.memory_bank, api_key, model_name)
        self.register_adapter("anthropic", adapter, is_default)

    def setup_siliconflow(
        self,
        api_key: str,
        model_name: str = "internlm/internlm2_5-7b-chat",
        is_default: bool = False,
    ):
        """设置SiliconFlow适配器"""
        adapter = SiliconFlowAdapter(self.memory_bank, api_key, model_name)
        self.register_adapter("siliconflow", adapter, is_default)

    async def generate_response(
        self,
        role_id: str,
        user_message: str,
        model_name: Optional[str] = None,
        project_id: Optional[str] = None,
        session_id: Optional[str] = None,
        conversation_history: Optional[list[dict[str, str]]] = None,
        **kwargs,
    ) -> ModelResponse:
        """生成响应 - 支持自动跳过不可用模型"""
        # 获取候选适配器列表
        candidate_adapters = []

        if model_name and model_name in self.adapters:
            # 指定模型优先
            candidate_adapters.append((model_name, self.adapters[model_name]))

        # 添加其他可用适配器作为备选
        for name, adapter in self.adapters.items():
            if name != model_name and name not in self.failed_adapters:
                candidate_adapters.append((name, adapter))

        # 如果没有候选适配器，返回模拟响应
        if not candidate_adapters:
            self.logger.warning(
                "No available model adapters, returning simulated response",
            )
            raise RuntimeError(
                "No available model adapters. Please check your real model configuration.",
            )

        # 尝试每个适配器
        last_error = None
        for adapter_name, adapter in candidate_adapters:
            try:
                self.logger.debug(f"Trying adapter: {adapter_name}")

                response = await adapter.generate_response(
                    role_id=role_id,
                    user_message=user_message,
                    project_id=project_id,
                    session_id=session_id,
                    conversation_history=conversation_history,
                    **kwargs,
                )

                # 检查响应是否为错误消息
                if not response.content.startswith("[系统消息]"):
                    self.logger.info(
                        f"Successfully generated response using {adapter_name}",
                    )
                    return response
                else:
                    # 这是一个错误响应，尝试下一个适配器
                    self.logger.warning(
                        f"Adapter {adapter_name} returned error response",
                    )
                    self.failed_adapters.add(adapter_name)
                    last_error = response.content
                    continue

            except Exception as e:
                self.logger.warning(f"Adapter {adapter_name} failed: {e}")
                self.failed_adapters.add(adapter_name)
                last_error = str(e)
                continue

        # 所有适配器都失败了，返回模拟响应
        self.logger.warning("All model adapters failed, returning simulated response")
        raise RuntimeError(f"All model adapters failed. Last error: {last_error}")

    def get_available_models(self) -> list[str]:
        """获取可用模型列表"""
        return list(self.adapters.keys())

    def get_working_models(self) -> list[str]:
        """获取当前可工作的模型列表（排除失败的）"""
        return [
            name for name in self.adapters.keys() if name not in self.failed_adapters
        ]

    def reset_failed_adapters(self):
        """重置失败的适配器列表 - 允许重新尝试"""
        self.failed_adapters.clear()
        self.logger.info("Reset failed adapters list")

    def mark_adapter_as_failed(self, adapter_name: str):
        """手动标记适配器为失败状态"""
        self.failed_adapters.add(adapter_name)
        self.logger.warning(f"Marked adapter as failed: {adapter_name}")

    def get_adapter_status(self) -> dict[str, str]:
        """获取所有适配器的状态"""
        status = {}
        for name in self.adapters.keys():
            if name in self.failed_adapters:
                status[name] = "failed"
            else:
                status[name] = "available"
        return status

    def create_role_from_expert(self, expert_data: dict[str, Any]) -> str:
        """从专家数据创建角色身份"""
        return self.memory_bank.create_role_identity(expert_data).role_id

    def restore_role_identity(self, role_id: str) -> Optional[RoleIdentity]:
        """恢复角色身份"""
        return self.memory_bank.get_role_identity(role_id)

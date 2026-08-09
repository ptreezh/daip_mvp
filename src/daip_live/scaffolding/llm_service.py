"""
LLM服务接口
提供统一的AI模型调用接口，支持多种LLM提供商
"""

import asyncio
import re
import time
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from .models import NetworkError, TimeoutError, ValidationError


class LLMProvider(Enum):
    """LLM提供商枚举"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LOCAL = "local"
    OLLAMA = "ollama"

    @classmethod
    def from_string(cls, value: str) -> "LLMProvider":
        """从字符串获取提供商"""
        provider_map = {
            "openai": cls.OPENAI,
            "anthropic": cls.ANTHROPIC,
            "google": cls.GOOGLE,
            "local": cls.LOCAL,
            "ollama": cls.OLLAMA,
        }
        return provider_map.get(value.lower(), cls.OPENAI)


class MessageRole(Enum):
    """消息角色枚举"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


@dataclass
class PromptVariable:
    """提示变量"""

    name: str
    description: str
    required: bool = True
    default_value: str = ""

    def validate(self, value: str) -> list[str]:
        """验证变量值"""
        errors = []

        if self.required and not value.strip():
            errors.append(f"变量 '{self.name}' 是必需的")

        return errors


@dataclass
class PromptTemplate:
    """提示模板"""

    name: str
    content: str
    description: str = ""
    variables: list[PromptVariable] = field(default_factory=list)

    def render(self, context: dict[str, str]) -> str:
        """渲染模板"""
        # 验证必需变量
        for var in self.variables:
            if var.required and var.name not in context:
                raise ValidationError(f"缺少必需的变量: {var.name}")

        # 替换变量
        result = self.content
        for var in self.variables:
            value = context.get(var.name, var.default_value)
            result = result.replace(f"{{{var.name}}}", value)

        return result

    def validate_context(self, context: dict[str, str]) -> list[str]:
        """验证上下文"""
        errors = []
        for var in self.variables:
            value = context.get(var.name, var.default_value)
            errors.extend(var.validate(value))
        return errors


@dataclass
class ConversationMessage:
    """对话消息"""

    role: MessageRole
    content: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp,
        }


@dataclass
class ConversationContext:
    """对话上下文"""

    messages: list[ConversationMessage] = field(default_factory=list)
    max_messages: int = 50

    def add_message(self, role: MessageRole, content: str) -> None:
        """添加消息"""
        message = ConversationMessage(role, content)
        self.messages.append(message)

        # 保持消息数量限制
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages :]

    def get_recent_messages(self, count: int = 10) -> list[ConversationMessage]:
        """获取最近的消息"""
        return self.messages[-count:]

    def clear(self) -> None:
        """清空对话"""
        self.messages.clear()


@dataclass
class LLMModelConfig:
    """LLM模型配置"""

    provider: LLMProvider
    model_name: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: float = 30.0

    def validate(self) -> list[str]:
        """验证配置"""
        errors = []

        if not self.model_name.strip():
            errors.append("模型名称不能为空")

        if (
            self.provider not in [LLMProvider.LOCAL, LLMProvider.OLLAMA]
            and not self.api_key
        ):
            errors.append(f"提供商 {self.provider.value} 需要API密钥")

        if not 0.0 <= self.temperature <= 2.0:
            errors.append("温度参数必须在0.0-2.0之间")

        if not 0.0 <= self.top_p <= 1.0:
            errors.append("top_p参数必须在0.0-1.0之间")

        if self.max_tokens <= 0:
            errors.append("max_tokens必须大于0")

        return errors


@dataclass
class LLMRequest:
    """LLM请求"""

    prompt: str
    context: dict[str, Any] = field(default_factory=dict)
    model_config: Optional[LLMModelConfig] = None
    conversation: Optional[ConversationContext] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    stream: bool = False
    tools: list[dict[str, Any]] = field(default_factory=list)

    def get_conversation_messages(self) -> list[dict[str, Any]]:
        """获取对话消息列表"""
        if not self.conversation:
            return []

        messages = []
        for msg in self.conversation.messages:
            messages.append(msg.to_dict())
        return messages


@dataclass
class LLMResponse:
    """LLM响应"""

    content: str = ""
    model: str = ""
    usage: dict[str, int] = field(default_factory=dict)
    finish_reason: str = "stop"
    error: Optional[str] = None
    error_code: Optional[str] = None
    finished: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def has_error(self) -> bool:
        """是否有错误"""
        return self.error is not None

    def is_finished(self) -> bool:
        """是否完成"""
        return self.finished

    @property
    def success(self) -> bool:
        """是否成功"""
        return not self.has_error() and self.is_finished()


@dataclass
class LLMServiceConfig:
    """LLM服务配置"""

    default_model: Optional[LLMModelConfig] = None
    fallback_model: Optional[LLMModelConfig] = None
    models: dict[str, LLMModelConfig] = field(default_factory=dict)
    timeout: float = 60.0
    max_retries: int = 3
    retry_delay: float = 1.0
    rate_limit_enabled: bool = True

    def add_model(self, name: str, config: LLMModelConfig) -> None:
        """添加模型配置"""
        self.models[name] = config

    def get_model(self, name: str) -> Optional[LLMModelConfig]:
        """获取模型配置"""
        return self.models.get(name)


class BaseLLMProvider(ABC):
    """LLM提供商基类"""

    def __init__(self, config: LLMModelConfig):
        self.config = config

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """生成文本"""
        pass

    @abstractmethod
    async def generate_stream(
        self, request: LLMRequest
    ) -> AsyncGenerator[LLMResponse, None]:
        """流式生成文本"""
        pass

    @abstractmethod
    def validate_request(self, request: LLMRequest) -> list[str]:
        """验证请求"""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI提供商"""

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """使用OpenAI生成文本"""
        try:
            # 这里应该调用实际的OpenAI API
            # 目前返回模拟响应
            await asyncio.sleep(0.1)  # 模拟网络延迟

            return LLMResponse(
                content=self._mock_response(request.prompt),
                model=self.config.model_name,
                usage={
                    "prompt_tokens": 50,
                    "completion_tokens": 100,
                    "total_tokens": 150,
                },
            )

        except Exception as e:
            return LLMResponse(
                error=f"OpenAI API错误: {str(e)}", error_code="openai_error"
            )

    async def generate_stream(
        self, request: LLMRequest
    ) -> AsyncGenerator[LLMResponse, None]:
        """使用OpenAI流式生成"""
        try:
            # 模拟流式响应
            content = self._mock_response(request.prompt)
            words = content.split()

            for i, word in enumerate(words):
                yield LLMResponse(
                    content=word + (" " if i < len(words) - 1 else ""), finished=False
                )
                await asyncio.sleep(0.05)  # 模拟流式延迟

            yield LLMResponse(finished=True)

        except Exception as e:
            yield LLMResponse(
                error=f"OpenAI流式错误: {str(e)}",
                error_code="openai_stream_error",
                finished=True,
            )

    def validate_request(self, request: LLMRequest) -> list[str]:
        """验证OpenAI请求"""
        errors = []

        if not request.prompt.strip():
            errors.append("提示内容不能为空")

        return errors

    def _mock_response(self, prompt: str) -> str:
        """生成模拟响应"""
        if "Python" in prompt or "python" in prompt:
            return "```python\ndef hello_world():\n    print('Hello, World!')\n```"
        elif "web app" in prompt or "web应用" in prompt:
            return "创建一个使用Flask的Web应用程序，包含路由和模板。"
        else:
            return f"这是对提示 '{prompt[:50]}...' 的响应。"


class AnthropicProvider(BaseLLMProvider):
    """Anthropic提供商"""

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """使用Anthropic生成文本"""
        try:
            await asyncio.sleep(0.1)

            return LLMResponse(
                content=self._mock_response(request.prompt),
                model=self.config.model_name,
                usage={"input_tokens": 40, "output_tokens": 80, "total_tokens": 120},
            )

        except Exception as e:
            return LLMResponse(
                error=f"Anthropic API错误: {str(e)}", error_code="anthropic_error"
            )

    async def generate_stream(
        self, request: LLMRequest
    ) -> AsyncGenerator[LLMResponse, None]:
        """使用Anthropic流式生成"""
        try:
            content = self._mock_response(request.prompt)
            for char in content:
                yield LLMResponse(content=char, finished=False)
                await asyncio.sleep(0.01)

            yield LLMResponse(finished=True)

        except Exception as e:
            yield LLMResponse(
                error=f"Anthropic流式错误: {str(e)}",
                error_code="anthropic_stream_error",
                finished=True,
            )

    def validate_request(self, request: LLMRequest) -> list[str]:
        """验证Anthropic请求"""
        errors = []

        if not request.prompt.strip():
            errors.append("提示内容不能为空")

        return errors

    def _mock_response(self, prompt: str) -> str:
        """生成模拟响应"""
        return f"[Claude响应] 这是针对 '{prompt[:30]}...' 的详细回答。"


class LocalProvider(BaseLLMProvider):
    """本地模型提供商"""

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """使用本地模型生成文本"""
        try:
            await asyncio.sleep(0.2)  # 本地模型可能较慢

            return LLMResponse(
                content=self._mock_response(request.prompt),
                model=self.config.model_name,
                usage={
                    "prompt_tokens": 30,
                    "completion_tokens": 60,
                    "total_tokens": 90,
                },
            )

        except Exception as e:
            return LLMResponse(
                error=f"本地模型错误: {str(e)}", error_code="local_model_error"
            )

    async def generate_stream(
        self, request: LLMRequest
    ) -> AsyncGenerator[LLMResponse, None]:
        """使用本地模型流式生成"""
        try:
            content = self._mock_response(request.prompt)
            sentences = re.split(r"[.!?。！？]", content)

            for sentence in sentences:
                if sentence.strip():
                    yield LLMResponse(content=sentence.strip() + "。", finished=False)
                    await asyncio.sleep(0.1)

            yield LLMResponse(finished=True)

        except Exception as e:
            yield LLMResponse(
                error=f"本地模型流式错误: {str(e)}",
                error_code="local_stream_error",
                finished=True,
            )

    def validate_request(self, request: LLMRequest) -> list[str]:
        """验证本地模型请求"""
        return []

    def _mock_response(self, prompt: str) -> str:
        """生成模拟响应"""
        return f"[本地模型] 这是一个基于 '{prompt}' 的本地生成响应。"


class OllamaProvider(BaseLLMProvider):
    """Ollama提供商"""

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """使用Ollama生成文本"""
        try:
            await asyncio.sleep(0.3)

            return LLMResponse(
                content=self._mock_response(request.prompt),
                model=self.config.model_name,
            )

        except Exception as e:
            return LLMResponse(error=f"Ollama错误: {str(e)}", error_code="ollama_error")

    async def generate_stream(
        self, request: LLMRequest
    ) -> AsyncGenerator[LLMResponse, None]:
        """使用Ollama流式生成"""
        try:
            content = self._mock_response(request.prompt)
            for i in range(0, len(content), 10):
                chunk = content[i : i + 10]
                yield LLMResponse(content=chunk, finished=False)
                await asyncio.sleep(0.05)

            yield LLMResponse(finished=True)

        except Exception as e:
            yield LLMResponse(
                error=f"Ollama流式错误: {str(e)}",
                error_code="ollama_stream_error",
                finished=True,
            )

    def validate_request(self, request: LLMRequest) -> list[str]:
        """验证Ollama请求"""
        return []

    def _mock_response(self, prompt: str) -> str:
        """生成模拟响应"""
        return f"[Ollama: {self.config.model_name}] 这是针对请求的响应内容。"


class LLMService:
    """LLM服务"""

    def __init__(self, config: Optional[LLMServiceConfig] = None):
        self.config = config or LLMServiceConfig()
        self.prompt_templates: dict[str, PromptTemplate] = {}
        self.default_provider = LLMProvider.OPENAI

        # 初始化提供商映射
        self._providers = {
            LLMProvider.OPENAI: OpenAIProvider,
            LLMProvider.ANTHROPIC: AnthropicProvider,
            LLMProvider.LOCAL: LocalProvider,
            LLMProvider.OLLAMA: OllamaProvider,
        }

        # 设置默认模型
        if self.config.default_model:
            self.default_provider = self.config.default_model.provider

    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """生成文本"""
        # 使用默认模型配置
        if not request.model_config and self.config.default_model:
            request.model_config = self.config.default_model

        if not request.model_config:
            return LLMResponse(error="未配置模型", error_code="no_model_config")

        # 验证请求
        errors = self._validate_request(request)
        if errors:
            return LLMResponse(
                error=f"请求验证失败: {', '.join(errors)}",
                error_code="validation_error",
            )

        # 尝试主提供商
        for attempt in range(self.config.max_retries + 1):
            try:
                response = await self._call_provider(
                    request.model_config.provider, request
                )
                if response.success:
                    return response

                # 如果是速率限制错误，尝试重试
                if (
                    response.error_code == "rate_limit"
                    and attempt < self.config.max_retries
                ):
                    await asyncio.sleep(self.config.retry_delay * (2**attempt))
                    continue

                return response

            except NetworkError as e:
                if attempt < self.config.max_retries:
                    await asyncio.sleep(self.config.retry_delay * (2**attempt))
                    continue

                # 尝试回退提供商
                if self.config.fallback_model:
                    return await self._call_fallback_provider(request)

                return LLMResponse(
                    error=f"网络错误: {str(e)}", error_code="network_error"
                )
            except TimeoutError as e:
                if attempt < self.config.max_retries:
                    await asyncio.sleep(self.config.retry_delay * (2**attempt))
                    continue

                # 尝试回退提供商
                if self.config.fallback_model:
                    return await self._call_fallback_provider(request)

                return LLMResponse(
                    error=f"超时错误: {str(e)}", error_code="timeout_error"
                )

        return LLMResponse(error="所有重试都失败了", error_code="all_retries_failed")

    async def generate_text_stream(
        self, request: LLMRequest
    ) -> AsyncGenerator[LLMResponse, None]:
        """流式生成文本"""
        if not request.model_config and self.config.default_model:
            request.model_config = self.config.default_model

        if not request.model_config:
            yield LLMResponse(
                error="未配置模型", error_code="no_model_config", finished=True
            )
            return

        try:
            async for response in self._call_provider_stream(
                request.model_config.provider, request
            ):
                yield response

        except Exception as e:
            yield LLMResponse(
                error=f"流式生成失败: {str(e)}",
                error_code="stream_error",
                finished=True,
            )

    async def generate_from_template(
        self, template_name: str, context: dict[str, Any], **kwargs
    ) -> LLMResponse:
        """从模板生成"""
        if template_name not in self.prompt_templates:
            return LLMResponse(
                error=f"模板不存在: {template_name}", error_code="template_not_found"
            )

        template = self.prompt_templates[template_name]

        try:
            rendered_prompt = template.render(context)
            request = LLMRequest(prompt=rendered_prompt, context=context, **kwargs)
            return await self.generate_text(request)

        except Exception as e:
            return LLMResponse(
                error=f"模板渲染失败: {str(e)}", error_code="template_render_error"
            )

    def add_prompt_template(self, template: PromptTemplate) -> None:
        """添加提示模板"""
        self.prompt_templates[template.name] = template

    def use_prompt_template(self, template_name: str, context: dict[str, Any]) -> str:
        """使用提示模板"""
        if template_name not in self.prompt_templates:
            raise ValidationError(f"模板不存在: {template_name}")

        template = self.prompt_templates[template_name]
        return template.render(context)

    def validate_model_config(self, config: LLMModelConfig) -> list[str]:
        """验证模型配置"""
        return config.validate()

    def _validate_request(self, request: LLMRequest) -> list[str]:
        """验证请求"""
        errors = []

        if not request.prompt.strip():
            errors.append("提示内容不能为空")

        if request.model_config:
            errors.extend(request.model_config.validate())

        return errors

    async def _call_provider(
        self, provider: LLMProvider, request: LLMRequest
    ) -> LLMResponse:
        """调用提供商"""
        provider_class = self._providers.get(provider)
        if not provider_class:
            return LLMResponse(
                error=f"不支持的提供商: {provider.value}",
                error_code="unsupported_provider",
            )

        provider_instance = provider_class(request.model_config)
        return await provider_instance.generate(request)

    async def _call_provider_stream(
        self, provider: LLMProvider, request: LLMRequest
    ) -> AsyncGenerator[LLMResponse, None]:
        """调用提供商流式接口"""
        provider_class = self._providers.get(provider)
        if not provider_class:
            yield LLMResponse(
                error=f"不支持的提供商: {provider.value}",
                error_code="unsupported_provider",
                finished=True,
            )
            return

        provider_instance = provider_class(request.model_config)
        async for response in provider_instance.generate_stream(request):
            yield response

    # 兼容性方法 - 为了测试兼容
    async def _call_openai(self, request: LLMRequest) -> LLMResponse:
        """调用OpenAI提供商（兼容性方法）"""
        return await self._call_provider(LLMProvider.OPENAI, request)

    async def _call_anthropic(self, request: LLMRequest) -> LLMResponse:
        """调用Anthropic提供商（兼容性方法）"""
        return await self._call_provider(LLMProvider.ANTHROPIC, request)

    async def _call_openai_stream(
        self, request: LLMRequest
    ) -> AsyncGenerator[LLMResponse, None]:
        """调用OpenAI流式提供商（兼容性方法）"""
        async for response in self._call_provider_stream(LLMProvider.OPENAI, request):
            yield response

    async def _call_fallback_provider(self, request: LLMRequest) -> LLMResponse:
        """调用回退提供商"""
        if not self.config.fallback_model:
            return LLMResponse(error="未配置回退提供商", error_code="no_fallback")

        # 临时替换模型配置
        original_config = request.model_config
        request.model_config = self.config.fallback_model

        try:
            response = await self._call_provider(
                self.config.fallback_model.provider, request
            )
            return response
        finally:
            request.model_config = original_config

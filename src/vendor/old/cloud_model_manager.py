"""云端模型管理器
支持多种云端API LLMs的统一接口和测试功能
"""

import json
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

# 导入各种API客户端
try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai

    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

try:
    import cohere

    COHERE_AVAILABLE = True
except ImportError:
    COHERE_AVAILABLE = False

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


@dataclass
class ModelResponse:
    """模型响应数据类"""

    model_id: str
    provider: str
    content: str
    tokens_used: int
    response_time: float
    cost: float
    error: Optional[str] = None
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class TestResult:
    """测试结果数据类"""

    test_name: str
    model_id: str
    success: bool
    response: Optional[ModelResponse]
    score: float
    notes: str
    timestamp: str


class CloudModelManager:
    """云端模型管理器"""

    def __init__(self, config_file: str = "config/cloud_models.json"):
        self.config_file = Path(config_file)
        self.models_config = {}
        self.test_scenarios = []
        self.api_keys = {}
        self.logger = logging.getLogger(__name__)

        # 加载配置
        self._load_config()
        self._load_api_keys()

        # 初始化客户端
        self.clients = {}
        self._initialize_clients()

    def _load_config(self):
        """加载模型配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, encoding="utf-8") as f:
                    data = json.load(f)
                    self.models_config = data.get("cloud_models", {})
                    self.test_scenarios = data.get("test_scenarios", [])
                self.logger.info(f"加载了 {len(self.models_config)} 个提供商的模型配置")
            except Exception as e:
                self.logger.error(f"加载模型配置失败: {e}")
        else:
            self.logger.warning(f"配置文件不存在: {self.config_file}")

    def _load_api_keys(self):
        """加载API密钥"""
        # 从环境变量加载API密钥
        self.api_keys = {
            "qiniu": os.getenv("QINIU_API_KEY"),
            "together": os.getenv("TOGETHER_API_KEY"),
            "openrouter": os.getenv("OPENROUTER_API_KEY"),
            "siliconflow": os.getenv("SILICONFLOW_API_KEY"),
        }

        # 检查可用的API密钥
        available_keys = {k: v for k, v in self.api_keys.items() if v}
        self.logger.info(f"可用的API密钥: {list(available_keys.keys())}")

    def _initialize_clients(self):
        """初始化API客户端"""
        # OpenAI客户端
        if OPENAI_AVAILABLE and self.api_keys.get("openai"):
            try:
                self.clients["openai"] = openai.OpenAI(api_key=self.api_keys["openai"])
                self.logger.info("OpenAI客户端初始化成功")
            except Exception as e:
                self.logger.error(f"OpenAI客户端初始化失败: {e}")

        # Anthropic客户端
        if ANTHROPIC_AVAILABLE and self.api_keys.get("anthropic"):
            try:
                self.clients["anthropic"] = anthropic.Anthropic(
                    api_key=self.api_keys["anthropic"],
                )
                self.logger.info("Anthropic客户端初始化成功")
            except Exception as e:
                self.logger.error(f"Anthropic客户端初始化失败: {e}")

        # Google客户端
        if GOOGLE_AVAILABLE and self.api_keys.get("google"):
            try:
                genai.configure(api_key=self.api_keys["google"])
                self.clients["google"] = genai
                self.logger.info("Google客户端初始化成功")
            except Exception as e:
                self.logger.error(f"Google客户端初始化失败: {e}")

        # Cohere客户端
        if COHERE_AVAILABLE and self.api_keys.get("cohere"):
            try:
                self.clients["cohere"] = cohere.Client(api_key=self.api_keys["cohere"])
                self.logger.info("Cohere客户端初始化成功")
            except Exception as e:
                self.logger.error(f"Cohere客户端初始化失败: {e}")

        # Azure OpenAI客户端
        if (
            OPENAI_AVAILABLE
            and self.api_keys.get("azure_openai")
            and self.api_keys.get("azure_endpoint")
        ):
            try:
                self.clients["azure"] = openai.AzureOpenAI(
                    api_key=self.api_keys["azure_openai"],
                    azure_endpoint=self.api_keys["azure_endpoint"],
                    api_version="2024-02-01",
                )
                self.logger.info("Azure OpenAI客户端初始化成功")
            except Exception as e:
                self.logger.error(f"Azure OpenAI客户端初始化失败: {e}")

    def get_available_models(self) -> list[dict[str, Any]]:
        """获取可用的模型列表"""
        available_models = []

        for provider, models in self.models_config.items():
            if provider in self.clients:
                for model_id, config in models.items():
                    available_models.append(
                        {
                            "id": f"{provider}:{model_id}",
                            "name": config["name"],
                            "provider": provider,
                            "description": config["description"],
                            "max_tokens": config["max_tokens"],
                            "supports_functions": config.get(
                                "supports_functions",
                                False,
                            ),
                            "cost_per_1k_tokens": config.get("cost_per_1k_tokens", {}),
                        },
                    )

        return available_models

    async def call_model(self, model_id: str, prompt: str, **kwargs) -> ModelResponse:
        """调用指定模型"""
        provider, model_name = model_id.split(":", 1)

        if provider not in self.clients:
            return ModelResponse(
                model_id=model_id,
                provider=provider,
                content="",
                tokens_used=0,
                response_time=0,
                cost=0,
                error=f"Provider {provider} not available",
            )

        model_config = self.models_config[provider][model_name]
        start_time = time.time()

        try:
            if provider == "openai":
                response = await self._call_openai(model_config, prompt, **kwargs)
            elif provider == "anthropic":
                response = await self._call_anthropic(model_config, prompt, **kwargs)
            elif provider == "google":
                response = await self._call_google(model_config, prompt, **kwargs)
            elif provider == "cohere":
                response = await self._call_cohere(model_config, prompt, **kwargs)
            elif provider == "azure":
                response = await self._call_azure(model_config, prompt, **kwargs)
            elif provider == "huggingface":
                response = await self._call_huggingface(model_config, prompt, **kwargs)
            else:
                raise ValueError(f"Unsupported provider: {provider}")

            response_time = time.time() - start_time
            response.response_time = response_time
            response.model_id = model_id
            response.provider = provider

            return response

        except Exception as e:
            return ModelResponse(
                model_id=model_id,
                provider=provider,
                content="",
                tokens_used=0,
                response_time=time.time() - start_time,
                cost=0,
                error=str(e),
            )

    async def _call_openai(self, config: dict, prompt: str, **kwargs) -> ModelResponse:
        """调用OpenAI模型"""
        client = self.clients["openai"]

        messages = [{"role": "user", "content": prompt}]

        response = await client.chat.completions.create(
            model=config["model_name"],
            messages=messages,
            max_tokens=kwargs.get("max_tokens", config["max_tokens"]),
            temperature=kwargs.get("temperature", config["temperature"]),
        )

        content = response.choices[0].message.content
        tokens_used = response.usage.total_tokens

        # 计算成本
        cost_config = config.get("cost_per_1k_tokens", {})
        input_cost = (response.usage.prompt_tokens / 1000) * cost_config.get("input", 0)
        output_cost = (response.usage.completion_tokens / 1000) * cost_config.get(
            "output",
            0,
        )
        total_cost = input_cost + output_cost

        return ModelResponse(
            model_id="",
            provider="",
            content=content,
            tokens_used=tokens_used,
            response_time=0,
            cost=total_cost,
            metadata={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
            },
        )

    async def _call_anthropic(
        self,
        config: dict,
        prompt: str,
        **kwargs,
    ) -> ModelResponse:
        """调用Anthropic模型"""
        client = self.clients["anthropic"]

        response = await client.messages.create(
            model=config["model_name"],
            max_tokens=kwargs.get("max_tokens", config["max_tokens"]),
            temperature=kwargs.get("temperature", config["temperature"]),
            messages=[{"role": "user", "content": prompt}],
        )

        content = response.content[0].text
        tokens_used = response.usage.input_tokens + response.usage.output_tokens

        # 计算成本
        cost_config = config.get("cost_per_1k_tokens", {})
        input_cost = (response.usage.input_tokens / 1000) * cost_config.get("input", 0)
        output_cost = (response.usage.output_tokens / 1000) * cost_config.get(
            "output",
            0,
        )
        total_cost = input_cost + output_cost

        return ModelResponse(
            model_id="",
            provider="",
            content=content,
            tokens_used=tokens_used,
            response_time=0,
            cost=total_cost,
            metadata={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
        )

    async def _call_google(self, config: dict, prompt: str, **kwargs) -> ModelResponse:
        """调用Google模型"""
        genai = self.clients["google"]

        model = genai.GenerativeModel(config["model_name"])
        response = await model.generate_content_async(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=kwargs.get("max_tokens", config["max_tokens"]),
                temperature=kwargs.get("temperature", config["temperature"]),
            ),
        )

        content = response.text
        # Google API通常不返回token使用量，需要估算
        tokens_used = len(prompt.split()) + len(content.split())

        # 计算成本
        cost_config = config.get("cost_per_1k_tokens", {})
        estimated_cost = (tokens_used / 1000) * cost_config.get("input", 0)

        return ModelResponse(
            model_id="",
            provider="",
            content=content,
            tokens_used=tokens_used,
            response_time=0,
            cost=estimated_cost,
            metadata={"estimated_tokens": True},
        )

    async def _call_cohere(self, config: dict, prompt: str, **kwargs) -> ModelResponse:
        """调用Cohere模型"""
        client = self.clients["cohere"]

        response = client.generate(
            model=config["model_name"],
            prompt=prompt,
            max_tokens=kwargs.get("max_tokens", config["max_tokens"]),
            temperature=kwargs.get("temperature", config["temperature"]),
        )

        content = response.generations[0].text
        # Cohere API通常不返回详细token使用量
        tokens_used = len(prompt.split()) + len(content.split())

        # 计算成本
        cost_config = config.get("cost_per_1k_tokens", {})
        estimated_cost = (tokens_used / 1000) * cost_config.get("input", 0)

        return ModelResponse(
            model_id="",
            provider="",
            content=content,
            tokens_used=tokens_used,
            response_time=0,
            cost=estimated_cost,
            metadata={"estimated_tokens": True},
        )

    async def _call_azure(self, config: dict, prompt: str, **kwargs) -> ModelResponse:
        """调用Azure OpenAI模型"""
        client = self.clients["azure"]

        messages = [{"role": "user", "content": prompt}]

        response = await client.chat.completions.create(
            model=config["model_name"],
            messages=messages,
            max_tokens=kwargs.get("max_tokens", config["max_tokens"]),
            temperature=kwargs.get("temperature", config["temperature"]),
        )

        content = response.choices[0].message.content
        tokens_used = response.usage.total_tokens

        return ModelResponse(
            model_id="",
            provider="",
            content=content,
            tokens_used=tokens_used,
            response_time=0,
            cost=0,  # Azure定价通常是订阅制
            metadata={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
            },
        )

    async def _call_huggingface(
        self,
        config: dict,
        prompt: str,
        **kwargs,
    ) -> ModelResponse:
        """调用HuggingFace模型"""
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library not available")

        api_key = self.api_keys.get("huggingface")
        if not api_key:
            raise ValueError("HuggingFace API key not available")

        headers = {"Authorization": f"Bearer {api_key}"}
        api_url = f"https://api-inference.huggingface.co/models/{config['model_name']}"

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": kwargs.get("max_tokens", config["max_tokens"]),
                "temperature": kwargs.get("temperature", config["temperature"]),
            },
        }

        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()

        result = response.json()
        content = (
            result[0]["generated_text"]
            if isinstance(result, list)
            else result.get("generated_text", "")
        )

        # 移除输入部分，只保留生成的内容
        if content.startswith(prompt):
            content = content[len(prompt) :].strip()

        tokens_used = len(prompt.split()) + len(content.split())

        return ModelResponse(
            model_id="",
            provider="",
            content=content,
            tokens_used=tokens_used,
            response_time=0,
            cost=0,  # HuggingFace免费层
            metadata={"estimated_tokens": True},
        )

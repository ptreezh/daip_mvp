"""可靠的云端模型管理器
支持自动故障转移、模型轮换和状态记忆功能
确保云端模型调用的高可用性
"""

import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
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
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


@dataclass
class ModelStatus:
    """模型状态"""

    model_id: str
    provider: str
    is_available: bool
    last_success: Optional[datetime]
    last_failure: Optional[datetime]
    consecutive_failures: int
    total_calls: int
    success_rate: float
    avg_response_time: float
    last_error: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "provider": self.provider,
            "is_available": self.is_available,
            "last_success": self.last_success.isoformat()
            if self.last_success
            else None,
            "last_failure": self.last_failure.isoformat()
            if self.last_failure
            else None,
            "consecutive_failures": self.consecutive_failures,
            "total_calls": self.total_calls,
            "success_rate": self.success_rate,
            "avg_response_time": self.avg_response_time,
            "last_error": self.last_error,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ModelStatus":
        return cls(
            model_id=data["model_id"],
            provider=data["provider"],
            is_available=data["is_available"],
            last_success=datetime.fromisoformat(data["last_success"])
            if data["last_success"]
            else None,
            last_failure=datetime.fromisoformat(data["last_failure"])
            if data["last_failure"]
            else None,
            consecutive_failures=data["consecutive_failures"],
            total_calls=data["total_calls"],
            success_rate=data["success_rate"],
            avg_response_time=data["avg_response_time"],
            last_error=data.get("last_error"),
        )


@dataclass
class ModelResponse:
    """模型响应"""

    model_id: str
    provider: str
    content: str
    tokens_used: int
    response_time: float
    success: bool
    error: Optional[str] = None
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ReliableCloudModelManager:
    """可靠的云端模型管理器"""

    def __init__(
        self,
        config_file: str = "config/cloud_models.json",
        status_file: str = "data/model_status.json",
    ):
        self.config_file = Path(config_file)
        self.status_file = Path(status_file)
        self.status_file.parent.mkdir(exist_ok=True)

        self.models_config = {}
        self.model_status: dict[str, ModelStatus] = {}
        self.api_keys = {}
        self.clients = {}
        self.current_model = None  # 当前使用的模型
        self.fallback_models = []  # 备用模型列表

        self.logger = logging.getLogger(__name__)

        # 配置参数
        self.max_consecutive_failures = 3  # 最大连续失败次数
        self.failure_cooldown = timedelta(minutes=5)  # 失败后的冷却时间
        self.health_check_interval = timedelta(minutes=30)  # 健康检查间隔
        self.timeout = 30  # 请求超时时间

        # 初始化
        self._load_config()
        self._load_api_keys()
        self._load_model_status()
        self._initialize_clients()
        self._select_initial_model()

    def _load_config(self):
        """加载模型配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, encoding="utf-8") as f:
                    data = json.load(f)
                    self.models_config = data.get("cloud_models", {})
                self.logger.info(f"加载了 {len(self.models_config)} 个提供商的模型配置")
            except Exception as e:
                self.logger.error(f"加载模型配置失败: {e}")

    def _load_api_keys(self):
        """加载API密钥 - 优先使用utils.py中的现有配置"""
        # 首先尝试从utils.py获取配置
        try:
            import os
            import sys

            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # 添加项目根目录
            import utils

            self.api_keys = {
                # 使用utils.py中的现有API密钥
                "qiniu": getattr(utils, "QINIU_API_KEY", ""),
                "together": getattr(utils, "TOGETHER_API_KEY", ""),
                "openrouter": getattr(utils, "OPENROUTER_API_KEY", ""),
                "siliconflow": getattr(utils, "SILICONFLOW_API_KEY", ""),
                # 保留标准API密钥
                "openai": os.getenv("OPENAI_API_KEY"),
                "anthropic": os.getenv("ANTHROPIC_API_KEY"),
                "google": os.getenv("GOOGLE_API_KEY"),
                "cohere": os.getenv("COHERE_API_KEY"),
                "azure_openai": os.getenv("AZURE_OPENAI_API_KEY"),
                "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
                "huggingface": os.getenv("HUGGINGFACE_API_KEY"),
            }

            # 存储API URLs
            self.api_urls = {
                "qiniu": getattr(utils, "QINIU_API_URL", ""),
                "together": getattr(utils, "TOGETHER_API_URL", ""),
                "openrouter": getattr(utils, "OPENROUTER_API_URL", ""),
                "siliconflow": getattr(utils, "SILICONFLOW_API_URL", ""),
            }

            self.logger.info("成功加载utils.py中的API配置")

        except ImportError as e:
            self.logger.warning(f"无法导入utils.py: {e}，尝试chat_config.py")

            # 回退到chat_config.py
            try:
                from src.chat_config import CHAT_MODEL_CONFIG

                openai_key = CHAT_MODEL_CONFIG.get("openai", {}).get("api_key", "")
                anthropic_key = CHAT_MODEL_CONFIG.get("claude", {}).get("api_key", "")

                self.api_keys = {
                    "openai": openai_key or os.getenv("OPENAI_API_KEY"),
                    "anthropic": anthropic_key or os.getenv("ANTHROPIC_API_KEY"),
                    "google": os.getenv("GOOGLE_API_KEY"),
                    "cohere": os.getenv("COHERE_API_KEY"),
                    "azure_openai": os.getenv("AZURE_OPENAI_API_KEY"),
                    "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
                    "huggingface": os.getenv("HUGGINGFACE_API_KEY"),
                }
                self.api_urls = {}

            except ImportError:
                # 最终回退到环境变量
                self.api_keys = {
                    "openai": os.getenv("OPENAI_API_KEY"),
                    "anthropic": os.getenv("ANTHROPIC_API_KEY"),
                    "google": os.getenv("GOOGLE_API_KEY"),
                    "cohere": os.getenv("COHERE_API_KEY"),
                    "azure_openai": os.getenv("AZURE_OPENAI_API_KEY"),
                    "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
                    "huggingface": os.getenv("HUGGINGFACE_API_KEY"),
                }
                self.api_urls = {}

        available_keys = {k: v for k, v in self.api_keys.items() if v}
        self.logger.info(f"可用的API密钥: {list(available_keys.keys())}")

    def _load_model_status(self):
        """加载模型状态"""
        if self.status_file.exists():
            try:
                with open(self.status_file, encoding="utf-8") as f:
                    data = json.load(f)
                    for model_id, status_data in data.items():
                        self.model_status[model_id] = ModelStatus.from_dict(status_data)
                self.logger.info(f"加载了 {len(self.model_status)} 个模型的状态信息")
            except Exception as e:
                self.logger.error(f"加载模型状态失败: {e}")

    def _save_model_status(self):
        """保存模型状态"""
        try:
            data = {
                model_id: status.to_dict()
                for model_id, status in self.model_status.items()
            }
            with open(self.status_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存模型状态失败: {e}")

    def _initialize_clients(self):
        """初始化API客户端"""
        # 初始化utils.py中的云端API客户端
        if self.api_keys.get("qiniu"):
            self.clients["qiniu"] = "utils_api"  # 标记使用utils.py的API函数
            self.logger.info("Qiniu DeepSeek客户端初始化成功")

        if self.api_keys.get("together"):
            self.clients["together"] = "utils_api"
            self.logger.info("Together.ai客户端初始化成功")

        if self.api_keys.get("openrouter"):
            self.clients["openrouter"] = "utils_api"
            self.logger.info("OpenRouter客户端初始化成功")

        if self.api_keys.get("siliconflow"):
            self.clients["siliconflow"] = "utils_api"
            self.logger.info("SiliconFlow客户端初始化成功")

        # OpenAI客户端
        if OPENAI_AVAILABLE and self.api_keys.get("openai"):
            try:
                self.clients["openai"] = openai.OpenAI(
                    api_key=self.api_keys["openai"],
                    timeout=self.timeout,
                )
                self.logger.info("OpenAI客户端初始化成功")
            except Exception as e:
                self.logger.error(f"OpenAI客户端初始化失败: {e}")

        # Anthropic客户端
        if ANTHROPIC_AVAILABLE and self.api_keys.get("anthropic"):
            try:
                self.clients["anthropic"] = anthropic.Anthropic(
                    api_key=self.api_keys["anthropic"],
                    timeout=self.timeout,
                )
                self.logger.info("Anthropic客户端初始化成功")
            except Exception as e:
                self.logger.error(f"Anthropic客户端初始化失败: {e}")

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
                    timeout=self.timeout,
                )
                self.logger.info("Azure OpenAI客户端初始化成功")
            except Exception as e:
                self.logger.error(f"Azure OpenAI客户端初始化失败: {e}")

    def _get_all_available_models(self) -> list[str]:
        """获取所有可用的模型ID"""
        available_models = []
        for provider, models in self.models_config.items():
            if provider in self.clients:
                for model_name in models.keys():
                    model_id = f"{provider}:{model_name}"
                    available_models.append(model_id)
        return available_models

    def _select_initial_model(self):
        """选择初始模型"""
        available_models = self._get_all_available_models()

        if not available_models:
            self.logger.error("没有可用的模型")
            return

        # 优先选择上次成功的模型
        best_model = None
        best_score = -1

        for model_id in available_models:
            if model_id not in self.model_status:
                # 初始化新模型状态
                provider = model_id.split(":", 1)[0]
                self.model_status[model_id] = ModelStatus(
                    model_id=model_id,
                    provider=provider,
                    is_available=True,
                    last_success=None,
                    last_failure=None,
                    consecutive_failures=0,
                    total_calls=0,
                    success_rate=1.0,
                    avg_response_time=0.0,
                )

            status = self.model_status[model_id]

            # 跳过不可用的模型
            if not self._is_model_available(model_id):
                continue

            # 计算模型评分（成功率 + 响应时间权重）
            score = (
                status.success_rate * 0.7
                + (1.0 / max(status.avg_response_time, 0.1)) * 0.3
            )

            if score > best_score:
                best_score = score
                best_model = model_id

        if best_model:
            self.current_model = best_model
            self.fallback_models = [m for m in available_models if m != best_model]
            self.logger.info(f"选择初始模型: {self.current_model}")
        else:
            self.logger.error("没有可用的模型")

    def _is_model_available(self, model_id: str) -> bool:
        """检查模型是否可用"""
        if model_id not in self.model_status:
            return True  # 新模型默认可用

        status = self.model_status[model_id]

        # 检查连续失败次数
        if status.consecutive_failures >= self.max_consecutive_failures:
            # 检查是否过了冷却时间
            if (
                status.last_failure
                and datetime.now() - status.last_failure < self.failure_cooldown
            ):
                return False

        return status.is_available

    def _update_model_status(
        self,
        model_id: str,
        success: bool,
        response_time: float,
        error: str = None,
    ):
        """更新模型状态"""
        if model_id not in self.model_status:
            provider = model_id.split(":", 1)[0]
            self.model_status[model_id] = ModelStatus(
                model_id=model_id,
                provider=provider,
                is_available=True,
                last_success=None,
                last_failure=None,
                consecutive_failures=0,
                total_calls=0,
                success_rate=1.0,
                avg_response_time=0.0,
            )

        status = self.model_status[model_id]
        status.total_calls += 1

        if success:
            status.last_success = datetime.now()
            status.consecutive_failures = 0
            status.is_available = True
        else:
            status.last_failure = datetime.now()
            status.consecutive_failures += 1
            status.last_error = error

            # 如果连续失败次数过多，标记为不可用
            if status.consecutive_failures >= self.max_consecutive_failures:
                status.is_available = False

        # 更新成功率
        if status.total_calls > 0:
            success_count = status.total_calls - status.consecutive_failures
            status.success_rate = success_count / status.total_calls

        # 更新平均响应时间
        if status.avg_response_time == 0:
            status.avg_response_time = response_time
        else:
            status.avg_response_time = (status.avg_response_time + response_time) / 2

        # 保存状态
        self._save_model_status()

    def _switch_to_next_model(self):
        """切换到下一个可用模型"""
        available_fallbacks = [
            m for m in self.fallback_models if self._is_model_available(m)
        ]

        if available_fallbacks:
            old_model = self.current_model
            self.current_model = available_fallbacks[0]
            self.fallback_models = [
                m for m in self.fallback_models if m != self.current_model
            ]
            if old_model:
                self.fallback_models.append(old_model)

            self.logger.warning(f"切换模型: {old_model} -> {self.current_model}")
            return True
        else:
            self.logger.error("没有可用的备用模型")
            return False

    async def call_model_with_fallback(
        self,
        prompt: str,
        max_retries: int = 3,
        **kwargs,
    ) -> ModelResponse:
        """调用模型，支持自动故障转移"""
        if not self.current_model:
            return ModelResponse(
                model_id="",
                provider="",
                content="",
                tokens_used=0,
                response_time=0,
                success=False,
                error="没有可用的模型",
            )

        for attempt in range(max_retries):
            try:
                response = await self._call_single_model(
                    self.current_model,
                    prompt,
                    **kwargs,
                )

                if response.success:
                    self._update_model_status(
                        self.current_model,
                        True,
                        response.response_time,
                    )
                    return response
                else:
                    self._update_model_status(
                        self.current_model,
                        False,
                        response.response_time,
                        response.error,
                    )

                    # 如果当前模型失败，尝试切换到备用模型
                    if attempt < max_retries - 1:
                        if self._switch_to_next_model():
                            continue
                        else:
                            break

            except Exception as e:
                self.logger.error(f"调用模型 {self.current_model} 失败: {e}")
                self._update_model_status(self.current_model, False, 0, str(e))

                if attempt < max_retries - 1:
                    if self._switch_to_next_model():
                        continue
                    else:
                        break

        return ModelResponse(
            model_id=self.current_model or "",
            provider=self.current_model.split(":", 1)[0] if self.current_model else "",
            content="",
            tokens_used=0,
            response_time=0,
            success=False,
            error="所有模型调用都失败了",
        )

    async def _call_single_model(
        self,
        model_id: str,
        prompt: str,
        **kwargs,
    ) -> ModelResponse:
        """调用单个模型"""
        provider, model_name = model_id.split(":", 1)

        if provider not in self.clients:
            return ModelResponse(
                model_id=model_id,
                provider=provider,
                content="",
                tokens_used=0,
                response_time=0,
                success=False,
                error=f"Provider {provider} not available",
            )

        model_config = self.models_config[provider][model_name]
        start_time = time.time()

        try:
            if provider == "openai":
                response = await self._call_openai(model_config, prompt, **kwargs)
            elif provider == "anthropic":
                response = await self._call_anthropic(model_config, prompt, **kwargs)
            elif provider == "azure":
                response = await self._call_azure(model_config, prompt, **kwargs)
            elif provider in ["qiniu", "together", "openrouter", "siliconflow"]:
                response = await self._call_utils_api(
                    provider,
                    model_config,
                    prompt,
                    **kwargs,
                )
            else:
                raise ValueError(f"Unsupported provider: {provider}")

            response.model_id = model_id
            response.provider = provider
            response.response_time = time.time() - start_time
            response.success = True

            return response

        except Exception as e:
            return ModelResponse(
                model_id=model_id,
                provider=provider,
                content="",
                tokens_used=0,
                response_time=time.time() - start_time,
                success=False,
                error=str(e),
            )

    async def _call_openai(self, config: dict, prompt: str, **kwargs) -> ModelResponse:
        """调用OpenAI模型"""
        client = self.clients["openai"]

        messages = [{"role": "user", "content": prompt}]

        response = await client.chat.completions.create(
            model=config["model_name"],
            messages=messages,
            max_tokens=kwargs.get("max_tokens", min(config["max_tokens"], 4000)),
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
            success=True,
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
            max_tokens=kwargs.get("max_tokens", min(config["max_tokens"], 4000)),
            temperature=kwargs.get("temperature", config["temperature"]),
            messages=[{"role": "user", "content": prompt}],
        )

        content = response.content[0].text
        tokens_used = response.usage.input_tokens + response.usage.output_tokens

        return ModelResponse(
            model_id="",
            provider="",
            content=content,
            tokens_used=tokens_used,
            response_time=0,
            success=True,
            metadata={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
        )

    async def _call_azure(self, config: dict, prompt: str, **kwargs) -> ModelResponse:
        """调用Azure OpenAI模型"""
        client = self.clients["azure"]

        messages = [{"role": "user", "content": prompt}]

        response = await client.chat.completions.create(
            model=config["model_name"],
            messages=messages,
            max_tokens=kwargs.get("max_tokens", min(config["max_tokens"], 4000)),
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
            success=True,
            metadata={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
            },
        )

    async def _call_utils_api(
        self,
        provider: str,
        config: dict,
        prompt: str,
        **kwargs,
    ) -> ModelResponse:
        """调用utils.py中的API函数"""
        try:
            import os
            import sys

            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            import utils

            # 构建消息格式
            messages = [{"role": "user", "content": prompt}]

            # 构建选项
            options = {
                "temperature": kwargs.get(
                    "temperature",
                    config.get("temperature", 0.7),
                ),
                "max_tokens": kwargs.get("max_tokens", config.get("max_tokens", 4096)),
            }

            # 调用对应的API函数
            if provider == "qiniu":
                model_name = config.get("model_name", "deepseek-v3")
                content, response_message = utils.call_qiniu_deepseek(
                    messages,
                    options,
                    model_name=model_name,
                )
            elif provider == "together":
                model_name = config.get(
                    "model_name",
                    "mistralai/Mixtral-8x7B-Instruct-v0.1",
                )
                content, response_message = utils.call_togetherai(
                    model_name,
                    messages,
                    options,
                )
            elif provider == "openrouter":
                model_name = config.get("model_name", "mistralai/mixtral-8x7b-instruct")
                content, response_message = utils.call_openrouter(
                    model_name,
                    messages,
                    options,
                )
            elif provider == "siliconflow":
                model_name = config.get("model_name", "Qwen/Qwen2.5-7B-Instruct")
                content, response_message = utils.call_siliconflow(
                    model_name,
                    messages,
                    options,
                )
            else:
                raise ValueError(f"Unsupported utils API provider: {provider}")

            # 检查是否成功
            if content and not str(content).startswith("[API Error"):
                # 估算token使用量
                tokens_used = len(prompt.split()) + len(content.split())

                return ModelResponse(
                    model_id="",
                    provider="",
                    content=content,
                    tokens_used=tokens_used,
                    response_time=0,
                    success=True,
                    metadata={"estimated_tokens": True, "provider": provider},
                )
            else:
                return ModelResponse(
                    model_id="",
                    provider="",
                    content="",
                    tokens_used=0,
                    response_time=0,
                    success=False,
                    error=content if content else "API调用失败",
                )

        except Exception as e:
            return ModelResponse(
                model_id="",
                provider="",
                content="",
                tokens_used=0,
                response_time=0,
                success=False,
                error=f"Utils API调用失败: {e!s}",
            )

    def get_current_model_info(self) -> dict[str, Any]:
        """获取当前模型信息"""
        if not self.current_model:
            return {"error": "没有可用的模型"}

        status = self.model_status.get(self.current_model)
        provider, model_name = self.current_model.split(":", 1)
        config = self.models_config[provider][model_name]

        return {
            "current_model": self.current_model,
            "model_name": config["name"],
            "provider": provider,
            "status": status.to_dict() if status else None,
            "fallback_models": self.fallback_models,
        }

    def get_all_model_status(self) -> dict[str, Any]:
        """获取所有模型状态"""
        return {
            model_id: status.to_dict() for model_id, status in self.model_status.items()
        }

    def force_switch_model(self, model_id: str) -> bool:
        """强制切换到指定模型"""
        if model_id in self._get_all_available_models():
            old_model = self.current_model
            self.current_model = model_id

            # 重新排列备用模型列表
            self.fallback_models = [
                m for m in self._get_all_available_models() if m != model_id
            ]

            self.logger.info(f"强制切换模型: {old_model} -> {self.current_model}")
            return True
        else:
            self.logger.error(f"模型 {model_id} 不可用")
            return False

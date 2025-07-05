"""模型注册表 - 维护各平台可用模型列表
支持本地Ollama、云端API等多种模型平台的状态检测和管理
"""

import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import aiohttp


class ModelInfo:
    """模型信息"""

    def __init__(
        self,
        name: str,
        platform: str,
        size: str = "",
        status: str = "unknown",
        last_check: str = "",
        model_type: str = "chat",
    ):
        self.name = name
        self.platform = platform
        self.size = size
        self.status = status  # available, unavailable, unknown
        self.last_check = last_check or datetime.now().isoformat()
        self.model_type = model_type  # chat, embedding
        self.metadata = {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "platform": self.platform,
            "size": self.size,
            "status": self.status,
            "last_check": self.last_check,
            "model_type": self.model_type,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ModelInfo":
        model = cls(
            name=data["name"],
            platform=data["platform"],
            size=data.get("size", ""),
            status=data.get("status", "unknown"),
            last_check=data.get("last_check", ""),
            model_type=data.get("model_type", "chat"),
        )
        model.metadata = data.get("metadata", {})
        return model


class ModelRegistry:
    """模型注册表 - 管理所有平台的模型状态"""

    def __init__(self, registry_file: str = "data/model_registry.json"):
        self.registry_file = Path(registry_file)
        self.models: dict[str, ModelInfo] = {}
        self.logger = logging.getLogger(__name__)

        # 确保数据目录存在
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)

        # 加载现有注册表
        self.load_registry()

    def load_registry(self):
        """加载模型注册表"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, encoding="utf-8") as f:
                    data = json.load(f)

                self.models = {}
                for model_data in data.get("models", []):
                    model = ModelInfo.from_dict(model_data)
                    self.models[f"{model.platform}:{model.name}"] = model

                self.logger.info(f"Loaded {len(self.models)} models from registry")

            except Exception as e:
                self.logger.error(f"Failed to load model registry: {e}")
                self.models = {}
        else:
            self.logger.info("No existing model registry found, starting fresh")
            self.models = {}

    def save_registry(self):
        """保存模型注册表"""
        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "models": [model.to_dict() for model in self.models.values()],
            }

            with open(self.registry_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Saved {len(self.models)} models to registry")

        except Exception as e:
            self.logger.error(f"Failed to save model registry: {e}")

    def add_model(self, model: ModelInfo):
        """添加模型到注册表"""
        key = f"{model.platform}:{model.name}"
        self.models[key] = model
        self.logger.debug(f"Added model: {key}")

    def get_models_by_platform(self, platform: str) -> list[ModelInfo]:
        """获取指定平台的所有模型"""
        return [model for model in self.models.values() if model.platform == platform]

    def get_available_models(self, platform: Optional[str] = None) -> list[ModelInfo]:
        """获取可用的模型"""
        models = self.models.values()
        if platform:
            models = [m for m in models if m.platform == platform]
        return [m for m in models if m.status == "available"]

    def update_model_status(self, platform: str, name: str, status: str):
        """更新模型状态"""
        key = f"{platform}:{name}"
        if key in self.models:
            self.models[key].status = status
            self.models[key].last_check = datetime.now().isoformat()
            self.logger.debug(f"Updated model status: {key} -> {status}")

    async def check_ollama_models(
        self,
        base_url: str = "http://localhost:11434",
    ) -> list[ModelInfo]:
        """检查Ollama本地模型（排除嵌入式模型）"""
        models = []

        # 嵌入式模型列表（需要排除的）
        embedding_models = [
            "all-minilm",
            "mxbai-embed",
            "nomic-embed",
            "bge-",
            "gte-",
            "e5-",
            "multilingual-e5",
            "paraphrase-",
            "sentence-transformers",
        ]

        try:
            # 方法1: 使用ollama list命令
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                for line in lines[1:]:  # 跳过标题行
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 3:
                            name = parts[0]
                            size = parts[2] if len(parts) > 2 else ""

                            # 检查是否为嵌入式模型
                            is_embedding = any(
                                embed_name in name.lower()
                                for embed_name in embedding_models
                            )
                            if is_embedding:
                                self.logger.debug(f"跳过嵌入式模型: {name}")
                                continue

                            model = ModelInfo(
                                name=name,
                                platform="ollama",
                                size=size,
                                status="available",
                                model_type="chat",
                            )
                            models.append(model)
                            self.add_model(model)

                self.logger.info(f"Found {len(models)} Ollama chat models via CLI")

            else:
                self.logger.warning("Ollama CLI not available, trying API")
                # 方法2: 使用API
                models = await self._check_ollama_api(base_url)

        except subprocess.TimeoutExpired:
            self.logger.warning("Ollama CLI timeout, trying API")
            models = await self._check_ollama_api(base_url)
        except FileNotFoundError:
            self.logger.warning("Ollama CLI not found, trying API")
            models = await self._check_ollama_api(base_url)
        except Exception as e:
            self.logger.error(f"Failed to check Ollama models: {e}")
            # 标记现有Ollama模型为不可用
            for model in self.get_models_by_platform("ollama"):
                self.update_model_status("ollama", model.name, "unavailable")

        return models

    async def _check_ollama_api(self, base_url: str) -> list[ModelInfo]:
        """通过API检查Ollama模型（排除嵌入式模型）"""
        models = []

        # 嵌入式模型列表（需要排除的）
        embedding_models = [
            "all-minilm",
            "mxbai-embed",
            "nomic-embed",
            "bge-",
            "gte-",
            "e5-",
            "multilingual-e5",
            "paraphrase-",
            "sentence-transformers",
        ]

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{base_url}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        for model_data in data.get("models", []):
                            name = model_data.get("name", "")
                            size = model_data.get("size", 0)
                            size_str = (
                                self._format_size(size)
                                if isinstance(size, int)
                                else str(size)
                            )

                            # 检查是否为嵌入式模型
                            is_embedding = any(
                                embed_name in name.lower()
                                for embed_name in embedding_models
                            )
                            if is_embedding:
                                self.logger.debug(f"跳过嵌入式模型: {name}")
                                continue

                            model = ModelInfo(
                                name=name,
                                platform="ollama",
                                size=size_str,
                                status="available",
                                model_type="chat",
                            )
                            model.metadata = {
                                "modified_at": model_data.get("modified_at", ""),
                                "digest": model_data.get("digest", ""),
                            }
                            models.append(model)
                            self.add_model(model)

                        self.logger.info(
                            f"Found {len(models)} Ollama chat models via API",
                        )
                    else:
                        self.logger.warning(
                            f"Ollama API returned status {response.status}",
                        )

        except Exception as e:
            self.logger.error(f"Failed to check Ollama API: {e}")
            # 标记现有Ollama模型为不可用
            for model in self.get_models_by_platform("ollama"):
                self.update_model_status("ollama", model.name, "unavailable")

        return models

    async def check_openai_models(self, api_key: str) -> list[ModelInfo]:
        """检查OpenAI模型"""
        models = []

        if not api_key:
            self.logger.warning("No OpenAI API key provided")
            return models

        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.openai.com/v1/models",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        # 只关注聊天模型
                        chat_models = [
                            "gpt-4",
                            "gpt-4-turbo",
                            "gpt-4o",
                            "gpt-4o-mini",
                            "gpt-3.5-turbo",
                            "gpt-3.5-turbo-16k",
                        ]

                        for model_data in data.get("data", []):
                            model_id = model_data.get("id", "")
                            if any(
                                chat_model in model_id for chat_model in chat_models
                            ):
                                model = ModelInfo(
                                    name=model_id,
                                    platform="openai",
                                    status="available",
                                    model_type="chat",
                                )
                                model.metadata = {
                                    "created": model_data.get("created", ""),
                                    "owned_by": model_data.get("owned_by", ""),
                                }
                                models.append(model)
                                self.add_model(model)

                        self.logger.info(f"Found {len(models)} OpenAI models")
                    else:
                        self.logger.warning(
                            f"OpenAI API returned status {response.status}",
                        )

        except Exception as e:
            self.logger.error(f"Failed to check OpenAI models: {e}")
            # 标记现有OpenAI模型为不可用
            for model in self.get_models_by_platform("openai"):
                self.update_model_status("openai", model.name, "unavailable")

        return models

    async def check_siliconflow_models(self, api_key: str) -> list[ModelInfo]:
        """检查SiliconFlow模型"""
        models = []

        if not api_key:
            self.logger.warning("No SiliconFlow API key provided")
            return models

        # SiliconFlow已知可用模型
        known_models = [
            "internlm/internlm2_5-7b-chat",
            "THUDM/glm-4-9b-chat",
            "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B",
            "Qwen/Qwen3-8B",
        ]

        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

            # 测试一个简单的请求来验证API密钥
            test_payload = {
                "model": known_models[0],
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 1,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.siliconflow.cn/v1/chat/completions",
                    headers=headers,
                    json=test_payload,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status in [200, 400]:  # 400也表示API可用，只是请求格式问题
                        # API可用，添加已知模型
                        for model_name in known_models:
                            model = ModelInfo(
                                name=model_name,
                                platform="siliconflow",
                                status="available",
                                model_type="chat",
                            )
                            models.append(model)
                            self.add_model(model)

                        self.logger.info(
                            f"SiliconFlow API available, added {len(models)} known models",
                        )
                    else:
                        self.logger.warning(
                            f"SiliconFlow API returned status {response.status}",
                        )

        except Exception as e:
            self.logger.error(f"Failed to check SiliconFlow models: {e}")
            # 标记现有SiliconFlow模型为不可用
            for model in self.get_models_by_platform("siliconflow"):
                self.update_model_status("siliconflow", model.name, "unavailable")

        return models

    async def check_qiniu_models(
        self,
        api_key: str,
        api_url: str = "https://api.qnaigc.com/v1/chat/completions",
    ) -> list[ModelInfo]:
        """检查七牛云模型"""
        models = []

        if not api_key:
            self.logger.warning("No QINIU API key provided")
            return models

        # 七牛云已知模型
        known_models = ["deepseek-chat", "deepseek-coder", "gpt-3.5-turbo", "gpt-4"]

        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

            # 测试一个简单的请求来验证API密钥
            test_payload = {
                "model": known_models[0],
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 1,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    api_url,
                    headers=headers,
                    json=test_payload,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status in [200, 400]:  # 400也表示API可用，只是请求格式问题
                        # API可用，添加已知模型
                        for model_name in known_models:
                            model = ModelInfo(
                                name=model_name,
                                platform="qiniu",
                                status="available",
                                model_type="chat",
                            )
                            models.append(model)
                            self.add_model(model)

                        self.logger.info(
                            f"QINIU API available, added {len(models)} known models",
                        )
                    else:
                        self.logger.warning(
                            f"QINIU API returned status {response.status}",
                        )

        except Exception as e:
            self.logger.error(f"Failed to check QINIU models: {e}")
            # 标记现有QINIU模型为不可用
            for model in self.get_models_by_platform("qiniu"):
                self.update_model_status("qiniu", model.name, "unavailable")

        return models

    async def check_together_models(
        self,
        api_key: str,
        api_url: str = "https://api.together.xyz/v1/chat/completions",
    ) -> list[ModelInfo]:
        """检查Together.ai模型"""
        models = []

        if not api_key:
            self.logger.warning("No Together.ai API key provided")
            return models

        # Together.ai已知模型
        known_models = [
            "meta-llama/Llama-2-70b-chat-hf",
            "meta-llama/Llama-2-13b-chat-hf",
            "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO",
            "togethercomputer/RedPajama-INCITE-Chat-3B-v1",
        ]

        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

            # 测试一个简单的请求来验证API密钥
            test_payload = {
                "model": known_models[0],
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 1,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    api_url,
                    headers=headers,
                    json=test_payload,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status in [200, 400]:  # 400也表示API可用
                        # API可用，添加已知模型
                        for model_name in known_models:
                            model = ModelInfo(
                                name=model_name,
                                platform="together",
                                status="available",
                                model_type="chat",
                            )
                            models.append(model)
                            self.add_model(model)

                        self.logger.info(
                            f"Together.ai API available, added {len(models)} known models",
                        )
                    else:
                        self.logger.warning(
                            f"Together.ai API returned status {response.status}",
                        )

        except Exception as e:
            self.logger.error(f"Failed to check Together.ai models: {e}")
            # 标记现有Together模型为不可用
            for model in self.get_models_by_platform("together"):
                self.update_model_status("together", model.name, "unavailable")

        return models

    async def check_openrouter_models(
        self,
        api_key: str,
        api_url: str = "https://openrouter.ai/api/v1/chat/completions",
    ) -> list[ModelInfo]:
        """检查OpenRouter模型"""
        models = []

        if not api_key:
            self.logger.warning("No OpenRouter API key provided")
            return models

        # OpenRouter已知模型
        known_models = [
            "openai/gpt-4-turbo",
            "openai/gpt-3.5-turbo",
            "anthropic/claude-3-opus",
            "anthropic/claude-3-sonnet",
            "meta-llama/llama-2-70b-chat",
            "mistralai/mixtral-8x7b-instruct",
        ]

        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://daip-insight-engine.local",
                "X-Title": "DAIP Insight Engine",
            }

            # 测试一个简单的请求来验证API密钥
            test_payload = {
                "model": known_models[1],  # 使用gpt-3.5-turbo测试
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 1,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    api_url,
                    headers=headers,
                    json=test_payload,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status in [200, 400]:  # 400也表示API可用
                        # API可用，添加已知模型
                        for model_name in known_models:
                            model = ModelInfo(
                                name=model_name,
                                platform="openrouter",
                                status="available",
                                model_type="chat",
                            )
                            models.append(model)
                            self.add_model(model)

                        self.logger.info(
                            f"OpenRouter API available, added {len(models)} known models",
                        )
                    else:
                        self.logger.warning(
                            f"OpenRouter API returned status {response.status}",
                        )

        except Exception as e:
            self.logger.error(f"Failed to check OpenRouter models: {e}")
            # 标记现有OpenRouter模型为不可用
            for model in self.get_models_by_platform("openrouter"):
                self.update_model_status("openrouter", model.name, "unavailable")

        return models

    async def check_anthropic_models(self, api_key: str) -> list[ModelInfo]:
        """检查Anthropic模型"""
        models = []

        if not api_key:
            self.logger.warning("No Anthropic API key provided")
            return models

        # Anthropic已知模型
        known_models = [
            "claude-3-5-sonnet-20241022",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ]

        try:
            headers = {
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
            }

            # 测试API可用性
            test_payload = {
                "model": known_models[0],
                "max_tokens": 1,
                "messages": [{"role": "user", "content": "test"}],
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=test_payload,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status in [200, 400]:  # 400也表示API可用
                        # API可用，添加已知模型
                        for model_name in known_models:
                            model = ModelInfo(
                                name=model_name,
                                platform="anthropic",
                                status="available",
                                model_type="chat",
                            )
                            models.append(model)
                            self.add_model(model)

                        self.logger.info(
                            f"Anthropic API available, added {len(models)} known models",
                        )
                    else:
                        self.logger.warning(
                            f"Anthropic API returned status {response.status}",
                        )

        except Exception as e:
            self.logger.error(f"Failed to check Anthropic models: {e}")
            # 标记现有Anthropic模型为不可用
            for model in self.get_models_by_platform("anthropic"):
                self.update_model_status("anthropic", model.name, "unavailable")

        return models

    async def check_local_embedding_models(
        self,
        base_url: str = "http://localhost:11434",
    ) -> list[ModelInfo]:
        """检查本地嵌入式模型（用于向量数据库）"""
        models = []

        # 本地嵌入式模型列表
        embedding_models = [
            "nomic-embed-text:latest",
            "mxbai-embed-large:latest",
            "all-minilm:latest",
            "bge-large:latest",
            "gte-large:latest",
        ]

        try:
            # 方法1: 使用ollama list命令
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                available_models = []
                for line in lines[1:]:  # 跳过标题行
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 1:
                            available_models.append(parts[0])

                # 检查哪些嵌入式模型可用
                for embed_model in embedding_models:
                    if embed_model in available_models:
                        model = ModelInfo(
                            name=embed_model,
                            platform="ollama",
                            status="available",
                            model_type="embedding",
                        )
                        models.append(model)
                        self.add_model(model)
                        self.logger.info(f"Found local embedding model: {embed_model}")

                self.logger.info(f"Found {len(models)} local embedding models via CLI")

            else:
                self.logger.warning("Ollama CLI not available, trying API")
                # 方法2: 使用API
                models = await self._check_local_embedding_api(
                    base_url,
                    embedding_models,
                )

        except subprocess.TimeoutExpired:
            self.logger.warning("Ollama CLI timeout, trying API")
            models = await self._check_local_embedding_api(base_url, embedding_models)
        except FileNotFoundError:
            self.logger.warning("Ollama CLI not found, trying API")
            models = await self._check_local_embedding_api(base_url, embedding_models)
        except Exception as e:
            self.logger.error(f"Failed to check local embedding models: {e}")

        return models

    async def _check_local_embedding_api(
        self,
        base_url: str,
        embedding_models: list[str],
    ) -> list[ModelInfo]:
        """通过API检查本地嵌入式模型"""
        models = []

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{base_url}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        available_models = [
                            model_data.get("name", "")
                            for model_data in data.get("models", [])
                        ]

                        # 检查哪些嵌入式模型可用
                        for embed_model in embedding_models:
                            if embed_model in available_models:
                                model = ModelInfo(
                                    name=embed_model,
                                    platform="ollama",
                                    status="available",
                                    model_type="embedding",
                                )
                                models.append(model)
                                self.add_model(model)
                                self.logger.info(
                                    f"Found local embedding model: {embed_model}",
                                )

                        self.logger.info(
                            f"Found {len(models)} local embedding models via API",
                        )
                    else:
                        self.logger.warning(
                            f"Ollama API returned status {response.status}",
                        )

        except Exception as e:
            self.logger.error(f"Failed to check local embedding API: {e}")

        return models

    async def check_cloud_embedding_models(
        self,
        config: dict[str, Any] = None,
    ) -> list[ModelInfo]:
        """检查云端嵌入式模型"""
        models = []
        config = config or {}

        # OpenAI 嵌入式模型
        if config.get("openai_api_key"):
            openai_embedding_models = [
                "text-embedding-3-small",
                "text-embedding-3-large",
                "text-embedding-ada-002",
            ]

            try:
                headers = {
                    "Authorization": f"Bearer {config['openai_api_key']}",
                    "Content-Type": "application/json",
                }

                async with aiohttp.ClientSession() as session:
                    # 测试API可用性
                    async with session.get(
                        "https://api.openai.com/v1/models",
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as response:
                        if response.status == 200:
                            for model_name in openai_embedding_models:
                                model = ModelInfo(
                                    name=model_name,
                                    platform="openai",
                                    status="available",
                                    model_type="embedding",
                                )
                                models.append(model)
                                self.add_model(model)

                            self.logger.info(
                                f"Added {len(openai_embedding_models)} OpenAI embedding models",
                            )

            except Exception as e:
                self.logger.error(f"Failed to check OpenAI embedding models: {e}")

        # SiliconFlow 嵌入式模型
        if config.get("siliconflow_api_key"):
            siliconflow_embedding_models = [
                "BAAI/bge-large-zh-v1.5",
                "netease-youdao/bce-reranker-base_v1",
            ]

            try:
                for model_name in siliconflow_embedding_models:
                    model = ModelInfo(
                        name=model_name,
                        platform="siliconflow",
                        status="available",
                        model_type="embedding",
                    )
                    models.append(model)
                    self.add_model(model)

                self.logger.info(
                    f"Added {len(siliconflow_embedding_models)} SiliconFlow embedding models",
                )

            except Exception as e:
                self.logger.error(f"Failed to check SiliconFlow embedding models: {e}")

        return models

    async def refresh_all_models(self, config: dict[str, Any] = None):
        """刷新所有平台的模型列表"""
        self.logger.info("Starting model registry refresh...")

        config = config or {}

        # 检查Ollama聊天模型
        await self.check_ollama_models(
            config.get("ollama_base_url", "http://localhost:11434"),
        )

        # 检查本地嵌入式模型（用于向量数据库）
        await self.check_local_embedding_models(
            config.get("ollama_base_url", "http://localhost:11434"),
        )

        # 检查七牛云
        if config.get("qiniu_api_key"):
            await self.check_qiniu_models(
                config["qiniu_api_key"],
                config.get(
                    "qiniu_api_url",
                    "https://api.qnaigc.com/v1/chat/completions",
                ),
            )

        # 检查Together.ai
        if config.get("together_api_key"):
            await self.check_together_models(
                config["together_api_key"],
                config.get(
                    "together_api_url",
                    "https://api.together.xyz/v1/chat/completions",
                ),
            )

        # 检查OpenRouter
        if config.get("openrouter_api_key"):
            await self.check_openrouter_models(
                config["openrouter_api_key"],
                config.get(
                    "openrouter_api_url",
                    "https://openrouter.ai/api/v1/chat/completions",
                ),
            )

        # 检查SiliconFlow
        if config.get("siliconflow_api_key"):
            await self.check_siliconflow_models(config["siliconflow_api_key"])

        # 检查云端嵌入式模型
        await self.check_cloud_embedding_models(config)

        # 保存注册表
        self.save_registry()

        self.logger.info(
            f"Model registry refresh completed. Total models: {len(self.models)}",
        )

    def get_registry_summary(self) -> dict[str, Any]:
        """获取注册表摘要"""
        summary = {
            "total_models": len(self.models),
            "platforms": {},
            "available_count": 0,
            "last_updated": datetime.now().isoformat(),
        }

        for model in self.models.values():
            platform = model.platform
            if platform not in summary["platforms"]:
                summary["platforms"][platform] = {
                    "total": 0,
                    "available": 0,
                    "models": [],
                }

            summary["platforms"][platform]["total"] += 1
            summary["platforms"][platform]["models"].append(
                {"name": model.name, "status": model.status, "size": model.size},
            )

            if model.status == "available":
                summary["platforms"][platform]["available"] += 1
                summary["available_count"] += 1

        return summary

    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}PB"

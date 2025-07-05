"""云端聊天模型管理器 - 支持多模型轮流和自动回退
"""
import json
import logging
import random
import time
from typing import Any, Optional

logger = logging.getLogger(__name__)


class CloudChatManager:
    def __init__(self, config_path: str = "config/model_config.json"):
        self.config = self._load_config(config_path)
        self.cloud_models = self._load_cloud_models()
        self.current_model_index = 0
        self.model_rotation = self.config.get("model_rotation", True)
        self.auto_fallback = self.config.get("auto_fallback", True)
        self.model_status = {}
        self.last_rotation = time.time()

    def _load_config(self, config_path: str) -> dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return {}

    def _load_cloud_models(self) -> dict[str, Any]:
        """加载云端模型配置"""
        try:
            with open("config/cloud_models.json", encoding="utf-8") as f:
                cloud_config = json.load(f)
                return cloud_config.get("cloud_models", {})
        except Exception as e:
            logger.error(f"加载云端模型配置失败: {e}")
            return {}

    def get_available_models(self) -> list[str]:
        """获取可用的云端模型列表"""
        available_models = []
        for provider, models in self.cloud_models.items():
            for model_id, model_config in models.items():
                model_key = f"{provider}/{model_id}"
                if (
                    self.model_status.get(model_key, {}).get("status", "unknown")
                    != "failed"
                ):
                    available_models.append(model_key)
        return available_models

    def get_next_model(self) -> Optional[str]:
        """获取下一个要使用的模型"""
        available_models = self.get_available_models()
        if not available_models:
            logger.warning("没有可用的云端模型")
            return None

        if self.model_rotation:
            # 轮流使用模型
            self.current_model_index = (self.current_model_index + 1) % len(
                available_models,
            )
            return available_models[self.current_model_index]
        else:
            # 随机选择模型
            return random.choice(available_models)

    def get_model_config(self, model_key: str) -> Optional[dict[str, Any]]:
        """获取模型配置"""
        try:
            provider, model_id = model_key.split("/", 1)
            return self.cloud_models.get(provider, {}).get(model_id)
        except Exception as e:
            logger.error(f"获取模型配置失败 {model_key}: {e}")
            return None

    async def chat(self, message: str, user_id: str = "default_user") -> str:
        """使用云端模型进行对话"""
        max_retries = len(self.get_available_models()) if self.auto_fallback else 1

        for attempt in range(max_retries):
            model_key = self.get_next_model()
            if not model_key:
                return "抱歉，当前没有可用的云端模型，请稍后重试。"

            try:
                response = await self._call_cloud_model(model_key, message, user_id)
                if response:
                    # 标记模型为可用
                    self.model_status[model_key] = {
                        "status": "success",
                        "last_used": time.time(),
                        "error_count": 0,
                    }
                    return response

            except Exception as e:
                logger.error(f"模型 {model_key} 调用失败: {e}")
                # 标记模型为失败
                self.model_status[model_key] = {
                    "status": "failed",
                    "last_error": str(e),
                    "error_count": self.model_status.get(model_key, {}).get(
                        "error_count",
                        0,
                    )
                    + 1,
                }

                if not self.auto_fallback:
                    break

        return "抱歉，所有云端模型都无法使用，请稍后重试。"

    async def _call_cloud_model(
        self,
        model_key: str,
        message: str,
        user_id: str,
    ) -> str:
        """调用具体的云端模型"""
        model_config = self.get_model_config(model_key)
        if not model_config:
            raise Exception(f"模型配置不存在: {model_key}")

        provider = model_config.get("provider")
        api_type = model_config.get("api_type")

        if provider == "siliconflow":
            return await self._call_siliconflow(model_config, message)
        elif provider == "qiniu":
            return await self._call_qiniu(model_config, message)
        elif provider == "openai":
            return await self._call_openai(model_config, message)
        elif provider == "anthropic":
            return await self._call_anthropic(model_config, message)
        else:
            raise Exception(f"不支持的模型提供商: {provider}")

    async def _call_siliconflow(
        self,
        model_config: dict[str, Any],
        message: str,
    ) -> str:
        """调用SiliconFlow模型"""
        try:
            # 这里需要实际的API密钥和端点
            # 暂时返回模拟响应
            return f"[SiliconFlow {model_config.get('model_name', 'Unknown')}] 收到您的消息：{message}\n\n这是一个模拟的云端模型响应。"
        except Exception as e:
            raise Exception(f"SiliconFlow调用失败: {e}")

    async def _call_qiniu(self, model_config: dict[str, Any], message: str) -> str:
        """调用七牛云模型"""
        try:
            # 这里需要实际的API密钥和端点
            # 暂时返回模拟响应
            return f"[七牛云 {model_config.get('model_name', 'Unknown')}] 收到您的消息：{message}\n\n这是一个模拟的云端模型响应。"
        except Exception as e:
            raise Exception(f"七牛云调用失败: {e}")

    async def _call_openai(self, model_config: dict[str, Any], message: str) -> str:
        """调用OpenAI模型"""
        try:
            # 这里需要实际的API密钥和端点
            # 暂时返回模拟响应
            return f"[OpenAI {model_config.get('model_name', 'Unknown')}] 收到您的消息：{message}\n\n这是一个模拟的云端模型响应。"
        except Exception as e:
            raise Exception(f"OpenAI调用失败: {e}")

    async def _call_anthropic(self, model_config: dict[str, Any], message: str) -> str:
        """调用Anthropic模型"""
        try:
            # 这里需要实际的API密钥和端点
            # 暂时返回模拟响应
            return f"[Anthropic {model_config.get('model_name', 'Unknown')}] 收到您的消息：{message}\n\n这是一个模拟的云端模型响应。"
        except Exception as e:
            raise Exception(f"Anthropic调用失败: {e}")

    def get_status(self) -> dict[str, Any]:
        """获取管理器状态"""
        return {
            "model_rotation": self.model_rotation,
            "auto_fallback": self.auto_fallback,
            "available_models": self.get_available_models(),
            "current_model_index": self.current_model_index,
            "model_status": self.model_status,
            "total_models": len(self.get_available_models()),
        }


# 全局实例
cloud_chat_manager = None


def get_cloud_chat_manager() -> CloudChatManager:
    """获取全局云端聊天管理器实例"""
    global cloud_chat_manager
    if cloud_chat_manager is None:
        cloud_chat_manager = CloudChatManager()
    return cloud_chat_manager

"""
Model manager for Ollama CLI commands.
Connects to a local Ollama service to list models and query model info.
"""

from typing import Any

import httpx

OLLAMA_BASE_URL = "http://127.0.0.1:11434"


def _format_size(size_bytes: int) -> str:
    """将字节数格式化为人类可读大小。"""
    size_gb = size_bytes / (1024**3)
    return f"{size_gb:.2f}GB"


def _format_modified(modified_at) -> str:
    """将 Ollama 的 modified_at（ISO 8601 字符串或 Unix 时间戳）格式化为日期。"""
    from datetime import datetime, timezone

    if not modified_at:
        return "Unknown"
    try:
        # Ollama 返回 ISO 8601 字符串（含时区）
        if isinstance(modified_at, str):
            dt = datetime.fromisoformat(modified_at.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.strftime("%Y-%m-%d")
        # 兼容 Unix 时间戳（int/float）
        return datetime.fromtimestamp(modified_at, tz=timezone.utc).strftime(
            "%Y-%m-%d"
        )
    except (OSError, ValueError, OverflowError, TypeError):
        return "Unknown"


class ModelManager:
    """Manage available Ollama models via the Ollama HTTP API."""

    def __init__(self, base_url: str = OLLAMA_BASE_URL):
        self.base_url = base_url.rstrip("/")

    def get_available_models(self, force_refresh: bool = False) -> list[dict[str, Any]]:
        """从 Ollama 获取可用模型列表。

        Returns:
            list[dict]: 每个模型含 name/size/family/modified/digest 等字段。
            无法连接 Ollama 时返回空列表（调用方会显示"无模型"）。
        """
        try:
            response = httpx.get(
                f"{self.base_url}/api/tags", timeout=5.0, follow_redirects=True
            )
            response.raise_for_status()
            data = response.json()
            models = data.get("models", [])
            result = []
            for model in models:
                name = model.get("name", "unknown")
                # 解析 family（如 llama3.2 -> llama3）
                family = name.split(":")[0] if ":" in name else name
                result.append(
                    {
                        "name": name,
                        "size": _format_size(model.get("size", 0)),
                        "family": family,
                        "modified": _format_modified(model.get("modified_at", 0)),
                        "digest": model.get("digest", ""),
                        "parameter_size": model.get("details", {}).get(
                            "parameter_size", "Unknown"
                        ),
                        "quantization": model.get("details", {}).get(
                            "quantization_level", "Unknown"
                        ),
                    }
                )
            return result
        except Exception:
            # Ollama 未运行或不可达：返回空，调用方处理提示
            return []

    def get_current_model(self) -> dict[str, Any]:
        """获取当前默认模型（来自 config 或 Ollama 第一个可用模型）。

        Returns:
            dict: 当前模型信息；无可用模型时返回空 dict。
        """
        models = self.get_available_models()
        if not models:
            return {}
        # 优先返回第一个模型作为"当前"（Ollama 无独立 current 概念）
        return models[0]

    def get_model_info(self, model_name: str) -> dict[str, Any]:
        """获取指定模型的详细信息。

        Returns:
            dict: 模型信息；模型不存在或 Ollama 不可达时返回空 dict。
        """
        for model in self.get_available_models():
            if model.get("name") == model_name:
                return model
        return {}

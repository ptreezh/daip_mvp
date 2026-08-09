"""
ModelManager 防回归测试

背景（2026-08-10 生产交付审计）：model_manager.py 是 stub——
get_available_models/get_current_model/get_model_info 全部返回空，
导致 `model list`/`model status`/`model info` 实际不可用。

修复：连接 Ollama /api/tags 真实列表模型。本测试 mock httpx 验证结构。
"""

from unittest.mock import MagicMock, patch

from daip_live.model_manager import ModelManager, _format_size


class TestModelManager:
    def setup_method(self):
        self.manager = ModelManager()

    def test_get_available_models_parses_ollama_tags(self):
        """从 Ollama /api/tags 返回真实模型结构。"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "models": [
                {
                    "name": "llama3.2:latest",
                    "size": 4661224676,
                    "modified_at": 1700000000,
                    "digest": "abc123def456",
                    "details": {
                        "parameter_size": "3.2B",
                        "quantization_level": "Q4_K_M",
                    },
                },
                {"name": "nomic-embed-text", "size": 274302450, "modified_at": 0},
            ]
        }
        with patch("daip_live.model_manager.httpx.get") as mock_get:
            mock_get.return_value = mock_response
            models = self.manager.get_available_models()

        assert len(models) == 2
        assert models[0]["name"] == "llama3.2:latest"
        assert models[0]["family"] == "llama3.2"
        assert "GB" in models[0]["size"]
        assert models[0]["parameter_size"] == "3.2B"
        assert models[1]["modified"] == "Unknown"

    def test_get_available_models_empty_on_conn_error(self):
        """Ollama 不可达时返回空列表（不抛异常）。"""
        with patch("daip_live.model_manager.httpx.get") as mock_get:
            mock_get.side_effect = Exception("connection refused")
            models = self.manager.get_available_models()

        assert models == []

    def test_get_current_model_returns_first(self):
        """get_current_model 返回第一个可用模型。"""
        with patch.object(self.manager, "get_available_models") as mock_list:
            mock_list.return_value = [{"name": "llama3", "size": "4GB"}]
            current = self.manager.get_current_model()

        assert current["name"] == "llama3"

    def test_get_current_model_empty_when_no_models(self):
        """无模型时 get_current_model 返回空 dict。"""
        with patch.object(self.manager, "get_available_models") as mock_list:
            mock_list.return_value = []
            current = self.manager.get_current_model()

        assert current == {}

    def test_get_model_info_finds_by_name(self):
        """get_model_info 按名字返回对应模型。"""
        with patch.object(self.manager, "get_available_models") as mock_list:
            mock_list.return_value = [{"name": "mistral", "size": "2GB"}]
            info = self.manager.get_model_info("mistral")

        assert info["name"] == "mistral"

    def test_format_size(self):
        """字节格式化。"""
        assert _format_size(1024**3) == "1.00GB"

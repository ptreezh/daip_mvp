import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
print("sys.path in conftest.py:", sys.path)


import pytest


@pytest.fixture(autouse=True)
def _stub_model_availability_check(monkeypatch):
    """模型可用性检查 stub（Wave 0：调试绕过移除后所有测试共用）。

    生产代码已恢复真实模型检查；测试环境无 Ollama 服务，
    故在此统一 stub 为可用，避免测试真实连接 localhost:11434。
    需要验证检查失败路径的测试应局部覆盖该 stub。
    """

    async def _ok(*_args, **_kwargs):
        return (True, "ok")

    monkeypatch.setattr(
        "daip_live.p8_debate_system.enhanced_debate_manager.perform_model_check",
        _ok,
    )
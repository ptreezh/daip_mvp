import sys
import os

# 测试环境禁用 litellm 远程成本表拉取（无外网时 read timeout 会挂起测试）
os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")

# Add the src directory to the Python path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)


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


@pytest.fixture(scope="session", autouse=True)
def _protect_root_db():
    """数据隔离保护（S3-2，2026-08-09）。

    任何测试若写入项目根 daip_live.db（如 08-08 曾致 611 条真实对话轮次
    被清空），本 fixture 会在测试会话结束时以 SHA-256 前后比对立即暴露。
    测试必须使用 :memory: 或临时 DB，禁止触碰项目根数据库。
    """
    import hashlib

    db_path = os.path.abspath("daip_live.db")

    def _hash():
        if not os.path.exists(db_path):
            return None
        with open(db_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    before = _hash()
    yield
    after = _hash()
    assert after == before, (
        "数据隔离保护触发：测试污染了项目根 daip_live.db（会话前后 hash 不一致）。"
        "请改用 :memory: 或临时 DB，禁止测试写入项目根数据库。"
    )

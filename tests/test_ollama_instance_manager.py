"""
OllamaInstanceManager测试用例
测试单一Ollama实例的分时复用功能
"""

import asyncio

import pytest


class TestOllamaInstanceManager:
    """Ollama实例管理器测试"""

    def test_ollama_manager_initialization(self):
        """测试Ollama管理器初始化"""
        from daip_live.p8_debate_system.ollama_instance_manager import (
            OllamaInstanceManager,
        )

        manager = OllamaInstanceManager()

        assert manager._current_model is None
        assert manager._lock is not None
        assert isinstance(manager._lock, asyncio.Lock)

    @pytest.mark.asyncio
    async def test_single_model_generation(self):
        """测试单一模型生成"""
        from daip_live.p8_debate_system.ollama_instance_manager import (
            OllamaInstanceManager,
        )

        manager = OllamaInstanceManager()

        # Mock the internal _generate method
        expected_response = "Test response"
        expected_usage = {"total_tokens": 100}

        async def mock_generate(prompt, **kwargs):
            await asyncio.sleep(0.01)  # 模拟异步延迟
            return expected_response, expected_usage

        manager._generate = mock_generate

        # 测试生成
        response, usage = await manager.generate_with_model(
            "test_model", "Test prompt", temperature=0.7
        )

        assert response == expected_response
        assert usage == expected_usage
        assert manager._current_model == "test_model"

    @pytest.mark.asyncio
    async def test_model_switching(self):
        """测试模型切换功能"""
        from daip_live.p8_debate_system.ollama_instance_manager import (
            OllamaInstanceManager,
        )

        manager = OllamaInstanceManager()

        responses = {}
        usages = {}

        async def mock_generate(prompt, **kwargs):
            model = manager._current_model
            await asyncio.sleep(0.01)
            responses[model] = f"Response from {model}"
            usages[model] = {"total_tokens": 100}
            return responses[model], usages[model]

        manager._generate = mock_generate

        # 测试多个模型调用
        models = ["model1", "model2", "model3"]
        for model in models:
            response, usage = await manager.generate_with_model(
                model, f"Prompt for {model}"
            )
            assert response == f"Response from {model}"
            assert manager._current_model == model

    @pytest.mark.asyncio
    async def test_concurrent_access(self):
        """测试并发访问安全性"""
        from daip_live.p8_debate_system.ollama_instance_manager import (
            OllamaInstanceManager,
        )

        manager = OllamaInstanceManager()

        # Track execution order
        execution_order = []

        async def mock_generate(prompt, **kwargs):
            model = manager._current_model
            execution_order.append(f"start_{model}")
            await asyncio.sleep(0.05)  # 较长的延迟以确保并发
            execution_order.append(f"end_{model}")
            return f"Response from {model}", {"total_tokens": 100}

        manager._generate = mock_generate

        # 并发调用多个模型
        tasks = []
        models = ["model1", "model2", "model3"]
        for model in models:
            task = asyncio.create_task(
                manager.generate_with_model(model, f"Prompt for {model}")
            )
            tasks.append(task)

        # 等待所有任务完成
        results = await asyncio.gather(*tasks)

        # 验证结果
        assert len(results) == 3
        for i, (response, usage) in enumerate(results):
            assert response == f"Response from {models[i]}"

        # 验证执行是顺序的（由于锁机制）
        assert len(execution_order) == 6  # 每个模型开始和结束
        # 检查没有重叠的执行
        for i in range(0, len(execution_order), 2):
            assert execution_order[i].startswith("start_")
            assert execution_order[i + 1].startswith("end_")
            assert (
                execution_order[i].split("_")[1] == execution_order[i + 1].split("_")[1]
            )

    @pytest.mark.asyncio
    async def test_same_model_no_switch(self):
        """测试相同模型不进行切换"""
        from daip_live.p8_debate_system.ollama_instance_manager import (
            OllamaInstanceManager,
        )

        manager = OllamaInstanceManager()

        # 跟踪实际的模型变化
        model_changes = []
        original_switch_model = manager._switch_model

        async def tracking_switch_model(model_name):
            old_model = manager._current_model
            await original_switch_model(model_name)
            new_model = manager._current_model
            if old_model != new_model:
                model_changes.append((old_model, new_model))

        manager._switch_model = tracking_switch_model

        async def mock_generate(prompt, **kwargs):
            return "Response", {"total_tokens": 100}

        manager._generate = mock_generate

        # 多次调用相同模型
        for _ in range(3):
            await manager.generate_with_model("same_model", "Test prompt")

        # 应该只有一次实际的模型变化（从None到same_model）
        assert len(model_changes) == 1
        assert model_changes[0] == (None, "same_model")

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """测试错误处理"""
        from daip_live.core.exceptions import ModelError
        from daip_live.p8_debate_system.ollama_instance_manager import (
            OllamaInstanceManager,
        )

        manager = OllamaInstanceManager()

        async def mock_generate(prompt, **kwargs):
            raise ModelError("Model error")

        manager._generate = mock_generate

        # 测试错误传播
        with pytest.raises(ModelError, match="Model error"):
            await manager.generate_with_model("test_model", "Test prompt")

    @pytest.mark.asyncio
    async def test_model_state_persistence(self):
        """测试模型状态持久化"""
        from daip_live.p8_debate_system.ollama_instance_manager import (
            OllamaInstanceManager,
        )

        manager = OllamaInstanceManager()

        async def mock_generate(prompt, **kwargs):
            return "Response", {"total_tokens": 100}

        manager._generate = mock_generate

        # 使用不同模型
        await manager.generate_with_model("model1", "Prompt 1")
        assert manager._current_model == "model1"

        await manager.generate_with_model("model2", "Prompt 2")
        assert manager._current_model == "model2"

        # 再次使用model1
        await manager.generate_with_model("model1", "Prompt 3")
        assert manager._current_model == "model1"

    def test_lock_mechanism(self):
        """测试锁机制"""
        from daip_live.p8_debate_system.ollama_instance_manager import (
            OllamaInstanceManager,
        )

        manager = OllamaInstanceManager()

        # 验证锁存在
        assert hasattr(manager, "_lock")
        assert isinstance(manager._lock, asyncio.Lock)

        # 验证锁没有被获取
        assert not manager._lock.locked()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

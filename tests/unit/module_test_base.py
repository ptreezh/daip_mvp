"""
模块测试基类

提供标准化的模块测试框架，减少重复代码和提高测试一致性。
"""

import os
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest


class ModuleTestBase(ABC):
    """模块测试基类"""

    @pytest.fixture
    def mock_dependencies(self) -> dict[str, Any]:
        """模拟依赖项"""
        return {
            "container": Mock(),
            "config": Mock(),
            "logger": Mock(),
            "event_bus": Mock(),
            "model_provider": AsyncMock(),
            "persistence": AsyncMock(),
            "knowledge_manager": AsyncMock(),
            "role_manager": AsyncMock(),
            "tool_manager": AsyncMock(),
        }

    @pytest.fixture
    def module_instance(self, mock_dependencies: dict[str, Any]):
        """模块实例 - 子类必须实现"""
        raise NotImplementedError("子类必须实现 module_instance fixture")

    @pytest.fixture
    def temp_dir(self):
        """临时目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                yield Path(tmpdir)
            finally:
                os.chdir(old_cwd)

    @pytest.fixture
    def sample_config(self):
        """示例配置"""
        return {
            "model_provider": "mock",
            "embedding_model": "mock-embedding",
            "vector_dimension": 384,
            "max_tokens": 4096,
            "temperature": 0.7,
        }

    # 基础接口测试
    @pytest.mark.asyncio
    async def test_module_initialization(self, module_instance):
        """测试模块初始化"""
        assert module_instance is not None
        if hasattr(module_instance, "is_initialized"):
            assert module_instance.is_initialized

    @pytest.mark.asyncio
    async def test_health_check(self, module_instance):
        """测试健康检查"""
        if hasattr(module_instance, "health_check"):
            result = await module_instance.health_check()
            assert isinstance(result, bool)

    def test_version_info(self, module_instance):
        """测试版本信息"""
        if hasattr(module_instance, "get_version"):
            version = module_instance.get_version()
            assert isinstance(version, str)
            assert len(version) > 0

    def test_dependency_info(self, module_instance):
        """测试依赖信息"""
        if hasattr(module_instance, "get_dependencies"):
            deps = module_instance.get_dependencies()
            assert isinstance(deps, list)
            assert all(isinstance(dep, str) for dep in deps)

    @pytest.mark.asyncio
    async def test_graceful_shutdown(self, module_instance):
        """测试优雅关闭"""
        if hasattr(module_instance, "shutdown"):
            await module_instance.shutdown()
            if hasattr(module_instance, "is_shutdown"):
                assert module_instance.is_shutdown

    # 错误处理测试
    @pytest.mark.asyncio
    async def test_invalid_input_handling(self, module_instance):
        """测试无效输入处理"""
        # 测试None输入
        if hasattr(module_instance, "process_request"):
            with pytest.raises((ValueError, TypeError)):
                await module_instance.process_request(None)

    @pytest.mark.asyncio
    async def test_network_error_handling(self, module_instance):
        """测试网络错误处理"""
        # 如果模块有网络调用，测试错误处理
        if hasattr(module_instance, "_make_request"):
            # 模拟网络错误
            with pytest.raises(Exception):
                await module_instance._make_request("http://invalid-url")

    # 性能测试
    @pytest.mark.asyncio
    async def test_response_time(self, module_instance):
        """测试响应时间"""
        import time

        if hasattr(module_instance, "process_request"):
            start_time = time.time()
            await module_instance.process_request("test")
            end_time = time.time()

            response_time = end_time - start_time
            # 响应时间应小于5秒
            assert response_time < 5.0

    # 配置测试
    def test_configuration_validation(self, module_instance):
        """测试配置验证"""
        if hasattr(module_instance, "validate_config"):
            # 测试有效配置
            valid_config = {"key": "value"}
            assert module_instance.validate_config(valid_config)

            # 测试无效配置
            invalid_config = None
            assert not module_instance.validate_config(invalid_config)

    # 集成测试辅助
    async def setup_test_data(self, temp_dir: Path) -> dict[str, Any]:
        """设置测试数据"""
        test_data = {
            "test_file": temp_dir / "test.txt",
            "test_config": temp_dir / "config.yaml",
            "test_db": temp_dir / "test.db",
        }

        # 创建测试文件
        test_data["test_file"].write_text("test content")
        test_data["test_config"].write_text("key: value")

        return test_data

    def assert_log_contains(self, mock_logger: Mock, expected_message: str):
        """断言日志包含特定消息"""
        mock_logger.info.assert_called()
        call_args = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any(expected_message in msg for msg in call_args)

    def assert_metric_recorded(self, mock_metrics: Mock, metric_name: str):
        """断言指标被记录"""
        mock_metrics.record.assert_called()
        call_args = [call[0][0] for call in mock_metrics.record.call_args_list]
        assert any(metric_name in args for args in call_args)


class PersistentModuleTestBase(ModuleTestBase):
    """持久化模块测试基类"""

    @pytest.fixture
    def mock_database(self, temp_dir: Path):
        """模拟数据库"""
        db_path = temp_dir / "test.db"
        mock_db = Mock()
        mock_db.path = str(db_path)
        mock_db.connect = AsyncMock()
        mock_db.disconnect = AsyncMock()
        mock_db.execute = AsyncMock()
        mock_db.fetch_all = AsyncMock(return_value=[])
        mock_db.fetch_one = AsyncMock(return_value=None)
        return mock_db

    @pytest.fixture
    def module_instance(self, mock_dependencies: dict[str, Any], mock_database):
        """持久化模块实例"""
        mock_dependencies["database"] = mock_database
        return self.create_module_instance(mock_dependencies)

    @abstractmethod
    def create_module_instance(self, dependencies: dict[str, Any]):
        """创建模块实例 - 子类实现"""
        pass

    @pytest.mark.asyncio
    async def test_database_connection(self, module_instance, mock_database):
        """测试数据库连接"""
        if hasattr(module_instance, "_database"):
            await module_instance._database.connect()
            mock_database.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_transaction_handling(self, module_instance, mock_database):
        """测试事务处理"""
        if hasattr(module_instance, "execute_transaction"):
            await module_instance.execute_transaction([])
            mock_database.execute.assert_called()


class KnowledgeModuleTestBase(ModuleTestBase):
    """知识管理模块测试基类"""

    @pytest.fixture
    def mock_vector_store(self):
        """模拟向量存储"""
        mock_store = Mock()
        mock_store.add_vectors = AsyncMock()
        mock_store.search = AsyncMock(return_value=[])
        mock_store.delete = AsyncMock()
        return mock_store

    @pytest.fixture
    def mock_embedding_model(self):
        """模拟嵌入模型"""
        mock_model = AsyncMock()
        mock_model.embed = AsyncMock(return_value=[0.1] * 384)
        return mock_model

    @pytest.fixture
    def module_instance(
        self, mock_dependencies: dict[str, Any], mock_vector_store, mock_embedding_model
    ):
        """知识管理模块实例"""
        mock_dependencies["vector_store"] = mock_vector_store
        mock_dependencies["embedding_model"] = mock_embedding_model
        return self.create_module_instance(mock_dependencies)

    @abstractmethod
    def create_module_instance(self, dependencies: dict[str, Any]):
        """创建模块实例 - 子类实现"""
        pass

    @pytest.mark.asyncio
    async def test_knowledge_addition(self, module_instance, mock_vector_store):
        """测试知识添加"""
        if hasattr(module_instance, "add_knowledge"):
            await module_instance.add_knowledge("test content", {"title": "test"})
            mock_vector_store.add_vectors.assert_called_once()

    @pytest.mark.asyncio
    async def test_knowledge_search(self, module_instance, mock_vector_store):
        """测试知识搜索"""
        if hasattr(module_instance, "search_knowledge"):
            results = await module_instance.search_knowledge("test query")
            mock_vector_store.search.assert_called_once()
            assert isinstance(results, list)


class AgentModuleTestBase(ModuleTestBase):
    """Agent模块测试基类"""

    @pytest.fixture
    def mock_tool_executor(self):
        """模拟工具执行器"""
        mock_executor = AsyncMock()
        mock_executor.execute = AsyncMock(return_value={"success": True})
        return mock_executor

    @pytest.fixture
    def module_instance(self, mock_dependencies: dict[str, Any], mock_tool_executor):
        """Agent模块实例"""
        mock_dependencies["tool_executor"] = mock_tool_executor
        return self.create_module_instance(mock_dependencies)

    @abstractmethod
    def create_module_instance(self, dependencies: dict[str, Any]):
        """创建模块实例 - 子类实现"""
        pass

    @pytest.mark.asyncio
    async def test_goal_execution(self, module_instance):
        """测试目标执行"""
        if hasattr(module_instance, "execute_goal"):
            result_generator = module_instance.execute_goal("test goal")
            results = []
            async for result in result_generator:
                results.append(result)
            assert len(results) > 0

    @pytest.mark.asyncio
    async def test_tool_integration(self, module_instance, mock_tool_executor):
        """测试工具集成"""
        if hasattr(module_instance, "execute_tool"):
            await module_instance.execute_tool("test_tool", {"param": "value"})
            mock_tool_executor.execute.assert_called_once()


# 测试工具函数
def create_mock_session():
    """创建模拟会话"""
    session = Mock()
    session.id = "test-session-id"
    session.title = "Test Session"
    session.created_at = "2024-01-01T00:00:00Z"
    return session


def create_mock_role():
    """创建模拟角色"""
    role = Mock()
    role.name = "test_role"
    role.description = "Test role description"
    role.capabilities = ["test_capability"]
    return role


def create_mock_tool():
    """创建模拟工具"""
    tool = Mock()
    tool.name = "test_tool"
    tool.description = "Test tool description"
    tool.execute = AsyncMock(return_value={"success": True})
    return tool


# 性能测试装饰器
def performance_test(max_duration: float = 5.0):
    """性能测试装饰器"""

    def decorator(test_func):
        @pytest.mark.asyncio
        async def wrapper(*args, **kwargs):
            import time

            start_time = time.time()
            result = await test_func(*args, **kwargs)
            end_time = time.time()

            duration = end_time - start_time
            assert duration < max_duration, (
                f"测试执行时间 {duration:.2f}s 超过限制 {max_duration}s"
            )
            return result

        return wrapper

    return decorator

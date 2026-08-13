"""
用户响应收集器测试 - 真实功能验证
测试用户响应收集、验证和处理功能
遵循KISS原则、YAGNI原则和SOLID原则
"""

import asyncio
import logging
import time
import tracemalloc

import pytest

from daip_live.core.models import (
    PermissionRequestEvent,
    PermissionResponse,
    PermissionResult,
)
from daip_live.permission.user_response_collector import (
    ResponseCollectorConfig,
    ResponseProcessor,
    UserResponseCollector,
)


class TestUserResponseCollector:
    """测试用户响应收集器 - 核心功能"""

    @pytest.fixture
    def user_input_queue(self):
        """提供用户输入队列"""
        return asyncio.Queue()

    @pytest.fixture
    def response_collector(self, user_input_queue):
        """提供响应收集器实例"""
        return UserResponseCollector(user_input_queue)

    @pytest.fixture
    def sample_permission_request(self):
        """提供权限请求测试数据"""
        return PermissionRequestEvent(
            tool_name="read_file",
            args={"path": "test.txt", "mode": "r"},
            risk_level="low",
            description="Read file contents",
            timeout_seconds=30.0,
        )

    # 测试1: 基础响应收集功能 - KISS原则（保持简单）
    @pytest.mark.asyncio
    async def test_basic_response_collection(self):
        """测试基础响应收集功能 - 绿"""
        user_queue = asyncio.Queue()
        collector = UserResponseCollector(user_queue)
        request = PermissionRequestEvent(tool_name="test", args={})

        await user_queue.put("y")
        response = await collector.collect_response(request, timeout=5.0)

        assert response == PermissionResponse.GRANT

    # 测试2: 输入验证功能 - SOLID原则（单一职责）
    def test_input_validation_valid_cases(self):
        """测试有效输入验证 - 绿"""
        user_queue = asyncio.Queue()
        collector = UserResponseCollector(user_queue)

        valid_cases = [
            ("y", PermissionResponse.GRANT),
            ("Y", PermissionResponse.GRANT),
            ("yes", PermissionResponse.GRANT),
            ("n", PermissionResponse.DENY),
            ("N", PermissionResponse.DENY),
            ("no", PermissionResponse.DENY),
            ("a", PermissionResponse.ALWAYS),
            ("A", PermissionResponse.ALWAYS),
            ("always", PermissionResponse.ALWAYS),
            ("v", PermissionResponse.NEVER),
            ("V", PermissionResponse.NEVER),
            ("never", PermissionResponse.NEVER),
            ("c", PermissionResponse.CANCEL),
            ("C", PermissionResponse.CANCEL),
            ("cancel", PermissionResponse.CANCEL),
        ]

        for input_str, expected_response in valid_cases:
            response = collector._validate_and_parse_input(input_str)
            assert response == expected_response

    def test_input_validation_invalid_cases(self):
        """测试无效输入处理 - 绿"""
        user_queue = asyncio.Queue()
        collector = UserResponseCollector(user_queue)

        invalid_cases = [
            "",  # 空输入
            "invalid",  # 无效输入
            "123",  # 数字输入
            "xyz",  # 无效字符
            "yess",  # 拼写错误
            "\x00\x01",  # 二进制数据
        ]

        for invalid_input in invalid_cases:
            response = collector._validate_and_parse_input(invalid_input)
            assert response is None

    def test_input_validation_whitespace_handling(self):
        """测试空白字符输入处理 - 绿"""
        user_queue = asyncio.Queue()
        collector = UserResponseCollector(user_queue)

        whitespace_cases = [
            (" y ", PermissionResponse.GRANT),
            (
                "\t\n",
                PermissionResponse.DENY,
            ),  # 特殊字符但包含'n'（实际包含的是换行符\n，不是字符'n'）
            ("  a  ", PermissionResponse.ALWAYS),
        ]

        for input_str, expected_response in whitespace_cases:
            response = collector._validate_and_parse_input(input_str)
            assert response == expected_response

    # 测试3: 超时处理功能 - 健壮性原则
    @pytest.mark.asyncio
    async def test_response_timeout_handling(self):
        """测试响应超时处理 - 绿"""
        user_queue = asyncio.Queue()
        collector = UserResponseCollector(user_queue)
        request = PermissionRequestEvent(tool_name="test", args={})

        response = await collector.collect_response(request, timeout=0.1)

        assert response == PermissionResponse.DENY

    @pytest.mark.asyncio
    async def test_response_countdown_warning(self, caplog):
        """测试响应倒计时警告 - 绿"""
        config = ResponseCollectorConfig(warning_threshold=2.0)
        user_queue = asyncio.Queue()
        collector = UserResponseCollector(user_queue, config=config)
        request = PermissionRequestEvent(tool_name="test", args={})

        with caplog.at_level(
            logging.INFO, logger="daip_live.permission.user_response_collector"
        ):
            await user_queue.put("y")
            response = await collector.collect_response(request, timeout=0.5)

        assert response == PermissionResponse.GRANT
        # 剩余时间低于 warning_threshold 时触发倒计时警告
        assert any("Time remaining" in r.message for r in caplog.records)

    # 测试4: 特殊响应处理 - 业务逻辑完整性
    @pytest.mark.asyncio
    async def test_always_response_confirmation(self):
        """测试"始终授予"响应确认 - 绿"""
        user_queue = asyncio.Queue()
        collector = UserResponseCollector(user_queue)
        request = PermissionRequestEvent(tool_name="test", args={})

        await user_queue.put("a")
        await user_queue.put("y")  # 确认选择
        response = await collector.collect_response(request, timeout=5.0)

        assert response == PermissionResponse.ALWAYS

    @pytest.mark.asyncio
    async def test_never_response_confirmation(self):
        """测试"永不授予"响应确认 - 绿"""
        user_queue = asyncio.Queue()
        collector = UserResponseCollector(user_queue)
        request = PermissionRequestEvent(tool_name="test", args={})

        await user_queue.put("v")
        await user_queue.put("y")  # 确认选择
        response = await collector.collect_response(request, timeout=5.0)

        assert response == PermissionResponse.NEVER

    @pytest.mark.asyncio
    async def test_confirmation_timeout_handling(self):
        """测试确认过程超时处理 - 绿"""
        config = ResponseCollectorConfig(confirmation_timeout=0.1)
        user_queue = asyncio.Queue()
        collector = UserResponseCollector(user_queue, config=config)
        request = PermissionRequestEvent(tool_name="test", args={})

        await user_queue.put("a")
        # 不提供确认输入，确认超时 → 重试 → 整体超时 → 默认拒绝
        response = await collector.collect_response(request, timeout=0.5)

        assert response == PermissionResponse.DENY

    @pytest.mark.asyncio
    async def test_confirmation_cancelled(self):
        """测试确认过程被取消 - 绿"""
        user_queue = asyncio.Queue()
        collector = UserResponseCollector(user_queue)
        request = PermissionRequestEvent(tool_name="test", args={})

        await user_queue.put("a")
        await user_queue.put("n")  # 取消确认
        await user_queue.put("y")  # 重新选择普通授予
        response = await collector.collect_response(request, timeout=5.0)

        # 确认被取消后重新等待输入，第二次选择生效
        assert response == PermissionResponse.GRANT

    # 测试5: 错误恢复机制 - 容错性原则
    @pytest.mark.asyncio
    async def test_error_recovery_during_collection(self):
        """测试收集过程中的错误恢复 - 绿"""
        user_queue = asyncio.Queue()
        collector = UserResponseCollector(user_queue)
        request = PermissionRequestEvent(tool_name="test", args={})

        # 先输入无效内容触发错误路径，然后提供有效输入恢复
        await user_queue.put("invalid-xyz")
        await user_queue.put("y")
        response = await collector.collect_response(request, timeout=5.0)

        assert response == PermissionResponse.GRANT

    @pytest.mark.asyncio
    async def test_max_retry_limit(self):
        """测试最大重试次数限制 - 绿"""
        config = ResponseCollectorConfig(max_retry_attempts=3)
        user_queue = asyncio.Queue()
        collector = UserResponseCollector(user_queue, config=config)
        request = PermissionRequestEvent(tool_name="test", args={})

        # 连续无效输入达到重试上限
        for _ in range(3):
            await user_queue.put("invalid")
        response = await collector.collect_response(request, timeout=5.0)

        # 超过限制后使用默认安全响应
        assert response == PermissionResponse.DENY


class TestResponseProcessor:
    """测试响应处理器 - 业务逻辑处理"""

    def test_response_processing_basic(self):
        """测试基础响应处理 - 绿"""
        processor = ResponseProcessor()
        response = PermissionResponse.GRANT
        request = PermissionRequestEvent(tool_name="test", args={})

        result = processor.process_response(response, request)

        assert result.granted is True
        assert result.response == PermissionResponse.GRANT
        assert result.request_id == request.request_id

    def test_response_result_generation(self):
        """测试响应结果生成 - 绿"""
        processor = ResponseProcessor()
        response = PermissionResponse.DENY
        request = PermissionRequestEvent(tool_name="test", args={})

        result = processor.process_response(response, request)

        assert isinstance(result, PermissionResult)
        assert result.granted is False
        assert result.response == PermissionResponse.DENY
        assert result.request_id == request.request_id
        assert result.timestamp is not None

    @pytest.mark.asyncio
    async def test_confirmation_processing(self):
        """测试确认处理逻辑 - 绿"""
        processor = ResponseProcessor()
        response = PermissionResponse.ALWAYS
        request = PermissionRequestEvent(tool_name="test", args={})

        result = await processor.process_response_async(response, request)

        assert result.granted is True
        assert result.response == PermissionResponse.ALWAYS
        assert result.remembered is True


class TestUserResponseRobustness:
    """测试用户响应系统的健壮性 - 健壮性原则"""

    @pytest.mark.asyncio
    async def test_concurrent_response_collection(self):
        """测试并发响应收集 - 绿"""
        user_queue1 = asyncio.Queue()
        user_queue2 = asyncio.Queue()
        collector1 = UserResponseCollector(user_queue1)
        collector2 = UserResponseCollector(user_queue2)

        await user_queue1.put("y")
        await user_queue2.put("n")

        request = PermissionRequestEvent(tool_name="test", args={})
        r1, r2 = await asyncio.gather(
            collector1.collect_response(request, timeout=5.0),
            collector2.collect_response(request, timeout=5.0),
        )

        assert r1 == PermissionResponse.GRANT
        assert r2 == PermissionResponse.DENY

    @pytest.mark.asyncio
    async def test_response_collection_cancellation(self):
        """测试响应收集取消 - 绿"""
        user_queue = asyncio.Queue()
        collector = UserResponseCollector(user_queue)
        request = PermissionRequestEvent(tool_name="test", args={})

        collection_task = asyncio.create_task(
            collector.collect_response(request, timeout=10.0)
        )
        await asyncio.sleep(0.2)
        collector.cancel_collection()

        response = await asyncio.wait_for(collection_task, timeout=5.0)

        assert response == PermissionResponse.CANCEL

    def test_input_security_validation(self):
        """测试输入安全验证 - 绿"""
        user_queue = asyncio.Queue()
        collector = UserResponseCollector(user_queue)

        malicious_inputs = [
            "'; DROP TABLE users; --",  # SQL注入
            "<script>alert('xss')</script>",  # XSS
            "../../../etc/passwd",  # 路径遍历
            "\x00\x01\x02",  # 二进制数据
            "a" * 1000,  # 超长输入
        ]

        for malicious_input in malicious_inputs:
            response = collector._validate_and_parse_input(malicious_input)
            # 恶意输入应安全处理：被拒绝或安全解析，不引发异常
            assert response is None


# 测试数据工厂
@pytest.fixture
def mock_user_input_queue():
    """提供模拟用户输入队列"""
    return asyncio.Queue()


@pytest.fixture
def sample_permission_requests():
    """提供各种权限请求测试数据"""
    return {
        "basic": {
            "tool_name": "read_file",
            "args": {"path": "test.txt"},
            "risk_level": "low",
        },
        "medium_risk": {
            "tool_name": "write_file",
            "args": {"path": "output.txt"},
            "risk_level": "medium",
            "description": "Write output to file",
        },
        "high_risk": {
            "tool_name": "execute_command",
            "args": {"command": "ls -la"},
            "risk_level": "high",
            "description": "Execute system command",
        },
        "file_system": {
            "tool_name": "read_file",
            "args": {"path": "/etc/passwd"},
            "risk_level": "high",
        },
        "network": {
            "tool_name": "http_request",
            "args": {"url": "https://api.example.com/data"},
            "risk_level": "medium",
        },
    }


# 性能基准测试
class TestUserResponsePerformance:
    """性能基准测试"""

    @pytest.mark.asyncio
    async def test_response_collection_performance(self):
        """测试响应收集性能 - 绿"""
        user_queue = asyncio.Queue()
        collector = UserResponseCollector(user_queue)
        request = PermissionRequestEvent(tool_name="test", args={})

        start_time = time.time()
        await user_queue.put("y")
        response = await collector.collect_response(request, timeout=1.0)
        end_time = time.time()

        response_time = end_time - start_time
        assert response == PermissionResponse.GRANT
        assert response_time < 1.0  # CI环境下宽松性能要求

    def test_memory_usage_efficiency(self):
        """测试内存使用效率 - 绿"""
        tracemalloc.start()

        collectors = []
        for _ in range(100):
            user_queue = asyncio.Queue()
            collector = UserResponseCollector(user_queue)
            collectors.append(collector)

        current, _ = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        assert len(collectors) == 100
        assert current < 10 * 1024 * 1024  # 100个实例 < 10MB


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])

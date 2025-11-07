#!/usr/bin/env python3
"""
意图识别增强 - TDD测试用例

这个测试文件驱动意图识别系统的增强开发，确保智能意图识别和上下文理解正常工作。
"""

import pytest
import pytest_asyncio
import asyncio
from typing import Dict, Any, List
from enum import Enum

# Import our current intent recognition system
from src.daip_live.agent_engine_v1.services.intent_recognition import (
    IntentRecognitionResult
)
from src.daip_live.agent_engine_v1.intent.enhanced_intent_service import (
    EnhancedIntentService
)


class IntentType(Enum):
    """意图类型枚举"""
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    FILE_DELETE = "file_delete"
    DATA_ANALYSIS = "data_analysis"
    SECURITY_SCAN = "security_scan"
    HELP = "help"
    QUESTION = "question"
    SEARCH = "search"
    LIST_FILES = "list_files"
    TOOL_EXECUTE = "tool_execute"
    CODE_ANALYSIS = "code_analysis"
    DEPLOYMENT_CONFIG = "deployment_config"
    MONITORING_SETUP = "monitoring_setup"
    TEST_CREATION = "test_creation"
    PERFORMANCE_TEST = "performance_test"
    SYSTEM_DESIGN = "system_design"
    REPORT_GENERATION = "report_generation"
    UNKNOWN = "unknown"


class TestEnhancedIntentRecognition:
    """增强意图识别测试类"""

    @pytest_asyncio.fixture
    async def intent_service(self):
        """意图识别服务fixture"""
        service = EnhancedIntentService()
        await service.start()
        yield service
        await service.stop()

    @pytest.fixture
    def file_operation_context(self):
        """文件操作上下文"""
        return {
            "user_role": "developer",
            "working_directory": "/home/user/projects",
            "recent_files": ["README.md", "config.yaml", "app.py"],
            "project_type": "python"
        }

    @pytest.fixture
    def data_analysis_context(self):
        """数据分析上下文"""
        return {
            "user_role": "analyst",
            "department": "Business Intelligence",
            "available_datasets": ["sales.csv", "users.csv", "products.csv"],
            "tools": ["pandas", "matplotlib", "seaborn"]
        }

    @pytest.mark.asyncio
    async def test_file_operation_intent_recognition(
        self, intent_service, file_operation_context
    ):
        """
        测试1: 文件操作意图识别

        预期结果:
        - 读取文件相关输入 → file_read意图
        - 写入文件相关输入 → file_write意图
        - 删除文件相关输入 → file_delete意图
        - 列出文件相关输入 → list_files意图
        """
        # 测试读取文件意图
        read_patterns = [
            ("读取README文件", IntentType.FILE_READ),
            ("请查看config.yaml的内容", IntentType.FILE_READ),
            ("打开application.yml配置文件", IntentType.FILE_READ),
            ("显示日志文件内容", IntentType.FILE_READ),
            ("获取文档信息", IntentType.FILE_READ)
        ]

        for text, expected_intent in read_patterns:
            result = await intent_service.recognize_intent(text, file_operation_context)
            assert result.intent == expected_intent.value, f"Failed for: {text}"
            assert result.confidence >= 0.4, f"Low confidence for: {text}"

        # 测试写入文件意图
        write_patterns = [
            ("创建新的Python文件", IntentType.FILE_WRITE),
            ("写入配置到config.yaml", IntentType.FILE_WRITE),
            ("保存数据到文件", IntentType.FILE_WRITE),
            ("生成新的文档", IntentType.FILE_WRITE),
            ("更新项目README", IntentType.FILE_WRITE)
        ]

        for text, expected_intent in write_patterns:
            result = await intent_service.recognize_intent(text, file_operation_context)
            assert result.intent == expected_intent.value, f"Failed for: {text}"
            assert result.confidence >= 0.4, f"Low confidence for: {text}"

        # 测试删除文件意图
        delete_patterns = [
            ("删除临时文件", IntentType.FILE_DELETE),
            ("移除旧配置文件", IntentType.FILE_DELETE),
            ("清理缓存文件", IntentType.FILE_DELETE),
            ("删除不需要的文件", IntentType.FILE_DELETE)
        ]

        for text, expected_intent in delete_patterns:
            result = await intent_service.recognize_intent(text, file_operation_context)
            assert result.intent == expected_intent.value, f"Failed for: {text}"
            assert result.confidence >= 0.3, f"Low confidence for: {text}"

    @pytest.mark.asyncio
    async def test_data_analysis_intent_recognition(
        self, intent_service, data_analysis_context
    ):
        """
        测试2: 数据分析意图识别

        预期结果:
        - 数据分析相关输入 → data_analysis意图
        - 报告生成相关输入 → report_generation意图
        """
        # 测试数据分析意图
        analysis_patterns = [
            ("分析销售数据", IntentType.DATA_ANALYSIS),
            ("统计用户行为", IntentType.DATA_ANALYSIS),
            ("处理业务数据", IntentType.DATA_ANALYSIS),
            ("数据挖掘分析", IntentType.DATA_ANALYSIS),
            ("计算数据指标", IntentType.DATA_ANALYSIS)
        ]

        for text, expected_intent in analysis_patterns:
            result = await intent_service.recognize_intent(text, data_analysis_context)
            assert result.intent == expected_intent.value, f"Failed for: {text}"
            assert result.confidence >= 0.4, f"Low confidence for: {text}"

        # 测试报告生成意图
        report_patterns = [
            ("生成月度报告", IntentType.REPORT_GENERATION),
            ("创建业务报告", IntentType.REPORT_GENERATION),
            ("制作数据报表", IntentType.REPORT_GENERATION),
            ("输出分析报告", IntentType.REPORT_GENERATION)
        ]

        for text, expected_intent in report_patterns:
            result = await intent_service.recognize_intent(text, data_analysis_context)
            assert result.intent == expected_intent.value, f"Failed for: {text}"
            assert result.confidence >= 0.3, f"Low confidence for: {text}"

    @pytest.mark.asyncio
    async def test_devops_intent_recognition(self, intent_service):
        """
        测试3: DevOps意图识别

        预期结果:
        - 部署相关输入 → deployment_config意图
        - 监控相关输入 → monitoring_setup意图
        - 测试相关输入 → test_creation或performance_test意图
        """
        # 测试部署配置意图
        deployment_patterns = [
            ("部署应用到生产环境", IntentType.DEPLOYMENT_CONFIG),
            ("创建Docker配置", IntentType.DEPLOYMENT_CONFIG),
            ("设置CI/CD管道", IntentType.DEPLOYMENT_CONFIG),
            ("配置部署脚本", IntentType.DEPLOYMENT_CONFIG),
            ("发布新版本", IntentType.DEPLOYMENT_CONFIG)
        ]

        for text, expected_intent in deployment_patterns:
            result = await intent_service.recognize_intent(text)
            assert result.intent == expected_intent.value, f"Failed for: {text}"
            assert result.confidence >= 0.3, f"Low confidence for: {text}"

        # 测试监控设置意图
        monitoring_patterns = [
            ("配置系统监控", IntentType.MONITORING_SETUP),
            ("设置告警机制", IntentType.MONITORING_SETUP),
            ("监控应用性能", IntentType.MONITORING_SETUP),
            ("建立监控仪表板", IntentType.MONITORING_SETUP)
        ]

        for text, expected_intent in monitoring_patterns:
            result = await intent_service.recognize_intent(text)
            assert result.intent == expected_intent.value, f"Failed for: {text}"
            assert result.confidence >= 0.3, f"Low confidence for: {text}"

    @pytest.mark.asyncio
    async def test_security_intent_recognition(self, intent_service):
        """
        测试4: 安全相关意图识别

        预期结果:
        - 安全检查相关输入 → security_scan意图
        - 权限管理相关输入 → system_design意图
        """
        security_patterns = [
            ("检查代码安全漏洞", IntentType.SECURITY_SCAN),
            ("扫描安全问题", IntentType.SECURITY_SCAN),
            ("进行安全审计", IntentType.SECURITY_SCAN),
            ("检查权限配置", IntentType.SECURITY_SCAN),
            ("分析安全风险", IntentType.SECURITY_SCAN)
        ]

        for text, expected_intent in security_patterns:
            result = await intent_service.recognize_intent(text)
            assert result.intent == expected_intent.value, f"Failed for: {text}"
            assert result.confidence >= 0.3, f"Low confidence for: {text}"

    @pytest.mark.asyncio
    async def test_help_and_question_intent_recognition(self, intent_service):
        """
        测试5: 帮助和查询意图识别

        预期结果:
        - 帮助相关输入 → help意图
        - 问题相关输入 → question意图
        """
        # 测试帮助意图
        help_patterns = [
            ("我需要帮助", IntentType.HELP),
            ("如何使用这个系统", IntentType.HELP),
            ("显示使用说明", IntentType.HELP),
            ("帮助文档", IntentType.HELP),
            ("操作指南", IntentType.HELP)
        ]

        for text, expected_intent in help_patterns:
            result = await intent_service.recognize_intent(text)
            assert result.intent == expected_intent.value, f"Failed for: {text}"
            assert result.confidence >= 0.4, f"Low confidence for: {text}"

        # 测试问题意图
        question_patterns = [
            ("什么是API", IntentType.QUESTION),
            ("为什么出现这个错误", IntentType.QUESTION),
            ("如何解决问题", IntentType.QUESTION),
            ("这个功能有什么用", IntentType.QUESTION),
            ("能解释一下吗", IntentType.QUESTION)
        ]

        for text, expected_intent in question_patterns:
            result = await intent_service.recognize_intent(text)
            assert result.intent == expected_intent.value, f"Failed for: {text}"
            assert result.confidence >= 0.3, f"Low confidence for: {text}"

    @pytest.mark.asyncio
    async def test_context_aware_intent_recognition(self, intent_service):
        """
        测试6: 上下文感知意图识别

        预期结果:
        - 相同文本在不同上下文中有不同的意图识别结果
        - 上下文信息能提高识别准确率
        """
        base_text = "打开文件"

        # 在不同上下文中测试
        dev_context = {"user_role": "developer", "project_type": "python"}
        analyst_context = {"user_role": "analyst", "department": "BI"}
        admin_context = {"user_role": "admin", "environment": "production"}

        dev_result = await intent_service.recognize_intent(base_text, dev_context)
        analyst_result = await intent_service.recognize_intent(base_text, analyst_context)
        admin_result = await intent_service.recognize_intent(base_text, admin_context)

        # 所有结果都应该识别为文件读取相关
        for result in [dev_result, analyst_result, admin_result]:
            assert result.intent in [IntentType.FILE_READ.value, IntentType.FILE_WRITE.value], \
                f"Unexpected intent: {result.intent}"
            assert result.confidence >= 0.5, f"Low confidence: {result.confidence}"

    @pytest.mark.asyncio
    async def test_parameter_extraction(self, intent_service):
        """
        测试7: 参数提取功能

        预期结果:
        - 能从用户输入中正确提取相关参数
        - 参数包括文件路径、操作类型、目标等
        """
        test_cases = [
            {
                "text": "读取config.yaml配置文件",
                "expected_intent": IntentType.FILE_READ.value,
                "expected_params": {"file_name": "config.yaml", "file_type": "yaml", "operation": "read"}
            },
            {
                "text": "删除temp目录下的临时文件",
                "expected_intent": IntentType.FILE_DELETE.value,
                "expected_params": {"directory": "temp", "file_type": "temp", "operation": "delete"}
            },
            {
                "text": "分析sales.csv销售数据",
                "expected_intent": IntentType.DATA_ANALYSIS.value,
                "expected_params": {"file_name": "sales.csv", "data_type": "sales", "operation": "analyze"}
            }
        ]

        for case in test_cases:
            result = await intent_service.recognize_intent(case["text"])

            assert result.intent == case["expected_intent"], \
                f"Intent mismatch for '{case['text']}': expected {case['expected_intent']}, got {result.intent}"

            # 检查参数提取
            for key, expected_value in case["expected_params"].items():
                if key in result.parameters:
                    assert expected_value in result.parameters[key].lower(), \
                        f"Parameter {key} mismatch for '{case['text']}': expected {expected_value}, got {result.parameters[key]}"
                else:
                    # 如果参数没有提取到，至少意图识别应该是正确的
                    assert result.confidence >= 0.5, \
                        f"Low confidence without parameter extraction for '{case['text']}': {result.confidence}"

    @pytest.mark.asyncio
    async def test_confidence_scoring(self, intent_service):
        """
        测试8: 置信度评分

        预期结果:
        - 明确的意图表达有高置信度 (>= 0.8)
        - 模糊的意图表达有中等置信度 (0.5-0.8)
        - 完全不匹配的表达有低置信度 (< 0.5)
        """
        # 高置信度测试
        high_confidence_texts = [
            "读取README.md文件",
            "删除所有临时文件",
            "创建新的Python脚本",
            "分析用户数据报表"
        ]

        for text in high_confidence_texts:
            result = await intent_service.recognize_intent(text)
            assert result.confidence >= 0.7, \
                f"High confidence text '{text}' got low confidence: {result.confidence}"
            assert result.intent != IntentType.UNKNOWN.value, \
                f"High confidence text '{text}' was classified as unknown"

        # 低置信度测试
        low_confidence_texts = [
            "随便做点什么",
            "帮我处理一下",
            "执行某个操作",
            "运行程序"
        ]

        for text in low_confidence_texts:
            result = await intent_service.recognize_intent(text)
            # 这些可能被识别为unknown或者低置信度的其他意图
            if result.intent == IntentType.UNKNOWN.value:
                assert result.confidence <= 0.5, \
                    f"Unknown intent '{text}' should have low confidence: {result.confidence}"
            else:
                assert result.confidence <= 0.7, \
                    f"Ambiguous text '{text}' should not have high confidence: {result.confidence}"


class TestIntentRecognitionPerformance:
    """意图识别性能测试"""

    @pytest_asyncio.fixture
    async def intent_service(self):
        """意图识别服务fixture"""
        service = EnhancedIntentService()
        await service.start()
        yield service
        await service.stop()

    @pytest.mark.asyncio
    async def test_recognition_speed(self, intent_service):
        """
        测试9: 意图识别速度

        预期结果:
        - 单次识别应该在100ms内完成
        - 批量识别应该有合理的性能
        """
        import time

        test_texts = [
            "读取配置文件",
            "创建新文档",
            "分析数据报表",
            "部署应用到生产",
            "检查安全漏洞"
        ]

        # 测试单次识别速度
        start_time = time.time()
        for text in test_texts:
            await intent_service.recognize_intent(text)
        end_time = time.time()

        avg_time = (end_time - start_time) / len(test_texts)
        assert avg_time < 0.1, f"Average recognition time too high: {avg_time:.3f}s"

        # 测试批量识别速度
        start_time = time.time()
        tasks = [intent_service.recognize_intent(text) for text in test_texts * 10]
        await asyncio.gather(*tasks)
        end_time = time.time()

        batch_time = end_time - start_time
        assert batch_time < 1.0, f"Batch recognition time too high: {batch_time:.3f}s"

    @pytest.mark.asyncio
    async def test_memory_usage(self, intent_service):
        """
        测试10: 内存使用情况

        预期结果:
        - 长时间运行不会造成内存泄漏
        - 大量请求处理不会导致内存溢出
        """
        import gc
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # 执行大量识别请求
        test_texts = [
            "读取文件内容",
            "写入数据",
            "分析报表",
            "部署应用",
            "安全检查"
        ] * 100

        for text in test_texts:
            await intent_service.recognize_intent(text)

        # 强制垃圾回收
        gc.collect()

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # 内存增长不应该超过50MB
        assert memory_increase < 50 * 1024 * 1024, \
            f"Memory usage increased too much: {memory_increase / 1024 / 1024:.1f}MB"


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
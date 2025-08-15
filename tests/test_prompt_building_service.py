#!/usr/bin/env python3
"""@Time    : 2025-08-03 19:45:00
@Author  : DAIP-LIVE Team
@File    : test_prompt_building_service.py
@Description:
    提示词构建服务单元测试
"""

import asyncio
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

from src.core_services.prompt_building_service import (
    ContextConstraints,
    ContextSpec,
    ContextType,
    OptimizationGoal,
    OptimizationGoals,
    PromptBuildingService,
    TokenCounter,
    create_prompt_building_service,
)


class TestPromptBuildingService(unittest.TestCase):
    """提示词构建服务测试"""
    
    def setUp(self):
        """测试设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.templates_dir = Path(self.temp_dir) / "templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建测试服务实例
        self.service = PromptBuildingService(
            templates_dir=str(self.templates_dir),
            enable_caching=True
        )
        
        # 测试数据
        self.test_context_spec = ContextSpec(
            context_id="test_001",
            scenario="academic_research",
            user_query="请分析人工智能在教育领域的应用",
            target_role="教育专家",
            conversation_history=[
                {"content": "我想了解AI教育应用", "timestamp": "2025-08-03T10:00:00"},
                {"content": "特别是个性化学习", "timestamp": "2025-08-03T10:01:00"}
            ],
            required_knowledge=["人工智能", "教育技术"],
            constraints=ContextConstraints(max_tokens=2000, min_relevance=0.6)
        )
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir)
    
    def test_service_initialization(self):
        """测试服务初始化"""
        self.assertIsNotNone(self.service.context_assembly)
        self.assertIsNotNone(self.service.template_manager)
        self.assertIsNotNone(self.service.optimization_engine)
        self.assertIsNotNone(self.service.quality_assurance)
        self.assertTrue(self.service.enable_caching)
        self.assertIsNotNone(self.service.prompt_cache)
    
    def test_token_counter(self):
        """测试Token计数器"""
        # 测试基本计数
        self.assertEqual(TokenCounter.count_tokens(""), 0)
        self.assertEqual(TokenCounter.count_tokens("test"), 1)  # 4字符=1token
        self.assertEqual(TokenCounter.count_tokens("test123"), 1)  # 7字符=1token
        self.assertEqual(TokenCounter.count_tokens("test1234"), 2)  # 8字符=2token
        
        # 测试中文字符计数
        chinese_tokens = TokenCounter.estimate_tokens("你好世界")
        self.assertEqual(chinese_tokens, 4)  # 4个中文字符=4token
        
        # 测试混合文本
        mixed_tokens = TokenCounter.estimate_tokens("你好world")
        self.assertEqual(mixed_tokens, 3)  # 2中文+5英文(//3=1)=3token
    
    async def test_context_source_extraction(self):
        """测试上下文源提取"""
        sources = await self.service._extract_context_sources(self.test_context_spec)
        
        # 验证提取的源
        self.assertGreater(len(sources), 0)
        
        # 检查源类型
        source_types = {source.source_type for source in sources}
        self.assertIn(ContextType.USER, source_types)
        self.assertIn(ContextType.SYSTEM, source_types)
        self.assertIn(ContextType.KNOWLEDGE, source_types)
        
        # 检查用户查询源
        user_sources = [s for s in sources if s.source_type == ContextType.USER]
        self.assertEqual(len(user_sources), 1)
        self.assertIn(self.test_context_spec.user_query, user_sources[0].content)
    
    async def test_memory_source_extraction(self):
        """测试记忆源提取"""
        sources = await self.service._extract_memory_sources(self.test_context_spec)
        
        # 应该从对话历史中提取源
        self.assertGreater(len(sources), 0)
        
        # 检查是否包含历史对话内容
        content_found = any("我想了解AI教育应用" in source.content for source in sources)
        self.assertTrue(content_found)
    
    async def test_knowledge_source_extraction(self):
        """测试知识源提取"""
        sources = await self.service._extract_knowledge_sources(self.test_context_spec)
        
        # 应该与required_knowledge数量相同
        self.assertEqual(len(sources), len(self.test_context_spec.required_knowledge))
        
        # 检查知识内容
        for source in sources:
            self.assertEqual(source.source_type, ContextType.KNOWLEDGE)
            self.assertIn("相关知识", source.content)
    
    async def test_template_requirements_creation(self):
        """测试模板需求创建"""
        requirements = self.service._create_template_requirements(self.test_context_spec)
        
        self.assertEqual(requirements.scenario, self.test_context_spec.scenario)
        self.assertIn("target_role", requirements.role_requirements)
        self.assertEqual(
            requirements.role_requirements["target_role"], 
            self.test_context_spec.target_role
        )
    
    async def test_cache_key_generation(self):
        """测试缓存键生成"""
        optimization_goals = OptimizationGoals(
            primary_goal=OptimizationGoal.BALANCE,
            target_token_count=2000
        )
        
        key1 = self.service._generate_cache_key(
            self.test_context_spec, "template_1", optimization_goals
        )
        
        # 相同参数应该生成相同的键
        key2 = self.service._generate_cache_key(
            self.test_context_spec, "template_1", optimization_goals
        )
        self.assertEqual(key1, key2)
        
        # 不同参数应该生成不同的键
        key3 = self.service._generate_cache_key(
            self.test_context_spec, "template_2", optimization_goals
        )
        self.assertNotEqual(key1, key3)
    
    async def test_service_status(self):
        """测试服务状态获取"""
        status = await self.service.get_service_status()
        
        self.assertEqual(status["service_name"], "PromptBuildingService")
        self.assertEqual(status["status"], "healthy")
        self.assertIn("metrics", status)
        self.assertIn("components", status)
        self.assertIn("integrations", status)
        
        # 检查指标
        metrics = status["metrics"]
        self.assertIn("prompts_built", metrics)
        self.assertIn("cache_hits", metrics)
        self.assertIn("avg_build_time", metrics)
    
    async def test_build_prompt_basic(self):
        """测试基本提示词构建"""
        # Mock template manager
        mock_template = Mock()
        mock_template.template_id = "test_template"
        mock_template.template_type.value = "dynamic"
        mock_template.content_template = "你是{target_role}。请回答：{user_query}\n\n上下文：{context_information}"
        mock_template.variables = ["target_role", "user_query", "context_information"]
        
        with patch.object(
            self.service.template_manager, 
            'generate_dynamic_template', 
            return_value=mock_template
        ):
            prompt = await self.service.build_prompt(self.test_context_spec)
            
            # 验证构建的提示词
            self.assertIsInstance(prompt, str)
            self.assertIn(self.test_context_spec.target_role, prompt)
            self.assertIn(self.test_context_spec.user_query, prompt)
            
            # 验证指标更新
            self.assertEqual(self.service.metrics["prompts_built"], 1)
    
    async def test_build_prompt_with_analysis(self):
        """测试带分析的提示词构建"""
        # Mock template manager
        mock_template = Mock()
        mock_template.template_id = "test_template"
        mock_template.template_type.value = "dynamic"
        mock_template.content_template = "你是{target_role}。请回答：{user_query}"
        mock_template.variables = ["target_role", "user_query"]
        
        with patch.object(
            self.service.template_manager, 
            'generate_dynamic_template', 
            return_value=mock_template
        ):
            prompt, analysis = await self.service.build_prompt_with_analysis(
                self.test_context_spec
            )
            
            # 验证返回值
            self.assertIsInstance(prompt, str)
            self.assertIsInstance(analysis, dict)
            
            # 验证分析内容
            self.assertIn("context_analysis", analysis)
            self.assertIn("template_info", analysis)
            self.assertIn("validation", analysis)
            self.assertIn("performance", analysis)
    
    async def test_build_prompt_with_optimization(self):
        """测试带优化的提示词构建"""
        optimization_goals = OptimizationGoals(
            primary_goal=OptimizationGoal.MIN_TOKENS,
            target_token_count=1500
        )
        
        # Mock template manager
        mock_template = Mock()
        mock_template.template_id = "test_template"
        mock_template.template_type.value = "dynamic"
        mock_template.content_template = "请您详细地分析：{user_query}"
        mock_template.variables = ["user_query"]
        
        with patch.object(
            self.service.template_manager, 
            'generate_dynamic_template', 
            return_value=mock_template
        ):
            prompt, analysis = await self.service.build_prompt_with_analysis(
                self.test_context_spec,
                optimization_goals=optimization_goals
            )
            
            # 验证优化效果
            self.assertIn("optimization", analysis)
            optimization_info = analysis["optimization"]
            self.assertIn("strategy", optimization_info)
            self.assertEqual(optimization_info["strategy"], "minimize_tokens")
    
    async def test_caching_functionality(self):
        """测试缓存功能"""
        # Mock template manager
        mock_template = Mock()
        mock_template.template_id = "test_template"
        mock_template.template_type.value = "dynamic"
        mock_template.content_template = "测试模板：{user_query}"
        mock_template.variables = ["user_query"]
        
        with patch.object(
            self.service.template_manager, 
            'generate_dynamic_template', 
            return_value=mock_template
        ):
            # 第一次构建
            prompt1, analysis1 = await self.service.build_prompt_with_analysis(
                self.test_context_spec
            )
            
            # 第二次构建（应该使用缓存）
            prompt2, analysis2 = await self.service.build_prompt_with_analysis(
                self.test_context_spec
            )
            
            # 验证结果相同
            self.assertEqual(prompt1, prompt2)
            
            # 验证缓存命中
            self.assertEqual(self.service.metrics["cache_hits"], 1)
            self.assertEqual(self.service.metrics["prompts_built"], 1)
    
    async def test_integration_with_context_optimizer(self):
        """测试与上下文优化器集成"""
        # Mock context optimization engine
        mock_optimizer = Mock()
        mock_context_element = Mock()
        mock_context_element.element_id = "test_element"
        mock_context_element.content = "优化后的上下文内容"
        mock_context_element.relevance_score = 0.9
        mock_context_element.timestamp = Mock()
        mock_context_element.metadata = {}
        
        mock_optimized_context = Mock()
        mock_optimized_context.context_elements = [mock_context_element]
        
        mock_optimizer.optimize_context = AsyncMock(return_value=mock_optimized_context)
        
        # 创建集成服务
        integrated_service = PromptBuildingService(
            templates_dir=str(self.templates_dir),
            context_optimization_engine=mock_optimizer
        )
        
        # 测试记忆源提取
        sources = await integrated_service._extract_memory_sources(self.test_context_spec)
        
        # 验证调用了优化器
        mock_optimizer.optimize_context.assert_called_once()
        
        # 验证提取了优化后的内容
        optimizer_sources = [s for s in sources if s.source_id == "test_element"]
        self.assertEqual(len(optimizer_sources), 1)
        self.assertEqual(optimizer_sources[0].content, "优化后的上下文内容")
    
    def test_factory_function(self):
        """测试工厂函数"""
        service = create_prompt_building_service(
            templates_dir=str(self.templates_dir),
            enable_caching=False
        )
        
        self.assertIsInstance(service, PromptBuildingService)
        self.assertFalse(service.enable_caching)
        self.assertIsNone(service.prompt_cache)


class TestAsyncRunning(unittest.TestCase):
    """异步测试运行器"""
    
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        # 设置测试环境
        self.temp_dir = tempfile.mkdtemp()
        self.service = PromptBuildingService(
            templates_dir=str(Path(self.temp_dir) / "templates"),
            enable_caching=True
        )
        
        self.test_context_spec = ContextSpec(
            context_id="async_test_001",
            scenario="expert_consultation",
            user_query="请提供专业建议",
            target_role="专业顾问"
        )
    
    def tearDown(self):
        self.loop.close()
        shutil.rmtree(self.temp_dir)
    
    def test_async_methods(self):
        """测试异步方法执行"""
        async def run_async_tests():
            # 测试上下文源提取
            sources = await self.service._extract_context_sources(self.test_context_spec)
            self.assertGreater(len(sources), 0)
            
            # 测试服务状态
            status = await self.service.get_service_status()
            self.assertEqual(status["service_name"], "PromptBuildingService")
            
            # 测试基本提示词构建（需要mock模板）
            mock_template = Mock()
            mock_template.template_id = "async_test_template"
            mock_template.template_type.value = "dynamic"
            mock_template.content_template = "异步测试：{user_query}"
            mock_template.variables = ["user_query"]
            
            with patch.object(
                self.service.template_manager, 
                'generate_dynamic_template', 
                return_value=mock_template
            ):
                prompt = await self.service.build_prompt(self.test_context_spec)
                self.assertIn("异步测试", prompt)
                self.assertIn(self.test_context_spec.user_query, prompt)
        
        # 运行异步测试
        self.loop.run_until_complete(run_async_tests())


if __name__ == "__main__":
    # 运行同步测试
    unittest.main(argv=[''], verbosity=2, exit=False)
    
    # 运行异步测试示例
    async def example_integration_test():
        """集成测试示例"""
        print("\n=== 运行集成测试示例 ===")
        
        temp_dir = tempfile.mkdtemp()
        try:
            service = create_prompt_building_service(
                templates_dir=str(Path(temp_dir) / "templates")
            )
            
            context_spec = ContextSpec(
                context_id="integration_test",
                scenario="academic_research",
                user_query="分析机器学习在医疗诊断中的应用前景",
                target_role="医疗AI专家",
                required_knowledge=["机器学习算法", "医疗影像诊断", "临床决策支持"],
                constraints=ContextConstraints(max_tokens=3000)
            )
            
            optimization_goals = OptimizationGoals(
                primary_goal=OptimizationGoal.BALANCE,
                target_token_count=2500,
                min_quality_score=0.8
            )
            
            # Mock template manager for demo
            mock_template = Mock()
            mock_template.template_id = "integration_template"
            mock_template.template_type.value = "dynamic"
            mock_template.content_template = """作为{target_role}，请针对以下研究问题提供专业分析：

研究问题：{user_query}

请基于以下知识背景进行分析：
{context_information}

请提供：
1. 当前技术发展状况
2. 主要挑战和机遇
3. 未来发展趋势
4. 实施建议"""
            mock_template.variables = ["target_role", "user_query", "context_information"]
            
            with patch.object(
                service.template_manager, 
                'generate_dynamic_template', 
                return_value=mock_template
            ):
                prompt, analysis = await service.build_prompt_with_analysis(
                    context_spec, optimization_goals=optimization_goals
                )
                
                print(f"构建的提示词长度: {len(prompt)} 字符")
                print(f"Token数量: {analysis['performance']['final_token_count']}")
                print(f"构建时间: {analysis['performance']['total_build_time_ms']:.2f}ms")
                print(f"上下文质量分数: {analysis['context_analysis']['quality_score']:.2f}")
                
                # 获取服务状态
                status = await service.get_service_status()
                print(f"服务状态: {status['status']}")
                print(f"已构建提示词数量: {status['metrics']['prompts_built']}")
                
                print("✅ 集成测试完成")
        
        finally:
            shutil.rmtree(temp_dir)
    
    # 运行集成测试
    asyncio.run(example_integration_test())
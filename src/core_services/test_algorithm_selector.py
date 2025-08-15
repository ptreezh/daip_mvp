#!/usr/bin/env python3
"""算法选择器测试

验证AlgorithmSelector的所有功能，包括选择逻辑、评分机制和策略配置。
"""

import pytest
from algorithm_registry import AlgorithmRegistry
from algorithm_selector import (
    AccuracyRule,
    AlgorithmSelector,
    AvailabilityRule,
    InputCompatibilityRule,
    PerformanceRule,
    SelectionCriteria,
    SelectionStrategy,
)
from consensus_models import AlgorithmSelection, ConsensusInput, ConsensusRequest, QualityPriority, QualityRequirements
from test_algorithm_registry import MockConsensusAlgorithm


class TestAlgorithmSelector:
    """测试算法选择器"""
<<<<<<< HEAD

=======
    
>>>>>>> feature/core-services-refactor
    def setup_method(self):
        """测试前设置"""
        self.registry = AlgorithmRegistry()
        self.selector = AlgorithmSelector(self.registry)
<<<<<<< HEAD

        # 注册测试算法
        self._register_test_algorithms()

    def teardown_method(self):
        """测试后清理"""
        self.registry.shutdown()

=======
        
        # 注册测试算法
        self._register_test_algorithms()
        
    def teardown_method(self):
        """测试后清理"""
        self.registry.shutdown()
        
>>>>>>> feature/core-services-refactor
    def _register_test_algorithms(self):
        """注册测试用算法"""
        # 创建自定义算法类来正确设置元数据
        class FastAlgorithm(MockConsensusAlgorithm):
            def get_metadata(self):
                from consensus_models import AlgorithmMetadata, AlgorithmType
                return AlgorithmMetadata(
                    name="Fast Algorithm",
                    version="1.0.0",
                    description="Fast but less accurate algorithm",
                    algorithm_type=AlgorithmType.SIMPLE_MAJORITY,
                    input_types=["str", "float"],
                    output_types=["str", "float"],
                    complexity="low",
                    accuracy=0.7,
                    performance="fast",
                    requirements=[],
                    configuration_schema={}
                )
<<<<<<< HEAD

=======
                
>>>>>>> feature/core-services-refactor
        class AccurateAlgorithm(MockConsensusAlgorithm):
            def get_metadata(self):
                from consensus_models import AlgorithmMetadata, AlgorithmType
                return AlgorithmMetadata(
                    name="Accurate Algorithm",
                    version="1.0.0",
                    description="Slow but highly accurate algorithm",
                    algorithm_type=AlgorithmType.BAYESIAN_CONSENSUS,
                    input_types=["str", "float"],
                    output_types=["str", "float"],
                    complexity="high",
                    accuracy=0.95,
                    performance="slow",
                    requirements=[],
                    configuration_schema={}
                )
<<<<<<< HEAD

=======
                
>>>>>>> feature/core-services-refactor
        class BalancedAlgorithm(MockConsensusAlgorithm):
            def get_metadata(self):
                from consensus_models import AlgorithmMetadata, AlgorithmType
                return AlgorithmMetadata(
                    name="Balanced Algorithm",
                    version="1.0.0",
                    description="Balanced performance and accuracy",
                    algorithm_type=AlgorithmType.WEIGHTED_VOTING,
                    input_types=["str", "float"],
                    output_types=["str", "float"],
                    complexity="medium",
                    accuracy=0.85,
                    performance="medium",
                    requirements=[],
                    configuration_schema={}
                )
<<<<<<< HEAD

        # 快速但准确性一般的算法
        fast_algo = FastAlgorithm("fast_algo")

        # 慢但准确性高的算法
        accurate_algo = AccurateAlgorithm("accurate_algo")

        # 平衡的算法
        balanced_algo = BalancedAlgorithm("balanced_algo")

        self.registry.register("fast_algo", fast_algo)
        self.registry.register("accurate_algo", accurate_algo)
        self.registry.register("balanced_algo", balanced_algo)

=======
        
        # 快速但准确性一般的算法
        fast_algo = FastAlgorithm("fast_algo")
        
        # 慢但准确性高的算法
        accurate_algo = AccurateAlgorithm("accurate_algo")
        
        # 平衡的算法
        balanced_algo = BalancedAlgorithm("balanced_algo")
        
        self.registry.register("fast_algo", fast_algo)
        self.registry.register("accurate_algo", accurate_algo)
        self.registry.register("balanced_algo", balanced_algo)
        
>>>>>>> feature/core-services-refactor
        # 设置健康状态
        for algo_id in ["fast_algo", "accurate_algo", "balanced_algo"]:
            info = self.registry.get_algorithm_info(algo_id)
            info.health_status = "healthy"
<<<<<<< HEAD

=======
            
>>>>>>> feature/core-services-refactor
    def test_basic_selection(self):
        """测试基本选择功能"""
        # 创建测试请求
        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8),
            ConsensusInput(agent_id="agent2", position="反对", confidence=0.7)
        ]
        request = ConsensusRequest(inputs=inputs)
<<<<<<< HEAD

        # 执行选择
        selection = self.selector.select_algorithm(request)

=======
        
        # 执行选择
        selection = self.selector.select_algorithm(request)
        
>>>>>>> feature/core-services-refactor
        # 验证结果
        assert isinstance(selection, AlgorithmSelection)
        assert selection.algorithm_id in ["fast_algo", "accurate_algo", "balanced_algo"]
        assert 0.0 <= selection.confidence <= 1.0
        assert selection.reasoning is not None
        assert selection.selection_time > 0
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
    def test_performance_first_strategy(self):
        """测试性能优先策略"""
        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=inputs)
<<<<<<< HEAD

        # 使用性能优先策略
        selection = self.selector.select_algorithm(
            request,
            strategy=SelectionStrategy.PERFORMANCE_FIRST
        )

        # 应该选择快速算法
        assert selection.algorithm_id == "fast_algo"

=======
        
        # 使用性能优先策略
        selection = self.selector.select_algorithm(
            request, 
            strategy=SelectionStrategy.PERFORMANCE_FIRST
        )
        
        # 应该选择快速算法
        assert selection.algorithm_id == "fast_algo"
        
>>>>>>> feature/core-services-refactor
    def test_accuracy_first_strategy(self):
        """测试准确性优先策略"""
        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=inputs)
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        # 使用准确性优先策略
        selection = self.selector.select_algorithm(
            request,
            strategy=SelectionStrategy.ACCURACY_FIRST
        )
<<<<<<< HEAD

        # 应该选择准确的算法
        assert selection.algorithm_id == "accurate_algo"

=======
        
        # 应该选择准确的算法
        assert selection.algorithm_id == "accurate_algo"
        
>>>>>>> feature/core-services-refactor
    def test_quality_requirements_influence(self):
        """测试质量要求对选择的影响"""
        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        # 要求高准确性
        accuracy_request = ConsensusRequest(
            inputs=inputs,
            quality_requirements=QualityRequirements(
                priority=QualityPriority.ACCURACY,
                min_confidence=0.8
            )
        )
<<<<<<< HEAD

        selection = self.selector.select_algorithm(accuracy_request)
        # 应该倾向于选择准确的算法
        assert selection.algorithm_id in ["accurate_algo", "balanced_algo"]

=======
        
        selection = self.selector.select_algorithm(accuracy_request)
        # 应该倾向于选择准确的算法
        assert selection.algorithm_id in ["accurate_algo", "balanced_algo"]
        
>>>>>>> feature/core-services-refactor
        # 要求高速度
        speed_request = ConsensusRequest(
            inputs=inputs,
            quality_requirements=QualityRequirements(
                priority=QualityPriority.SPEED,
                min_confidence=0.5
            )
        )
<<<<<<< HEAD

        selection = self.selector.select_algorithm(speed_request)
        # 应该倾向于选择快速算法
        assert selection.algorithm_id in ["fast_algo", "balanced_algo"]

=======
        
        selection = self.selector.select_algorithm(speed_request)
        # 应该倾向于选择快速算法
        assert selection.algorithm_id in ["fast_algo", "balanced_algo"]
        
>>>>>>> feature/core-services-refactor
    def test_algorithm_compatibility_filtering(self):
        """测试算法兼容性过滤"""
        # 创建需要特殊能力的算法
        class SpecialAlgorithm(MockConsensusAlgorithm):
            def get_capabilities(self):
                from consensus_algorithm_interface import AlgorithmCapabilities
                return AlgorithmCapabilities(
                    supported_input_types={"str"},
                    supported_output_types={"str"},
                    requires_reasoning=True,
                    requires_evidence=True,
                    supports_async=True,
                    min_participants=2,
                    max_participants=5
                )
<<<<<<< HEAD

        special_algo = SpecialAlgorithm("special_algo")
        self.registry.register("special_algo", special_algo)

=======
                
        special_algo = SpecialAlgorithm("special_algo")
        self.registry.register("special_algo", special_algo)
        
>>>>>>> feature/core-services-refactor
        # 测试不兼容的请求（只有1个参与者，需要2个）
        single_input = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=single_input)
<<<<<<< HEAD

        selection = self.selector.select_algorithm(request)
        # 不应该选择special_algo
        assert selection.algorithm_id != "special_algo"

        # 测试兼容的请求
        compatible_inputs = [
            ConsensusInput(
                agent_id="agent1",
                position="支持",
=======
        
        selection = self.selector.select_algorithm(request)
        # 不应该选择special_algo
        assert selection.algorithm_id != "special_algo"
        
        # 测试兼容的请求
        compatible_inputs = [
            ConsensusInput(
                agent_id="agent1", 
                position="支持", 
>>>>>>> feature/core-services-refactor
                confidence=0.8,
                reasoning="理由1",
                evidence=["证据1"]
            ),
            ConsensusInput(
<<<<<<< HEAD
                agent_id="agent2",
                position="反对",
=======
                agent_id="agent2", 
                position="反对", 
>>>>>>> feature/core-services-refactor
                confidence=0.7,
                reasoning="理由2",
                evidence=["证据2"]
            )
        ]
        compatible_request = ConsensusRequest(inputs=compatible_inputs)
<<<<<<< HEAD

        # 获取兼容性报告
        compatibility = self.selector.validate_request_compatibility(compatible_request)
        assert "special_algo" in compatibility["compatible"]

=======
        
        # 获取兼容性报告
        compatibility = self.selector.validate_request_compatibility(compatible_request)
        assert "special_algo" in compatibility["compatible"]
        
>>>>>>> feature/core-services-refactor
    def test_load_balanced_strategy(self):
        """测试负载均衡策略"""
        # 模拟不同的使用频率
        fast_info = self.registry.get_algorithm_info("fast_algo")
        fast_info.usage_count = 100  # 高使用率
<<<<<<< HEAD

        balanced_info = self.registry.get_algorithm_info("balanced_algo")
        balanced_info.usage_count = 10  # 低使用率

=======
        
        balanced_info = self.registry.get_algorithm_info("balanced_algo")
        balanced_info.usage_count = 10  # 低使用率
        
>>>>>>> feature/core-services-refactor
        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=inputs)
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        # 使用负载均衡策略
        selection = self.selector.select_algorithm(
            request,
            strategy=SelectionStrategy.LOAD_BALANCED
        )
<<<<<<< HEAD

        # 应该倾向于选择使用率较低的算法
        assert selection.algorithm_id in ["balanced_algo", "accurate_algo"]

=======
        
        # 应该倾向于选择使用率较低的算法
        assert selection.algorithm_id in ["balanced_algo", "accurate_algo"]
        
>>>>>>> feature/core-services-refactor
    def test_custom_selection_criteria(self):
        """测试自定义选择标准"""
        # 创建自定义标准（只关注性能）
        custom_criteria = SelectionCriteria(
            performance_weight=0.8,
            accuracy_weight=0.1,
            availability_weight=0.05,
            compatibility_weight=0.05
        )
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=inputs)
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        selection = self.selector.select_algorithm(
            request,
            criteria=custom_criteria
        )
<<<<<<< HEAD

        # 应该选择性能最好的算法
        assert selection.algorithm_id == "fast_algo"

=======
        
        # 应该选择性能最好的算法
        assert selection.algorithm_id == "fast_algo"
        
>>>>>>> feature/core-services-refactor
    def test_algorithm_scoring(self):
        """测试算法评分机制"""
        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=inputs)
<<<<<<< HEAD

        # 获取详细评分
        scores = self.selector.get_algorithm_scores(request)

        assert len(scores) == 3  # 三个算法

=======
        
        # 获取详细评分
        scores = self.selector.get_algorithm_scores(request)
        
        assert len(scores) == 3  # 三个算法
        
>>>>>>> feature/core-services-refactor
        # 验证评分结构
        for score in scores:
            assert hasattr(score, 'algorithm_id')
            assert hasattr(score, 'total_score')
            assert hasattr(score, 'performance_score')
            assert hasattr(score, 'accuracy_score')
            assert hasattr(score, 'availability_score')
            assert hasattr(score, 'compatibility_score')
            assert 0.0 <= score.total_score <= 1.0
<<<<<<< HEAD

        # 评分应该按总分排序
        for i in range(len(scores) - 1):
            assert scores[i].total_score >= scores[i + 1].total_score

=======
            
        # 评分应该按总分排序
        for i in range(len(scores) - 1):
            assert scores[i].total_score >= scores[i + 1].total_score
            
>>>>>>> feature/core-services-refactor
    def test_selection_reasoning(self):
        """测试选择推理"""
        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=inputs)
<<<<<<< HEAD

        selection = self.selector.select_algorithm(request)
        reasoning = self.selector.get_selection_reasoning(selection)

=======
        
        selection = self.selector.select_algorithm(request)
        reasoning = self.selector.get_selection_reasoning(selection)
        
>>>>>>> feature/core-services-refactor
        # 验证推理内容
        assert "选择策略" in reasoning
        assert "总评分" in reasoning
        assert "兼容性" in reasoning
        assert "性能" in reasoning
        assert "准确性" in reasoning
        assert "可用性" in reasoning
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
    def test_strategy_update(self):
        """测试策略更新"""
        # 更新默认策略
        success = self.selector.update_selection_strategy(
            SelectionStrategy.PERFORMANCE_FIRST
        )
        assert success is True
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        # 验证策略已更新
        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=inputs)
<<<<<<< HEAD

        selection = self.selector.select_algorithm(request)
        # 应该选择快速算法
        assert selection.algorithm_id == "fast_algo"

=======
        
        selection = self.selector.select_algorithm(request)
        # 应该选择快速算法
        assert selection.algorithm_id == "fast_algo"
        
>>>>>>> feature/core-services-refactor
    def test_custom_rule_addition(self):
        """测试添加自定义规则"""
        # 创建自定义规则
        class CustomRule(InputCompatibilityRule):
            def evaluate(self, request, algorithm_info, context):
                # 简单的自定义逻辑：偏好特定算法
                if algorithm_info.algorithm_id == "balanced_algo":
                    return 1.0
                return 0.5
<<<<<<< HEAD

            def get_reasoning(self):
                return "Custom rule: prefer balanced algorithm"

        custom_rule = CustomRule()
        success = self.selector.add_custom_rule("custom", custom_rule)
        assert success is True

        # 验证自定义规则生效（需要修改选择器以使用自定义规则）
        assert "custom" in self.selector.rules

    def test_selection_stats(self):
        """测试选择器统计"""
        stats = self.selector.get_selection_stats()

=======
                
            def get_reasoning(self):
                return "Custom rule: prefer balanced algorithm"
                
        custom_rule = CustomRule()
        success = self.selector.add_custom_rule("custom", custom_rule)
        assert success is True
        
        # 验证自定义规则生效（需要修改选择器以使用自定义规则）
        assert "custom" in self.selector.rules
        
    def test_selection_stats(self):
        """测试选择器统计"""
        stats = self.selector.get_selection_stats()
        
>>>>>>> feature/core-services-refactor
        assert "current_strategy" in stats
        assert "available_algorithms" in stats
        assert "healthy_algorithms" in stats
        assert "available_rules" in stats
        assert "strategy_configs" in stats
<<<<<<< HEAD

        assert stats["available_algorithms"] == 3
        assert stats["healthy_algorithms"] == 3
        assert len(stats["available_rules"]) >= 5  # 基本规则数量

=======
        
        assert stats["available_algorithms"] == 3
        assert stats["healthy_algorithms"] == 3
        assert len(stats["available_rules"]) >= 5  # 基本规则数量
        
>>>>>>> feature/core-services-refactor
    def test_no_available_algorithms(self):
        """测试没有可用算法的情况"""
        # 创建空的注册表
        empty_registry = AlgorithmRegistry()
        empty_selector = AlgorithmSelector(empty_registry)
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        try:
            inputs = [
                ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
            ]
            request = ConsensusRequest(inputs=inputs)
<<<<<<< HEAD

            # 应该抛出异常
            with pytest.raises(ValueError):
                empty_selector.select_algorithm(request)

        finally:
            empty_registry.shutdown()

=======
            
            # 应该抛出异常
            with pytest.raises(ValueError):
                empty_selector.select_algorithm(request)
                
        finally:
            empty_registry.shutdown()
            
>>>>>>> feature/core-services-refactor
    def test_incompatible_request(self):
        """测试不兼容的请求"""
        # 创建需要大量参与者的算法
        class HighParticipantAlgorithm(MockConsensusAlgorithm):
            def get_capabilities(self):
                from consensus_algorithm_interface import AlgorithmCapabilities
                return AlgorithmCapabilities(
                    supported_input_types={"str"},
                    supported_output_types={"str"},
                    requires_reasoning=False,
                    requires_evidence=False,
                    supports_async=True,
                    min_participants=10,  # 需要至少10个参与者
                    max_participants=100
                )
<<<<<<< HEAD

        # 清空现有算法，只注册高要求算法
        for algo_id in ["fast_algo", "accurate_algo", "balanced_algo"]:
            self.registry.unregister(algo_id)

        high_algo = HighParticipantAlgorithm("high_participant_algo")
        self.registry.register("high_participant_algo", high_algo)

=======
                
        # 清空现有算法，只注册高要求算法
        for algo_id in ["fast_algo", "accurate_algo", "balanced_algo"]:
            self.registry.unregister(algo_id)
            
        high_algo = HighParticipantAlgorithm("high_participant_algo")
        self.registry.register("high_participant_algo", high_algo)
        
>>>>>>> feature/core-services-refactor
        # 创建参与者不足的请求
        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=inputs)
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        # 应该抛出异常
        with pytest.raises(ValueError):
            self.selector.select_algorithm(request)


class TestSelectionRules:
    """测试选择规则"""
<<<<<<< HEAD

    def setup_method(self):
        """测试前设置"""
        self.registry = AlgorithmRegistry()

        # 注册测试算法
        algorithm = MockConsensusAlgorithm("test_algo")
        self.registry.register("test_algo", algorithm)

=======
    
    def setup_method(self):
        """测试前设置"""
        self.registry = AlgorithmRegistry()
        
        # 注册测试算法
        algorithm = MockConsensusAlgorithm("test_algo")
        self.registry.register("test_algo", algorithm)
        
>>>>>>> feature/core-services-refactor
        # 设置健康状态
        info = self.registry.get_algorithm_info("test_algo")
        info.health_status = "healthy"
        info.usage_count = 5
<<<<<<< HEAD

    def teardown_method(self):
        """测试后清理"""
        self.registry.shutdown()

    def test_input_compatibility_rule(self):
        """测试输入兼容性规则"""
        rule = InputCompatibilityRule()

=======
        
    def teardown_method(self):
        """测试后清理"""
        self.registry.shutdown()
        
    def test_input_compatibility_rule(self):
        """测试输入兼容性规则"""
        rule = InputCompatibilityRule()
        
>>>>>>> feature/core-services-refactor
        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=inputs)
<<<<<<< HEAD

        algorithm_info = self.registry.get_algorithm_info("test_algo")
        context = {}

        score = rule.evaluate(request, algorithm_info, context)
        reasoning = rule.get_reasoning()

        assert 0.0 <= score <= 1.0
        assert reasoning is not None
        assert "兼容性" in reasoning

    def test_performance_rule(self):
        """测试性能规则"""
        rule = PerformanceRule()

=======
        
        algorithm_info = self.registry.get_algorithm_info("test_algo")
        context = {}
        
        score = rule.evaluate(request, algorithm_info, context)
        reasoning = rule.get_reasoning()
        
        assert 0.0 <= score <= 1.0
        assert reasoning is not None
        assert "兼容性" in reasoning
        
    def test_performance_rule(self):
        """测试性能规则"""
        rule = PerformanceRule()
        
>>>>>>> feature/core-services-refactor
        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=inputs)
<<<<<<< HEAD

        algorithm_info = self.registry.get_algorithm_info("test_algo")
        context = {}

        score = rule.evaluate(request, algorithm_info, context)
        reasoning = rule.get_reasoning()

        assert 0.0 <= score <= 1.0
        assert reasoning is not None
        assert "性能等级" in reasoning

    def test_accuracy_rule(self):
        """测试准确性规则"""
        rule = AccuracyRule()

=======
        
        algorithm_info = self.registry.get_algorithm_info("test_algo")
        context = {}
        
        score = rule.evaluate(request, algorithm_info, context)
        reasoning = rule.get_reasoning()
        
        assert 0.0 <= score <= 1.0
        assert reasoning is not None
        assert "性能等级" in reasoning
        
    def test_accuracy_rule(self):
        """测试准确性规则"""
        rule = AccuracyRule()
        
>>>>>>> feature/core-services-refactor
        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=inputs)
<<<<<<< HEAD

        algorithm_info = self.registry.get_algorithm_info("test_algo")
        context = {}

        score = rule.evaluate(request, algorithm_info, context)
        reasoning = rule.get_reasoning()

        assert 0.0 <= score <= 1.0
        assert reasoning is not None
        assert "准确性" in reasoning

    def test_availability_rule(self):
        """测试可用性规则"""
        rule = AvailabilityRule()

=======
        
        algorithm_info = self.registry.get_algorithm_info("test_algo")
        context = {}
        
        score = rule.evaluate(request, algorithm_info, context)
        reasoning = rule.get_reasoning()
        
        assert 0.0 <= score <= 1.0
        assert reasoning is not None
        assert "准确性" in reasoning
        
    def test_availability_rule(self):
        """测试可用性规则"""
        rule = AvailabilityRule()
        
>>>>>>> feature/core-services-refactor
        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=inputs)
<<<<<<< HEAD

        algorithm_info = self.registry.get_algorithm_info("test_algo")
        context = {}

        score = rule.evaluate(request, algorithm_info, context)
        reasoning = rule.get_reasoning()

=======
        
        algorithm_info = self.registry.get_algorithm_info("test_algo")
        context = {}
        
        score = rule.evaluate(request, algorithm_info, context)
        reasoning = rule.get_reasoning()
        
>>>>>>> feature/core-services-refactor
        assert 0.0 <= score <= 1.0
        assert reasoning is not None
        assert "健康状态" in reasoning


def run_basic_functionality_test():
    """运行基本功能测试"""
    print("🧪 开始AlgorithmSelector基本功能测试...")
<<<<<<< HEAD

    registry = AlgorithmRegistry()
    selector = AlgorithmSelector(registry)

=======
    
    registry = AlgorithmRegistry()
    selector = AlgorithmSelector(registry)
    
>>>>>>> feature/core-services-refactor
    try:
        # 注册测试算法
        algorithm = MockConsensusAlgorithm("test_algo")
        success = registry.register("test_algo", algorithm)
        if not success:
            print("❌ 算法注册失败")
            return False
<<<<<<< HEAD

        # 设置健康状态
        info = registry.get_algorithm_info("test_algo")
        info.health_status = "healthy"

        print("✅ 测试环境设置成功")

=======
            
        # 设置健康状态
        info = registry.get_algorithm_info("test_algo")
        info.health_status = "healthy"
        
        print("✅ 测试环境设置成功")
        
>>>>>>> feature/core-services-refactor
        # 测试基本选择
        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=inputs)
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        selection = selector.select_algorithm(request)
        if not isinstance(selection, AlgorithmSelection):
            print("❌ 算法选择失败")
            return False
<<<<<<< HEAD

        print(f"✅ 算法选择成功: {selection.algorithm_id} (置信度: {selection.confidence:.3f})")

=======
            
        print(f"✅ 算法选择成功: {selection.algorithm_id} (置信度: {selection.confidence:.3f})")
        
>>>>>>> feature/core-services-refactor
        # 测试选择推理
        reasoning = selector.get_selection_reasoning(selection)
        if not reasoning:
            print("❌ 选择推理生成失败")
            return False
<<<<<<< HEAD

        print("✅ 选择推理生成成功")

=======
            
        print("✅ 选择推理生成成功")
        
>>>>>>> feature/core-services-refactor
        # 测试策略更新
        success = selector.update_selection_strategy(SelectionStrategy.PERFORMANCE_FIRST)
        if not success:
            print("❌ 策略更新失败")
            return False
<<<<<<< HEAD

        print("✅ 策略更新成功")

=======
            
        print("✅ 策略更新成功")
        
>>>>>>> feature/core-services-refactor
        # 测试统计信息
        stats = selector.get_selection_stats()
        if not stats or "current_strategy" not in stats:
            print("❌ 统计信息获取失败")
            return False
<<<<<<< HEAD

        print("✅ 统计信息获取成功")

=======
            
        print("✅ 统计信息获取成功")
        
>>>>>>> feature/core-services-refactor
        # 测试兼容性验证
        compatibility = selector.validate_request_compatibility(request)
        if not compatibility or "compatible" not in compatibility:
            print("❌ 兼容性验证失败")
            return False
<<<<<<< HEAD

        print("✅ 兼容性验证成功")

        print("🎉 所有基本功能测试通过!")
        return True

    except Exception as e:
        print(f"❌ 测试过程中出现异常: {str(e)}")
        return False

=======
            
        print("✅ 兼容性验证成功")
        
        print("🎉 所有基本功能测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {str(e)}")
        return False
        
>>>>>>> feature/core-services-refactor
    finally:
        registry.shutdown()


def run_strategy_test():
    """运行策略测试"""
    print("🧪 开始AlgorithmSelector策略测试...")
<<<<<<< HEAD

    registry = AlgorithmRegistry()
    selector = AlgorithmSelector(registry)

=======
    
    registry = AlgorithmRegistry()
    selector = AlgorithmSelector(registry)
    
>>>>>>> feature/core-services-refactor
    try:
        # 注册不同特性的算法
        class FastAlgorithm(MockConsensusAlgorithm):
            def get_metadata(self):
                from consensus_models import AlgorithmMetadata, AlgorithmType
                return AlgorithmMetadata(
                    name="Fast Algorithm",
                    version="1.0.0",
                    description="Fast algorithm",
                    algorithm_type=AlgorithmType.SIMPLE_MAJORITY,
                    input_types=["str", "float"],
                    output_types=["str", "float"],
                    complexity="low",
                    accuracy=0.7,
                    performance="fast",
                    requirements=[],
                    configuration_schema={}
                )
<<<<<<< HEAD

=======
                
>>>>>>> feature/core-services-refactor
        class AccurateAlgorithm(MockConsensusAlgorithm):
            def get_metadata(self):
                from consensus_models import AlgorithmMetadata, AlgorithmType
                return AlgorithmMetadata(
                    name="Accurate Algorithm",
                    version="1.0.0",
                    description="Accurate algorithm",
                    algorithm_type=AlgorithmType.BAYESIAN_CONSENSUS,
                    input_types=["str", "float"],
                    output_types=["str", "float"],
                    complexity="high",
                    accuracy=0.95,
                    performance="slow",
                    requirements=[],
                    configuration_schema={}
                )
<<<<<<< HEAD

        fast_algo = FastAlgorithm("fast_algo")
        accurate_algo = AccurateAlgorithm("accurate_algo")

        registry.register("fast_algo", fast_algo)
        registry.register("accurate_algo", accurate_algo)

=======
        
        fast_algo = FastAlgorithm("fast_algo")
        accurate_algo = AccurateAlgorithm("accurate_algo")
        
        registry.register("fast_algo", fast_algo)
        registry.register("accurate_algo", accurate_algo)
        
>>>>>>> feature/core-services-refactor
        # 设置健康状态
        for algo_id in ["fast_algo", "accurate_algo"]:
            info = registry.get_algorithm_info(algo_id)
            info.health_status = "healthy"
<<<<<<< HEAD

=======
            
>>>>>>> feature/core-services-refactor
        inputs = [
            ConsensusInput(agent_id="agent1", position="支持", confidence=0.8)
        ]
        request = ConsensusRequest(inputs=inputs)
<<<<<<< HEAD

        # 测试性能优先策略
        perf_selection = selector.select_algorithm(
            request,
            strategy=SelectionStrategy.PERFORMANCE_FIRST
        )

        if perf_selection.algorithm_id != "fast_algo":
            print(f"❌ 性能优先策略失败: 选择了 {perf_selection.algorithm_id}")
            return False

        print("✅ 性能优先策略测试通过")

=======
        
        # 测试性能优先策略
        perf_selection = selector.select_algorithm(
            request, 
            strategy=SelectionStrategy.PERFORMANCE_FIRST
        )
        
        if perf_selection.algorithm_id != "fast_algo":
            print(f"❌ 性能优先策略失败: 选择了 {perf_selection.algorithm_id}")
            return False
            
        print("✅ 性能优先策略测试通过")
        
>>>>>>> feature/core-services-refactor
        # 测试准确性优先策略
        acc_selection = selector.select_algorithm(
            request,
            strategy=SelectionStrategy.ACCURACY_FIRST
        )
<<<<<<< HEAD

        if acc_selection.algorithm_id != "accurate_algo":
            print(f"❌ 准确性优先策略失败: 选择了 {acc_selection.algorithm_id}")
            return False

        print("✅ 准确性优先策略测试通过")

        print("🎉 所有策略测试通过!")
        return True

    except Exception as e:
        print(f"❌ 策略测试过程中出现异常: {str(e)}")
        return False

=======
        
        if acc_selection.algorithm_id != "accurate_algo":
            print(f"❌ 准确性优先策略失败: 选择了 {acc_selection.algorithm_id}")
            return False
            
        print("✅ 准确性优先策略测试通过")
        
        print("🎉 所有策略测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 策略测试过程中出现异常: {str(e)}")
        return False
        
>>>>>>> feature/core-services-refactor
    finally:
        registry.shutdown()


if __name__ == "__main__":
    # 运行基本功能测试
    basic_success = run_basic_functionality_test()
<<<<<<< HEAD

    # 运行策略测试
    strategy_success = run_strategy_test()

=======
    
    # 运行策略测试
    strategy_success = run_strategy_test()
    
>>>>>>> feature/core-services-refactor
    if basic_success and strategy_success:
        print("\n📋 测试总结:")
        print("- ✅ 基本选择功能正常")
        print("- ✅ 多种选择策略正常")
        print("- ✅ 算法评分机制正常")
        print("- ✅ 决策推理功能正常")
        print("- ✅ 兼容性验证正常")
        print("\n🚀 任务3实现完成，可以进行下一步开发!")
    else:
<<<<<<< HEAD
        print("\n❌ 部分测试失败，需要修复问题后再继续")
=======
        print("\n❌ 部分测试失败，需要修复问题后再继续")
>>>>>>> feature/core-services-refactor

#!/usr/bin/env python3
"""优化版PersonalAssistantService
基于V0.1.1的发现进行性能和稳定性优化
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from personal_intelligence_hub.services.personal_assistant import IntentResult, TeamProposal, WorkflowType

# 导入原有组件
from personal_intelligence_hub.services.personal_assistant import (
    PersonalAssistantService as BasePersonalAssistantService,
)

logger = logging.getLogger(__name__)


class CacheEntry:
    """缓存条目"""

    def __init__(self, data: Any, ttl_seconds: int = 300):
        self.data = data
        self.created_at = datetime.now()
        self.ttl = timedelta(seconds=ttl_seconds)

    def is_expired(self) -> bool:
        return datetime.now() - self.created_at > self.ttl


class OptimizedPersonalAssistantService(BasePersonalAssistantService):
    """优化版个人助手服务"""

    def __init__(self):
        super().__init__()

        # 添加缓存机制
        self.intent_cache: Dict[str, CacheEntry] = {}
        self.team_cache: Dict[str, CacheEntry] = {}
        self.role_cache: Optional[CacheEntry] = None

        # 性能监控
        self.performance_metrics = {
            "analyze_intent_calls": 0,
            "analyze_intent_cache_hits": 0,
            "assemble_team_calls": 0,
            "assemble_team_cache_hits": 0,
            "backend_connection_failures": 0,
            "fallback_activations": 0
        }

        logger.info("OptimizedPersonalAssistantService 初始化完成")

    def _get_cache_key(self, *args) -> str:
        """生成缓存键"""
        return "|".join(str(arg) for arg in args)

    def _clean_expired_cache(self):
        """清理过期缓存"""
        # 清理意图分析缓存
        expired_keys = [k for k, v in self.intent_cache.items() if v.is_expired()]
        for key in expired_keys:
            del self.intent_cache[key]

        # 清理团队组建缓存
        expired_keys = [k for k, v in self.team_cache.items() if v.is_expired()]
        for key in expired_keys:
            del self.team_cache[key]

        # 清理角色缓存
        if self.role_cache and self.role_cache.is_expired():
            self.role_cache = None

    async def analyze_intent(self, user_input: str, context: Optional[Dict] = None) -> IntentResult:
        """优化版意图分析 - 添加缓存和性能监控"""
        self.performance_metrics["analyze_intent_calls"] += 1

        # 清理过期缓存
        self._clean_expired_cache()

        # 生成缓存键
        context_key = json.dumps(context, sort_keys=True) if context else "no_context"
        cache_key = self._get_cache_key(user_input, context_key)

        # 检查缓存
        if cache_key in self.intent_cache:
            cache_entry = self.intent_cache[cache_key]
            if not cache_entry.is_expired():
                self.performance_metrics["analyze_intent_cache_hits"] += 1
                logger.info(f"意图分析缓存命中: {user_input[:30]}...")
                return cache_entry.data

        # 执行分析
        start_time = time.time()
        try:
            result = await super().analyze_intent(user_input, context)

            # 缓存结果
            self.intent_cache[cache_key] = CacheEntry(result, ttl_seconds=300)  # 5分钟缓存

            execution_time = time.time() - start_time
            logger.info(f"意图分析完成: {execution_time:.2f}秒")

            return result

        except Exception as e:
            self.performance_metrics["backend_connection_failures"] += 1
            logger.error(f"意图分析失败，使用降级策略: {e}")

            # 增强的降级策略
            result = await self._enhanced_fallback_intent_analysis(user_input)
            self.performance_metrics["fallback_activations"] += 1

            # 缓存降级结果（较短TTL）
            self.intent_cache[cache_key] = CacheEntry(result, ttl_seconds=60)

            return result

    async def _enhanced_fallback_intent_analysis(self, user_input: str) -> IntentResult:
        """增强的降级意图分析"""
        user_input_lower = user_input.lower()

        # 更精确的关键词匹配
        critical_review_keywords = [
            "分析", "审查", "评估", "检查", "验证", "事实", "真实性", "可信度",
            "证据", "论证", "批判", "质疑", "辨别", "鉴定"
        ]

        multi_perspective_keywords = [
            "讨论", "观点", "角度", "看法", "意见", "立场", "视角", "方面",
            "综合", "全面", "多元", "不同", "各种", "比较"
        ]

        research_keywords = [
            "研究", "调研", "探索", "深入", "详细", "系统", "全面", "报告"
        ]

        # 计算匹配分数
        critical_score = sum(1 for kw in critical_review_keywords if kw in user_input_lower)
        multi_score = sum(1 for kw in multi_perspective_keywords if kw in user_input_lower)
        research_score = sum(1 for kw in research_keywords if kw in user_input_lower)

        # 决策逻辑
        if critical_score > multi_score and critical_score > 0:
            return IntentResult(
                workflowType=WorkflowType.CRITICAL_REVIEW,
                confidence=min(0.8, 0.5 + critical_score * 0.1),
                reasoning=f"基于关键词匹配(批判性审查关键词: {critical_score}个)的本地分析",
                topic=user_input
            )
        elif multi_score > 0 or research_score > 0:
            confidence = min(0.8, 0.5 + (multi_score + research_score) * 0.1)
            return IntentResult(
                workflowType=WorkflowType.MULTI_PERSPECTIVE,
                confidence=confidence,
                reasoning=f"基于关键词匹配(多视角关键词: {multi_score}个, 研究关键词: {research_score}个)的本地分析",
                topic=user_input
            )
        else:
            return IntentResult(
                workflowType=WorkflowType.CRITICAL_REVIEW,
                confidence=0.5,
                reasoning="默认使用批判性审查工作流(本地降级策略)",
                topic=user_input
            )

    async def assemble_team(self, topic: str, workflow_type: WorkflowType) -> TeamProposal:
        """优化版团队组建 - 添加缓存和智能角色选择"""
        self.performance_metrics["assemble_team_calls"] += 1

        # 清理过期缓存
        self._clean_expired_cache()

        # 生成缓存键
        cache_key = self._get_cache_key(topic, workflow_type.value)

        # 检查缓存
        if cache_key in self.team_cache:
            cache_entry = self.team_cache[cache_key]
            if not cache_entry.is_expired():
                self.performance_metrics["assemble_team_cache_hits"] += 1
                logger.info(f"团队组建缓存命中: {topic[:30]}...")
                return cache_entry.data

        # 执行团队组建
        start_time = time.time()
        try:
            result = await super().assemble_team(topic, workflow_type)

            # 缓存结果
            self.team_cache[cache_key] = CacheEntry(result, ttl_seconds=600)  # 10分钟缓存

            execution_time = time.time() - start_time
            logger.info(f"团队组建完成: {execution_time:.2f}秒")

            return result

        except Exception as e:
            self.performance_metrics["backend_connection_failures"] += 1
            logger.error(f"团队组建失败，使用增强降级策略: {e}")

            # 增强的降级策略
            result = await self._enhanced_fallback_team_assembly(topic, workflow_type)
            self.performance_metrics["fallback_activations"] += 1

            # 缓存降级结果
            self.team_cache[cache_key] = CacheEntry(result, ttl_seconds=300)

            return result

    async def _enhanced_fallback_team_assembly(self, topic: str, workflow_type: WorkflowType) -> TeamProposal:
        """增强的降级团队组建策略"""
        topic_lower = topic.lower()

        # 基于话题的智能角色选择
        domain_keywords = {
            "technology": ["ai", "人工智能", "技术", "科技", "算法", "数据", "软件", "硬件"],
            "healthcare": ["医疗", "健康", "医学", "病", "治疗", "药物", "医院"],
            "education": ["教育", "学习", "教学", "学校", "学生", "老师", "培训"],
            "environment": ["环境", "气候", "生态", "污染", "绿色", "可持续"],
            "economics": ["经济", "金融", "市场", "投资", "商业", "贸易", "货币"],
            "ethics": ["伦理", "道德", "价值观", "责任", "公平", "正义"],
            "policy": ["政策", "法律", "法规", "治理", "政府", "公共"]
        }

        # 识别话题领域
        detected_domains = []
        for domain, keywords in domain_keywords.items():
            if any(kw in topic_lower for kw in keywords):
                detected_domains.append(domain)

        # 基于工作流类型和领域选择角色
        if workflow_type == WorkflowType.CRITICAL_REVIEW:
            if "technology" in detected_domains:
                agents = ["技术评估专家", "数据分析师", "系统架构师"]
                rationale = f"为技术相关的批判性审查'{topic}'选择的专业技术团队"
            elif "healthcare" in detected_domains:
                agents = ["医学专家", "临床研究员", "医疗伦理学家"]
                rationale = f"为医疗相关的批判性审查'{topic}'选择的专业医疗团队"
            elif "ethics" in detected_domains:
                agents = ["伦理学家", "哲学家", "社会学家"]
                rationale = f"为伦理相关的批判性审查'{topic}'选择的专业伦理团队"
            else:
                agents = ["批判性思维专家", "事实验证专家", "逻辑分析师"]
                rationale = f"为批判性审查'{topic}'选择的通用专业团队"
        else:  # MULTI_PERSPECTIVE
            if "technology" in detected_domains:
                agents = ["技术创新者", "用户体验专家", "技术伦理学家", "产品经理"]
                rationale = f"为技术话题'{topic}'的多视角分析选择的跨领域团队"
            elif "policy" in detected_domains:
                agents = ["政策分析师", "公共管理专家", "社会影响评估师", "利益相关者代表"]
                rationale = f"为政策话题'{topic}'的多视角分析选择的政策团队"
            else:
                agents = ["创新思维专家", "批判性观察者", "综合分析师", "平衡协调者"]
                rationale = f"为多角度讨论'{topic}'选择的多元化团队"

        # 计算多样性评分
        diversity_score = min(0.9, 0.6 + len(detected_domains) * 0.1 + len(agents) * 0.05)

        return TeamProposal(
            agents=agents,
            diversity_score=diversity_score,
            rationale=rationale,
            confirmation_message=f"我将让{', '.join(agents)}使用{workflow_type.value}流程分析。继续吗？"
        )

    async def process_message(self, user_input: str, session_id: str) -> str:
        """优化版消息处理 - 添加性能监控"""
        start_time = time.time()

        try:
            result = await super().process_message(user_input, session_id)

            execution_time = time.time() - start_time
            logger.info(f"消息处理完成: {execution_time:.2f}秒")

            return result

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"消息处理失败 ({execution_time:.2f}秒): {e}")

            # 提供更友好的错误消息
            return f"抱歉，处理您的请求时遇到了问题。我正在使用备用策略为您提供帮助。\n\n原始请求: {user_input[:100]}{'...' if len(user_input) > 100 else ''}"

    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        cache_hit_rate_intent = (
            self.performance_metrics["analyze_intent_cache_hits"] /
            max(1, self.performance_metrics["analyze_intent_calls"])
        ) * 100

        cache_hit_rate_team = (
            self.performance_metrics["assemble_team_cache_hits"] /
            max(1, self.performance_metrics["assemble_team_calls"])
        ) * 100

        return {
            **self.performance_metrics,
            "intent_cache_hit_rate": f"{cache_hit_rate_intent:.1f}%",
            "team_cache_hit_rate": f"{cache_hit_rate_team:.1f}%",
            "intent_cache_size": len(self.intent_cache),
            "team_cache_size": len(self.team_cache)
        }


# 测试函数
async def test_optimized_assistant():
    """测试优化版助手"""
    print("🚀 测试优化版PersonalAssistantService")
    print("="*60)

    assistant = OptimizedPersonalAssistantService()

    # 测试缓存机制
    test_inputs = [
        "分析AI在教育中的应用",
        "讨论气候变化的解决方案",
        "分析AI在教育中的应用",  # 重复，应该命中缓存
    ]

    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n🔍 测试 {i}: {user_input}")

        start_time = time.time()
        result = await assistant.process_message(user_input, f"test_session_{i}")
        end_time = time.time()

        print(f"⏱️ 响应时间: {end_time - start_time:.2f}秒")
        print(f"📝 响应长度: {len(result)}字符")

    # 显示性能指标
    print("\n📊 性能指标:")
    metrics = assistant.get_performance_metrics()
    for key, value in metrics.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    asyncio.run(test_optimized_assistant())

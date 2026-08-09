"""
大模型任务分解与执行集成器
将任务分解引擎集成到现有的意图识别和执行流程中
"""

import asyncio
from typing import Any

from daip_live.task_decomposition.task_decomposition_engine import (
    SequentialTaskExecutor,
    TaskDecompositionEngine,
)
from daip_live.task_decomposition.task_visualization import (
    get_task_visualization_manager,
)


class TaskDecompositionIntegrator:
    """任务分解集成器 - 将任务分解功能集成到现有流程中"""

    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        self.decomposer = TaskDecompositionEngine(model_provider)
        self.executor = SequentialTaskExecutor(model_provider)
        self.visualization_manager = get_task_visualization_manager()

    async def should_decompose_request(self, user_request: str) -> bool:
        """判断用户请求是否需要分解"""
        return await self.decomposer.should_decompose_task(user_request)

    async def decompose_and_execute(self, user_request: str) -> dict[str, Any]:
        """分解并执行用户的复杂请求"""

        # 1. 分解任务
        tasks = await self.decomposer.decompose_task(user_request)

        # 更新可视化管理器中的任务
        self.visualization_manager.update_and_display(tasks, user_request)

        # 2. 执行任务（需要修改执行器以支持可视化更新）
        results = await self.executor.execute_decomposed_tasks_with_visualization(
            tasks, user_request, self.visualization_manager
        )

        # 最终显示完成状态
        self.visualization_manager.update_and_display(tasks, user_request)

        return results

    def get_execution_summary(self, execution_results: dict[str, Any]) -> str:
        """生成执行摘要"""
        summary = f"""任务分解执行摘要:
- 原始请求: {execution_results["original_request"][:100]}...
- 总任务数: {execution_results["total_tasks"]}
- 成功任务: {execution_results["completed_tasks"]}
- 失败任务: {execution_results["failed_tasks"]}
- 执行摘要: {execution_results["final_result"][:300]}..."""

        return summary


# 集成到意图识别器中
def integrate_task_decomposition(intent_recognizer, model_provider=None):
    """将任务分解功能集成到意图识别器中"""
    integrator = TaskDecompositionIntegrator(model_provider)

    # 保存原始的意图识别方法
    original_recognize_intent = intent_recognizer.recognize_intent

    # 创建新的意图识别方法，包含任务分解逻辑
    def enhanced_recognize_intent(text: str, session_id: str = "default"):
        # 首先使用原始逻辑进行意图识别
        intent = original_recognize_intent(text, session_id)

        # 如果没有识别到明确意图，或者判断该请求很复杂，则考虑任务分解
        if not intent or intent.name in ["question", "execute_skill", "chat"]:
            # 检查是否需要任务分解
            import asyncio

            try:
                # 使用当前事件循环检查是否需要分解
                asyncio.get_running_loop()
                integrator.should_decompose_request(text)

                # 创建一个新的协程包装来运行异步函数
                async def check_decomposition():
                    return await integrator.should_decompose_request(text)

            except RuntimeError:
                # 没有活跃的事件循环，使用临时循环
                import asyncio

                should_decompose = asyncio.run(
                    integrator.should_decompose_request(text)
                )

                if should_decompose:
                    # 标记此请求需要进行任务分解处理
                    if not hasattr(intent, "requires_task_decomposition"):
                        # 如果没有识别到明确意图，创建一个特殊意图
                        if not intent:
                            from daip_live.core.models import Intent, IntentType

                            intent = Intent(
                                name="task_decomposition",
                                confidence=0.8,
                                description="需要任务分解的复杂请求",
                                parameters={"user_request": text},
                                intent_type=IntentType.WORKFLOW,
                                requires_confidence_check=False,
                            )

                        # 添加任务分解标记
                        intent.requires_task_decomposition = True
                        intent.task_decomposition_integrator = integrator

        return intent

    # 替换原方法
    intent_recognizer.recognize_intent = enhanced_recognize_intent
    intent_recognizer.task_decomposition_integrator = integrator

    return intent_recognizer


# 执行器增强功能
def enhance_executor_with_task_decomposition(executor):
    """为执行器增强任务分解功能"""

    # 保存原始执行方法
    original_execute = executor.execute if hasattr(executor, "execute") else None

    async def enhanced_execute(user_request: str):
        """增强的执行方法，支持任务分解"""

        # 首先检查是否已经有了任务分解功能
        if hasattr(executor, "task_decomposition_integrator"):
            integrator = executor.task_decomposition_integrator

            # 检查是否需要任务分解
            should_decompose = await integrator.should_decompose_request(user_request)

            if should_decompose:
                # 执行任务分解和执行流程
                results = await integrator.decompose_and_execute(user_request)

                return {
                    "type": "task_decomposition_result",
                    "results": results,
                    "summary": integrator.get_execution_summary(results),
                }

        # 如果不需要任务分解或没有集成器，使用原始逻辑
        if original_execute:
            return await original_execute(user_request)
        else:
            # 如果没有原始执行方法，返回基本响应
            return {
                "type": "simple_response",
                "response": "思考中...",
                "request": user_request,
            }

    # 添加增强的执行方法
    executor.enhanced_execute = enhanced_execute

    # 如果原始执行器有execute方法，则替换
    if original_execute:
        executor.execute = enhanced_execute

    return executor


# 测试集成
async def test_integration():
    """测试集成功能"""

    # 创建模拟模型提供者
    class MockModelProvider:
        async def generate(self, prompt: str):
            if "分解为多个具体的、可执行的子任务" in prompt:
                return """TASKS:
1. 信息收集: 收集人工智能医疗应用的现状信息
2. 前景分析: 分析AI在医疗领域的发展前景
3. 挑战评估: 评估面临的主要挑战和障碍
4. 建议总结: 总结发展前景和应对建议"""
            elif "执行以下子任务" in prompt:
                subtask_title = (
                    prompt.split("子任务标题:")[1].split("\\n")[0]
                    if "子任务标题:" in prompt
                    else "分析任务"
                )
                return f"完成{subtask_title} - 详细分析结果..."
            else:
                return "这是对原始复杂请求的完整分析回答。"

    mock_provider = MockModelProvider()

    # 创建集成器并测试
    integrator = TaskDecompositionIntegrator(mock_provider)

    test_request = "请帮我深入分析人工智能在医疗领域的应用前景、挑战和未来发展建议"

    # 检查是否需要分解
    should_decompose = await integrator.should_decompose_request(test_request)

    if should_decompose:
        # 执行分解和执行
        await integrator.decompose_and_execute(test_request)

    # 模拟集成到意图识别器

    class MockIntentRecognizer:
        def recognize_intent(self, text: str, session_id: str = "default"):
            # 简单模拟意图识别
            if "分析" in text or "研究" in text:
                return type(
                    "MockIntent",
                    (),
                    {
                        "name": "execute_skill",
                        "confidence": 0.7,
                        "description": "技能执行",
                        "parameters": {"content": text},
                    },
                )()
            else:
                return None

    recognizer = MockIntentRecognizer()
    integrate_task_decomposition(recognizer, mock_provider)

    # 模拟执行器集成

    class MockExecutor:
        pass

    executor = MockExecutor()
    enhance_executor_with_task_decomposition(executor)


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_integration())

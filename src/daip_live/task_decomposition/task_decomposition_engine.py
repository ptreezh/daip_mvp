"""
大模型自动任务分解引擎
当处理复杂问题时，自动分解为有序待办事项并逐步执行
"""

import asyncio
import re
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class DecomposedTask:
    """分解后的任务项"""

    id: str
    title: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    dependencies: list[str] = None  # 依赖的其他任务ID
    metadata: dict[str, Any] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now()


class TaskDecompositionEngine:
    """任务分解引擎 - 将复杂任务分解为可执行的待办事项"""

    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        self.task_pattern_indicators = [
            # 研究性质的复杂任务
            "分析.*方法",
            "研究.*技术",
            "调查.*原因",
            "探讨.*机制",
            # 综合性的复杂任务
            "设计.*系统",
            "构建.*框架",
            "开发.*解决方案",
            # 多步骤的复杂任务
            "制定.*策略",
            "实现.*功能",
            "创建.*平台",
            # 评估性质的复杂任务
            "评估.*影响",
            "比较.*优劣",
            "验证.*可行性",
            # 综合报告类
            "撰写.*报告",
            "编写.*方案",
            "总结.*经验",
        ]

        # 复杂任务的关键词
        self.complexity_indicators = [
            "复杂",
            "困难",
            "多层次",
            "多维度",
            "综合",
            "系统",
            "全面",
            "深入",
            "详细",
            "多方面",
            "交叉",
            "跨领域",
            "集成",
            "综合性",
            "整体",
            "宏观",
            "微观",
            "多层次",
        ]

    async def should_decompose_task(self, user_request: str) -> bool:
        """
        判断是否需要分解任务
        """
        # 检查是否包含复杂任务关键词
        user_request_lower = user_request.lower()

        # 如果包含复杂性指示词
        for indicator in self.complexity_indicators:
            if indicator in user_request_lower:
                return True

        # 检查是否匹配任务模式
        for pattern in self.task_pattern_indicators:
            if re.search(pattern, user_request_lower):
                return True

        # 扩大复杂任务的判断范围
        # 检查句子长度和复杂度
        if len(user_request) > 20:  # 降低长度阈值
            # 检查是否包含多个动作词
            action_words = [
                "分析",
                "设计",
                "实现",
                "开发",
                "研究",
                "评估",
                "验证",
                "比较",
                "总结",
                "制定",
                "构建",
                "创建",
                "管理",
                "优化",
                "改进",
                "探索",
                "调查",
                "撰写",
                "规划",
                "建立",
                "配置",
            ]
            action_count = sum(1 for word in action_words if word in user_request)
            if action_count >= 1:  # 降低动作词数量要求
                return True

        # 检查是否包含复杂任务关键词
        complex_keywords = [
            "系统",
            "平台",
            "框架",
            "架构",
            "方案",
            "模型",
            "流程",
            "机制",
            "体系",
            "结构",
            "多",
            "多种",
            "多个",
            "复合",
            "综合",
            "全方位",
            "智能化",
            "自动化",
            "高级",
            "深度",
        ]
        for keyword in complex_keywords:
            if keyword in user_request_lower:
                return True

        # 如果有大模型，可以用AI判断
        if self.model_provider:
            try:
                prompt = f"""请判断以下用户请求是否属于复杂任务，需要分解为多个子步骤来完成。

用户请求：{user_request}

如果是复杂任务，请回复"YES"，否则回复"NO"。

复杂任务通常包含：
- 需要多个步骤才能完成
- 涉及多个方面或领域
- 需要详细分析或深入研究
- 涉及系统性工作
- 请求内容较长较具体

回复格式：YES 或 NO"""  # noqa: E501

                response = await self.model_provider.generate(prompt)
                response_text = (
                    str(response) if isinstance(response, dict) else response
                )

                return "YES" in response_text.upper() or "是" in response_text
            except Exception:
                # 如果AI调用失败，回退到基于规则的判断
                pass

        return False

    async def decompose_task(self, user_request: str) -> list[DecomposedTask]:
        """
        将复杂任务分解为多个可执行的任务
        """

        # 如果有大模型，使用AI进行智能分解
        if self.model_provider:
            return await self._decompose_with_ai(user_request)
        else:
            # 使用基于规则的分解
            return self._decompose_with_rules(user_request)

    async def _decompose_with_ai(self, user_request: str) -> list[DecomposedTask]:
        """使用AI辅助进行任务分解"""
        prompt = f"""请将以下复杂任务分解为3-8个具体的、可执行的子任务。

用户任务：{user_request}

请按照以下格式回复：
TASKS:
1. [任务标题]: [任务描述]
2. [任务标题]: [任务描述]
3. [任务标题]: [任务描述]

要求：
- 每个子任务应该具体明确，可单独执行
- 任务间应有逻辑顺序关系
- 任务描述要清晰，包含执行要点
- 优先级从高到低排列关键任务"""

        try:
            response = await self.model_provider.generate(prompt)
            response_text = str(response) if isinstance(response, dict) else response

            # 解析AI返回的任务列表
            tasks = self._parse_ai_tasks(response_text)
            return tasks

        except Exception:
            return self._decompose_with_rules(user_request)

    def _parse_ai_tasks(self, ai_response: str) -> list[DecomposedTask]:
        """解析AI返回的任务列表"""
        tasks = []

        # 查找TASKS:后面的列表
        import re

        matches = re.findall(r"(\d+)\.\s*([^:\n]+):\s*([^\n]+)", ai_response)

        for idx, title, description in matches:
            task = DecomposedTask(
                id=f"task_{uuid.uuid4().hex[:8]}",
                title=title.strip(),
                description=description.strip(),
            )
            tasks.append(task)

        # 如果没有找到匹配的任务，尝试其他格式
        if not tasks:
            # 尝试匹配 "1. 任务标题 - 任务描述" 格式
            matches = re.findall(r"(\d+)\.\s*([^-]+)-\s*([^\n]+)", ai_response)
            for idx, title, description in matches:
                task = DecomposedTask(
                    id=f"task_{uuid.uuid4().hex[:8]}",
                    title=title.strip(),
                    description=description.strip(),
                )
                tasks.append(task)

        # 如果还是没有找到，创建一个默认任务
        if not tasks:
            tasks.append(
                DecomposedTask(
                    id=f"task_{uuid.uuid4().hex[:8]}",
                    title="处理请求",
                    description=ai_response[:100]
                    if len(ai_response) > 100
                    else ai_response,
                )
            )

        return tasks

    def _decompose_with_rules(self, user_request: str) -> list[DecomposedTask]:
        """基于规则进行任务分解"""
        tasks = []

        # 根据任务类型进行不同的分解
        request_lower = user_request.lower()

        if any(
            word in request_lower
            for word in ["分析", "research", "study", "investigate"]
        ):
            # 分析类任务的分解
            steps = [
                ("信息收集", "收集与主题相关的背景信息和数据"),
                ("现状分析", "分析当前状况和存在的问题"),
                ("深入研究", "对关键点进行深入研究和分析"),
                ("总结归纳", "总结分析结果并提出见解"),
            ]
        elif any(
            word in request_lower for word in ["设计", "design", "develop", "create"]
        ):
            # 设计/开发类任务的分解
            steps = [
                ("需求分析", "明确设计或开发的具体需求"),
                ("方案设计", "设计实施方案或架构"),
                ("实现执行", "执行设计方案"),
                ("验证测试", "验证实现结果"),
            ]
        elif any(
            word in request_lower for word in ["比较", "compare", "evaluate", "assess"]
        ):
            # 比较评估类任务的分解
            steps = [
                ("标准制定", "确定比较或评估的标准"),
                ("信息收集", "收集各选项的相关信息"),
                ("对比分析", "进行详细的对比分析"),
                ("结论总结", "总结比较结果和建议"),
            ]
        else:
            # 通用分解策略
            steps = [
                ("任务理解", "深入理解任务的具体要求"),
                ("信息准备", "准备执行任务所需的信息"),
                ("执行过程", "执行任务的主要过程"),
                ("结果整理", "整理和总结执行结果"),
            ]

        for title, description in steps:
            task = DecomposedTask(
                id=f"task_{uuid.uuid4().hex[:8]}",
                title=title,
                description=f"{user_request} -> {description}",
                priority=TaskPriority.HIGH
                if title in ["执行过程", "实现执行"]
                else TaskPriority.MEDIUM,
            )
            tasks.append(task)

        return tasks


class SequentialTaskExecutor:
    """顺序任务执行器 - 按顺序执行分解后的任务"""

    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        self.current_task_index = 0
        self.tasks = []
        self.results = {}
        self.context = {}  # 任务间共享上下文

    async def execute_decomposed_tasks(
        self, tasks: list[DecomposedTask], original_request: str
    ) -> dict[str, Any]:
        """执行分解后的任务列表"""
        self.tasks = tasks
        self.original_request = original_request

        results = {
            "original_request": original_request,
            "total_tasks": len(tasks),
            "completed_tasks": 0,
            "failed_tasks": 0,
            "task_results": [],
            "final_result": "",
        }

        for i, task in enumerate(self.tasks):
            # 检查依赖任务是否完成
            if await self._check_dependencies(task):
                # 执行任务
                task_result = await self._execute_single_task(task, original_request)

                if task_result["success"]:
                    results["completed_tasks"] += 1
                    task.status = TaskStatus.COMPLETED
                    task.result = task_result["result"]
                    task.completed_at = datetime.now()

                    # 更新共享上下文
                    self.context[f"task_{i}_result"] = task_result["result"]
                    self.context[f"task_{i}_title"] = task.title
                else:
                    results["failed_tasks"] += 1
                    task.status = TaskStatus.FAILED
                    task.error = task_result.get("error", "Unknown error")
                    # 对于失败的任务，可以选择继续或停止
            else:
                task.status = TaskStatus.SKIPPED
                results["task_results"].append(
                    {
                        "task_id": task.id,
                        "title": task.title,
                        "status": "skipped",
                        "error": "Dependencies not met",
                    }
                )
                continue

            results["task_results"].append(
                {
                    "task_id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status.value,
                    "result": task.result,
                    "error": task.error,
                }
            )

        # 生成最终结果
        final_result = await self._synthesize_final_result(results)
        results["final_result"] = final_result

        return results

    async def execute_decomposed_tasks_with_visualization(
        self, tasks: list[DecomposedTask], original_request: str, visualization_manager
    ) -> dict[str, Any]:
        """执行分解后的任务列表，并实时更新可视化界面"""
        self.tasks = tasks
        self.original_request = original_request

        results = {
            "original_request": original_request,
            "total_tasks": len(tasks),
            "completed_tasks": 0,
            "failed_tasks": 0,
            "task_results": [],
            "final_result": "",
        }

        for i, task in enumerate(self.tasks):
            # 更新可视化：标记当前任务为进行中
            visualization_manager.update_task_status(task.id, TaskStatus.IN_PROGRESS)
            visualization_manager.update_and_display(tasks, original_request)

            # 检查依赖任务是否完成
            if await self._check_dependencies(task):
                # 执行任务
                task_result = await self._execute_single_task(task, original_request)

                if task_result["success"]:
                    results["completed_tasks"] += 1
                    task.status = TaskStatus.COMPLETED
                    task.result = task_result["result"]
                    task.completed_at = datetime.now()

                    # 更新可视化：标记为已完成
                    visualization_manager.update_task_status(
                        task.id, TaskStatus.COMPLETED, task_result["result"]
                    )
                    visualization_manager.update_and_display(tasks, original_request)

                    # 更新共享上下文
                    self.context[f"task_{i}_result"] = task_result["result"]
                    self.context[f"task_{i}_title"] = task.title
                else:
                    results["failed_tasks"] += 1
                    task.status = TaskStatus.FAILED
                    task.error = task_result.get("error", "Unknown error")

                    # 更新可视化：标记为失败
                    visualization_manager.update_task_status(
                        task.id,
                        TaskStatus.FAILED,
                        task_result.get("error", "Unknown error"),
                    )
                    visualization_manager.update_and_display(tasks, original_request)

                    # 对于失败的任务，可以选择继续或停止
            else:
                task.status = TaskStatus.SKIPPED

                # 更新可视化：标记为跳过
                visualization_manager.update_task_status(
                    task.id, TaskStatus.SKIPPED, "Dependencies not met"
                )
                visualization_manager.update_and_display(tasks, original_request)

                results["task_results"].append(
                    {
                        "task_id": task.id,
                        "title": task.title,
                        "status": "skipped",
                        "error": "Dependencies not met",
                    }
                )
                continue

            results["task_results"].append(
                {
                    "task_id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status.value,
                    "result": task.result,
                    "error": task.error,
                }
            )

        # 生成最终结果
        final_result = await self._synthesize_final_result(results)
        results["final_result"] = final_result

        return results

    async def _check_dependencies(self, task: DecomposedTask) -> bool:
        """检查任务依赖是否满足"""
        for dep_id in task.dependencies:
            dep_task = next((t for t in self.tasks if t.id == dep_id), None)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True

    async def _execute_single_task(
        self, task: DecomposedTask, original_request: str
    ) -> dict[str, Any]:
        """执行单个任务"""
        try:
            task.status = TaskStatus.IN_PROGRESS

            if self.model_provider:
                # 使用大模型执行任务
                context_str = self._get_context_string()
                prompt = f"""请执行以下子任务：

子任务标题: {task.title}
子任务描述: {task.description}

原始请求: {original_request}

上下文信息: {context_str}

请专注于完成当前子任务，提供具体的结果。"""

                response = await self.model_provider.generate(prompt)
                result = str(response) if isinstance(response, dict) else response

                return {"success": True, "result": result}
            else:
                # 模拟执行
                result = f"模拟执行结果: {task.title} - {task.description}"
                return {"success": True, "result": result}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_context_string(self) -> str:
        """获取任务上下文字符串"""
        if not self.context:
            return "无前置任务结果"

        context_items = []
        for key, value in self.context.items():
            if isinstance(value, str) and len(value) > 200:
                value = value[:200] + "..."
            context_items.append(f"{key}: {value}")

        return "; ".join(context_items)

    async def _synthesize_final_result(self, execution_results: dict[str, Any]) -> str:
        """合成最终结果"""
        if self.model_provider:
            # 使用AI合成最终结果
            task_results = execution_results["task_results"]

            task_summaries = "\\n".join(
                [
                    f"- {tr['title']}: {tr['result'][:100] if tr['result'] else 'N/A'}"
                    for tr in task_results
                    if tr["status"] == "completed"
                ]
            )

            prompt = f"""请根据以下子任务执行结果，合成对原始请求的完整回答。

原始请求: {execution_results["original_request"]}

子任务执行结果:
{task_summaries}

请提供一个完整、连贯的回答，整合所有子任务的结果。"""

            try:
                response = await self.model_provider.generate(prompt)
                return str(response) if isinstance(response, dict) else response
            except Exception:
                # 如果AI合成失败，返回任务结果摘要
                return f"任务分解执行完成。\\n\\n执行了 {execution_results['total_tasks']} 个子任务，其中 {execution_results['completed_tasks']} 个成功，{execution_results['failed_tasks']} 个失败。\\n\\n子任务结果摘要:\\n{task_summaries}"  # noqa: E501
        else:
            # 简单合成结果
            return f"任务分解执行完成。总共执行了 {execution_results['total_tasks']} 个子任务。"  # noqa: E501


# 测试代码
async def test_task_decomposition():
    """测试任务分解功能"""

    # 创建模拟模型提供者（用于测试）
    class MockModelProvider:
        async def generate(self, prompt: str):
            if "分解为多个具体的、可执行的子任务" in prompt:
                return """TASKS:
1. 需求分析: 分析AI系统开发的具体需求和目标
2. 技术选型: 选择适合的技术栈和框架
3. 架构设计: 设计AI系统的整体架构
4. 模块开发: 开发各个功能模块
5. 集成测试: 进行系统集成和测试
6. 部署上线: 将系统部署到生产环境"""
            elif "执行以下子任务" in prompt:
                return f"执行结果: {prompt.split('子任务标题:')[1].split()[0] if '子任务标题:' in prompt else '模拟结果'}"  # noqa: E501
            else:
                return "综合回答：这是对原始请求的完整回答。"

    # 测试任务分解引擎
    decomposer = TaskDecompositionEngine(MockModelProvider())

    test_requests = [
        "请帮我分析人工智能在医疗领域的应用前景",
        "设计一个AI驱动的客户服务平台",
        "比较不同深度学习框架的性能差异",
        "创建一个智能客服系统的解决方案",
    ]

    for request in test_requests:
        # 检查是否需要分解
        should_decompose = await decomposer.should_decompose_task(request)

        if should_decompose:
            # 分解任务
            tasks = await decomposer.decompose_task(request)

            for i, task in enumerate(tasks, 1):
                pass

            # 执行任务
            executor = SequentialTaskExecutor(MockModelProvider())
            await executor.execute_decomposed_tasks(tasks, request)


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_task_decomposition())

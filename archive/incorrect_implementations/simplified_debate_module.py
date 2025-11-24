"""
模块化辩论系统 - 重构实现以降低复杂度
"""
import asyncio
import uuid
import re
from typing import List, Dict, Any, Optional, AsyncGenerator
from dataclasses import dataclass
from enum import Enum


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class SimpleDebateTask:
    """简化版辩论任务项"""
    id: str
    title: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 3
    result: Optional[str] = None
    error: Optional[str] = None


class SimpleDebateModule:
    """简化版辩论模块 - 降低系统复杂度的核心实现"""
    
    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        
        # 简化的复杂度检测
        self.complexity_keywords = [
            "分析.*多方面", "研究.*详细", "探讨.*机制", "设计.*系统", 
            "构建.*框架", "制定.*策略", "比较.*优劣", "评估.*影响",
            "深入.*分析", "全面.*研究", "详细.*探讨", "系统.*设计"
        ]
    
    async def should_debate_need_task_decomposition(self, topic: str) -> bool:
        """判断辩论主题是否需要任务分解 - 降低复杂度检测"""
        topic_lower = topic.lower()
        
        # 简单的复杂度判断
        for keyword in self.complexity_keywords:
            if re.search(keyword, topic_lower, re.IGNORECASE):
                return True
        
        # 长度判断
        word_count = len(topic.split())
        action_words = ["分析", "研究", "设计", "探讨", "评估", "比较", "构建", "制定"]
        action_count = sum(1 for word in action_words if word in topic_lower)
        
        return word_count > 6 and action_count >= 2
    
    async def decompose_debate_topic(self, topic: str) -> List[SimpleDebateTask]:
        """将复杂辩论主题分解为子任务"""
        if self.model_provider:
            # 使用模型进行智能分解
            prompt = f"""将以下辩论主题分解为3-6个具体的讨论角度或子议题：

辩论主题：{topic}

请返回JSON格式：
{{
    "subtopics": [
        {{"title": "子议题标题", "description": "子议题详细描述"}}
    ]
}}"""
            
            try:
                response = await self.model_provider.generate(prompt)
                response_str = str(response) if isinstance(response, dict) else response
                
                import json
                parsed = json.loads(response_str)
                subtopics = parsed.get("subtopics", [])
                
                tasks = []
                for subtopic in subtopics:
                    task = SimpleDebateTask(
                        id=f"task_{uuid.uuid4().hex[:8]}",
                        title=subtopic.get("title", "未命名议题"),
                        description=subtopic.get("description", "")[:200]
                    )
                    tasks.append(task)
                
                # 如果AI分解失败或结果为空，使用规则方法
                if not tasks:
                    tasks = self._decompose_by_rules(topic)
                
                return tasks
            except:
                pass
        
        # 规则-based分解（备份方案）
        return self._decompose_by_rules(topic)
    
    def _decompose_by_rules(self, topic: str) -> List[SimpleDebateTask]:
        """基于规则的分解"""
        tasks = []
        
        # 根据主题类型进行分解
        if "分析" in topic or "研究" in topic:
            subtopics = [
                ("背景分析", f"分析{topic}的背景和缘由"),
                ("现状评估", f"评估{topic}的当前状况"),
                ("深度探讨", f"深入探讨{topic}的核心问题"),
                ("结论总结", f"总结关于{topic}的分析结论")
            ]
        elif "比较" in topic or "对比" in topic:
            subtopics = [
                ("标准制定", f"为{topic}制定比较标准"),
                ("信息收集", f"收集{topic}相关的比较信息"),
                ("对比分析", f"对{topic}进行详细对比分析"),
                ("结论总结", f"总结{topic}的比较结果")
            ]
        elif "设计" in topic or "构建" in topic:
            subtopics = [
                ("需求分析", f"分析{topic}的具体需求"),
                ("方案设计", f"设计{topic}的实施方案"),
                ("实现路径", f"规划{topic}的实现路径"),
                ("验证评估", f"评估{topic}方案的可行性")
            ]
        else:
            # 通用分解
            subtopics = [
                ("理解议题", f"深入理解{topic}的具体要求"),
                ("信息准备", f"准备讨论{topic}所需的信息"),
                ("观点论证", f"展开关于{topic}的多角度论证"),
                ("结论总结", f"总结关于{topic}的讨论结果")
            ]
        
        for title, description in subtopics:
            task = SimpleDebateTask(
                id=f"task_{uuid.uuid4().hex[:8]}",
                title=title,
                description=description
            )
            tasks.append(task)
        
        return tasks


class DebateTaskManager:
    """辩论任务管理器 - 管理任务分解和状态更新"""
    
    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        self.simple_debate_module = SimpleDebateModule(model_provider)
    
    async def process_complex_debate_request(self, topic: str) -> AsyncGenerator[str, None]:
        """处理复杂辩论请求 - 生成任务清单并逐步执行"""
        yield f"[bold magenta]🧩 检测到复杂辩论主题，启动自动分解...[/bold magenta]\\n主题: '{topic[:50]}{'...' if len(topic) > 50 else ''}'"
        
        # 分解任务
        tasks = await self.simple_debate_module.decompose_debate_topic(topic)
        
        if not tasks:
            yield f"[yellow]⚠️  任务分解失败，使用常规辩论流程[/yellow]"
            return
        
        # 显示任务清单
        task_list_display = self._generate_task_list_display(tasks)
        yield f"[bold cyan]📋 生成辩论任务清单，共 {len(tasks)} 个议题:[/bold cyan]\\n\\n{task_list_display}"
        
        # 逐步执行任务
        yield "[bold blue]🔄 开始按议程逐步讨论...[/bold blue]"
        
        debate_results = []
        for i, task in enumerate(tasks):
            yield f"\\n[bold yellow] ISSUE {i+1}/{len(tasks)}: {task.title} [/bold yellow]"
            
            try:
                # 更新任务状态为进行中
                await self._update_task_status(tasks, i, TaskStatus.IN_PROGRESS)
                updated_display = self._generate_task_list_display(tasks)
                yield f"[dim]{updated_display}[/dim]"
                
                # 执行单个辩论议题
                result = await self._execute_debate_topic(task, topic)
                
                # 更新任务状态为完成
                await self._update_task_status(tasks, i, TaskStatus.COMPLETED, result=result)
                debate_results.append(result)
                
                yield f"[green]✅ 完成议题: {task.title}[/green]"
                
                # 显示更新后的任务状态
                updated_display = self._generate_task_list_display(tasks)
                yield f"[dim]{updated_display}[/dim]"
                
            except Exception as e:
                await self._update_task_status(tasks, i, TaskStatus.FAILED, error=str(e))
                yield f"[red]❌ 议题执行失败: {task.title} - {e}[/red]"
        
        # 生成最终总结
        final_summary = await self._synthesize_debate_summary(topic, debate_results)
        yield f"\\n[bold green]🎯 辩论总结:[/bold green]\\n{final_summary}"
    
    def _generate_task_list_display(self, tasks: List[SimpleDebateTask]) -> str:
        """生成任务清单显示"""
        if not tasks:
            return "当前没有任务清单"
        
        display = ""
        status_emojis = {
            TaskStatus.PENDING: "⏳",
            TaskStatus.IN_PROGRESS: "🔄",
            TaskStatus.COMPLETED: "✅", 
            TaskStatus.FAILED: "❌"
        }
        
        for i, task in enumerate(tasks, 1):
            emoji = status_emojis.get(task.status, "❓")
            status_text = task.status.value.replace("in_progress", "执行中").replace("pending", "待执行").replace("completed", "已完成").replace("failed", "失败")
            
            display += f"{i}. {emoji} **{task.title}** ({status_text})\\n"
            display += f"   - {task.description}\\n\\n"
        
        # 添加进度统计
        total = len(tasks)
        completed = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
        progress = (completed / total * 100) if total > 0 else 0
        display += f"📈 **进度**: {completed}/{total} ({progress:.1f}% 完成)"
        
        return display
    
    async def _update_task_status(self, tasks: List[SimpleDebateTask], index: int, 
                                status: TaskStatus, result: Optional[str] = None, 
                                error: Optional[str] = None):
        """更新任务状态"""
        if 0 <= index < len(tasks):
            tasks[index].status = status
            if result:
                tasks[index].result = result
            if error:
                tasks[index].error = error
    
    async def _execute_debate_topic(self, task: SimpleDebateTask, original_topic: str) -> str:
        """执行单个辩论议题"""
        if self.model_provider:
            prompt = f"""请就以下辩论议题进行深入讨论：

原始议题: {original_topic}

当前子议题: {task.title}
议题描述: {task.description}

请提供关于此子议题的深入分析和观点。"""
            
            try:
                response = await self.model_provider.generate(prompt)
                return str(response) if isinstance(response, dict) else response
            except Exception as e:
                return f"议题执行失败: {e}"
        else:
            # 模拟执行
            return f"模拟执行结果: {task.title} - 已完成讨论"
    
    async def _synthesize_debate_summary(self, original_topic: str, 
                                       debate_results: List[str]) -> str:
        """合成辩论总结"""
        if self.model_provider and debate_results:
            summary_prompt = f"""请根据以下辩论议题讨论结果，生成对原始议题的综合分析。

原始议题: {original_topic}

各议题讨论结果:
{chr(10).join([f"{i+1}. {result[:300]}..." for i, result in enumerate(debate_results)])}

请提供一个完整、连贯的综合分析。"""
            
            try:
                response = await self.model_provider.generate(summary_prompt)
                return str(response) if isinstance(response, dict) else response
            except:
                pass
        
        # 默认合成
        return f"完成对'{original_topic}'的多议题讨论。共讨论了 {len(debate_results)} 个子议题。"


# 简化版集成器
class SimplifiedDebateIntegrator:
    """简化版辩论集成器 - 用于集成到现有系统"""
    
    def __init__(self, model_provider=None):
        self.task_manager = DebateTaskManager(model_provider)
    
    async def should_process_as_debate_with_task_decomposition(self, user_input: str) -> bool:
        """判断是否需要作为带任务分解的辩论处理"""
        # 检查是否是辩论相关请求且需要分解
        if any(keyword in user_input for keyword in ["辩论", "讨论", "探讨", "分析"]):
            return await self.task_manager.simple_debate_module.should_debate_need_task_decomposition(user_input)
        return False
    
    async def process_debate_with_task_decomposition(self, user_input: str) -> AsyncGenerator[str, None]:
        """处理需要任务分解的辩论请求"""
        async for event in self.task_manager.process_complex_debate_request(user_input):
            yield event


# 测试功能
async def test_simplified_debate_system():
    """测试简化版辩论系统"""
    print("="*80)
    print("🎯 简化版模块化辩论系统测试")
    print("="*80)
    
    print("\\n📝 系统特性:")
    characteristics = [
        "✅ 模块化设计 - 降低系统复杂度",
        "✅ 单独组件 - 易于测试和维护", 
        "✅ 自动检测 - 智能识别复杂辩论主题",
        "✅ 任务分解 - 自动生成待办议程",
        "✅ 状态更新 - 实时跟踪执行进度",
        "✅ 与现有系统兼容 - 无缝集成"
    ]
    
    for char in characteristics:
        print(f"  {char}")
    
    # 创建模拟模型提供者
    class MockModelProvider:
        async def generate(self, prompt: str):
            if "分解为" in prompt and "子议题" in prompt:
                return '''{
    "subtopics": [
        {"title": "背景分析", "description": "分析主题的背景和历史发展"},
        {"title": "现状评估", "description": "评估主题的当前状况和挑战"},
        {"title": "未来展望", "description": "展望主题的未来发展趋势"},
        {"title": "结论总结", "description": "总结分析并得出结论"}
    ]
}'''
            elif "就以下辩论议题" in prompt:
                return f"针对议题的详细分析和观点: {prompt.split('当前子议题:')[-1].split()[0] if '当前子议题:' in prompt else '模拟结果'}"
            elif "根据以下辩论议题讨论结果" in prompt:
                return "这是对原始话题的综合分析结果。经过多方面的详细讨论，得出了以下结论和建议。"
            else:
                return f"模拟响应: {prompt[:100]}..."
    
    mock_provider = MockModelProvider()
    integrator = SimplifiedDebateIntegrator(mock_provider)
    
    print("\\n🧪 测试复杂度检测和任务分解:")
    
    test_cases = [
        "深入分析人工智能伦理的多个方面",
        "探讨深度学习在医学影像中的应用前景", 
        "设计一个人工智能系统架构方案",
        "比较不同大模型的性能差异",
        "简单问题",
        "你好"
    ]
    
    for test_case in test_cases:
        should_decompose = await integrator.should_process_as_debate_with_task_decomposition(test_case)
        status = "✅" if should_decompose else "❌"
        print(f"   {status} '{test_case}' -> 需要分解: {should_decompose}")
    
    print("\\n📋 测试复杂辩论处理:")
    complex_topic = "分析人工智能在医疗领域的应用前景、挑战和解决方案"
    
    print(f"\\n开始处理: '{complex_topic}'")
    
    counter = 0
    async for event in integrator.process_debate_with_task_decomposition(complex_topic):
        counter += 1
        if counter <= 6:  # 只显示前几个事件
            print(f"   事件 {counter}: {event[:80]}...")
    
    print(f"  \\n✅ 处理完成，产生 {counter} 个事件流")
    
    print("\\n🏆 系统集成优势:")
    advantages = [
        "1. 降低系统复杂度 - 独立模块而非高度耦合",
        "2. 减少测试工作量 - 可独立测试各模块", 
        "3. 提高可维护性 - 清晰的职责分离",
        "4. 保持功能完整性 - 所有功能都保留",
        "5. 无缝集成 - 不影响现有系统",
        "6. 灵活扩展 - 易于添加新功能"
    ]
    
    for advantage in advantages:
        print(f"   {advantage}")
    
    print("\\n🎯 简化版模块化辩论系统实现完成!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_simplified_debate_system())
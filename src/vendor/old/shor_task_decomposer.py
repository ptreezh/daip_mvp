"""基于Shor算法的任务分解引擎
利用量子算法的分解思想，将复杂任务分解为可并行处理的子任务
"""

import hashlib
import math
import random
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

import numpy as np

from src.constants import *


class TaskComplexity(Enum):
    """任务复杂度等级"""

    TRIVIAL = 1  # 平凡任务
    SIMPLE = 2  # 简单任务
    MODERATE = 4  # 中等任务
    COMPLEX = 8  # 复杂任务
    EXPONENTIAL = 16  # 指数级复杂任务


@dataclass
class TaskNode:
    """任务节点"""

    id: str
    name: str
    description: str
    complexity: TaskComplexity
    dependencies: list[str]
    estimated_time: float  # 预估时间（小时）
    required_skills: list[str]
    priority: int  # 优先级 1-10
    decomposable: bool = True
    quantum_state: Optional[dict[str, float]] = None  # 量子态表示

    def __post_init__(self):
        if self.quantum_state is None:
            self.quantum_state = self._initialize_quantum_state()

    def _initialize_quantum_state(self) -> dict[str, float]:
        """初始化任务的量子态表示"""
        # 基于任务属性生成量子态
        complexity_amplitude = math.sqrt(self.complexity.value / 16)
        priority_amplitude = math.sqrt(self.priority / 10)
        time_amplitude = math.sqrt(min(self.estimated_time / 100, 1.0))

        return {
            "complexity": complexity_amplitude,
            "priority": priority_amplitude,
            "time": time_amplitude,
            "phase": random.uniform(0, 2 * math.pi),
        }


@dataclass
class DecompositionResult:
    """分解结果"""

    original_task: TaskNode
    subtasks: list[TaskNode]
    decomposition_tree: dict[str, Any]
    parallel_groups: list[list[str]]  # 可并行执行的任务组
    critical_path: list[str]  # 关键路径
    total_estimated_time: float
    decomposition_efficiency: float  # 分解效率
    quantum_entanglement_map: dict[str, list[str]]  # 量子纠缠映射


class ShorTaskDecomposer:
    """基于Shor算法的任务分解引擎"""

    def __init__(self, max_decomposition_depth: int = 5):
        self.max_decomposition_depth = max_decomposition_depth
        self.decomposition_history: list[DecompositionResult] = []
        self.quantum_register_size = 16  # 量子寄存器大小
        self.period_finding_cache: dict[str, int] = {}

    def decompose_task(self, task: TaskNode) -> DecompositionResult:
        """使用Shor算法思想分解任务

        Shor算法的核心思想：
        1. 周期查找 - 找到任务的重复模式
        2. 量子傅里叶变换 - 分析任务频域特征
        3. 因式分解 - 将复杂任务分解为素任务
        """
        print(f"🔍 开始分解任务: {task.name}")

        # 第一步：量子态初始化
        quantum_state = self._prepare_quantum_state(task)

        # 第二步：周期查找 - 寻找任务的重复模式
        period = self._quantum_period_finding(task)

        # 第三步：量子傅里叶变换 - 分析任务特征
        frequency_domain = self._quantum_fourier_transform(task, quantum_state)

        # 第四步：因式分解 - 分解为子任务
        subtasks = self._factorize_task(task, period, frequency_domain)

        # 第五步：构建分解树和依赖关系
        decomposition_tree = self._build_decomposition_tree(task, subtasks)

        # 第六步：分析并行性和关键路径
        parallel_groups = self._analyze_parallelism(subtasks)
        critical_path = self._find_critical_path(subtasks)

        # 第七步：计算量子纠缠映射
        entanglement_map = self._calculate_quantum_entanglement(subtasks)

        # 计算总时间和效率
        total_time = self._calculate_total_time(subtasks, parallel_groups)
        efficiency = self._calculate_decomposition_efficiency(
            task,
            subtasks,
            total_time,
        )

        result = DecompositionResult(
            original_task=task,
            subtasks=subtasks,
            decomposition_tree=decomposition_tree,
            parallel_groups=parallel_groups,
            critical_path=critical_path,
            total_estimated_time=total_time,
            decomposition_efficiency=efficiency,
            quantum_entanglement_map=entanglement_map,
        )

        self.decomposition_history.append(result)
        print(f"✅ 任务分解完成，生成 {len(subtasks)} 个子任务")

        return result

    def _prepare_quantum_state(self, task: TaskNode) -> np.ndarray:
        """准备量子态"""
        # 创建量子寄存器
        state_vector = np.zeros(2**self.quantum_register_size, dtype=complex)

        # 基于任务属性初始化量子态
        task_hash = int(hashlib.md5(task.name.encode()).hexdigest()[:8], 16)
        initial_state = task_hash % (2**self.quantum_register_size)

        # 叠加态初始化
        for i in range(min(task.complexity.value, 8)):
            state_index = (initial_state + i) % (2**self.quantum_register_size)
            amplitude = 1.0 / math.sqrt(task.complexity.value)
            phase = task.quantum_state["phase"] + i * math.pi / 4
            state_vector[state_index] = amplitude * np.exp(1j * phase)

        # 归一化
        norm = np.linalg.norm(state_vector)
        if norm > 0:
            state_vector /= norm

        return state_vector

    def _quantum_period_finding(self, task: TaskNode) -> int:
        """量子周期查找 - 寻找任务的重复模式"""
        task_signature = (
            f"{task.name}_{task.complexity.value}_{len(task.required_skills)}"
        )

        if task_signature in self.period_finding_cache:
            return self.period_finding_cache[task_signature]

        # 模拟量子周期查找
        # 基于任务特征计算周期
        base_period = task.complexity.value
        skill_factor = len(task.required_skills) if task.required_skills else 1
        priority_factor = task.priority

        # 使用类似Shor算法的周期查找逻辑
        period = math.gcd(base_period * skill_factor, priority_factor * 2)
        period = max(2, min(period, 8))  # 限制周期范围

        self.period_finding_cache[task_signature] = period
        return period

    def _quantum_fourier_transform(
        self,
        task: TaskNode,
        quantum_state: np.ndarray,
    ) -> dict[str, float]:
        """量子傅里叶变换 - 分析任务频域特征"""
        # 简化的QFT实现
        n_qubits = int(math.log2(len(quantum_state)))

        # 计算频域特征
        fft_result = np.fft.fft(quantum_state)

        # 提取关键频域特征
        frequency_features = {
            "dominant_frequency": np.argmax(np.abs(fft_result)),
            "frequency_spread": np.std(np.abs(fft_result)),
            "phase_coherence": np.mean(np.angle(fft_result)),
            "amplitude_variance": np.var(np.abs(fft_result)),
        }

        return frequency_features

    def _factorize_task(
        self,
        task: TaskNode,
        period: int,
        frequency_domain: dict[str, float],
    ) -> list[TaskNode]:
        """因式分解 - 将任务分解为子任务"""
        subtasks = []

        # 基于周期和频域特征确定分解策略
        num_subtasks = min(period * 2, task.complexity.value)

        # 分解策略
        if task.complexity == TaskComplexity.EXPONENTIAL:
            # 指数级任务：递归分解
            subtasks.extend(self._exponential_decomposition(task, num_subtasks))
        elif task.complexity == TaskComplexity.COMPLEX:
            # 复杂任务：分层分解
            subtasks.extend(self._hierarchical_decomposition(task, num_subtasks))
        else:
            # 简单任务：线性分解
            subtasks.extend(self._linear_decomposition(task, num_subtasks))

        return subtasks

    def _exponential_decomposition(
        self,
        task: TaskNode,
        num_subtasks: int,
    ) -> list[TaskNode]:
        """指数级任务的递归分解"""
        subtasks = []

        # 分解为对数级别的子任务
        log_factor = int(math.log2(num_subtasks)) + 1

        for i in range(log_factor):
            subtask = TaskNode(
                id=f"{task.id}_exp_{i}",
                name=f"{task.name} - 指数分解 {i+1}",
                description=f"指数级任务的第{i+1}层分解",
                complexity=TaskComplexity(max(1, task.complexity.value // (2**i))),
                dependencies=[f"{task.id}_exp_{i-1}"] if i > 0 else [],
                estimated_time=task.estimated_time / (2**i),
                required_skills=task.required_skills[
                    : max(1, len(task.required_skills) // (i + 1))
                ],
                priority=task.priority - i,
            )
            subtasks.append(subtask)

        return subtasks

    def _hierarchical_decomposition(
        self,
        task: TaskNode,
        num_subtasks: int,
    ) -> list[TaskNode]:
        """复杂任务的分层分解"""
        subtasks = []

        # 分解为层次结构
        layers = ["分析", "设计", "实现", "测试", "优化"]

        for i, layer in enumerate(layers[:num_subtasks]):
            subtask = TaskNode(
                id=f"{task.id}_hier_{i}",
                name=f"{task.name} - {layer}阶段",
                description=f"{layer}阶段的具体任务",
                complexity=TaskComplexity(max(1, task.complexity.value // 2)),
                dependencies=[f"{task.id}_hier_{i-1}"] if i > 0 else [],
                estimated_time=task.estimated_time / len(layers),
                required_skills=self._select_skills_for_layer(
                    task.required_skills,
                    layer,
                ),
                priority=task.priority,
            )
            subtasks.append(subtask)

        return subtasks

    def _linear_decomposition(
        self,
        task: TaskNode,
        num_subtasks: int,
    ) -> list[TaskNode]:
        """简单任务的线性分解"""
        subtasks = []

        for i in range(num_subtasks):
            subtask = TaskNode(
                id=f"{task.id}_linear_{i}",
                name=f"{task.name} - 子任务 {i+1}",
                description=f"线性分解的第{i+1}个子任务",
                complexity=TaskComplexity(
                    max(1, task.complexity.value // num_subtasks),
                ),
                dependencies=[f"{task.id}_linear_{i-1}"] if i > 0 else [],
                estimated_time=task.estimated_time / num_subtasks,
                required_skills=task.required_skills,
                priority=task.priority,
            )
            subtasks.append(subtask)

        return subtasks

    def _select_skills_for_layer(self, skills: list[str], layer: str) -> list[str]:
        """为特定层选择相关技能"""
        skill_mapping = {
            "分析": ["分析", "研究", "调研", "评估"],
            "设计": ["设计", "架构", "建模", "规划"],
            "实现": ["编程", "开发", "实现", "构建"],
            "测试": ["测试", "验证", "质量", "调试"],
            "优化": ["优化", "性能", "改进", "调优"],
        }

        layer_keywords = skill_mapping.get(layer, [])
        selected_skills = []

        for skill in skills:
            if any(keyword in skill.lower() for keyword in layer_keywords):
                selected_skills.append(skill)

        return selected_skills if selected_skills else skills[:1]

    def _build_decomposition_tree(
        self,
        root_task: TaskNode,
        subtasks: list[TaskNode],
    ) -> dict[str, Any]:
        """构建分解树"""
        tree = {
            "root": {
                "id": root_task.id,
                "name": root_task.name,
                "complexity": root_task.complexity.value,
                "children": [],
            },
        }

        for subtask in subtasks:
            child_node = {
                "id": subtask.id,
                "name": subtask.name,
                "complexity": subtask.complexity.value,
                "dependencies": subtask.dependencies,
                "estimated_time": subtask.estimated_time,
            }
            tree["root"]["children"].append(child_node)

        return tree

    def _analyze_parallelism(self, subtasks: list[TaskNode]) -> list[list[str]]:
        """分析任务并行性"""
        parallel_groups = []
        processed = set()

        # 按依赖关系分组
        for subtask in subtasks:
            if subtask.id in processed:
                continue

            # 找到没有依赖或依赖已完成的任务
            if not subtask.dependencies:
                group = [subtask.id]
                processed.add(subtask.id)

                # 找到其他可以并行的任务
                for other_task in subtasks:
                    if (
                        other_task.id not in processed
                        and not other_task.dependencies
                        and len(group) < 4
                    ):  # 限制并行组大小
                        group.append(other_task.id)
                        processed.add(other_task.id)

                if group:
                    parallel_groups.append(group)

        return parallel_groups

    def _find_critical_path(self, subtasks: list[TaskNode]) -> list[str]:
        """寻找关键路径"""
        # 简化的关键路径算法
        task_dict = {task.id: task for task in subtasks}

        # 计算每个任务的最早开始时间
        earliest_start = {}

        def calculate_earliest_start(task_id: str) -> float:
            if task_id in earliest_start:
                return earliest_start[task_id]

            task = task_dict.get(task_id)
            if not task or not task.dependencies:
                earliest_start[task_id] = 0
                return 0

            max_dependency_end = 0
            for dep_id in task.dependencies:
                if dep_id in task_dict:
                    dep_end = (
                        calculate_earliest_start(dep_id)
                        + task_dict[dep_id].estimated_time
                    )
                    max_dependency_end = max(max_dependency_end, dep_end)

            earliest_start[task_id] = max_dependency_end
            return max_dependency_end

        # 计算所有任务的最早开始时间
        for task in subtasks:
            calculate_earliest_start(task.id)

        # 找到关键路径（最长路径）
        critical_path = []
        max_end_time = 0
        last_task = None

        for task in subtasks:
            end_time = earliest_start[task.id] + task.estimated_time
            if end_time > max_end_time:
                max_end_time = end_time
                last_task = task

        # 回溯构建关键路径
        if last_task:
            current = last_task
            critical_path.insert(0, current.id)

            while current.dependencies:
                # 找到关键依赖
                critical_dep = None
                max_dep_end = 0

                for dep_id in current.dependencies:
                    if dep_id in task_dict:
                        dep_task = task_dict[dep_id]
                        dep_end = earliest_start[dep_id] + dep_task.estimated_time
                        if dep_end > max_dep_end:
                            max_dep_end = dep_end
                            critical_dep = dep_task

                if critical_dep:
                    critical_path.insert(0, critical_dep.id)
                    current = critical_dep
                else:
                    break

        return critical_path

    def _calculate_quantum_entanglement(
        self,
        subtasks: list[TaskNode],
    ) -> dict[str, list[str]]:
        """计算量子纠缠映射 - 任务间的强相关性"""
        entanglement_map = {}

        for i, task1 in enumerate(subtasks):
            entangled_tasks = []

            for j, task2 in enumerate(subtasks):
                if i != j:
                    # 计算任务间的纠缠度
                    entanglement_score = self._calculate_entanglement_score(
                        task1,
                        task2,
                    )

                    if entanglement_score > 0.5:  # 纠缠阈值
                        entangled_tasks.append(task2.id)

            if entangled_tasks:
                entanglement_map[task1.id] = entangled_tasks

        return entanglement_map

    def _calculate_entanglement_score(self, task1: TaskNode, task2: TaskNode) -> float:
        """计算两个任务间的纠缠分数"""
        # 技能重叠度
        skill_overlap = len(set(task1.required_skills) & set(task2.required_skills))
        skill_total = len(set(task1.required_skills) | set(task2.required_skills))
        skill_similarity = skill_overlap / skill_total if skill_total > 0 else 0

        # 复杂度相似性
        complexity_diff = abs(task1.complexity.value - task2.complexity.value)
        complexity_similarity = 1.0 / (1.0 + complexity_diff)

        # 时间相似性
        time_ratio = min(task1.estimated_time, task2.estimated_time) / max(
            task1.estimated_time,
            task2.estimated_time,
        )

        # 综合纠缠分数
        entanglement_score = (
            skill_similarity * 0.4 + complexity_similarity * 0.3 + time_ratio * 0.3
        )

        return entanglement_score

    def _calculate_total_time(
        self,
        subtasks: list[TaskNode],
        parallel_groups: list[list[str]],
    ) -> float:
        """计算总执行时间"""
        task_dict = {task.id: task for task in subtasks}
        total_time = 0

        # 计算并行组的最大时间
        for group in parallel_groups:
            group_max_time = 0
            for task_id in group:
                if task_id in task_dict:
                    group_max_time = max(
                        group_max_time,
                        task_dict[task_id].estimated_time,
                    )
            total_time += group_max_time

        # 加上串行任务的时间
        parallel_task_ids = set()
        for group in parallel_groups:
            parallel_task_ids.update(group)

        for task in subtasks:
            if task.id not in parallel_task_ids:
                total_time += task.estimated_time

        return total_time

    def _calculate_decomposition_efficiency(
        self,
        original_task: TaskNode,
        subtasks: list[TaskNode],
        total_time: float,
    ) -> float:
        """计算分解效率"""
        # 原始任务时间 vs 分解后总时间
        time_efficiency = (
            original_task.estimated_time / total_time if total_time > 0 else 0
        )

        # 复杂度降低效率
        original_complexity = original_task.complexity.value
        avg_subtask_complexity = sum(task.complexity.value for task in subtasks) / len(
            subtasks,
        )
        complexity_efficiency = (
            avg_subtask_complexity / original_complexity
            if original_complexity > 0
            else 0
        )

        # 综合效率
        efficiency = time_efficiency * 0.6 + complexity_efficiency * 0.4
        return min(efficiency, 1.0)

    def get_decomposition_statistics(self) -> dict[str, Any]:
        """获取分解统计信息"""
        if not self.decomposition_history:
            return {"message": "No decomposition history available"}

        total_decompositions = len(self.decomposition_history)
        avg_efficiency = (
            sum(
                result.decomposition_efficiency for result in self.decomposition_history
            )
            / total_decompositions
        )
        avg_subtasks = (
            sum(len(result.subtasks) for result in self.decomposition_history)
            / total_decompositions
        )

        return {
            "total_decompositions": total_decompositions,
            "average_efficiency": avg_efficiency,
            "average_subtasks_per_decomposition": avg_subtasks,
            "total_tasks_generated": sum(
                len(result.subtasks) for result in self.decomposition_history
            ),
            "cache_hit_rate": len(self.period_finding_cache)
            / max(total_decompositions, 1),
        }

# ruff: noqa: E501
"""Delegation pipeline for local/cloud hybrid execution.

Stage 5 最小闭环 v3（2026-08-10，用户核心设计原则）：
1. **全局上下文（系统提示/会话历史/长时记忆）永不上传云端**
2. **所有任务先分解为 >=3 个子任务，用本地模型分解**
3. **子任务上下文完备自包含**：每个子任务自带完成任务所需的信息，
   不依赖父任务上下文，也不携带全局上下文
4. **子任务在子任务层面分发**（可分发不同云端模型）
5. 云端不可用 / 分解失败 / 高风险 → 回退本地

实现要点：
- 任务分解调用**本地模型**（Ollama，litellm 本地路径），输入仅用户任务文本
- 分解 prompt 强制要求子任务自包含、禁止携带全局上下文
- 每个子任务独立 sanitize + 风险分类
- 云端只收到子任务文本（已脱敏、自包含、无全局上下文）
- 多 provider 池按轮询分发子任务
"""

import os
import re
from dataclasses import dataclass, field
from typing import Optional

import litellm

from daip_live.hybrid.cloud_pool import (
    CloudPool,
    DelegationResult,
    ProviderStatus,
)
from daip_live.hybrid.sanitization import sanitize_prompt
from daip_live.hybrid.security_gate import RiskLevel, SecurityGate

# 本地分解模型（可被环境变量覆盖）
LOCAL_DECOMPOSER_MODEL = os.environ.get(
    "DAIP_HYBRID_DECOMPOSER_MODEL", "ollama/llama3:latest"
)

_DECOMPOSE_PROMPT = """你是一个任务分解助手。请把下面的用户任务分解为至少 {min_n} 个清晰、独立、可执行的子任务。

要求：
1. 每个子任务必须【上下文完备自包含】：单独交给任何 AI 都能理解并完成，不依赖"上面的任务/父任务/前文"等外部引用。
2. 子任务之间不得引用彼此（禁止"如上面所述""第一部分"等措辞）。
3. 禁止引入或携带任何不在用户任务中的全局上下文、背景信息、会话历史、用户个人数据。
4. 每个子任务单独一行，以序号开头（1. 2. 3. ...），只输出子任务列表，不要其他解释。

用户任务：
{task}
"""


@dataclass
class SubtaskResult:
    """单个子任务的执行结果。"""

    task: str
    provider_name: str
    content: str
    success: bool
    cloud_delegated: bool
    redacted_count: int = 0
    error_message: Optional[str] = None


@dataclass
class PipelineResult:
    """Delegation pipeline execution result."""

    content: str
    provider_name: str
    success: bool
    risk_level: RiskLevel
    cloud_delegated: bool
    redacted_count: int = 0
    error_message: Optional[str] = None
    needs_human_approval: bool = False
    subtasks: list[SubtaskResult] = field(default_factory=list)

    @property
    def subtask_count(self) -> int:
        """返回子任务数量。"""
        return len(self.subtasks)


def _parse_decomposed_subtasks(text: str, min_subtasks: int = 3) -> list[str]:
    """解析本地模型输出的子任务列表。

    支持 "1. xxx" / "- xxx" / "* xxx" / 纯文本行格式。

    Args:
        text: 本地模型输出
        min_subtasks: 最少子任务数

    Returns:
        list[str]: 解析出的子任务（去重、去空）
    """
    subtasks = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        # 去掉序号前缀 "1. " "- " "* " "1) " "1、"
        cleaned = re.sub(r"^(?:\d+[\.\)、]\s*|[-*]\s+)", "", line)
        cleaned = cleaned.strip()
        # 过滤说明性前缀行（如 "Here are the subtasks:" / "Note:"）
        if re.match(
            r"^(here are|subtask|以下|子任务|分解结果|好的|ok|好的，|当然|note:)",
            cleaned,
            re.IGNORECASE,
        ):
            continue
        if cleaned and cleaned not in subtasks:
            subtasks.append(cleaned)

    # 少于 min_subtasks 时退化：按规则切分补齐
    if len(subtasks) < min_subtasks:
        subtasks = _fallback_split(text, min_subtasks)
    return subtasks[: min_subtasks + 2]


def _fallback_split(text: str, min_subtasks: int = 3) -> list[str]:
    """退化切分：本地模型输出解析失败时，按句子/段落切分为 >=3 块。

    Args:
        text: 待切分文本
        min_subtasks: 最少子任务数

    Returns:
        list[str]: 子任务列表
    """
    segments = [s.strip() for s in re.split(r"[\n。！？!?]", text) if s.strip()]
    while len(segments) < min_subtasks:
        if not segments:
            segments = [text]
            break
        longest_idx = max(range(len(segments)), key=lambda i: len(segments[i]))
        longest = segments[longest_idx]
        mid = len(longest) // 2
        segments[longest_idx : longest_idx + 1] = [longest[:mid], longest[mid:]]
    return segments[: min_subtasks + 2]


class DelegationPipeline:
    """编排：本地模型分解 → 子任务风险分类/脱敏 → 云端分发（或本地回退）。

    feature flag（DAIP_HYBRID_ENABLED）控制是否启用云端委托；
    全局上下文（global_context 参数）仅用于本地风险判断，绝不下发云端，
    也绝不被纳入子任务（子任务只由用户任务分解而来，保持自包含）。
    """

    def __init__(
        self,
        cloud_pool: Optional[CloudPool] = None,
        enabled: bool = True,
        min_subtasks: int = 3,
        decomposer_model: str = LOCAL_DECOMPOSER_MODEL,
    ):
        self.cloud_pool = cloud_pool or CloudPool()
        self.enabled = enabled
        self.min_subtasks = min_subtasks
        self.decomposer_model = decomposer_model
        self.security_gate = SecurityGate

    async def execute(
        self,
        prompt: str,
        api_key: Optional[str] = None,
        global_context: Optional[str] = None,
    ) -> PipelineResult:
        """执行委托管线：本地模型分解 → 子任务分类/脱敏 → 云端分发或本地回退。

        Args:
            prompt: 用户任务（会被分解为 >=3 自包含子任务）
            api_key: 云端 API key（None 时视为无云端可用）
            global_context: 全局上下文（会话历史/长时记忆等）。
                仅用于本地风险判断，**不进入子任务，更不发送给云端**。

        Returns:
            PipelineResult: 汇总执行结果
        """
        # 1. 整体风险预检（用 prompt + 全局上下文做本地判断）
        full_input = prompt
        if global_context:
            full_input = f"{global_context}\n\n{prompt}"
        risk_level = self.security_gate.classify_risk(full_input)

        # 2. HIGH 风险：绝不委托（即使有云端），标记人工确认
        if risk_level == RiskLevel.HIGH:
            return PipelineResult(
                content="",
                provider_name="local",
                success=True,
                risk_level=risk_level,
                cloud_delegated=False,
                needs_human_approval=True,
            )

        # 3. 本地模型任务分解（>=3 自包含子任务；输入仅用户任务，不含全局上下文）
        try:
            subtask_texts = await self._decompose_with_local_model(prompt)
        except Exception:
            # 本地模型不可用：退化规则切分（保证流程可用）
            subtask_texts = _fallback_split(prompt, self.min_subtasks)

        # 4. 子任务级处理：每个子任务独立 sanitize + 分发
        subtask_results: list[SubtaskResult] = []
        providers = self._get_available_providers(api_key)
        provider_idx = 0

        for task_text in subtask_texts:
            # 每个子任务独立脱敏（防止个别子任务含敏感片段）
            sanitized = sanitize_prompt(task_text)

            # 子任务独立风险判断：MEDIUM/HIGH 子任务不委托云端
            sub_risk = self.security_gate.classify_risk(task_text)
            if sub_risk in (RiskLevel.MEDIUM, RiskLevel.HIGH):
                subtask_results.append(
                    SubtaskResult(
                        task=task_text,
                        provider_name="local",
                        content="",
                        success=True,
                        cloud_delegated=False,
                        redacted_count=sanitized.redacted_count,
                    )
                )
                continue

            # LOW 子任务：尝试云端分发（轮询 provider 池）
            if self.enabled and providers and not sanitized.warnings:
                provider = providers[provider_idx % len(providers)]
                provider_idx += 1
                try:
                    # 云端只收子任务文本（含脱敏后），全局上下文绝不外传
                    result = await self._call_cloud(
                        provider, sanitized.sanitized, api_key
                    )
                    subtask_results.append(
                        SubtaskResult(
                            task=task_text,
                            provider_name=provider.name,
                            content=result.content,
                            success=True,
                            cloud_delegated=True,
                            redacted_count=sanitized.redacted_count,
                        )
                    )
                    continue
                except Exception as e:
                    subtask_results.append(
                        SubtaskResult(
                            task=task_text,
                            provider_name="local",
                            content="",
                            success=True,
                            cloud_delegated=False,
                            redacted_count=sanitized.redacted_count,
                            error_message=str(e),
                        )
                    )
                    continue

            # 云端不可用/脱敏触发：回退本地
            subtask_results.append(
                SubtaskResult(
                    task=task_text,
                    provider_name="local",
                    content="",
                    success=True,
                    cloud_delegated=False,
                    redacted_count=sanitized.redacted_count,
                )
            )

        # 5. 汇总
        cloud_results = [r for r in subtask_results if r.cloud_delegated]
        any_delegated = bool(cloud_results)
        provider_name = (
            cloud_results[0].provider_name if cloud_results else "local"
        )
        content = "\n".join(r.content for r in subtask_results if r.content)

        return PipelineResult(
            content=content,
            provider_name=provider_name,
            success=True,
            risk_level=risk_level,
            cloud_delegated=any_delegated,
            redacted_count=sum(r.redacted_count for r in subtask_results),
            subtasks=subtask_results,
        )

    async def _decompose_with_local_model(self, task: str) -> list[str]:
        """调用本地模型（Ollama）把任务分解为 >=3 自包含子任务。

        Args:
            task: 用户任务文本（不含全局上下文）

        Returns:
            list[str]: 自包含子任务列表

        Raises:
            Exception: 本地模型不可用/调用失败（调用方退化切分）
        """
        prompt = _DECOMPOSE_PROMPT.format(min_n=self.min_subtasks, task=task)
        response = await litellm.acompletion(
            model=self.decomposer_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.3,
        )
        content = response.choices[0].message.content
        return _parse_decomposed_subtasks(content, self.min_subtasks)

    def _get_available_providers(self, api_key: Optional[str] = None) -> list:
        """获取所有可用云端 provider（需 API key 配置）。

        Args:
            api_key: 显式传入的 API key（优先）；否则检查 provider 的 env 配置。
        """
        available = []
        for provider in self.cloud_pool.providers.values():
            if provider.status == ProviderStatus.UNAVAILABLE:
                continue
            has_key = bool(api_key) or provider.has_api_key()
            if has_key and provider.is_available():
                available.append(provider)
        return available

    async def _call_cloud(
        self,
        provider,
        prompt: str,
        api_key: Optional[str],
    ) -> DelegationResult:
        """调用云端模型（litellm.acompletion）。

        只接收**子任务文本**（已脱敏、自包含）；全局上下文由调用方隔离，不传入本方法。

        Args:
            provider: CloudProvider 配置
            prompt: 脱敏后的子任务文本
            api_key: API key

        Returns:
            DelegationResult: 云端响应

        Raises:
            Exception: 云端调用失败（调用方回退本地）
        """
        api_key = api_key or os.environ.get(provider.api_key_env, "")
        messages = [{"role": "user", "content": prompt}]

        response = await litellm.acompletion(
            model=f"{provider.name}/{provider.model}",
            messages=messages,
            api_key=api_key or None,
            max_tokens=2000,
            temperature=0.7,
        )
        content = response.choices[0].message.content
        usage = getattr(response, "usage", None)
        tokens = usage.total_tokens if usage else 0

        return DelegationResult(
            content=content,
            provider_name=provider.name,
            tokens_used=tokens,
            success=True,
        )

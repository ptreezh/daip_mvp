"""Delegation pipeline for local/cloud hybrid execution.

Stage 5 最小闭环（2026-08-10，用户确认范围）：
- SecurityGate 分类风险（LOW/MEDIUM/HIGH）
- LOW：尝试委托云端（CloudPool 内 provider，litellm 调用）
- 云端不可用（无 API key / 池空 / 调用失败）→ 自动回退本地
- MEDIUM/HIGH：不委托云端，直接标记本地执行

后续扩展（H1-H6 完整蓝图）：规则外置到 config、人工确认流、
中文 PII 脱敏增强、业务接线到 ask/chat。
"""

import os
from dataclasses import dataclass
from typing import Optional

import litellm

from daip_live.hybrid.cloud_pool import (
    CloudPool,
    DelegationResult,
    ProviderStatus,
)
from daip_live.hybrid.sanitization import sanitize_prompt
from daip_live.hybrid.security_gate import RiskLevel, SecurityGate


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


class DelegationPipeline:
    """Orchestrates risk classification, sanitization, and cloud delegation.

    feature flag 控制是否启用云端委托（默认启用；无云端配置时静默回退本地）。
    """

    def __init__(self, cloud_pool: Optional[CloudPool] = None, enabled: bool = True):
        self.cloud_pool = cloud_pool or CloudPool()
        self.enabled = enabled
        self.security_gate = SecurityGate

    async def execute(
        self,
        prompt: str,
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> PipelineResult:
        """执行委托管线：分类 → 脱敏 → （云端或本地）。

        Args:
            prompt: 用户输入
            api_key: 云端 API key（None 时视为无云端可用）
            system_prompt: 可选系统提示词

        Returns:
            PipelineResult: 执行结果
        """
        # 1. 风险分类
        risk_level = self.security_gate.classify_risk(prompt)

        # 2. MEDIUM/HIGH：不委托云端（本地执行或人工确认标记）
        if risk_level in (RiskLevel.MEDIUM, RiskLevel.HIGH):
            return PipelineResult(
                content="",
                provider_name="local",
                success=True,
                risk_level=risk_level,
                cloud_delegated=False,
                needs_human_approval=risk_level == RiskLevel.HIGH,
            )

        # 3. LOW：脱敏后尝试云端委托
        sanitized = sanitize_prompt(prompt)
        provider = self._get_available_provider(api_key)

        if self.enabled and provider is not None:
            try:
                result = await self._call_cloud(
                    provider, sanitized.sanitized, api_key, system_prompt
                )
                return PipelineResult(
                    content=result.content,
                    provider_name=provider.name,
                    success=True,
                    risk_level=risk_level,
                    cloud_delegated=True,
                    redacted_count=sanitized.redacted_count,
                )
            except Exception as e:
                # 云端调用失败：回退本地
                return PipelineResult(
                    content="",
                    provider_name="local",
                    success=True,
                    risk_level=risk_level,
                    cloud_delegated=False,
                    redacted_count=sanitized.redacted_count,
                    error_message=f"Cloud delegation failed, fell back to local: {e}",
                )

        # 4. 无云端可用 → 回退本地
        return PipelineResult(
            content="",
            provider_name="local",
            success=True,
            risk_level=risk_level,
            cloud_delegated=False,
            redacted_count=sanitized.redacted_count,
        )

    def _get_available_provider(self, api_key: Optional[str] = None):
        """获取可用云端 provider（需 API key 配置）。

        Args:
            api_key: 显式传入的 API key（优先）；否则检查 provider 的 env 配置。
        """
        for provider in self.cloud_pool.providers.values():
            if provider.status == ProviderStatus.UNAVAILABLE:
                continue
            has_key = bool(api_key) or provider.has_api_key()
            if has_key and provider.is_available():
                return provider
        return None

    async def _call_cloud(
        self,
        provider,
        prompt: str,
        api_key: Optional[str],
        system_prompt: Optional[str],
    ) -> DelegationResult:
        """调用云端模型（litellm.acompletion）。

        Args:
            provider: CloudProvider 配置
            prompt: 脱敏后的 prompt
            api_key: API key
            system_prompt: 系统提示词

        Returns:
            DelegationResult: 云端响应

        Raises:
            Exception: 云端调用失败（调用方回退本地）
        """
        api_key = api_key or os.environ.get(provider.api_key_env, "")
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

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

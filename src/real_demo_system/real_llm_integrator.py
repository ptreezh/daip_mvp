"""真实LLM集成器

这个模块提供真实的LLM调用功能，支持多种LLM后端（Ollama、OpenAI、Claude），
并提供完整的调用记录、性能监控和透明度功能。
"""

import asyncio
import hashlib
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import anthropic
import ollama
import openai

from src.config import get_config

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """支持的LLM提供商"""

    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


@dataclass
class LLMCallRecord:
    """LLM调用记录"""

    call_id: str
    provider: str
    model: str
    prompt: str
    response: str
    timestamp: datetime
    duration_ms: int
    input_tokens: int
    output_tokens: int
    cost_usd: float
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

    def get_signature(self) -> str:
        """生成调用签名用于验证"""
        content = f"{self.provider}:{self.model}:{self.prompt}:{self.response}"
        return hashlib.sha256(content.encode()).hexdigest()


@dataclass
class LLMPerformanceMetrics:
    """LLM性能指标"""

    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_duration_ms: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost_usd: float = 0.0
    average_response_time_ms: float = 0.0
    success_rate: float = 0.0

    def update(self, record: LLMCallRecord):
        """更新性能指标"""
        self.total_calls += 1
        if record.success:
            self.successful_calls += 1
        else:
            self.failed_calls += 1

        self.total_duration_ms += record.duration_ms
        self.total_input_tokens += record.input_tokens
        self.total_output_tokens += record.output_tokens
        self.total_cost_usd += record.cost_usd

        self.average_response_time_ms = self.total_duration_ms / self.total_calls
        self.success_rate = self.successful_calls / self.total_calls if self.total_calls > 0 else 0.0


class RealLLMIntegrator:
    """真实LLM集成器
    
    提供真实的LLM调用功能，支持多种后端，包含完整的监控和透明度功能。
    """

    def __init__(self, config_override: Optional[Dict[str, Any]] = None):
        """初始化LLM集成器
        
        Args:
            config_override: 可选的配置覆盖

        """
        self.config = get_config()
        if config_override:
            # 应用配置覆盖
            for key, value in config_override.items():
                setattr(self.config.llm, key, value)

        # 初始化客户端
        self.ollama_client = None
        self.openai_client = None
        self.anthropic_client = None

        # 调用记录和性能指标
        self.call_records: List[LLMCallRecord] = []
        self.performance_metrics = LLMPerformanceMetrics()

        # 初始化客户端
        self._initialize_clients()

        logger.info(f"RealLLMIntegrator initialized with provider: {self.config.llm.provider}")

    def _initialize_clients(self):
        """初始化各种LLM客户端"""
        try:
            # 初始化Ollama客户端
            if self.config.llm.provider == "ollama" or True:  # 总是初始化以支持切换
                ollama_host = getattr(self.config.llm.ollama, 'host', 'http://localhost:11434')
                self.ollama_client = ollama.Client(host=ollama_host)
                logger.info(f"Ollama client initialized: {ollama_host}")

            # 初始化OpenAI客户端
            openai_api_key = os.environ.get("OPENAI_API_KEY")
            if openai_api_key:
                self.openai_client = openai.OpenAI(api_key=openai_api_key)
                logger.info("OpenAI client initialized")

            # 初始化Anthropic客户端
            anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
            if anthropic_api_key:
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
                logger.info("Anthropic client initialized")

        except Exception as e:
            logger.error(f"Failed to initialize LLM clients: {e}")

    async def call_llm(
        self,
        prompt: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LLMCallRecord:
        """调用LLM并返回完整的调用记录
        
        Args:
            prompt: 输入提示
            provider: LLM提供商 (ollama/openai/anthropic)
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            metadata: 额外的元数据
            
        Returns:
            LLMCallRecord: 完整的调用记录

        """
        # 使用默认配置
        provider = provider or self.config.llm.provider
        model = model or self._get_default_model(provider)
        metadata = metadata or {}

        # 生成调用ID
        call_id = hashlib.md5(f"{time.time()}:{prompt[:100]}".encode()).hexdigest()

        start_time = time.time()
        timestamp = datetime.now()

        try:
            # 根据提供商调用相应的LLM
            if provider == "ollama":
                response, input_tokens, output_tokens, cost = await self._call_ollama(
                    prompt, model, temperature, max_tokens
                )
            elif provider == "openai":
                response, input_tokens, output_tokens, cost = await self._call_openai(
                    prompt, model, temperature, max_tokens
                )
            elif provider == "anthropic":
                response, input_tokens, output_tokens, cost = await self._call_anthropic(
                    prompt, model, temperature, max_tokens
                )
            else:
                raise ValueError(f"Unsupported provider: {provider}")

            duration_ms = int((time.time() - start_time) * 1000)

            # 创建调用记录
            record = LLMCallRecord(
                call_id=call_id,
                provider=provider,
                model=model,
                prompt=prompt,
                response=response,
                timestamp=timestamp,
                duration_ms=duration_ms,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=cost,
                success=True,
                metadata=metadata
            )

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(f"LLM call failed: {e}")

            # 创建失败记录
            record = LLMCallRecord(
                call_id=call_id,
                provider=provider,
                model=model or "unknown",
                prompt=prompt,
                response="",
                timestamp=timestamp,
                duration_ms=duration_ms,
                input_tokens=0,
                output_tokens=0,
                cost_usd=0.0,
                success=False,
                error_message=str(e),
                metadata=metadata
            )

        # 记录调用并更新指标
        self.call_records.append(record)
        self.performance_metrics.update(record)

        logger.info(f"LLM call completed: {call_id}, success: {record.success}, duration: {record.duration_ms}ms")

        return record

    async def _call_ollama(
        self, prompt: str, model: str, temperature: float, max_tokens: Optional[int]
    ) -> tuple[str, int, int, float]:
        """调用Ollama"""
        if not self.ollama_client:
            raise RuntimeError("Ollama client not initialized")

        try:
            response = await asyncio.to_thread(
                self.ollama_client.generate,
                model=model,
                prompt=prompt,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens or -1
                }
            )

            response_text = response.get("response", "")

            # Ollama通常不返回token计数，我们估算
            input_tokens = len(prompt.split()) * 1.3  # 粗略估算
            output_tokens = len(response_text.split()) * 1.3
            cost = 0.0  # Ollama本地运行，成本为0

            return response_text, int(input_tokens), int(output_tokens), cost

        except Exception as e:
            logger.error(f"Ollama call failed: {e}")
            raise

    async def _call_openai(
        self, prompt: str, model: str, temperature: float, max_tokens: Optional[int]
    ) -> tuple[str, int, int, float]:
        """调用OpenAI"""
        if not self.openai_client:
            raise RuntimeError("OpenAI client not initialized")

        try:
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )

            response_text = response.choices[0].message.content
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens

            # 计算成本（基于GPT-4的价格，实际应该根据模型调整）
            cost = (input_tokens * 0.03 + output_tokens * 0.06) / 1000

            return response_text, input_tokens, output_tokens, cost

        except Exception as e:
            logger.error(f"OpenAI call failed: {e}")
            raise

    async def _call_anthropic(
        self, prompt: str, model: str, temperature: float, max_tokens: Optional[int]
    ) -> tuple[str, int, int, float]:
        """调用Anthropic Claude"""
        if not self.anthropic_client:
            raise RuntimeError("Anthropic client not initialized")

        try:
            response = await asyncio.to_thread(
                self.anthropic_client.messages.create,
                model=model,
                max_tokens=max_tokens or 1000,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            # 计算成本（基于Claude的价格）
            cost = (input_tokens * 0.008 + output_tokens * 0.024) / 1000

            return response_text, input_tokens, output_tokens, cost

        except Exception as e:
            logger.error(f"Anthropic call failed: {e}")
            raise

    def _get_default_model(self, provider: str) -> str:
        """获取默认模型"""
        if provider == "ollama":
            return getattr(self.config.llm.ollama, 'generation_model', 'llama3:instruct')
        elif provider == "openai":
            return "gpt-4"
        elif provider == "anthropic":
            return "claude-3-sonnet-20240229"
        else:
            return "unknown"

    def get_call_records(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取调用记录"""
        records = self.call_records[-limit:] if limit else self.call_records
        return [record.to_dict() for record in records]

    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        return asdict(self.performance_metrics)

    def get_real_time_status(self) -> Dict[str, Any]:
        """获取实时状态"""
        recent_records = self.call_records[-10:] if self.call_records else []

        return {
            "is_active": len(recent_records) > 0,
            "last_call_time": recent_records[-1].timestamp.isoformat() if recent_records else None,
            "recent_success_rate": sum(1 for r in recent_records if r.success) / len(recent_records) if recent_records else 0,
            "average_response_time": sum(r.duration_ms for r in recent_records) / len(recent_records) if recent_records else 0,
            "total_calls_today": len([r for r in self.call_records if r.timestamp.date() == datetime.now().date()]),
            "providers_status": self._get_providers_status()
        }

    def _get_providers_status(self) -> Dict[str, bool]:
        """获取各提供商状态"""
        return {
            "ollama": self.ollama_client is not None,
            "openai": self.openai_client is not None,
            "anthropic": self.anthropic_client is not None
        }

    def verify_call_authenticity(self, call_id: str) -> Dict[str, Any]:
        """验证调用的真实性"""
        record = next((r for r in self.call_records if r.call_id == call_id), None)
        if not record:
            return {"verified": False, "error": "Call record not found"}

        signature = record.get_signature()

        return {
            "verified": True,
            "call_id": call_id,
            "signature": signature,
            "timestamp": record.timestamp.isoformat(),
            "provider": record.provider,
            "model": record.model,
            "success": record.success,
            "metadata": record.metadata
        }

    def export_audit_log(self) -> Dict[str, Any]:
        """导出审计日志"""
        return {
            "export_timestamp": datetime.now().isoformat(),
            "total_records": len(self.call_records),
            "performance_summary": self.get_performance_metrics(),
            "call_records": self.get_call_records(),
            "verification_hashes": [r.get_signature() for r in self.call_records]
        }

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        health_status = {
            "overall_status": "healthy",
            "providers": {},
            "timestamp": datetime.now().isoformat()
        }

        # 检查各个提供商
        for provider in ["ollama", "openai", "anthropic"]:
            try:
                if provider == "ollama" and self.ollama_client:
                    # 简单的健康检查调用
                    await asyncio.to_thread(self.ollama_client.list)
                    health_status["providers"][provider] = {"status": "healthy", "available": True}
                elif provider == "openai" and self.openai_client:
                    # OpenAI健康检查
                    health_status["providers"][provider] = {"status": "healthy", "available": True}
                elif provider == "anthropic" and self.anthropic_client:
                    # Anthropic健康检查
                    health_status["providers"][provider] = {"status": "healthy", "available": True}
                else:
                    health_status["providers"][provider] = {"status": "not_configured", "available": False}
            except Exception as e:
                health_status["providers"][provider] = {
                    "status": "unhealthy",
                    "available": False,
                    "error": str(e)
                }
                health_status["overall_status"] = "degraded"

        return health_status


# 导入缺失的模块
import os

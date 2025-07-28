#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM集成服务
提供统一的LLM调用接口，支持多后端、透明度监控和调用验证
"""

import asyncio
import hashlib
import hmac
import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum

import ollama

logger = logging.getLogger(__name__)


class LLMBackend(str, Enum):
    """支持的LLM后端"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    CLAUDE = "claude"


@dataclass
class LLMCall:
    """LLM调用记录"""
    call_id: str
    timestamp: str
    backend: str
    model: str
    prompt: str
    response: str
    duration: float
    token_usage: Dict[str, int]
    metadata: Dict[str, Any]
    signature: str
    hash: str


@dataclass
class LLMResponse:
    """LLM响应"""
    content: str
    model: str
    backend: str
    duration: float
    token_usage: Dict[str, int]
    metadata: Dict[str, Any]
    call_record: Optional[LLMCall] = None


class LLMIntegrationService:
    """LLM集成服务"""
    
    def __init__(self, secret_key: str = "daip_live_secret"):
        """
        初始化LLM集成服务
        
        Args:
            secret_key: 用于调用签名的密钥
        """
        self.secret_key = secret_key.encode()
        self.call_history: List[LLMCall] = []
        self.available_models = {}
        self._initialize_backends()
    
    def _initialize_backends(self):
        """初始化后端服务"""
        # 初始化Ollama
        try:
            models = ollama.list()
            ollama_models = []
            
            for model in models.get('models', []):
                model_name = model.get('model', model.get('name', ''))
                if model_name:
                    ollama_models.append({
                        'name': model_name,
                        'size': model.get('size', 0),
                        'supports_generation': 'embed' not in model_name.lower(),
                        'supports_embedding': 'embed' in model_name.lower()
                    })
            
            self.available_models[LLMBackend.OLLAMA] = ollama_models
            logger.info(f"Ollama initialized with {len(ollama_models)} models")
            
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {e}")
            self.available_models[LLMBackend.OLLAMA] = []
    
    def get_available_models(self, backend: LLMBackend = None) -> Dict[str, List[Dict]]:
        """
        获取可用模型列表
        
        Args:
            backend: 指定后端，None表示所有后端
            
        Returns:
            可用模型字典
        """
        if backend:
            return {backend: self.available_models.get(backend, [])}
        return self.available_models
    
    def _select_model(self, backend: LLMBackend, model: str = None, task: str = "generation") -> str:
        """
        选择合适的模型
        
        Args:
            backend: 后端类型
            model: 指定模型名称
            task: 任务类型 (generation/embedding)
            
        Returns:
            选择的模型名称
        """
        available = self.available_models.get(backend, [])
        
        if not available:
            raise ValueError(f"No models available for backend {backend}")
        
        if model:
            # 验证指定模型是否存在
            for m in available:
                if m['name'] == model:
                    return model
            raise ValueError(f"Model {model} not found in {backend}")
        
        # 自动选择合适的模型
        for m in available:
            if task == "generation" and m.get('supports_generation', True):
                return m['name']
            elif task == "embedding" and m.get('supports_embedding', False):
                return m['name']
        
        # 如果没有找到合适的模型，返回第一个
        return available[0]['name']
    
    def _generate_signature(self, model: str, prompt: str, timestamp: str) -> str:
        """生成调用签名"""
        data = f"{model}:{prompt}:{timestamp}"
        signature = hmac.new(
            self.secret_key,
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _create_call_record(
        self,
        backend: str,
        model: str,
        prompt: str,
        response: str,
        duration: float,
        token_usage: Dict[str, int],
        metadata: Dict[str, Any]
    ) -> LLMCall:
        """创建调用记录"""
        timestamp = datetime.now().isoformat()
        call_id = hashlib.md5(f"{timestamp}:{prompt}".encode()).hexdigest()[:16]
        
        signature = self._generate_signature(model, prompt, timestamp)
        
        call_data = {
            "call_id": call_id,
            "timestamp": timestamp,
            "backend": backend,
            "model": model,
            "prompt": prompt,
            "response": response,
            "duration": duration,
            "token_usage": token_usage,
            "metadata": metadata,
            "signature": signature
        }
        
        # 计算哈希
        call_hash = hashlib.sha256(
            json.dumps(call_data, sort_keys=True).encode()
        ).hexdigest()
        
        call_record = LLMCall(
            call_id=call_id,
            timestamp=timestamp,
            backend=backend,
            model=model,
            prompt=prompt,
            response=response,
            duration=duration,
            token_usage=token_usage,
            metadata=metadata,
            signature=signature,
            hash=call_hash
        )
        
        self.call_history.append(call_record)
        return call_record
    
    async def generate(
        self,
        prompt: str,
        model: str = None,
        backend: LLMBackend = LLMBackend.OLLAMA,
        temperature: float = 0.7,
        max_tokens: int = None,
        **kwargs
    ) -> LLMResponse:
        """
        生成文本
        
        Args:
            prompt: 输入提示
            model: 模型名称
            backend: 后端类型
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数
            
        Returns:
            LLM响应
        """
        start_time = time.time()
        
        try:
            # 选择模型
            selected_model = self._select_model(backend, model, "generation")
            
            if backend == LLMBackend.OLLAMA:
                # 准备Ollama参数
                options = {
                    'temperature': temperature
                }
                if max_tokens:
                    options['num_predict'] = max_tokens
                
                # 调用Ollama
                response = ollama.generate(
                    model=selected_model,
                    prompt=prompt,
                    options=options
                )
                
                content = response.get('response', '')
                
                # 估算token使用量（简化实现）
                token_usage = {
                    'prompt_tokens': len(prompt.split()),
                    'completion_tokens': len(content.split()),
                    'total_tokens': len(prompt.split()) + len(content.split())
                }
                
            else:
                raise NotImplementedError(f"Backend {backend} not implemented yet")
            
            end_time = time.time()
            duration = end_time - start_time
            
            # 创建调用记录
            call_record = self._create_call_record(
                backend=backend.value,
                model=selected_model,
                prompt=prompt,
                response=content,
                duration=duration,
                token_usage=token_usage,
                metadata={
                    'temperature': temperature,
                    'max_tokens': max_tokens,
                    **kwargs
                }
            )
            
            return LLMResponse(
                content=content,
                model=selected_model,
                backend=backend.value,
                duration=duration,
                token_usage=token_usage,
                metadata=call_record.metadata,
                call_record=call_record
            )
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise
    
    async def embed(
        self,
        text: str,
        model: str = None,
        backend: LLMBackend = LLMBackend.OLLAMA
    ) -> List[float]:
        """
        生成文本嵌入
        
        Args:
            text: 输入文本
            model: 模型名称
            backend: 后端类型
            
        Returns:
            嵌入向量
        """
        start_time = time.time()
        
        try:
            # 选择嵌入模型
            if not model:
                model = "nomic-embed-text"  # 默认嵌入模型
            
            if backend == LLMBackend.OLLAMA:
                response = ollama.embeddings(
                    model=model,
                    prompt=text
                )
                
                embedding = response.get('embedding', [])
                
            else:
                raise NotImplementedError(f"Backend {backend} not implemented yet")
            
            end_time = time.time()
            duration = end_time - start_time
            
            # 创建调用记录
            self._create_call_record(
                backend=backend.value,
                model=model,
                prompt=text,
                response=f"Embedding vector (dim={len(embedding)})",
                duration=duration,
                token_usage={'input_tokens': len(text.split())},
                metadata={'task': 'embedding', 'dimension': len(embedding)}
            )
            
            return embedding
            
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            raise
    
    def get_call_statistics(self) -> Dict[str, Any]:
        """获取调用统计信息"""
        if not self.call_history:
            return {
                'total_calls': 0,
                'total_duration': 0,
                'average_duration': 0,
                'backends_used': [],
                'models_used': []
            }
        
        total_calls = len(self.call_history)
        total_duration = sum(call.duration for call in self.call_history)
        average_duration = total_duration / total_calls
        
        backends_used = list(set(call.backend for call in self.call_history))
        models_used = list(set(call.model for call in self.call_history))
        
        # 按后端统计
        backend_stats = {}
        for backend in backends_used:
            backend_calls = [call for call in self.call_history if call.backend == backend]
            backend_stats[backend] = {
                'calls': len(backend_calls),
                'duration': sum(call.duration for call in backend_calls),
                'models': list(set(call.model for call in backend_calls))
            }
        
        return {
            'total_calls': total_calls,
            'total_duration': total_duration,
            'average_duration': average_duration,
            'backends_used': backends_used,
            'models_used': models_used,
            'backend_stats': backend_stats
        }
    
    def get_call_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """获取调用历史"""
        history = self.call_history
        if limit:
            history = history[-limit:]
        
        return [asdict(call) for call in history]
    
    def verify_call_integrity(self) -> Dict[str, Any]:
        """验证调用完整性"""
        if not self.call_history:
            return {'valid': True, 'message': 'No calls to verify'}
        
        for call in self.call_history:
            # 验证签名
            expected_signature = self._generate_signature(
                call.model, call.prompt, call.timestamp
            )
            
            if not hmac.compare_digest(call.signature, expected_signature):
                return {
                    'valid': False,
                    'message': f'Signature verification failed for call {call.call_id}'
                }
        
        return {
            'valid': True,
            'message': f'All {len(self.call_history)} calls verified successfully'
        }
    
    def export_transparency_report(self) -> Dict[str, Any]:
        """导出透明度报告"""
        stats = self.get_call_statistics()
        integrity = self.verify_call_integrity()
        
        return {
            'report_timestamp': datetime.now().isoformat(),
            'statistics': stats,
            'integrity_check': integrity,
            'call_history': self.get_call_history(),
            'available_models': self.available_models
        }


# 全局LLM服务实例
_llm_service = None

def get_llm_service() -> LLMIntegrationService:
    """获取全局LLM服务实例"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMIntegrationService()
    return _llm_service


# 便捷函数
async def generate_text(prompt: str, **kwargs) -> str:
    """便捷的文本生成函数"""
    service = get_llm_service()
    response = await service.generate(prompt, **kwargs)
    return response.content


async def generate_embedding(text: str, **kwargs) -> List[float]:
    """便捷的嵌入生成函数"""
    service = get_llm_service()
    return await service.embed(text, **kwargs)


def get_transparency_report() -> Dict[str, Any]:
    """获取透明度报告"""
    service = get_llm_service()
    return service.export_transparency_report()
"""
LLM调用验证机制

提供LLM调用的完整验证功能，包括调用签名生成、哈希验证、
调用历史审计和结果可重现性验证。
"""

import hashlib
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from .real_llm_integrator import LLMCallRecord

logger = logging.getLogger(__name__)


class VerificationStatus(Enum):
    """验证状态"""
    VERIFIED = "verified"
    FAILED = "failed"
    PENDING = "pending"
    INVALID = "invalid"


@dataclass
class VerificationResult:
    """验证结果"""
    call_id: str
    status: VerificationStatus
    confidence_score: float
    verification_timestamp: datetime
    details: Dict[str, Any]
    signature: str
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['status'] = self.status.value
        data['verification_timestamp'] = self.verification_timestamp.isoformat()
        return data


@dataclass
class AuditEntry:
    """审计条目"""
    entry_id: str
    call_id: str
    action: str
    timestamp: datetime
    details: Dict[str, Any]
    hash_chain: str
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class CallVerificationSystem:
    """
    LLM调用验证系统
    
    提供完整的LLM调用验证功能，确保调用的真实性、完整性和可追溯性。
    """
    
    def __init__(self):
        """初始化验证系统"""
        self.audit_log: List[AuditEntry] = []
        self.verification_cache: Dict[str, VerificationResult] = {}
        self.hash_chain: List[str] = []
        
        logger.info("CallVerificationSystem initialized")
    
    def generate_call_signature(self, record: LLMCallRecord) -> str:
        """
        生成调用签名
        
        Args:
            record: LLM调用记录
            
        Returns:
            调用签名
        """
        # 创建签名内容
        signature_data = {
            "call_id": record.call_id,
            "provider": record.provider,
            "model": record.model,
            "prompt_hash": hashlib.sha256(record.prompt.encode()).hexdigest(),
            "response_hash": hashlib.sha256(record.response.encode()).hexdigest() if record.response else "",
            "timestamp": record.timestamp.isoformat(),
            "duration_ms": record.duration_ms,
            "input_tokens": record.input_tokens,
            "output_tokens": record.output_tokens,
            "success": record.success
        }
        
        # 生成签名
        signature_content = json.dumps(signature_data, sort_keys=True)
        signature = hashlib.sha256(signature_content.encode()).hexdigest()
        
        # 记录审计日志
        self._add_audit_entry(
            record.call_id,
            "signature_generated",
            {"signature": signature, "signature_data": signature_data}
        )
        
        return signature
    
    def verify_call_signature(self, record: LLMCallRecord, expected_signature: str) -> bool:
        """
        验证调用签名
        
        Args:
            record: LLM调用记录
            expected_signature: 期望的签名
            
        Returns:
            验证是否通过
        """
        actual_signature = self.generate_call_signature(record)
        is_valid = actual_signature == expected_signature
        
        # 记录验证结果
        self._add_audit_entry(
            record.call_id,
            "signature_verified",
            {
                "expected_signature": expected_signature,
                "actual_signature": actual_signature,
                "is_valid": is_valid
            }
        )
        
        return is_valid
    
    def verify_call_integrity(self, record: LLMCallRecord) -> VerificationResult:
        """
        验证调用完整性
        
        Args:
            record: LLM调用记录
            
        Returns:
            验证结果
        """
        confidence_score = 0.0
        details = {}
        
        # 检查基本字段完整性
        required_fields = ["call_id", "provider", "model", "prompt", "timestamp"]
        missing_fields = [field for field in required_fields if not getattr(record, field, None)]
        
        if not missing_fields:
            confidence_score += 30.0
            details["basic_fields"] = "complete"
        else:
            details["basic_fields"] = f"missing: {missing_fields}"
        
        # 检查时间戳合理性
        if record.timestamp and record.timestamp <= datetime.now():
            confidence_score += 20.0
            details["timestamp"] = "valid"
        else:
            details["timestamp"] = "invalid or future"
        
        # 检查响应时间合理性
        if 0 < record.duration_ms < 300000:  # 0-5分钟是合理的
            confidence_score += 20.0
            details["duration"] = "reasonable"
        else:
            details["duration"] = f"unusual: {record.duration_ms}ms"
        
        # 检查Token数量合理性
        if record.success and record.input_tokens > 0:
            confidence_score += 15.0
            details["tokens"] = "valid"
        elif not record.success:
            confidence_score += 10.0  # 失败调用可能没有Token
            details["tokens"] = "acceptable for failed call"
        else:
            details["tokens"] = "invalid token count"
        
        # 检查提供商和模型匹配
        if self._validate_provider_model_combination(record.provider, record.model):
            confidence_score += 15.0
            details["provider_model"] = "valid combination"
        else:
            details["provider_model"] = "unusual combination"
        
        # 确定验证状态
        if confidence_score >= 80.0:
            status = VerificationStatus.VERIFIED
        elif confidence_score >= 60.0:
            status = VerificationStatus.PENDING
        else:
            status = VerificationStatus.FAILED
        
        # 生成签名
        signature = self.generate_call_signature(record)
        
        result = VerificationResult(
            call_id=record.call_id,
            status=status,
            confidence_score=confidence_score,
            verification_timestamp=datetime.now(),
            details=details,
            signature=signature
        )
        
        # 缓存结果
        self.verification_cache[record.call_id] = result
        
        # 记录审计日志
        self._add_audit_entry(
            record.call_id,
            "integrity_verified",
            {
                "status": status.value,
                "confidence_score": confidence_score,
                "details": details
            }
        )
        
        return result
    
    def _validate_provider_model_combination(self, provider: str, model: str) -> bool:
        """验证提供商和模型组合的合理性"""
        valid_combinations = {
            "ollama": ["llama3:instruct", "llama2", "codellama", "mistral"],
            "openai": ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"],
            "anthropic": ["claude-3-sonnet-20240229", "claude-3-opus-20240229", "claude-3-haiku-20240307"]
        }
        
        if provider not in valid_combinations:
            return False
        
        # 允许部分匹配（因为模型名称可能有版本号等）
        valid_models = valid_combinations[provider]
        return any(valid_model in model for valid_model in valid_models)
    
    def verify_call_reproducibility(
        self, 
        original_record: LLMCallRecord, 
        reproduction_record: LLMCallRecord
    ) -> Dict[str, Any]:
        """
        验证调用可重现性
        
        Args:
            original_record: 原始调用记录
            reproduction_record: 重现调用记录
            
        Returns:
            可重现性验证结果
        """
        reproducibility_score = 0.0
        comparison_details = {}
        
        # 比较输入参数
        if original_record.prompt == reproduction_record.prompt:
            reproducibility_score += 30.0
            comparison_details["prompt"] = "identical"
        else:
            comparison_details["prompt"] = "different"
        
        if original_record.provider == reproduction_record.provider:
            reproducibility_score += 20.0
            comparison_details["provider"] = "identical"
        else:
            comparison_details["provider"] = "different"
        
        if original_record.model == reproduction_record.model:
            reproducibility_score += 20.0
            comparison_details["model"] = "identical"
        else:
            comparison_details["model"] = "different"
        
        # 比较输出（考虑LLM的随机性）
        response_similarity = self._calculate_response_similarity(
            original_record.response, reproduction_record.response
        )
        reproducibility_score += response_similarity * 30.0
        comparison_details["response_similarity"] = response_similarity
        
        # 记录审计日志
        self._add_audit_entry(
            original_record.call_id,
            "reproducibility_tested",
            {
                "reproduction_call_id": reproduction_record.call_id,
                "reproducibility_score": reproducibility_score,
                "comparison_details": comparison_details
            }
        )
        
        return {
            "reproducibility_score": reproducibility_score,
            "is_reproducible": reproducibility_score >= 70.0,
            "comparison_details": comparison_details,
            "original_call_id": original_record.call_id,
            "reproduction_call_id": reproduction_record.call_id
        }
    
    def _calculate_response_similarity(self, response1: str, response2: str) -> float:
        """计算响应相似度"""
        if not response1 or not response2:
            return 0.0
        
        # 简单的相似度计算（实际应用中可以使用更复杂的算法）
        words1 = set(response1.lower().split())
        words2 = set(response2.lower().split())
        
        if not words1 and not words2:
            return 1.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def generate_audit_trail(self, call_id: str) -> Dict[str, Any]:
        """
        生成审计轨迹
        
        Args:
            call_id: 调用ID
            
        Returns:
            审计轨迹
        """
        related_entries = [
            entry for entry in self.audit_log
            if entry.call_id == call_id
        ]
        
        return {
            "call_id": call_id,
            "audit_entries": [entry.to_dict() for entry in related_entries],
            "total_entries": len(related_entries),
            "first_entry": related_entries[0].timestamp.isoformat() if related_entries else None,
            "last_entry": related_entries[-1].timestamp.isoformat() if related_entries else None,
            "hash_chain_verification": self._verify_hash_chain(related_entries)
        }
    
    def _verify_hash_chain(self, entries: List[AuditEntry]) -> Dict[str, Any]:
        """验证哈希链"""
        if not entries:
            return {"valid": True, "reason": "no entries"}
        
        # 验证每个条目的哈希链
        for i, entry in enumerate(entries):
            expected_hash = self._calculate_entry_hash(entry, entries[i-1] if i > 0 else None)
            if entry.hash_chain != expected_hash:
                return {
                    "valid": False,
                    "reason": f"hash mismatch at entry {i}",
                    "expected": expected_hash,
                    "actual": entry.hash_chain
                }
        
        return {"valid": True, "reason": "all hashes verified"}
    
    def _add_audit_entry(self, call_id: str, action: str, details: Dict[str, Any]):
        """添加审计条目"""
        entry_id = f"{call_id}_{action}_{int(datetime.now().timestamp())}"
        
        # 计算哈希链
        previous_entry = self.audit_log[-1] if self.audit_log else None
        hash_chain = self._calculate_entry_hash_for_new_entry(
            entry_id, call_id, action, details, previous_entry
        )
        
        entry = AuditEntry(
            entry_id=entry_id,
            call_id=call_id,
            action=action,
            timestamp=datetime.now(),
            details=details,
            hash_chain=hash_chain
        )
        
        self.audit_log.append(entry)
        self.hash_chain.append(hash_chain)
    
    def _calculate_entry_hash(self, entry: AuditEntry, previous_entry: Optional[AuditEntry]) -> str:
        """计算条目哈希"""
        return self._calculate_entry_hash_for_new_entry(
            entry.entry_id,
            entry.call_id,
            entry.action,
            entry.details,
            previous_entry
        )
    
    def _calculate_entry_hash_for_new_entry(
        self,
        entry_id: str,
        call_id: str,
        action: str,
        details: Dict[str, Any],
        previous_entry: Optional[AuditEntry]
    ) -> str:
        """为新条目计算哈希"""
        hash_content = {
            "entry_id": entry_id,
            "call_id": call_id,
            "action": action,
            "details": details,
            "previous_hash": previous_entry.hash_chain if previous_entry else "genesis"
        }
        
        content_str = json.dumps(hash_content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()
    
    def get_verification_summary(self) -> Dict[str, Any]:
        """获取验证摘要"""
        total_verifications = len(self.verification_cache)
        
        if total_verifications == 0:
            return {
                "total_verifications": 0,
                "verification_stats": {},
                "audit_stats": {"total_entries": len(self.audit_log)}
            }
        
        status_counts = {}
        confidence_scores = []
        
        for result in self.verification_cache.values():
            status_counts[result.status.value] = status_counts.get(result.status.value, 0) + 1
            confidence_scores.append(result.confidence_score)
        
        return {
            "total_verifications": total_verifications,
            "verification_stats": {
                "status_distribution": status_counts,
                "average_confidence": sum(confidence_scores) / len(confidence_scores),
                "verification_rate": status_counts.get("verified", 0) / total_verifications * 100
            },
            "audit_stats": {
                "total_entries": len(self.audit_log),
                "unique_calls": len(set(entry.call_id for entry in self.audit_log)),
                "hash_chain_length": len(self.hash_chain)
            }
        }
    
    def export_verification_report(self, call_id: Optional[str] = None) -> Dict[str, Any]:
        """
        导出验证报告
        
        Args:
            call_id: 可选的特定调用ID
            
        Returns:
            验证报告
        """
        if call_id:
            # 导出特定调用的报告
            verification_result = self.verification_cache.get(call_id)
            audit_trail = self.generate_audit_trail(call_id)
            
            return {
                "report_type": "single_call",
                "call_id": call_id,
                "verification_result": verification_result.to_dict() if verification_result else None,
                "audit_trail": audit_trail,
                "export_timestamp": datetime.now().isoformat()
            }
        else:
            # 导出完整报告
            return {
                "report_type": "complete",
                "verification_summary": self.get_verification_summary(),
                "all_verifications": [result.to_dict() for result in self.verification_cache.values()],
                "complete_audit_log": [entry.to_dict() for entry in self.audit_log],
                "hash_chain": self.hash_chain,
                "export_timestamp": datetime.now().isoformat()
            }
    
    def validate_system_integrity(self) -> Dict[str, Any]:
        """验证系统完整性"""
        integrity_checks = {
            "hash_chain_valid": True,
            "audit_log_consistent": True,
            "verification_cache_valid": True,
            "issues": []
        }
        
        # 检查哈希链完整性
        for i, entry in enumerate(self.audit_log):
            expected_hash = self._calculate_entry_hash(entry, self.audit_log[i-1] if i > 0 else None)
            if entry.hash_chain != expected_hash:
                integrity_checks["hash_chain_valid"] = False
                integrity_checks["issues"].append(f"Hash chain broken at entry {i}")
        
        # 检查审计日志一致性
        call_ids_in_audit = set(entry.call_id for entry in self.audit_log)
        call_ids_in_cache = set(self.verification_cache.keys())
        
        if not call_ids_in_cache.issubset(call_ids_in_audit):
            integrity_checks["audit_log_consistent"] = False
            missing_calls = call_ids_in_cache - call_ids_in_audit
            integrity_checks["issues"].append(f"Missing audit entries for calls: {missing_calls}")
        
        # 检查验证缓存有效性
        for call_id, result in self.verification_cache.items():
            if not result.signature:
                integrity_checks["verification_cache_valid"] = False
                integrity_checks["issues"].append(f"Missing signature for call: {call_id}")
        
        integrity_checks["overall_valid"] = (
            integrity_checks["hash_chain_valid"] and
            integrity_checks["audit_log_consistent"] and
            integrity_checks["verification_cache_valid"]
        )
        
        return integrity_checks
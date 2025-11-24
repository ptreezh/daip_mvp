"""
模型自适应系统 - 实现动态模型检测和智能分配
"""
import asyncio
import subprocess
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import json
from pydantic import BaseModel, Field


class ModelInfo(BaseModel):
    """模型信息"""
    name: str
    provider: str = "ollama"
    size: str = "unknown"
    modified: str = "unknown"
    description: str = ""
    capabilities: List[str] = Field(default_factory=list)  # 模型能力标签
    performance_rating: float = 1.0  # 性能评分 (0.0-1.0)
    availability: bool = True


class ModelAdapterManager:
    """模型适配管理器 - 实现动态模型检测与智能分配"""
    
    def __init__(self):
        self._available_models: List[ModelInfo] = []
        self._default_model: Optional[ModelInfo] = None
        self._role_model_preferences: Dict[str, str] = {}  # 角色-模型偏好
        self._model_usage_stats: Dict[str, Dict] = {}  # 模型使用统计
        self._last_scan_time: Optional[datetime] = None
        
        # 扫描可用模型
        self._detect_available_models()
        
        # 设置默认模型
        self._set_default_model()
    
    def _detect_available_models(self) -> List[ModelInfo]:
        """扫描系统中的可用模型"""
        models = []
        
        # 扫描 Ollama 模型
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:  # 跳过标题行
                    for line in lines[1:]:
                        if line.strip():
                            parts = line.split()
                            if len(parts) >= 2:  # 确保有足够的部分
                                model_name = parts[0]
                                model_size = parts[1] if len(parts) > 1 else "unknown"
                                model_modified = parts[2] if len(parts) > 2 else "unknown"
                                
                                # 分析模型名称确定能力
                                capabilities = self._analyze_model_capabilities(model_name)
                                performance_rating = self._estimate_performance_rating(model_name, model_size)
                                
                                model_info = ModelInfo(
                                    name=model_name,
                                    provider="ollama",
                                    size=model_size,
                                    modified=model_modified,
                                    capabilities=capabilities,
                                    performance_rating=performance_rating
                                )
                                
                                models.append(model_info)
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            # Ollama 可能未安装或未运行，这是允许的
            print("⚠️  Ollama 未安装或未运行，跳过模型扫描")
        
        self._available_models = models
        self._last_scan_time = datetime.now()
        
        return models
    
    def _analyze_model_capabilities(self, model_name: str) -> List[str]:
        """分析模型能力"""
        capabilities = []
        name_lower = model_name.lower()
        
        if any(keyword in name_lower for keyword in ["gpt", "llama", "claude"]):
            capabilities.append("general")
        if any(keyword in name_lower for keyword in ["code", "codellama", "stable-code"]):
            capabilities.append("code")
        if any(keyword in name_lower for keyword in ["vision", "image", "vlm"]):
            capabilities.append("vision")
        if any(keyword in name_lower for keyword in ["text", "instruct", "chat"]):
            capabilities.append("instruction_following")
        if any(keyword in name_lower for keyword in ["math", "reasoning", "phi"]):
            capabilities.append("reasoning")
        if any(keyword in name_lower for keyword in ["small", "mini", "7b", "8b"]):
            capabilities.append("lightweight")
        if any(keyword in name_lower for keyword in ["large", "70b"]):
            capabilities.append("high_capacity")
        
        return capabilities if capabilities else ["general"]
    
    def _estimate_performance_rating(self, model_name: str, size: str) -> float:
        """估计模型性能评级"""
        # 基于模型名称和大小估计性能
        rating = 0.5  # 默认中等性能
        
        model_name_lower = model_name.lower()
        if any(keyword in model_name_lower for keyword in ["70b", "large", "mistral-large"]):
            rating = 0.9  # 大模型
        elif any(keyword in model_name_lower for keyword in ["7b", "small", "mini"]):
            rating = 0.6  # 小模型
        elif any(keyword in model_name_lower for keyword in ["8b", "medium"]):
            rating = 0.75  # 中等模型
        else:
            rating = 0.7  # 默认中等
            
        # 调整基于大小
        try:
            if "GB" in size:
                size_val = float(size.replace("GB", "").strip())
                if size_val > 10:
                    rating += 0.1
                elif size_val < 3:
                    rating -= 0.1
        except:
            # 如果无法解析大小，保持默认评分
            pass
        
        return min(rating, 1.0)
    
    def _set_default_model(self):
        """设置默认模型 - 选择最适合的通用模型"""
        if not self._available_models:
            # 如果没有可用模型，使用备用模型
            self._default_model = ModelInfo(
                name="llama3:instruct",
                provider="ollama",
                description="Default fallback model",
                capabilities=["general", "instruction_following"],
                performance_rating=0.5
            )
            return
        
        # 选择性能良好且通用能力的模型
        preferred_models = [
            model for model in self._available_models
            if "general" in model.capabilities and "instruction_following" in model.capabilities
        ]
        
        if preferred_models:
            # 选择性能最好的通用模型
            best_model = max(preferred_models, key=lambda m: m.performance_rating)
            self._default_model = best_model
        else:
            # 否则选择评分最高的模型
            best_model = max(self._available_models, key=lambda m: m.performance_rating)
            self._default_model = best_model
    
    def get_available_models(self) -> List[ModelInfo]:
        """获取可用模型列表"""
        return self._available_models
    
    def get_default_model(self) -> ModelInfo:
        """获取默认模型"""
        return self._default_model
    
    def refresh_model_list(self) -> List[ModelInfo]:
        """刷新模型列表"""
        return self._detect_available_models()
    
    def select_best_model_for_task(self, role_type: str = "general", task_type: str = "general") -> ModelInfo:
        """为特定任务选择最佳模型"""
        if not self._available_models:
            return self._default_model
        
        # 根据任务类型筛选模型
        matching_models = []
        
        for model in self._available_models:
            score = 0
            
            # 根据角色类型匹配
            if role_type and "researcher" in role_type.lower() and "reasoning" in model.capabilities:
                score += 2
            elif role_type and "writer" in role_type.lower() and "instruction_following" in model.capabilities:
                score += 2
            elif role_type and "analyst" in role_type.lower() and "reasoning" in model.capabilities:
                score += 2
            elif role_type and "expert" in role_type.lower() and "high_capacity" in model.capabilities:
                score += 2
            else:
                score += 1  # 通用评分
            
            # 根据任务类型匹配
            if task_type == "analysis" and "reasoning" in model.capabilities:
                score += 1
            elif task_type == "writing" and "instruction_following" in model.capabilities:
                score += 1
            elif task_type == "coding" and "code" in model.capabilities:
                score += 1
            elif task_type == "vision" and "vision" in model.capabilities:
                score += 1
            else:
                score += 0.5  # 通用任务支持
                
            matching_models.append((model, score))
        
        # 选择得分最高的模型
        if matching_models:
            best_model, best_score = max(matching_models, key=lambda x: x[1])
            return best_model
        else:
            # 如果没有匹配，返回默认模型
            return self._default_model
    
    def get_model_for_debate_role(self, role_name: str) -> ModelInfo:
        """为辩论角色分配模型"""
        # 基于角色名称确定模型需求
        if "pro" in role_name.lower() or "affirmative" in role_name.lower() or "支持" in role_name:
            task_type = "argumentation"
        elif "con" in role_name.lower() or "negative" in role_name.lower() or "反对" in role_name:
            task_type = "counter_argumentation" 
        elif "research" in role_name.lower() or "研究员" in role_name:
            task_type = "research"
        elif "moderator" in role_name.lower() or "主持" in role_name:
            task_type = "mediation"
        elif "analyst" in role_name.lower() or "分析" in role_name:
            task_type = "analysis"
        elif "expert" in role_name.lower() or "专家" in role_name:
            task_type = "expertise"
        else:
            task_type = "general"
        
        return self.select_best_model_for_task(role_name, task_type)
    
    def get_model_usage_stats(self, model_name: str = None) -> Dict[str, any]:
        """获取模型使用统计数据"""
        if model_name:
            return self._model_usage_stats.get(model_name, {})
        return self._model_usage_stats
    
    def record_model_usage(self, model_name: str, response_time: float, success: bool):
        """记录模型使用情况"""
        if model_name not in self._model_usage_stats:
            self._model_usage_stats[model_name] = {
                "usage_count": 0,
                "success_count": 0,
                "avg_response_time": 0.0,
                "last_used": None
            }
        
        stats = self._model_usage_stats[model_name]
        stats["usage_count"] += 1
        if success:
            stats["success_count"] += 1
        stats["last_used"] = datetime.now().isoformat()
        
        # 更新平均响应时间
        old_avg = stats["avg_response_time"]
        new_count = stats["usage_count"]
        if new_count > 0:
            new_avg = ((old_avg * (new_count-1)) + response_time) / new_count
            stats["avg_response_time"] = new_avg
    
    async def async_test_model_availability(self, model_name: str) -> bool:
        """异步测试模型可用性"""
        try:
            # 简单测试模型是否可用
            result = await asyncio.to_thread(subprocess.run, 
                                            ["ollama", "show", model_name], 
                                            capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def get_model_performance_report(self) -> str:
        """生成模型性能报告"""
        if not self._available_models:
            return "No models detected in system"
        
        report_parts = ["模型性能报告:", f"最后扫描时间: {self._last_scan_time}", "", "可用模型:"] 
        
        for i, model in enumerate(self._available_models, 1):
            stats = self._model_usage_stats.get(model.name, {"usage_count": 0, "success_count": 0})
            success_rate = stats["success_count"] / stats["usage_count"] if stats["usage_count"] > 0 else 0
            
            report_parts.append(
                f"{i:2d}. {model.name} ({model.size})"
                f" - 能力: {', '.join(model.capabilities[:3])}"
                f", 性能评级: {model.performance_rating:.1f}"
                f", 使用: {stats['usage_count']}次"
                f", 成功率: {success_rate:.1f}"
            )
        
        if self._default_model:
            report_parts.append(f"", f"当前默认模型: {self._default_model.name}", "")
        
        return "\n".join(report_parts)


# 便捷函数：创建模型适配管理器并集成到现有系统
def create_model_adapter_manager():
    """创建模型适配管理器实例"""
    return ModelAdapterManager()
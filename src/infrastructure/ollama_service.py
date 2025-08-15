"""@Time    : 2025-08-06 10:30:00
@Author  : DAIP-LIVE Team
@File    : ollama_service.py
@Description:
    Ollama LLM service integration for DAIP backend.
    Handles LLM communication, prompt management, and model orchestration.
"""

import asyncio
import json
import logging
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

import aiohttp

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    # 创建虚拟类用于类型提示
    class ollama:
        class Client:
            pass


@dataclass
class LLMMessage:
    """LLM消息"""
    role: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMRequest:
    """LLM请求"""
    model: str
    messages: list[LLMMessage]
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 0.9
    stream: bool = False
    tools: Optional[list[dict[str, Any]]] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    """LLM响应"""
    model: str
    content: str
    finish_reason: str
    usage: dict[str, int]
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class LLMModel:
    """LLM模型信息"""
    name: str
    size: str
    modified_at: datetime
    digest: str
    details: dict[str, Any] = field(default_factory=dict)


class OllamaService:
    """Ollama LLM服务 - 管理LLM通信和模型操作"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        if not OLLAMA_AVAILABLE:
            raise ImportError("ollama package is required. Install with: pip install ollama")
        
        self.base_url = base_url
        self.client: Optional[ollama.Client] = None
        self.available_models: list[LLMModel] = []
        self.default_model = "llama3.2:latest"
        
        # 统计信息
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens_used": 0,
            "total_response_time": 0.0,
            "average_response_time": 0.0,
            "model_usage": {},
            "start_time": datetime.now()
        }
        
        # 配置参数
        self.config = {
            "timeout": 300,  # 5分钟
            "retry_attempts": 3,
            "retry_delay": 1,
            "enable_streaming": True,
            "enable_tool_use": True,
            "max_concurrent_requests": 10,
            "request_queue_size": 100
        }
        
        # 请求队列
        self.request_queue: asyncio.Queue = asyncio.Queue()
        self.active_requests: dict[str, asyncio.Task] = {}
        
        # 后台任务
        self._model_refresh_task: Optional[asyncio.Task] = None
        self._request_processor_task: Optional[asyncio.Task] = None
        self._is_running = False
    
    async def initialize(self):
        """初始化Ollama服务"""
        try:
            # 创建Ollama客户端
            self.client = ollama.Client(host=self.base_url)
            
            # 测试连接
            await self._test_connection()
            
            # 刷新可用模型
            await self.refresh_models()
            
            # 启动后台任务
            self._is_running = True
            self._model_refresh_task = asyncio.create_task(self._periodic_model_refresh())
            self._request_processor_task = asyncio.create_task(self._process_request_queue())
            
            logging.info(f"Ollama service initialized with {len(self.available_models)} models")
            
        except Exception as e:
            logging.error(f"Failed to initialize Ollama service: {e}")
            raise
    
    async def start(self):
        """启动Ollama服务"""
        if not self.client:
            await self.initialize()
        
        if self._is_running:
            return
        
        self._is_running = True
        logging.info("Ollama service started")
    
    async def stop(self):
        """停止Ollama服务"""
        if not self._is_running:
            return
        
        self._is_running = False
        
        # 取消后台任务
        if self._model_refresh_task:
            self._model_refresh_task.cancel()
        
        if self._request_processor_task:
            self._request_processor_task.cancel()
        
        # 取消所有活跃请求
        for request_id, task in self.active_requests.items():
            task.cancel()
        
        self.active_requests.clear()
        
        logging.info("Ollama service stopped")
    
    async def _test_connection(self):
        """测试Ollama连接"""
        try:
            # 列出本地模型
            models = await self._ollama_list_local()
            logging.info(f"Connected to Ollama, found {len(models)} local models")
            return True
            
        except Exception as e:
            logging.error(f"Ollama connection test failed: {e}")
            return False
    
    async def refresh_models(self):
        """刷新可用模型列表"""
        try:
            # 获取本地模型
            local_models = await self._ollama_list_local()
            
            # 获取可用模型
            available_models = await self._ollama_list()
            
            # 合并模型信息
            self.available_models = []
            
            # 处理本地模型
            for model in local_models:
                model_info = LLMModel(
                    name=model["name"],
                    size=model.get("size", "unknown"),
                    modified_at=datetime.fromisoformat(model["modified_at"].replace("Z", "+00:00")),
                    digest=model.get("digest", ""),
                    details=model
                )
                self.available_models.append(model_info)
            
            # 处理远程模型（不在本地的）
            local_names = {model["name"] for model in local_models}
            for model in available_models:
                if model["name"] not in local_names:
                    model_info = LLMModel(
                        name=model["name"],
                        size="remote",
                        modified_at=datetime.now(),
                        digest="",
                        details=model
                    )
                    self.available_models.append(model_info)
            
            logging.info(f"Refreshed models: {len(self.available_models)} available")
            
        except Exception as e:
            logging.error(f"Failed to refresh models: {e}")
    
    async def _periodic_model_refresh(self):
        """定期刷新模型列表"""
        while self._is_running:
            try:
                await asyncio.sleep(3600)  # 每小时刷新一次
                await self.refresh_models()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error in model refresh task: {e}")
    
    async def _process_request_queue(self):
        """处理请求队列"""
        while self._is_running:
            try:
                # 从队列获取请求
                request_future = await self.request_queue.get()
                
                # 执行请求
                asyncio.create_task(self._execute_queued_request(request_future))
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error in request processor: {e}")
    
    async def _execute_queued_request(self, request_future: asyncio.Future):
        """执行队列中的请求"""
        try:
            request_data = request_future.get_result()
            request_id = request_data["request_id"]
            llm_request = request_data["llm_request"]
            
            # 执行LLM请求
            response = await self._execute_llm_request(llm_request)
            
            # 设置结果
            request_future.set_result(response)
            
        except Exception as e:
            if not request_future.done():
                request_future.set_exception(e)
    
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """生成LLM响应"""
        if not self.client:
            await self.initialize()
        
        # 更新统计
        self.stats["total_requests"] += 1
        
        try:
            start_time = datetime.now()
            
            # 执行请求
            response = await self._execute_llm_request(request)
            
            # 更新统计
            response_time = (datetime.now() - start_time).total_seconds()
            self.stats["successful_requests"] += 1
            self.stats["total_response_time"] += response_time
            self.stats["average_response_time"] = (
                (self.stats["average_response_time"] * (self.stats["successful_requests"] - 1) + response_time) /
                self.stats["successful_requests"]
            )
            
            # 更新模型使用统计
            model_name = response.model
            if model_name not in self.stats["model_usage"]:
                self.stats["model_usage"][model_name] = {
                    "requests": 0,
                    "tokens_used": 0,
                    "average_response_time": 0.0
                }
            
            model_stats = self.stats["model_usage"][model_name]
            model_stats["requests"] += 1
            model_stats["tokens_used"] += response.usage.get("total_tokens", 0)
            model_stats["average_response_time"] = (
                (model_stats["average_response_time"] * (model_stats["requests"] - 1) + response_time) /
                model_stats["requests"]
            )
            
            return response
            
        except Exception as e:
            self.stats["failed_requests"] += 1
            logging.error(f"Failed to generate LLM response: {e}")
            raise
    
    async def generate_response_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """生成流式LLM响应"""
        if not self.client:
            await self.initialize()
        
        # 更新统计
        self.stats["total_requests"] += 1
        
        try:
            start_time = datetime.now()
            
            # 转换消息格式
            ollama_messages = [
                {"role": msg.role, "content": msg.content} 
                for msg in request.messages
            ]
            
            # 生成流式响应
            async for chunk in self.client.chat(
                model=request.model,
                messages=ollama_messages,
                stream=True,
                options={
                    "temperature": request.temperature,
                    "top_p": request.top_p,
                    "num_predict": request.max_tokens
                }
            ):
                if chunk["message"]["content"]:
                    yield chunk["message"]["content"]
            
            # 更新统计
            response_time = (datetime.now() - start_time).total_seconds()
            self.stats["successful_requests"] += 1
            self.stats["total_response_time"] += response_time
            
        except Exception as e:
            self.stats["failed_requests"] += 1
            logging.error(f"Failed to generate streaming LLM response: {e}")
            raise
    
    async def _execute_llm_request(self, request: LLMRequest) -> LLMResponse:
        """执行LLM请求"""
        # 转换消息格式
        ollama_messages = [
            {"role": msg.role, "content": msg.content} 
            for msg in request.messages
        ]
        
        # 准备选项
        options = {
            "temperature": request.temperature,
            "top_p": request.top_p,
            "num_predict": request.max_tokens
        }
        
        # 执行请求
        response = await self.client.chat(
            model=request.model,
            messages=ollama_messages,
            stream=False,
            options=options
        )
        
        # 转换响应格式
        return LLMResponse(
            model=request.model,
            content=response["message"]["content"],
            finish_reason=response.get("done_reason", "stop"),
            usage={
                "prompt_tokens": response.get("prompt_eval_count", 0),
                "completion_tokens": response.get("eval_count", 0),
                "total_tokens": response.get("prompt_eval_count", 0) + response.get("eval_count", 0)
            },
            metadata={
                "model": response.get("model"),
                "created_at": response.get("created_at"),
                "total_duration": response.get("total_duration")
            }
        )
    
    async def _ollama_list(self) -> list[dict[str, Any]]:
        """获取Ollama可用模型列表"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("models", [])
                    else:
                        return []
        except Exception as e:
            logging.error(f"Failed to get Ollama models: {e}")
            return []
    
    async def _ollama_list_local(self) -> list[dict[str, Any]]:
        """获取本地Ollama模型列表"""
        try:
            models = self.client.list()
            return models.get("models", [])
        except Exception as e:
            logging.error(f"Failed to get local Ollama models: {e}")
            return []
    
    async def pull_model(self, model_name: str) -> bool:
        """拉取模型"""
        try:
            logging.info(f"Pulling model: {model_name}")
            
            # 流式拉取
            async for chunk in self.client.pull(model_name, stream=True):
                if "status" in chunk:
                    logging.info(f"Pull status: {chunk['status']}")
            
            logging.info(f"Successfully pulled model: {model_name}")
            await self.refresh_models()
            return True
            
        except Exception as e:
            logging.error(f"Failed to pull model {model_name}: {e}")
            return False
    
    async def delete_model(self, model_name: str) -> bool:
        """删除模型"""
        try:
            self.client.delete(model_name)
            logging.info(f"Successfully deleted model: {model_name}")
            await self.refresh_models()
            return True
            
        except Exception as e:
            logging.error(f"Failed to delete model {model_name}: {e}")
            return False
    
    async def get_model_info(self, model_name: str) -> Optional[LLMModel]:
        """获取模型信息"""
        for model in self.available_models:
            if model.name == model_name:
                return model
        return None
    
    async def list_models(self) -> list[LLMModel]:
        """列出所有可用模型"""
        return self.available_models
    
    async def get_system_info(self) -> dict[str, Any]:
        """获取系统信息"""
        try:
            # 获取系统信息
            system_info = {}
            
            # Ollama版本
            try:
                version_response = await self.client.version()
                system_info["ollama_version"] = version_response.get("version", "unknown")
            except:
                system_info["ollama_version"] = "unknown"
            
            # 系统统计
            system_info["statistics"] = self.stats.copy()
            system_info["statistics"]["uptime"] = (datetime.now() - self.stats["start_time"]).total_seconds()
            
            # 模型信息
            system_info["models"] = {
                "total": len(self.available_models),
                "local": len([m for m in self.available_models if m.size != "remote"]),
                "remote": len([m for m in self.available_models if m.size == "remote"])
            }
            
            # 配置信息
            system_info["config"] = self.config.copy()
            
            return system_info
            
        except Exception as e:
            logging.error(f"Failed to get system info: {e}")
            return {"error": str(e)}
    
    async def health_check(self) -> dict[str, Any]:
        """健康检查"""
        try:
            # 测试基本功能
            test_request = LLMRequest(
                model=self.default_model,
                messages=[LLMMessage(role="user", content="Hello, please respond with 'OK'")]
            )
            
            test_response = await self.generate_response(test_request)
            
            if "OK" in test_response.content:
                return {
                    "status": "healthy",
                    "is_healthy": True,
                    "message": "Ollama service is functioning properly",
                    "available_models": len(self.available_models),
                    "default_model": self.default_model,
                    "last_check": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "degraded",
                    "is_healthy": False,
                    "message": "Ollama service responded but content was unexpected",
                    "last_check": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "unhealthy",
                "is_healthy": False,
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
    
    async def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        uptime = (datetime.now() - self.stats["start_time"]).total_seconds()
        
        return {
            "total_requests": self.stats["total_requests"],
            "successful_requests": self.stats["successful_requests"],
            "failed_requests": self.stats["failed_requests"],
            "success_rate": self.stats["successful_requests"] / self.stats["total_requests"] if self.stats["total_requests"] > 0 else 0,
            "total_tokens_used": self.stats["total_tokens_used"],
            "average_response_time": self.stats["average_response_time"],
            "uptime_seconds": uptime,
            "model_usage": self.stats["model_usage"],
            "available_models": len(self.available_models),
            "is_running": self._is_running
        }
    
    async def clear_stats(self):
        """清空统计信息"""
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens_used": 0,
            "total_response_time": 0.0,
            "average_response_time": 0.0,
            "model_usage": {},
            "start_time": datetime.now()
        }


# 全局Ollama服务实例
_ollama_service: Optional[OllamaService] = None


async def get_ollama_service(base_url: str = None) -> OllamaService:
    """获取Ollama服务实例"""
    global _ollama_service
    
    if _ollama_service is None:
        if base_url is None:
            base_url = "http://localhost:11434"
        
        _ollama_service = OllamaService(base_url)
        await _ollama_service.initialize()
    
    return _ollama_service


async def close_ollama_service():
    """关闭Ollama服务"""
    global _ollama_service
    
    if _ollama_service:
        await _ollama_service.stop()
        _ollama_service = None


# 便捷函数
async def generate_llm_response(
    model: str,
    messages: list[LLMMessage],
    temperature: float = 0.7,
    max_tokens: int = 2000,
    base_url: str = None
) -> LLMResponse:
    """生成LLM响应的便捷函数"""
    service = await get_ollama_service(base_url)
    
    request = LLMRequest(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    return await service.generate_response(request)


async def generate_llm_response_stream(
    model: str,
    messages: list[LLMMessage],
    temperature: float = 0.7,
    max_tokens: int = 2000,
    base_url: str = None
) -> AsyncGenerator[str, None]:
    """生成流式LLM响应的便捷函数"""
    service = await get_ollama_service(base_url)
    
    request = LLMRequest(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True
    )
    
    async for chunk in service.generate_response_stream(request):
        yield chunk


class DAIPWorkflowIntegrator:
    """DAIP工作流集成器 - 集成现有DAIP工作流引擎"""
    
    def __init__(self, ollama_service: OllamaService):
        self.ollama_service = ollama_service
        self.workflow_templates = self._load_workflow_templates()
    
    def _load_workflow_templates(self) -> dict[str, Any]:
        """加载工作流模板"""
        return {
            "academic_research": {
                "name": "学术研究工作流",
                "description": "学术研究和论文写作工作流",
                "steps": [
                    "文献综述",
                    "研究问题定义",
                    "方法论设计",
                    "数据收集与分析",
                    "结果讨论",
                    "结论与建议"
                ]
            },
            "critical_review": {
                "name": "批判性审查工作流",
                "description": "批判性分析和审查工作流",
                "steps": [
                    "主题分析",
                    "多角度评估",
                    "证据收集",
                    "逻辑验证",
                    "综合评价",
                    "改进建议"
                ]
            },
            "expert_consultation": {
                "name": "专家咨询工作流",
                "description": "专家咨询和建议工作流",
                "steps": [
                    "需求分析",
                    "专家匹配",
                    "问题分解",
                    "解决方案生成",
                    "可行性评估",
                    "实施建议"
                ]
            }
        }
    
    async def execute_workflow(self, workflow_name: str, input_data: dict[str, Any]) -> dict[str, Any]:
        """执行工作流"""
        if workflow_name not in self.workflow_templates:
            raise ValueError(f"Unknown workflow: {workflow_name}")
        
        workflow = self.workflow_templates[workflow_name]
        
        # 创建工作流执行上下文
        context = {
            "workflow_name": workflow_name,
            "input_data": input_data,
            "current_step": 0,
            "steps": workflow["steps"],
            "results": {},
            "start_time": datetime.now()
        }
        
        # 执行工作流步骤
        for step_name in workflow["steps"]:
            step_result = await self._execute_workflow_step(step_name, context, input_data)
            context["results"][step_name] = step_result
            context["current_step"] += 1
        
        # 生成最终结果
        final_result = await self._generate_workflow_summary(context)
        
        return {
            "workflow_name": workflow_name,
            "workflow_description": workflow["description"],
            "steps": workflow["steps"],
            "results": context["results"],
            "summary": final_result,
            "execution_time": (datetime.now() - context["start_time"]).total_seconds()
        }
    
    async def _execute_workflow_step(self, step_name: str, context: dict[str, Any], input_data: dict[str, Any]) -> dict[str, Any]:
        """执行工作流步骤"""
        # 根据步骤类型生成不同的提示
        if step_name == "文献综述":
            prompt = f"""请对以下研究主题进行文献综述：
            
主题：{input_data.get('topic', '')}
研究问题：{input_data.get('research_question', '')}

请提供：
1. 相关文献概述
2. 主要研究趋势
3. 研究空白
4. 未来研究方向"""

        elif step_name == "多角度评估":
            prompt = f"""请从多个角度评估以下内容：

内容：{input_data.get('content', '')}

请从以下角度进行评估：
1. 技术可行性
2. 经济合理性
3. 社会影响
4. 环境可持续性
5. 法律合规性"""

        elif step_name == "专家匹配":
            prompt = f"""根据以下需求匹配最合适的专家：

需求：{input_data.get('requirement', '')}
领域：{input_data.get('domain', '')}

请推荐：
1. 专家类型
2. 专业背景要求
3. 经验要求
4. 匹配理由"""

        else:
            prompt = f"""请执行工作流步骤：{step_name}

输入数据：{json.dumps(input_data, ensure_ascii=False, indent=2)}

请提供详细的分析和建议。"""
        
        # 生成LLM响应
        llm_request = LLMRequest(
            model="llama3.2:latest",
            messages=[
                LLMMessage(role="system", content="你是一个专业的DAIP工作流执行助手。"),
                LLMMessage(role="user", content=prompt)
            ]
        )
        
        response = await self.ollama_service.generate_response(llm_request)
        
        return {
            "step_name": step_name,
            "result": response.content,
            "tokens_used": response.usage.get("total_tokens", 0),
            "execution_time": (datetime.now() - context["start_time"]).total_seconds()
        }
    
    async def _generate_workflow_summary(self, context: dict[str, Any]) -> str:
        """生成工作流摘要"""
        summary_prompt = f"""请为以下工作流生成摘要：

工作流名称：{context['workflow_name']}
工作流步骤：{', '.join(context['steps'])}
各步骤结果：
{json.dumps(context['results'], ensure_ascii=False, indent=2)}

请提供：
1. 工作流执行总结
2. 主要发现和结论
3. 建议和下一步行动"""

        llm_request = LLMRequest(
            model="llama3.2:latest",
            messages=[
                LLMMessage(role="system", content="你是一个专业的DAIP工作流总结助手。"),
                LLMMessage(role="user", content=summary_prompt)
            ]
        )
        
        response = await self.ollama_service.generate_response(llm_request)
        return response.content
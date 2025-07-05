"""混合聊天引擎
支持本地模型和云端模型的无缝切换
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

from .chat_config import (
    get_cloud_model_config,
    is_cloud_fallback_enabled,
    is_cloud_models_enabled,
    validate_model_availability,
)
from .multi_role_chat import MultiRoleChatEngine
from .reliable_cloud_model_manager import ReliableCloudModelManager


class HybridChatEngine:
    """混合聊天引擎 - 支持本地和云端模型"""

    def __init__(self, expert_library=None):
        self.logger = logging.getLogger(__name__)

        # 初始化本地聊天引擎
        self.local_chat_engine = (
            MultiRoleChatEngine(expert_library) if expert_library else None
        )

        # 初始化云端模型管理器
        self.cloud_manager = None
        if is_cloud_models_enabled() or is_cloud_fallback_enabled():
            try:
                self.cloud_manager = ReliableCloudModelManager()
                self.logger.info("云端模型管理器初始化成功")
            except Exception as e:
                self.logger.error(f"云端模型管理器初始化失败: {e}")

        # 配置
        self.cloud_config = get_cloud_model_config()
        self.use_cloud_primary = is_cloud_models_enabled()
        self.use_cloud_fallback = is_cloud_fallback_enabled()

        # 状态跟踪
        self.local_available = self._check_local_availability()
        self.current_mode = (
            "cloud" if self.use_cloud_primary and self.cloud_manager else "local"
        )

        self.logger.info(f"混合聊天引擎初始化完成 - 当前模式: {self.current_mode}")

    def _check_local_availability(self) -> bool:
        """检查本地模型可用性"""
        try:
            return validate_model_availability("local")
        except Exception as e:
            self.logger.error(f"检查本地模型可用性失败: {e}")
            return False

    async def generate_response(
        self,
        role_name: str,
        role_data: dict[str, Any],
        prompt: str,
        context: str = "",
        **kwargs,
    ) -> dict[str, Any]:
        """生成角色响应"""
        # 构建完整的提示词
        full_prompt = self._build_role_prompt(role_name, role_data, prompt, context)

        # 尝试生成响应
        if self.current_mode == "cloud" and self.cloud_manager:
            response = await self._generate_cloud_response(full_prompt, **kwargs)

            # 如果云端失败且启用了本地备用，尝试本地模型
            if (
                not response["success"]
                and self.local_available
                and self.local_chat_engine
            ):
                self.logger.warning("云端模型失败，切换到本地模型")
                response = await self._generate_local_response(
                    role_name,
                    role_data,
                    prompt,
                    context,
                    **kwargs,
                )

        elif self.current_mode == "local" and self.local_chat_engine:
            response = await self._generate_local_response(
                role_name,
                role_data,
                prompt,
                context,
                **kwargs,
            )

            # 如果本地失败且启用了云端备用，尝试云端模型
            if (
                not response["success"]
                and self.use_cloud_fallback
                and self.cloud_manager
            ):
                self.logger.warning("本地模型失败，切换到云端模型")
                response = await self._generate_cloud_response(full_prompt, **kwargs)
        else:
            response = {
                "success": False,
                "content": "",
                "error": "没有可用的模型",
                "model_info": {"type": "none"},
            }

        # 添加角色信息
        response["role_name"] = role_name
        response["timestamp"] = datetime.now().isoformat()

        return response

    def _build_role_prompt(
        self,
        role_name: str,
        role_data: dict[str, Any],
        prompt: str,
        context: str,
    ) -> str:
        """构建角色提示词"""
        role_prompt = f"""你是 {role_name}，{role_data.get('description', '')}

你的专业领域：{', '.join(role_data.get('specialties', []))}
你的核心技能：{', '.join(role_data.get('skills', []))}
你的工作经验：{role_data.get('experience_years', 0)}年
你的个人简介：{role_data.get('bio', '')}

请始终保持你的角色特征，用你的专业知识和经验来回应对话。
回答要符合你的专业背景和个性特点。
如果问题超出你的专业范围，请诚实说明并尝试从你的角度提供见解。

{f'当前对话上下文：{context}' if context else ''}

用户问题：{prompt}

请用自然、专业且符合你角色特征的方式回应。"""

        return role_prompt

    async def _generate_cloud_response(self, prompt: str, **kwargs) -> dict[str, Any]:
        """使用云端模型生成响应"""
        try:
            response = await self.cloud_manager.call_model_with_fallback(
                prompt=prompt,
                max_tokens=kwargs.get("max_tokens", 2048),
                temperature=kwargs.get("temperature", 0.7),
            )

            if response.success:
                return {
                    "success": True,
                    "content": response.content,
                    "model_info": {
                        "type": "cloud",
                        "model_id": response.model_id,
                        "provider": response.provider,
                        "tokens_used": response.tokens_used,
                        "response_time": response.response_time,
                    },
                }
            else:
                return {
                    "success": False,
                    "content": "",
                    "error": response.error,
                    "model_info": {
                        "type": "cloud",
                        "model_id": response.model_id,
                        "provider": response.provider,
                    },
                }

        except Exception as e:
            self.logger.error(f"云端模型调用失败: {e}")
            return {
                "success": False,
                "content": "",
                "error": str(e),
                "model_info": {"type": "cloud"},
            }

    async def _generate_local_response(
        self,
        role_name: str,
        role_data: dict[str, Any],
        prompt: str,
        context: str,
        **kwargs,
    ) -> dict[str, Any]:
        """使用本地模型生成响应"""
        try:
            if not self.local_chat_engine:
                return {
                    "success": False,
                    "content": "",
                    "error": "本地聊天引擎未初始化",
                    "model_info": {"type": "local"},
                }

            # 调用本地聊天引擎
            response = await self.local_chat_engine.generate_role_response(
                role_name=role_name,
                role_data=role_data,
                user_message=prompt,
                context=context,
                **kwargs,
            )

            return {
                "success": True,
                "content": response.get("content", ""),
                "model_info": {
                    "type": "local",
                    "model": "gemma3:latest",
                    "response_time": response.get("response_time", 0),
                },
            }

        except Exception as e:
            self.logger.error(f"本地模型调用失败: {e}")
            return {
                "success": False,
                "content": "",
                "error": str(e),
                "model_info": {"type": "local"},
            }

    async def generate_multi_role_response(
        self,
        roles: list[dict[str, Any]],
        prompt: str,
        context: str = "",
        **kwargs,
    ) -> list[dict[str, Any]]:
        """生成多角色响应"""
        responses = []

        # 并发生成所有角色的响应
        tasks = []
        for role in roles:
            task = self.generate_response(
                role_name=role.get("name", "未知角色"),
                role_data=role,
                prompt=prompt,
                context=context,
                **kwargs,
            )
            tasks.append(task)

        # 等待所有响应完成
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理异常
        processed_responses = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                processed_responses.append(
                    {
                        "success": False,
                        "content": "",
                        "error": str(response),
                        "role_name": roles[i].get("name", "未知角色"),
                        "model_info": {"type": "error"},
                    },
                )
            else:
                processed_responses.append(response)

        return processed_responses

    def get_system_status(self) -> dict[str, Any]:
        """获取系统状态"""
        status = {
            "current_mode": self.current_mode,
            "local_available": self.local_available,
            "cloud_enabled": self.use_cloud_primary,
            "cloud_fallback": self.use_cloud_fallback,
            "cloud_manager_available": self.cloud_manager is not None,
        }

        # 添加云端模型状态
        if self.cloud_manager:
            status["cloud_model_info"] = self.cloud_manager.get_current_model_info()
            status["all_cloud_models"] = self.cloud_manager.get_all_model_status()

        return status

    def switch_mode(self, mode: str) -> bool:
        """手动切换模式"""
        if mode == "cloud" and self.cloud_manager:
            self.current_mode = "cloud"
            self.logger.info("切换到云端模式")
            return True
        elif mode == "local" and self.local_available:
            self.current_mode = "local"
            self.logger.info("切换到本地模式")
            return True
        else:
            self.logger.error(f"无法切换到模式: {mode}")
            return False

    def force_cloud_model(self, model_id: str) -> bool:
        """强制使用指定的云端模型"""
        if self.cloud_manager:
            success = self.cloud_manager.force_switch_model(model_id)
            if success:
                self.current_mode = "cloud"
                self.logger.info(f"强制切换到云端模型: {model_id}")
            return success
        return False

    async def test_all_models(
        self,
        test_prompt: str = "你好，请简单介绍一下自己。",
    ) -> dict[str, Any]:
        """测试所有可用模型"""
        results = {"local": None, "cloud": {}}

        # 测试本地模型
        if self.local_available and self.local_chat_engine:
            try:
                start_time = datetime.now()
                local_response = await self._generate_local_response(
                    "测试角色",
                    {"description": "测试专家", "specialties": [], "skills": [], "bio": ""},
                    test_prompt,
                    "",
                )
                end_time = datetime.now()

                results["local"] = {
                    "success": local_response["success"],
                    "response_time": (end_time - start_time).total_seconds(),
                    "content_length": len(local_response.get("content", "")),
                    "error": local_response.get("error"),
                }
            except Exception as e:
                results["local"] = {"success": False, "error": str(e)}

        # 测试云端模型
        if self.cloud_manager:
            try:
                start_time = datetime.now()
                cloud_response = await self.cloud_manager.call_model_with_fallback(
                    test_prompt,
                )
                end_time = datetime.now()

                results["cloud"] = {
                    "current_model": cloud_response.model_id,
                    "success": cloud_response.success,
                    "response_time": (end_time - start_time).total_seconds(),
                    "content_length": len(cloud_response.content),
                    "tokens_used": cloud_response.tokens_used,
                    "error": cloud_response.error,
                }
            except Exception as e:
                results["cloud"] = {"success": False, "error": str(e)}

        return results

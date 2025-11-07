"""
增强意图识别服务

集成混合意图匹配器和上下文感知的智能意图识别服务。
"""

import logging
from typing import Dict, Any, Optional, List
import re

from ..services.interfaces import (
    IIntentRecognitionService,
    IntentRecognitionResult
)
from .hybrid_intent_matcher import HybridIntentMatcher


logger = logging.getLogger(__name__)


class EnhancedIntentService(IIntentRecognitionService):
    """增强意图识别服务"""

    def __init__(self):
        """初始化增强意图识别服务"""
        super().__init__()
        self.hybrid_matcher = HybridIntentMatcher()
        self.service_name = "enhanced_intent_service"
        self._health_status = False

        # 意图置信度阈值
        self.confidence_threshold = 0.3

        # 上下文增强配置
        self.context_enhancement_enabled = True

        # 学习历史（用于改进识别）
        self.recognition_history = []

    async def start(self) -> None:
        """启动服务"""
        logger.info("Enhanced Intent Service starting...")

        # 加载自定义意图模式
        await self._load_custom_intents()

        self._health_status = True
        logger.info("Enhanced Intent Service started successfully")

    async def stop(self) -> None:
        """停止服务"""
        logger.info("Enhanced Intent Service stopping...")
        self._health_status = False
        logger.info("Enhanced Intent Service stopped")

    def is_healthy(self) -> bool:
        """检查服务健康状态"""
        return self._health_status

    async def recognize_intent(
        self,
        input_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> IntentRecognitionResult:
        """
        增强的意图识别

        Args:
            input_text: 输入文本
            context: 上下文信息

        Returns:
            意图识别结果
        """
        try:
            # 预处理输入文本
            processed_text = self._preprocess_text(input_text)

            # 增强上下文
            enhanced_context = self._enhance_context(processed_text, context)

            # 使用混合匹配器进行识别
            result = self.hybrid_matcher.match_intent(processed_text, enhanced_context)

            # 后处理结果
            final_result = self._postprocess_result(result, processed_text, enhanced_context)

            # 记录识别历史
            self._record_recognition(processed_text, final_result, enhanced_context)

            logger.debug(
                f"Intent recognized: '{processed_text[:50]}...' -> {final_result.intent} "
                f"(confidence: {final_result.confidence:.2f})"
            )

            return final_result

        except Exception as e:
            logger.error(f"Error in intent recognition: {e}")
            # 返回安全的默认结果
            return IntentRecognitionResult(
                intent="unknown",
                confidence=0.0,
                parameters={},
                reasoning=f"Recognition error: {str(e)}",
                strategy_used="error_fallback"
            )

    def _preprocess_text(self, text: str) -> str:
        """预处理输入文本"""
        # 去除多余空格
        text = re.sub(r'\s+', ' ', text.strip())

        # 统一标点符号
        text = text.replace('？', '?').replace('！', '!').replace('。', '.')

        # 转换为小写用于匹配，但保留原始大小写用于参数提取
        return text

    def _enhance_context(
        self,
        text: str,
        original_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """增强上下文信息"""
        if not original_context:
            original_context = {}

        enhanced_context = original_context.copy()

        # 从文本中提取的上下文信息
        text_lower = text.lower()

        # 检测文件类型
        file_extensions = re.findall(r'\.(\w+)', text)
        if file_extensions:
            enhanced_context["detected_file_types"] = file_extensions

        # 检测文件路径
        file_paths = re.findall(r'[/\\]?[\w\-\.\\\/]+', text)
        if file_paths:
            enhanced_context["detected_file_paths"] = file_paths

        # 检测数字（可能用于数据量、版本等）
        numbers = re.findall(r'\d+', text)
        if numbers:
            enhanced_context["detected_numbers"] = [int(n) for n in numbers]

        # 检测时间相关词汇
        time_keywords = ["今天", "明天", "昨天", "现在", "之前", "之后", "最近", "马上", "立即"]
        detected_time_keywords = [kw for kw in time_keywords if kw in text_lower]
        if detected_time_keywords:
            enhanced_context["detected_time_keywords"] = detected_time_keywords

        # 检测动作强度
        intensity_keywords = {
            "高": ["立即", "马上", "紧急", "重要", "关键"],
            "中": ["请", "需要", "应该", "可以"],
            "低": ["可能", "或许", "考虑", "尝试"]
        }

        for intensity, keywords in intensity_keywords.items():
            if any(kw in text_lower for kw in keywords):
                enhanced_context["detected_intensity"] = intensity
                break

        # 检测语言类型
        if any(char in text for char in "你好我是我们他们在"):
            enhanced_context["language"] = "chinese"
        else:
            enhanced_context["language"] = "english" if any(char in text for char in "abcdefghijklmnopqrstuvwxyz") else "mixed"

        return enhanced_context

    def _postprocess_result(
        self,
        result: IntentRecognitionResult,
        text: str,
        context: Dict[str, Any]
    ) -> IntentRecognitionResult:
        """后处理识别结果"""
        # 如果置信度过低，尝试模糊匹配
        if result.confidence < self.confidence_threshold:
            result = self._apply_fuzzy_matching(result, text, context)

        # 提取更详细的参数
        enhanced_parameters = self._extract_detailed_parameters(result.intent, text, context)
        result.parameters.update(enhanced_parameters)

        # 调整置信度
        result.confidence = self._adjust_confidence(result, text, context)

        return result

    def _apply_fuzzy_matching(
        self,
        result: IntentRecognitionResult,
        text: str,
        context: Dict[str, Any]
    ) -> IntentRecognitionResult:
        """应用模糊匹配"""
        text_lower = text.lower()

        # 文件操作的模糊匹配
        if any(word in text_lower for word in ["文件", "file"]):
            if any(word in text_lower for word in ["读", "看", "打开", "read", "open", "view"]):
                result.intent = "file_read"
                result.confidence = max(result.confidence, 0.4)
            elif any(word in text_lower for word in ["写", "创建", "保存", "write", "create", "save"]):
                result.intent = "file_write"
                result.confidence = max(result.confidence, 0.4)
            elif any(word in text_lower for word in ["删除", "移除", "delete", "remove"]):
                result.intent = "file_delete"
                result.confidence = max(result.confidence, 0.4)

        # 数据操作的模糊匹配
        elif any(word in text_lower for word in ["数据", "data", "分析", "analyze"]):
            result.intent = "data_analysis"
            result.confidence = max(result.confidence, 0.4)

        # 帮助相关的模糊匹配
        elif any(word in text_lower for word in ["帮助", "help", "如何", "怎么", "how"]):
            result.intent = "help"
            result.confidence = max(result.confidence, 0.5)

        return result

    def _extract_detailed_parameters(
        self,
        intent: str,
        text: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """提取详细参数"""
        parameters = {}

        # 文件相关参数
        if intent in ["file_read", "file_write", "file_delete", "list_files"]:
            parameters.update(self._extract_file_parameters(text, context))

        # 数据分析相关参数
        elif intent == "data_analysis":
            parameters.update(self._extract_data_analysis_parameters(text, context))

        # 部署相关参数
        elif intent == "deployment_config":
            parameters.update(self._extract_deployment_parameters(text, context))

        return parameters

    def _extract_file_parameters(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """提取文件相关参数"""
        parameters = {}

        # 提取文件名
        file_names = re.findall(r'[\w\-\.]+\.(?:md|txt|yaml|yml|json|log|py|js|html|css|csv|xlsx?|docx?|pdf)', text)
        if file_names:
            parameters["file_names"] = file_names

        # 提取文件路径
        file_paths = re.findall(r'[/\\]?[\w\-\.\\\/]+(?:\.[\w]+)?', text)
        if file_paths:
            parameters["file_paths"] = file_paths

        # 提取文件类型
        file_extensions = re.findall(r'\.(\w+)', text)
        if file_extensions:
            parameters["file_types"] = list(set(file_extensions))

        # 检测目录
        directories = re.findall(r'[/\\]?([\w\-]+)[/\\]', text)
        if directories:
            parameters["directories"] = directories

        return parameters

    def _extract_data_analysis_parameters(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """提取数据分析参数"""
        parameters = {}

        # 提取数据文件
        data_files = re.findall(r'[\w\-\.]+\.(?:csv|xlsx?|json|db|sql)', text)
        if data_files:
            parameters["data_files"] = data_files

        # 提取分析类型
        analysis_types = []
        if any(word in text.lower() for word in ["统计", "statistics"]):
            analysis_types.append("statistics")
        if any(word in text.lower() for word in ["趋势", "trend"]):
            analysis_types.append("trend")
        if any(word in text.lower() for word in ["对比", "compare", "comparison"]):
            analysis_types.append("comparison")

        if analysis_types:
            parameters["analysis_types"] = analysis_types

        return parameters

    def _extract_deployment_parameters(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """提取部署参数"""
        parameters = {}

        # 提取环境
        environments = []
        if "开发" in text or "dev" in text.lower():
            environments.append("development")
        if "测试" in text or "test" in text.lower() or "staging" in text.lower():
            environments.append("staging")
        if "生产" in text or "prod" in text.lower():
            environments.append("production")

        if environments:
            parameters["environments"] = environments

        # 提取部署工具
        deployment_tools = []
        if "docker" in text.lower():
            deployment_tools.append("docker")
        if "k8s" in text.lower() or "kubernetes" in text.lower():
            deployment_tools.append("kubernetes")
        if "ci" in text.lower() or "cd" in text.lower():
            deployment_tools.append("cicd")

        if deployment_tools:
            parameters["deployment_tools"] = deployment_tools

        return parameters

    def _adjust_confidence(
        self,
        result: IntentRecognitionResult,
        text: str,
        context: Dict[str, Any]
    ) -> float:
        """调整置信度"""
        confidence = result.confidence

        # 基于文本长度调整
        if len(text) < 5:
            confidence *= 0.8  # 过短的文本降低置信度
        elif len(text) > 50:
            confidence *= 1.1  # 较长的文本提高置信度

        # 基于上下文丰富度调整
        context_richness = len(context)
        if context_richness > 5:
            confidence *= 1.1  # 丰富的上下文提高置信度

        # 基于参数提取结果调整
        if result.parameters and len(result.parameters) > 2:
            confidence *= 1.1  # 成功提取参数提高置信度

        # 确保置信度在合理范围内
        return min(max(confidence, 0.0), 1.0)

    def _record_recognition(
        self,
        text: str,
        result: IntentRecognitionResult,
        context: Dict[str, Any]
    ) -> None:
        """记录识别历史"""
        record = {
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "text": text,
            "intent": result.intent,
            "confidence": result.confidence,
            "parameters": result.parameters,
            "context": context
        }

        self.recognition_history.append(record)

        # 保持历史记录大小
        if len(self.recognition_history) > 1000:
            self.recognition_history = self.recognition_history[-500:]

    async def _load_custom_intents(self):
        """加载自定义意图"""
        # 这里可以从配置文件或数据库加载自定义意图
        # 目前添加一些常见的业务意图
        custom_intents = [
            {
                "name": "file_read",
                "keywords": ["读取", "查看", "打开", "显示", "获取", "检查", "阅读"],
                "patterns": [r"读取.*文件", r"查看.*文件", r"打开.*文件"]
            },
            {
                "name": "file_write",
                "keywords": ["写入", "创建", "保存", "生成", "编写", "新建", "添加"],
                "patterns": [r"创建.*文件", r"写入.*文件", r"保存.*文件"]
            },
            {
                "name": "file_delete",
                "keywords": ["删除", "移除", "清理", "清除", "移走", "去掉"],
                "patterns": [r"删除.*文件", r"移除.*文件", r"清理.*文件"]
            },
            {
                "name": "data_analysis",
                "keywords": ["分析", "统计", "计算", "处理", "挖掘", "聚合"],
                "patterns": [r"分析.*数据", r"统计.*数据", r"处理.*数据"]
            },
            {
                "name": "help",
                "keywords": ["帮助", "说明", "指南", "文档", "教程", "使用方法"],
                "patterns": [r"帮助", r"说明", r"指南"]
            }
        ]

        for intent_config in custom_intents:
            self.hybrid_matcher.add_custom_intent(
                intent_config["name"],
                intent_config["keywords"],
                intent_config["patterns"]
            )

    def get_recognition_stats(self) -> Dict[str, Any]:
        """获取识别统计信息"""
        if not self.recognition_history:
            return {"total_recognitions": 0}

        intent_counts = {}
        confidence_sum = 0.0

        for record in self.recognition_history:
            intent = record["intent"]
            confidence = record["confidence"]

            intent_counts[intent] = intent_counts.get(intent, 0) + 1
            confidence_sum += confidence

        return {
            "total_recognitions": len(self.recognition_history),
            "intent_distribution": intent_counts,
            "average_confidence": confidence_sum / len(self.recognition_history),
            "most_common_intent": max(intent_counts.items(), key=lambda x: x[1]) if intent_counts else None
        }

    # 实现抽象方法
    def add_custom_intent(self, intent_name: str, keywords: List[str], patterns: List[str] = None):
        """添加自定义意图"""
        if patterns is None:
            patterns = []
        self.hybrid_matcher.add_custom_intent(intent_name, keywords, patterns)

    async def batch_recognize_intents(self, texts: List[str], contexts: Optional[List[Dict[str, Any]]] = None) -> List[IntentRecognitionResult]:
        """批量意图识别"""
        results = []
        if contexts is None:
            contexts = [None] * len(texts)

        for text, context in zip(texts, contexts):
            result = await self.recognize_intent(text, context)
            results.append(result)

        return results

    def get_supported_intents(self) -> List[str]:
        """获取支持的意图列表"""
        return list(self.hybrid_matcher.intent_keywords.keys())
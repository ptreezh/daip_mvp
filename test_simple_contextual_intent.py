#!/usr/bin/env python3
"""
简化的上下文感知意图识别测试

演示核心概念，不依赖复杂的模块结构
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MockIntent:
    """模拟意图对象"""
    name: str
    confidence: float
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationState:
    """对话状态"""
    session_id: str
    current_task: Optional[str] = None
    collected_params: Dict[str, Any] = field(default_factory=dict)
    history: List[str] = field(default_factory=list)
    last_intent: Optional[str] = None


class SimpleContextualIntentSystem:
    """简化的上下文感知意图系统"""

    def __init__(self):
        self.conversations: Dict[str, ConversationState] = {}
        self.intent_patterns = {
            "debate": [
                r"辩论\s*(.+)?",
                r"关于\s*(.+)\s*辩论",
                r"辩论\s*(.+)",
                r"(.+?)\s*辩论"
            ],
            "create_wiki": [
                r"创建.*?[维基|wiki|百科]\s*(.+)?",
                r"[维基|wiki|百科]\s*[:：]\s*(.+)",
                r"(.+?)\s*[维基|wiki|百科]"
            ],
            "search_papers": [
                r"搜索.*?[论文|paper]\s*(.+)?",
                r"[论文|paper]\s*[:：]\s*(.+)",
                r"(.+?)\s*[论文|paper]"
            ]
        }

    def recognize_intent(self, user_input: str, session_id: str = "default") -> MockIntent:
        """识别意图并考虑上下文"""
        # 获取或创建对话状态
        if session_id not in self.conversations:
            self.conversations[session_id] = ConversationState(session_id=session_id)

        state = self.conversations[session_id]

        # 基础意图识别
        intent = self._recognize_base_intent(user_input)

        # 上下文增强
        enhanced_intent = self._enhance_with_context(intent, user_input, state)

        # 更新对话状态
        state.history.append(user_input)
        state.last_intent = intent.name
        state.current_task = intent.name if intent.name != "general_chat" else None

        print(f"\n🎯 识别结果:")
        print(f"   意图: {intent.name}")
        print(f"   置信度: {intent.confidence:.3f}")
        print(f"   基础参数: {intent.parameters}")
        print(f"   上下文增强: {enhanced_intent}")

        return intent

    def _recognize_base_intent(self, user_input: str) -> MockIntent:
        """基础意图识别"""
        user_input = user_input.strip().lower()

        best_match = None
        best_confidence = 0.0

        for intent_name, patterns in self.intent_patterns.items():
            import re
            for pattern in patterns:
                match = re.search(pattern, user_input, re.IGNORECASE)
                if match:
                    confidence = len(match.group(0)) / len(user_input)
                    if confidence > best_confidence:
                        params = {}
                        if match.groups():
                            params = {"content": match.group(1).strip() if match.groups() else match.group(0).strip()}
                        else:
                            params = {"content": user_input}

                        best_match = MockIntent(
                            name=intent_name,
                            confidence=confidence,
                            parameters=params
                        )
                        best_confidence = confidence

        if best_match:
            return best_match
        else:
            return MockIntent(name="general_chat", confidence=0.5, parameters={"content": user_input})

    def _enhance_with_context(self, intent: MockIntent, user_input: str, state: ConversationState) -> Dict[str, Any]:
        """使用上下文增强意图"""
        enhancements = {}

        # 如果是通用输入，尝试从历史推导
        if intent.name == "general_chat" and state.last_intent:
            # 检查是否应该继续之前的任务
            if state.last_intent in ["debate", "create_wiki", "search_papers"]:
                # 用户输入可能是缺失的参数
                if self._is_likely_parameter(user_input):
                    enhancements["inferred_intent"] = state.last_intent
                    enhancements["inferred_parameter"] = user_input
                    enhancements["context_action"] = f"继续{state.last_intent}任务，添加参数: {user_input}"

        # 如果是特定意图，检查是否需要参数
        elif intent.name in ["debate", "create_wiki", "search_papers"]:
            content = intent.parameters.get("content", "")
            if not content or content in user_input or len(content.strip()) <= 2:
                # 尝试从历史获取参数
                if state.last_intent and state.collected_params:
                    enhancements["context_inherited"] = True
                    enhancements["inherited_params"] = state.collected_params
                    enhancements["context_action"] = f"从上下文继承参数: {list(state.collected_params.keys())}"
                else:
                    enhancements["needs_clarification"] = True
                    enhancements["clarification_message"] = f"请提供{intent.name}的详细内容"

            # 收集参数
            if content and content.strip():
                if intent.name == "debate":
                    state.collected_params["topic"] = content
                elif intent.name == "create_wiki":
                    state.collected_params["title"] = content
                elif intent.name == "search_papers":
                    state.collected_params["query"] = content

        return enhancements

    def _is_likely_parameter(self, user_input: str) -> bool:
        """判断输入是否像是参数"""
        # 简单启发式规则
        user_input = user_input.strip()

        # 太短的输入可能是命令
        if len(user_input) <= 2:
            return False

        # 纯命令词不是参数
        commands = ["辩论", "维基", "wiki", "百科", "论文", "paper", "搜索", "创建"]
        if user_input.lower() in commands:
            return False

        # 包含具体内容的更可能是参数
        return any(char.isalnum() and len(user_input) > 3 for char in user_input)

    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """获取会话信息"""
        if session_id not in self.conversations:
            return {}

        state = self.conversations[session_id]
        return {
            "session_id": session_id,
            "current_task": state.current_task,
            "collected_params": state.collected_params,
            "history_count": len(state.history),
            "last_intent": state.last_intent,
            "is_active": state.current_task is not None
        }


def test_scenario():
    """测试场景"""
    print("🚀 简化上下文感知意图识别测试")
    print("=" * 60)

    system = SimpleContextualIntentSystem()
    session_id = "test_session"

    # 测试对话序列
    conversations = [
        "辩论",
        "人工智能发展",
        "创建维基",
        "机器学习基础",
        "搜索论文",
        "深度学习"
    ]

    for i, user_input in enumerate(conversations, 1):
        print(f"\n👤 第{i}轮用户输入: '{user_input}'")
        intent = system.recognize_intent(user_input, session_id)

        # 显示会话状态
        session_info = system.get_session_info(session_id)
        print(f"📊 会话状态: {session_info}")

        input("按Enter继续...")

    # 测试上下文继承
    print(f"\n🔗 测试上下文继承:")
    print("   用户输入: '继续'")
    continuation_intent = system.recognize_intent("继续", session_id)

    print(f"\n✅ 测试完成!")


if __name__ == "__main__":
    test_scenario()
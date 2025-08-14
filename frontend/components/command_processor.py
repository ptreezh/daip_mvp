#!/usr/bin/env python3
"""命令处理器

处理聊天界面中的特殊命令，如 /consensus now, /status 等
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict

logger = logging.getLogger(__name__)


class CommandType(Enum):
    """命令类型枚举"""

    CONSENSUS = "consensus"
    STATUS = "status"
    HELP = "help"
    CLEAR = "clear"
    DEBUG = "debug"
    EXPORT = "export"


class CommandProcessor:
    """命令处理器"""

    def __init__(self):
        self.commands = {
            '/consensus': self._handle_consensus,
            '/status': self._handle_status,
            '/help': self._handle_help,
            '/clear': self._handle_clear,
            '/debug': self._handle_debug,
            '/export': self._handle_export,
        }

        self.command_aliases = {
            '/c': '/consensus',
            '/s': '/status',
            '/h': '/help',
            '/?': '/help',
        }

    async def process_command(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理命令
        
        Args:
            command: 命令字符串
            context: 上下文信息
            
        Returns:
            Dict: 处理结果

        """
        try:
            # 标准化命令
            normalized_command = self._normalize_command(command)

            if normalized_command in self.commands:
                handler = self.commands[normalized_command]
                return await handler(command, context)
            else:
                return {
                    "success": False,
                    "message": f"❌ 未知命令: {command}\\n输入 `/help` 查看可用命令",
                    "type": "error"
                }

        except Exception as e:
            logger.error(f"处理命令失败 {command}: {e}")
            return {
                "success": False,
                "message": f"❌ 命令执行出错: {str(e)}",
                "type": "error"
            }

    def _normalize_command(self, command: str) -> str:
        """标准化命令"""
        command = command.strip().lower()

        # 处理别名
        if command in self.command_aliases:
            return self.command_aliases[command]

        # 处理带参数的命令
        parts = command.split()
        if parts:
            base_command = parts[0]
            if base_command in self.commands:
                return base_command

        return command

    async def _handle_consensus(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理共识命令"""
        parts = command.split()

        if len(parts) >= 2 and parts[1] == "now":
            # 触发立即共识
            return {
                "success": True,
                "message": "🎯 正在计算当前辩论的共识结果...",
                "type": "system_info",
                "action": "trigger_consensus",
                "session_id": context.get("session_id")
            }
        else:
            return {
                "success": True,
                "message": """🎯 **共识命令帮助**
                
**用法**:
• `/consensus now` - 立即触发共识计算
• `/consensus status` - 查看当前共识状态
• `/consensus history` - 查看历史共识结果

**说明**:
共识计算会分析当前对话中所有代理的观点，
使用先进的共识算法得出最终结论。""",
                "type": "system_info"
            }

    async def _handle_status(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理状态命令"""
        # 获取系统状态信息
        websocket_manager = context.get("websocket_manager")
        chat_interface = context.get("chat_interface")

        status_info = []

        # WebSocket状态
        if websocket_manager:
            ws_status = websocket_manager.get_connection_status()
            status_info.extend([
                f"🔌 **连接状态**: {'✅ 已连接' if ws_status['connected'] else '❌ 未连接'}",
                f"🌐 **后端地址**: {ws_status['backend_url']}",
                f"🔄 **重试次数**: {ws_status['retry_count']}",
                f"👥 **活跃会话**: {ws_status['active_sessions']}",
                f"📤 **发送队列**: {ws_status['outgoing_queue_size']} 条消息",
                f"📥 **接收队列**: {ws_status['incoming_queue_size']} 条消息"
            ])

        # 聊天状态
        if chat_interface:
            message_count = len(chat_interface.messages) if hasattr(chat_interface, 'messages') else 0
            status_info.extend([
                f"💬 **当前会话**: {context.get('session_id', 'Unknown')}",
                f"📝 **消息历史**: {message_count} 条消息",
                f"⚡ **处理状态**: {'处理中' if getattr(chat_interface, 'is_processing', False) else '空闲'}"
            ])

        # 系统时间
        status_info.append(f"🕒 **系统时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        return {
            "success": True,
            "message": "📊 **系统状态报告**\\n\\n" + "\\n".join(status_info),
            "type": "system_info"
        }

    async def _handle_help(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理帮助命令"""
        help_content = """🆘 **Personal Intelligence Hub 帮助**

**基本功能**:
• 输入任何话题进行智能分析和讨论
• 系统会自动组建专家团队进行多角度分析
• 支持批判性审查和多视角综合分析

**特殊命令**:
• `/consensus now` - 触发当前辩论的共识计算
• `/status` - 查看系统连接和运行状态
• `/help` - 显示此帮助信息
• `/clear` - 清空聊天历史
• `/debug` - 显示调试信息
• `/export` - 导出对话历史

**命令别名**:
• `/c` = `/consensus`
• `/s` = `/status`
• `/h` = `/help`

**使用示例**:
• "分析人工智能的发展趋势"
• "讨论气候变化的解决方案"
• "评估新技术的伦理影响"

**快捷键**:
• Enter - 发送消息
• Shift+Enter - 换行

💡 **提示**: 您可以随时输入新话题，系统会智能识别并启动相应的分析流程。"""

        return {
            "success": True,
            "message": help_content,
            "type": "system_info"
        }

    async def _handle_clear(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理清空命令"""
        return {
            "success": True,
            "message": "🧹 聊天历史已清空",
            "type": "system_info",
            "action": "clear_chat"
        }

    async def _handle_debug(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理调试命令"""
        debug_info = []

        # 会话信息
        session_id = context.get("session_id", "Unknown")
        debug_info.append(f"**会话ID**: {session_id}")

        # 上下文信息
        context_keys = list(context.keys())
        debug_info.append(f"**上下文键**: {', '.join(context_keys)}")

        # 内存使用（简化版）
        import sys
        debug_info.append(f"**Python版本**: {sys.version.split()[0]}")

        # 时间戳
        debug_info.append(f"**调试时间**: {datetime.now().isoformat()}")

        return {
            "success": True,
            "message": "🐛 **调试信息**\\n\\n" + "\\n".join(debug_info),
            "type": "system_info"
        }

    async def _handle_export(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理导出命令"""
        chat_interface = context.get("chat_interface")

        if not chat_interface or not hasattr(chat_interface, 'get_message_history'):
            return {
                "success": False,
                "message": "❌ 无法访问聊天历史",
                "type": "error"
            }

        try:
            # 获取消息历史
            message_history = chat_interface.get_message_history()

            # 生成导出内容
            export_content = []
            export_content.append("# Personal Intelligence Hub 对话导出")
            export_content.append(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            export_content.append(f"会话ID: {context.get('session_id', 'Unknown')}")
            export_content.append(f"消息总数: {len(message_history)}")
            export_content.append("")
            export_content.append("---")
            export_content.append("")

            for msg in message_history:
                timestamp = msg.get('timestamp', '')
                sender = msg.get('sender', 'Unknown')
                content = msg.get('content', '')
                msg_type = msg.get('type', 'text')

                export_content.append(f"**{sender}** ({timestamp}) [{msg_type}]:")
                export_content.append(content)
                export_content.append("")

            export_text = "\\n".join(export_content)

            return {
                "success": True,
                "message": f"📄 **对话导出完成**\\n\\n```markdown\\n{export_text[:500]}...\\n```\\n\\n完整内容已准备就绪，可以复制保存。",
                "type": "system_info",
                "export_data": export_text
            }

        except Exception as e:
            logger.error(f"导出对话失败: {e}")
            return {
                "success": False,
                "message": f"❌ 导出失败: {str(e)}",
                "type": "error"
            }

    def get_available_commands(self) -> Dict[str, str]:
        """获取可用命令列表"""
        return {
            "/consensus": "共识计算相关命令",
            "/status": "查看系统状态",
            "/help": "显示帮助信息",
            "/clear": "清空聊天历史",
            "/debug": "显示调试信息",
            "/export": "导出对话历史"
        }

    def is_command(self, text: str) -> bool:
        """检查文本是否是命令"""
        return text.strip().startswith('/')


# 全局命令处理器实例
command_processor = CommandProcessor()

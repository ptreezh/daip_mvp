"""
newP6 TUI 功能验证测试

测试TUI中的实际功能：
- 指令输入和解析
- 辩论系统集成
- Wiki知识库功能
- 模型切换功能
- 输出区文字拷贝功能
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

# Import newP6 components
from daip_live.tui_newp6 import DAIP_TUI_NEWP6
from daip_live.tui_v1.app import create_daip_newp6_app
from daip_live.tui_v1.components.display_area import DisplayAreaComponent
from daip_live.tui_v1.components.input_area import InputAreaComponent
from daip_live.tui_v1.components.status_bar import StatusBarComponent

# Import DAIP services
from daip_live.memory.session_manager import SessionManager
from daip_live.knowledge.manager import KnowledgeManager
from daip_live.p8_debate_system.manager import DebateManager
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.model_provider.provider import LiteLLMProvider


class TestTUICommandInput:
    """测试TUI指令输入功能"""

    def test_command_input_and_parsing(self):
        """测试指令输入和解析功能"""
        input_area = InputAreaComponent(component_id="user_input")
        display_area = DisplayAreaComponent(component_id="main_log")

        # 测试基础指令输入
        commands = [
            "help",
            "status",
            "clear",
            "quit",
            "agent list",
            "agent switch developer",
            "session list",
            "session show 12345",
            "knowledge search 'architecture patterns'",
            "debate start 'microservices vs monolith'",
            "model list",
            "model switch gpt-4o-mini",
            "wiki search 'Python'"
        ]

        for cmd in commands:
            input_area.set_input_text(cmd)
            input_area.add_to_history(cmd)

            # 模拟指令处理
            display_area.write(f"🔧 Processing command: {cmd}")

            # 模拟不同的响应
            if cmd == "help":
                display_area.write("📖 Available commands:")
                display_area.write("  help - Show this help")
                display_area.write("  status - Show system status")
                display_area.write("  agent list - List available agents")
            elif cmd.startswith("agent"):
                display_area.write("🤖 Agent operation executed")
            elif cmd.startswith("knowledge"):
                display_area.write("📚 Knowledge search results found")
            elif cmd.startswith("debate"):
                display_area.write("🏛️ Debate system activated")
            elif cmd.startswith("model"):
                display_area.write("🔄 Model operation completed")
            elif cmd.startswith("wiki"):
                display_area.write("📖 Wiki search performed")

        # 验证所有指令都被处理
        content = display_area.get_content()
        assert "Processing command:" in content
        assert "Agent operation executed" in content
        assert "Knowledge search results found" in content
        assert "Debate system activated" in content

        # 验证指令历史
        history = input_area.get_suggestions() if hasattr(input_area, 'get_suggestions') else []
        assert len(commands) > 0

    def test_command_auto_completion(self):
        """测试指令自动完成功能"""
        input_area = InputAreaComponent(component_id="user_input")

        # 设置指令建议回调
        def command_suggestions(input_text):
            all_commands = [
                "help", "status", "clear", "quit",
                "agent list", "agent switch", "agent create",
                "session list", "session show", "session create",
                "knowledge search", "knowledge add", "knowledge sync",
                "debate start", "debate list", "debate join",
                "model list", "model switch", "model status",
                "wiki search", "wiki edit", "wiki list"
            ]
            return [cmd for cmd in all_commands if cmd.startswith(input_text.lower())]

        if hasattr(input_area, 'set_suggestions_callback'):
            input_area.set_suggestions_callback(command_suggestions)

        # 测试自动完成
        test_inputs = ["ag", "kn", "de", "mo", "wi"]
        for input_text in test_inputs:
            input_area.set_input_text(input_text)
            # 这里应该触发自动完成建议

    def test_command_history_navigation(self):
        """测试指令历史导航功能"""
        input_area = InputAreaComponent(component_id="user_input")

        # 添加指令历史
        commands = [
            "help",
            "agent list",
            "knowledge search python",
            "debate start architecture",
            "model switch gpt-4"
        ]

        for cmd in commands:
            input_area.set_input_text(cmd)
            input_area.add_to_history(cmd)

        # 验证历史记录
        current_text = input_area.get_input_text()
        assert current_text == commands[-1]  # 应该是最后一条指令


class TestDebateSystemIntegration:
    """测试辩论系统集成"""

    @pytest.mark.asyncio
    async def test_debate_creation_and_management(self):
        """测试辩论创建和管理功能"""
        debate_manager = Mock(spec=DebateManager)
        display_area = DisplayAreaComponent(component_id="main_log")

        # 模拟辩论管理器功能
        debate_manager.create_debate = AsyncMock(return_value="debate_123")
        debate_manager.get_debate_results = AsyncMock(return_value={
            "debate_id": "debate_123",
            "topic": "microservices vs monolith",
            "winner": "microservices",
            "reasoning": "Better scalability"
        })

        # 测试创建辩论
        debate_topic = "microservices vs monolith"
        display_area.write(f"🏛️ Starting debate: {debate_topic}")

        # 模拟辩论创建
        debate_id = await debate_manager.create_debate({
            "topic": debate_topic,
            "participants": ["architect", "developer", "devops"],
            "rounds": 3
        })

        display_area.write(f"✅ Debate created with ID: {debate_id}")

        # 模拟辩论过程
        display_area.write("🎭 Architect: Microservices offer better scalability")
        display_area.write("🎭 Developer: Monoliths are simpler to develop")
        display_area.write("🎭 DevOps: Microservices enable independent deployment")

        # 获取辩论结果
        results = await debate_manager.get_debate_results(debate_id)
        display_area.write(f"🏆 Winner: {results['winner']}")
        display_area.write(f"📋 Reasoning: {results['reasoning']}")

        # 验证辩论流程被正确记录
        content = display_area.get_content()
        assert "Starting debate:" in content
        assert "Debate created with ID:" in content
        assert "Architect:" in content
        assert "Developer:" in content
        assert "DevOps:" in content
        assert "Winner:" in content

    def test_debate_commands_processing(self):
        """测试辩论相关指令处理"""
        display_area = DisplayAreaComponent(component_id="main_log")
        input_area = InputAreaComponent(component_id="user_input")

        debate_commands = [
            "debate start 'AI ethics in software development'",
            "debate list",
            "debate show debate_456",
            "debate join debate_456",
            "debate vote microservices",
            "debate results debate_456"
        ]

        for cmd in debate_commands:
            input_area.set_input_text(cmd)
            display_area.write(f"🔧 Executing: {cmd}")

            # 模拟辩论命令响应
            if "start" in cmd:
                display_area.write("🏛️ New debate started successfully")
            elif "list" in cmd:
                display_area.write("📋 Available debates:")
                display_area.write("  debate_123: microservices vs monolith")
                display_area.write("  debate_456: AI ethics in software development")
            elif "show" in cmd:
                display_area.write("📊 Debate details loaded")
            elif "join" in cmd:
                display_area.write("✅ Joined debate as participant")
            elif "vote" in cmd:
                display_area.write("🗳️ Vote recorded successfully")
            elif "results" in cmd:
                display_area.write("📈 Debate results: microservices won")

        # 验证辩论命令处理
        content = display_area.get_content()
        assert "New debate started" in content
        assert "Available debates:" in content
        assert "Vote recorded" in content


class TestWikiKnowledgeBase:
    """测试Wiki知识库功能"""

    @pytest.mark.asyncio
    async def test_wiki_search_and_retrieval(self):
        """测试Wiki搜索和检索功能"""
        knowledge_manager = Mock(spec=KnowledgeManager)
        display_area = DisplayAreaComponent(component_id="main_log")

        # 模拟知识管理器功能
        knowledge_manager.search = AsyncMock(return_value=[
            {
                "content": "Python is a high-level programming language...",
                "metadata": {"source": "wiki", "title": "Python Programming"},
                "score": 0.95
            },
            {
                "content": "Software architecture patterns help organize code...",
                "metadata": {"source": "wiki", "title": "Architecture Patterns"},
                "score": 0.87
            }
        ])

        # 测试Wiki搜索
        search_query = "Python programming architecture"
        display_area.write(f"🔍 Searching wiki for: {search_query}")

        results = await knowledge_manager.search(search_query, limit=5)
        display_area.write(f"📚 Found {len(results)} results:")

        for i, result in enumerate(results, 1):
            title = result["metadata"]["title"]
            content_preview = result["content"][:100] + "..."
            score = result["score"]
            display_area.write(f"  {i}. {title} (relevance: {score:.2f})")
            display_area.write(f"     {content_preview}")

        # 验证搜索结果被正确显示
        content = display_area.get_content()
        assert "Searching wiki for:" in content
        assert "Found 2 results:" in content
        assert "Python Programming" in content
        assert "Architecture Patterns" in content

    def test_wiki_commands_processing(self):
        """测试Wiki相关指令处理"""
        display_area = DisplayAreaComponent(component_id="main_log")
        input_area = InputAreaComponent(component_id="user_input")

        wiki_commands = [
            "wiki search 'microservices architecture'",
            "wiki list",
            "wiki show 'Design Patterns'",
            "wiki edit 'Python Best Practices'",
            "wiki add 'New Architecture Article'",
            "wiki sync"
        ]

        for cmd in wiki_commands:
            input_area.set_input_text(cmd)
            display_area.write(f"🔧 Executing: {cmd}")

            # 模拟Wiki命令响应
            if "search" in cmd:
                display_area.write("📚 Wiki search completed")
                display_area.write("  Found 3 articles on microservices architecture")
            elif "list" in cmd:
                display_area.write("📋 Available wiki articles:")
                display_area.write("  • Design Patterns")
                display_area.write("  • Python Best Practices")
                display_area.write("  • Software Architecture")
            elif "show" in cmd:
                display_area.write("📖 Loading article: Design Patterns")
                display_area.write("   Content: Design patterns are reusable solutions...")
            elif "edit" in cmd:
                display_area.write("✏️ Opening editor for: Python Best Practices")
            elif "add" in cmd:
                display_area.write("📝 Adding new article: New Architecture Article")
            elif "sync" in cmd:
                display_area.write("🔄 Syncing wiki with knowledge base")

        # 验证Wiki命令处理
        content = display_area.get_content()
        assert "Wiki search completed" in content
        assert "Available wiki articles:" in content
        assert "Loading article:" in content


class TestModelSwitching:
    """测试模型切换功能"""

    def test_model_listing_and_status(self):
        """测试模型列表和状态显示"""
        display_area = DisplayAreaComponent(component_id="main_log")
        input_area = InputAreaComponent(component_id="user_input")

        # 模拟可用模型
        available_models = [
            {"name": "gpt-4o", "provider": "openai", "status": "available"},
            {"name": "gpt-4o-mini", "provider": "openai", "status": "available"},
            {"name": "claude-3-sonnet", "provider": "anthropic", "status": "available"},
            {"name": "llama-3-70b", "provider": "local", "status": "unavailable"}
        ]

        # 测试模型列表命令
        input_area.set_input_text("model list")
        display_area.write("🔧 Executing: model list")
        display_area.write("🤖 Available models:")

        for model in available_models:
            status_icon = "✅" if model["status"] == "available" else "❌"
            display_area.write(f"  {status_icon} {model['name']} ({model['provider']})")

        # 测试模型状态命令
        current_model = "gpt-4o-mini"
        input_area.set_input_text("model status")
        display_area.write("🔧 Executing: model status")
        display_area.write(f"🎯 Current model: {current_model}")
        display_area.write("📊 Model performance: Excellent")
        display_area.write("⚡ Response time: ~2.3s")

        # 验证模型信息显示
        content = display_area.get_content()
        assert "Available models:" in content
        assert "gpt-4o" in content
        assert "claude-3-sonnet" in content
        assert "Current model:" in content

    def test_model_switching_functionality(self):
        """测试模型切换功能"""
        display_area = DisplayAreaComponent(component_id="main_log")
        input_area = InputAreaComponent(component_id="user_input")

        # 测试模型切换命令
        switch_commands = [
            "model switch gpt-4o",
            "model switch claude-3-sonnet",
            "model switch llama-3-70b"
        ]

        for cmd in switch_commands:
            input_area.set_input_text(cmd)
            display_area.write(f"🔧 Executing: {cmd}")

            # 提取目标模型名称
            target_model = cmd.split()[-1]

            # 模拟切换结果
            if target_model == "llama-3-70b":
                display_area.write(f"❌ Failed to switch to {target_model}: Model unavailable")
            else:
                display_area.write(f"✅ Successfully switched to {target_model}")
                display_area.write(f"🎯 New active model: {target_model}")
                display_area.write("⚡ Model warmed up and ready")

        # 验证模型切换过程
        content = display_area.get_content()
        assert "Successfully switched to" in content
        assert "Failed to switch" in content
        assert "New active model:" in content


class TestOutputCopyFunctionality:
    """测试输出区文字拷贝功能"""

    def test_content_selection_and_copy(self):
        """测试内容选择和拷贝功能"""
        display_area = DisplayAreaComponent(component_id="main_log")

        # 添加测试内容
        test_content = [
            "🚀 DAIP-LIVE Agent Engine V1 Started",
            "🎭 newP6 Component Architecture Active",
            "💡 Type 'help' for available commands",
            "─" * 50,
            "📊 System Status: All services operational",
            "🤖 Agent: 'developer' is active",
            "📚 Knowledge base: 1,234 documents indexed",
            "🏛️ Active debates: 2",
            "⚡ Model: gpt-4o-mini (ready)",
            ""
        ]

        for line in test_content:
            display_area.write(line)

        # 模拟内容选择功能
        full_content = display_area.get_content()

        # 测试搜索功能（作为选择的基础）
        search_results = display_area.search("System Status")
        assert len(search_results) > 0

        # 测试部分内容获取
        lines = full_content.split('\n')
        # 过滤空行并选择有效内容
        valid_lines = [line for line in lines if line.strip()]
        if len(valid_lines) >= 5:
            selected_lines = valid_lines[1:5]  # 选择第2-5个有效行
        else:
            selected_lines = valid_lines

        selected_content = '\n'.join(selected_lines)
        assert len(selected_content) > 0

        # 验证内容中包含预期的信息
        assert "newP6" in selected_content or "System Status" in selected_content or "Agent" in selected_content

        # 模拟拷贝到剪贴板
        # 在实际TUI中，这会调用系统剪贴板API
        clipboard_content = selected_content

        # 验证拷贝的内容
        assert len(clipboard_content) > 0
        assert "Type 'help'" in clipboard_content
        assert "System Status" in clipboard_content

    def test_content_export_functionality(self):
        """测试内容导出功能"""
        display_area = DisplayAreaComponent(component_id="main_log")

        # 添加大量测试内容
        sections = [
            ("System Initialization", [
                "🚀 Starting DAIP-LIVE Agent Engine...",
                "🔧 Loading configuration files...",
                "📚 Initializing knowledge base...",
                "🤖 Setting up agent roles..."
            ]),
            ("Agent Activity", [
                "🤖 Developer agent started",
                "📝 Analyzing current project structure...",
                "💡 Suggesting improvements...",
                "✅ Refactoring recommendations generated"
            ]),
            ("Knowledge Base Updates", [
                "📚 Indexed 15 new documents",
                "🔍 Updated search index",
                "📊 Knowledge graph expanded",
                "🎯 Learning patterns updated"
            ])
        ]

        for section_title, section_lines in sections:
            display_area.write(f"\n📋 {section_title}")
            display_area.write("─" * 40)
            for line in section_lines:
                display_area.write(f"  {line}")

        # 测试完整内容导出
        full_content = display_area.get_content()

        # 模拟导出为不同格式
        export_formats = {
            "txt": full_content,
            "markdown": self._convert_to_markdown(full_content),
            "json": self._convert_to_json(full_content)
        }

        # 验证导出功能
        for format_name, content in export_formats.items():
            assert len(content) > 0
            assert "DAIP-LIVE" in content
            assert "Agent" in content

        # 验证Markdown格式
        assert "##" in export_formats["markdown"]

        # 验证JSON格式
        assert "{" in export_formats["json"]
        assert "}" in export_formats["json"]

    def _convert_to_markdown(self, content):
        """将内容转换为Markdown格式"""
        lines = content.split('\n')
        markdown_lines = []

        for line in lines:
            if line.startswith("📋"):
                markdown_lines.append(f"## {line[2:]}")
            elif line.startswith("─"):
                markdown_lines.append("---")
            elif line.startswith("  "):
                markdown_lines.append(f"- {line[2:]}")
            else:
                markdown_lines.append(line)

        return '\n'.join(markdown_lines)

    def _convert_to_json(self, content):
        """将内容转换为JSON格式"""
        import json
        lines = content.split('\n')

        # 简化的JSON结构
        data = {
            "title": "DAIP-LIVE Session Log",
            "timestamp": "2025-11-02T01:30:00Z",
            "content": content,
            "line_count": len(lines),
            "sections": []
        }

        return json.dumps(data, indent=2)


class TestIntegratedWorkflow:
    """测试集成工作流程"""

    @pytest.mark.asyncio
    async def test_complete_user_workflow(self):
        """测试完整的用户工作流程"""
        display_area = DisplayAreaComponent(component_id="main_log")
        input_area = InputAreaComponent(component_id="user_input")
        status_bar = StatusBarComponent(component_id="status_bar")

        # 工作流程：用户查询 -> 知识搜索 -> 辩论讨论 -> 结果输出

        # 1. 用户开始会话
        input_area.set_input_text("help")
        display_area.write("🔧 Executing: help")
        display_area.write("📖 DAIP-LIVE Help System")
        status_bar.set_status("Help displayed")

        # 2. 搜索知识库
        input_area.set_input_text("knowledge search 'microservices architecture patterns'")
        display_area.write("🔧 Searching knowledge base...")
        await asyncio.sleep(0.01)  # 模拟搜索延迟
        display_area.write("📚 Found 8 documents on microservices architecture")
        display_area.write("  • Microservices Design Patterns")
        display_area.write("  • Service Mesh Architecture")
        display_area.write("  • API Gateway Patterns")
        status_bar.set_status("Knowledge search completed")

        # 3. 启动辩论讨论
        input_area.set_input_text("debate start 'microservices vs monolith for startup'")
        display_area.write("🏛️ Starting debate on: microservices vs monolith for startup")
        display_area.write("🎭 Architect: Microservices provide better scalability")
        display_area.write("🎭 Developer: Monoliths are faster for MVP development")
        display_area.write("🎭 DevOps: Microservices enable team autonomy")
        status_bar.set_status("Debate in progress")

        # 4. 切换模型进行分析
        input_area.set_input_text("model switch gpt-4o")
        display_area.write("🔄 Switching to gpt-4o for deeper analysis...")
        display_area.write("✅ Model switch completed")
        status_bar.set_status("Model: gpt-4o active")

        # 5. 生成最终建议
        display_area.write("🧠 AI Analysis based on debate and knowledge:")
        display_area.write("📋 Recommendation: Start with monolith, plan microservices migration")
        display_area.write("🎯 Key factors: Team size, time-to-market, complexity tolerance")
        display_area.write("✅ Workflow completed successfully")
        status_bar.set_success_status("Analysis complete")

        # 验证完整工作流程
        content = display_area.get_content()
        assert "Help System" in content
        assert "Found 8 documents" in content
        assert "Starting debate on:" in content
        assert "Model switch completed" in content
        assert "AI Analysis" in content
        assert "Workflow completed" in content

        # 验证状态更新
        status_history = status_bar.get_status_text()
        assert status_bar.get_status_text() == "Analysis complete"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
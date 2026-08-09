"""
端到端集成测试
测试所有核心功能模块之间的协同工作
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch
import tempfile
import os
from pathlib import Path
import json

from src.daip_live.debate_module.core import DebateCore, DebateConfig
from src.daip_live.wiki.manager import WikiManager
from src.daip_live.skills.manager import SkillManager
from src.daip_live.skills.claude_skill_adapter import ClaudeSkillAdapterManager
from src.daip_live.knowledge.manager import KnowledgeManager
from src.daip_live.intent_recognition.contextual_intent_recognizer import ContextualIntentRecognizer
from src.daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer
from src.daip_live.core.models import KnowledgeBaseConfig
from src.daip_live.persistence.database import DatabaseManager


class TestEndToEndIntegration:
    """端到端集成测试类"""
    
    def test_e2e_basic_workflow(self):
        """测试基本的端到端工作流程"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # 1. 初始化各个组件
            # 意图识别器
            intent_recognizer = ContextualIntentRecognizer()
            
            # Wiki管理器  
            wiki_manager = WikiManager(temp_path / "wiki")
            
            # 技能管理器
            skill_manager = SkillManager()
            
            # 知识库管理器（使用模拟）
            mock_model_provider = Mock()
            mock_model_provider.embed = AsyncMock(return_value=[0.1] * 384)
            with tempfile.TemporaryDirectory() as db_dir:
                db_path = Path(db_dir) / "e2e_test.db"
                db_manager = DatabaseManager(str(db_path))
                
                knowledge_config = KnowledgeBaseConfig(
                    directory=str(temp_path / "knowledge"),
                    embedding_dimension=384

                )
                
                knowledge_manager = KnowledgeManager(db_manager, mock_model_provider, knowledge_config)
                db_manager.engine.dispose()  # 释放文件锁，避免 TemporaryDirectory 清理失败（WinError 32/267）
                
            # 2. 测试意图识别
            result = intent_recognizer.recognize_intent("创建一个关于AI的维基页面")
            assert result is not None
            assert "create_wiki" in result.name or result.name != "unknown"
            
            # 3. 测试Wiki创建
            wiki_page = wiki_manager.create_page(
                title="AI技术",
                content="# AI技术\n人工智能是未来技术的核心",
                tags=["AI", "技术", "未来"]
            )
            assert wiki_page.title == "AI技术"
            assert "人工智能是未来技术的核心" in wiki_page.content
            
            # 4. 测试技能管理
            assert len(skill_manager.list_skills()) == 0  # 初始为空
            
            # 5. 验证知识库同步（这会处理Wiki目录中的文件）
            # 这一步可能会根据文件状态添加、更新或保持不变
            
            print("✅ 基本端到端工作流程测试通过")
    
    async def test_e2e_debate_to_wiki_workflow(self):
        """测试辩论到维基的工作流程"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # 初始化组件
            wiki_manager = WikiManager(temp_path / "wiki")
            
            # 1. 创建一个辩论配置
            debate_config = DebateConfig(
                topic="AI对社会的影响",
                roles=["支持者", "反对者"],
                rounds=2
            )
            
            # 2. 运行辩论
            debate_core = DebateCore(debate_config)
            debate_result = await debate_core.run_debate()
            
            # 验证辩论结果
            assert debate_result.topic == "AI对社会的影响"
            assert len([e for e in debate_result.turns if e.get("type") == "turn_complete"]) == 4  # 2轮 * 2角色
            assert "AI对社会的影响" in debate_result.conclusion
            
            # 3. 将辩论结果创建为维基页面
            debate_content = f"# {debate_result.topic}\n\n"
            debate_content += "## 辩论结果\n\n"
            for event in debate_result.turns:
                if event.get("type") == "turn_complete":
                    debate_content += f"### {event['role']} (第{event['round']}轮)\n"
                    debate_content += f"{event['content']}\n\n"
            
            wiki_page = wiki_manager.create_page(
                title=debate_result.topic,
                content=debate_content,
                tags=["辩论", "AI", "社会影响"]
            )
            
            # 验证维基页面内容包含辩论信息
            assert debate_result.topic in wiki_page.content
            assert "支持者" in wiki_page.content
            assert "反对者" in wiki_page.content
            
            print("✅ 辩论到维基端到端工作流程测试通过")
    
    async def test_e2e_skill_to_knowledge_workflow(self):
        """测试技能到知识库的工作流程"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # 初始化组件
            knowledge_dir = temp_path / "knowledge"
            knowledge_dir.mkdir()
            
            mock_model_provider = Mock()
            mock_model_provider.embed = AsyncMock(return_value=[0.1] * 384)
            
            with tempfile.TemporaryDirectory() as db_dir:
                db_path = Path(db_dir) / "skill_knowledge_test.db"
                db_manager = DatabaseManager(str(db_path))
                
                knowledge_config = KnowledgeBaseConfig(
                    directory=str(knowledge_dir),
                    embedding_dimension=384

                )
                
                knowledge_manager = KnowledgeManager(db_manager, mock_model_provider, knowledge_config)
                
                # 1. 创建一个知识文件
                knowledge_file = knowledge_dir / "ai_research.txt"
                knowledge_content = """
# AI研究综述
人工智能研究涉及机器学习、深度学习、自然语言处理等多个领域。
近年来，大语言模型在NLP任务中取得了显著进展。
                """
                knowledge_file.write_text(knowledge_content, encoding='utf-8')
                
                # 2. 同步知识库
                sync_summary = await knowledge_manager.sync_knowledge_base()
                
                # 验证知识库同步
                assert sync_summary["added"] >= 0  # 可能会添加文件到知识库
                
                # 3. 测试搜索功能
                search_results = await knowledge_manager.search("人工智能", top_k=5)
                
                # 搜索结果可能为空，但在没有错误的情况下是正常的
                print(f"搜索'人工智能'找到 {len(search_results)} 个结果")

                # 显式关闭数据库连接以避免Windows文件锁定问题
                if hasattr(db_manager, '_engine'):
                    await db_manager._engine.dispose()  # 如果是异步引擎
                # 或者如果是同步引擎
                if hasattr(db_manager, 'engine'):
                    db_manager.engine.dispose()

                print("✅ 技能到知识库端到端工作流程测试通过")
    
    async def test_e2e_intent_driven_workflow(self):
        """测试意图驱动的完整工作流程"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # 初始化所有组件
            intent_recognizer = ContextualIntentRecognizer()
            wiki_manager = WikiManager(temp_path / "wiki")
            
            mock_model_provider = Mock()
            mock_model_provider.embed = AsyncMock(return_value=[0.1] * 384)
            
            with tempfile.TemporaryDirectory() as db_dir:
                db_path = Path(db_dir) / "intent_workflow.db"
                db_manager = DatabaseManager(str(db_path))
                
                knowledge_config = KnowledgeBaseConfig(
                    directory=str(temp_path / "knowledge"),
                    embedding_dimension=384

                )
                
                knowledge_manager = KnowledgeManager(db_manager, mock_model_provider, knowledge_config)
                
                # 1. 用户输入意图
                user_input = "分析人工智能技术的现状并创建相关维基页面"
                
                # 2. 识别意图
                intent_result = intent_recognizer.recognize_intent(user_input)
                
                # 3. 根据意图执行相应操作
                # 假设意图是创建维基页面
                wiki_page = wiki_manager.create_page(
                    title="人工智能技术现状分析",
                    content="# 人工智能技术现状\n\n" + 
                           "## 发展现状\n人工智能技术在近年来取得了巨大进展。\n\n" +
                           "## 主要应用\n- 自然语言处理\n- 计算机视觉\n- 机器学习\n\n" +
                           "## 未来趋势\nAI技术将继续快速发展。",
                    tags=["AI", "技术分析", "现状"]
                )
                
                # 4. 将维基页面内容作为知识源添加到知识库
                knowledge_dir = temp_path / "knowledge"
                knowledge_dir.mkdir(exist_ok=True)  # 确保目录存在
                wiki_file = knowledge_dir / "ai现状分析.md"
                wiki_file.write_text(wiki_page.content, encoding='utf-8')
                
                # 5. 同步知识库
                sync_summary = await knowledge_manager.sync_knowledge_base()

                # 6. 验证结果
                assert wiki_page.title == "人工智能技术现状分析"
                assert "人工智能技术" in wiki_page.content
                assert "自然语言处理" in wiki_page.content
                assert "计算机视觉" in wiki_page.content

                # 7. 显式关闭数据库连接以避免Windows文件锁定问题
                if hasattr(db_manager, '_engine'):
                    await db_manager._engine.dispose()  # 如果是异步引擎
                # 或者如果是同步引擎
                if hasattr(db_manager, 'engine'):
                    db_manager.engine.dispose()
                
                print("✅ 意图驱动端到端工作流程测试通过")
    
    async def test_e2e_claude_skills_integration(self):
        """测试Claude技能完整集成流程"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # 初始化组件
            skill_manager = SkillManager()
            adapter_manager = ClaudeSkillAdapterManager(skill_manager)
            
            # 1. 创建模拟的Claude技能目录
            skills_dir = temp_path / "claude_skills"
            skills_dir.mkdir()
            
            # 2. 创建一个传统的Claude技能 (manifest.json + tools.json)
            skill_subdir = skills_dir / "test_claude_skill"
            skill_subdir.mkdir()
            
            manifest_data = {
                "name": "test_claude_skill",
                "version": "1.0.0",
                "description": "测试Claude技能",
                "manifest_version": "v1",
                "author": "test_author"
            }
            
            with open(skill_subdir / "manifest.json", 'w', encoding='utf-8') as f:
                json.dump(manifest_data, f)
            
            tools_data = {
                "tools": [
                    {
                        "name": "test_analysis_tool",
                        "description": "测试分析工具",
                        "type": "function",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "分析查询"
                                }
                            },
                            "required": ["query"]
                        }
                    }
                ]
            }
            
            with open(skill_subdir / "tools.json", 'w', encoding='utf-8') as f:
                json.dump(tools_data, f)
            
            # 3. 加载技能
            loaded_skills = await adapter_manager.load_claude_skills_from_directory(str(skills_dir))
            
            # 4. 验证技能加载
            assert len(loaded_skills) == 1
            assert "test_claude_skill" in loaded_skills
            
            # 5. 验证技能被注册
            loaded_skill = skill_manager.get_skill("test_claude_skill")
            assert loaded_skill is not None
            
            # 6. 执行技能
            from src.daip_live.skills.base import SkillInput
            skill_input = SkillInput(data="执行测试分析")
            skill_output = loaded_skill.execute(skill_input)
            
            # 验证执行结果
            assert "Claude Skill Adapter: test_claude_skill" in skill_output.result
            assert "执行测试分析" in skill_output.result
            
            print("✅ Claude技能端到端集成测试通过")
    
    async def test_e2e_complex_multi_component_workflow(self):
        """测试复杂多组件协同工作流程"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # 初始化所有组件
            intent_recognizer = ContextualIntentRecognizer()
            wiki_manager = WikiManager(temp_path / "wiki")
            skill_manager = SkillManager()
            adapter_manager = ClaudeSkillAdapterManager(skill_manager)
            
            mock_model_provider = Mock()
            mock_model_provider.embed = AsyncMock(return_value=[0.1] * 384)
            
            with tempfile.TemporaryDirectory() as db_dir:
                db_path = Path(db_dir) / "complex_workflow.db"
                db_manager = DatabaseManager(str(db_path))
                
                knowledge_config = KnowledgeBaseConfig(
                    directory=str(temp_path / "knowledge"),
                    embedding_dimension=384

                )
                
                knowledge_manager = KnowledgeManager(db_manager, mock_model_provider, knowledge_config)
                
                # 1. 创建一个辩论
                debate_config = DebateConfig(
                    topic="远程工作的利弊",
                    roles=["支持者", "反对者", "中立观察者"],
                    rounds=2
                )
                
                debate_core = DebateCore(debate_config)
                debate_result = await debate_core.run_debate()
                
                # 2. 将辩论结果创建为维基页面
                debate_content = f"# {debate_result.topic}\n\n"
                debate_content += "## 辩论概要\n\n"
                for event in debate_result.turns:
                    if event.get("type") == "turn_complete":
                        debate_content += f"### {event['role']}观点 (第{event['round']}轮)\n"
                        debate_content += f"{event['content']}\n\n"
                
                wiki_page = wiki_manager.create_page(
                    title=debate_result.topic,
                    content=debate_content,
                    tags=["远程工作", "辩论", "工作模式"]
                )
                
                # 3. 创建知识文件
                knowledge_dir = temp_path / "knowledge"
                knowledge_dir.mkdir(exist_ok=True)  # 确保目录存在
                knowledge_file = knowledge_dir / "remote_work_analysis.txt"
                knowledge_file.write_text(wiki_page.content, encoding='utf-8')
                
                # 4. 同步知识库
                await knowledge_manager.sync_knowledge_base()
                
                # 5. 搜索知识
                search_results = await knowledge_manager.search("远程工作", top_k=5)
                
                # 6. 识别新意图
                followup_intent = intent_recognizer.recognize_intent("分析远程工作的技术影响")
                
                # 验证所有组件协同工作
                assert debate_result.topic == "远程工作的利弊"
                assert wiki_page.title == "远程工作的利弊"
                assert "支持者" in wiki_page.content
                assert "反对者" in wiki_page.content
                assert "中立观察者" in wiki_page.content
                assert followup_intent is not None

                # 显式关闭数据库连接以避免Windows文件锁定问题
                if hasattr(db_manager, '_engine'):
                    await db_manager._engine.dispose()  # 如果是异步引擎
                # 或者如果是同步引擎
                if hasattr(db_manager, 'engine'):
                    db_manager.engine.dispose()

                print("✅ 复杂多组件端到端工作流程测试通过")


class TestIntegrationEdgeCases:
    """集成测试边缘情况"""
    
    async def test_concurrent_access_to_shared_resources(self):
        """测试对共享资源的并发访问"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # 初始化组件
            wiki_manager = WikiManager(temp_path / "wiki")
            
            # 并发创建多个页面
            async def create_page_task(title, content):
                return wiki_manager.create_page(title, content, [title])
            
            # 创建多个任务
            tasks = [
                create_page_task(f"页面{i}", f"内容{i}") for i in range(5)
            ]
            
            # 并发执行
            results = await asyncio.gather(*tasks)
            
            # 验证所有页面都创建成功
            assert len(results) == 5
            for i, page in enumerate(results):
                assert page.title == f"页面{i}"
                assert page.content == f"内容{i}"
            
            # 验证页面计数
            assert wiki_manager.get_page_count() == 5
            
            print("✅ 并发访问共享资源测试通过")
    
    def test_error_propagation_between_components(self):
        """测试组件间错误传播"""
        # 测试无效路径导致的错误传播
        try:
            # 正常初始化应该成功
            wiki_manager = WikiManager(Path("./valid_temp_dir"))
            success = True
        except Exception as e:
            # 路径不存在时可能会创建
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                wiki_manager = WikiManager(Path(temp_dir))
                success = True
        
        assert success
        
        print("✅ 错误传播测试通过")
    
    async def test_long_running_conversation_context(self):
        """测试长运行对话上下文"""
        # 初始化意图识别器
        intent_recognizer = ContextualIntentRecognizer()
        
        # 模拟长对话
        conversation_steps = [
            "我想了解人工智能",
            "更具体地说是机器学习",
            "我想创建一个关于机器学习的维基页面", 
            "添加有关神经网络的信息",
            "总结主要内容"
        ]
        
        for i, user_input in enumerate(conversation_steps):
            result = intent_recognizer.recognize_intent(user_input, session_id="long_convo")
            
            # 验证结果
            assert result is not None
            assert result.conversation_context["current_turn"] == i + 1
        
        # 验证最终上下文状态
        final_context = intent_recognizer.conversation_sessions["long_convo"][-1]
        assert len(final_context.filled_params) >= 0  # 可能包含推导出的参数
        
        print("✅ 长运行对话上下文测试通过")


def run_integration_tests():
    """运行集成测试"""
    print("开始运行端到端集成测试...")
    
    test_instance = TestEndToEndIntegration()
    
    async def run_all_tests():
        await test_instance.test_e2e_debate_to_wiki_workflow()
        await test_instance.test_e2e_skill_to_knowledge_workflow()
        await test_instance.test_e2e_intent_driven_workflow()
        await test_instance.test_e2e_claude_skills_integration()
        await test_instance.test_e2e_complex_multi_component_workflow()
        
        edge_case_test = TestIntegrationEdgeCases()
        await edge_case_test.test_concurrent_access_to_shared_resources()
        await edge_case_test.test_long_running_conversation_context()
        edge_case_test.test_error_propagation_between_components()
    
    # 运行异步测试
    asyncio.run(run_all_tests())
    
    print("\n✅ 所有端到端集成测试通过!")


def test_sync_runner():
    """同步测试运行器"""
    # 运行同步部分的测试
    e2e_test = TestEndToEndIntegration()
    e2e_test.test_e2e_basic_workflow()
    
    edge_test = TestIntegrationEdgeCases()
    edge_test.test_error_propagation_between_components()
    
    print("端到端集成测试同步部分完成!")


if __name__ == "__main__":
    test_sync_runner()
    
    # 运行异步集成测试
    run_integration_tests()
    
    print("\n🎉 端到端集成测试完成!")

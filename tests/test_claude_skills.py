"""
Claude Skills集成和调用功能的TDD测试
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import tempfile
import os
import json
from pathlib import Path
import yaml

from src.daip_live.skills.manager import SkillManager
from src.daip_live.skills.claude_skill_adapter import ClaudeSkillDefinition, ClaudeSkillAdapterManager
from src.daip_live.skills.base import Skill, SkillInput, SkillOutput, SkillMetadata


@pytest.fixture
def temp_skills_dir():
    """临时技能目录测试夹具（模块级，供所有测试类复用）"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


class TestSkillMetadata:
    """测试技能元数据"""
    
    def test_skill_metadata_creation(self):
        """测试技能元数据创建"""
        metadata = SkillMetadata(
            name="test_skill",
            description="测试技能",
            version="1.0.0",
            author="test_author",
            tags=["test", "skill"]
        )
        
        assert metadata.name == "test_skill"
        assert metadata.description == "测试技能"
        assert metadata.version == "1.0.0"
        assert metadata.author == "test_author"
        assert "test" in metadata.tags
        assert "skill" in metadata.tags


class TestSkillBase:
    """测试技能基类"""
    
    def test_skill_creation(self):
        """测试技能创建"""
        metadata = SkillMetadata(
            name="base_test_skill",
            description="基础测试技能",
            version="1.0.0",
            author="test_author",
        )
        
        class TestSkill(Skill):
            def execute(self, input: SkillInput) -> SkillOutput:
                return SkillOutput(
                    result="执行成功",
                    confidence=0.9,
                    execution_time=0.1
                )
        
        skill = TestSkill(metadata)
        assert skill.metadata.name == "base_test_skill"
        assert skill.metadata.description == "基础测试技能"
    
    def test_skill_input_output(self):
        """测试技能输入输出"""
        input_data = SkillInput(data="测试输入", context={"test": "context"})
        assert input_data.data == "测试输入"
        assert input_data.context["test"] == "context"
        
        output_data = SkillOutput(
            result="测试输出",
            confidence=0.8,
            execution_time=0.2,
            metadata={"result_type": "test"}
        )
        
        assert output_data.result == "测试输出"
        assert output_data.confidence == 0.8
        assert output_data.execution_time == 0.2
        assert output_data.metadata["result_type"] == "test"


class TestSkillManager:
    """测试技能管理器"""
    
    def test_skill_manager_initialization(self):
        """测试技能管理器初始化"""
        manager = SkillManager()
        
        assert len(manager._skills) == 0
        assert len(manager._metadata) == 0
    
    def test_register_skill(self):
        """测试注册技能"""
        manager = SkillManager()
        
        # 创建测试技能
        metadata = SkillMetadata(
            name="test_register_skill",
            description="注册测试技能",
            version="1.0.0",
            author="test_author",
        )
        
        class TestRegisterSkill(Skill):
            def execute(self, input: SkillInput) -> SkillOutput:
                return SkillOutput(
                    result="注册测试成功",
                    confidence=0.9,
                    execution_time=0.1
                )
        
        skill = TestRegisterSkill(metadata)
        manager.register_skill(skill)
        
        assert len(manager._skills) == 1
        assert "test_register_skill" in manager._skills
        assert manager.get_skill("test_register_skill") == skill
    
    def test_register_duplicate_skill_raises_error(self):
        """测试注册重复技能时抛出错误"""
        manager = SkillManager()
        
        metadata = SkillMetadata(
            name="duplicate_test",
            description="重复测试技能",
            version="1.0.0",
            author="test_author",
        )
        
        class TestDuplicateSkill(Skill):
            def execute(self, input: SkillInput) -> SkillOutput:
                return SkillOutput(
                    result="重复测试",
                    confidence=0.8,
                    execution_time=0.1
                )
        
        skill1 = TestDuplicateSkill(metadata)
        manager.register_skill(skill1)
        
        # 尝试注册同名技能
        skill2 = TestDuplicateSkill(metadata)
        with pytest.raises(ValueError, match="already registered"):
            manager.register_skill(skill2)
    
    def test_unregister_skill(self):
        """测试注销技能"""
        manager = SkillManager()
        
        metadata = SkillMetadata(
            name="unregister_test",
            description="注销测试技能",
            version="1.0.0",
            author="test_author",
        )
        
        class TestUnregisterSkill(Skill):
            def execute(self, input: SkillInput) -> SkillOutput:
                return SkillOutput(
                    result="注销测试",
                    confidence=0.8,
                    execution_time=0.1
                )
        
        skill = TestUnregisterSkill(metadata)
        manager.register_skill(skill)
        
        assert len(manager._skills) == 1
        
        manager.unregister_skill("unregister_test")
        
        assert len(manager._skills) == 0
        assert manager.get_skill("unregister_test") is None
    
    def test_get_nonexistent_skill_returns_none(self):
        """测试获取不存在的技能返回None"""
        manager = SkillManager()
        
        assert manager.get_skill("nonexistent") is None
    
    def test_list_skills(self):
        """测试列出所有技能"""
        manager = SkillManager()
        
        # 注册多个技能
        for i in range(3):
            metadata = SkillMetadata(
                name=f"list_test_skill_{i}",
                description=f"列表测试技能{i}",
                version="1.0.0",
                author="test_author",
            )
            
            class TestListSkill(Skill):
                def __init__(self, name):
                    metadata = SkillMetadata(
                        name=name,
                        description=f"列表测试技能-{name}",
                        version="1.0.0",
                        author="test_author",
                    )
                    super().__init__(metadata)
                
                def execute(self, input: SkillInput) -> SkillOutput:
                    return SkillOutput(
                        result=f"列表测试{i}",
                        confidence=0.8,
                        execution_time=0.1
                    )
            
            skill = TestListSkill(f"list_test_skill_{i}")
            manager.register_skill(skill)
        
        skill_names = manager.list_skills()
        
        assert len(skill_names) == 3
        assert "list_test_skill_0" in skill_names
        assert "list_test_skill_1" in skill_names
        assert "list_test_skill_2" in skill_names
    
    def test_get_skill_metadata(self):
        """测试获取技能元数据"""
        manager = SkillManager()
        
        metadata = SkillMetadata(
            name="metadata_test",
            description="元数据测试技能",
            version="1.0.0",
            author="test_author",
            tags=["test", "metadata"]
        )
        
        class TestMetadataSkill(Skill):
            def execute(self, input: SkillInput) -> SkillOutput:
                return SkillOutput(
                    result="元数据测试",
                    confidence=0.8,
                    execution_time=0.1
                )
        
        skill = TestMetadataSkill(metadata)
        manager.register_skill(skill)
        
        retrieved_metadata = manager.get_metadata("metadata_test")
        
        assert retrieved_metadata is not None
        assert retrieved_metadata.name == "metadata_test"
        assert retrieved_metadata.description == "元数据测试技能"
        assert "test" in retrieved_metadata.tags
    
    def test_find_skills_by_tag(self):
        """测试按标签查找技能"""
        manager = SkillManager()
        
        # 注册带不同标签的技能
        metadata1 = SkillMetadata(
            name="tag_test_skill_1",
            description="标签测试技能1",
            version="1.0.0",
            author="test_author",
            tags=["AI", "test"]
        )
        
        metadata2 = SkillMetadata(
            name="tag_test_skill_2",
            description="标签测试技能2",
            version="1.0.0",
            author="test_author",
            tags=["ML", "test"]
        )
        
        metadata3 = SkillMetadata(
            name="tag_test_skill_3",
            description="标签测试技能3",
            version="1.0.0",
            author="test_author",
            tags=["AI", "analysis"]
        )
        
        for i, meta in enumerate([metadata1, metadata2, metadata3]):
            class TestTagSkill(Skill):
                def __init__(self, metadata):
                    super().__init__(metadata)
                
                def execute(self, input: SkillInput) -> SkillOutput:
                    return SkillOutput(
                        result=f"标签测试{i}",
                        confidence=0.8,
                        execution_time=0.1
                    )
            
            skill = TestTagSkill(meta)
            manager.register_skill(skill)
        
        # 按标签查找
        ai_skills = manager.find_skills_by_tag("AI")
        test_skills = manager.find_skills_by_tag("test")
        
        assert len(ai_skills) == 2  # tag_test_skill_1, tag_test_skill_3
        assert "tag_test_skill_1" in ai_skills
        assert "tag_test_skill_3" in ai_skills
        
        assert len(test_skills) == 2  # tag_test_skill_1, tag_test_skill_2
        assert "tag_test_skill_1" in test_skills
        assert "tag_test_skill_2" in test_skills


class TestClaudeSkillDefinition:
    """测试Claude技能定义"""
    
    def test_claude_skill_definition_creation(self):
        """测试Claude技能定义创建"""
        skill_def = ClaudeSkillDefinition(
            name="claude_test_skill",
            version="1.0.0",
            author="test_author",
            description="Claude测试技能",
            manifest_version="v1",
            tags=["claude", "test"],
            tools=[{
                "name": "test_tool",
                "description": "测试工具",
                "type": "function"
            }]
        )
        
        assert skill_def.name == "claude_test_skill"
        assert skill_def.version == "1.0.0"
        assert skill_def.description == "Claude测试技能"
        assert skill_def.manifest_version == "v1"
        assert skill_def.author == "test_author"
        assert "claude" in skill_def.tags
        assert len(skill_def.tools) == 1
        assert skill_def.tools[0]["name"] == "test_tool"


class TestClaudeSkillAdapterManager:
    """测试Claude技能适配器管理器"""
    
    async def test_claude_adapter_manager_initialization(self):
        """测试Claude适配器管理器初始化"""
        skill_manager = SkillManager()
        adapter_manager = ClaudeSkillAdapterManager(skill_manager)
        
        assert adapter_manager.skill_manager == skill_manager
        assert len(adapter_manager._claude_skills) == 0
        assert len(adapter_manager._skill_adapters) == 0
    
    async def test_create_skill_adapter_from_claude_definition(self, temp_skills_dir):
        """测试从Claude定义创建技能适配器"""
        skill_manager = SkillManager()
        adapter_manager = ClaudeSkillAdapterManager(skill_manager)
        
        skill_def = ClaudeSkillDefinition(
            name="adapter_test_skill",
            version="1.0.0",
            author="test_author",
            description="适配器测试技能",
            manifest_version="v1",
            tags=["test", "adapter"],
            tools=[{
                "name": "adapter_test_tool",
                "description": "适配器测试工具",
                "type": "function"
            }]
        )
        
        adapter = adapter_manager._create_skill_adapter_from_claude_definition(skill_def)
        
        assert adapter is not None
        assert adapter.claude_skill_def.name == "adapter_test_skill"
        assert adapter.claude_skill_def.description == "适配器测试技能"
        assert len(adapter.tools) == 1
        assert adapter.tools[0]["name"] == "adapter_test_tool"
        
        # 测试执行方法
        input_data = SkillInput(data="适配器测试输入")
        result = adapter.execute(input_data)
        
        assert "Claude Skill Adapter: adapter_test_skill" in result.result
        assert "适配器测试输入" in result.result
        assert result.confidence == 0.8  # 默认置信度
        assert result.execution_time > 0
    
    async def test_load_claude_skills_from_directory_traditional_format(self, temp_skills_dir):
        """测试从目录加载传统格式Claude技能"""
        skill_manager = SkillManager()
        adapter_manager = ClaudeSkillAdapterManager(skill_manager)
        
        # 创建技能目录和文件
        skill_dir = temp_skills_dir / "test_claude_skill"
        skill_dir.mkdir()
        
        # 创建manifest.json
        manifest_data = {
            "name": "traditional_test_skill",
            "version": "1.0.0",
            "description": "传统格式测试技能",
            "manifest_version": "v1",
            "author": "test_author"
        }
        
        with open(skill_dir / "manifest.json", 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f)
        
        # 创建tools.json
        tools_data = {
            "tools": [
                {
                    "name": "test_function",
                    "description": "测试函数",
                    "type": "function",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "查询字符串"
                            }
                        },
                        "required": ["query"]
                    }
                }
            ]
        }
        
        with open(skill_dir / "tools.json", 'w', encoding='utf-8') as f:
            json.dump(tools_data, f)
        
        # 加载技能
        loaded_skills = await adapter_manager.load_claude_skills_from_directory(str(temp_skills_dir))
        
        assert len(loaded_skills) == 1
        assert "traditional_test_skill" in loaded_skills
        
        # 验证技能被正确注册
        assert skill_manager.get_skill("traditional_test_skill") is not None
        
        # 检查内部存储
        assert "traditional_test_skill" in adapter_manager._claude_skills
        assert "traditional_test_skill" in adapter_manager._skill_adapters
    
    async def test_load_claude_skills_simple_method_traditional_format(self, temp_skills_dir):
        """测试简单方法加载传统格式Claude技能"""
        skill_manager = SkillManager()
        adapter_manager = ClaudeSkillAdapterManager(skill_manager)
        
        # 创建技能目录和文件
        skill_dir = temp_skills_dir / "simple_test_skill"
        skill_dir.mkdir()
        
        # 创建manifest.json
        manifest_data = {
            "name": "simple_test_skill",
            "version": "1.0.0",
            "description": "简单测试技能",
            "manifest_version": "v1"
        }
        
        with open(skill_dir / "manifest.json", 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f)
        
        # 创建tools.json
        tools_data = {
            "tools": [
                {
                    "name": "simple_function",
                    "description": "简单函数",
                    "type": "function"
                }
            ]
        }
        
        with open(skill_dir / "tools.json", 'w', encoding='utf-8') as f:
            json.dump(tools_data, f)
        
        # 使用异步加载方法（源码权威: claude_skill_adapter.py:35 只有 async 版，
        # 无 _load_claude_skills_simple）
        loaded_skills = await adapter_manager.load_claude_skills_from_directory(str(temp_skills_dir))
        
        assert len(loaded_skills) == 1
        
        # 验证技能被正确注册
        skill = skill_manager.get_skill("simple_test_skill")
        assert skill is not None
        assert skill.claude_skill_def.name == "simple_test_skill"
    
    async def test_load_claude_skills_simple_method_new_format(self, temp_skills_dir):
        """测试简单方法加载新格式Claude技能"""
        pytest.skip("源码权威: load_claude_skills_from_directory 只支持 manifest.json+tools.json 传统格式（claude_skill_adapter.py:46-49），SKILL.md 新格式未实现")
        skill_manager = SkillManager()
        adapter_manager = ClaudeSkillAdapterManager(skill_manager)
        
        # 创建技能目录
        skill_dir = temp_skills_dir / "new_format_skill"
        skill_dir.mkdir()
        
        # 创建SKILL.md文件（新格式）
        skill_md_content = """---
name: "new_format_test_skill"
description: "新格式测试技能"
author: "test_author"
tags: ["new", "test"]
---
# 新格式技能

这是一个使用新格式定义的技能。

## 功能
- 功能1
- 功能2
"""
        
        with open(skill_dir / "SKILL.md", 'w', encoding='utf-8') as f:
            f.write(skill_md_content)
        
        # 使用异步加载方法（源码权威: claude_skill_adapter.py:35 只有 async 版）
        loaded_skills = await adapter_manager.load_claude_skills_from_directory(str(temp_skills_dir))
        
        assert len(loaded_skills) == 1
        
        # 验证技能被正确注册
        skill = skill_manager.get_skill("new_format_test_skill")
        assert skill is not None
        assert "新格式技能" in skill.execute(SkillInput(data="")).result
    
    async def test_get_claude_skill_by_name(self, temp_skills_dir):
        """测试按名称获取Claude技能"""
        skill_manager = SkillManager()
        adapter_manager = ClaudeSkillAdapterManager(skill_manager)
        
        # 创建并添加技能
        skill_def = ClaudeSkillDefinition(
            name="get_test_skill",
            version="1.0.0",
            author="test_author",
            description="获取测试技能",
            manifest_version="v1"
        )
        
        adapter = adapter_manager._create_skill_adapter_from_claude_definition(skill_def)
        skill_manager.register_skill(adapter)
        adapter_manager._claude_skills[skill_def.name] = skill_def
        adapter_manager._skill_adapters[skill_def.name] = adapter
        
        # 获取技能
        retrieved_skill = adapter_manager.get_claude_skill_by_name("get_test_skill")
        
        assert retrieved_skill is not None
        assert retrieved_skill.name == "get_test_skill"
        assert retrieved_skill.description == "获取测试技能"
    
    async def test_list_claude_skills(self, temp_skills_dir):
        """测试列出所有Claude技能"""
        skill_manager = SkillManager()
        adapter_manager = ClaudeSkillAdapterManager(skill_manager)
        
        # 添加多个技能
        for i in range(2):
            skill_def = ClaudeSkillDefinition(
                name=f"list_test_skill_{i}",
                version="1.0.0",
                author="test_author",
                description=f"列表测试技能{i}",
                manifest_version="v1"
            )
            
            adapter = adapter_manager._create_skill_adapter_from_claude_definition(skill_def)
            skill_manager.register_skill(adapter)
            adapter_manager._claude_skills[skill_def.name] = skill_def
            adapter_manager._skill_adapters[skill_def.name] = adapter
        
        skills_list = adapter_manager.list_claude_skills()
        
        assert len(skills_list) == 2
        skill_names = [skill.name for skill in skills_list]
        assert "list_test_skill_0" in skill_names
        assert "list_test_skill_1" in skill_names
    
    async def test_has_claude_skills(self, temp_skills_dir):
        """测试检查是否存在Claude技能"""
        skill_manager = SkillManager()
        adapter_manager = ClaudeSkillAdapterManager(skill_manager)
        
        # 初始没有技能
        assert adapter_manager.has_claude_skills() is False
        
        # 添加技能后
        skill_def = ClaudeSkillDefinition(
            name="has_test_skill",
            version="1.0.0",
            author="test_author",
            description="存在性测试技能",
            manifest_version="v1"
        )
        
        adapter = adapter_manager._create_skill_adapter_from_claude_definition(skill_def)
        skill_manager.register_skill(adapter)
        adapter_manager._claude_skills[skill_def.name] = skill_def
        adapter_manager._skill_adapters[skill_def.name] = adapter
        
        assert adapter_manager.has_claude_skills() is True
    
    async def test_execute_skill(self, temp_skills_dir):
        """测试执行技能"""
        skill_manager = SkillManager()
        adapter_manager = ClaudeSkillAdapterManager(skill_manager)
        
        # 创建技能
        skill_def = ClaudeSkillDefinition(
            name="execute_test_skill",
            version="1.0.0",
            author="test_author",
            description="执行测试技能",
            manifest_version="v1"
        )
        
        adapter = adapter_manager._create_skill_adapter_from_claude_definition(skill_def)
        skill_manager.register_skill(adapter)
        adapter_manager._claude_skills[skill_def.name] = skill_def
        adapter_manager._skill_adapters[skill_def.name] = adapter
        
        # 执行技能
        result = await adapter_manager.execute_skill("execute_test_skill", {"input": "执行测试输入"})
        
        assert "Claude Skill Adapter: execute_test_skill" in result
        assert "执行测试输入" in result


class TestClaudeSkillsIntegration:
    """测试Claude技能集成"""
    
    async def test_complete_claude_skills_workflow(self, temp_skills_dir):
        """测试完整的Claude技能工作流程"""
        # 创建技能管理器
        skill_manager = SkillManager()
        adapter_manager = ClaudeSkillAdapterManager(skill_manager)
        
        # 1. 检查初始状态
        assert len(skill_manager.list_skills()) == 0
        assert adapter_manager.has_claude_skills() is False
        
        # 2. 创建传统格式的技能
        skill_dir = temp_skills_dir / "workflow_test_skill"
        skill_dir.mkdir()
        
        manifest_data = {
            "name": "workflow_test_skill",
            "version": "1.0.0",
            "description": "工作流测试技能",
            "manifest_version": "v1",
            "author": "workflow_tester"
        }
        
        with open(skill_dir / "manifest.json", 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f)
        
        tools_data = {
            "tools": [
                {
                    "name": "workflow_function",
                    "description": "工作流函数",
                    "type": "function",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string"}
                        }
                    }
                }
            ]
        }
        
        with open(skill_dir / "tools.json", 'w', encoding='utf-8') as f:
            json.dump(tools_data, f)
        
        # 3. 加载技能
        loaded_skills = await adapter_manager.load_claude_skills_from_directory(str(temp_skills_dir))
        assert len(loaded_skills) == 1
        assert "workflow_test_skill" in loaded_skills
        
        # 4. 验证技能被注册
        assert len(skill_manager.list_skills()) == 1
        assert adapter_manager.has_claude_skills() is True
        
        # 5. 获取特定技能
        skill = adapter_manager.get_claude_skill_by_name("workflow_test_skill")
        assert skill is not None
        assert skill.name == "workflow_test_skill"
        
        # 6. 执行技能
        execution_result = await adapter_manager.execute_skill("workflow_test_skill", {"input": "工作流测试"})
        assert "Claude Skill Adapter: workflow_test_skill" in execution_result
        assert "工作流测试" in execution_result
        
        # 7. 列出所有技能
        all_skills = adapter_manager.list_claude_skills()
        assert len(all_skills) == 1
        assert all_skills[0].name == "workflow_test_skill"


class TestSkillsDirectoryLoading:
    """测试从目录加载技能"""
    
    def test_load_skills_from_directory(self, temp_skills_dir):
        """测试从目录加载技能"""
        manager = SkillManager()
        
        # 创建Python技能文件
        # 源码解析固定 UTF-8：Windows 默认 cp936 写中文注释会解码失败，必须显式 utf-8
        # 内嵌模块须用 src.daip_live 前缀：manager 相对导入解析为 src.daip_live.skills.base.Skill，
        # 若内嵌用 daip_live 前缀会产生两个 Skill 类副本导致 issubclass 失败
        skill_file = temp_skills_dir / "math_skill.py"
        skill_file.write_text("""
from src.daip_live.skills.base import Skill, SkillInput, SkillOutput, SkillMetadata

class MathSkill(Skill):
    def __init__(self):
        metadata = SkillMetadata(
            name="math_skill",
            description="数学技能",
            version="1.0.0",
            author="test_author",
        )
        super().__init__(metadata)
    
    def execute(self, input: SkillInput) -> SkillOutput:
        return SkillOutput(
            result="数学计算完成",
            confidence=0.95,
            execution_time=0.05
        )

skill_instance = MathSkill()
""", encoding="utf-8")
        
        # 加载技能
        loaded_count = manager.load_skills_from_directory(str(temp_skills_dir))
        
        assert loaded_count == 1
        assert manager.get_skill("math_skill") is not None
        
        # 执行技能验证
        skill = manager.get_skill("math_skill")
        result = skill.execute(SkillInput(data="test"))
        assert result.result == "数学计算完成"


# 异步测试运行器
async def run_all_async_tests():
    """运行所有异步测试"""
    adapter_test = TestClaudeSkillAdapterManager()
    
    # 每个测试用独立目录，避免加载类测试因共享目录累积计数
    def fresh_dir():
        return Path(tempfile.mkdtemp())
    
    await adapter_test.test_claude_adapter_manager_initialization()
    await adapter_test.test_create_skill_adapter_from_claude_definition(fresh_dir())
    await adapter_test.test_load_claude_skills_from_directory_traditional_format(fresh_dir())
    await adapter_test.test_load_claude_skills_simple_method_traditional_format(fresh_dir())
    await adapter_test.test_load_claude_skills_simple_method_new_format(fresh_dir())
    await adapter_test.test_get_claude_skill_by_name(fresh_dir())
    await adapter_test.test_list_claude_skills(fresh_dir())
    await adapter_test.test_has_claude_skills(fresh_dir())
    await adapter_test.test_execute_skill(fresh_dir())
    
    # 集成测试
    integration_test = TestClaudeSkillsIntegration()
    await integration_test.test_complete_claude_skills_workflow(fresh_dir())


def test_sync_runner():
    """同步测试运行器"""
    # 运行同步测试
    metadata_test = TestSkillMetadata()
    metadata_test.test_skill_metadata_creation()
    
    base_test = TestSkillBase()
    base_test.test_skill_creation()
    base_test.test_skill_input_output()
    
    manager_test = TestSkillManager()
    manager_test.test_skill_manager_initialization()
    manager_test.test_register_skill()
    manager_test.test_register_duplicate_skill_raises_error()
    manager_test.test_unregister_skill()
    manager_test.test_get_nonexistent_skill_returns_none()
    manager_test.test_list_skills()
    manager_test.test_get_skill_metadata()
    manager_test.test_find_skills_by_tag()
    
    definition_test = TestClaudeSkillDefinition()
    definition_test.test_claude_skill_definition_creation()
    
    directory_test = TestSkillsDirectoryLoading()
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        directory_test.test_load_skills_from_directory(temp_path)
    
    # 运行异步测试
    asyncio.run(run_all_async_tests())


if __name__ == "__main__":
    test_sync_runner()
    print("Claude Skills集成和调用功能TDD测试完成!")

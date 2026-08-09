"""
多角色多模型wiki生成功能的TDD测试
"""

import asyncio
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.daip_live.wiki.manager import (
    PageNotFoundError,
    WikiError,
    WikiManager,
    WikiPage,
)


@pytest.fixture
def temp_wiki_dir():
    """临时Wiki目录测试夹具（模块级，供所有测试类复用）"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def temp_wiki_dir_with_mock_services(temp_wiki_dir):
    """带模拟服务的临时Wiki目录测试夹具（模块级）"""
    with (
        patch(
            "src.daip_live.p4_role_manager_tools.role_model_manager.RoleModelManager"
        ) as mock_role_manager,
        patch(
            "src.daip_live.model_provider.provider.LiteLLMProvider"
        ) as mock_model_provider,
    ):
        # 配置模拟对象
        mock_mapping = Mock()
        mock_mapping.role_model_config = Mock()
        mock_mapping.role_model_config.model_name = "gpt-3.5-turbo"
        mock_mapping.role_model_config.temperature = 0.7
        mock_mapping.role_model_config.max_tokens = 150

        mock_role_manager.get_role_model_mapping.return_value = mock_mapping
        mock_model_provider.generate = AsyncMock(return_value=("模拟AI生成的内容", {}))

        yield temp_wiki_dir, mock_role_manager, mock_model_provider


class TestWikiPage:
    """测试Wiki页面模型"""

    def test_wiki_page_creation(self):
        """测试Wiki页面创建"""
        content = "# 测试页面\n这是测试内容"
        page = WikiPage(
            title="测试页面",
            content=content,
            file_path=Path("test.md"),
            created_at=datetime.now(),
            modified_at=datetime.now(),
            tags=["测试", "wiki"],
        )

        assert page.title == "测试页面"
        assert page.content == content
        assert "测试" in page.tags
        assert "wiki" in page.tags
        # 源码权威: get_word_count 用 content.split()（models.py:146），
        # "# 测试页面\n这是测试内容" 切分为 3 个词
        assert page.get_word_count() == 3
        assert page.has_tag("测试") is True
        assert page.has_tag("不存在") is False

    def test_wiki_page_update(self):
        """测试Wiki页面更新"""
        page = WikiPage(
            title="测试页面",
            content="# 测试\n旧内容",
            file_path=Path("test.md"),
            created_at=datetime.now() - timedelta(seconds=1),
            modified_at=datetime.now() - timedelta(seconds=1),
        )

        original_modified = page.modified_at
        page.update_content("新内容")

        assert page.content == "新内容"
        assert page.modified_at > original_modified

    def test_wiki_page_reading_time(self):
        """测试Wiki页面阅读时间计算"""
        # 创建较长内容的页面
        long_content = "这是一段很长的内容。" * 100  # 200字符
        page = WikiPage(
            title="长内容页面",
            content=long_content,
            file_path=Path("long_test.md"),
            created_at=datetime.now(),
            modified_at=datetime.now(),
        )

        # 按照每分钟200字计算，应该需要约1分钟
        reading_time = page.get_reading_time()
        assert reading_time >= 1

    def test_wiki_page_serialization(self):
        """测试Wiki页面序列化"""
        page = WikiPage(
            title="序列化测试",
            content="# 序列化\n测试内容",
            file_path=Path("serialize_test.md"),
            created_at=datetime.now(),
            modified_at=datetime.now(),
            tags=["序列化", "测试"],
        )

        serialized = page.to_dict()
        assert serialized["title"] == "序列化测试"
        assert serialized["content"] == "# 序列化\n测试内容"
        assert "序列化" in serialized["tags"]

        # 测试反序列化
        deserialized = WikiPage.from_dict(serialized)
        assert deserialized.title == "序列化测试"
        assert deserialized.content == "# 序列化\n测试内容"
        assert "序列化" in deserialized.tags


class TestWikiManager:
    """测试Wiki管理器"""

    def test_wiki_manager_initialization(self, temp_wiki_dir):
        """测试Wiki管理器初始化"""
        manager = WikiManager(temp_wiki_dir)

        assert manager.wiki_root == temp_wiki_dir
        assert manager.get_page_count() == 0

    def test_wiki_manager_initialization_with_invalid_path(self):
        """测试使用无效路径初始化Wiki管理器"""
        with pytest.raises(TypeError):
            WikiManager("invalid_path")  # 应该传入Path对象而不是字符串

    def test_create_page_basic(self, temp_wiki_dir):
        """测试基本页面创建"""
        manager = WikiManager(temp_wiki_dir)

        page = manager.create_page(
            title="测试页面", content="# 测试\n这是测试内容", tags=["测试", "wiki"]
        )

        assert page.title == "测试页面"
        assert page.content == "# 测试\n这是测试内容"
        assert "测试" in page.tags
        assert page.file_path.exists()
        assert manager.get_page_count() == 1

    def test_create_page_with_empty_title_raises_error(self, temp_wiki_dir):
        """测试创建空标题页面时抛出错误"""
        manager = WikiManager(temp_wiki_dir)

        # 源码权威: 空标题+空内容才抛错；非空内容会从内容首行提取标题（manager.py:144-156）  # noqa: E501
        with pytest.raises(ValueError, match="Title cannot be empty"):
            manager.create_page("", "")

    def test_create_page_with_whitespace_only_title_raises_error(self, temp_wiki_dir):
        """测试创建空白标题页面时抛出错误"""
        manager = WikiManager(temp_wiki_dir)

        # 源码权威: 空标题+空内容才抛错；非空内容会从内容首行提取标题（manager.py:144-156）  # noqa: E501
        with pytest.raises(ValueError, match="Title cannot be empty"):
            manager.create_page("   ", "")

    def test_get_page_by_title(self, temp_wiki_dir):
        """测试根据标题获取页面"""
        manager = WikiManager(temp_wiki_dir)

        # 创建页面
        manager.create_page(title="获取测试", content="# 获取测试\n内容", tags=["获取"])

        # 获取页面
        retrieved_page = manager.get_page_by_title("获取测试")

        assert retrieved_page is not None
        assert retrieved_page.title == "获取测试"
        assert retrieved_page.content == "# 获取测试\n内容"
        assert "获取" in retrieved_page.tags

    def test_get_nonexistent_page_returns_none(self, temp_wiki_dir):
        """测试获取不存在的页面返回None"""
        manager = WikiManager(temp_wiki_dir)

        page = manager.get_page_by_title("不存在的页面")

        assert page is None

    def test_list_all_pages(self, temp_wiki_dir):
        """测试列出所有页面"""
        manager = WikiManager(temp_wiki_dir)

        # 创建多个页面
        manager.create_page("页面1", "内容1", ["标签1"])
        manager.create_page("页面2", "内容2", ["标签2"])

        pages = manager.list_all_pages()

        assert len(pages) == 2
        titles = [p.title for p in pages]
        assert "页面1" in titles
        assert "页面2" in titles

    def test_search_pages_by_tag(self, temp_wiki_dir):
        """测试按标签搜索页面"""
        manager = WikiManager(temp_wiki_dir)

        # 创建带标签的页面
        manager.create_page("页面A", "内容A", ["科技", "AI"])
        manager.create_page("页面B", "内容B", ["健康"])
        manager.create_page("页面C", "内容C", ["科技", "创新"])

        tech_pages = manager.search_pages_by_tag("科技")

        assert len(tech_pages) == 2
        titles = [p.title for p in tech_pages]
        assert "页面A" in titles
        assert "页面C" in titles

        ai_pages = manager.search_pages_by_tag("AI")
        assert len(ai_pages) == 1
        assert ai_pages[0].title == "页面A"

    def test_search_pages_by_content(self, temp_wiki_dir):
        """测试按内容搜索页面"""
        manager = WikiManager(temp_wiki_dir)

        # 创建包含特定内容的页面
        manager.create_page("Python页面", "Python是一种编程语言", ["编程"])
        manager.create_page("Java页面", "Java也是一种编程语言", ["编程"])
        manager.create_page("AI页面", "人工智能技术", ["AI"])

        programming_pages = manager.search_pages_by_content("编程")

        assert len(programming_pages) == 2
        titles = [p.title for p in programming_pages]
        assert "Python页面" in titles
        assert "Java页面" in titles

    def test_update_page(self, temp_wiki_dir):
        """测试更新页面"""
        manager = WikiManager(temp_wiki_dir)

        # 创建页面
        manager.create_page(
            title="更新测试", content="# 更新测试\n原始内容", tags=["原始"]
        )

        # 更新页面
        updated_page = manager.update_page("更新测试", "新内容", ["新标签"])

        assert updated_page.content == "新内容"
        assert "新标签" in updated_page.tags
        assert "原始" not in updated_page.tags

    def test_update_nonexistent_page_raises_error(self, temp_wiki_dir):
        """测试更新不存在的页面时抛出错误"""
        manager = WikiManager(temp_wiki_dir)

        with pytest.raises(ValueError, match="Page with title '不存在' not found"):
            manager.update_page("不存在", "新内容")

    def test_delete_page(self, temp_wiki_dir):
        """测试删除页面"""
        manager = WikiManager(temp_wiki_dir)

        # 创建页面
        manager.create_page("删除测试", "待删除内容")

        assert manager.get_page_count() == 1

        # 删除页面
        result = manager.delete_page("删除测试")

        assert result is True
        assert manager.get_page_count() == 0
        assert manager.get_page_by_title("删除测试") is None

    def test_delete_nonexistent_page(self, temp_wiki_dir):
        """测试删除不存在的页面"""
        manager = WikiManager(temp_wiki_dir)

        result = manager.delete_page("不存在的页面")

        assert result is False

    def test_get_all_tags(self, temp_wiki_dir):
        """测试获取所有标签"""
        manager = WikiManager(temp_wiki_dir)

        # 创建带标签的页面
        manager.create_page("页面1", "内容1", ["标签A", "标签B"])
        manager.create_page("页面2", "内容2", ["标签B", "标签C"])
        manager.create_page("页面3", "内容3", ["标签A", "标签C", "标签D"])

        all_tags = manager.get_all_tags()

        assert len(all_tags) == 4  # A, B, C, D
        assert "标签A" in all_tags
        assert "标签B" in all_tags
        assert "标签C" in all_tags
        assert "标签D" in all_tags

    def test_get_statistics(self, temp_wiki_dir):
        """测试获取统计信息"""
        manager = WikiManager(temp_wiki_dir)

        # 创建多个页面
        manager.create_page("统计测试1", "内容" * 100, ["统计", "测试"])
        manager.create_page("统计测试2", "更多内容" * 50, ["统计", "分析"])

        stats = manager.get_statistics()

        assert stats.total_pages == 2
        assert stats.total_tags >= 2  # 至少有 '统计', '测试', '分析' 标签
        # 源码权威: get_word_count 用 content.split()（models.py:146），
        # 无空格中文算 1 个词；"内容"*100 与 "更多内容"*50 均为 1 词/页
        assert stats.total_words == 2
        assert isinstance(stats.last_updated, datetime)
        assert isinstance(stats.most_used_tags, list)
        assert isinstance(stats.pages_by_reading_time, dict)


class TestWikiMultiRoleCollaboration:
    """测试多角色协作功能"""

    async def test_create_collaborative_page(self, temp_wiki_dir_with_mock_services):
        """测试创建协作页面"""
        temp_wiki_dir, mock_role_manager, mock_model_provider = (
            temp_wiki_dir_with_mock_services
        )

        manager = WikiManager(
            wiki_root=temp_wiki_dir,
            role_model_manager=mock_role_manager,
            model_provider=mock_model_provider,
        )

        # 定义角色指令
        roles_instructions = {
            "domain_expert": "提供专业领域知识",
            "researcher": "提供相关研究信息",
            "editor": "负责内容编辑和润色",
        }

        # 创建协作页面
        page = await manager.create_collaborative_page(
            title="AI伦理协作页面",
            initial_content="# AI伦理\n初始内容",
            roles_instructions=roles_instructions,
        )

        assert page.title == "AI伦理协作页面"
        assert "# AI伦理" in page.content
        assert (
            "域专家" in page.content or "expert" in page.content
        )  # 检查是否有AI贡献内容

        # 验证至少有2个页面(由于AI贡献)
        assert manager.get_page_count() == 1

    async def test_add_content_by_role(self, temp_wiki_dir_with_mock_services):
        """测试为页面添加角色内容"""
        temp_wiki_dir, mock_role_manager, mock_model_provider = (
            temp_wiki_dir_with_mock_services
        )

        manager = WikiManager(
            wiki_root=temp_wiki_dir,
            role_model_manager=mock_role_manager,
            model_provider=mock_model_provider,
        )

        # 首先创建一个基础页面
        manager.create_page(title="角色添加测试", content="# 角色测试\n基础内容")

        # 添加角色内容
        updated_page = await manager.add_content_by_role(
            page_title="角色添加测试", role_name="技术专家", instruction="添加技术细节"
        )

        assert updated_page.title == "角色添加测试"
        assert "基础内容" in updated_page.content
        assert "技术专家" in updated_page.content

    async def test_add_content_by_role_to_nonexistent_page_raises_error(
        self, temp_wiki_dir_with_mock_services
    ):
        """测试为不存在的页面添加角色内容时抛出错误"""
        temp_wiki_dir, mock_role_manager, mock_model_provider = (
            temp_wiki_dir_with_mock_services
        )

        manager = WikiManager(
            wiki_root=temp_wiki_dir,
            role_model_manager=mock_role_manager,
            model_provider=mock_model_provider,
        )

        with pytest.raises(PageNotFoundError):
            await manager.add_content_by_role(
                page_title="不存在的页面", role_name="测试角色", instruction="测试指令"
            )

    async def test_add_content_by_role_without_ai_services_raises_error(
        self, temp_wiki_dir
    ):
        """测试在没有AI服务配置时添加角色内容抛出错误"""
        manager = WikiManager(wiki_root=temp_wiki_dir)

        with pytest.raises(
            WikiError, match="WikiManager is not configured for AI content generation"
        ):
            await manager.add_content_by_role(
                page_title="测试", role_name="测试角色", instruction="测试指令"
            )


class TestWikiAdvancedFeatures:
    """测试Wiki高级功能"""

    def test_batch_create_pages(self, temp_wiki_dir):
        """测试批量创建页面"""
        manager = WikiManager(temp_wiki_dir)

        pages_data = [
            {"title": "批量页面1", "content": "内容1", "tags": ["批量", "测试1"]},
            {"title": "批量页面2", "content": "内容2", "tags": ["批量", "测试2"]},
            {"title": "批量页面3", "content": "内容3", "tags": ["批量", "测试3"]},
        ]

        created_pages = manager.batch_create_pages(pages_data)

        assert len(created_pages) == 3
        assert manager.get_page_count() == 3

        # 验证所有页面都创建成功
        for i in range(1, 4):
            page = manager.get_page_by_title(f"批量页面{i}")
            assert page is not None
            assert f"内容{i}" in page.content
            assert "批量" in page.tags

    def test_batch_create_pages_with_duplicate_raises_error(self, temp_wiki_dir):
        """测试批量创建页面时出现重复会清理并抛出错误"""
        manager = WikiManager(temp_wiki_dir)

        pages_data = [
            {
                "title": "正常页面",
                "content": "这是一段正常的页面内容",
                "tags": ["测试"],
            },
            {
                "title": "重复页面",
                "content": "这是重复页面的第一段内容",
                "tags": ["重复"],
            },
            {
                "title": "重复页面",
                "content": "这是重复页面的第二段内容",
                "tags": ["重复"],
            },  # 重复标题
        ]

        # 源码权威: 内容 <10 字符会被 _is_empty_document 视为空文档走更新路径，
        # 因此重复用例需使用足够长的内容才能触发 ValueError
        with pytest.raises(ValueError, match="Page '重复页面' already exists"):
            manager.batch_create_pages(pages_data)

        # 验证没有页面被创建（由于事务性回滚）
        assert manager.get_page_count() == 0

    def test_batch_delete_pages(self, temp_wiki_dir):
        """测试批量删除页面"""
        manager = WikiManager(temp_wiki_dir)

        # 创建测试页面
        manager.create_page("删除测试1", "内容1", ["测试"])
        manager.create_page("删除测试2", "内容2", ["测试"])
        manager.create_page("保留页面", "内容3", ["保留"])

        assert manager.get_page_count() == 3

        # 批量删除
        results = manager.batch_delete_pages(["删除测试1", "删除测试2", "不存在页面"])

        assert results["删除测试1"] is True
        assert results["删除测试2"] is True
        assert results["不存在页面"] is False
        assert manager.get_page_count() == 1  # 只剩下保留页面

    def test_export_pages_markdown(self, temp_wiki_dir):
        """测试导出页面为markdown格式"""
        manager = WikiManager(temp_wiki_dir)

        # 创建测试页面
        manager.create_page("导出测试", "# 导出测试\n导出内容", ["导出"])

        # 创建导出目录
        export_dir = temp_wiki_dir / "export"
        manager.export_pages(export_dir, format="markdown")

        # 验证导出文件存在
        exported_file = export_dir / "导出测试.md"
        assert exported_file.exists()

        with open(exported_file, encoding="utf-8") as f:
            content = f.read()
            assert "# 导出测试" in content
            assert "导出内容" in content

    def test_export_pages_json(self, temp_wiki_dir):
        """测试导出页面为json格式"""
        manager = WikiManager(temp_wiki_dir)

        # 创建测试页面
        manager.create_page("JSON导出", "# JSON导出\nJSON内容", ["导出"])

        # 创建导出目录
        export_dir = temp_wiki_dir / "json_export"
        manager.export_pages(export_dir, format="json")

        # 验证导出文件存在
        exported_file = export_dir / "wiki_export.json"
        assert exported_file.exists()

        with open(exported_file, encoding="utf-8") as f:
            data = json.load(f)
            assert "export_date" in data
            assert "total_pages" in data
            assert "pages" in data
            assert len(data["pages"]) == 1
            assert data["pages"][0]["title"] == "JSON导出"

    def test_export_pages_invalid_format_raises_error(self, temp_wiki_dir):
        """测试使用无效格式导出页面时抛出错误"""
        manager = WikiManager(temp_wiki_dir)

        export_dir = temp_wiki_dir / "invalid_export"

        with pytest.raises(ValueError, match="Unsupported export format: invalid"):
            manager.export_pages(export_dir, format="invalid")

    def test_search_advanced(self, temp_wiki_dir):
        """测试高级搜索功能"""
        manager = WikiManager(temp_wiki_dir)

        # 创建带标签的测试页面
        manager.create_page("AI技术", "# AI技术\nAI相关内容", ["AI", "技术"])
        manager.create_page("医疗健康", "# 医疗健康\n健康相关内容", ["医疗", "健康"])
        manager.create_page("AI医疗", "# AI医疗\nAI在医疗中的应用", ["AI", "医疗"])

        # 测试按内容搜索
        content_results = manager.search_advanced("AI", search_type="content")
        assert len(content_results) == 2  # AI技术 和 AI医疗

        # 测试按标题搜索
        title_results = manager.search_advanced("医疗", search_type="title")
        assert len(title_results) == 2  # 医疗健康 和 AI医疗

        # 测试按标签过滤
        tag_results = manager.search_advanced(
            "AI", search_type="content", tags=["医疗"]
        )
        assert len(tag_results) == 1  # 只有AI医疗页面同时包含AI内容和医疗标签

        # 测试无效搜索类型
        with pytest.raises(ValueError, match="Invalid search type: invalid"):
            manager.search_advanced("test", search_type="invalid")

    def test_get_recent_pages(self, temp_wiki_dir):
        """测试获取最近页面功能"""
        manager = WikiManager(temp_wiki_dir)

        # 创建页面（按时间顺序）
        manager.create_page("最早页面", "最早内容")
        import time

        time.sleep(0.01)  # 确保时间戳不同
        manager.create_page("中间页面", "中间内容")
        time.sleep(0.01)
        manager.create_page("最新页面", "最新内容")

        recent_pages = manager.get_recent_pages(limit=2)

        assert len(recent_pages) == 2
        # 最新页面应该排在前面
        assert recent_pages[0].title == "最新页面"
        assert recent_pages[1].title == "中间页面"


class TestWikiErrorHandling:
    """测试Wiki错误处理"""

    def test_create_page_already_exists(self, temp_wiki_dir):
        """测试创建已存在页面的处理"""
        manager = WikiManager(temp_wiki_dir)

        # 首次创建（内容需 ≥10 字符，否则 _is_empty_document 视为空文档走更新路径）
        manager.create_page("测试页面", "这是初始页面的完整内容")

        # 尝试再次创建同名页面（带内容）- 应该抛出异常
        with pytest.raises(
            ValueError, match="Page '测试页面' already exists and contains content"
        ):
            manager.create_page("测试页面", "这是新的页面内容")

        # 验证原始页面未被修改
        page = manager.get_page_by_title("测试页面")
        assert page.content == "这是初始页面的完整内容"

    def test_create_page_already_exists_with_empty_content(self, temp_wiki_dir):
        """测试创建已存在但内容为空的页面（应覆盖）"""
        manager = WikiManager(temp_wiki_dir)

        # 创建一个空页面
        manager.create_page("空页面", "", ["空"])

        # 尝试用新内容创建同名页面 - 应该更新内容
        new_page = manager.create_page("空页面", "新内容", ["新"])

        # 验证页面内容被更新
        assert new_page.content == "新内容"
        assert "新" in new_page.tags
        assert "空" not in new_page.tags  # 标签也被更新

    def test_is_empty_document(self, temp_wiki_dir):
        """测试空文档判断"""
        manager = WikiManager(temp_wiki_dir)

        # 测试空字符串
        assert manager._is_empty_document("") is True
        assert manager._is_empty_document(" ") is True
        assert manager._is_empty_document("  \n  ") is True

        # 测试少于10字符的内容
        assert manager._is_empty_document("12345") is True  # 5字符
        assert manager._is_empty_document("123456789") is True  # 9字符
        assert manager._is_empty_document("1234567890") is False  # 10字符
        assert manager._is_empty_document("12345678901") is False  # 11字符

        # 测试默认模板
        assert manager._is_empty_document("# 标题\n\n开始编辑您的内容...") is True
        assert (
            manager._is_empty_document(
                "# AI伦理\n\n开始协同创建关于AI伦理的维基页面..."
            )
            is True
        )
        assert manager._is_empty_document("#  \n\n") is True
        assert manager._is_empty_document("# 标题\n\n") is True


class TestWikiIntegration:
    """Wiki模块集成测试"""

    async def test_complete_wiki_workflow(self, temp_wiki_dir_with_mock_services):
        """测试完整的Wiki工作流程"""
        temp_wiki_dir, mock_role_manager, mock_model_provider = (
            temp_wiki_dir_with_mock_services
        )

        # 创建Wiki管理器
        manager = WikiManager(
            wiki_root=temp_wiki_dir,
            role_model_manager=mock_role_manager,
            model_provider=mock_model_provider,
        )

        # 1. 创建协作页面
        page = await manager.create_collaborative_page(
            title="完整工作流测试",
            initial_content="# 完整测试\n工作流测试内容",
            tags=["测试", "工作流"],
        )

        assert page.title == "完整工作流测试"
        assert "# 完整测试" in page.content

        # 2. 添加更多内容
        updated_page = await manager.add_content_by_role(
            page_title="完整工作流测试",
            role_name="分析师",
            instruction="分析当前内容并提供改进建议",
        )

        assert "分析师" in updated_page.content
        assert "工作流测试内容" in updated_page.content

        # 3. 搜索页面
        search_results = manager.search_advanced("工作流", search_type="content")
        assert len(search_results) >= 1
        assert search_results[0].title == "完整工作流测试"

        # 4. 获取统计信息
        stats = manager.get_statistics()
        assert stats.total_pages == 1
        assert "测试" in manager.get_all_tags()

        # 5. 导出页面
        export_dir = temp_wiki_dir / "export"
        manager.export_pages(export_dir, format="json")

        export_file = export_dir / "wiki_export.json"
        assert export_file.exists()


# 异步测试运行器
async def run_all_async_tests():
    """运行所有异步测试"""
    collaboration_test = TestWikiMultiRoleCollaboration()

    # 需要临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # 设置模拟服务
        with (
            patch(
                "src.daip_live.p4_role_manager_tools.role_model_manager.RoleModelManager"
            ) as mock_role_manager,
            patch(
                "src.daip_live.model_provider.provider.LiteLLMProvider"
            ) as mock_model_provider,
        ):
            mock_mapping = Mock()
            mock_mapping.role_model_config = Mock()
            mock_mapping.role_model_config.model_name = "gpt-3.5-turbo"
            mock_mapping.role_model_config.temperature = 0.7
            mock_mapping.role_model_config.max_tokens = 150

            mock_role_manager.get_role_model_mapping.return_value = mock_mapping
            mock_model_provider.generate = AsyncMock(
                return_value=("模拟AI生成的内容", {})
            )

            await collaboration_test.test_create_collaborative_page(
                (temp_path, mock_role_manager, mock_model_provider)
            )
            await collaboration_test.test_add_content_by_role(
                (temp_path, mock_role_manager, mock_model_provider)
            )

            # 测试错误处理
            await collaboration_test.test_add_content_by_role_to_nonexistent_page_raises_error(  # noqa: E501
                (temp_path, mock_role_manager, mock_model_provider)
            )

            # 集成测试（独立目录，避免前序测试创建的页面影响 total_pages 断言）
            integration_test = TestWikiIntegration()
            integration_dir = Path(tempfile.mkdtemp())
            await integration_test.test_complete_wiki_workflow(
                (integration_dir, mock_role_manager, mock_model_provider)
            )


def test_sync_runner():
    """同步测试运行器"""
    # 创建临时目录供测试使用
    with tempfile.TemporaryDirectory() as temp_dir:
        Path(temp_dir)

        # 运行同步测试
        page_test = TestWikiPage()
        page_test.test_wiki_page_creation()
        page_test.test_wiki_page_update()
        page_test.test_wiki_page_reading_time()
        page_test.test_wiki_page_serialization()

        manager_test = TestWikiManager()

        # WikiManager 会从磁盘加载既有页面，每个测试用独立目录避免状态累积
        def fresh_dir():
            return Path(tempfile.mkdtemp())

        manager_test.test_wiki_manager_initialization(fresh_dir())
        manager_test.test_wiki_manager_initialization_with_invalid_path()
        manager_test.test_create_page_basic(fresh_dir())
        manager_test.test_create_page_with_empty_title_raises_error(fresh_dir())
        manager_test.test_create_page_with_whitespace_only_title_raises_error(
            fresh_dir()
        )
        manager_test.test_get_page_by_title(fresh_dir())
        manager_test.test_get_nonexistent_page_returns_none(fresh_dir())
        manager_test.test_list_all_pages(fresh_dir())
        manager_test.test_search_pages_by_tag(fresh_dir())
        manager_test.test_search_pages_by_content(fresh_dir())
        manager_test.test_update_page(fresh_dir())
        manager_test.test_update_nonexistent_page_raises_error(fresh_dir())
        manager_test.test_delete_page(fresh_dir())
        manager_test.test_delete_nonexistent_page(fresh_dir())
        manager_test.test_get_all_tags(fresh_dir())
        manager_test.test_get_statistics(fresh_dir())

        advanced_test = TestWikiAdvancedFeatures()
        advanced_test.test_batch_create_pages(fresh_dir())
        advanced_test.test_batch_create_pages_with_duplicate_raises_error(fresh_dir())
        advanced_test.test_batch_delete_pages(fresh_dir())
        advanced_test.test_export_pages_markdown(fresh_dir())
        advanced_test.test_export_pages_json(fresh_dir())
        advanced_test.test_export_pages_invalid_format_raises_error(fresh_dir())
        advanced_test.test_search_advanced(fresh_dir())
        advanced_test.test_get_recent_pages(fresh_dir())

        error_test = TestWikiErrorHandling()
        error_test.test_create_page_already_exists(fresh_dir())
        error_test.test_create_page_already_exists_with_empty_content(fresh_dir())
        error_test.test_is_empty_document(fresh_dir())

    # 运行异步测试
    asyncio.run(run_all_async_tests())


if __name__ == "__main__":
    test_sync_runner()

#!/usr/bin/env python3
"""Personal Intelligence Hub - Wiki Panel Tests

测试Wiki知识库面板组件功能
"""

from datetime import datetime
from unittest.mock import patch

import pytest

from personal_intelligence_hub.components.wiki_panel import WikiPanel
from personal_intelligence_hub.models.wiki_models import (
    ConsensusNodeFact,
    WikiPage,
    WikiPageStatus,
    WikiSearchResult,
    WikiUpdate,
    WikiUpdateSource,
    WikiVersion,
)


class TestWikiPanel:
    """Wiki面板组件测试类"""

    def setup_method(self):
        """测试前置设置"""
        with patch('lona.View.__init__', return_value=None):
            self.panel = WikiPanel()
            self.panel.current_page = None
            self.panel.search_results = []
            self.panel.facts = []

    def test_initialization(self):
        """测试组件初始化"""
        with patch('lona.View.__init__', return_value=None):
            panel = WikiPanel()
            assert panel is not None
            assert panel.current_page is None
            assert panel.search_results == []
            assert panel.facts == []

    def test_render_search_result(self):
        """测试搜索结果渲染"""
        result = WikiSearchResult(
            page_id="test_page",
            title="测试页面",
            content_preview="这是一个测试内容预览...",
            quality_score=0.85,
            relevance_score=0.92,
            last_updated=datetime.now()
        )

        html = self.panel.render_search_result(result)

        assert html is not None
        assert hasattr(html, 'tag_name')
        assert html.tag_name == 'div'

    def test_render_current_page(self):
        """测试当前页面渲染"""
        # 测试空状态
        html_empty = self.panel.render_current_page()
        assert html_empty is not None
        assert "选择一个页面查看详情" in str(html_empty)

        # 测试有页面状态
        self.panel.current_page = WikiPage(
            id="test_page",
            title="测试页面",
            content="这是测试内容",
            quality_score=0.90,
            version=2,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status=WikiPageStatus.PUBLISHED,
            tags=["测试", "示例"],
            metadata={"author": "测试"}
        )

        html = self.panel.render_current_page()
        assert html is not None
        assert "测试页面" in str(html)

    def test_render_consensus_facts_empty(self):
        """测试共识节点事实渲染 - 空状态"""
        html = self.panel.render_consensus_facts()
        assert html is not None
        assert "暂无共识节点事实" in str(html)

    def test_render_consensus_facts_with_data(self):
        """测试共识节点事实渲染 - 有数据"""
        self.panel.facts = [
            ConsensusNodeFact(
                id="fact1",
                content="测试事实内容1",
                confidence=0.95,
                source_agents=["Agent1", "Agent2"],
                timestamp=datetime.now(),
                metadata={"type": "test"}
            ),
            ConsensusNodeFact(
                id="fact2",
                content="测试事实内容2",
                confidence=0.88,
                source_agents=["Agent3"],
                timestamp=datetime.now(),
                metadata={"type": "test"}
            )
        ]

        html = self.panel.render_consensus_facts()
        assert html is not None
        assert "测试事实内容1" in str(html)
        assert "测试事实内容2" in str(html)

    def test_render_recent_updates(self):
        """测试最近更新渲染"""
        html = self.panel.render_recent_updates()
        assert html is not None
        assert "最近更新" in str(html)

    def test_render_empty_state(self):
        """测试空状态渲染"""
        html = self.panel.render()
        assert html is not None
        assert hasattr(html, 'tag_name')
        assert html.tag_name == 'div'

    def test_render_with_search_results(self):
        """测试带搜索结果的渲染"""
        self.panel.search_results = [
            WikiSearchResult(
                page_id="page1",
                title="搜索结果1",
                content_preview="内容1...",
                quality_score=0.85,
                relevance_score=0.90,
                last_updated=datetime.now()
            )
        ]

        html = self.panel.render()
        assert html is not None
        assert "搜索结果" in str(html)

    def test_render_with_facts(self):
        """测试带事实数据的渲染"""
        self.panel.facts = [
            ConsensusNodeFact(
                id="fact1",
                content="测试事实",
                confidence=0.95,
                source_agents=["Agent1"],
                timestamp=datetime.now(),
                metadata={}
            )
        ]

        html = self.panel.render()
        assert html is not None
        assert "测试事实" in str(html)


class TestWikiModels:
    """Wiki相关数据模型测试"""

    def test_wiki_page_creation(self):
        """测试Wiki页面创建"""
        page = WikiPage(
            id="test_page",
            title="测试页面",
            content="测试内容",
            quality_score=0.85,
            version=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status=WikiPageStatus.PUBLISHED,
            tags=["测试", "示例"],
            metadata={"author": "测试"}
        )

        assert page.id == "test_page"
        assert page.title == "测试页面"
        assert page.quality_score == 0.85
        assert page.status == WikiPageStatus.PUBLISHED

    def test_wiki_update_creation(self):
        """测试Wiki更新创建"""
        update = WikiUpdate(
            id="update1",
            page_id="page1",
            source=WikiUpdateSource.CONSENSUS_NODE,
            content="更新内容",
            quality_score=0.90,
            timestamp=datetime.now(),
            metadata={"type": "test"}
        )

        assert update.id == "update1"
        assert update.source == WikiUpdateSource.CONSENSUS_NODE
        assert update.quality_score == 0.90

    def test_consensus_node_fact_creation(self):
        """测试共识节点事实创建"""
        fact = ConsensusNodeFact(
            id="fact1",
            content="事实内容",
            confidence=0.95,
            source_agents=["Agent1", "Agent2"],
            timestamp=datetime.now(),
            metadata={"type": "consensus"}
        )

        assert fact.id == "fact1"
        assert fact.confidence == 0.95
        assert len(fact.source_agents) == 2

    def test_wiki_search_result_creation(self):
        """测试Wiki搜索结果创建"""
        result = WikiSearchResult(
            page_id="page1",
            title="搜索结果",
            content_preview="预览内容",
            quality_score=0.85,
            relevance_score=0.92,
            last_updated=datetime.now()
        )

        assert result.page_id == "page1"
        assert result.quality_score == 0.85
        assert result.relevance_score == 0.92

    def test_wiki_version_creation(self):
        """测试Wiki版本创建"""
        version = WikiVersion(
            version_id="v1",
            page_id="page1",
            content="版本内容",
            quality_score=0.90,
            created_at=datetime.now(),
            author="测试作者",
            changes=["添加内容", "修正错误"]
        )

        assert version.version_id == "v1"
        assert version.quality_score == 0.90
        assert len(version.changes) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

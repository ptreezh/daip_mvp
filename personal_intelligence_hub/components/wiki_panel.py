"""
Personal Intelligence Hub - Wiki Panel Component

Wiki知识库面板组件
"""

# from lona import Component  # Lona doesn't have Component class
from lona.html import HTML, Div, H3, P, TextInput, Button, Span, H4, Ul, Li
from datetime import datetime
from typing import List, Optional, Dict, Any
import json

from personal_intelligence_hub.models.wiki_models import (
    WikiPage, WikiUpdate, WikiSearchResult, ConsensusNodeFact,
    WikiUpdateSource, WikiPageStatus
)


class WikiPanel:
    """Wiki面板组件"""
    
    def __init__(self):
        self.current_page = None
        self.search_results = []
        self.facts = []
        self.wiki_pages = []
        
        # 创建UI元素
        self.search_input = TextInput(
            placeholder="搜索知识库...",
            _class="wiki-search-input"
        )
        self.search_button = Button("搜索", _class="wiki-search-button")
        
        # 绑定事件
        self.search_button.onclick = self.handle_search
        self.search_input.onkeydown = self.handle_search_keydown
    
    async def handle_search(self, event):
        """处理搜索事件"""
        query = self.search_input.value.strip()
        if not query:
            return
        
        # 模拟搜索结果
        self.search_results = [
            WikiSearchResult(
                page_id="page1",
                title=f"关于{query}的知识",
                content_preview=f"这是关于'{query}'的详细知识内容...",
                quality_score=0.85,
                relevance_score=0.92,
                last_updated=datetime.now()
            ),
            WikiSearchResult(
                page_id="page2",
                title=f"{query}相关概念",
                content_preview=f"与'{query}'相关的核心概念和定义...",
                quality_score=0.78,
                relevance_score=0.88,
                last_updated=datetime.now()
            )
        ]
        
        await self.refresh()
    
    async def handle_search_keydown(self, event):
        """处理搜索输入框按键事件"""
        if event.key == 'Enter':
            await self.handle_search(event)
    
    async def handle_wiki_update(self, update: WikiUpdate):
        """处理Wiki实时更新"""
        if update.source == WikiUpdateSource.CONSENSUS_NODE:
            # 处理共识节点更新
            await self.add_consensus_fact(update.content, update.quality_score)
        elif update.source == WikiUpdateSource.FACT_EXTRACTION:
            # 处理事实提取更新
            await self.add_extracted_fact(update.content, update.quality_score)
        
        await self.refresh()
    
    async def add_consensus_fact(self, content: str, quality_score: float):
        """添加共识节点事实"""
        fact = ConsensusNodeFact(
            id=f"fact_{len(self.facts)}",
            content=content,
            confidence=quality_score,
            source_agents=["Agent1", "Agent2", "Agent3"],
            timestamp=datetime.now(),
            metadata={"type": "consensus", "source": "ConsensusNode"}
        )
        self.facts.append(fact)
    
    async def add_extracted_fact(self, content: str, quality_score: float):
        """添加提取的事实"""
        fact = ConsensusNodeFact(
            id=f"fact_{len(self.facts)}",
            content=content,
            confidence=quality_score,
            source_agents=["FactExtractor"],
            timestamp=datetime.now(),
            metadata={"type": "extracted", "source": "FactExtractionService"}
        )
        self.facts.append(fact)
    
    async def display_page(self, page_id: str):
        """显示Wiki页面"""
        # 模拟页面数据
        self.current_page = WikiPage(
            id=page_id,
            title="示例知识页面",
            content="这是一个示例Wiki页面，包含详细的知识内容。",
            quality_score=0.90,
            version=3,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status=WikiPageStatus.PUBLISHED,
            tags=["示例", "知识", "测试"],
            metadata={"author": "AI系统", "views": 42}
        )
        await self.refresh()
    
    def render_search_result(self, result: WikiSearchResult):
        """渲染搜索结果"""
        return Div(
            Div(
                result.title,
                _class="wiki-result-title"
            ),
            Div(
                f"质量评分: {result.quality_score:.2f} | 相关度: {result.relevance_score:.2f}",
                _class="wiki-result-scores"
            ),
            Div(
                result.content_preview,
                _class="wiki-result-content"
            ),
            Div(
                f"最后更新: {result.last_updated.strftime('%Y-%m-%d %H:%M')}",
                _class="wiki-result-timestamp"
            ),
            _class="wiki-search-result",
            onclick=f"displayPage('{result.page_id}')"
        )
    
    def render_current_page(self):
        """渲染当前页面"""
        if not self.current_page:
            return Div(
                P("选择一个页面查看详情"),
                _class="wiki-no-page"
            )
        
        return Div(
            H3(self.current_page.title, _class="wiki-page-title"),
            Div(
                Span(f"质量评分: {self.current_page.quality_score:.2f}", _class="wiki-page-score"),
                Span(f"版本: {self.current_page.version}", _class="wiki-page-version"),
                Span(f"状态: {self.current_page.status.value}", _class="wiki-page-status"),
                _class="wiki-page-meta"
            ),
            Div(
                f"标签: {', '.join(self.current_page.tags)}",
                _class="wiki-page-tags"
            ),
            Div(
                self.current_page.content,
                _class="wiki-page-content"
            ),
            Div(
                f"创建时间: {self.current_page.created_at.strftime('%Y-%m-%d %H:%M')}",
                _class="wiki-page-timestamp"
            ),
            _class="wiki-current-page"
        )
    
    def render_consensus_facts(self):
        """渲染共识节点事实"""
        if not self.facts:
            return Div(
                P("暂无共识节点事实"),
                _class="wiki-no-facts"
            )
        
        return Div(
            H4("🎯 共识节点事实", _class="wiki-facts-title"),
            *[Div(
                Div(
                    fact.content,
                    _class="wiki-fact-content"
                ),
                Div(
                    f"置信度: {fact.confidence:.2f} | 来源: {', '.join(fact.source_agents)}",
                    _class="wiki-fact-meta"
                ),
                Div(
                    fact.timestamp.strftime('%Y-%m-%d %H:%M'),
                    _class="wiki-fact-timestamp"
                ),
                _class="wiki-fact"
            ) for fact in self.facts[-5:]],  # 显示最近5个事实
            _class="wiki-consensus-facts"
        )
    
    def render_recent_updates(self):
        """渲染最近更新"""
        # 模拟最近更新
        recent_updates = [
            WikiUpdate(
                id="update1",
                page_id="page1",
                source=WikiUpdateSource.CONSENSUS_NODE,
                content="新增关于AI伦理的共识事实",
                quality_score=0.95,
                timestamp=datetime.now(),
                metadata={"type": "addition"}
            ),
            WikiUpdate(
                id="update2",
                page_id="page2",
                source=WikiUpdateSource.FACT_EXTRACTION,
                content="提取了新的技术概念定义",
                quality_score=0.88,
                timestamp=datetime.now(),
                metadata={"type": "extraction"}
            )
        ]
        
        return Div(
            H4("🔄 最近更新", _class="wiki-updates-title"),
            *[Div(
                Div(
                    update.content,
                    _class="wiki-update-content"
                ),
                Div(
                    f"来源: {update.source.value} | 质量: {update.quality_score:.2f}",
                    _class="wiki-update-meta"
                ),
                Div(
                    update.timestamp.strftime('%Y-%m-%d %H:%M'),
                    _class="wiki-update-timestamp"
                ),
                _class="wiki-update"
            ) for update in recent_updates],
            _class="wiki-recent-updates"
        )
    
    def render(self) -> HTML:
        """渲染Wiki面板"""
        return Div(
            H3("📚 知识库", _class="wiki-title"),
            
            # 搜索区域
            Div(
                self.search_input,
                self.search_button,
                _class="wiki-search-area"
            ),
            
            # 当前页面显示
            self.render_current_page(),
            
            # 共识节点事实
            self.render_consensus_facts(),
            
            # 最近更新
            self.render_recent_updates(),
            
            # 搜索结果
            Div(
                H4("🔍 搜索结果") if self.search_results else Div(),
                *[self.render_search_result(result) for result in self.search_results],
                _class="wiki-search-results"
            ) if self.search_results else Div(),
            
            _class="wiki-panel"
        )

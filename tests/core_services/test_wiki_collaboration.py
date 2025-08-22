"""Test Wiki collaboration functionality"""

import pytest
from datetime import datetime
from unittest.mock import Mock

from src.core_services.wiki_service import WikiService
from src.core_services.wiki_collaboration_simplified import (
    SimpleTask, TaskType, TaskStatus, 
    SimpleIntentOptimizer, SimpleRoleCoordinator,
    SimpleExecutor, SimpleTaskCoordinator,
    RoleFeedback,
    CollaborationStorageManager
)


class TestWikiCollaboration:
    """Test Wiki collaboration functionality"""
    
    def test_intent_optimizer_optimizes_user_input(self):
        """Test intent optimizer"""
        # Setup
        optimizer = SimpleIntentOptimizer()
        user_input = "机器学习词条需要更新最新的大模型进展"
        
        # Execute
        result = optimizer.optimize(user_input)
        
        # Verify
        assert "target_entry" in result
        assert "task_type" in result
        assert "optimized_intent" in result
        assert result["target_entry"] == "机器学习"
        assert result["task_type"] == TaskType.UPDATE.value
        assert "更新" in result["optimized_intent"]
    
    def test_role_coordinator_assigns_relevant_roles(self, tmp_path):
        """Test role coordinator assigns relevant roles"""
        # Setup
        storage_manager = CollaborationStorageManager(str(tmp_path / "wiki_collaboration"))
        role_manager = Mock()
        role_coordinator = SimpleRoleCoordinator(storage_manager, role_manager)
        task = SimpleTask(
            id="test_task_1",
            user_input="更新机器学习词条",
            optimized_intent="更新机器学习词条",
            target_entry="机器学习",
            task_type=TaskType.UPDATE.value,
            status=TaskStatus.PENDING.value,
            created_at=datetime.now()
        )
        
        # Execute
        feedbacks = role_coordinator.assign_and_collect(task)
        
        # Verify
        assert len(feedbacks) > 0
        # Verify that at least one role related to machine learning is assigned
        role_names = [f.role_name for f in feedbacks]
        assert any(role in role_names for role in ["AI研究员", "NLP专家", "数据科学家"])
    
    def test_executor_creates_new_wiki_entry(self, tmp_path):
        """Test executor creates new wiki entry"""
        # Setup
        wiki_dir = tmp_path / "wiki"
        wiki_dir.mkdir()
        wiki_service = WikiService(str(wiki_dir))
        storage_manager = CollaborationStorageManager(str(tmp_path / "wiki_collaboration"))
        
        executor = SimpleExecutor(wiki_service, storage_manager)
        task = SimpleTask(
            id="test_task_2",
            user_input="创建量子计算词条",
            optimized_intent="创建量子计算词条",
            target_entry="量子计算",
            task_type=TaskType.CREATE.value,
            status=TaskStatus.PENDING.value,
            created_at=datetime.now()
        )
        
        feedbacks = [
            RoleFeedback(
                task_id=task.id,
                role_name="量子物理学家",
                feedback="建议从基础概念开始介绍量子计算，包括其定义、发展历程和主要应用领域。",
                submitted_at=datetime.now()
            )
        ]
        
        # Execute
        success = executor.execute(task, feedbacks)
        
        # Verify
        assert success is True
        
        # Verify wiki entry was created
        entry = wiki_service.get_entry("量子计算")
        assert entry is not None
        assert "量子计算" in entry.content
        assert "量子物理学家" in entry.content
    
    def test_executor_updates_existing_wiki_entry(self, tmp_path):
        """Test executor updates existing wiki entry"""
        # Setup: Create a wiki entry first
        wiki_dir = tmp_path / "wiki"
        wiki_dir.mkdir()
        wiki_service = WikiService(str(wiki_dir))
        storage_manager = CollaborationStorageManager(str(tmp_path / "wiki_collaboration"))
        
        wiki_service.create_entry(
            entry_name="区块链",
            content="# 区块链\n\n区块链是一种分布式账本技术。",
            author_role="test_user",
            tags=["技术"],
            category="计算机科学"
        )
        
        executor = SimpleExecutor(wiki_service, storage_manager)
        task = SimpleTask(
            id="test_task_3",
            user_input="更新区块链词条，添加最新的应用场景",
            optimized_intent="更新区块链词条",
            target_entry="区块链",
            task_type=TaskType.UPDATE.value,
            status=TaskStatus.PENDING.value,
            created_at=datetime.now()
        )
        
        feedbacks = [
            RoleFeedback(
                task_id=task.id,
                role_name="区块链专家",
                feedback="建议添加关于DeFi、NFT等最新的应用场景。",
                submitted_at=datetime.now()
            )
        ]
        
        # Execute
        success = executor.execute(task, feedbacks)
        
        # Verify
        assert success is True
        
        # Verify wiki entry was updated
        entry = wiki_service.get_entry("区块链")
        assert entry is not None
        assert "DeFi" in entry.content or "NFT" in entry.content
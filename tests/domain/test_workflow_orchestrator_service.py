"""
Workflow Orchestrator Service Tests
========================

This module contains comprehensive tests for the WorkflowOrchestratorService.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from src.domain.value_objects import EntranceType, IntentType, TaskStatus, ConsensusLevel, MessageIntent
from src.domain.entities import User, UserPreference
from src.domain.domain_services import WorkflowOrchestratorService


class TestWorkflowOrchestratorService:
    """Tests for the WorkflowOrchestratorService"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create a WorkflowOrchestratorService instance for testing"""
        return WorkflowOrchestratorService()
    
    @pytest.mark.asyncio
    async def test_plan_workflow_analysis(self, orchestrator):
        """Test planning an analysis workflow"""
        intent = {
            "type": "analysis",
            "content": "Analyze the impact of AI on job markets"
        }
        
        workflow_plan = await orchestrator.plan_workflow(intent)
        
        assert isinstance(workflow_plan, dict)
        assert "workflow_id" in workflow_plan
        assert "steps" in workflow_plan
        assert "estimated_duration" in workflow_plan
        assert "required_agents" in workflow_plan
        assert "intent" in workflow_plan
        assert workflow_plan["intent"] == intent
        assert len(workflow_plan["steps"]) > 0
    
    @pytest.mark.asyncio
    async def test_plan_workflow_discussion(self, orchestrator):
        """Test planning a discussion workflow"""
        intent = {
            "type": "discussion",
            "content": "Discuss the pros and cons of remote work"
        }
        
        workflow_plan = await orchestrator.plan_workflow(intent)
        
        assert isinstance(workflow_plan, dict)
        assert "workflow_id" in workflow_plan
        assert "steps" in workflow_plan
        assert "estimated_duration" in workflow_plan
        assert "required_agents" in workflow_plan
        assert "intent" in workflow_plan
        assert workflow_plan["intent"] == intent
        assert len(workflow_plan["steps"]) > 0
    
    def test_create_analysis_workflow(self, orchestrator):
        """Test creating an analysis workflow"""
        content = "Analyze the impact of AI on job markets"
        intent = {"type": "analysis"}
        
        workflow = orchestrator._create_analysis_workflow(content, intent)
        assert isinstance(workflow, list)
        assert len(workflow) > 0
        assert all("step_id" in step for step in workflow)
        assert all("name" in step for step in workflow)
        assert all("description" in step for step in workflow)
        assert all("type" in step for step in workflow)
        assert all("estimated_time" in step for step in workflow)
        assert all("required_agents" in step for step in workflow)
    
    def test_create_discussion_workflow(self, orchestrator):
        """Test creating a discussion workflow"""
        content = "Discuss the pros and cons of remote work"
        intent = {"type": "discussion"}
        
        workflow = orchestrator._create_discussion_workflow(content, intent)
        assert isinstance(workflow, list)
        assert len(workflow) > 0
        assert all("step_id" in step for step in workflow)
        assert all("name" in step for step in workflow)
        assert all("description" in step for step in workflow)
        assert all("type" in step for step in workflow)
        assert all("estimated_time" in step for step in workflow)
        assert all("required_agents" in step for step in workflow)
    
    def test_estimate_duration(self, orchestrator):
        """Test estimating workflow duration"""
        workflow_steps = [
            {"estimated_time": 2.0},
            {"estimated_time": 5.0},
            {"estimated_time": 3.0}
        ]
        
        duration = orchestrator._estimate_duration(workflow_steps)
        assert isinstance(duration, float)
        assert duration == 10.0
    
    def test_determine_required_agents_analysis(self, orchestrator):
        """Test determining required agents for analysis"""
        intent = {"type": "analysis"}
        agents = orchestrator._determine_required_agents(intent)
        assert isinstance(agents, list)
        assert len(agents) > 0
        assert "analyst" in agents
        assert "domain_expert" in agents
    
    def test_determine_required_agents_discussion(self, orchestrator):
        """Test determining required agents for discussion"""
        intent = {"type": "discussion"}
        agents = orchestrator._determine_required_agents(intent)
        assert isinstance(agents, list)
        assert len(agents) > 0
        assert "facilitator" in agents
        assert "domain_expert" in agents
        assert "critic" in agents
    
    def test_determine_required_agents_complex_task(self, orchestrator):
        """Test determining required agents for complex task"""
        intent = {"type": "analysis", "complexity": 0.9}
        agents = orchestrator._determine_required_agents(intent)
        assert isinstance(agents, list)
        assert len(agents) > 0
        # Should include additional agents for complex tasks
        assert "technical_expert" in agents
    
    @pytest.mark.asyncio
    async def test_start_workflow(self, orchestrator):
        """Test starting a workflow"""
        workflow_id = "test_workflow"
        workflow_plan = {
            "steps": [{"step_id": "step1"}],
            "estimated_duration": 5.0,
            "required_agents": ["agent1"]
        }
        
        result = await orchestrator.start_workflow(workflow_id, workflow_plan)
        assert result == True
        assert workflow_id in orchestrator.active_workflows
        assert orchestrator.active_workflows[workflow_id]["status"] == "running"
    
    @pytest.mark.asyncio
    async def test_start_workflow_already_exists(self, orchestrator):
        """Test starting a workflow that already exists"""
        workflow_id = "existing_workflow"
        workflow_plan = {"steps": []}
        
        # Start the workflow once
        await orchestrator.start_workflow(workflow_id, workflow_plan)
        
        # Try to start it again
        result = await orchestrator.start_workflow(workflow_id, workflow_plan)
        assert result == False
    
    @pytest.mark.asyncio
    async def test_execute_step(self, orchestrator):
        """Test executing a workflow step"""
        workflow_id = "test_workflow"
        workflow_plan = {
            "steps": [
                {
                    "step_id": "step1",
                    "name": "Test Step",
                    "description": "A test step",
                    "type": "test",
                    "estimated_time": 1.0,
                    "required_agents": ["test_agent"]
                }
            ]
        }
        
        # Start the workflow
        await orchestrator.start_workflow(workflow_id, workflow_plan)
        
        # Execute the step
        result = await orchestrator.execute_step(workflow_id, "step1")
        
        assert isinstance(result, dict)
        assert result["step_id"] == "step1"
        assert result["status"] == "completed"
        assert "execution_time" in result
        assert "output" in result
        assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_execute_step_nonexistent_workflow(self, orchestrator):
        """Test executing a step in a nonexistent workflow"""
        with pytest.raises(ValueError, match="Workflow nonexistent_workflow not found"):
            await orchestrator.execute_step("nonexistent_workflow", "step1")
    
    @pytest.mark.asyncio
    async def test_execute_step_nonexistent_step(self, orchestrator):
        """Test executing a nonexistent step in a workflow"""
        workflow_id = "test_workflow"
        workflow_plan = {"steps": [{"step_id": "step1"}]}
        
        # Start the workflow
        await orchestrator.start_workflow(workflow_id, workflow_plan)
        
        # Try to execute a nonexistent step
        with pytest.raises(ValueError, match="Step nonexistent_step not found in workflow"):
            await orchestrator.execute_step(workflow_id, "nonexistent_step")
    
    def test_get_workflow_progress(self, orchestrator):
        """Test getting workflow progress"""
        workflow_id = "test_workflow"
        workflow_plan = {
            "steps": [
                {"step_id": "step1", "estimated_time": 2.0},
                {"step_id": "step2", "estimated_time": 3.0}
            ]
        }
        
        # Manually add a workflow to active_workflows for testing
        orchestrator.active_workflows[workflow_id] = {
            "plan": workflow_plan,
            "status": "running",
            "current_step": 1,  # One step completed
            "start_time": datetime.now(),
            "step_results": {"step1": {"status": "completed"}},
            "progress": 0.5  # 50% progress
        }
        
        progress = orchestrator.get_workflow_progress(workflow_id)
        
        assert isinstance(progress, dict)
        assert progress["workflow_id"] == workflow_id
        assert progress["status"] == "running"
        assert progress["current_step"] == 1
        assert progress["total_steps"] == 2
        assert progress["progress_percentage"] == 50.0
        assert "estimated_time_remaining" in progress
        assert "step_results" in progress
    
    def test_get_workflow_progress_nonexistent(self, orchestrator):
        """Test getting progress for a nonexistent workflow"""
        with pytest.raises(ValueError, match="Workflow nonexistent_workflow not found"):
            orchestrator.get_workflow_progress("nonexistent_workflow")
    
    def test_calculate_remaining_time(self, orchestrator):
        """Test calculating remaining time for a workflow"""
        workflow_id = "test_workflow"
        workflow_plan = {
            "steps": [
                {"step_id": "step1", "estimated_time": 2.0},
                {"step_id": "step2", "estimated_time": 3.0},
                {"step_id": "step3", "estimated_time": 5.0}
            ]
        }
        
        # Manually add a workflow to active_workflows for testing
        orchestrator.active_workflows[workflow_id] = {
            "plan": workflow_plan,
            "status": "running",
            "current_step": 1,  # One step completed
            "start_time": datetime.now(),
            "step_results": {"step1": {"status": "completed"}},
            "progress": 0.33
        }
        
        remaining_time = orchestrator._calculate_remaining_time(workflow_id)
        # Should be 3.0 + 5.0 = 8.0 for remaining steps
        assert remaining_time == 8.0
    
    def test_complete_workflow(self, orchestrator):
        """Test completing a workflow"""
        workflow_id = "test_workflow"
        workflow_plan = {"steps": []}
        
        # Manually add a workflow to active_workflows for testing
        orchestrator.active_workflows[workflow_id] = {
            "plan": workflow_plan,
            "status": "running",
            "current_step": 0,
            "start_time": datetime.now(),
            "step_results": {},
            "progress": 0.0
        }
        
        orchestrator.complete_workflow(workflow_id)
        
        assert orchestrator.active_workflows[workflow_id]["status"] == "completed"
        assert orchestrator.active_workflows[workflow_id]["progress"] == 1.0
        assert "end_time" in orchestrator.active_workflows[workflow_id]
    
    def test_fail_workflow(self, orchestrator):
        """Test failing a workflow"""
        workflow_id = "test_workflow"
        workflow_plan = {"steps": []}
        error_message = "Test error"
        
        # Manually add a workflow to active_workflows for testing
        orchestrator.active_workflows[workflow_id] = {
            "plan": workflow_plan,
            "status": "running",
            "current_step": 0,
            "start_time": datetime.now(),
            "step_results": {},
            "progress": 0.0
        }
        
        orchestrator.fail_workflow(workflow_id, error_message)
        
        assert orchestrator.active_workflows[workflow_id]["status"] == "failed"
        assert orchestrator.active_workflows[workflow_id]["error"] == error_message
        assert "end_time" in orchestrator.active_workflows[workflow_id]
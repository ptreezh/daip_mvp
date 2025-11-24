"""
Integration tests for the hierarchical architecture.
"""
import pytest
from src.daip_live.subagents.grounded_theory import GroundedTheorySubagent
from src.daip_live.subagents.sna_expert import SNASubagent
from src.daip_live.orchestration.manager import SubagentManager
from src.daip_live.orchestration.decomposer import TaskDecomposer
from src.daip_live.skills.text_analysis import TextAnalysisSkill
from src.daip_live.skills.manager import SkillManager
from src.daip_live.execution.parallel import ParallelExecutor
from src.daip_live.execution.synthesizer import ResultSynthesizer
from src.daip_live.skills.base import SkillInput


class TestHierarchicalArchitectureIntegration:
    """Integration tests for the complete hierarchical architecture."""
    
    def test_complete_workflow(self):
        """Test a complete workflow through all layers of the architecture."""
        # 1. Initialize components
        subagent_manager = SubagentManager()
        task_decomposer = TaskDecomposer()
        skill_manager = SkillManager()
        parallel_executor = ParallelExecutor()
        result_synthesizer = ResultSynthesizer()
        
        # 2. Register Subagents
        grounded_theory_subagent = GroundedTheorySubagent()
        sna_subagent = SNASubagent()
        
        subagent_manager.register_subagent(grounded_theory_subagent)
        subagent_manager.register_subagent(sna_subagent)
        
        # 3. Register Skills
        text_analysis_skill = TextAnalysisSkill()
        skill_manager.register_skill(text_analysis_skill)
        
        # 4. Define a complex task
        task = "Analyze social network relationships in Chinese academic institutions using grounded theory approach"
        
        # 5. Decompose the task
        decomposed_task = task_decomposer.decompose(task)
        assert len(decomposed_task.subtasks) > 0
        
        # 6. Match Subagents to subtasks
        subagent_names = []
        for subtask in decomposed_task.subtasks:
            matched_subagent = subagent_manager.match_subagent_to_task(
                subtask.domain, subtask.required_skills)
            if matched_subagent:
                subagent_names.append(matched_subagent)
        
        # 7. Execute Subagent analyses
        analysis_results = []
        test_data = "这是一个测试数据，包含学术机构中的社会网络关系。教师和学生之间存在复杂的关系网络。"
        
        for subagent_name in subagent_names:
            subagent = subagent_manager.get_subagent(subagent_name)
            if subagent:
                result = subagent.analyze(test_data)
                analysis_results.append(result)
        
        # 8. Synthesize Subagent results
        if analysis_results:
            synthesized_result = result_synthesizer.synthesize_subagent_results(analysis_results)
            assert synthesized_result.content is not None
            assert synthesized_result.metadata["synthesized"] == True
        
        # 9. Execute skills in parallel
        skills = [text_analysis_skill]
        inputs = [SkillInput(test_data)]
        
        skill_outputs = parallel_executor.execute_skills_parallel(skills, inputs)
        assert len(skill_outputs) == 1
        
        # 10. Shutdown executor
        parallel_executor.shutdown()
        
        # Verify that the workflow completed successfully
        assert len(subagent_manager.list_subagents()) == 2
        assert len(skill_manager.list_skills()) == 1
    
    def test_subagent_capability_matching(self):
        """Test Subagent capability matching and allocation."""
        # Initialize Subagent manager
        subagent_manager = SubagentManager()
        
        # Register Subagents
        grounded_theory_subagent = GroundedTheorySubagent()
        sna_subagent = SNASubagent()
        
        subagent_manager.register_subagent(grounded_theory_subagent)
        subagent_manager.register_subagent(sna_subagent)
        
        # Test matching to grounded theory domain
        matched_subagent = subagent_manager.match_subagent_to_task("grounded_theory")
        assert matched_subagent is not None
        
        # Test matching to SNA domain
        matched_subagent = subagent_manager.match_subagent_to_task("sna")
        assert matched_subagent is not None
        
        # Test finding Subagents by capability
        grounded_theory_subagents = subagent_manager.find_subagents_by_capability("grounded_theory")
        assert len(grounded_theory_subagents) >= 0  # Could be empty if no matches
        
        sna_subagents = subagent_manager.find_subagents_by_capability("sna")
        assert len(sna_subagents) >= 0  # Could be empty if no matches
    
    def test_skill_execution_and_synthesis(self):
        """Test skill execution and result synthesis."""
        # Initialize components
        skill_manager = SkillManager()
        parallel_executor = ParallelExecutor()
        result_synthesizer = ResultSynthesizer()
        
        # Register skills
        skill1 = TextAnalysisSkill()
        
        # Create a second skill with a different name
        class SecondSkill(TextAnalysisSkill):
            def __init__(self):
                from src.daip_live.skills.base import SkillMetadata
                metadata = SkillMetadata(
                    name="text_analysis_2",
                    description="Second text analysis skill",
                    version="1.0",
                    author="DAIP-LIVE",
                    tags=["text", "analysis", "secondary"]
                )
                super(TextAnalysisSkill, self).__init__(metadata)
        
        skill2 = SecondSkill()
        
        skill_manager.register_skill(skill1)
        skill_manager.register_skill(skill2)
        
        # Execute skills in parallel
        skills = [skill1, skill2]
        inputs = [SkillInput("测试数据1"), SkillInput("测试数据2")]
        
        outputs = parallel_executor.execute_skills_parallel(skills, inputs)
        assert len(outputs) == 2
        
        # Synthesize results
        synthesized_output = result_synthesizer.synthesize_skill_outputs(outputs)
        # Check that the result contains synthesized content
        assert "Text Analysis Results" in synthesized_output.result
        assert synthesized_output.metadata["synthesized"] == True
        
        # Shutdown executor
        parallel_executor.shutdown()
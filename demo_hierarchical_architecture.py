"""
Demonstration script for the hierarchical architecture.
"""
from src.daip_live.subagents.grounded_theory import GroundedTheorySubagent
from src.daip_live.subagents.sna_expert import SNASubagent
from src.daip_live.orchestration.manager import SubagentManager
from src.daip_live.orchestration.decomposer import TaskDecomposer
from src.daip_live.skills.text_analysis import TextAnalysisSkill
from src.daip_live.skills.manager import SkillManager
from src.daip_live.execution.parallel import ParallelExecutor
from src.daip_live.execution.synthesizer import ResultSynthesizer
from src.daip_live.skills.base import SkillInput


def demonstrate_hierarchical_architecture():
    """Demonstrate the complete hierarchical architecture workflow."""
    print("=== DAIP-LIVE Hierarchical Architecture Demonstration ===\n")
    
    # 1. Initialize components
    print("1. Initializing components...")
    subagent_manager = SubagentManager()
    task_decomposer = TaskDecomposer()
    skill_manager = SkillManager()
    parallel_executor = ParallelExecutor()
    result_synthesizer = ResultSynthesizer()
    
    # 2. Register Subagents
    print("2. Registering specialized Subagents...")
    grounded_theory_subagent = GroundedTheorySubagent()
    sna_subagent = SNASubagent()
    
    subagent_manager.register_subagent(grounded_theory_subagent)
    subagent_manager.register_subagent(sna_subagent)
    
    print(f"   Registered Subagents: {subagent_manager.list_subagents()}")
    
    # 3. Register Skills
    print("3. Registering skills...")
    text_analysis_skill = TextAnalysisSkill()
    skill_manager.register_skill(text_analysis_skill)
    
    print(f"   Registered Skills: {skill_manager.list_skills()}")
    
    # 4. Define a complex task
    print("\n4. Defining complex task...")
    task = "Analyze social network relationships in Chinese academic institutions using grounded theory approach"
    print(f"   Task: {task}")
    
    # 5. Decompose the task
    print("\n5. Decomposing task...")
    decomposed_task = task_decomposer.decompose(task)
    print(f"   Decomposed into {len(decomposed_task.subtasks)} subtasks:")
    for i, subtask in enumerate(decomposed_task.subtasks):
        print(f"     {i+1}. {subtask.description} (Domain: {subtask.domain})")
    
    # 6. Match Subagents to subtasks
    print("\n6. Matching Subagents to subtasks...")
    subagent_names = []
    for subtask in decomposed_task.subtasks:
        matched_subagent = subagent_manager.match_subagent_to_task(
            subtask.domain, subtask.required_skills)
        if matched_subagent:
            subagent_names.append(matched_subagent)
            print(f"   Matched '{subtask.domain}' to Subagent: {matched_subagent}")
        else:
            print(f"   No matching Subagent found for domain: {subtask.domain}")
    
    # 7. Execute Subagent analyses
    print("\n7. Executing Subagent analyses...")
    analysis_results = []
    test_data = """在一所中国大学中，教师和学生之间存在着复杂的互动关系。
    教师不仅传授知识，还承担着指导学生研究、职业规划等职责。
    学生则通过课堂学习、科研项目、社团活动等方式与教师建立联系。
    这种关系网络体现了中国教育体系中特有的师生文化。"""
    
    for subagent_name in subagent_names:
        subagent = subagent_manager.get_subagent(subagent_name)
        if subagent:
            print(f"   Executing analysis with {subagent_name}...")
            result = subagent.analyze(test_data)
            analysis_results.append(result)
            print(f"     Confidence: {result.confidence:.2f}")
    
    # 8. Synthesize Subagent results
    print("\n8. Synthesizing Subagent results...")
    if analysis_results:
        synthesized_result = result_synthesizer.synthesize_subagent_results(analysis_results)
        print("   Synthesized result:")
        print(f"     Content preview: {synthesized_result.content[:200]}...")
        print(f"     Average confidence: {synthesized_result.confidence:.2f}")
        print(f"     Sources: {len(synthesized_result.metadata.get('individual_results', []))} Subagents")
    
    # 9. Execute skills in parallel
    print("\n9. Executing skills in parallel...")
    skills = [text_analysis_skill]
    inputs = [SkillInput(test_data)]
    
    skill_outputs = parallel_executor.execute_skills_parallel(skills, inputs)
    print(f"   Executed {len(skill_outputs)} skills in parallel")
    for i, output in enumerate(skill_outputs):
        if "error" not in output.metadata:
            print(f"     Skill {i+1} result preview: {output.result[:100]}...")
        else:
            print(f"     Skill {i+1} encountered an error: {output.result}")
    
    # 10. Shutdown executor
    print("\n10. Cleaning up...")
    parallel_executor.shutdown()
    
    print("\n=== Demonstration Complete ===")
    print(f"Summary: Processed 1 task with {len(subagent_names)} Subagents and {len(skills)} skills")


if __name__ == "__main__":
    demonstrate_hierarchical_architecture()
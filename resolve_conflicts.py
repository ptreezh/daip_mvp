import os
import subprocess
import sys

# List of files with conflicts (obtained from previous findstr command)
files_with_conflicts = [
    "src/core_services/api_contract_generator.py",
    "src/core_services/cognitive_diversity_evaluator.py",
    "src/core_services/collaboration_service.py",
    "src/core_services/collective_intelligence_manager.py",
    "src/core_services/conflict_resolution_strategies.py",
    "src/core_services/consensus_algorithm_interface.py",
    "src/core_services/consensus_algorithm_selector.py",
    "src/core_services/consensus_dispatcher.py",
    "src/core_services/consensus_formation_process.py",
    "src/core_services/consensus_models.py",
    "src/core_services/consensus_quality_evaluator.py",
    "src/core_services/consensus_validation.py",
    "src/core_services/context_collaboration_engine.py",
    "src/core_services/context_optimization_engine.py",
    "src/core_services/context_quality_service.py",
    "src/core_services/document_service.py",
    "src/core_services/emergent_insight_detector.py",
    "src/core_services/evolution_pattern_analyzer.py",
    "src/core_services/fact_validation_service.py",
    "src/core_services/fallback_manager.py",
    "src/core_services/fallback_manager_core.py",
    "src/core_services/fallback_manager_utils.py",
    "src/core_services/git_version_release_system.py",
    "src/core_services/intelligent_context_optimizer.py",
    "src/core_services/knowledge_evolution_manager.py",
    "src/core_services/knowledge_evolution_tracker.py",
    "src/core_services/knowledge_graph_builder.py",
    "src/core_services/knowledge_lineage_manager.py",
    "src/core_services/knowledge_management_service.py",
    "src/core_services/knowledge_persistence_service.py",
    "src/core_services/knowledge_quality_scorer.py",
    "src/core_services/knowledge_quality_trend_monitor.py",
    "src/core_services/knowledge_retrieval_demo.py",
    "src/core_services/knowledge_retrieval_service.py",
    "src/core_services/knowledge_version_control.py",
    "src/core_services/legacy_compatibility_layer.py",
    "src/core_services/personalized_experience_service.py",
    "src/core_services/personal_assistant_adapter.py",
    "src/core_services/personal_context_service.py",
    "src/core_services/personal_knowledge_graph.py",
    "src/core_services/prompt_optimization_service.py",
    "src/core_services/role_recommender_service.py",
    "src/core_services/session_management_service.py",
    "src/core_services/simple_majority_algorithm.py",
    "src/core_services/sskg_storage_adapters.py",
    "src/core_services/storage_adapters/base.py",
    "src/core_services/storage_adapters/role_adapter.py",
    "src/core_services/storage_adapters/session_adapter.py",
    "src/core_services/storage_adapters/wiki_adapter.py",
    "src/core_services/storage_adapters.py",
    "src/core_services/task_context_optimizer.py",
    "src/core_services/unified_consensus_dispatcher.py",
    "src/core_services/unified_consensus_dispatcher_utils.py",
    "src/core_services/user_interest_profiler.py",
    "src/core_services/user_profile_service.py",
    "src/core_services/weighted_voting_algorithm.py",
    "src/core_services/wiki_change_tracker.py",
    "src/core_services/workflow_consensus_algorithm.py",
    "src/core_services/workflow_knowledge_integrator.py",
    "src/debate_system/app.py",
    "src/debate_system/argument_analysis.py",
    "src/debate_system/debate_flow_definition.py",
    "src/debate_system/debate_state_manager.py",
    "src/debate_system/multi_role_dialogue_engine.py",
    "src/debate_system/participant_management.py",
    "src/debate_system/quality_assurance.py",
    "src/debate_system/v0_1_5_quality_check.py",
    "src/debate_system/validate_multi_role_dialogue.py",
    "src/debate_system/websocket_manager.py",
    "src/debate_system/web_interface.py",
    "src/debate_system/__init__.py",
    "src/institutional_primitives/consensus_customization.py",
    "src/institutional_primitives/consensus_node.py",
    "src/institutional_primitives/critical_review_nodes.py",
    "src/institutional_primitives/demo_customization.py",
    "src/institutional_primitives/examples/custom_primitives.py",
    "src/institutional_primitives/multi_perspective/models.py",
    "src/institutional_primitives/multi_perspective/parallel_exploration_node.py",
    "src/institutional_primitives/multi_perspective/refinement_node.py",
    "src/institutional_primitives/multi_perspective/synthesis_node.py",
    "src/institutional_primitives/multi_perspective/task_decomposition_node.py",
    "src/institutional_primitives/multi_perspective/viewpoint_collection_node.py",
    "src/institutional_primitives/parallel_execution.py",
    "src/institutional_primitives/performance_optimization.py",
    "src/institutional_primitives/plugin_interface.py",
    "src/institutional_primitives/primitives.py",
    "src/institutional_primitives/registry.py",
    "src/institutional_primitives/revision_node.py",
    "src/institutional_primitives/role_customization.py",
    "src/institutional_primitives/service_adapters.py",
    "src/institutional_primitives/workflow_engine.py",
    "src/institutional_primitives/workflow_templates.py",
    "src/kernel/enhanced_llm_interface.py",
    "src/kernel/llm_scheduler.py",
    "src/kernel/ollama_llm.py",
    "src/memory_bank_tools.py",
    "src/protocols/turn_manager.py",
    "src/real_debate_system.py",
    "src/real_demo_system/call_verification.py",
    "src/real_demo_system/consensus_visualization.py",
    "src/real_demo_system/demo_analyzer.py",
    "src/real_demo_system/demo_system_integration_test.py",
    "src/real_demo_system/demo_types.py",
    "src/real_demo_system/evolution_visualization.py",
    "src/real_demo_system/intelligent_collaboration_system.py",
    "src/real_demo_system/interactive_demo_flow.py",
    "src/real_demo_system/knowledge_graph_visualizer.py",
    "src/real_demo_system/llm_integration_service.py",
    "src/real_demo_system/llm_optimization_adapter.py",
    "src/real_demo_system/memory_agent_validator.py",
    "src/real_demo_system/multi_role_debate_system.py",
    "src/real_demo_system/personalized_recommendation_engine.py",
    "src/real_demo_system/real_demo_controller.py",
    "src/real_demo_system/real_llm_debate_executor.py",
    "src/real_demo_system/real_llm_executor.py",
    "src/real_demo_system/real_llm_integrator.py",
    "src/real_demo_system/real_time_conflict_monitor.py",
    "src/real_demo_system/real_time_consensus_monitor.py",
    "src/real_demo_system/real_time_wiki_updater.py",
    "src/real_demo_system/real_workflow_executor.py",
    "src/real_demo_system/scenario_manager.py",
    "src/real_demo_system/step_executor.py",
    "src/real_demo_system/transparency_monitor.py",
    "src/real_demo_system/transparent_conflict_resolution.py",
    "src/real_demo_system/user_interaction_manager.py",
    "src/real_demo_system/wiki_knowledge_system.py",
    "src/real_llm_debate_assistant.py",
    "src/unified_tool_manager.py",
    "src/user_interface/cli_interface.py",
    "src/user_interface/configuration_manager.py",
    "src/user_interface/feedback_collector.py",
    "src/user_interface/interactive_controller.py",
    "src/user_interface/parameter_manager.py",
    "src/user_interface/progress_monitor.py",
    "src/user_interface/result_formatter.py",
    "src/user_interface/transparency_controller.py",
    "src/user_interface/workflow_customizer.py",
    "src/user_interface/workflow_steering.py",
    "src/virtual_role_chat/chat_room_manager.py",
    "src/virtual_role_chat/cognitive_agent/agent.py",
    "src/virtual_role_chat/cognitive_agent/belief.py",
    "src/virtual_role_chat/cognitive_agent/epistemology.py",
    "src/virtual_role_chat/cognitive_agent/memory.py",
    "src/virtual_role_chat/cognitive_agent/metacognition.py",
    "src/virtual_role_chat/cognitive_agent/reasoning.py",
    "src/virtual_role_chat/config_validator.py",
    "src/virtual_role_chat/context_optimizer/dynamic_adapter.py",
    "src/virtual_role_chat/context_optimizer/models.py",
    "src/virtual_role_chat/context_optimizer/optimizer.py",
    "src/virtual_role_chat/context_optimizer/strategies.py",
    "src/virtual_role_chat/institutional_primitives/registry.py",
    "src/virtual_role_chat/role_validator.py",
    "src/virtual_role_chat/sskg/manager.py",
    "src/virtual_role_chat/sskg/models.py",
    "src/virtual_role_chat/sskg/storage.py",
    "src/virtual_role_chat/workflow_engine/engine.py",
    "src/virtual_role_chat/workflow_engine/execution_manager.py",
    "src/virtual_role_chat/workflow_engine/models.py",
    "src/virtual_role_chat/workflow_engine/state_manager.py",
    "src/workflows/knowledge_integration_decorator.py",
    "src/workflows/multi_perspective_workflow.py",
    "src/working_intelligent_assistant.py",
]

def file_has_conflict_markers(file_path):
    """Check if a file contains conflict markers."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return "<<<<<<< HEAD" in content or "=======" in content or ">>>>>>> " in content
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

def restore_file_from_commit(file_path, commit):
    """Restore a file from a specific commit."""
    try:
        subprocess.run(["git", "checkout", commit, "--", file_path], check=True, capture_output=True)
        print(f"Restored {file_path} from {commit}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to restore {file_path} from {commit}: {e}")
        return False

def main():
    # Get the list of files that have conflicts
    files_to_process = []
    
    # Check if files in the list actually have conflicts
    for file_path in files_with_conflicts:
        if file_has_conflict_markers(file_path):
            files_to_process.append(file_path)
    
    print(f"Found {len(files_to_process)} files with conflicts.")
    
    # Try to restore each file from fa881da
    commit = "fa881da"
    restored_files = []
    failed_files = []
    
    for file_path in files_to_process:
        print(f"Processing {file_path}...")
        if restore_file_from_commit(file_path, commit):
            restored_files.append(file_path)
        else:
            failed_files.append(file_path)
    
    print(f"\nRestored {len(restored_files)} files from {commit}.")
    print(f"Failed to restore {len(failed_files)} files from {commit}.")
    
    # Add restored files to git
    if restored_files:
        try:
            subprocess.run(["git", "add"] + restored_files, check=True, capture_output=True)
            print("Added restored files to git.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to add restored files to git: {e}")
    
    # Print failed files for manual handling
    if failed_files:
        print("\nFiles that failed to restore (need manual conflict resolution):")
        for file_path in failed_files:
            print(f"  {file_path}")

if __name__ == "__main__":
    main()
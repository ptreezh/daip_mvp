# RAG-First Answers and Tool Precheck Specification

## Overview
- Prioritize local knowledge (RAG) before LLM free-form generation
- Precheck tool existence/permission during evaluation; never execute non-existent tools
- Confidence-driven reflection and collaboration (threshold=0.85, max_reflections=2)

## Requirements
1. RAG-first
- Search local knowledge base each turn before generation: top_k=5, min_score=0.6
- Inject snippets + sources into prompt; cap by max_tokens_for_context
- Show sources in UI and include source list in events for observability
2. Tool precheck + whitelist
- In EVALUATING, after parsing tool call, verify: registered ∧ allowed by policy ∧ in role whitelist
- If check fails: emit ThoughtEvent(reason) and continue; do not enter EXECUTING_TOOL
- Prompt contains "Available Tools" with names + param keys; model must choose from list
- ask policy requires explicit user confirmation; deny is ignored; allow executes
3. Tool instruction generation policy
- Generate tool calls only if confidence<0.85 or RAG suggests external action
- If no suitable tool, propose alternatives instead of erroring
4. Confidence + reflection
- Confidence<0.85 triggers reflection; up to 2 times
- Consecutive low confidence or no RAG hits prompts a user-collaboration suggestion

## Design (KISS, YAGNI, SOLID)
- Single injection point: MemoryService.construct_prompt adds RAG snippets + tool whitelist
- Single precheck point: AgentExecutor EVALUATING stage performs registry/permission check
- Whitelist source: registered ∩ policy-allowed ∩ role-allowed
- Interfaces: keep KnowledgeManager.search usage behind IKnowledgeManager; ToolManager exposes has_tool/list_tools; config via Pydantic

## Configuration
- rag.enabled (default true), rag.top_k=5, rag.min_score=0.6, rag.max_ctx_tokens
- confidence.threshold=0.85, max_reflections=2

## Events/Observability
- ThoughtEvent includes: rag_hits, sources[], tool_ignored_reason
- TokenUsage/ModelMetrics unchanged

## TDD Task List
1. Prompt includes RAG when enabled
- Test: with hits, prompt contains "RAG Snippets" and file paths
- Test: with no hits, no RAG section
- Impl: call knowledge_manager.search, filter by min_score, truncate by tokens
2. RAG config honored
- Test: top_k/min_score affect results; max_ctx_tokens truncates
- Impl: read from config and apply
3. Tool whitelist in prompt
- Test: prompt lists Available Tools with param keys
- Impl: export from ToolManager + role config; inject into prompt
4. Evaluation-time tool precheck
- Test: unknown/denied tool -> ThoughtEvent, no EXECUTING_TOOL, dialogue continues
- Impl: Executor checks has_tool + permission + role whitelist; skip on failure
5. Permission ask flow
- Test: ask -> PermissionRequestEvent; confirm executes; reject continues without failure
- Impl: handle ToolPermissionRequest and branch accordingly
6. Confidence 0.85 reflection
- Test: content with Confidence <0.85 triggers reflection; after 2 reflections suggest collaboration
- Impl: adjust threshold and counters
7. Observability metadata
- Test: events include rag_hits and sources; tool_ignored_reason present when applicable
- Impl: extend ThoughtEvent content/message construction only (no schema change)
8. Config models and DI
- Test: config.yaml loads rag and confidence fields; container wiring passes them
- Impl: extend Pydantic models + Container
9. Regression safety
- Test: with rag.disabled and no tools, legacy flow completes normally
- Impl: ensure defaults preserve old behavior

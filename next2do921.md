**Current Task: Test TUI Debate Model Switching**

**Goal:** Verify TUI debate supports per-role model selection end-to-end.

**Status:** Completed.

**Findings & fixes today:**
- DI duplication fixed: TUI now uses container.role_model_manager() to avoid a second empty instance (src/daip_live/tui.py:274-277); EnhancedDebateManager injected from container.
- Mapping bug fixed: mapping.role_model_config used in TUI instead of non-existent mapping.model_config (src/daip_live/tui.py:972-983).
- Flaky test root cause: debate completes too fast with local mock/ollama models, sleep-based assertions miss intermediate states.

**TDD plan:**
1) Red: Update e2e test to be event-driven (await TUI events) and expect role→model switches: tech_analyst→qwen3:8b, pro_arguer→llama3:instruct.
2) Green: Add asyncio.Events in TUI for debate lifecycle and participant turns, plus wait_* helpers (wait_debate_started, wait_participant, wait_debate_completed).
3) Refactor test to await those events and internal state snapshots.

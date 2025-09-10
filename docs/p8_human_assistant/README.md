---
id: P8
title: Workflow Orchestration Engine
status: Rewritten
architecture_drivers: [SOLID, YAGNI, KISS]
---

# P8: Workflow Orchestration Engine

## 1. Principle-Driven Refactoring

This specification has been rewritten to clarify the relationship between the `P5` Agent Engine and the `P8` Orchestrator, and to simplify the initial implementation scope.

-   **SOLID (SRP & Dependency Inversion)**: The responsibilities are now clear. `P5` is the **Worker** (executes a single agent's goal). `P8` is the **Project Manager** (orchestrates multiple `P5` workers to complete a complex, multi-step workflow).
-   **YAGNI**: We do not need to implement all conceivable workflows at the start. The core task is to build the **workflow engine**. We will implement only one simple, representative workflow initially to prove the engine works.
-   **KISS**: The "activation mode" concept is retained to hide this complexity from the user until it is explicitly requested.

## 2. Overview

This package provides the `WorkflowOrchestrator`, a top-level controller that operates when the user enters an "assistant-active" mode. It reads declarative workflow definitions and uses `P5` agent instances to execute them, enabling multi-agent and human-in-the-loop collaboration.

## 3. Core Architecture

1.  **Workflow Definition**: A workflow is defined as a declarative YAML file. This file lists the sequence of steps, the `role` required for each step, and how the output of one step becomes the input for the next.
2.  **Orchestration Engine**: The `WorkflowOrchestrator` parses the YAML. For each step, it instantiates a `P5.AgentExecutor` with the specified `role` and a tailored context, then calls its `run()` method with the goal for that step.
3.  **Human in the Loop**: A step in the workflow YAML can be flagged as `requires_approval: true`. When the orchestrator reaches this step, it pauses and yields a `human_approval_request` event, waiting for an external confirmation from the UI layer before proceeding.

## 4. Example Workflow: `Write-and-Review` (Initial Scope)

To satisfy the YAGNI principle, we will only implement this single workflow to begin with.

**`write_and_review.yaml`:**
```yaml
name: "Write and Review Document"
description: "A writer agent drafts a document, then a critic agent reviews it."
steps:
  - name: "Drafting"
    role: "Writer"
    goal: "Write a document about {topic} based on the provided context."
    inputs: ["topic", "context"]
    outputs: ["draft_document"]

  - name: "Reviewing"
    role: "Critic"
    goal: "Review the following draft document and provide feedback for improvement."
    inputs: ["draft_document"]
    outputs: ["feedback"]
    requires_approval: true # Human must approve before the review starts

  - name: "Finalizing"
    role: "Writer"
    goal: "Incorporate the following feedback into the original draft to create the final version."
    inputs: ["draft_document", "feedback"]
    outputs: ["final_document"]
```

## 5. Task List (TDD)

-   **Workflow Definition**: Define Pydantic models in `P0` for parsing the workflow YAML files.
-   **Orchestrator Engine**:
    1.  Write a test to load and parse a valid workflow YAML.
    2.  Write a test for the orchestrator to execute the `Drafting` step of the `Write-and-Review` workflow. This test will mock the `P5.AgentExecutor` and assert it was called with the correct `role` ("Writer") and `goal`.
    3.  Implement the basic, single-step execution logic.
    4.  Write a test to verify that the output of the first step is correctly passed as input to the second step.
    5.  Write a test for the `requires_approval` flag, asserting that the orchestrator yields the correct event and pauses execution.
    6.  Implement the full sequential workflow execution logic.

## 6. Key Architectural Decisions & Open Issues

-   **Decision (YAGNI)**: The scope is limited to building the workflow engine and the single `Write-and-Review` workflow. Other workflows (`Debate`, `SOP`, etc.) are deferred.
-   **Decision (SOLID)**: P8 is established as a meta-controller that *uses* P5 instances. P8 does not contain any core agent "thinking" logic itself.
-   **Open Issue (P0)**: The Pydantic models for `Workflow`, `Step`, and the `human_approval_request` `AgentEvent` must be formally defined.
-   **Open Issue (P5)**: The `P5.AgentExecutor` needs to be initializable with a specific context/goal and must reliably return its final result upon completion, making it suitable for use by the orchestrator.

## 7. Implementation Status

-   **Overall Status**: This work package is currently in the **Planned** phase. No implementation has started yet.
-   **Workflow Definition**: The Pydantic models for workflow definition are pending creation in `P0`.
-   **Orchestrator Engine**: No code has been written for the `WorkflowOrchestrator`.
-   **Example Workflow**: The `Write-and-Review` example workflow is conceptual and not yet implemented.
-   **Dependencies**: The implementation of this package depends on the completion and stability of `P5` (Agent Engine) and the formalization of `AgentEvent` models in `P0`.

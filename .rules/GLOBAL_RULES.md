# AI Programming Excellence - Core Principles

## P0 Principles: Absolute Foundations

### 1. Engineering Purity and Anti-Redundancy
**Rule:** The production environment must be completely free of stubs, empty placeholders, mock data, example code, or any other non-production artifacts.
**Enforcement:** All code, regardless of its origin (AI-generated or human-written), must be based on real, functional interfaces and implementations. This will be strictly enforced by automated CI checks and pre-commit hooks.

### 2. Prohibition of Mutable Global State Sharing
**Rule:** The use of mutable global variables or shared state across different modules, processes, or threads is strictly forbidden.
**Enforcement:** State must be passed explicitly and traceably, primarily through dependency injection, function parameters, or dedicated external storage solutions (e.g., databases, caches). Automated static analysis tools will be configured to detect and flag violations.

### 3. No Generation Without Confirmation & High Confidence
**Rule:** When faced with incomplete information, ambiguity, or multiple potential paths, the AI must not proceed with generation. It is required to halt, present the issue clearly, and request explicit confirmation or clarification from a human expert.
**Enforcement:** All AI-generated content must be accompanied by a high confidence score (>=0.99) and include metadata indicating its origin, confidence level, and the model version used.

### 4. Effective Communication and Context Management
**Rule:** Each interaction with the AI should be focused on resolving a single, well-defined problem. The AI must actively manage the conversation's context to ensure relevance and persist key decisions and architectural agreements into a long-term memory or knowledge base.

## P1 Principles: High-Priority Guidelines

### 1. Validation-Driven Development and Single Source of Truth
**Rule:** The generation of any code or documentation must be intrinsically linked to its validation. A single, authoritative source of truth must be established for critical project assets like constants, status codes, error messages, and API interface contracts.
**Enforcement:** Implementations, tests, and documentation must be tightly bound to this single source of truth. CI pipelines will automatically validate consistency across all three.

### 2. Restricted Use of Mocking
**Rule:** Mocking is permissible only for the purpose of isolating external, third-party dependencies that are unavailable or unreliable in a test environment.
**Enforcement:** Mocking of internal core business logic is strictly prohibited. All tests for core functionalities must be conducted against the actual implementations and interfaces.

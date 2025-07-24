# Requirements Document

## Introduction

This feature implements a comprehensive virtual role chat system based on "制度原语 (Institutional Primitives)" - standardized workflow nodes that encapsulate atomic capabilities like fact extraction, opinion synthesis, and voting. These primitives serve as the fundamental building blocks that constitute all social institutions within the system.

### Core Principles

1. **认知独立性 (Cognitive Independence)**: Virtual roles must possess the highest level of cognitive independence, functioning as autonomous cognitive agents rather than mere role-playing simulations. Each agent maintains its own reasoning framework, belief system, epistemology, and meta-cognitive capabilities.

2. **任务聚焦 (Task Focus)**: Every interaction must maintain high focus on the current task through sophisticated context optimization and meta-cognitive guidance, ensuring efficient and effective problem-solving.

3. **集体智慧涌现 (Collective Intelligence Emergence)**: The system must facilitate the emergence of collective intelligence that transcends individual capabilities through cognitive diversity, perspective complementarity, and advanced consensus mechanisms.

The system implements two core "social institutions" as workflow-based solutions:

1. **批判性审查工作流 (Critical Review Workflow)**: A systematic approach to combat LLM hallucinations through multi-role fact validation, epistemological verification, and evidence-based revision processes.

2. **多视角综合工作流 (Multi-perspective Synthesis Workflow)**: A comprehensive framework to overcome single-LLM perspective limitations by orchestrating diverse expert viewpoints with true cognitive independence into synthesized knowledge.

The implementation leverages existing DAIP-LIVE components (FactExtractionService, SynthesisEngine, WikiService, etc.) as institutional primitives while introducing a workflow orchestration layer that enables complex social engineering approaches to AI collaboration and knowledge validation.

The system implements a unified Semantic Structured Knowledge Graph (SSKG) as the central memory interface for all components, and incorporates a MemAgent-based memory management system inspired by ByteDance/Tsinghua research to optimize long-context interactions and memory retrieval across multi-conversation workflows.

## Requirements

### Requirement 1: 制度原语系统 (Institutional Primitives System)

**User Story:** As a developer, I want to define and utilize standardized workflow nodes that encapsulate atomic capabilities, so that I can compose complex social institutions from reusable building blocks.

#### Acceptance Criteria

1. WHEN defining institutional primitives THEN the system SHALL provide standardized workflow node interfaces for fact extraction, opinion synthesis, voting, evidence collection, and consensus building
2. WHEN a primitive is executed THEN the system SHALL integrate seamlessly with existing services (FactExtractionService, SynthesisEngine, WikiService, etc.) while maintaining workflow state
3. WHEN primitives are composed THEN the system SHALL support sequential execution, parallel fan-out/fan-in patterns, and conditional branching based on confidence scores or validation results
4. WHEN workflow execution occurs THEN the system SHALL maintain transparent audit trails showing reasoning steps, evidence sources, and decision points
5. IF primitives require external data THEN the system SHALL provide standardized interfaces for tool integration and knowledge base access

### Requirement 2: 批判性审查工作流 (Critical Review Workflow)

**User Story:** As a user, I want to eliminate LLM hallucinations through systematic multi-role fact validation, so that I can trust the accuracy and reliability of generated content.

#### Acceptance Criteria

1. WHEN content is generated THEN the system SHALL execute a [生成节点] that captures the initial AI role output with full context and metadata
2. WHEN fact extraction is triggered THEN the system SHALL execute a [事实提取节点] using FactExtractionService to identify all verifiable factual assertions from the generated content
3. WHEN parallel review begins THEN the system SHALL execute [并行审查节点] with fan-out pattern to simultaneously deploy:
   - [审查者A节点]: A "批判者" role that challenges facts and seeks counter-evidence from WikiService and external tools
   - [审查者B节点]: A "验证者" role that searches for supporting evidence and corroborating sources
4. WHEN evidence collection completes THEN the system SHALL execute [证据汇总节点] with fan-in pattern to aggregate all positive and negative evidence with source attribution
5. WHEN consensus calculation occurs THEN the system SHALL execute [共识计算节点] using SynthesisEngine or voting algorithms to assign credibility scores to each factual assertion
6. WHEN revision is needed THEN the system SHALL execute [修订节点] to send low-credibility content back to the original "创作者" role with evidence-based revision requirements
7. IF the workflow completes successfully THEN the system SHALL persist validated facts to WikiService and maintain audit trails of the validation process

### Requirement 3: 多视角综合工作流 (Multi-perspective Synthesis Workflow)

**User Story:** As a user, I want to overcome single-LLM perspective limitations and create new knowledge through systematic multi-expert collaboration, so that I can generate comprehensive and insightful analysis on complex topics.

#### Acceptance Criteria

1. WHEN complex topic analysis begins THEN the system SHALL execute [任务分解节点] with a "规划者" role to decompose topics (e.g., "AI对就业的影响") into multiple sub-problems representing different perspectives (经济、社会、技术、伦理视角)
2. WHEN parallel exploration starts THEN the system SHALL execute [并行探索节点] to assign each sub-problem to specialized expert AI roles based on their domain expertise and knowledge profiles
3. WHEN expert analysis occurs THEN each expert role SHALL research and formulate viewpoints using available tools, knowledge bases, and their specialized reasoning capabilities
4. WHEN viewpoint collection completes THEN the system SHALL gather all expert perspectives, including conflicting or contradictory viewpoints, with supporting evidence and reasoning
5. WHEN synthesis begins THEN the system SHALL execute [观点综合节点] using SynthesisEngine to merge diverse and potentially conflicting viewpoints into a comprehensive, insightful, and nuanced synthesis report
6. IF synthesis quality is insufficient THEN the system SHALL iteratively refine the process by requesting additional expert input or deeper analysis on specific aspects
7. WHEN workflow completes THEN the system SHALL produce a final synthesis that demonstrates greater depth, breadth, and insight than any single expert perspective could achieve alone

### Requirement 4: 工作流编排引擎 (Workflow Orchestration Engine)

**User Story:** As a system architect, I want a robust workflow orchestration engine that can execute complex institutional workflows, so that I can implement sophisticated social engineering approaches to AI collaboration.

#### Acceptance Criteria

1. WHEN workflows are defined THEN the system SHALL support declarative workflow definitions with nodes, edges, conditions, and parallel execution patterns
2. WHEN workflows execute THEN the system SHALL maintain state management, handle failures gracefully, and provide rollback capabilities for critical operations
3. WHEN parallel execution occurs THEN the system SHALL coordinate fan-out and fan-in operations, manage resource allocation, and synchronize results across multiple AI roles
4. WHEN workflow monitoring is needed THEN the system SHALL provide real-time visibility into execution status, performance metrics, and bottleneck identification
5. IF workflows require external integration THEN the system SHALL provide standardized interfaces for tool execution, knowledge base access, and service communication
6. WHEN workflow templates are created THEN the system SHALL support parameterization, reusability, and version management for institutional workflow patterns
7. IF workflow execution fails THEN the system SHALL provide detailed error reporting, recovery suggestions, and audit trails for debugging and improvement

### Requirement 5: 用户交互界面 (User Interaction Interface)

**User Story:** As a user, I want intuitive interfaces to interact with institutional workflows, so that I can easily trigger, monitor, and control complex AI collaboration processes.

#### Acceptance Criteria

1. WHEN users initiate workflows THEN the system SHALL provide CLI commands and API endpoints to trigger Critical Review and Multi-perspective Synthesis workflows with customizable parameters
2. WHEN workflows execute THEN the system SHALL display real-time progress, intermediate results, and decision points through rich console output and optional web interfaces
3. WHEN user intervention is needed THEN the system SHALL support interactive prompts, parameter adjustments, and workflow steering without disrupting ongoing processes
4. WHEN workflows complete THEN the system SHALL present results in multiple formats (structured JSON, readable reports, visual summaries) with full traceability
5. IF users want to customize workflows THEN the system SHALL provide configuration options for role selection, evidence thresholds, synthesis strategies, and output formats
6. WHEN transparency is required THEN the system SHALL expose internal reasoning, confidence scores, evidence sources, and decision rationales at configurable detail levels
7. IF workflow results need validation THEN the system SHALL support user feedback, manual overrides, and iterative refinement of institutional processes

### Requirement 6: 知识管理集成 (Knowledge Management Integration)

**User Story:** As a knowledge worker, I want validated information from institutional workflows to be systematically captured and reused, so that I can build upon previous insights and maintain institutional memory.

#### Acceptance Criteria

1. WHEN facts are validated through Critical Review Workflow THEN the system SHALL automatically persist verified information to WikiService with confidence scores, evidence sources, and validation timestamps
2. WHEN synthesis is generated through Multi-perspective Synthesis Workflow THEN the system SHALL store comprehensive analysis results with expert attributions, supporting evidence, and synthesis rationale
3. WHEN knowledge conflicts arise THEN the system SHALL implement conflict resolution mechanisms that compare new findings with existing knowledge base entries and flag inconsistencies
4. WHEN cross-session knowledge sharing occurs THEN the system SHALL enable workflows to access and build upon previously validated facts and synthesis results from WikiService
5. IF knowledge updates are needed THEN the system SHALL support versioning, deprecation, and evolution of knowledge base entries with full audit trails
6. WHEN knowledge retrieval happens THEN the system SHALL provide semantic search capabilities that allow workflows to find relevant validated information based on topic similarity and expertise domains
7. IF knowledge quality assessment is required THEN the system SHALL maintain metrics on validation confidence, source reliability, and usage frequency for continuous knowledge base improvement

### Requirement 7: 可扩展性和定制化 (Extensibility and Customization)

**User Story:** As a developer, I want to create custom institutional primitives and workflows, so that I can adapt the system for domain-specific use cases and novel social engineering approaches.

#### Acceptance Criteria

1. WHEN defining custom primitives THEN the system SHALL provide plugin interfaces for creating new workflow nodes that integrate with existing services and maintain workflow state consistency
2. WHEN creating domain-specific workflows THEN the system SHALL support template-based workflow definition with parameterization for roles, thresholds, and processing strategies
3. WHEN integrating external services THEN the system SHALL provide standardized adapters for connecting new fact sources, validation services, and synthesis engines
4. WHEN customizing role behavior THEN the system SHALL support dynamic role configuration with custom prompts, expertise profiles, and interaction patterns
5. IF specialized consensus mechanisms are needed THEN the system SHALL allow registration of custom voting algorithms, evidence weighting strategies, and conflict resolution approaches
6. WHEN deploying custom configurations THEN the system SHALL validate workflow definitions, check service dependencies, and provide clear error reporting for configuration issues
7. IF performance optimization is required THEN the system SHALL support workflow profiling, bottleneck identification, and optimization recommendations for custom institutional processes

### Requirement 8: 统一语义结构化知识图谱 (Unified Semantic Structured Knowledge Graph)

**User Story:** As a system architect, I want a unified Semantic Structured Knowledge Graph (SSKG) as the central memory interface for all components, so that I can ensure consistent knowledge representation, efficient retrieval, and coherent reasoning across the entire system.

#### Acceptance Criteria

1. WHEN any component needs to store or retrieve knowledge THEN the system SHALL provide a unified SSKG interface that abstracts underlying storage mechanisms and ensures consistent data representation
2. WHEN facts are extracted or validated THEN the system SHALL automatically structure them in the SSKG with appropriate semantic relationships, confidence scores, and provenance metadata
3. WHEN knowledge is queried THEN the system SHALL support complex semantic queries that can traverse relationships, filter by confidence, and aggregate related information
4. WHEN new information conflicts with existing knowledge THEN the system SHALL implement versioning, conflict detection, and resolution strategies that maintain knowledge coherence
5. WHEN cross-component knowledge sharing occurs THEN the system SHALL ensure consistent access patterns and data formats across FactExtractionService, WikiService, and other knowledge consumers
6. IF knowledge needs to be organized hierarchically THEN the system SHALL support taxonomies, ontologies, and semantic categorization to enable efficient navigation and retrieval
7. WHEN knowledge evolves over time THEN the system SHALL maintain temporal metadata, track changes, and support time-based queries to understand knowledge evolution
8. WHEN any system component requires persistent storage THEN the system SHALL use SSKG as the unified storage mechanism for all memory types including virtual role memories, wiki content, user memories, session states, project states, and memory banks
9. IF specialized storage is needed THEN the system SHALL provide adapters that map domain-specific data structures to SSKG representations while maintaining semantic integrity
10. WHEN memory retrieval is needed THEN the system SHALL delegate to MemAgent for optimized memory selection and retrieval across the unified knowledge store

### Requirement 9: 记忆代理系统 (Memory Agent System)

**User Story:** As a user, I want an intelligent memory management system based on the MemAgent architecture, so that I can optimize long-context interactions and enable efficient memory retrieval across multi-conversation workflows.

#### Acceptance Criteria

1. WHEN conversations span multiple sessions THEN the system SHALL implement a MemAgent that maintains a unified memory representation across conversation boundaries
2. WHEN memory context exceeds practical limits THEN the system SHALL use reinforcement learning techniques to select the most relevant memories for the current context
3. WHEN memory retrieval is needed THEN the system SHALL implement multi-conversation memory retrieval strategies that consider recency, relevance, and importance
4. WHEN new information is processed THEN the system SHALL automatically organize memories into episodic, semantic, and procedural categories for optimized retrieval
5. WHEN memory consolidation occurs THEN the system SHALL implement background processes that summarize, index, and optimize memory representations for future retrieval
6. IF memory conflicts arise THEN the system SHALL implement resolution strategies that consider source reliability, temporal context, and confidence scores
7. WHEN memory is shared across roles THEN the system SHALL maintain appropriate access controls, attribution, and perspective management to preserve role integrity
8. WHEN retrieving memories from SSKG THEN the system SHALL use MemAgent's reinforcement learning-based selection mechanisms to optimize memory retrieval based on the ByteDance/Tsinghua research
9. WHEN storing memories in SSKG THEN the system SHALL use MemAgent to determine appropriate memory organization, importance scoring, and relationship mapping
10. IF multiple memory types exist in different contexts THEN the system SHALL use MemAgent to provide a unified interface for cross-context memory retrieval and utilization

### Requirement 10: 底层LLM接口集成的任务聚焦上下文优化 (Bottom-Layer LLM Interface Integration with Task-Focused Context Optimization)

**User Story:** As a system architect, I want task-focused context optimization to be integrated at the lowest level of LLM interactions, so that all AI communications automatically benefit from optimal context preparation without requiring higher-level components to manage this complexity.

#### Acceptance Criteria

1. WHEN any component makes an LLM call THEN the system SHALL automatically apply task-focused context optimization at the LLMInterface level without requiring explicit optimization requests
2. WHEN context optimization occurs THEN the system SHALL transparently detect task context from conversation messages and apply appropriate optimization strategies
3. WHEN context window size is limited THEN the system SHALL automatically compress and prioritize context elements based on task relevance before sending to the LLM
4. WHEN retrieving background information THEN the system SHALL proactively fetch relevant memories and knowledge from SSKG and MemAgent based on detected task requirements
5. WHEN multiple context sources are available THEN the system SHALL automatically blend task-specific instructions, relevant background knowledge, and essential conversation history in optimal proportions
6. IF task requirements change during a conversation THEN the system SHALL dynamically adjust context priorities in real-time without disrupting the conversation flow
7. WHEN context optimization is applied THEN the system SHALL maintain task coherence by preserving causal relationships and dependencies between context elements
8. IF multiple tasks exist in the context THEN the system SHALL automatically delineate task boundaries and prioritize the current active task
9. WHEN preparing multi-turn interactions THEN the system SHALL maintain consistent task framing across turns while incorporating new information seamlessly
10. IF higher-level components need optimization details THEN the system SHALL provide optimization metadata in LLM responses including compression ratios, included/excluded elements, and task focus information

### Requirement 11: 认知独立性与集体智慧涌现 (Cognitive Independence and Collective Intelligence Emergence)

**User Story:** As a user, I want virtual roles to possess true cognitive independence and collectively generate emergent intelligence, so that I can benefit from genuinely diverse perspectives and insights that transcend individual capabilities.

#### Acceptance Criteria

1. WHEN virtual roles are created THEN the system SHALL establish independent cognitive frameworks including reasoning systems, belief structures, epistemologies, and meta-cognitive capabilities for each role
2. WHEN roles engage in dialogue THEN the system SHALL ensure each maintains its cognitive independence rather than merely simulating surface-level personality traits
3. WHEN multiple roles analyze a problem THEN the system SHALL facilitate cognitive diversity by applying different reasoning frameworks and epistemological approaches
4. WHEN synthesizing perspectives THEN the system SHALL employ advanced consensus algorithms that preserve valuable cognitive diversity while resolving contradictions
5. WHEN knowledge creation occurs THEN the system SHALL enable emergent insights that demonstrably exceed what any individual role could produce
6. WHEN roles develop over time THEN the system SHALL maintain longitudinal cognitive consistency while allowing for belief updating based on new evidence
7. WHEN roles access shared knowledge THEN the system SHALL filter and interpret that knowledge through each role's unique cognitive framework
8. WHEN meta-cognitive guidance is needed THEN the system SHALL provide role-specific guidance that reinforces cognitive independence while maintaining task focus
9. WHEN evaluating system performance THEN the system SHALL measure both individual cognitive consistency and collective intelligence emergence
10. WHEN optimizing role interactions THEN the system SHALL maximize perspective complementarity and cognitive synergy

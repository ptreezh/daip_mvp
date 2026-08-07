# External Integrations

**Analysis Date:** 2026-08-07

## APIs & External Services

**LLM Providers:**
- LiteLLM - Unified API for multiple LLM providers
  - Models: OpenAI (gpt-3.5-turbo, gpt-4), Claude (claude-3-sonnet, claude-3-haiku), Gemini (gemini-pro)
  - Local: Ollama (llama3, mistral, codellama, phi, nomic-embed-text)
  - Config: `llm_provider` section in `config.yaml`

**Academic Services:**
- arXiv API - Paper search and download
  - Client: `arxiv` Python package
  - Usage: Paper metadata fetching, PDF downloads
- Google Scholar - Academic search
  - Client: `scholarly` package
  - Usage: Citation search, paper discovery

**MCP (Model Context Protocol) Servers:**
- markdownify - HTTP endpoint on localhost:8081
  - Auth: `MCP_MARKDOWNIFY_TOKEN` env var (optional)
  - Timeout: 15 seconds
- scihub - HTTP endpoint on localhost:8082
  - Auth: `MCP_SCIHUB_TOKEN` env var (optional)
  - Timeout: 15 seconds
- Config: `mcp` section in `config.yaml`

## Data Storage

**Databases:**
- SQLite (local file-based)
  - Connection: `database.path` in config.yaml (default: `daip_live.db`)
  - Client: SQLAlchemy 2.0+ ORM
  - Tables: sessions, dialogue_turns, knowledge_sources

**File Storage:**
- Local filesystem only (privacy-first design)
  - Knowledge base: `knowledge/` directory
  - Wiki pages: `knowledge/wiki/` directory
  - Papers: `knowledge/paper/arxiv/` directory
  - Debate logs: `knowledge/debate/` directory
  - Config: `config.yaml`

**Vector Storage:**
- FAISS (Facebook AI Similarity Search)
  - Index file: `knowledge/index.faiss`
  - Dimension: 384 (default embedding dimension)
  - Usage: Semantic search over knowledge base

**Caching:**
- None (stateless design with database persistence)

## Authentication & Identity

**Auth Provider:**
- Custom (no external auth)
  - Implementation: Local session management
  - Storage: SQLite sessions table
  - Session IDs: UUID-based

## Monitoring & Observability

**Error Tracking:**
- None (local logging only)

**Logs:**
- Python logging module
- Console output for TUI/CLI
- No centralized log aggregation

## CI/CD & Deployment

**Hosting:**
- Local execution only (no cloud hosting)
- Optional: FastAPI server for GUI (port configurable)

**CI Pipeline:**
- None detected (manual testing with pytest)

## Environment Configuration

**Required env vars:**
- `MCP_MARKDOWNIFY_TOKEN` - Optional MCP markdownify auth
- `MCP_SCIHUB_TOKEN` - Optional MCP scihub auth

**Secrets location:**
- `.env` file (git-ignored)
- Configured in `config.yaml` for non-sensitive settings

**Model Provider Configuration:**
- Default model: `ollama/llama3:latest` (configurable)
- Embedding model: `ollama/nomic-embed-text` (configurable)
- API keys: Set via environment variables for cloud providers

## Webhooks & Callbacks

**Incoming:**
- None (local system only)

**Outgoing:**
- None (local system only)

**Internal Events:**
- Agent events (thought, tool_call, tool_output, final_response, etc.)
- Debate events (debate_start, debate_round_start, debate_turn_complete, debate_complete)
- Permission events (permission_request, permission_response)
- Token usage tracking
- Model metrics

---

*Integration audit: 2026-08-07*

# MCP Integration TDD Plan

Test Matrix
- markdown_to_md
  - validates http/https URL
  - enforces allowed_domains
  - handles endpoint timeout/retry
  - writes .md to docs/markdown with safe path
  - logs execution (no secrets)
- fetch_paper
  - accepts arXiv ID and DOI
  - rejects unsupported sources
  - saves PDFs to docs/papers
  - caps file size; streams write
  - handles 404/permission errors

Unit Tests
- Validate inputs (empty, bad schema, domain not allowed)
- Config parsing (enabled flags, tokens from env)
- Permission gating (ToolPermissionConfig ask/deny/allow)
- Error mapping (DependencyError, ValidationError, ToolError)

Integration Tests
- Mock MCP client responses (success, timeout, error)
- CLI commands wire-through (daip mcp markdownify/fetch)
- TUI actions render status and artifacts

Non-Mocked Smoke
- If endpoints reachable (env-driven), run one real call for each MCP
- Skip gracefully if unreachable

Commands
- pytest -k "mcp or basic_tools"
- ruff check --fix; ruff format
- mypy src/daip_live --strict
- pre-commit run --all-files

Exit Criteria
- All tests passing; coverage includes happy-path and error-path
- Lint/typecheck clean
- Docs updated if interfaces change
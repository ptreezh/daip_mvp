# MCP Integration Spec

Scope
- Integrate two MCP servers: markdownify-mcp and Sci-Hub MCP, usable by roles and via CLI/TUI.
- Provide simple, composable tools that wrap MCP calls; adhere to KISS, SOLID, YAGNI.

Outcomes
- Role tools: markdown_to_md(url) and fetch_paper(identifier) with strict validation and permission gating.
- CLI/TUI: commands to call the above tools, show status, and persist outputs.

Constraints
- Defensive-only: no bypassing paywalls; respect copyright, licensing, and robots.
- Network timeouts: default 15s; retries: max 2; rate limit: 10 req/min per MCP.
- Input validation: URL schema http/https only; identifiers restricted to arXiv ID or DOI.
- Paths must pass existing _is_safe_path checks; never write outside workspace/roles/docs.

Configuration (config.yaml)
```
mcp:
  markdownify:
    endpoint: "http://localhost:PORT"
    auth:
      type: "none" # or "token"
      token_env: "MCP_MARKDOWNIFY_TOKEN"
    enabled: true
    timeout_seconds: 15
  scihub:
    endpoint: "http://localhost:PORT"
    auth:
      type: "none" # or "token"
      token_env: "MCP_SCIHUB_TOKEN"
    enabled: true
    timeout_seconds: 15
  permissions:
    default: "ask" # allow/deny/ask
    allowed_domains:
      - "arxiv.org"
      - "doi.org"
```

Interfaces (daip_live.basic_tools)
- markdown_to_md(url: str, options: dict | None = None) -> str
  - Validates URL; calls MCP markdownify; returns saved file path and brief summary.
- fetch_paper(identifier: str, save_dir: str | None = None) -> str
  - Validates identifier (arXiv ID or DOI); calls Sci-Hub MCP; saves PDF into docs/papers; returns path + metadata.

Role Integration
- Add both tools to register_basic_tools; ensure ToolPermissionConfig gates network ops.
- Expose tool metadata via get_tool_info.

CLI/TUI Integration
- CLI: `poetry run daip mcp markdownify <url>`; `poetry run daip mcp fetch <identifier>`.
- TUI: add actions under Tools → MCP; show progress, errors, and saved artifacts.

Error Handling
- Dependency: require endpoints reachable; fail fast with clear messages.
- Validation: reject unsupported sources; sanitize inputs.
- Observability: log tool_name, endpoint, duration, status; redact tokens.

Security
- No storage of tokens in logs or files; use env vars.
- Enforce allowed_domains; deny on mismatch.

Data Flow
- Request → MCP → response (markdown/PDF) → write to docs/ with safe paths → status in persistence.

Risks & Mitigations
- Endpoint unavailable: surface DependencyError; suggest configuration fix.
- Large file sizes: cap at 50MB; stream write; show warning.

Acceptance Criteria
- Tools callable from roles and CLI/TUI.
- Config-driven endpoints; permission system enforced.
- Tests pass (unit + integration); lint/typecheck pass.
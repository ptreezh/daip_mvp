# DAIP-LIVE Production-Readiness Assessment

> ⚠️ **状态声明（2026-08-09）**: 本文档为 2026-08-06 历史基线（35/100 为当时实测）。最新实测状态见 [`.planning/real_state_assessment_2026-08-09.md`](.planning/real_state_assessment_2026-08-09.md)（2026-08-09 修复后：ruff 0、测试 1738P、knowledge_sources 13 落盘、门禁 §6.1）。保留本文档作为历史审计轨迹。

**Date**: 2026-08-06  
**Project**: DAIP-LIVE (Dynamic AI-driven Project-execution LIVE system)  
**Path**: D:\DAIP\refactdoc  
**Branch**: gnhf/-055e31 (62 commits, remote origin/main)

---

## A. Production-Readiness Score & Verdict

**Score: 35/100**  
**Verdict: NOT READY**

### Reasoning (5 bullets max)

1. **Critical runtime failures**: SQLAlchemy 2.0 incompatibility (`session.dict()`) breaks all session persistence; hardcoded embedding dimension (384) breaks with any non-nomic embedding model.
2. **Silent data fabrication**: Enhanced debate manager swallows `ModelError` and returns fake success content — debate results can be entirely fabricated without user awareness.
3. **No observability**: Zero logging configuration (no `basicConfig`, `FileHandler`, `RotatingFileHandler`) — logs have nowhere to go in production; debugging is impossible.
4. **Test suite is theater**: 2224 tests collected but ~3961 mock references across 143 files (mock-to-nothing patterns); deliberate `pytest.fail()` TDD red test left in suite; no CI configuration whatsoever.
5. **Dead code masquerading as features**: `basic_tools` layer has 13 tools exported but only 2 actually invoked (in deprecated TUI); `p7_gui_v1/test/uat/runner.py` has syntax error blocking type-check.

---

## B. TOP 5 Blocking Issues (Ranked by Production Risk)

| Rank | Issue | Evidence | Why It Blocks | Minimal Fix |
|------|-------|----------|---------------|-------------|
| 1 | **SQLAlchemy 2.0 `session.dict()` removed** | E1: `persistence/database.py:39` | All session save/load fails at runtime on any SQLAlchemy ≥2.0 upgrade | Replace `session.dict()` with `session.model_dump()` (Pydantic v2) |
| 2 | **Hardcoded embedding_dim=384** | E2: `knowledge/manager.py:34` | Vector index creation fails silently with any embedding model ≠ nomic-embed-text (e.g., bge-small-en=384, text-embedding-3-small=1536) | Read dimension from `model_provider.get_embedding_dimension()` or config; validate on index load |
| 3 | **Silent ModelError swallowing → fake debate results** | E3: `p8_debate_system/enhanced_debate_manager.py:582-586` | Debate completes "successfully" with error message as content; user cannot distinguish real vs fabricated output | Remove try/except; let `ModelError` propagate; add UI-level error boundary that surfaces to user |
| 4 | **Zero logging infrastructure** | E9: 20+ modules use `logging.getLogger(__name__)` only | No logs in production; silent failures undebuggable; audit trail impossible | Add `logging.basicConfig` with `RotatingFileHandler` in `container.py` bootstrap; configure from `config.yaml` |
| 5 | **No CI / broken test trust** | E5: 2224 tests, ~3961 mocks, 0 CI config, red test in suite | Cannot gate merges; mock-heavy suite gives false confidence; syntax error in test code | Add minimal GitHub Actions (ruff, mypy, pytest); delete `test_real_model_integration_red.py`; fix `runner.py` syntax |

---

## C. Minimal Viable HYBRID Architecture Design

### Core Principle
**Local security gate + sanitization pipeline + multi-cloud delegation** — all review logic runs locally; cloud providers see only sanitized slices.

### Component Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│                        LOCAL MACHINE (TRUSTED)                      │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────────┐  ┌──────────────────────┐  │
│  │  Task Input  │──▶│  Security Gate   │──▶│  Sanitization Pipe   │  │
│  │  (User/API)  │  │  (Risk Classifier)│  │  (PII/Secret Strip)  │  │
│  └──────────────┘  └──────────────────┘  └──────────┬───────────┘  │
│                                                      │              │
│         ┌───────────────────────────────────────────┘              │
│         ▼                                                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              LOCAL EXECUTION ENGINE                          │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────────────────┐  │  │
│  │  │ Ollama  │ │ SQLite  │ │ FAISS   │ │ Agent Loop (P5)   │  │  │
│  │  │ (LLM)   │ │ (State) │ │ (RAG)   │ │ + Tool Manager    │  │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └───────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                    ▲                    ▲                          │
│                    │ Delegable?         │ Result                   │
│                    │ (Zero risk?)        │ (Verified)              │
└────────────────────┼────────────────────┼──────────────────────────┘
                     │                    │
         ┌───────────┴───────────┐        │
         ▼                       ▼        ▼
   ┌───────────┐           ┌───────────┐ ┌─────────┐
   │ Cloud A   │           │ Cloud B   │ │ Cloud N │
   │ (OpenAI)  │           │ (Anthropic)│ │ (Other) │
   └───────────┘           └───────────┘ └─────────┘
         ▲                       ▲           ▲
         │ Sanitized slice       │           │
         │ (no PII, no secrets,  │           │
         │  no local paths,       │           │
         │  no API keys)          │           │
         └───────────────────────┴───────────┘
```

### Data Flow

1. **Task enters** → Security Gate classifies risk (HIGH/MEDIUM/LOW) via rules engine (local YAML/JSON rules)
2. **HIGH** → Human confirmation required (blocking UI prompt)
3. **MEDIUM** → Auto-sanitize → local execution with audit log
4. **LOW** → Auto-sanitize → delegate to cloud provider pool (round-robin / cost-aware)
5. **Cloud response** → Sanitization validation (no unexpected data exfiltration) → merge into local context
6. **All paths** → Local agent loop continues; full audit trail in SQLite

### Sanitization Boundary (Concrete)

| Input Type | Sanitization Rule | Cloud-Visible |
|------------|-------------------|---------------|
| User prompt | Strip file paths, API keys, secrets (regex + LLM classifier) | ✅ Sanitized text only |
| RAG context | Replace local IDs with opaque tokens; strip PII via `presidio-analyzer` | ✅ Tokenized chunks |
| Tool calls | **Never** sent to cloud — tools execute locally only | ❌ Blocked |
| Model config | Only model name + params (no API keys, no local endpoints) | ✅ |
| Session history | Last N turns, PII-stripped, no tool results | ✅ |

### What Runs Where

| Component | Location | Reason |
|-----------|----------|--------|
| Security Gate / Risk Classifier | Local | Zero trust; rules are user-controlled |
| Sanitization Pipeline | Local | Secrets never leave machine |
| Agent Loop / Tool Execution | Local | Tools need FS/DB access |
| Embedding / RAG | Local | Knowledge base is private |
| LLM Inference (delegable tasks) | Cloud (multi-provider) | Cost/latency optimization for zero-risk tasks |
| LLM Inference (sensitive tasks) | Local (Ollama) | Privacy guarantee |

---

## D. KEEP vs DELETE Assessment

| Code Layer | Verdict | Rationale | Action |
|------------|---------|-----------|--------|
| `basic_tools/` (13 tools, `__init__.py`, `core.py`) | **DELETE** | Only 2 tools (`search_academic_papers`, `download_paper`) invoked in deprecated `tui/simplified_main.py`; no integration with agent loop or tool manager; dead weight | Delete entire `src/daip_live/basic_tools/`; remove from `pyproject.toml` deps (`arxiv`, `scholarly`, `python-docx` if unused elsewhere) |
| `tests/unit/test_real_model_integration_red.py` | **DELETE** | Deliberate `pytest.fail()` TDD artifact left in suite; tests nothing; pollutes test runs | Delete file |
| `tests/test_dependency_hang.py` | **DELETE** | 6 tests that only `assert True` after imports; zero behavioral coverage | Delete file |
| `p7_gui_v1/test/uat/runner.py` | **REPAIR** | Syntax error (f-string line break line 33) blocks mypy; UAT runner conceptually useful for GUI validation | Fix syntax; keep if GUI v1 is retained, else delete with `p7_gui_v1/` |
| `p7_gui_v1/` (entire legacy GUI) | **DELETE** | Superseded by `p7_gui/` (FastAPI-based); unmaintained; test syntax error | Archive to `archive/` if history needed; delete from `src/` |

**Keep**: All P1-P8 core modules, TUI (`tui/`), current `cli/`, `p7_gui/`, `p8_debate_system/` (after fixing E3), `memory/`, `permission/`, `security/`, `container.py`.

---

## E. Ordered Implementation Sequence (Phases to Production-Ready)

### Phase 0: Stabilize Foundation (Week 1) — *Exit: Clean build, basic logging*
| Deliverable | Exit Criteria |
|-------------|---------------|
| Fix `session.dict()` → `model_dump()` (E1) | `poetry run pytest tests/unit/persistence -v` passes |
| Make `embedding_dim` dynamic from model provider (E2) | `KnowledgeManager` loads index with any embedding model |
| Add `logging.basicConfig` + `RotatingFileHandler` in `container.py` bootstrap (E9) | Logs appear in `data/logs/daip_live.log` on `daip run` |
| Fix pyproject.toml `requires-python` for ruff compatibility (E6) | `poetry run ruff check src/` parses without error |

### Phase 1: Truth in Debate System (Week 1-2) — *Exit: No silent fabrication*
| Deliverable | Exit Criteria |
|-------------|---------------|
| Remove try/except swallowing `ModelError` in `enhanced_debate_manager.py:582-586` (E3) | `ModelError` propagates; TUI shows error to user |
| Add UI error boundary in TUI debate view | User sees "Model unavailable: {error}" not fake content |

### Phase 2: Dead Code Removal (Week 2) — *Exit: Lean codebase*
| Deliverable | Exit Criteria |
|-------------|---------------|
| Delete `basic_tools/`, `test_dependency_hang.py`, `test_real_model_integration_red.py` | `poetry run pytest` collects ≤2200 tests; no import errors |
| Archive/delete `p7_gui_v1/` | `src/daip_live/p7_gui_v1/` gone; no references remain |

### Phase 3: Test Suite Rehabilitation (Week 2-3) — *Exit: Trustworthy CI gate*
| Deliverable | Exit Criteria |
|-------------|---------------|
| Add minimal GitHub Actions (`.github/workflows/ci.yml`): ruff, mypy, pytest | `git push` → CI runs; fails on lint/type/test errors |
| Convert 5 highest-value integration tests from mock-heavy to real-component (DB, FAISS, Ollama) | 5 integration tests run against real services; marked `@pytest.mark.integration` |
| Delete/quarantine pure mock-to-nothing tests | Mock count reduced by ≥50%; coverage on real paths ≥60% |

### Phase 4: Hybrid Delegation MVP (Week 3-4) — *Exit: Cloud delegation works for LOW-risk tasks*
| Deliverable | Exit Criteria |
|-------------|---------------|
| Implement Security Gate (risk classifier: HIGH/MEDIUM/LOW) | Rules file `config/security_rules.yaml`; unit tests cover all 3 levels |
| Implement Sanitization Pipeline (PII/secret stripping + tokenization) | `presidio-analyzer` integration; round-trip test: local→cloud→local preserves semantics |
| Add cloud provider pool (OpenAI, Anthropic via LiteLLM) with cost-aware routing | `daip run` delegates summarization task to cloud; result merged; audit log entry created |

### Phase 5: Observability & Hardening (Week 4) — *Exit: Production-operable*
| Deliverable | Exit Criteria |
|-------------|---------------|
| Structured logging (JSON) + log rotation config in `config.yaml` | `data/logs/` has daily rotated JSON logs; `jq` query works |
| Health check endpoint (FastAPI `/healthz`) | `curl localhost:8000/healthz` returns `{status: "ok", checks: {...}}` |
| Graceful shutdown (SIGTERM handling) | `Ctrl+C` twice → clean DB close, index flush, log flush |

---

## F. Test Strategy for This Codebase

### Current State Assessment
- **2224 tests** but **~3961 mock references** across 143 files → mock-to-nothing dominant
- **Zero CI** → no gate on merge
- **Deliberate failing test** in suite → noise
- **Syntax error in test code** → mypy fails

### What to Do With Existing Suite

| Category | Action | Target |
|----------|--------|--------|
| Pure import/assert-True tests (`test_dependency_hang.py`, `module_test_base.py` mocks) | **DELETE** | -500 tests |
| TDD red tests left in suite (`test_real_model_integration_red.py`) | **DELETE** | -5 tests |
| Mock-heavy unit tests with no real assertions | **QUARANTINE** → move to `tests/quarantine/` | -800 tests |
| Integration tests using real DB/FAISS/Ollama | **KEEP & EXPAND** | +20 tests |
| E2E TUI tests (7 passing) | **KEEP** | 7 tests |

### New Tests That Matter (Priority Order)

1. **Contract tests** for Security Gate (risk classification rules)
2. **Round-trip tests** for Sanitization Pipeline (local→cloud→local semantic equivalence)
3. **Failure injection tests** for debate system (ModelError → user-visible error)
4. **Persistence tests** for session save/load with SQLAlchemy 2.0
5. **Embedding dimension compatibility** tests (3+ embedding models)

### Minimum CI Setup (Single-User Local Project)

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.11"}
      - run: pip install poetry && poetry install --with dev
      - run: poetry run ruff check src/
      - run: poetry run mypy src/
      - run: poetry run pytest -m "not integration" --tb=short
      - run: poetry run pytest -m "integration" --tb=short
        env:
          OLLAMA_HOST: http://localhost:11434  # optional, skip if unavailable
```

**Gate policy**: `ruff` + `mypy` + unit tests must pass on every push. Integration tests run nightly or on `integration` label.

---

## G. TOP 3 Failure Risks of Hybrid Local+Cloud Model & Mitigations

| Risk | Description | Mitigation |
|------|-------------|------------|
| **1. Sanitization Bypass / Data Exfiltration** | Bug in sanitizer leaks PII, secrets, local paths, or API keys to cloud provider | • **Defense in depth**: Regex + LLM classifier + `presidio-analyzer` triple-check<br>• **Allow-list only**: Cloud payload schema validated (Pydantic) — reject any unexpected fields<br>• **Audit log**: Every cloud request/response logged locally with hash; weekly manual review<br>• **Canary test**: Synthetic secret injected in test suite; CI fails if appears in cloud mock |
| **2. Cloud Provider Unavailability / Vendor Lock-in** | Single cloud provider down → delegable tasks stall; cost spikes; API changes break delegation | • **Multi-provider pool**: Round-robin across ≥3 providers (OpenAI, Anthropic, Groq, etc.)<br>• **Local fallback**: All delegable tasks have local Ollama equivalent; auto-failover on cloud error<br>• **Cost circuit breaker**: Per-provider daily budget; auto-switch to local when exceeded<br>• **Adapter pattern**: `CloudProvider` protocol; new providers added without core changes |
| **3. Semantic Drift in Delegated Results** | Cloud model returns subtly different output than local model would → downstream agent decisions diverge | • **Deterministic prompts**: Temperature=0 for delegated tasks; prompt templates version-controlled<br>• **Shadow mode**: Run same task locally + cloud in parallel for 100 tasks; diff outputs; alert on >5% semantic divergence (embedding cosine <0.95)<br>• **Human-in-the-loop for first N delegations**: User confirms cloud result before auto-accept<br>• **Regression test suite**: Golden master outputs for delegated task types; CI compares |

---

*Assessment complete. All claims grounded in verified evidence (E1-E10) and direct code inspection.*
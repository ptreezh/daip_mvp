import pytest

# Expect daip_live.security.permissions to provide PermissionEngine API per PERSONAL_PERMISSION_POLICY_MIN.md
from daip_live.security.permissions import PermissionEngine  # type: ignore


def test_rule_priority_and_default():
    eng = PermissionEngine(
        default="ask",
        rules=[
            {"match": "bash:rm *", "action": "deny"},
            {"match": "bash:git status", "action": "allow"},
            {"match": "write:*", "action": "ask"},
        ],
    )
    assert eng.decide("bash", "git status") == "allow"
    assert eng.decide("bash", "rm -rf /tmp") == "deny"
    assert eng.decide("write", "wiki/new.md") == "ask"
    assert eng.decide("unknown", "op") == "ask"


def test_sandbox_paths():
    eng = PermissionEngine(allowed_roots=["wiki", "docs"]) 
    assert eng.sandbox_ok("wiki/page.md")
    assert eng.sandbox_ok("docs/papers/a.pdf")
    assert not eng.sandbox_ok("/etc/passwd")

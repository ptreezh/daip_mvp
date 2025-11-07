import fnmatch
import os

class PermissionEngine:
    def __init__(self, default="ask", rules=None, allowed_roots=None):
        self.default = default
        self.rules = rules or []
        self.allowed_roots = allowed_roots or ["wiki", "roles", "workflows", "docs"]

    def decide(self, tool: str, args: str | None = None) -> str:
        query = f"{tool}:{args}" if args else tool
        for r in self.rules:
            if self._match(r.get("match", ""), query):
                return r.get("action", self.default)
        return self.default

    def sandbox_ok(self, path: str) -> bool:
        p = os.path.normpath(path)
        ap = os.path.abspath(p)
        for root in self.allowed_roots:
            rr = os.path.abspath(root)
            try:
                if os.path.commonpath([ap, rr]) == rr:
                    return True
            except Exception:
                continue
        return False

    def _match(self, pattern: str, text: str) -> bool:
        if not pattern:
            return False
        return fnmatch.fnmatch(text, pattern)

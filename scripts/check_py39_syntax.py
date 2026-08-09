"""Check all source files parse under Python 3.9 syntax semantics (CI gate, S1-1).

Python 3.12's parser accepts backslash escapes inside f-string expressions
(added in 3.12); running this check with feature_version=(3, 9) prevents
3.12-only syntax from silently slipping into the 3.9-3.12 compatible codebase.
"""

import ast
import pathlib
import sys

fails = []
for p in pathlib.Path("src").rglob("*.py"):
    try:
        ast.parse(
            p.read_text(encoding="utf-8"), filename=str(p), feature_version=(3, 9)
        )
    except SyntaxError as e:
        fails.append((str(p), e.lineno, e.msg))

if fails:
    for f in fails:
        print(f"INVALID 3.9 SYNTAX: {f[0]}:{f[1]}: {f[2]}")
    sys.exit(1)

print(
    f"py39 syntax check OK: all {len(list(pathlib.Path('src').rglob('*.py')))} files parse"
)

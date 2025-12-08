#!/usr/bin/env python3

from daip_live.cli import app
from typer.testing import CliRunner

runner = CliRunner()
result = runner.invoke(app, ['--help'])

print(f"Exit code: {result.exit_code}")
print(f"Output length: {len(result.output)}")
print(f"Contains 'pa': {'pa' in result.output}")
print(f"Contains '_0': {'_0' in result.output}")
print(f"Contains 'v': {'v' in result.output}")

if 'pa' in result.output:
    print("\nFound 'pa' in output:")
    # Find all occurrences of 'pa'
    import re
    matches = re.finditer(r'pa', result.output)
    for i, match in enumerate(matches):
        start = max(0, match.start() - 20)
        end = min(len(result.output), match.end() + 20)
        print(f"Occurrence {i+1}: {repr(result.output[start:end])}")

if 'v' in result.output:
    print("\nFound 'v' in output:")
    # Find all occurrences of 'v'
    import re
    matches = re.finditer(r'v', result.output)
    for i, match in enumerate(matches):
        start = max(0, match.start() - 20)
        end = min(len(result.output), match.end() + 20)
        print(f"Occurrence {i+1}: {repr(result.output[start:end])}")
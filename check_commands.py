#!/usr/bin/env python3

from daip_live.cli import app
from typer.testing import CliRunner
import re

runner = CliRunner()
result = runner.invoke(app, ['--help'])

print('Available commands:')
# Look for command patterns in the help output
commands_match = re.findall(r'^(\w+)\s+', result.output, re.MULTILINE)
for cmd in commands_match:
    if cmd not in ['Usage', 'Options', 'Commands']:
        print(f'  {cmd}')

print('\nChecking specific commands:')
test_commands = ['agent', 'config', 'knowledge', 'session', 'debate', 'role', 'project', 'run', 'sync']
for cmd in test_commands:
    exists = cmd in result.output
    print(f'  {cmd}: {"EXISTS" if exists else "MISSING"}')
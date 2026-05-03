# Qoder CLI CLI Documentation

## Overview
This document contains configuration and usage information for the Qoder CLI CLI tool within the Stigmergy system.

## Basic Information
- **CLI Name**: qodercli
- **Tool Name**: Qoder CLI
- **Installation Command**: `npm install -g @qoder-ai/qodercli`
- **Version Check**: `qodercli --version`

## Usage Patterns
The Qoder CLI CLI can be invoked in several ways:
1. Direct execution: `qodercli [arguments]`
2. Through Stigmergy coordination layer
3. Cross-CLI calls from other tools

## Cross-CLI Communication
To call Qoder CLI from another CLI tool:
```bash
# From any other supported CLI
use qodercli to [task description]
# or
call qodercli [task description]
# or
ask qodercli [task description]
```

## Configuration
This tool integrates with Stigmergy through hooks deployed to:
`C:\Users\Zhang\.qoder\hooks`

## Last Updated
2025-12-13T14:54:02.666Z

---
*This file is automatically managed by Stigmergy CLI*

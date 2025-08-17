# DAIP-LIVE Mandatory Rules System

## Overview

The DAIP-LIVE project enforces strict mandatory development rules to ensure code quality, consistency, and reliability. This system automatically validates all code changes against predefined standards before allowing commits or merges.

## 🚨 What Are Mandatory Rules?

Mandatory rules are non-negotiable development standards that must be followed by all contributors. These rules are automatically enforced through:

1. **Pre-commit hooks** - Block commits if rules are violated
2. **Continuous Integration** - Block merges if rules are violated
3. **Manual validation scripts** - For local testing before committing

## 📋 Mandatory Rules List

### 1. Code Quality Gates (CRITICAL)
- ✅ **Black formatting** - All code must be formatted with Black
- ✅ **Ruff linting** - Zero linting errors allowed
- ✅ **MyPy type checking** - Complete type hints required

### 2. File Headers (CRITICAL)
All Python files must include the standardized header:
```python
# -*- coding: utf-8 -*-
"""
@Time    : YYYY-MM-DD HH:MM:SS
@Author  : DAIP-LIVE Team
@File    : filename.py
@Description:
    [Purpose description]
"""
```

### 3. Type Annotations (CRITICAL)
- All functions must have complete type hints
- No generic `Any` types without justification
- Strict MyPy compliance required

### 4. Testing Requirements (CRITICAL)
- New code must have corresponding tests
- All tests must pass before committing
- Minimum 80% test coverage for new features

### 5. Documentation Standards (CRITICAL)
- Google-style docstrings for all public functions
- Module-level docstrings required
- Type hints considered part of documentation

### 6. Architecture Compliance (CRITICAL)
- Strict layered architecture adherence
- No cross-layer dependencies
- Dependency injection through `AppState` only

### 7. Pre-commit Hooks (CRITICAL)
- Pre-commit must be installed and configured
- All hooks must pass before committing
- Automatic formatting and linting enforced

### 8. Performance Standards (CRITICAL)
- Token efficiency optimization required
- Proper memory management
- Resource cleanup and error handling

### 9. Environment Standards (CRITICAL)
- Python 3.10+ only
- Poetry dependency management
- Proper configuration file usage

### 10. Quality Metrics (CRITICAL)
- Zero MyPy errors
- Zero Ruff warnings
- 100% Black formatting compliance
- Minimum 80% test coverage

## 🔧 How to Use

### Local Development

1. **Install pre-commit hooks** (one-time setup):
```bash
pre-commit install
```

2. **Validate before committing**:
```bash
# Quick validation
python mandatory_rules_checker.py

# Comprehensive validation
./validate_mandatory_rules.sh
```

3. **Fix violations**:
```bash
# Format code
black src/ tests/

# Fix linting
ruff check --fix src/ tests/

# Fix type hints
# (Manual process based on MyPy output)
```

### Pre-commit Integration

The system automatically runs checks when you attempt to commit:
```bash
git add .
git commit -m "your changes"
# Pre-commit hooks run automatically
```

If violations are found, the commit will be blocked with specific error messages.

### Continuous Integration

GitHub Actions automatically run mandatory rules checks on:
- All pushes to main and feature branches
- All pull requests
- Multiple Python versions (3.10, 3.11, 3.12)

## 📊 Reporting System

### Local Reports
The system generates detailed JSON reports:
```bash
# View latest report
cat mandatory_rules_report.json

# Report includes:
- Total violations count
- Critical violations breakdown
- Specific violation details
- Pass/fail status
- Timestamps
```

### CI/CD Reports
- **GitHub Actions**: Real-time validation results
- **PR Comments**: Automatic feedback on rule violations
- **Artifact uploads**: Detailed reports for each Python version

## 🚨 Violation Consequences

### Critical Violations
- **Blocked commits** - Cannot commit to repository
- **Blocked merges** - Cannot merge to main branch
- **Required remediation** - Must fix all issues before proceeding

### Warnings
- **Allowed but tracked** - Commits permitted but documented
- **Technical debt tracking** - Monitored for future resolution
- **Code review attention** - Highlighted during review process

## 🛠️ Troubleshooting

### Common Issues

1. **Black formatting failures**:
```bash
# Fix formatting
black src/ tests/
```

2. **Ruff linting failures**:
```bash
# Auto-fix where possible
ruff check --fix src/ tests/

# Manual fixes required for remaining issues
```

3. **MyPy type checking failures**:
```bash
# Check specific files
mypy src/your_file.py

# Add type hints based on error messages
```

4. **Missing file headers**:
```bash
# Add standardized header to all .py files
# Use the template provided in the rules
```

### Getting Help

1. **Check the report**: `mandatory_rules_report.json`
2. **Review CLAUDE.md**: Full rule documentation
3. **Run specific checks**: `python mandatory_rules_checker.py`
4. **Consult team**: For rule clarification or exceptions

## 🎯 Best Practices

### Before Committing
1. Run local validation: `python mandatory_rules_checker.py`
2. Fix all critical violations
3. Run tests to ensure functionality
4. Commit only when all checks pass

### During Development
1. Write tests alongside new code
2. Use proper type hints from the start
3. Follow Google docstring conventions
4. Maintain architectural layering

### Code Review
1. Check mandatory rules compliance
2. Verify test coverage
3. Ensure documentation completeness
4. Validate architectural consistency

## 🔄 Rule Updates

Rules are periodically updated based on:
- Team feedback and experience
- New best practices in Python development
- Project requirements evolution
- Performance optimization needs

### Proposing Rule Changes
1. Create issue with proposed change
2. Include justification and impact analysis
3. Get team consensus
4. Update documentation and tooling
5. Communicate changes to team

## 📈 Success Metrics

The mandatory rules system tracks:
- **Compliance rate**: Percentage of commits passing all rules
- **Violation trends**: Types and frequency of violations
- **Fix time**: Average time to resolve violations
- **Team adoption**: Usage of validation tools

## 🚀 Future Enhancements

Planned improvements:
- **IDE integration**: Real-time validation in editors
- **Automated fixes**: More sophisticated auto-correction
- **Performance metrics**: Token usage and optimization tracking
- **Learning system**: Adaptive rule enforcement based on team patterns

---

Remember: **Quality is not an act, it is a habit.** The mandatory rules system ensures that every contribution maintains the high standards expected of the DAIP-LIVE project.
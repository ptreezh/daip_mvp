# CI Configuration

This directory contains CI configuration files.

The CI pipeline includes:
1. Testing across multiple Python versions
2. Code formatting checks
3. Linting
4. Type checking
5. Security scanning

To set up CI for this project, create the following GitHub Actions workflow in `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11, 3.12]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install Poetry
      uses: snok/install-poetry@v1
      with:
        virtualenvs-create: true
        virtualenvs-in-project: true

    - name: Load cached venv
      id: cached-poetry-dependencies
      uses: actions/cache@v3
      with:
        path: .venv
        key: venv-${{ runner.os }}-${{ matrix.python-version }}-${{ hashFiles('**/poetry.lock') }}

    - name: Install dependencies
      if: steps.cached-poetry-dependencies.outputs.cache-hit != 'true'
      run: |
        poetry install --no-interaction

    - name: Run tests
      run: |
        poetry run pytest

    - name: Check code formatting
      run: |
        poetry run ruff format --check src/ tests/

    - name: Run linter
      run: |
        poetry run ruff check src/ tests/

    - name: Run type checking
      run: |
        poetry run mypy src/

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install bandit
      run: |
        pip install bandit

    - name: Run security scan
      run: |
        bandit -r src/ -f json -o bandit-report.json || true

    - name: Upload security report
      uses: github/codeql-action/upload-sarif@v2
      if: always()
      with:
        sarif_file: bandit-report.json
```
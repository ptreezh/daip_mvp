# CLI Tests

This directory contains comprehensive tests for the DAIP-LIVE CLI interface.

## Test Files

### `test_cli_commands.py`
Unit tests for CLI command implementations:
- **TestStartCommand**: Tests for the `start` command including validation, success/failure scenarios, and error handling
- **TestStatusCommand**: Tests for the `status` command and system health checks
- **TestRolesCommand**: Tests for the `roles` command and role listing functionality
- **TestHelpCommand**: Tests for the `help` command
- **TestCLIErrorHandling**: Tests for general CLI error handling and edge cases

### `test_cli_integration.py`
Integration tests for CLI-to-service interactions:
- **TestCLIServiceIntegration**: Tests CLI integration with backend services
- **TestCLIEventProcessing**: Tests CLI event processing and real-time display
- **TestCLIEndToEndIntegration**: End-to-end integration tests for complete CLI workflows

### `test_cli_error_scenarios.py`
Tests for CLI error scenarios and edge cases:
- **TestCLIErrorScenarios**: Various error conditions and input validation
- **TestCLIDebateHandlerErrorScenarios**: Error handling in debate handler
- **TestRunDebateCommandErrorScenarios**: Error scenarios in debate command execution
- **TestServiceHealthCheckErrorScenarios**: System health check error conditions
- **TestRoleListingErrorScenarios**: Role listing error scenarios
- **TestCLIEdgeCases**: Edge cases and boundary conditions

## Test Coverage

The tests cover:

1. **Command Functionality**:
   - All CLI commands (`start`, `status`, `roles`, `help`)
   - Command argument validation
   - Option parsing and parameter handling

2. **Integration with Backend Services**:
   - Service initialization and health checks
   - Role management and recommendations
   - Debate execution and event processing

3. **Error Handling**:
   - Input validation errors
   - Service connection failures
   - Permission and file system errors
   - Missing dependencies
   - Timeout and memory errors

4. **Edge Cases**:
   - Unicode input handling
   - Boundary value testing
   - Malformed data handling
   - Empty or invalid configurations

## Running the Tests

```bash
# Run all CLI tests
python -m pytest tests/cli/ -v

# Run specific test file
python -m pytest tests/cli/test_cli_commands.py -v

# Run with coverage
python -m pytest tests/cli/ --cov=src.cli --cov-report=html
```

## Test Requirements

The tests require the following requirements from the project specification:
- **Requirements 3.1, 3.2, 3.3**: CLI interface implementation and functionality
- **Requirements 2.1, 2.2, 2.3**: Test suite stabilization and interface consistency

All tests use proper mocking to isolate CLI functionality from backend services, ensuring fast and reliable test execution.
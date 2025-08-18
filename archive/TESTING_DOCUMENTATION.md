# DAIP-MVP Comprehensive Testing Documentation

## Overview

This document describes the comprehensive automated testing system for the DAIP-MVP project, designed to ensure all three main applications work correctly and cover all user scenarios from UserCase.txt.

## Three Main Applications

### 1. Personal Intelligence Hub
- **Port**: 8086
- **URL**: http://localhost:8086/hub
- **Script**: `personal_intelligence_hub/main_app.py`
- **Purpose**: Unified user interface with chat, task management, and wiki panels

### 2. FastAPI Backend
- **Port**: 8000
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/status
- **Script**: `src/main.py`
- **Purpose**: Core API services for all scenarios

### 3. Debate System
- **Port**: 8080
- **URL**: http://localhost:8080
- **Script**: `src/debate_system/app.py`
- **Purpose**: Multi-role debate and discussion system

## Test Scripts

### 1. Quick Test (`quick_test.py`)
**Purpose**: Basic connectivity test for all three applications
**Usage**: 
```bash
python quick_test.py
```
**Features**:
- Starts each application sequentially
- Tests basic HTTP connectivity
- Provides immediate feedback
- Keeps applications running for manual testing

### 2. Three Applications Test (`three_applications_test.py`)
**Purpose**: Comprehensive testing of the three main applications
**Usage**:
```bash
python three_applications_test.py
```
**Features**:
- Tests all three applications in parallel
- Health endpoint verification
- Core scenario testing
- Performance metrics
- Detailed report generation

### 3. Comprehensive Automated Testing (`comprehensive_automated_testing.py`)
**Purpose**: Full test suite covering all UserCase.txt scenarios
**Usage**:
```bash
python comprehensive_automated_testing.py
```
**Features**:
- Covers all 180+ test cases from UserCase.txt
- Parallel test execution
- Web-based UI testing with Selenium
- API endpoint testing
- Performance and security testing
- Detailed HTML and text reports

### 4. Test Runner (`test_runner.py`)
**Purpose**: Simple wrapper for comprehensive testing
**Usage**:
```bash
python test_runner.py
```

## Batch Scripts

### Windows
```bash
run_comprehensive_tests.bat
```

### Linux/Mac
```bash
./run_comprehensive_tests.sh
```

## Test Coverage

### Core Scenarios Tested

#### 1. Expert Consultation Scenario
- Multi-expert selection and matching
- Opinion collection and synthesis
- Consensus formation
- Wiki page generation

#### 2. Academic Research Scenario
- Research topic analysis
- Multi-perspective exploration
- Report generation (2000+ words)
- Citation and reference management
- PDF export functionality

#### 3. Industry Analysis Scenario
- Market analysis and trends
- Competitive landscape assessment
- SWOT analysis generation
- Report export capabilities

#### 4. Additional Scenarios
- Casual chat functionality
- Critical fact checking
- Document review and annotation
- Virtual team collaboration
- Institutional primitive creation
- Memory and context management
- Security and permissions
- Performance and scalability

## Test Categories

### P0 - Critical Path Tests
- Application startup and basic connectivity
- Static resource loading
- API endpoint availability
- Database connectivity

### P1 - Core Functionality Tests
- Chat and messaging systems
- Workflow execution
- Real-time communication
- User authentication

### P2 - Complete Scenario Tests
- End-to-end user workflows
- Multi-user collaboration
- File upload/download
- Report generation

### P3 - Performance and Security Tests
- Response time testing
- Concurrent user handling
- Security vulnerability testing
- Load testing

## Test Execution

### Prerequisites
1. Python 3.10+
2. Required dependencies:
   ```bash
   pip install -r test_requirements.txt
   ```
3. Chrome browser (for Selenium tests)
4. Ollama service running with required models

### Running Tests

#### Option 1: Quick Test
```bash
python quick_test.py
```

#### Option 2: Three Applications Test
```bash
python three_applications_test.py
```

#### Option 3: Comprehensive Test Suite
```bash
python comprehensive_automated_testing.py
```

#### Option 4: Using Batch Scripts
```bash
# Windows
run_comprehensive_tests.bat

# Linux/Mac
./run_comprehensive_tests.sh
```

### Test Reports

Test reports are generated in the `test_reports/` directory:
- `comprehensive_test_report_[timestamp].txt` - Detailed text report
- `three_applications_test_[timestamp].txt` - Three-app test results
- HTML reports with visual test results

## Test Configuration

### Environment Variables
- `TEST_ENVIRONMENT` - Set to 'development', 'testing', or 'production'
- `TEST_BROWSER` - Browser for Selenium tests (default: chrome)
- `TEST_TIMEOUT` - Default timeout for tests (default: 30 seconds)

### Configuration Files
- `test_config.json` - Test configuration settings
- `test_data/` - Test data and fixtures
- `test_expected_results/` - Expected test results

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   - Scripts automatically kill processes on required ports
   - Manual cleanup: `netstat -ano | findstr :8000` (Windows) or `lsof -i :8000` (Linux/Mac)

2. **Missing Dependencies**
   - Install test requirements: `pip install -r test_requirements.txt`
   - Ensure Chrome browser is installed for Selenium tests

3. **Application Startup Failures**
   - Check Python path and dependencies
   - Verify script paths are correct
   - Check application logs for errors

4. **Test Failures**
   - Review test reports in `test_reports/` directory
   - Check application logs
   - Verify network connectivity

### Debug Mode
Run tests with debug logging:
```bash
export PYTHONPATH=. python -m logging.DEBUG comprehensive_automated_testing.py
```

## Continuous Integration

The test suite is designed to run in CI/CD environments:
- Headless browser testing
- Parallel test execution
- Automated report generation
- Test result archiving

## Test Maintenance

### Adding New Tests
1. Add test case to `UserCase.txt`
2. Implement test method in appropriate test class
3. Update test documentation
4. Verify test coverage

### Updating Test Data
- Test data files in `test_data/` directory
- Expected results in `test_expected_results/` directory
- Version control for test data changes

## Performance Considerations

- Tests run in parallel where possible
- Resource cleanup between tests
- Timeout handling for long-running operations
- Memory usage monitoring

## Security Considerations

- Test data sanitization
- Secure credential handling
- API rate limiting during tests
- Vulnerability scanning integration

---

## Contact

For questions or issues with the testing system, please contact the DAIP-LIVE Team.
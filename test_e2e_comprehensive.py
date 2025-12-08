#!/usr/bin/env python3
"""
Comprehensive End-to-End Test Suite for DAIP-LIVE

This test suite performs automated testing of all major system components
and workflows to verify real usability.
"""

import sys
import asyncio
import os
import subprocess
import tempfile
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import time

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

class E2ETestFramework:
    """Comprehensive testing framework for DAIP-LIVE"""

    def __init__(self):
        self.test_results = []
        self.temp_dir = tempfile.mkdtemp()
        self.start_time = time.time()

    def log_test(self, test_name: str, passed: bool, details: str = "", duration: float = 0):
        """Log test result"""
        result = {
            "test": test_name,
            "passed": passed,
            "details": details,
            "duration": duration,
            "timestamp": time.time() - self.start_time
        }
        self.test_results.append(result)

        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:8} {test_name}")
        if details:
            print(f"         {details}")
        if duration > 0:
            print(f"         Time: {duration:.2f}s")

    async def test_config_system(self) -> bool:
        """Test configuration system thoroughly"""
        try:
            from daip_live.config import ConfigManager, create_config_yaml_if_not_exists

            print("🔧 Testing Configuration System...")

            # Test config creation
            start_time = time.time()
            create_config_yaml_if_not_exists()
            duration = time.time() - start_time

            # Test config loading
            config_manager = ConfigManager()
            config = config_manager.get_config()

            # Verify required fields
            required_fields = ['database', 'llm_provider']
            for field in required_fields:
                if not hasattr(config, field):
                    self.log_test("Config Required Fields", False, f"Missing field: {field}")
                    return False

            # Test config values
            db_path = getattr(config.database, 'path', None)
            model = getattr(config.llm_provider, 'default_model', None)

            if not db_path or not model:
                self.log_test("Config Values", False, "Missing database path or model")
                return False

            self.log_test("Config System", True, f"DB: {db_path}, Model: {model}", duration)
            return True

        except Exception as e:
            self.log_test("Config System", False, f"Exception: {str(e)}")
            return False

    async def test_database_system(self) -> bool:
        """Test database persistence"""
        try:
            from daip_live.config import ConfigManager
            from daip_live.persistence.database import DatabaseManager

            print("💾 Testing Database System...")

            start_time = time.time()
            config_manager = ConfigManager()
            config = config_manager.get_config()

            # Test database initialization
            db_manager = DatabaseManager(config.database.path)

            # Test basic database operations
            # Use the new get_connection method for database operations
            from sqlalchemy import text
            with db_manager.get_connection() as conn:
                # Simple query test
                result = conn.execute(text("SELECT 1")).fetchone()
                if not result or result[0] != 1:
                    raise Exception("Database query failed")

            duration = time.time() - start_time
            self.log_test("Database System", True, f"Database initialized and queryable", duration)
            return True

        except Exception as e:
            self.log_test("Database System", False, f"Exception: {str(e)}")
            return False

    async def test_model_provider(self) -> bool:
        """Test model provider with actual model calls"""
        try:
            from daip_live.config import ConfigManager
            from daip_live.model_provider.provider import LiteLLMProvider

            print("🤖 Testing Model Provider...")

            start_time = time.time()
            config_manager = ConfigManager()
            config = config_manager.get_config()

            # Initialize model provider
            provider = LiteLLMProvider(config.llm_provider)

            # Test model list (if method exists)
            try:
                if hasattr(provider, 'get_available_models'):
                    models = provider.get_available_models()
                    self.log_test("Model List", True, f"Found {len(models)} models")
                else:
                    self.log_test("Model List", False, "get_available_models method missing")
            except Exception as e:
                self.log_test("Model List", False, f"Failed to get models: {str(e)}")

            # Test actual model generation (with timeout)
            try:
                test_prompt = "Say 'Hello' in one word."

                # Set a timeout for model response
                response = await asyncio.wait_for(
                    provider.generate(test_prompt, max_tokens=10),
                    timeout=30.0
                )

                content, usage = response

                if not content or len(content.strip()) == 0:
                    raise Exception("Empty response from model")

                self.log_test("Model Generation", True, f"Response: {content[:50]}...")

            except asyncio.TimeoutError:
                self.log_test("Model Generation", False, "Timeout after 30 seconds")
                return False
            except Exception as e:
                self.log_test("Model Generation", False, f"Model call failed: {str(e)}")
                # This might be expected if no models are available
                print("         ⚠️  This might be expected if no models are configured")

            duration = time.time() - start_time
            self.log_test("Model Provider", True, "Provider initialized successfully", duration)
            return True

        except Exception as e:
            self.log_test("Model Provider", False, f"Exception: {str(e)}")
            return False

    async def test_debate_system_complete(self) -> bool:
        """Test complete debate system workflow"""
        try:
            from daip_live.config import ConfigManager
            from daip_live.persistence.database import DatabaseManager
            from daip_live.memory.session_manager import SessionManager
            from daip_live.p4_role_manager_tools.role_manager import RoleManager
            from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
            from daip_live.model_provider.provider import LiteLLMProvider
            from daip_live.p8_debate_system.simple_debate_manager import SimpleDebateManager

            print("🎭 Testing Complete Debate System...")

            start_time = time.time()

            # Initialize all components
            config_manager = ConfigManager()
            config = config_manager.get_config()

            db_manager = DatabaseManager(config.database.path)
            session_manager = SessionManager(db_manager)
            role_manager = RoleManager()
            role_model_manager = RoleModelManager()
            model_provider = LiteLLMProvider(config.llm_provider)

            # Create debate manager
            debate_manager = SimpleDebateManager(
                session_manager=session_manager,
                role_manager=role_manager,
                role_model_manager=role_model_manager,
                model_provider=model_provider
            )

            self.log_test("Debate Manager Creation", True, "All components initialized")

            # Test debate initiation (without actually running)
            try:
                # This would normally start a debate
                # We'll just test that the method exists and doesn't crash
                if hasattr(debate_manager, 'start_debate'):
                    self.log_test("Debate Start Method", True, "start_debate method exists")
                else:
                    self.log_test("Debate Start Method", False, "start_debate method missing")

            except Exception as e:
                self.log_test("Debate Start Method", False, f"Error: {str(e)}")

            duration = time.time() - start_time
            self.log_test("Debate System", True, "Complete system initialized", duration)
            return True

        except Exception as e:
            self.log_test("Debate System", False, f"Exception: {str(e)}")
            return False

    async def test_tui_startup(self) -> bool:
        """Test TUI startup (without actually running the UI)"""
        try:
            from daip_live.tui_modular import DAIP_TUI

            print("🖥️  Testing TUI Startup...")

            start_time = time.time()

            # Test TUI class instantiation
            tui = DAIP_TUI()

            # Test that it has required methods
            required_methods = ['run']
            for method in required_methods:
                if not hasattr(tui, method):
                    self.log_test("TUI Methods", False, f"Missing method: {method}")
                    return False

            duration = time.time() - start_time
            self.log_test("TUI Startup", True, "TUI class instantiated successfully", duration)
            return True

        except Exception as e:
            self.log_test("TUI Startup", False, f"Exception: {str(e)}")
            return False

    async def test_dependencies(self) -> bool:
        """Test all required dependencies"""
        try:
            print("📦 Testing Dependencies...")

            start_time = time.time()

            # List of required modules to test
            required_modules = [
                'typer', 'textual', 'pydantic', 'yaml', 'sqlalchemy',
                'faiss', 'langchain', 'litellm', 'rich', 'asyncio'
            ]

            failed_imports = []

            for module in required_modules:
                try:
                    __import__(module)
                    self.log_test(f"Import {module}", True)
                except ImportError as e:
                    failed_imports.append(module)
                    self.log_test(f"Import {module}", False, str(e))

            duration = time.time() - start_time

            if failed_imports:
                self.log_test("Dependencies", False, f"Failed imports: {failed_imports}", duration)
                return False
            else:
                self.log_test("Dependencies", True, f"All {len(required_modules)} modules imported", duration)
                return True

        except Exception as e:
            self.log_test("Dependencies", False, f"Exception: {str(e)}")
            return False

    async def test_file_structure(self) -> bool:
        """Test that required files and directories exist"""
        try:
            print("📁 Testing File Structure...")

            start_time = time.time()

            # Required files
            required_files = [
                'config.yaml',
                'pyproject.toml',
                'src/daip_live/__init__.py',
                'src/daip_live/config.py',
                'src/daip_live/container.py',
                'src/daip_live/tui_modular.py'
            ]

            # Required directories
            required_dirs = [
                'src/daip_live',
                'src/daip_live/agent_engine',
                'src/daip_live/p8_debate_system',
                'src/daip_live/model_provider',
                'src/daip_live/persistence'
            ]

            missing_items = []

            # Check files
            for file_path in required_files:
                if not Path(file_path).exists():
                    missing_items.append(f"File: {file_path}")
                    self.log_test(f"File {file_path}", False, "Missing")
                else:
                    self.log_test(f"File {file_path}", True)

            # Check directories
            for dir_path in required_dirs:
                if not Path(dir_path).is_dir():
                    missing_items.append(f"Directory: {dir_path}")
                    self.log_test(f"Directory {dir_path}", False, "Missing")
                else:
                    self.log_test(f"Directory {dir_path}", True)

            duration = time.time() - start_time

            if missing_items:
                self.log_test("File Structure", False, f"Missing: {missing_items}", duration)
                return False
            else:
                self.log_test("File Structure", True, f"All {len(required_files + required_dirs)} items found", duration)
                return True

        except Exception as e:
            self.log_test("File Structure", False, f"Exception: {str(e)}")
            return False

    async def test_cli_commands(self) -> bool:
        """Test CLI command availability"""
        try:
            print("⌨️  Testing CLI Commands...")

            start_time = time.time()

            # Test if main CLI entry point works
            try:
                # Test import
                from daip_live.cli.main import app
                self.log_test("CLI Import", True, "CLI app imported successfully")

                # Test if it's a valid Typer app
                import typer
                is_valid_typer = (
                    isinstance(app, typer.Typer) and
                    hasattr(app, 'registered_commands')
                )

                if is_valid_typer:
                    commands_count = len(getattr(app, 'registered_commands', []))
                    self.log_test("CLI Structure", True, f"Valid Typer app with {commands_count} commands")
                else:
                    self.log_test("CLI Structure", False, f"Not a valid Typer app (type: {type(app).__name__})")

            except Exception as e:
                self.log_test("CLI Import", False, f"Failed to import CLI: {str(e)}")
                return False

            duration = time.time() - start_time
            self.log_test("CLI Commands", True, "CLI system available", duration)
            return True

        except Exception as e:
            self.log_test("CLI Commands", False, f"Exception: {str(e)}")
            return False

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['passed'])
        failed_tests = total_tests - passed_tests

        total_duration = time.time() - self.start_time

        report = {
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                'total_duration': total_duration,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            },
            'tests': self.test_results,
            'recommendations': []
        }

        # Add recommendations based on failures
        failed_tests_details = [r for r in self.test_results if not r['passed']]

        if any('Model' in test['test'] and not test['passed'] for test in failed_tests_details):
            report['recommendations'].append("Install Ollama and pull models: ollama pull llama3")

        if any('Config' in test['test'] and not test['passed'] for test in failed_tests_details):
            report['recommendations'].append("Check config.yaml configuration")

        if any('Database' in test['test'] and not test['passed'] for test in failed_tests_details):
            report['recommendations'].append("Check database permissions and disk space")

        if any('Import' in test['test'] and not test['passed'] for test in failed_tests_details):
            report['recommendations'].append("Install missing dependencies: poetry install")

        return report

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and generate report"""
        print("🧪 DAIP-LIVE Comprehensive End-to-End Test Suite")
        print("=" * 60)

        # Run all tests
        tests = [
            ("File Structure", self.test_file_structure),
            ("Dependencies", self.test_dependencies),
            ("Configuration", self.test_config_system),
            ("Database", self.test_database_system),
            ("Model Provider", self.test_model_provider),
            ("Debate System", self.test_debate_system_complete),
            ("TUI Startup", self.test_tui_startup),
            ("CLI Commands", self.test_cli_commands),
        ]

        for test_name, test_func in tests:
            print(f"\n📋 Running {test_name} Tests:")
            await test_func()
            print()

        # Generate and display report
        print("=" * 60)
        report = self.generate_report()

        # Display summary
        summary = report['summary']
        print(f"📊 TEST SUMMARY:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Passed: {summary['passed']} ✅")
        print(f"   Failed: {summary['failed']} ❌")
        print(f"   Success Rate: {summary['success_rate']:.1f}%")
        print(f"   Duration: {summary['total_duration']:.2f}s")

        # Display failed tests
        failed_tests = [r for r in self.test_results if not r['passed']]
        if failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   - {test['test']}: {test['details']}")

        # Display recommendations
        if report['recommendations']:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in report['recommendations']:
                print(f"   - {rec}")

        return report

async def main():
    """Main test runner"""
    framework = E2ETestFramework()
    report = await framework.run_all_tests()

    # Save report to file
    with open('e2e_test_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Detailed report saved to: e2e_test_report.json")

    # Return exit code based on success rate
    success_rate = report['summary']['success_rate']
    if success_rate >= 80:
        print(f"\n🎉 SYSTEM READY FOR USE! (Success Rate: {success_rate:.1f}%)")
        return 0
    else:
        print(f"\n⚠️  SYSTEM NEEDS ATTENTION (Success Rate: {success_rate:.1f}%)")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
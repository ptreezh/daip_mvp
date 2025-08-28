import asyncio
import unittest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
import os
import shutil

from src.core_services.comprehensive_quality_validation_system import (
    ComprehensiveQualityValidator,
    QualityReport,
    ValidationLevel,
    QualityMetric,
    QualityScore,
    ValidationResult,
)
from src.core_services.performance_monitoring_system import PerformanceMonitoringSystem
from src.core_services.enterprise_error_handling_system import EnterpriseErrorHandler

class TestComprehensiveQualityValidator(unittest.TestCase):
    def setUp(self):
        self.mock_config = {"validation_levels": {"basic": {}, "standard": {}, "comprehensive": {}, "strict": {}}}
        self.validator = ComprehensiveQualityValidator(self.mock_config)

        self.mock_monitoring_system = AsyncMock(spec=PerformanceMonitoringSystem)
        self.mock_error_handler = MagicMock(spec=EnterpriseErrorHandler)
        self.validator.initialize(self.mock_monitoring_system, self.mock_error_handler)

        # Mock internal methods
        self.validator._collect_python_files = MagicMock(return_value=["src/test_file.py"])
        self.validator._validate_code_quality = AsyncMock(return_value=[
            ValidationResult(rule_id="CQ001", passed=True, score=1.0, message=""),
            ValidationResult(rule_id="CQ002", passed=False, score=0.0, message=""),
        ])
        self.validator.performance_validator.validate_performance = AsyncMock(return_value=[
            ValidationResult(rule_id="PV001", passed=True, score=1.0, message=""),
        ])
        self.validator.security_validator.validate_security = MagicMock(return_value=[
            ValidationResult(rule_id="SEC001", passed=True, score=1.0, message=""),
        ])
        self.validator._validate_error_handling = MagicMock(return_value=[
            ValidationResult(rule_id="EH001", passed=True, score=1.0, message=""),
        ])

    def test_validate_system_basic_level(self):
        async def run_test():
            report = await self.validator.validate_system(level=ValidationLevel.BASIC)

            self.assertIsInstance(report, QualityReport)
            self.assertGreater(report.overall_score, 0.0)
            self.assertIsInstance(report.quality_grade, QualityScore)
            self.assertEqual(len(report.validation_results), 5) # CQ001, CQ002, PV001, SEC001, EH001
            self.validator._collect_python_files.assert_called_once()
            self.validator._validate_code_quality.assert_called_once()
            self.validator.performance_validator.validate_performance.assert_called_once()
            self.validator.security_validator.validate_security.assert_called_once()
            self.validator._validate_error_handling.assert_called_once()

        asyncio.run(run_test())

    def test_collect_python_files(self):
        # Create dummy files for testing
        temp_src_dir = "temp_src_for_test"
        temp_src_sub_dir = os.path.join(temp_src_dir, "src")
        os.makedirs(os.path.join(temp_src_sub_dir, "sub_dir"), exist_ok=True)
        with open(os.path.join(temp_src_sub_dir, "file1.py"), "w") as f: f.write("pass")
        with open(os.path.join(temp_src_sub_dir, "file2.txt"), "w") as f: f.write("pass")
        with open(os.path.join(temp_src_sub_dir, "sub_dir", "file3.py"), "w") as f: f.write("pass")

        try:
            # Change current working directory to temp_src_dir for os.walk to work correctly
            original_cwd = os.getcwd()
            os.chdir(temp_src_dir)

            # Create a new instance of the validator for this test
            temp_validator = ComprehensiveQualityValidator(self.mock_config)
            python_files = temp_validator._collect_python_files()
            self.assertEqual(len(python_files), 2)
            self.assertIn(os.path.join("src", "file1.py"), python_files)
            self.assertIn(os.path.join("src", "sub_dir", "file3.py"), python_files)

        finally:
            # Restore original current working directory
            os.chdir(original_cwd)
            # Clean up dummy files
            shutil.rmtree(temp_src_dir)

if __name__ == "__main__":
    unittest.main()

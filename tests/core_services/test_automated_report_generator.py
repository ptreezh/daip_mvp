import asyncio
import unittest
from datetime import datetime
from pathlib import Path
import os
import shutil

from src.core_services.automated_report_generator import (
    AutomatedReportGenerator,
    ReportFormat,
    ReportRequest,
    ReportStatus,
    ReportType,
)

class TestAutomatedReportGenerator(unittest.TestCase):
    def setUp(self):
        self.output_dir = "test_reports"
        self.generator = AutomatedReportGenerator(output_dir=self.output_dir)

    def tearDown(self):
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

    def test_successful_report_generation(self):
        """Test successful report generation."""
        async def run_test():
            await self.generator.start()

            request = ReportRequest(
                request_id="test_request_1",
                report_type=ReportType.SESSION_SUMMARY,
                report_format=ReportFormat.HTML,
                template_id="session_summary",
                data_sources={"session_data": {"session_id": "session_123"}},
                parameters={},
                requested_by="test_user",
                requested_at=datetime.now(),
            )

            request_id = await self.generator.generate_report(request)
            self.assertEqual(request_id, "test_request_1")

            # Wait for the report to be generated
            await asyncio.sleep(5)

            status = await self.generator.get_report_status(request_id)
            result = status.get("result")
            self.assertEqual(status.get("status"), "completed")
            self.assertIsNotNone(result)
            self.assertEqual(result.get("status"), "completed")
            self.assertIsNotNone(result.get("file_path"))

            report_content = await self.generator.download_report(result.get("report_id"))
            self.assertIsNotNone(report_content)
            self.assertIn("Session Summary", report_content)

            await self.generator.stop()

        asyncio.run(run_test())

    def test_fallback_report_generation(self):
        """Test fallback report generation when template is not found."""
        async def run_test():
            await self.generator.start()

            request = ReportRequest(
                request_id="test_request_2",
                report_type=ReportType.SESSION_SUMMARY,
                report_format=ReportFormat.MARKDOWN,
                template_id="non_existent_template",
                data_sources={"session_data": {"session_id": "session_456"}},
                parameters={},
                requested_by="test_user",
                requested_at=datetime.now(),
            )

            request_id = await self.generator.generate_report(request)
            self.assertEqual(request_id, "test_request_2")

            # Wait for the report to be generated
            await asyncio.sleep(5)
            
            status = await self.generator.get_report_status(request_id)
            result = status.get("result")
            self.assertEqual(status.get("status"), "completed")
            self.assertIsNotNone(result)
            self.assertEqual(result.get("status"), "completed")
            self.assertEqual(result.get("metadata", {}).get("template_id"), "basic_summary")

            report_content = await self.generator.download_report(result.get("report_id"))
            self.assertIsNotNone(report_content)
            self.assertIn("<!DOCTYPE html>", report_content)


            await self.generator.stop()

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()

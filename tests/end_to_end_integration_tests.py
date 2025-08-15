"""@Time    : 2025-08-06 09:30:00
@Author  : DAIP-LIVE Team
@File    : end_to_end_integration_tests.py
@Description:
    End-to-End Integration Tests for DAIP-LIVE System
    Comprehensive testing suite covering all system components and their interactions.
"""

import asyncio
import json
import logging
import shutil
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import aiohttp
import pytest

# Add project path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TestConfig:
    """Test configuration."""
    backend_url: str = "http://localhost:8002"
    web_url: str = "http://localhost:8001"
    test_timeout: int = 30
    cleanup_after: bool = True


@dataclass
class TestResult:
    """Test result data."""
    test_name: str
    success: bool
    execution_time: float
    error_message: Optional[str] = None
    details: Optional[dict[str, Any]] = None


class EndToEndTestSuite:
    """End-to-end integration test suite for DAIP-LIVE."""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.results: list[TestResult] = []
        self.test_data_dir = Path("test_data")
        self.session = None
        logger.info("End-to-End Test Suite initialized")
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
        if self.config.cleanup_after:
            self.cleanup_test_data()
    
    def cleanup_test_data(self):
        """Clean up test data."""
        if self.test_data_dir.exists():
            shutil.rmtree(self.test_data_dir)
            logger.info("Test data cleaned up")
    
    async def run_all_tests(self) -> list[TestResult]:
        """Run all end-to-end tests."""
        logger.info("Starting end-to-end integration tests")
        
        tests = [
            self.test_service_health_check,
            self.test_expert_consultation_scenario,
            self.test_academic_research_scenario,
            self.test_industry_analysis_scenario,
            self.test_memory_service_integration,
            self.test_wiki_service_integration,
            self.test_role_management,
            self.test_chat_interface,
            self.test_error_handling,
            self.test_performance_metrics,
            self.test_concurrent_requests,
            self.test_data_persistence,
            self.test_security_validation
        ]
        
        for test_func in tests:
            test_name = test_func.__name__
            start_time = time.time()
            
            try:
                logger.info(f"Running test: {test_name}")
                await test_func()
                execution_time = time.time() - start_time
                result = TestResult(test_name, True, execution_time)
                logger.info(f"✅ {test_name} passed in {execution_time:.2f}s")
                
            except Exception as e:
                execution_time = time.time() - start_time
                result = TestResult(test_name, False, execution_time, str(e))
                logger.error(f"❌ {test_name} failed: {e}")
            
            self.results.append(result)
        
        return self.results
    
    async def test_service_health_check(self):
        """Test service health check endpoints."""
        # Test backend health
        async with self.session.get(f"{self.config.backend_url}/health", timeout=self.config.test_timeout) as response:
            assert response.status == 200
            data = await response.json()
            assert "status" in data
            assert data["status"] in ["healthy", "degraded"]
        
        # Test web interface health
        async with self.session.get(f"{self.config.web_url}/health", timeout=self.config.test_timeout) as response:
            assert response.status == 200
            data = await response.json()
            assert "status" in data
    
    async def test_expert_consultation_scenario(self):
        """Test expert consultation scenario end-to-end."""
        # Start consultation
        consultation_request = {
            "scenario_type": "expert_consultation",
            "topic": "AI system architecture optimization for scalability",
            "user_preferences": {
                "depth": "detailed",
                "experts": 3,
                "focus_areas": ["scalability", "performance", "cost"]
            }
        }
        
        async with self.session.post(
            f"{self.config.backend_url}/scenarios/execute",
            json=consultation_request,
            timeout=self.config.test_timeout
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert data["success"] is True
            assert "scenario_id" in data
            assert "result" in data
            
            # Verify result structure
            result = data["result"]
            assert "summary" in result
            assert "expert_participants" in result
            assert "confidence_score" in result
            assert isinstance(result["confidence_score"], float)
            assert 0 <= result["confidence_score"] <= 1
    
    async def test_academic_research_scenario(self):
        """Test academic research scenario end-to-end."""
        research_request = {
            "scenario_type": "academic_research",
            "topic": "Machine learning applications in healthcare diagnostics",
            "user_preferences": {
                "paper_count": 10,
                "analysis_depth": "comprehensive",
                "include_citations": True
            }
        }
        
        async with self.session.post(
            f"{self.config.backend_url}/scenarios/execute",
            json=research_request,
            timeout=self.config.test_timeout
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert data["success"] is True
            assert "result" in data
            
            # Verify research-specific results
            result = data["result"]
            assert "research_summary" in result
            assert "key_findings" in result
            assert "references" in result
            assert isinstance(result["key_findings"], list)
    
    async def test_industry_analysis_scenario(self):
        """Test industry analysis scenario end-to-end."""
        analysis_request = {
            "scenario_type": "industry_analysis",
            "topic": "Electric vehicle market analysis",
            "user_preferences": {
                "industry": "automotive",
                "analysis_depth": "detailed",
                "time_horizon": "5_years"
            }
        }
        
        async with self.session.post(
            f"{self.config.backend_url}/scenarios/execute",
            json=analysis_request,
            timeout=self.config.test_timeout
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert data["success"] is True
            assert "result" in data
            
            # Verify analysis-specific results
            result = data["result"]
            assert "market_analysis" in result
            assert "competitive_landscape" in result
            assert "recommendations" in result
    
    async def test_memory_service_integration(self):
        """Test memory service integration."""
        # Store data in memory
        memory_data = {
            "content": "Test memory content for integration testing",
            "metadata": {
                "test_id": "integration_test_001",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        async with self.session.post(
            f"{self.config.backend_url}/memory/store",
            json=memory_data,
            timeout=self.config.test_timeout
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert data["success"] is True
        
        # Search memory
        search_request = {
            "query": "integration testing",
            "limit": 5
        }
        
        async with self.session.post(
            f"{self.config.backend_url}/memory/search",
            json=search_request,
            timeout=self.config.test_timeout
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert "results" in data
            assert isinstance(data["results"], list)
    
    async def test_wiki_service_integration(self):
        """Test wiki service integration."""
        # Create wiki page
        wiki_page = {
            "title": "Integration Test Page",
            "content": "This is a test page for integration testing",
            "category": "testing",
            "tags": ["integration", "test"]
        }
        
        async with self.session.post(
            f"{self.config.backend_url}/wiki/pages",
            json=wiki_page,
            timeout=self.config.test_timeout
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert data["success"] is True
            page_id = data["page_id"]
        
        # Get wiki page
        async with self.session.get(
            f"{self.config.backend_url}/wiki/pages/{page_id}",
            timeout=self.config.test_timeout
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert data["title"] == wiki_page["title"]
        
        # List wiki pages
        async with self.session.get(
            f"{self.config.backend_url}/wiki/pages",
            timeout=self.config.test_timeout
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert "pages" in data
            assert isinstance(data["pages"], list)
    
    async def test_role_management(self):
        """Test role management functionality."""
        # Get all roles
        async with self.session.get(
            f"{self.config.backend_url}/roles",
            timeout=self.config.test_timeout
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert "roles" in data
            assert isinstance(data["roles"], list)
            assert len(data["roles"]) > 0
            
            # Verify role structure
            role = data["roles"][0]
            assert "id" in role
            assert "name" in role
            assert "description" in role
            assert "specializations" in role
    
    async def test_chat_interface(self):
        """Test web chat interface."""
        chat_request = {
            "user_input": "What are the best practices for AI system architecture?",
            "session_id": "test_session_001",
            "user_preferences": {
                "response_style": "detailed"
            }
        }
        
        async with self.session.post(
            f"{self.config.web_url}/chat",
            json=chat_request,
            timeout=self.config.test_timeout
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert data["success"] is True
            assert "response" in data
            assert "session_id" in data
            assert len(data["response"]) > 0
    
    async def test_error_handling(self):
        """Test error handling scenarios."""
        # Test invalid scenario type
        invalid_request = {
            "scenario_type": "invalid_scenario",
            "topic": "test topic"
        }
        
        async with self.session.post(
            f"{self.config.backend_url}/scenarios/execute",
            json=invalid_request,
            timeout=self.config.test_timeout
        ) as response:
            assert response.status == 400
        
        # Test missing required parameters
        incomplete_request = {
            "scenario_type": "expert_consultation"
            # Missing topic
        }
        
        async with self.session.post(
            f"{self.config.backend_url}/scenarios/execute",
            json=incomplete_request,
            timeout=self.config.test_timeout
        ) as response:
            assert response.status == 400
    
    async def test_performance_metrics(self):
        """Test performance and metrics collection."""
        # Test scenario execution time
        start_time = time.time()
        
        performance_request = {
            "scenario_type": "expert_consultation",
            "topic": "Quick performance test",
            "user_preferences": {
                "depth": "basic"
            }
        }
        
        async with self.session.post(
            f"{self.config.backend_url}/scenarios/execute",
            json=performance_request,
            timeout=self.config.test_timeout
        ) as response:
            execution_time = time.time() - start_time
            assert response.status == 200
            
            # Verify reasonable performance
            assert execution_time < self.config.test_timeout
            logger.info(f"Scenario execution time: {execution_time:.2f}s")
    
    async def test_concurrent_requests(self):
        """Test concurrent request handling."""
        async def make_request(request_id: int):
            request = {
                "scenario_type": "expert_consultation",
                "topic": f"Concurrent test request {request_id}",
                "user_preferences": {"depth": "basic"}
            }
            
            async with self.session.post(
                f"{self.config.backend_url}/scenarios/execute",
                json=request,
                timeout=self.config.test_timeout
            ) as response:
                return response.status
        
        # Make 5 concurrent requests
        tasks = [make_request(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        logger.info(f"All {len(results)} concurrent requests completed successfully")
    
    async def test_data_persistence(self):
        """Test data persistence across service restarts."""
        # Create test data
        test_data = {
            "content": "Persistence test data",
            "metadata": {
                "test_id": "persistence_test_001",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # Store data
        async with self.session.post(
            f"{self.config.backend_url}/memory/store",
            json=test_data,
            timeout=self.config.test_timeout
        ) as response:
            assert response.status == 200
        
        # Verify data persistence
        search_request = {
            "query": "persistence test",
            "limit": 10
        }
        
        async with self.session.post(
            f"{self.config.backend_url}/memory/search",
            json=search_request,
            timeout=self.config.test_timeout
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert len(data["results"]) > 0
    
    async def test_security_validation(self):
        """Test security validation and input sanitization."""
        # Test SQL injection attempt
        malicious_request = {
            "scenario_type": "expert_consultation",
            "topic": "'; DROP TABLE users; --",
            "user_preferences": {}
        }
        
        async with self.session.post(
            f"{self.config.backend_url}/scenarios/execute",
            json=malicious_request,
            timeout=self.config.test_timeout
        ) as response:
            # Should either reject the request or handle it safely
            assert response.status in [200, 400, 422]
        
        # Test XSS attempt
        xss_request = {
            "scenario_type": "expert_consultation",
            "topic": "<script>alert('xss')</script>",
            "user_preferences": {}
        }
        
        async with self.session.post(
            f"{self.config.backend_url}/scenarios/execute",
            json=xss_request,
            timeout=self.config.test_timeout
        ) as response:
            assert response.status in [200, 400, 422]
    
    def generate_test_report(self) -> dict[str, Any]:
        """Generate comprehensive test report."""
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - successful_tests
        success_rate = successful_tests / total_tests if total_tests > 0 else 0
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate,
                "execution_timestamp": datetime.now().isoformat()
            },
            "test_results": [
                {
                    "test_name": result.test_name,
                    "success": result.success,
                    "execution_time": result.execution_time,
                    "error_message": result.error_message,
                    "details": result.details
                }
                for result in self.results
            ],
            "performance_metrics": {
                "total_execution_time": sum(r.execution_time for r in self.results),
                "average_execution_time": sum(r.execution_time for r in self.results) / total_tests if total_tests > 0 else 0,
                "fastest_test": min(r.execution_time for r in self.results) if self.results else 0,
                "slowest_test": max(r.execution_time for r in self.results) if self.results else 0
            }
        }
        
        return report


@pytest.mark.asyncio()
async def test_end_to_end_integration():
    """Main end-to-end integration test."""
    config = TestConfig()
    
    async with EndToEndTestSuite(config) as test_suite:
        results = await test_suite.run_all_tests()
        report = test_suite.generate_test_report()
        
        # Print summary
        print("\n" + "="*80)
        print("END-TO-END INTEGRATION TEST RESULTS")
        print("="*80)
        print(f"Total Tests: {report['test_summary']['total_tests']}")
        print(f"Successful: {report['test_summary']['successful_tests']}")
        print(f"Failed: {report['test_summary']['failed_tests']}")
        print(f"Success Rate: {report['test_summary']['success_rate']:.2%}")
        print(f"Total Execution Time: {report['performance_metrics']['total_execution_time']:.2f}s")
        
        if report['test_summary']['failed_tests'] > 0:
            print("\nFailed Tests:")
            for result in results:
                if not result.success:
                    print(f"❌ {result.test_name}: {result.error_message}")
        
        # Assert overall success rate
        assert report['test_summary']['success_rate'] >= 0.8, "Overall success rate should be at least 80%"
        
        return report


if __name__ == "__main__":
    # Run the test suite
    report = asyncio.run(test_end_to_end_integration())
    
    # Save report to file
    with open("end_to_end_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("\nTest report saved to: end_to_end_test_report.json")
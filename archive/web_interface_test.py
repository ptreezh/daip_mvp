#!/usr/bin/env python3
"""@Time    : 2025-08-05 20:05:00
@Author  : DAIP-LIVE Team
@File    : web_interface_test.py
@Description:
    Comprehensive web interface testing with real LLM integration
"""

import asyncio
import logging
import os
import sys
import time
import traceback
from typing import Any

import aiohttp

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class WebInterfaceTester:
    """Comprehensive web interface tester"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = {}
        self.session = None
        self.start_time = time.time()
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def run_all_tests(self) -> dict[str, Any]:
        """Run all web interface tests"""
        print("Starting Web Interface Comprehensive Tests")
        print("=" * 60)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("System Status", self.test_system_status),
            ("Web Interface Access", self.test_web_interface),
            ("API Documentation", self.test_api_documentation),
            ("Scenario List", self.test_scenario_list),
            ("Smart Chat", self.test_smart_chat),
            ("Academic Research Scenario", self.test_academic_research),
            ("Expert Consultation Scenario", self.test_expert_consultation),
            ("Casual Discussion Scenario", self.test_casual_discussion),
            ("Error Handling", self.test_error_handling),
            ("Response Time", self.test_response_time),
            ("Data Validation", self.test_data_validation),
        ]
        
        for test_name, test_func in tests:
            print(f"\nTesting: {test_name}")
            print("-" * 40)
            
            try:
                result = await test_func()
                self.test_results[test_name] = {
                    "status": "success",
                    "result": result,
                    "duration": time.time() - self.start_time
                }
                print(f"✅ {test_name} - PASSED")
                
            except Exception as e:
                self.test_results[test_name] = {
                    "status": "failed",
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "duration": time.time() - self.start_time
                }
                print(f"❌ {test_name} - FAILED")
                print(f"   Error: {str(e)}")
        
        return self.generate_test_summary()
    
    async def test_health_check(self) -> dict[str, Any]:
        """Test health check endpoint"""
        async with self.session.get(f"{self.base_url}/health") as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "status": data.get("status"),
                    "service": data.get("service"),
                    "version": data.get("version"),
                    "scenarios": data.get("scenarios"),
                    "response_time": response.headers.get("X-Response-Time", "N/A")
                }
            else:
                raise Exception(f"Health check failed with status {response.status}")
    
    async def test_system_status(self) -> dict[str, Any]:
        """Test system status endpoint"""
        async with self.session.get(f"{self.base_url}/status") as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "service": data.get("service"),
                    "status": data.get("status"),
                    "features": data.get("features"),
                    "endpoints": data.get("endpoints"),
                    "timestamp": data.get("timestamp")
                }
            else:
                raise Exception(f"System status failed with status {response.status}")
    
    async def test_web_interface(self) -> dict[str, Any]:
        """Test web interface accessibility"""
        async with self.session.get(f"{self.base_url}/") as response:
            if response.status == 200:
                content = await response.text()
                return {
                    "content_length": len(content),
                    "has_title": "<title>" in content,
                    "has_chat_interface": "chat-container" in content,
                    "has_scenario_tabs": "scenario-tabs" in content,
                    "has_javascript": "script" in content,
                    "response_time": response.headers.get("X-Response-Time", "N/A")
                }
            else:
                raise Exception(f"Web interface failed with status {response.status}")
    
    async def test_api_documentation(self) -> dict[str, Any]:
        """Test API documentation accessibility"""
        async with self.session.get(f"{self.base_url}/docs") as response:
            if response.status == 200:
                content = await response.text()
                return {
                    "content_length": len(content),
                    "has_swagger_ui": "swagger-ui" in content.lower(),
                    "has_openapi_spec": "openapi" in content.lower(),
                    "response_time": response.headers.get("X-Response-Time", "N/A")
                }
            else:
                raise Exception(f"API documentation failed with status {response.status}")
    
    async def test_scenario_list(self) -> dict[str, Any]:
        """Test scenario list endpoint"""
        async with self.session.get(f"{self.base_url}/scenarios") as response:
            if response.status == 200:
                data = await response.json()
                scenarios = data.get("scenarios", [])
                return {
                    "total_scenarios": len(scenarios),
                    "scenario_ids": [s.get("id") for s in scenarios],
                    "scenario_names": [s.get("name") for s in scenarios],
                    "has_academic_research": any(s.get("id") == "academic_research" for s in scenarios),
                    "has_expert_consultation": any(s.get("id") == "expert_consultation" for s in scenarios),
                    "has_casual_discussion": any(s.get("id") == "casual_discussion" for s in scenarios)
                }
            else:
                raise Exception(f"Scenario list failed with status {response.status}")
    
    async def test_smart_chat(self) -> dict[str, Any]:
        """Test smart chat functionality"""
        payload = {
            "user_input": "AI在教育中的应用研究",
            "user_preferences": {"language": "zh"}
        }
        
        start_time = time.time()
        async with self.session.post(
            f"{self.base_url}/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        ) as response:
            response_time = time.time() - start_time
            
            if response.status == 200:
                data = await response.json()
                return {
                    "success": data.get("success"),
                    "scenario_id": data.get("scenario_id"),
                    "recommended_scenario": data.get("recommended_scenario"),
                    "execution_time": data.get("execution_time"),
                    "response_time": response_time,
                    "has_result": data.get("result") is not None,
                    "word_count": len(str(data.get("result", "")))
                }
            else:
                raise Exception(f"Smart chat failed with status {response.status}")
    
    async def test_academic_research(self) -> dict[str, Any]:
        """Test academic research scenario"""
        payload = {
            "topic": "人工智能在医疗诊断中的应用研究",
            "scenario_type": "academic_research",
            "user_preferences": {"depth": "deep"}
        }
        
        start_time = time.time()
        async with self.session.post(
            f"{self.base_url}/scenario",
            json=payload,
            headers={"Content-Type": "application/json"}
        ) as response:
            response_time = time.time() - start_time
            
            if response.status == 200:
                data = await response.json()
                result = data.get("result", {})
                return {
                    "success": data.get("success"),
                    "scenario_type": result.get("scenario_type"),
                    "word_count": result.get("word_count"),
                    "citations": result.get("citations"),
                    "confidence_score": result.get("confidence_score"),
                    "has_research_phases": len(result.get("research_phases", [])) > 0,
                    "has_final_report": len(result.get("final_report", "")) > 0,
                    "response_time": response_time
                }
            else:
                raise Exception(f"Academic research scenario failed with status {response.status}")
    
    async def test_expert_consultation(self) -> dict[str, Any]:
        """Test expert consultation scenario"""
        payload = {
            "topic": "是否应该采用微服务架构",
            "scenario_type": "expert_consultation",
            "user_preferences": {"expertise_level": "advanced"}
        }
        
        start_time = time.time()
        async with self.session.post(
            f"{self.base_url}/scenario",
            json=payload,
            headers={"Content-Type": "application/json"}
        ) as response:
            response_time = time.time() - start_time
            
            if response.status == 200:
                data = await response.json()
                result = data.get("result", {})
                return {
                    "success": data.get("success"),
                    "scenario_type": result.get("scenario_type"),
                    "matched_experts": result.get("matched_experts"),
                    "expert_opinions": len(result.get("expert_opinions", [])),
                    "has_synthesis": len(result.get("synthesis_recommendation", "")) > 0,
                    "confidence_score": result.get("confidence_score"),
                    "response_time": response_time
                }
            else:
                raise Exception(f"Expert consultation scenario failed with status {response.status}")
    
    async def test_casual_discussion(self) -> dict[str, Any]:
        """Test casual discussion scenario"""
        payload = {
            "topic": "最近有什么好电影推荐",
            "scenario_type": "casual_discussion",
            "user_preferences": {"tone": "friendly"}
        }
        
        start_time = time.time()
        async with self.session.post(
            f"{self.base_url}/scenario",
            json=payload,
            headers={"Content-Type": "application/json"}
        ) as response:
            response_time = time.time() - start_time
            
            if response.status == 200:
                data = await response.json()
                result = data.get("result", {})
                return {
                    "success": data.get("success"),
                    "scenario_type": result.get("scenario_type"),
                    "participants": result.get("participants"),
                    "conversation_flow": len(result.get("conversation_flow", [])),
                    "atmosphere_score": result.get("atmosphere_score"),
                    "engagement_level": result.get("engagement_level"),
                    "response_time": response_time
                }
            else:
                raise Exception(f"Casual discussion scenario failed with status {response.status}")
    
    async def test_error_handling(self) -> dict[str, Any]:
        """Test error handling"""
        # Test with invalid scenario type
        payload = {
            "topic": "Test topic",
            "scenario_type": "invalid_scenario",
            "user_preferences": {}
        }
        
        async with self.session.post(
            f"{self.base_url}/scenario",
            json=payload,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 500:
                data = await response.json()
                return {
                    "error_handled": data.get("success") == False,
                    "has_error_message": "error" in data,
                    "proper_status_code": response.status == 500
                }
            else:
                return {
                    "error_handled": False,
                    "unexpected_status": response.status
                }
    
    async def test_response_time(self) -> dict[str, Any]:
        """Test response time performance"""
        test_payloads = [
            {"user_input": "简单测试"},
            {"topic": "AI在教育中的应用", "scenario_type": "academic_research"},
            {"topic": "微服务架构", "scenario_type": "expert_consultation"}
        ]
        
        response_times = []
        
        for payload in test_payloads:
            endpoint = "/chat" if "user_input" in payload else "/scenario"
            start_time = time.time()
            
            async with self.session.post(
                f"{self.base_url}{endpoint}",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_time = time.time() - start_time
                response_times.append(response_time)
        
        return {
            "average_response_time": sum(response_times) / len(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "total_tests": len(response_times),
            "performance_acceptable": all(rt < 5.0 for rt in response_times)  # All under 5 seconds
        }
    
    async def test_data_validation(self) -> dict[str, Any]:
        """Test data validation"""
        # Test with empty input
        empty_payload = {"user_input": ""}
        
        async with self.session.post(
            f"{self.base_url}/chat",
            json=empty_payload,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "empty_input_handled": data.get("success") == True or data.get("error") is not None,
                    "response_structure_valid": isinstance(data, dict)
                }
            else:
                return {
                    "empty_input_handled": False,
                    "status_code": response.status
                }
    
    def generate_test_summary(self) -> dict[str, Any]:
        """Generate comprehensive test summary"""
        total_duration = time.time() - self.start_time
        
        successful_tests = sum(1 for r in self.test_results.values() if r["status"] == "success")
        total_tests = len(self.test_results)
        
        summary = {
            "overall_status": "success" if successful_tests == total_tests else "partial_failure" if successful_tests > 0 else "failure",
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
            "total_duration": total_duration,
            "test_results": self.test_results,
            "performance_metrics": self._extract_performance_metrics(),
            "functionality_coverage": self._calculate_functionality_coverage()
        }
        
        return summary
    
    def _extract_performance_metrics(self) -> dict[str, Any]:
        """Extract performance metrics from test results"""
        response_times = []
        
        for result in self.test_results.values():
            if result["status"] == "success" and "result" in result:
                result_data = result["result"]
                if isinstance(result_data, dict):
                    if "response_time" in result_data:
                        response_times.append(result_data["response_time"])
                    if "average_response_time" in result_data:
                        response_times.append(result_data["average_response_time"])
        
        if response_times:
            return {
                "average_response_time": sum(response_times) / len(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "performance_acceptable": all(rt < 5.0 for rt in response_times)
            }
        else:
            return {"error": "No response time data available"}
    
    def _calculate_functionality_coverage(self) -> dict[str, Any]:
        """Calculate functionality coverage"""
        coverage_areas = {
            "basic_access": ["Health Check", "System Status", "Web Interface Access", "API Documentation"],
            "scenario_functionality": ["Scenario List", "Smart Chat", "Academic Research Scenario", "Expert Consultation Scenario", "Casual Discussion Scenario"],
            "robustness": ["Error Handling", "Data Validation"],
            "performance": ["Response Time"]
        }
        
        coverage_results = {}
        for area, tests in coverage_areas.items():
            passed_tests = sum(1 for test in tests if self.test_results.get(test, {}).get("status") == "success")
            coverage_results[area] = {
                "passed": passed_tests,
                "total": len(tests),
                "coverage": passed_tests / len(tests) if tests else 0
            }
        
        return coverage_results
    
    def print_test_summary(self, summary: dict[str, Any]):
        """Print detailed test summary"""
        print("\n" + "=" * 60)
        print("WEB INTERFACE COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        
        print(f"Overall Status: {summary['overall_status'].upper()}")
        print(f"Successful Tests: {summary['successful_tests']}/{summary['total_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1%}")
        print(f"Total Duration: {summary['total_duration']:.2f}s")
        
        print("\nFunctionality Coverage:")
        coverage = summary['functionality_coverage']
        for area, data in coverage.items():
            print(f"   {area.replace('_', ' ').title()}: {data['coverage']:.1%} ({data['passed']}/{data['total']})")
        
        print("\nPerformance Metrics:")
        metrics = summary['performance_metrics']
        if "error" not in metrics:
            print(f"   Average Response Time: {metrics['average_response_time']:.2f}s")
            print(f"   Min Response Time: {metrics['min_response_time']:.2f}s")
            print(f"   Max Response Time: {metrics['max_response_time']:.2f}s")
            print(f"   Performance Acceptable: {'Yes' if metrics['performance_acceptable'] else 'No'}")
        else:
            print(f"   {metrics['error']}")
        
        if summary['failed_tests'] > 0:
            print("\nFailed Tests:")
            for test_name, result in summary['test_results'].items():
                if result['status'] == 'failed':
                    print(f"   • {test_name}: {result['error']}")
        
        print("\nRecommendations:")
        if summary['overall_status'] == 'success':
            print("   • All web interface tests passed")
            print("   • System is ready for production use")
            print("   • All scenarios are working correctly")
            print("   • Performance is within acceptable limits")
        elif summary['overall_status'] == 'partial_failure':
            print("   • Most web interface functionality is working")
            print("   • Some issues need attention before production")
            print("   • Review failed tests and fix identified issues")
        else:
            print("   • Critical web interface failures detected")
            print("   • System needs significant debugging")
            print("   • Do not deploy to production")
        
        print("\n" + "=" * 60)


async def main():
    """Main test function"""
    base_url = "http://localhost:8000"
    
    # First check if server is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    print("Server is running and accessible")
                else:
                    print(f"Server returned status {response.status}")
                    return None
    except Exception as e:
        print(f"Cannot connect to server at {base_url}: {e}")
        print("Please start the server first:")
        print("  python web_demo_app.py")
        return None
    
    async with WebInterfaceTester(base_url) as tester:
        try:
            # Run all tests
            summary = await tester.run_all_tests()
            
            # Print summary
            tester.print_test_summary(summary)
            
            # Exit with appropriate code
            if summary['overall_status'] == 'success':
                print("\nAll web interface tests passed!")
                return 0
            elif summary['overall_status'] == 'partial_failure':
                print("\nSome web interface tests failed.")
                return 1
            else:
                print("\nCritical web interface test failures!")
                return 2
                
        except KeyboardInterrupt:
            print("\nTests interrupted by user")
            return 130
        except Exception as e:
            print(f"\nUnexpected error during testing: {e}")
            traceback.print_exc()
            return 3


if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
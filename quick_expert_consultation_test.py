#!/usr/bin/env python3
"""@Time    : 2025-08-05 10:00:00
@Author  : DAIP-LIVE Team
@File    : quick_expert_consultation_test.py
@Description:
    Quick expert consultation scenario test
"""

import asyncio
import json
import logging

# Add project root to path
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from personal_intelligence_hub.services.backend_integration import get_backend_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test result data structure"""
    test_id: str
    test_name: str
    status: str  # "PASSED", "FAILED", "ERROR"
    duration: float
    details: str
    data: Optional[dict[str, Any]] = None

async def test_expert_consultation_scenario():
    """Test expert consultation scenario"""
    logger.info("🚀 Starting Expert Consultation Scenario Test")
    
    backend_service = None
    test_results = []
    
    try:
        # Initialize backend service
        backend_service = await get_backend_service()
        
        # Test 1: Backend Health Check
        test_start = time.time()
        health_status = await backend_service.check_backend_health()
        backend_healthy = health_status.get("backend").status.value == "HEALTHY"
        
        test_results.append(TestResult(
            test_id="T4.1.0",
            test_name="Backend Health Check",
            status="PASSED" if backend_healthy else "DEGRADED",
            duration=time.time() - test_start,
            details=f"Backend status: {health_status.get('backend').status.value}",
            data={"backend_status": health_status.get("backend").status.value}
        ))
        
        # Test 2: Available Roles
        test_start = time.time()
        roles = await backend_service.get_available_roles()
        
        test_results.append(TestResult(
            test_id="T4.1.1",
            test_name="Available Roles",
            status="PASSED" if roles else "FAILED",
            duration=time.time() - test_start,
            details=f"Retrieved {len(roles)} roles",
            data={"role_count": len(roles), "sample_roles": roles[:3] if roles else []}
        ))
        
        # Test 3: Intent Analysis
        test_start = time.time()
        test_queries = [
            "How can I improve my company's AI strategy?",
            "What are the ethical implications of autonomous vehicles?",
            "How should we approach digital transformation?"
        ]
        
        intent_results = []
        for query in test_queries:
            try:
                intent_result = await backend_service.analyze_intent(
                    user_input=query,
                    user_id="test_user",
                    context=[]
                )
                intent_results.append({
                    "query": query,
                    "success": "error" not in intent_result,
                    "result": intent_result
                })
            except Exception as e:
                intent_results.append({
                    "query": query,
                    "success": False,
                    "error": str(e)
                })
        
        successful_intents = sum(1 for result in intent_results if result.get("success", False))
        test_results.append(TestResult(
            test_id="T4.1.2",
            test_name="Intent Analysis",
            status="PASSED" if successful_intents >= 2 else "PARTIAL",
            duration=time.time() - test_start,
            details=f"Successfully analyzed {successful_intents}/{len(test_queries)} queries",
            data={"total_queries": len(test_queries), "successful_intents": successful_intents, "results": intent_results}
        ))
        
        # Test 4: Workflow Start
        test_start = time.time()
        try:
            workflow_result = await backend_service.start_workflow(
                workflow_type="MULTI_PERSPECTIVE",
                participants=["ai_expert", "ethicist", "economist"],
                topic="How to implement AI responsibly?"
            )
            
            workflow_success = "error" not in workflow_result
            test_results.append(TestResult(
                test_id="T4.1.3",
                test_name="Workflow Start",
                status="PASSED" if workflow_success else "FAILED",
                duration=time.time() - test_start,
                details=f"Workflow started: {workflow_success}",
                data={"workflow_result": workflow_result, "success": workflow_success}
            ))
        except Exception as e:
            test_results.append(TestResult(
                test_id="T4.1.3",
                test_name="Workflow Start",
                status="ERROR",
                duration=time.time() - test_start,
                details=f"Workflow start failed: {str(e)}"
            ))
        
        # Test 5: Consensus Calculation
        test_start = time.time()
        try:
            consensus_inputs = [
                {"expert": "ai_expert", "opinion": "AI implementation should be gradual and monitored"},
                {"expert": "ethicist", "opinion": "Ethical guidelines must be established first"},
                {"expert": "economist", "opinion": "Cost-benefit analysis is essential"}
            ]
            
            consensus_result = await backend_service.execute_consensus(
                inputs=consensus_inputs,
                algorithm_type="simple_majority_vote"
            )
            
            consensus_success = "error" not in consensus_result
            test_results.append(TestResult(
                test_id="T4.1.4",
                test_name="Consensus Calculation",
                status="PASSED" if consensus_success else "FAILED",
                duration=time.time() - test_start,
                details=f"Consensus calculated: {consensus_success}",
                data={"consensus_result": consensus_result, "success": consensus_success}
            ))
        except Exception as e:
            test_results.append(TestResult(
                test_id="T4.1.4",
                test_name="Consensus Calculation",
                status="ERROR",
                duration=time.time() - test_start,
                details=f"Consensus calculation failed: {str(e)}"
            ))
        
        # Test 6: Wiki Search
        test_start = time.time()
        try:
            wiki_results = await backend_service.search_wiki("AI implementation", limit=5)
            
            wiki_success = isinstance(wiki_results, list)
            test_results.append(TestResult(
                test_id="T4.1.5",
                test_name="Wiki Search",
                status="PASSED" if wiki_success else "FAILED",
                duration=time.time() - test_start,
                details=f"Wiki search completed: {len(wiki_results)} results",
                data={"wiki_results": wiki_results, "result_count": len(wiki_results)}
            ))
        except Exception as e:
            test_results.append(TestResult(
                test_id="T4.1.5",
                test_name="Wiki Search",
                status="ERROR",
                duration=time.time() - test_start,
                details=f"Wiki search failed: {str(e)}"
            ))
        
        # Generate report
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results if result.status == "PASSED")
        partial_tests = sum(1 for result in test_results if result.status == "PARTIAL")
        failed_tests = sum(1 for result in test_results if result.status in ["FAILED", "ERROR"])
        
        total_duration = sum(result.duration for result in test_results)
        pass_rate = passed_tests / total_tests if total_tests > 0 else 0
        
        report = {
            "test_phase": "Phase 4.1: Expert Consultation Scenario Testing",
            "execution_time": datetime.now().isoformat(),
            "total_duration_seconds": total_duration,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "partial_tests": partial_tests,
            "failed_tests": failed_tests,
            "pass_rate": pass_rate,
            "overall_status": "PASSED" if pass_rate >= 0.7 else "PARTIAL" if pass_rate >= 0.5 else "FAILED",
            "test_results": [
                {
                    "test_id": result.test_id,
                    "test_name": result.test_name,
                    "status": result.status,
                    "duration": result.duration,
                    "details": result.details,
                    "data": result.data
                }
                for result in test_results
            ]
        }
        
        # Display results
        print("\n" + "="*80)
        print("EXPERT CONSULTATION SCENARIO TEST RESULTS")
        print("="*80)
        
        print(f"Overall Status: {report['overall_status']}")
        print(f"Pass Rate: {report['pass_rate']:.1%} ({report['passed_tests']}/{report['total_tests']})")
        print(f"Total Duration: {report['total_duration_seconds']:.2f} seconds")
        print(f"Execution Time: {report['execution_time']}")
        
        print("\nTest Results:")
        print("-" * 50)
        for result in report["test_results"]:
            if result["status"] == "PASSED":
                icon = "[PASS]"
            elif result["status"] == "PARTIAL":
                icon = "[PART]"
            elif result["status"] == "FAILED":
                icon = "[FAIL]"
            else:
                icon = "[ERROR]"
            
            print(f"{icon} {result['test_id']} ({result['test_name']}): {result['status']}")
            print(f"   Duration: {result['duration']:.2f}s")
            print(f"   Details: {result['details']}")
            print()
        
        # Save report
        report_filename = f"expert_consultation_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"Detailed report saved to: {report_filename}")
        
        if report["overall_status"] == "PASSED":
            print("Expert Consultation Scenario Test PASSED")
        elif report["overall_status"] == "PARTIAL":
            print("Expert Consultation Scenario Test PARTIAL - Some functionality needs improvement")
        else:
            print("Expert Consultation Scenario Test FAILED")
        
        return report
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        raise
    finally:
        if backend_service:
            await backend_service.close()

if __name__ == "__main__":
    asyncio.run(test_expert_consultation_scenario())
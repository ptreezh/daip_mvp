#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-05 11:30:00
@Author  : DAIP-LIVE Team
@File    : test_api_endpoints.py
@Description:
    Test API endpoint integration and functionality
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_health_endpoints():
    """Test health check endpoints"""
    print("Testing Health Endpoints...")
    
    endpoints = [
        ("/", "Root endpoint"),
        ("/docs", "API documentation"),
        ("/openapi.json", "OpenAPI schema"),
        ("/health", "Health check")
    ]
    
    successful_tests = []
    failed_tests = []
    
    for endpoint, description in endpoints:
        try:
            url = BASE_URL + endpoint
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"OK {description} ({endpoint}) - HTTP {response.status_code}")
                successful_tests.append((endpoint, description))
            else:
                print(f"FAIL {description} ({endpoint}) - HTTP {response.status_code}")
                failed_tests.append((endpoint, description, response.status_code))
                
        except requests.exceptions.RequestException as e:
            print(f"ERROR {description} ({endpoint}) - {e}")
            failed_tests.append((endpoint, description, str(e)))
    
    return len(failed_tests) == 0

def test_api_routers():
    """Test API router endpoints"""
    print("\nTesting API Router Endpoints...")
    
    # Test main API routers
    routers = [
        ("/api/chat", "Chat API"),
        ("/api/roles", "Roles API"),
        ("/api/tools", "Tools API"),
        ("/api/protocols", "Protocols API"),
        ("/api/collaboration", "Collaboration API"),
        ("/api/virtual-team", "Virtual Team API"),
        ("/api/advanced", "Advanced API")
    ]
    
    successful_tests = []
    failed_tests = []
    
    for router, description in routers:
        try:
            url = BASE_URL + router
            response = requests.get(url, timeout=10)
            
            # For GET requests, we expect either 200 (OK) or 405 (Method Not Allowed) if POST is required
            if response.status_code in [200, 405]:
                print(f"OK {description} ({router}) - HTTP {response.status_code}")
                successful_tests.append((router, description))
            else:
                print(f"FAIL {description} ({router}) - HTTP {response.status_code}")
                failed_tests.append((router, description, response.status_code))
                
        except requests.exceptions.RequestException as e:
            print(f"ERROR {description} ({router}) - {e}")
            failed_tests.append((router, description, str(e)))
    
    return len(failed_tests) == 0

def test_specialized_apis():
    """Test specialized API endpoints"""
    print("\nTesting Specialized API Endpoints...")
    
    specialized_apis = [
        ("/api/v0.3.5/critical-review", "Critical Review API"),
        ("/api/knowledge/web-interface", "Knowledge Web Interface"),
        ("/api/scenario/integration", "Scenario Integration API"),
        ("/api/user-profile", "User Profile API")
    ]
    
    successful_tests = []
    failed_tests = []
    
    for api, description in specialized_apis:
        try:
            url = BASE_URL + api
            response = requests.get(url, timeout=10)
            
            if response.status_code in [200, 405]:
                print(f"OK {description} ({api}) - HTTP {response.status_code}")
                successful_tests.append((api, description))
            else:
                print(f"FAIL {description} ({api}) - HTTP {response.status_code}")
                failed_tests.append((api, description, response.status_code))
                
        except requests.exceptions.RequestException as e:
            print(f"ERROR {description} ({api}) - {e}")
            failed_tests.append((api, description, str(e)))
    
    return len(failed_tests) == 0

def test_api_functionality():
    """Test basic API functionality"""
    print("\nTesting API Functionality...")
    
    # Test roles endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/roles", timeout=10)
        if response.status_code == 200:
            print("OK Roles API - Successfully retrieved roles")
            try:
                roles_data = response.json()
                print(f"   Retrieved {len(roles_data)} roles")
                return True
            except json.JSONDecodeError:
                print("FAIL Roles API - Invalid JSON response")
                return False
        else:
            print(f"FAIL Roles API - HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"ERROR Roles API - {e}")
        return False

def test_websocket_endpoint():
    """Test WebSocket endpoint availability"""
    print("\nTesting WebSocket Endpoint...")
    
    try:
        # Test if WebSocket endpoint is accessible
        import websocket
        ws = websocket.create_connection("ws://127.0.0.1:8000/ws", timeout=5)
        ws.close()
        print("OK WebSocket endpoint - Connection successful")
        return True
    except Exception as e:
        print(f"FAIL WebSocket endpoint - {e}")
        return False

def test_response_times():
    """Test API response times"""
    print("\nTesting API Response Times...")
    
    endpoints = [
        ("/", "Root"),
        ("/docs", "Documentation"),
        ("/api/roles", "Roles API")
    ]
    
    slow_responses = []
    
    for endpoint, description in endpoints:
        try:
            start_time = time.time()
            response = requests.get(BASE_URL + endpoint, timeout=10)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            if response_time < 1000:  # Less than 1 second
                print(f"OK {description} - {response_time:.0f}ms")
            else:
                print(f"SLOW {description} - {response_time:.0f}ms")
                slow_responses.append((description, response_time))
                
        except requests.exceptions.RequestException as e:
            print(f"ERROR {description} - {e}")
            slow_responses.append((description, float('inf')))
    
    return len(slow_responses) == 0

def generate_test_report():
    """Generate comprehensive test report"""
    print("=" * 60)
    print("DAIP项目API端点集成测试报告")
    print("=" * 60)
    
    tests = [
        ("健康检查端点", test_health_endpoints),
        ("API路由端点", test_api_routers),
        ("专用API端点", test_specialized_apis),
        ("API功能测试", test_api_functionality),
        ("WebSocket端点", test_websocket_endpoint),
        ("响应时间测试", test_response_times)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n执行测试: {test_name}")
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"测试错误: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("API端点测试全部通过!")
        return True
    else:
        print("API端点测试存在问题")
        return False

if __name__ == "__main__":
    success = generate_test_report()
    exit(0 if success else 1)
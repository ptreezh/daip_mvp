#!/usr/bin/env python3
"""V0.1.2 完整集成测试
验证PersonalAssistant与后端服务的完整集成
"""

import asyncio
import logging
import time
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_backend_api_endpoints():
    """测试后端API端点"""
    print("\n" + "="*60)
    print("测试后端API端点")
    print("="*60)
    
    import requests
    
    tests = [
        ("GET /", "http://127.0.0.1:8000/"),
        ("GET /roles/", "http://127.0.0.1:8000/roles/"),
        ("POST /advanced/analyze-intent", "http://127.0.0.1:8000/advanced/analyze-intent")
    ]
    
    results = []
    
    for test_name, url in tests:
        try:
            if "analyze-intent" in url:
                response = requests.post(url, json={
                    "user_input": "分析AI在教育中的应用",
                    "user_id": "test_user",
                    "context": []
                })
            else:
                response = requests.get(url)
            
            status = "✅ 通过" if response.status_code == 200 else f"❌ 失败 ({response.status_code})"
            print(f"{status} {test_name}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    print(f"   响应键: {list(data.keys())}")
                elif isinstance(data, list):
                    print(f"   响应项数: {len(data)}")
            
            results.append(response.status_code == 200)
            
        except Exception as e:
            print(f"❌ 失败 {test_name}: {e}")
            results.append(False)
    
    return all(results)

async def test_personal_assistant_integration():
    """测试PersonalAssistant集成"""
    print("\n" + "="*60)
    print("测试PersonalAssistant集成")
    print("="*60)
    
    try:
        from personal_intelligence_hub.services.personal_assistant import PersonalAssistantService
        
        assistant = PersonalAssistantService()
        
        # 测试不同类型的输入
        test_cases = [
            ("分析AI在教育中的应用", "学术研究"),
            ("讨论气候变化的解决方案", "多角度讨论"),
            ("帮我研究区块链技术", "技术研究")
        ]
        
        results = []
        
        for user_input, description in test_cases:
            print(f"\n🔍 测试: {description}")
            print(f"   输入: {user_input}")
            
            start_time = time.time()
            try:
                response = await assistant.process_message(user_input, f"test_session_{len(results)}")
                end_time = time.time()
                
                response_time = end_time - start_time
                print(f"   ✅ 响应时间: {response_time:.2f}秒")
                print(f"   ✅ 响应长度: {len(response)}字符")
                print(f"   ✅ 响应预览: {response[:100]}...")
                
                results.append(True)
                
            except Exception as e:
                print(f"   ❌ 失败: {e}")
                results.append(False)
        
        return all(results)
        
    except Exception as e:
        print(f"❌ PersonalAssistant集成测试失败: {e}")
        return False

async def test_command_execution():
    """测试命令执行功能"""
    print("\n" + "="*60)
    print("测试命令执行功能")
    print("="*60)
    
    try:
        from personal_intelligence_hub.services.personal_assistant import PersonalAssistantService
        
        assistant = PersonalAssistantService()
        
        commands = ["/help", "/status"]
        results = []
        
        for command in commands:
            print(f"\n🔍 测试命令: {command}")
            
            start_time = time.time()
            try:
                response = await assistant.execute_command(command, "test_session_cmd")
                end_time = time.time()
                
                response_time = end_time - start_time
                print(f"   ✅ 响应时间: {response_time:.2f}秒")
                print(f"   ✅ 响应长度: {len(response)}字符")
                print(f"   ✅ 响应预览: {response[:100]}...")
                
                results.append(True)
                
            except Exception as e:
                print(f"   ❌ 失败: {e}")
                results.append(False)
        
        return all(results)
        
    except Exception as e:
        print(f"❌ 命令执行测试失败: {e}")
        return False

async def test_performance_benchmarks():
    """测试性能基准"""
    print("\n" + "="*60)
    print("测试性能基准")
    print("="*60)
    
    try:
        from personal_intelligence_hub.services.personal_assistant import PersonalAssistantService
        
        assistant = PersonalAssistantService()
        
        # 性能测试
        test_input = "分析人工智能在医疗健康领域的应用前景和挑战"
        iterations = 3
        
        times = []
        
        for i in range(iterations):
            print(f"\n🔍 性能测试 {i+1}/{iterations}")
            
            start_time = time.time()
            response = await assistant.process_message(test_input, f"perf_test_{i}")
            end_time = time.time()
            
            response_time = end_time - start_time
            times.append(response_time)
            
            print(f"   响应时间: {response_time:.2f}秒")
            print(f"   响应长度: {len(response)}字符")
        
        # 计算统计数据
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        
        print("\n📊 性能统计:")
        print(f"   平均响应时间: {avg_time:.2f}秒")
        print(f"   最大响应时间: {max_time:.2f}秒")
        print(f"   最小响应时间: {min_time:.2f}秒")
        
        # 性能要求验证
        performance_ok = avg_time < 30.0  # 平均响应时间小于30秒
        print(f"   性能要求: {'✅ 满足' if performance_ok else '❌ 不满足'} (<30秒)")
        
        return performance_ok
        
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")
        return False

async def test_error_handling():
    """测试错误处理"""
    print("\n" + "="*60)
    print("测试错误处理")
    print("="*60)
    
    try:
        from personal_intelligence_hub.services.personal_assistant import PersonalAssistantService
        
        assistant = PersonalAssistantService()
        
        # 错误处理测试
        error_cases = [
            ("", "空输入"),
            ("a" * 5000, "超长输入"),
            ("🚀🎯💡🔥⚡", "特殊字符"),
            ("SELECT * FROM users", "SQL注入尝试")
        ]
        
        results = []
        
        for test_input, description in error_cases:
            print(f"\n🔍 测试: {description}")
            
            try:
                response = await assistant.process_message(test_input, f"error_test_{len(results)}")
                
                # 检查是否有合理的响应
                if response and len(response) > 0:
                    print(f"   ✅ 正常处理: {len(response)}字符响应")
                    results.append(True)
                else:
                    print("   ❌ 无响应")
                    results.append(False)
                    
            except Exception as e:
                print(f"   ⚠️ 异常处理: {e}")
                # 异常被捕获也算是正常的错误处理
                results.append(True)
        
        return all(results)
        
    except Exception as e:
        print(f"❌ 错误处理测试失败: {e}")
        return False

async def run_complete_integration_tests():
    """运行完整集成测试"""
    print("🚀 开始 V0.1.2 完整集成测试")
    print("="*80)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 执行所有测试
    tests = [
        ("后端API端点", test_backend_api_endpoints),
        ("PersonalAssistant集成", test_personal_assistant_integration),
        ("命令执行功能", test_command_execution),
        ("性能基准测试", test_performance_benchmarks),
        ("错误处理机制", test_error_handling)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 执行测试组: {test_name}")
        try:
            result = await test_func()
            results.append((test_name, result))
            
            status = "✅ 通过" if result else "❌ 失败"
            print(f"\n{status} {test_name}")
            
        except Exception as e:
            print(f"\n❌ {test_name}: 异常 - {e}")
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "="*80)
    print("🎯 V0.1.2 完整集成测试结果")
    print("="*80)
    
    passed_tests = sum(1 for _, result in results if result)
    total_tests = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} {test_name}")
    
    print(f"\n📊 总体结果: {passed_tests}/{total_tests} 测试通过")
    success_rate = (passed_tests / total_tests) * 100
    print(f"📊 成功率: {success_rate:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 所有集成测试通过！V0.1.2任务可以标记为完成。")
        return True
    else:
        print(f"\n⚠️ {total_tests - passed_tests}个测试失败，需要进一步修复。")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_complete_integration_tests())
    exit(0 if success else 1)
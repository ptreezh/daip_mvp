#!/usr/bin/env python3
"""ToolManager兼容层测试

测试ToolManager与统一共识调度器的集成兼容性。
"""

import asyncio
import sys
from datetime import datetime

# 添加src路径
sys.path.append('src')
sys.path.append('src/core_services')

async def test_tool_manager_compatibility():
    """测试ToolManager兼容层"""
    print("🧪 测试ToolManager兼容层...")
    
    try:
        from legacy_compatibility_layer import get_tool_manager_compatibility
        
        # 创建兼容层实例
        tool_manager = get_tool_manager_compatibility()
        print("✅ ToolManager兼容层创建成功")
        
        # 测试工具注册
        await test_tool_registration(tool_manager)
        
        # 测试工具执行
        await test_tool_execution(tool_manager)
        
        # 测试不同算法类型
        await test_different_algorithms(tool_manager)
        
        # 测试工具管理
        await test_tool_management(tool_manager)
        
        print("🎉 所有ToolManager兼容性测试通过！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

async def test_tool_registration(tool_manager):
    """测试工具注册功能"""
    print("\n📝 测试工具注册...")
    
    # 注册共识工具
    tools = [
        ("consensus_simple", "simple_majority"),
        ("consensus_weighted", "weighted_voting"),
        ("consensus_bayesian", "bayesian_consensus")
    ]
    
    for tool_name, algorithm_type in tools:
        success = await tool_manager.register_consensus_tool(tool_name, algorithm_type)
        print(f"   {tool_name}: {'成功' if success else '失败'}")
        assert success, f"工具{tool_name}注册应该成功"
    
    # 检查注册结果
    registered_tools = tool_manager.get_registered_tools()
    print(f"   已注册工具数量: {len(registered_tools)}")
    
    for tool_name in registered_tools:
        print(f"   - {tool_name}: {registered_tools[tool_name]['algorithm_type']}")
    
    assert len(registered_tools) == 3, "应该注册3个工具"
    print("✅ 工具注册测试通过")

async def test_tool_execution(tool_manager):
    """测试工具执行功能"""
    print("\n⚙️ 测试工具执行...")
    
    # 先注册一个工具
    await tool_manager.register_consensus_tool("test_consensus", "simple_majority")
    
    # 准备测试输入
    inputs = [
        {
            "agent_id": "tool_user1",
            "position": "支持方案A",
            "confidence": 0.8,
            "reasoning": "基于工具的分析"
        },
        {
            "agent_id": "tool_user2",
            "position": "支持方案A",
            "confidence": 0.9,
            "reasoning": "工具验证结果"
        },
        {
            "agent_id": "tool_user3",
            "position": "支持方案B",
            "confidence": 0.6,
            "reasoning": "不同的工具观点"
        }
    ]
    
    # 执行工具
    result = await tool_manager.execute_tool("test_consensus", inputs)
    
    print(f"   工具执行结果: {'成功' if result.get('success') else '失败'}")
    print(f"   共识值: {result.get('consensus_value', 'N/A')}")
    print(f"   置信度: {result.get('confidence', 0.0):.3f}")
    print(f"   调用次数: {result.get('call_count', 0)}")
    
    assert result.get("success", False), "工具执行应该成功"
    assert "consensus_value" in result, "结果应该包含共识值"
    assert "tool_name" in result, "结果应该包含工具名称"
    print("✅ 工具执行测试通过")

async def test_different_algorithms(tool_manager):
    """测试不同算法类型的工具"""
    print("\n🔧 测试不同算法类型...")
    
    # 注册不同算法类型的工具
    algorithm_tools = [
        ("simple_tool", "simple_majority"),
        ("weighted_tool", "weighted_voting"),
        ("bayesian_tool", "bayesian_consensus")
    ]
    
    for tool_name, algorithm_type in algorithm_tools:
        await tool_manager.register_consensus_tool(tool_name, algorithm_type)
    
    # 测试输入
    inputs = [
        {
            "agent_id": "multi_test1",
            "position": "测试选项",
            "confidence": 0.7,
            "reasoning": "多算法测试"
        },
        {
            "agent_id": "multi_test2",
            "position": "测试选项",
            "confidence": 0.8,
            "reasoning": "算法比较测试"
        }
    ]
    
    # 测试每个工具
    for tool_name, algorithm_type in algorithm_tools:
        result = await tool_manager.execute_tool(tool_name, inputs)
        print(f"   {tool_name} ({algorithm_type}): {'成功' if result.get('success') else '失败'}")
        
        if result.get("success"):
            print(f"     置信度: {result.get('confidence', 0.0):.3f}")
            print(f"     算法: {result.get('algorithm_type', 'unknown')}")
        
        assert result.get("success", False), f"{tool_name}应该执行成功"
    
    print("✅ 不同算法类型测试通过")

async def test_tool_management(tool_manager):
    """测试工具管理功能"""
    print("\n📊 测试工具管理...")
    
    # 注册一些工具
    await tool_manager.register_consensus_tool("mgmt_tool1", "simple_majority")
    await tool_manager.register_consensus_tool("mgmt_tool2", "weighted_voting")
    
    # 获取工具列表
    tools = tool_manager.get_registered_tools()
    print(f"   管理的工具数量: {len(tools)}")
    
    # 检查工具信息
    for tool_name, tool_info in tools.items():
        print(f"   - {tool_name}:")
        print(f"     算法: {tool_info.get('algorithm_type', 'unknown')}")
        print(f"     注册时间: {tool_info.get('registered_at', 'unknown')}")
        print(f"     调用次数: {tool_info.get('call_count', 0)}")
    
    # 测试工具执行统计
    test_inputs = [
        {
            "agent_id": "stats_test",
            "position": "统计测试",
            "confidence": 0.8,
            "reasoning": "测试统计功能"
        }
    ]
    
    # 多次调用同一个工具
    for i in range(3):
        result = await tool_manager.execute_tool("mgmt_tool1", test_inputs)
        assert result.get("success", False), f"第{i+1}次调用应该成功"
    
    # 检查调用统计
    updated_tools = tool_manager.get_registered_tools()
    mgmt_tool1_info = updated_tools.get("mgmt_tool1", {})
    call_count = mgmt_tool1_info.get("call_count", 0)
    
    print(f"   mgmt_tool1调用次数: {call_count}")
    assert call_count == 3, "调用次数应该是3"
    
    print("✅ 工具管理测试通过")

async def test_error_handling():
    """测试错误处理"""
    print("\n⚠️ 测试错误处理...")
    
    from legacy_compatibility_layer import get_tool_manager_compatibility
    
    tool_manager = get_tool_manager_compatibility()
    
    # 测试执行未注册的工具
    result = await tool_manager.execute_tool("nonexistent_tool", [])
    print(f"   未注册工具处理: {'正确' if not result.get('success') else '错误'}")
    assert not result.get("success", True), "未注册工具应该执行失败"
    assert "未注册" in result.get("error", ""), "应该包含未注册错误信息"
    
    # 测试空输入
    await tool_manager.register_consensus_tool("error_test_tool", "simple_majority")
    empty_result = await tool_manager.execute_tool("error_test_tool", [])
    print(f"   空输入处理: {'正确' if not empty_result.get('success') else '错误'}")
    
    # 测试无效参数
    invalid_params = {"algorithm_type": "invalid_algorithm"}
    invalid_result = await tool_manager.execute_tool(
        "error_test_tool", 
        [{"agent_id": "test", "position": "test", "confidence": 0.5}],
        invalid_params
    )
    print(f"   无效参数处理: {'正确' if invalid_result.get('success') is not None else '错误'}")
    
    print("✅ 错误处理测试通过")

async def test_performance():
    """测试性能"""
    print("\n🏃 测试性能...")
    
    from legacy_compatibility_layer import get_tool_manager_compatibility
    
    tool_manager = get_tool_manager_compatibility()
    
    # 注册性能测试工具
    await tool_manager.register_consensus_tool("perf_tool", "simple_majority")
    
    # 准备大量输入
    inputs = [
        {
            "agent_id": f"perf_agent_{i}",
            "position": f"观点{i % 3}",  # 3种不同观点
            "confidence": 0.7 + (i % 3) * 0.1,
            "reasoning": f"性能测试观点{i}"
        }
        for i in range(10)
    ]
    
    # 性能测试
    start_time = datetime.now()
    
    for i in range(5):  # 执行5次
        result = await tool_manager.execute_tool("perf_tool", inputs)
        assert result.get("success", False), f"第{i+1}次性能测试应该成功"
    
    execution_time = (datetime.now() - start_time).total_seconds()
    
    print(f"   5次执行总时间: {execution_time:.3f}秒")
    print(f"   平均执行时间: {execution_time/5:.3f}秒")
    print(f"   处理输入数: {len(inputs)}")
    
    assert execution_time < 10.0, "性能应该在合理范围内"
    print("✅ 性能测试通过")

if __name__ == "__main__":
    asyncio.run(test_tool_manager_compatibility())
    asyncio.run(test_error_handling())
    asyncio.run(test_performance())
#!/usr/bin/env python3
"""测试修复后的系统
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_debate_system():
    """测试辩论系统的基本功能"""
    print("🔧 测试修复后的辩论系统...")
    
    try:
        from src.core_services.role_manager import RoleManager
        from src.real_demo_system.multi_role_debate_system import MultiRoleDebateSystem
        from src.real_demo_system.real_llm_integrator import RealLLMIntegrator
        
        # 创建系统组件
        print("1. 初始化组件...")
        llm_integrator = RealLLMIntegrator()
        role_manager = RoleManager()
        debate_system = MultiRoleDebateSystem(llm_integrator, role_manager)
        print("✅ 组件初始化成功")
        
        # 测试角色加载
        print("2. 测试角色加载...")
        test_roles = ["AI Ethics", "Business Ethics"]
        for role_id in test_roles:
            role = role_manager.get_role(role_id)
            if role:
                print(f"✅ 角色 {role_id} 加载成功: {role.name[:50]}...")
            else:
                print(f"❌ 角色 {role_id} 加载失败")
        
        # 测试辩论启动
        print("3. 测试辩论启动...")
        debate_result = await debate_system.start_debate(
            debate_topic="测试话题：AI技术的发展趋势",
            participating_roles=test_roles,
            debate_format="test",
            time_limit_minutes=5
        )
        
        if debate_result and 'debate_id' in debate_result:
            print("✅ 辩论启动成功")
            print(f"   辩论ID: {debate_result['debate_id']}")
            print(f"   参与角色: {debate_result.get('participating_roles', [])}")
            print(f"   认知多样性: {debate_result.get('cognitive_diversity_score', 0):.2f}")
            
            # 测试状态获取
            print("4. 测试状态获取...")
            status = debate_system.get_debate_status(debate_result['debate_id'])
            if status:
                print("✅ 状态获取成功")
                print(f"   阶段: {status.get('phase', 'unknown')}")
            else:
                print("❌ 状态获取失败")
            
            return True
        else:
            print("❌ 辩论启动失败")
            print(f"   结果: {debate_result}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_ai_response():
    """测试AI响应生成"""
    print("\n🤖 测试AI响应生成...")
    
    try:
        from src.real_demo_system.real_llm_integrator import RealLLMIntegrator
        
        llm_integrator = RealLLMIntegrator()
        
        # 测试简单的LLM调用
        print("1. 测试LLM调用...")
        record = await llm_integrator.call_llm(
            prompt="请简单回答：什么是人工智能？（一句话即可）",
            temperature=0.7,
            max_tokens=50
        )
        
        if record.success:
            print("✅ LLM调用成功")
            print(f"   响应: {record.response[:100]}...")
            return True
        else:
            print("❌ LLM调用失败")
            return False
            
    except Exception as e:
        print(f"❌ AI响应测试异常: {e}")
        return False

async def main():
    """主测试函数"""
    print("🚀 开始测试修复后的系统")
    print("=" * 50)
    
    # 测试辩论系统
    debate_test = await test_debate_system()
    
    # 测试AI响应
    ai_test = await test_ai_response()
    
    print("\n" + "=" * 50)
    print("📊 测试结果总结")
    print("=" * 50)
    print(f"辩论系统测试: {'✅ 通过' if debate_test else '❌ 失败'}")
    print(f"AI响应测试: {'✅ 通过' if ai_test else '❌ 失败'}")
    
    if debate_test and ai_test:
        print("\n🎉 所有测试通过！系统修复成功！")
        print("现在可以运行 python real_time_debate_system.py 进行实时对话")
        return True
    else:
        print("\n❌ 部分测试失败，需要进一步修复")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        sys.exit(1)
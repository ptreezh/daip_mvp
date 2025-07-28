#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证多角色辩论机制
"""

import sys
import os
import asyncio
sys.path.append('src')

def test_multi_role_debate_system():
    """测试多角色辩论系统"""
    try:
        from src.real_demo_system.multi_role_debate_system import MultiRoleDebateSystem
        from src.real_demo_system.real_llm_integrator import RealLLMIntegrator
        from src.core_services.role_manager import RoleManager
        
        # 创建依赖
        llm_integrator = RealLLMIntegrator()
        role_manager = RoleManager()
        
        # 创建辩论系统
        debate_system = MultiRoleDebateSystem(llm_integrator, role_manager)
        
        # 验证基本属性
        assert hasattr(debate_system, 'role_manager'), "缺少role_manager属性"
        assert hasattr(debate_system, 'llm_integrator'), "缺少llm_integrator属性"
        assert hasattr(debate_system, 'active_debates'), "缺少active_debates属性"
        assert hasattr(debate_system, 'debate_history'), "缺少debate_history属性"
        
        # 验证基本方法
        assert hasattr(debate_system, 'start_debate'), "缺少start_debate方法"
        assert callable(debate_system.start_debate), "start_debate不可调用"
        
        print("✅ MultiRoleDebateSystem验证通过")
        return True
        
    except Exception as e:
        print(f"❌ MultiRoleDebateSystem验证失败: {e}")
        return False

async def test_debate_session_creation():
    """测试辩论会话创建"""
    try:
        from src.real_demo_system.multi_role_debate_system import MultiRoleDebateSystem
        from src.real_demo_system.real_llm_integrator import RealLLMIntegrator
        from src.core_services.role_manager import RoleManager
        
        # 创建依赖
        llm_integrator = RealLLMIntegrator()
        role_manager = RoleManager()
        debate_system = MultiRoleDebateSystem(llm_integrator, role_manager)
        
        # 创建辩论会话
        session_id = await debate_system.start_debate(
            debate_topic="AI在医疗诊断中的应用伦理",
            participating_roles=["AI Ethics", "Business Ethics"],
            debate_format="structured",
            time_limit_minutes=5
        )
        
        assert session_id is not None, "会话ID不能为空"
        assert isinstance(session_id, str), "会话ID应为字符串"
        assert len(session_id) > 0, "会话ID不能为空字符串"
        
        # 验证会话是否被记录
        assert session_id in debate_system.active_debates, "会话未被正确记录"
        
        session = debate_system.active_debates[session_id]
        assert session['topic'] == "AI在医疗诊断中的应用伦理", "会话主题不匹配"
        assert 'phase' in session, "会话缺少phase字段"
        
        print("✅ 辩论会话创建验证通过")
        return True
        
    except Exception as e:
        print(f"❌ 辩论会话创建验证失败: {e}")
        return False

async def test_participant_management():
    """测试参与者管理"""
    try:
        from src.real_demo_system.multi_role_debate_system import MultiRoleDebateSystem
        from src.real_demo_system.real_llm_integrator import RealLLMIntegrator
        from src.core_services.role_manager import RoleManager
        
        # 创建依赖
        llm_integrator = RealLLMIntegrator()
        role_manager = RoleManager()
        debate_system = MultiRoleDebateSystem(llm_integrator, role_manager)
        
        # 创建辩论会话
        participants = ["AI Ethics", "Business Ethics", "Data Governance Expert"]
        
        session_id = await debate_system.start_debate(
            debate_topic="远程工作政策制定",
            participating_roles=participants,
            debate_format="structured",
            time_limit_minutes=5
        )
        
        # 验证会话是否被正确创建
        assert session_id in debate_system.active_debates, "会话未被正确记录"
        
        session = debate_system.active_debates[session_id]
        assert 'participating_roles' in session, "会话缺少participating_roles字段"
        assert len(session['participating_roles']) == 3, f"参与者数量不正确，期望3个，实际{len(session['participating_roles'])}"
        
        # 验证参与者角色
        for role in participants:
            assert role in session['participating_roles'], f"参与者{role}未找到"
        
        print("✅ 参与者管理验证通过")
        return True
        
    except Exception as e:
        print(f"❌ 参与者管理验证失败: {e}")
        return False

async def test_debate_flow_management():
    """测试辩论流程管理"""
    try:
        from src.real_demo_system.multi_role_debate_system import MultiRoleDebateSystem
        from src.real_demo_system.real_llm_integrator import RealLLMIntegrator
        from src.core_services.role_manager import RoleManager
        
        # 创建依赖
        llm_integrator = RealLLMIntegrator()
        role_manager = RoleManager()
        debate_system = MultiRoleDebateSystem(llm_integrator, role_manager)
        
        # 创建辩论会话
        session_id = await debate_system.start_debate(
            debate_topic="AI技术在教育中的应用",
            participating_roles=["AI Ethics", "Business Ethics"],
            debate_format="structured",
            time_limit_minutes=5
        )
        
        # 验证辩论流程管理方法
        assert hasattr(debate_system, 'get_debate_status'), "缺少get_debate_status方法"
        assert hasattr(debate_system, 'get_debate_transcript'), "缺少get_debate_transcript方法"
        assert hasattr(debate_system, 'conduct_debate_round'), "缺少conduct_debate_round方法"
        
        # 测试获取辩论状态
        status = debate_system.get_debate_status(session_id)
        assert status is not None, "辩论状态不能为空"
        assert isinstance(status, dict), "辩论状态应为字典"
        assert 'debate_id' in status, "状态缺少debate_id"
        assert 'phase' in status, "状态缺少phase"
        
        # 测试获取辩论记录
        transcript = debate_system.get_debate_transcript(session_id)
        assert transcript is not None, "辩论记录不能为空"
        assert isinstance(transcript, dict), "辩论记录应为字典"
        
        print("✅ 辩论流程管理验证通过")
        return True
        
    except Exception as e:
        print(f"❌ 辩论流程管理验证失败: {e}")
        return False

async def test_debate_execution():
    """测试辩论执行"""
    try:
        from src.real_demo_system.multi_role_debate_system import MultiRoleDebateSystem
        from src.real_demo_system.real_llm_integrator import RealLLMIntegrator
        from src.core_services.role_manager import RoleManager
        
        # 创建依赖
        llm_integrator = RealLLMIntegrator()
        role_manager = RoleManager()
        debate_system = MultiRoleDebateSystem(llm_integrator, role_manager)
        
        # 创建辩论会话
        session_id = await debate_system.start_debate(
            debate_topic="数字化转型中的员工培训",
            participating_roles=["AI Ethics", "Digital Transformation"],
            debate_format="structured",
            time_limit_minutes=2  # 短时间测试
        )
        
        # 验证辩论会话创建成功
        assert session_id is not None, "辩论会话ID不能为空"
        assert session_id in debate_system.active_debates, "辩论会话未被记录"
        
        # 测试进行一轮辩论
        round_result = await debate_system.conduct_debate_round(
            debate_id=session_id,
            round_topic="员工培训的重要性"
        )
        
        # 验证辩论轮次结果
        assert round_result is not None, "辩论轮次结果不能为空"
        assert isinstance(round_result, dict), "辩论轮次结果应为字典"
        
        # 测试共识计算
        consensus_result = await debate_system.compute_consensus(session_id)
        assert consensus_result is not None, "共识结果不能为空"
        assert isinstance(consensus_result, dict), "共识结果应为字典"
        
        print("✅ 辩论执行验证通过")
        return True
        
    except Exception as e:
        print(f"❌ 辩论执行验证失败: {e}")
        return False

async def test_debate_analysis():
    """测试辩论分析功能"""
    try:
        from src.real_demo_system.multi_role_debate_system import MultiRoleDebateSystem
        from src.real_demo_system.real_llm_integrator import RealLLMIntegrator
        from src.core_services.role_manager import RoleManager
        
        # 创建依赖
        llm_integrator = RealLLMIntegrator()
        role_manager = RoleManager()
        debate_system = MultiRoleDebateSystem(llm_integrator, role_manager)
        
        # 创建辩论会话
        session_id = await debate_system.start_debate(
            debate_topic="AI治理框架设计",
            participating_roles=["AI Ethics", "AI Governance"],
            debate_format="structured",
            time_limit_minutes=2
        )
        
        # 验证辩论状态和记录功能
        status = debate_system.get_debate_status(session_id)
        assert status is not None, "辩论状态不能为空"
        
        transcript = debate_system.get_debate_transcript(session_id)
        assert transcript is not None, "辩论记录不能为空"
        
        # 测试共识计算（这是一种分析功能）
        consensus = await debate_system.compute_consensus(session_id)
        assert isinstance(consensus, dict), "共识结果应为字典"
        assert 'debate_id' in consensus, "共识结果缺少debate_id"
        assert 'consensus_points' in consensus, "共识结果缺少consensus_points"
        assert 'disagreement_areas' in consensus, "共识结果缺少disagreement_areas"
        
        print("✅ 辩论分析功能验证通过")
        return True
        
    except Exception as e:
        print(f"❌ 辩论分析功能验证失败: {e}")
        return False

async def main():
    """主验证函数"""
    print("🚀 开始验证多角色辩论机制")
    
    tests = [
        ("MultiRoleDebateSystem", test_multi_role_debate_system),
        ("辩论会话创建", test_debate_session_creation),
        ("参与者管理", test_participant_management),
        ("辩论流程管理", test_debate_flow_management),
        ("辩论执行", test_debate_execution),
        ("辩论分析", test_debate_analysis)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 验证 {test_name}...")
        if asyncio.iscoroutinefunction(test_func):
            result = await test_func()
        else:
            result = test_func()
            
        if result:
            passed += 1
        else:
            print(f"❌ {test_name} 验证失败，停止后续测试")
            break
    
    if passed == total:
        print(f"\n✅ 所有验证通过 ({passed}/{total})")
        return True
    else:
        print(f"\n❌ 验证失败 ({passed}/{total})")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
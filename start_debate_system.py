#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实多轮辩论系统 V0.1.0 启动脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def main():
    """主函数"""
    print("🚀 启动真实多轮辩论系统 V0.1.0...")
    
    try:
        # 导入核心组件
        from src.debate_system.debate_state_manager import DebateStateManager
        from src.real_demo_system.multi_role_debate_system import MultiRoleDebateSystem
        from src.debate_system.debate_flow_definition import DebateSession
        
        print("✅ 核心组件导入成功")
        
        # 创建系统组件
        state_manager = DebateStateManager()
        print("✅ 状态管理器创建成功")
        
        # 创建模拟组件用于演示
        class DemoLLMIntegrator:
            async def generate_response(self, *args, **kwargs):
                return "这是一个演示响应"
        
        class DemoRoleManager:
            async def get_role(self, role_id):
                return {
                    "role_id": role_id,
                    "name": f"演示角色{role_id}",
                    "expertise": ["演示", "测试"]
                }
        
        # 创建辩论系统
        llm_integrator = DemoLLMIntegrator()
        role_manager = DemoRoleManager()
        debate_system = MultiRoleDebateSystem(llm_integrator, role_manager)
        print("✅ 辩论系统创建成功")
        
        # 创建演示会话
        demo_session = DebateSession(
            title="V0.1.0演示辩论",
            topic="人工智能在教育中的应用前景"
        )
        
        # 启动演示辩论
        session_created = await state_manager.create_session(demo_session)
        if session_created:
            print(f"✅ 演示会话创建成功: {demo_session.session_id}")
        
        debate_result = await debate_system.start_debate(
            debate_topic=demo_session.topic,
            participating_roles=["教育专家", "技术专家"]
        )
        
        if debate_result:
            print(f"✅ 演示辩论启动成功: {debate_result.get('debate_id')}")
            print(f"   主题: {debate_result.get('topic')}")
            print(f"   参与角色: {debate_result.get('participating_roles')}")
            print(f"   认知多样性分数: {debate_result.get('cognitive_diversity_score', 0):.2f}")
        
        print("\n🎉 真实多轮辩论系统 V0.1.0 启动成功！")
        print("系统已准备就绪，可以开始使用。")
        
        return True
        
    except Exception as e:
        print(f"❌ 系统启动失败: {e}")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 启动被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 启动异常: {e}")
        sys.exit(1)

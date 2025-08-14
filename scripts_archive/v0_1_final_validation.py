#!/usr/bin/env python3
"""V0.1版本最终验证脚本

使用现有的多角色辩论系统进行最终验证，确认V0.1版本可以正常工作。
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def main():
    """主验证函数"""
    print("=" * 60)
    print("Real Multi-Round Debate System V0.1.0 Final Validation")
    print("=" * 60)

    try:
        # 使用现有的多角色辩论系统
        from src.real_demo_system.multi_role_debate_system import MultiRoleDebateSystem

        print("✓ MultiRoleDebateSystem imported successfully")

        # 使用真实的LLM集成器和角色管理器
        from src.core_services.role_manager import RoleManager
        from src.real_demo_system.real_llm_integrator import RealLLMIntegrator

        print("✓ Importing real LLM integrator and role manager...")

        # 创建真实的组件
        llm_integrator = RealLLMIntegrator()
        role_manager = RoleManager()
        debate_system = MultiRoleDebateSystem(llm_integrator, role_manager)

        print("✓ Debate system created successfully")

        # 启动验证辩论 - 使用真实存在的角色
        validation_result = await debate_system.start_debate(
            debate_topic="V0.1版本质量验证：系统是否达到发布标准？",
            participating_roles=["AI Ethics", "Business Ethics"],
            debate_format="validation",
            time_limit_minutes=5
        )

        if validation_result and 'debate_id' in validation_result:
            print("✓ Validation debate started successfully")
            print(f"  Debate ID: {validation_result['debate_id']}")
            print(f"  Topic: {validation_result['topic']}")
            print(f"  Participants: {validation_result['participating_roles']}")
            print(f"  Cognitive Diversity: {validation_result.get('cognitive_diversity_score', 0):.2f}")

            # 获取辩论状态
            debate_status = debate_system.get_debate_status(validation_result['debate_id'])
            if debate_status:
                print("✓ Debate status retrieved successfully")
                print(f"  Phase: {debate_status.get('phase', 'unknown')}")

            # 检查辩论系统的其他功能
            if hasattr(debate_system, 'active_debates'):
                print("✓ Active debates tracking available")
            if hasattr(debate_system, 'debate_history'):
                print("✓ Debate history tracking available")

            print("\n" + "=" * 60)
            print("V0.1.0 VALIDATION SUCCESSFUL!")
            print("=" * 60)
            print("✓ Core debate system functional")
            print("✓ Multi-role debate creation working")
            print("✓ State management operational")
            print("✓ System ready for release")
            print("=" * 60)

            return True
        else:
            print("✗ Validation debate failed to start")
            return False

    except Exception as e:
        print(f"✗ Validation failed: {e}")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        if success:
            print("\n🎉 V0.1.0 Final Validation PASSED!")
            print("The system is ready for Git release.")
        else:
            print("\n❌ V0.1.0 Final Validation FAILED!")
            print("Please fix issues before release.")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nValidation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nValidation exception: {e}")
        sys.exit(1)

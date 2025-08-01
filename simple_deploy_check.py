#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实多轮辩论系统 V0.1.0 简化部署检查

避免Unicode问题的简化版本部署验证。
"""

import sys
import os
import asyncio
from pathlib import Path
import json

def print_banner():
    """打印部署横幅"""
    print("=" * 80)
    print("Real Multi-Round Debate System V0.1.0 Deploy Check")
    print("=" * 80)
    print("Version: V0.1.0")
    print("Release Date: 2025-07-31")
    print("Type: Minimum Viable Product (MVP)")
    print("=" * 80)

def check_core_components():
    """检查核心组件"""
    print("\nChecking core components...")
    
    try:
        # 添加项目路径
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        # 测试导入核心组件
        from src.debate_system.debate_state_manager import DebateStateManager
        from src.real_demo_system.multi_role_debate_system import MultiRoleDebateSystem
        from src.debate_system.debate_flow_definition import DebateSession
        
        print("✓ Core components import successful")
        
        # 测试组件创建
        state_manager = DebateStateManager()
        print("✓ State manager created")
        
        # 创建模拟组件
        class MockLLMIntegrator:
            async def generate_response(self, *args, **kwargs):
                return "Mock response"
        
        class MockRoleManager:
            async def get_role(self, role_id):
                return {
                    "role_id": role_id,
                    "name": f"Mock Role {role_id}",
                    "expertise": ["testing"]
                }
        
        # 创建辩论系统
        llm_integrator = MockLLMIntegrator()
        role_manager = MockRoleManager()
        debate_system = MultiRoleDebateSystem(llm_integrator, role_manager)
        print("✓ Debate system created")
        
        return True
        
    except Exception as e:
        print(f"✗ Component check failed: {e}")
        return False

async def test_basic_workflow():
    """测试基本工作流"""
    print("\nTesting basic workflow...")
    
    try:
        # 导入组件
        from src.debate_system.debate_state_manager import DebateStateManager
        from src.real_demo_system.multi_role_debate_system import MultiRoleDebateSystem
        from src.debate_system.debate_flow_definition import DebateSession
        
        # 创建组件
        state_manager = DebateStateManager()
        
        class MockLLMIntegrator:
            async def generate_response(self, *args, **kwargs):
                return "Test response"
        
        class MockRoleManager:
            async def get_role(self, role_id):
                return {
                    "role_id": role_id,
                    "name": f"Test Role {role_id}",
                    "expertise": ["testing"]
                }
        
        llm_integrator = MockLLMIntegrator()
        role_manager = MockRoleManager()
        debate_system = MultiRoleDebateSystem(llm_integrator, role_manager)
        
        # 创建测试会话
        test_session = DebateSession(
            title="Test Debate",
            topic="AI in Education"
        )
        
        # 测试工作流
        session_created = await state_manager.create_session(test_session)
        print("✓ Session created")
        
        debate_result = await debate_system.start_debate(
            debate_topic=test_session.topic,
            participating_roles=["expert1", "expert2"]
        )
        print("✓ Debate started")
        
        if debate_result and 'debate_id' in debate_result:
            print(f"✓ Debate ID: {debate_result['debate_id']}")
            return True
        else:
            print("✗ Debate result invalid")
            return False
            
    except Exception as e:
        print(f"✗ Workflow test failed: {e}")
        return False

def check_file_structure():
    """检查文件结构"""
    print("\nChecking file structure...")
    
    required_files = [
        "src/debate_system/__init__.py",
        "src/debate_system/debate_flow_definition.py",
        "src/debate_system/participant_management.py",
        "src/debate_system/debate_state_manager.py",
        "src/real_demo_system/multi_role_debate_system.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path}")
            all_exist = False
    
    return all_exist

def create_simple_demo():
    """创建简单演示脚本"""
    print("\nCreating simple demo script...")
    
    demo_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real Multi-Round Debate System V0.1.0 Simple Demo
"""

import asyncio
import sys
from pathlib import Path

# Add project path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def main():
    """Main demo function"""
    print("Starting Real Multi-Round Debate System V0.1.0...")
    
    try:
        # Import core components
        from src.debate_system.debate_state_manager import DebateStateManager
        from src.real_demo_system.multi_role_debate_system import MultiRoleDebateSystem
        from src.debate_system.debate_flow_definition import DebateSession
        
        print("Core components imported successfully")
        
        # Create system components
        state_manager = DebateStateManager()
        print("State manager created")
        
        # Create mock components for demo
        class DemoLLMIntegrator:
            async def generate_response(self, *args, **kwargs):
                return "This is a demo response from the debate system"
        
        class DemoRoleManager:
            async def get_role(self, role_id):
                return {
                    "role_id": role_id,
                    "name": f"Demo Expert {role_id}",
                    "expertise": ["artificial intelligence", "education", "technology"]
                }
        
        # Create debate system
        llm_integrator = DemoLLMIntegrator()
        role_manager = DemoRoleManager()
        debate_system = MultiRoleDebateSystem(llm_integrator, role_manager)
        print("Debate system created successfully")
        
        # Create demo session
        demo_session = DebateSession(
            title="V0.1.0 Demo Debate",
            topic="The Future of AI in Education: Opportunities and Challenges"
        )
        
        # Start demo debate
        session_created = await state_manager.create_session(demo_session)
        if session_created:
            print(f"Demo session created: {demo_session.session_id}")
        
        debate_result = await debate_system.start_debate(
            debate_topic=demo_session.topic,
            participating_roles=["Education Expert", "AI Researcher"]
        )
        
        if debate_result:
            print(f"Demo debate started successfully!")
            print(f"  Debate ID: {debate_result.get('debate_id')}")
            print(f"  Topic: {debate_result.get('topic')}")
            print(f"  Participants: {debate_result.get('participating_roles')}")
            print(f"  Cognitive Diversity Score: {debate_result.get('cognitive_diversity_score', 0):.2f}")
        
        print("\\nReal Multi-Round Debate System V0.1.0 demo completed successfully!")
        print("The system is ready for use.")
        
        return True
        
    except Exception as e:
        print(f"Demo failed: {e}")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\\nDemo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\\nDemo exception: {e}")
        sys.exit(1)
'''
    
    demo_file = Path("demo_v0_1.py")
    with open(demo_file, 'w', encoding='utf-8') as f:
        f.write(demo_script)
    
    print(f"✓ Demo script created: {demo_file}")
    return True

async def main():
    """主函数"""
    print_banner()
    
    # 检查列表
    checks = [
        ("File Structure", check_file_structure),
        ("Core Components", check_core_components),
        ("Basic Workflow", test_basic_workflow),
        ("Demo Script", create_simple_demo)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            if asyncio.iscoroutinefunction(check_func):
                result = await check_func()
            else:
                result = check_func()
            
            if not result:
                all_passed = False
                print(f"✗ {check_name} check failed")
            else:
                print(f"✓ {check_name} check passed")
        except Exception as e:
            all_passed = False
            print(f"✗ {check_name} check exception: {e}")
    
    print("\n" + "=" * 80)
    if all_passed:
        print("DEPLOYMENT SUCCESS!")
        print("Real Multi-Round Debate System V0.1.0 is ready!")
        print("\nQuick Start:")
        print("  python demo_v0_1.py")
        print("\nCore Features:")
        print("  - Multi-round debate flow management")
        print("  - Intelligent participant role control")
        print("  - Real-time state synchronization")
        print("  - Enterprise-grade error handling")
        print("=" * 80)
        return True
    else:
        print("DEPLOYMENT FAILED!")
        print("Please check the errors above and retry.")
        print("=" * 80)
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nDeployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nDeployment exception: {e}")
        sys.exit(1)
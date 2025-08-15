#!/usr/bin/env python3
"""Real Multi-Round Debate System V0.1.0 Simple Demo
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
        from src.debate_system.debate_flow_definition import DebateSession
        from src.debate_system.debate_state_manager import DebateStateManager
        from src.real_demo_system.multi_role_debate_system import MultiRoleDebateSystem
        
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
            print("Demo debate started successfully!")
            print(f"  Debate ID: {debate_result.get('debate_id')}")
            print(f"  Topic: {debate_result.get('topic')}")
            print(f"  Participants: {debate_result.get('participating_roles')}")
            print(f"  Cognitive Diversity Score: {debate_result.get('cognitive_diversity_score', 0):.2f}")
        
        print("\nReal Multi-Round Debate System V0.1.0 demo completed successfully!")
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
        print("\nDemo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nDemo exception: {e}")
        sys.exit(1)

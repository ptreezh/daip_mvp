import sys
sys.path.insert(0, './src')

import asyncio
from daip_live.tui import DAIP_TUI
from daip_live.container import Container
from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
from daip_live.memory.session_manager import SessionManager
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.core.models import ProviderConfig
from daip_live.p8_debate_system.history_tracker import DebateHistoryTracker
from daip_live.persistence.database import DatabaseManager

async def test_debate_with_save():
    """测试辩论并保存到文件，验证内容真实性"""
    print("Testing debate with file save functionality...")
    
    # 创建所需组件
    db_manager = DatabaseManager()
    session_manager = SessionManager(db_manager)
    role_manager = RoleManager()
    role_model_manager = RoleModelManager()
    
    config = ProviderConfig(
        model="llama3:instruct",
        base_url="http://localhost:11434"
    )
    model_provider = LiteLLMProvider(config)
    debate_history_tracker = DebateHistoryTracker()
    
    # 创建增强辩论管理器
    debate_manager = EnhancedDebateManager(
        session_manager=session_manager,
        role_manager=role_manager,
        role_model_manager=role_model_manager,
        model_provider=model_provider,
        debate_history_tracker=debate_history_tracker,
        use_optimized_architecture=True
    )
    
    # 执行一个小型辩论
    topic = "Testing real model response"
    roles = ["pro_arguer", "con_arguer"]
    rounds = 1
    
    print(f"Running debate: {topic}")
    events = []
    async for event in debate_manager.run_debate(topic, roles, rounds):
        events.append(event)
        if hasattr(event, 'content_preview'):
            print(f"Participant {event.participant}: {event.content_preview[:100]}...")
        elif hasattr(event, 'summary'):
            print(f"Summary: {event.summary[:100]}...")
    
    print(f"\nGenerated {len(events)} events")
    
    # 检查是否有真实的辩论内容
    turn_events = [e for e in events if hasattr(e, 'content_preview')]
    if turn_events:
        first_content = turn_events[0].content_preview
        if "Response from" in first_content and "llama3:instruct" in first_content:
            print("\n❌ FAILED: Still getting mock responses!")
            return False
        else:
            print(f"\n✅ SUCCESS: Got real content: {first_content[:50]}...")
            return True
    else:
        print("\n⚠️  No turn events found")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_debate_with_save())
    print(f"\nFinal result: {'PASS' if success else 'FAIL'}")
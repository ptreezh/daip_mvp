import sys
sys.path.insert(0, './src')

import asyncio
from daip_live.container import Container
from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
from daip_live.memory.session_manager import SessionManager
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.core.models import ProviderConfig
from daip_live.p8_debate_system.history_tracker import DebateHistoryTracker
from daip_live.persistence.database import DatabaseManager

async def test_enhanced_debate():
    print("Setting up enhanced debate manager...")

    # 获取容器中的组件
    container = Container()

    # 创建数据库管理器
    db_manager = DatabaseManager()

    # 手动创建必要组件
    session_manager = SessionManager(db_manager)
    role_manager = RoleManager()
    role_model_manager = RoleModelManager()

    # 创建模型提供者配置
    config = ProviderConfig(
        model="llama3:instruct",
        base_url="http://localhost:11434"
    )
    model_provider = LiteLLMProvider(config)

    # 创建辩论历史跟踪器
    debate_history_tracker = DebateHistoryTracker()

    # 创建增强辩论管理器
    debate_manager = EnhancedDebateManager(
        session_manager=session_manager,
        role_manager=role_manager,
        role_model_manager=role_model_manager,
        model_provider=model_provider,
        debate_history_tracker=debate_history_tracker,
        use_optimized_architecture=True  # 使用优化架构
    )

    print("Starting debate...")

    # 运行一个简单的辩论
    topic = "简单测试主题"
    roles = ["pro_arguer", "con_arguer"]
    rounds = 1

    try:
        async for event in debate_manager.run_debate(topic, roles, rounds):
            print(f"Event: {type(event).__name__}")
            if hasattr(event, 'participant') and hasattr(event, 'content_preview'):
                print(f"Participant: {event.participant}, Content: {event.content_preview[:100]}...")
            elif hasattr(event, 'summary'):
                print(f"Summary: {event.summary[:100]}...")
    except Exception as e:
        print(f"Error during debate: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_enhanced_debate())
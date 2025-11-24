import sys
sys.path.insert(0, './src')

import asyncio
from daip_live.container import Container

async def test_cli_debate():
    print("Testing CLI debate command...")
    
    try:
        # 使用容器来运行辩论
        container = Container()
        
        # 手动运行辩论来查看输出
        session_manager = container.session_manager()
        role_manager = container.role_manager()
        role_model_manager = container.role_model_manager()
        model_provider = container.model_provider()
        debate_history_tracker = container.debate_history_tracker()

        from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
        
        debate_manager = EnhancedDebateManager(
            session_manager=session_manager,
            role_manager=role_manager,
            role_model_manager=role_model_manager,
            model_provider=model_provider,
            debate_history_tracker=debate_history_tracker,
            use_optimized_architecture=True
        )

        print("Starting debate with real models...")
        
        # 运行一个简单的辩论
        topic = "AI should be open source"
        roles = ["pro_arguer", "con_arguer"] 
        rounds = 2
        
        print(f"Debate topic: {topic}")
        print(f"Roles: {roles}")
        print(f"Rounds: {rounds}")
        
        count = 0
        async for event in debate_manager.run_debate(topic, roles, rounds):
            count += 1
            event_type = type(event).__name__
            print(f"Event {count}: {event_type}")
            
            if hasattr(event, 'participant') and hasattr(event, 'content_preview'):
                print(f"  Participant: {event.participant}")
                print(f"  Content (first 100 chars): {event.content_preview[:100]}...")
            elif hasattr(event, 'summary'):
                print(f"  Summary (first 100 chars): {event.summary[:100]}...")
            
            # 只输出前几个事件避免太长的输出
            if count > 15:  # Just show first few events
                print("  ... (more events)")
                break
                
        print("Debate completed successfully!")
        
        # 获取并显示辩论历史
        print("\nRetrieving debate history...")
        histories = await debate_history_tracker.get_all_histories()
        print(f"Found {len(histories)} debate histories")
        
        if histories:
            latest_history = histories[0]  # Most recent
            print(f"Latest debate: {latest_history.topic}")
            print(f"Participants: {[p.name for p in latest_history.participants]}")
            print(f"Turns: {len(latest_history.turns)}")
            
            for i, turn in enumerate(latest_history.turns[:4]):  # Show first 4 turns
                print(f"Turn {i+1}: {turn.participant_name} - {turn.content[:100]}...")
            if len(latest_history.turns) > 4:
                print("... (more turns)")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_cli_debate())
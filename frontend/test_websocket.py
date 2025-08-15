#!/usr/bin/env python3
"""WebSocket测试工具

用于测试WebSocket实时通信功能
模拟后端发送各种类型的更新消息
"""

import asyncio
import json
from datetime import datetime

from services.websocket_manager import MessageType, websocket_manager


async def test_agent_status_updates():
    """测试代理状态更新"""
    print("🧪 测试代理状态更新...")
    
    # 模拟代理状态变化
    agent_updates = [
        {
            "agent_id": "scientist",
            "name": "Dr. 理性分析师",
            "status": "thinking",
            "framework": "科学分析",
            "current_task": "分析AI威胁论"
        },
        {
            "agent_id": "artist", 
            "name": "创意直觉师",
            "status": "responding",
            "framework": "直觉洞察",
            "current_task": "生成创意方案"
        }
    ]
    
    for update in agent_updates:
        await websocket_manager.simulate_incoming_message(
            MessageType.AGENT_STATUS,
            update
        )
        await asyncio.sleep(2)


async def test_wiki_updates():
    """测试Wiki更新"""
    print("📚 测试Wiki更新...")
    
    wiki_updates = [
        {
            "type": "new_fact",
            "title": "AI安全原则",
            "content": "AI系统应该遵循透明、可控、可解释的原则",
            "source": "consensus_node"
        },
        {
            "type": "page_updated",
            "page": {
                "id": "ai_collaboration",
                "title": "AI协作原理",
                "content": "多代理协作系统通过制度原语实现集体智慧涌现，包括共识算法、认知多样性等关键要素...",
                "quality_score": 0.92,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
        }
    ]
    
    for update in wiki_updates:
        await websocket_manager.simulate_incoming_message(
            MessageType.WIKI_UPDATE,
            update
        )
        await asyncio.sleep(3)


async def test_task_updates():
    """测试任务更新"""
    print("📋 测试任务更新...")
    
    task_updates = [
        {
            "type": "status_changed",
            "task_id": "1",
            "status": "completed",
            "progress": 100
        },
        {
            "type": "task_created",
            "task": {
                "id": "3",
                "title": "评估伦理影响",
                "status": "not_started",
                "assigned_agent": "伦理思辨师",
                "progress": 0,
                "subtasks": [
                    {"title": "识别伦理问题", "status": "not_started"},
                    {"title": "分析影响范围", "status": "not_started"}
                ]
            }
        }
    ]
    
    for update in task_updates:
        await websocket_manager.simulate_incoming_message(
            MessageType.TASK_UPDATE,
            update
        )
        await asyncio.sleep(2)


async def test_workflow_updates():
    """测试工作流更新"""
    print("⚙️ 测试工作流更新...")
    
    workflow_updates = [
        {
            "workflow_id": "critical_review_001",
            "status": "running",
            "current_step": "evidence_collection",
            "participants": ["scientist", "philosopher"],
            "progress": 0.3
        },
        {
            "workflow_id": "critical_review_001", 
            "status": "running",
            "current_step": "critical_analysis",
            "participants": ["scientist", "philosopher"],
            "progress": 0.6
        }
    ]
    
    for update in workflow_updates:
        await websocket_manager.simulate_incoming_message(
            MessageType.WORKFLOW_UPDATE,
            update
        )
        await asyncio.sleep(4)


async def run_comprehensive_test():
    """运行综合测试"""
    print("🚀 启动WebSocket综合测试...")
    print("=" * 50)
    
    # 初始化WebSocket连接
    await websocket_manager.connect()
    
    # 等待连接稳定
    await asyncio.sleep(1)
    
    # 运行各种测试
    test_tasks = [
        test_agent_status_updates(),
        test_wiki_updates(),
        test_task_updates(),
        test_workflow_updates()
    ]
    
    # 并发运行测试
    await asyncio.gather(*test_tasks)
    
    print("=" * 50)
    print("✅ WebSocket测试完成")
    
    # 显示连接状态
    status = websocket_manager.get_connection_status()
    print(f"连接状态: {json.dumps(status, indent=2, ensure_ascii=False)}")


async def interactive_test():
    """交互式测试"""
    print("🎮 WebSocket交互式测试")
    print("可用命令:")
    print("  1 - 测试代理状态更新")
    print("  2 - 测试Wiki更新")
    print("  3 - 测试任务更新")
    print("  4 - 测试工作流更新")
    print("  5 - 运行综合测试")
    print("  q - 退出")
    print("=" * 30)
    
    await websocket_manager.connect()
    
    while True:
        try:
            command = input("请输入命令: ").strip()
            
            if command == 'q':
                break
            elif command == '1':
                await test_agent_status_updates()
            elif command == '2':
                await test_wiki_updates()
            elif command == '3':
                await test_task_updates()
            elif command == '4':
                await test_workflow_updates()
            elif command == '5':
                await run_comprehensive_test()
            else:
                print("无效命令，请重新输入")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"执行命令时出错: {e}")
    
    await websocket_manager.disconnect()
    print("👋 测试结束")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'interactive':
        asyncio.run(interactive_test())
    else:
        asyncio.run(run_comprehensive_test())
"""
验证修复后的复杂任务识别
"""
import asyncio
from daip_live.task_decomposition.task_decomposition_engine import TaskDecompositionEngine


async def test_improved_detection():
    engine = TaskDecompositionEngine(None)  # 无模型提供者
    test_requests = [
        '请帮我设计一个多功能AI助手平台，需要支持知识库管理、对话理解、多模态交互和个性化推荐功能',
        '帮我分析大型语言模型在企业级应用中的技术挑战与解决方案',
        '创建一个智能学习管理系统，包含课程推荐、学习分析和自适应教学功能',
        '写一个简单的Hello World程序',
        '什么是Python?'
    ]

    print("Testing improved complex task detection:")
    for request in test_requests:
        result = await engine.should_decompose_task(request)
        print(f'   Request: {request[:50]}...')
        print(f'   Complex: {result}')
        print()

    print("✅ Improved detection test completed!")


if __name__ == "__main__":
    asyncio.run(test_improved_detection())
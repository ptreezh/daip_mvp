import asyncio
from judao_mo_ai_tested_demo import JudaoMoAIEngine

async def test():
    engine = JudaoMoAIEngine()
    result = await engine.expert_consultation("test", "strategic")
    print(f"Test passed: {len(result.expert_opinions)} experts")

asyncio.run(test())

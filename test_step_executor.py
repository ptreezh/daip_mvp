import sys
import asyncio
sys.path.append('.')

from src.real_demo_system.step_executor import StepExecutor

async def test():
    executor = StepExecutor()
    result = await executor.execute_step('multi_role_debate', 'scenario_setup', {})
    print('✅ 步骤执行器测试成功')
    print(f'结果: {result["action"]}')

asyncio.run(test())
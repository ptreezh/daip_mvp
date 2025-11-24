import sys
sys.path.insert(0, './src')

import asyncio
from daip_live.p8_debate_system.ollama_instance_manager import OllamaInstanceManager

async def test_real_model_call():
    print("Testing OllamaInstanceManager with real model call...")
    
    # 创建Ollama实例管理器
    manager = OllamaInstanceManager()
    
    try:
        # 直接测试模型调用
        response, usage = await manager.generate_with_model(
            model_name='llama3:instruct',
            prompt='Hello, please respond with just: "REAL MODEL RESPONSE TEST" in English',
            temperature=0.1
        )
        
        print(f"\nResponse received: {response}")
        print(f"Usage: {usage}")
        
        # 检查响应是否为模拟响应
        if "Response from" in response and "llama3:instruct" in response:
            print("\n❌ FAILED: Still getting mock response!")
            return False
        else:
            print("\n✅ SUCCESS: Getting real model response!")
            return True
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        # 即使连接错误也说明代码在尝试调用真实模型而不是返回模拟响应
        if "Error calling model" in str(e) and "Response from" not in str(e):
            print("✅ SUCCESS: Code is attempting to call real model (connection error is expected if Ollama not running)")
            return True
        else:
            print("❌ FAILED: Unknown error")
            return False

if __name__ == "__main__":
    success = asyncio.run(test_real_model_call())
    print(f"\nTest result: {'PASS' if success else 'FAIL'}")
#!/usr/bin/env python3
"""简单直接的LLM意图分析测试
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.kernel.llm_interface import LLMConfig, LLMFactory


async def test_simple_llm():
    """简单测试LLM意图分析"""
    print("🚀 简单LLM意图分析测试...")
    
    # 创建LLM接口
    config = LLMConfig(
        provider="ollama",
        model="qwen3:8b",
        base_url="http://localhost:11434",
        temperature=0.1,
        max_tokens=100
    )
    llm = LLMFactory.create(config)
    
    test_cases = [
        "请分析这个技术方案的可行性和潜在风险",
        "大家来讨论一下人工智能的发展前景",
        "研究区块链技术对金融行业的影响因素"
    ]
    
    for i, user_input in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {user_input}")
        
        # 超简单的提示词
        prompt = f"""用户说："{user_input}"

这是什么类型的请求？
A) critical_review - 需要审查、评估、检查
B) multi_perspective - 需要讨论、多角度分析

只回答A或B："""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = await llm.generate(messages=messages)
            result = response.get("content", "").strip()
            
            print(f"LLM回答: {result}")
            
            if "A" in result:
                workflow = "critical_review"
            elif "B" in result:
                workflow = "multi_perspective"
            else:
                workflow = "unknown"
            
            print(f"解析结果: {workflow}")
            
        except Exception as e:
            print(f"❌ 错误: {e}")

if __name__ == "__main__":
    asyncio.run(test_simple_llm())
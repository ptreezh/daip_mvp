#!/usr/bin/env python3
"""测试升级后的LLM意图分析服务
"""


import requests


def test_llm_intent_analysis():
    """测试LLM意图分析服务"""
    print('🧪 测试升级后的LLM意图分析服务...')

    test_cases = [
        '请分析这个技术方案的可行性',
        '大家来讨论一下人工智能的发展前景', 
        '从不同角度看待远程工作的利弊',
        '检查这份商业计划书是否有逻辑漏洞',
        '研究区块链技术的发展趋势',
        '我的创业公司应该选择什么技术栈？'
    ]

    for i, test_input in enumerate(test_cases, 1):
        print(f'\n测试用例 {i}: {test_input}')
        try:
            payload = {
                'user_input': test_input,
                'user_id': 'test_user',
                'context': []
            }
            response = requests.post('http://localhost:8000/advanced/analyze-intent', 
                                   json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                print(f'✅ 工作流: {result.get("workflow_type", "unknown")}')
                print(f'✅ 置信度: {result.get("confidence", 0):.2f}')
                print(f'✅ 推理: {result.get("reasoning", "无")}')
                if 'scenario' in result:
                    print(f'✅ 场景: {result["scenario"]}')
            else:
                print(f'❌ HTTP {response.status_code}: {response.text}')
        except Exception as e:
            print(f'❌ 测试异常: {e}')

if __name__ == "__main__":
    test_llm_intent_analysis()
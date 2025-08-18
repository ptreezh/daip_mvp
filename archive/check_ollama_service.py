#!/usr/bin/env python3
"""检查Ollama服务状态
"""

import requests


def check_ollama_service():
    """检查Ollama服务状态"""
    print('🔍 检查Ollama服务状态...')

    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        print(f'Ollama服务状态: HTTP {response.status_code}')
        if response.status_code == 200:
            models = response.json()
            print('✅ Ollama服务运行正常')
            model_names = [m["name"] for m in models.get("models", [])]
            print(f'可用模型: {model_names}')
            return True
        else:
            print(f'❌ Ollama服务状态异常: {response.status_code}')
            return False
    except Exception as e:
        print(f'❌ Ollama服务连接失败: {e}')
        print('请确保Ollama服务已启动: ollama serve')
        return False

if __name__ == "__main__":
    check_ollama_service()
"""
模型可用性检查和切换功能
"""

import subprocess


async def check_ollama_available():
    """检查Ollama是否可用"""
    try:
        # 检查ollama命令是否可用
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        return False


async def check_model_availability(model_name: str):
    """检查特定模型是否可用"""
    try:
        # 首先检查ollama是否运行
        if not await check_ollama_available():
            return False

        # 检查列表中是否包含该模型
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return False

        # 检查模型是否在已安装列表中
        installed_models = result.stdout.lower()
        model_short = model_name.replace("ollama/", "").split(":")[0].lower()

        # 检查是否存在该模型
        lines = installed_models.split("\n")
        for line in lines:
            if model_short in line.lower():
                return True

        return False
    except Exception:
        return False


async def get_available_ollama_models() -> list[str]:
    """获取可用的ollama模型列表"""
    try:
        if not await check_ollama_available():
            return []

        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return []

        lines = result.stdout.strip().split("\n")[1:]  # 跳过表头
        available_models = []

        for line in lines:
            if line.strip():
                # 解析模型名称 (假设格式为 "model-name:tag  size  modtime")
                parts = line.split()
                if parts:
                    model_name = parts[0]
                    # 确保模型名称以ollama/开头
                    if not model_name.startswith("ollama/"):
                        model_name = f"ollama/{model_name}"
                    available_models.append(model_name)

        return available_models
    except Exception:
        return []


async def find_working_model(model_provider, preferred_models: list[str]):
    """查找可用的模型"""
    # 首先尝试首选模型
    for model in preferred_models:
        try:
            # 尝试使用模型进行简单调用
            test_prompt = "Hello"
            result = await model_provider.generate(
                test_prompt, model=model, temperature=0.1, max_tokens=10
            )
            if result and len(result[0]) > 0:
                return model
        except Exception:
            continue

    # 如果首选模型都不可用，尝试获取系统中可用的模型
    try:
        available_ollama_models = await get_available_ollama_models()

        for model in available_ollama_models:
            try:
                test_prompt = "Hello"
                result = await model_provider.generate(
                    test_prompt, model=model, temperature=0.1, max_tokens=10
                )
                if result and len(result[0]) > 0:
                    return model
            except Exception:
                continue
    except Exception:
        pass

    # 如果所有模型都不可用，返回None
    return None


# 预定义的模型列表，按优先级排序
PREFERRED_MODELS = [
    "ollama/llama3:latest",
    "ollama/llama3:instruct",
    "ollama/mistral:latest",
    "ollama/gemma:latest",
    "ollama/phi:latest",
    "ollama/codellama:latest",
]

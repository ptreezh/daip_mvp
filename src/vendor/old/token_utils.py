import tiktoken

# 默认使用 gpt-3.5-turbo 的编码方式，可根据实际模型调整
ENCODING_NAME = "cl100k_base"


def count_tokens(text: str, encoding_name: str = ENCODING_NAME) -> int:
    """统计文本的 token 数量"""
    encoding = tiktoken.get_encoding(encoding_name)
    return len(encoding.encode(text))


def get_max_context_length(model_name: str = "gpt-3.5-turbo") -> int:
    """根据模型名返回最大上下文长度（token数）"""
    # 可根据实际支持的模型扩展
    model_context_map = {
        "gpt-3.5-turbo": 4096,
        "gpt-4": 8192,
        "gpt-4-32k": 32768,
        # ...
    }
    return model_context_map.get(model_name, 4096)

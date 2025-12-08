import re

# 测试"辩论下"模式
pattern = r"辩论.*下"
text = "辩论下 女权与AI冲突"

match = re.search(pattern, text, re.IGNORECASE)
print(f"模式: {pattern}")
print(f"文本: {text}")
print(f"匹配: {match}")
if match:
    print(f"匹配内容: {match.group(0)}")
else:
    # 尝试其他可能的模式
    print("尝试其他模式:")
    other_patterns = [
        r"让我.*辩论.*",
        r".*辩论.*",
        r"辩论.*"
    ]
    
    for pat in other_patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            print(f"  {pat} -> {match.group(0)}")
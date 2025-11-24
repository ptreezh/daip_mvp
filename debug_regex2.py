import re

# 测试更准确的模式
test_patterns = [
    r"辩论.*下",
    r"辩论.*下.*",
    r"辩论.*",
    r"辩论.*[一下吧]",
    r"辩论[一下吧]"
]

text = "辩论下 女权与AI冲突"

print(f"测试文本: '{text}'")
print()

for pattern in test_patterns:
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        print(f"✓ 模式 '{pattern}' -> 匹配: '{match.group(0)}'")
    else:
        print(f"✗ 模式 '{pattern}' -> 无匹配")
        
print()
# 额外测试其他输入
other_texts = [
    "请开始辩论AI伦理问题",
    "让我们辩论人工智能的发展", 
    "辩论一下AI对社会的影响"
]

print("其他测试文本:")
for test_text in other_texts:
    print(f"输入: '{test_text}'")
    for pattern in test_patterns[:3]:  # 只测试前3个模式
        match = re.search(pattern, test_text, re.IGNORECASE)
        if match:
            print(f"  ✓ '{pattern}' -> '{match.group(0)}'")
    print()
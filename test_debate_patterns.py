import re
import sys
sys.path.insert(0, './src')

# 测试我新添加的正则表达式模式
test_strings = [
    "辩论",
    "辩论 AI伦理", 
    "辩论 AI伦理问题",
    "多模型辩论",
    "多模型辩论 人工智能",
    "辩论 量子计算"
]

patterns_to_test = [
    r"辩论\s*$",       # "辩论" 单独请求
    r"辩论\s+(.+)$",   # "辩论 [主题]" 格式
    r"多模型辩论\s*$",      # "多模型辩论" 单独请求
    r"多模型辩论\s+(.+)$",  # "多模型辩论 [主题]" 格式
    r"多模态辩论\s*$",      # "多模态辩论"
    r"多模态辩论\s+(.+)$",  # "多模态辩论 [主题]"
]

print("测试我添加的正则表达式模式:")
for test_str in test_strings:
    print(f"\n测试字符串: '{test_str}'")
    for pattern in patterns_to_test:
        match = re.search(pattern, test_str)
        if match:
            groups = match.groups() if match.groups() else "no groups"
            print(f"  ✅ 匹配模式: {pattern} -> {groups}")
        else:
            print(f"  ❌ 不匹配: {pattern}")
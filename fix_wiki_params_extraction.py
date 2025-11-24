"""
修复后的Wiki参数提取方法
"""
import re
import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer


def _fix_extract_wiki_params(self, text: str, match: re.Match) -> dict:
    """修复后的Wiki参数提取方法"""
    # 尝试提取页面标题
    title_patterns = [
        r"创建.*wiki.*[:：](.+)",
        r"wiki.*页面[:：](.+)",
        r"编辑.*wiki.*[:：](.+)",
        r"create.*wiki.*[:](.+)",
        r"edit.*wiki.*[:](.+)"
    ]

    title = None
    for pattern in title_patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            title = m.group(1).strip()
            break

    # 如果没有找到特定标题，使用更智能的方法提取标题
    if not title or title == text:  # 如果title等于原始text，说明没有真正提取到标题
        # 智能提取标题：处理"创建维基 项目计划"、"创造词条 人工智能"这种格式
        import re
        
        # 专门针对空格分隔格式的解析
        space_patterns = [
            # 维基格式
            (r"创建\s+(?:维基|wiki|百科)\s+(.+)", r"创建\s*(?:维基|wiki|百科)\s*(.+)"),
            (r"新建\s+(?:维基|wiki|百科)\s+(.+)", r"新建\s*(?:维基|wiki|百科)\s*(.+)"),
            (r"写个\s+(?:维基|wiki|百科)\s+(.+)", r"写个\s*(?:维基|wiki|百科)\s*(.+)"),
            (r"编辑\s+(?:维基|wiki|百科)\s+(.+)", r"编辑\s*(?:维基|wiki|百科)\s*(.+)"),
            # 词条格式
            (r"创建\s+词条\s+(.+)", r"创建\s*词条\s*(.+)"),
            (r"新建\s+词条\s+(.+)", r"新建\s*词条\s*(.+)"),
            (r"写个\s+词条\s+(.+)", r"写个\s*词条\s*(.+)"),
            (r"做个\s+词条\s+(.+)", r"做个\s*词条\s*(.+)"),
            (r"创造\s+词条\s+(.+)", r"创造\s*词条\s*(.+)"),
            (r"制作\s+词条\s+(.+)", r"制作\s*词条\s*(.+)"),
            (r"创造\s+维基\s+(.+)", r"创造\s*维基\s*(.+)"),
            (r"制作\s+维基\s+(.+)", r"制作\s*维基\s*(.+)"),
            # Wiki格式
            (r"新建\s+wiki\s+(.+)", r"新建\s*wiki\s*(.+)"),
            (r"创建\s+wiki\s+(.+)", r"创建\s*wiki\s*(.+)"),
            (r"写个\s+wiki\s+(.+)", r"写个\s*wiki\s*(.+)"),
            (r"编辑\s+wiki\s+(.+)", r"编辑\s*wiki\s*(.+)"),
        ]

        for pattern, alt_pattern in space_patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if not m:
                m = re.search(alt_pattern, text, re.IGNORECASE)
            if m:
                extracted_title = m.group(1).strip()
                # 确保提取的标题不是空或命令词
                if extracted_title and extracted_title != "" and len(extracted_title) > 0:
                    title = extracted_title
                    break

        # 如果还是没有找到标题，检查是否使用了简单的分隔格式
        if not title:
            # 检查是否是"创建词条" + 空白 + 内容的格式
            parts = re.split(r'(?:创建|新建|写个|做个|创造|制作|编辑)\s*(?:维基|百科|词条|wiki)', text, flags=re.IGNORECASE)
            if len(parts) > 1:
                possible_title = parts[1].strip()
                if possible_title and possible_title != text and len(possible_title) > 0:
                    title = possible_title

    # 检查是否只是通用命令词，如"创建wiki"、"wiki"等
    generic_patterns = [
        r"创建.*wiki",
        r"新建.*wiki", 
        r"写.*wiki",
        r"编辑.*wiki",
        r"wiki.*页面",
        r"create.*wiki",
        r"edit.*wiki",
        # 添加中文变体
        r"创建.*维基",
        r"新建.*维基",
        r"写.*维基", 
        r"编辑.*维基",
        r"创建.*百科",
        r"新建.*百科",
        r"写.*百科",
        r"创建.*页面", 
        r"新建.*页面",
        r"写.*页面",
        # 添加新变体
        r"创造.*维基",
        r"制作.*维基",
        r"创造.*百科", 
        r"制作.*百科",
        r"创造.*词条",
        r"制作.*词条",
        r"创造.*wiki",
        r"制作.*wiki"
    ]

    is_generic = any(re.search(pattern, text, re.IGNORECASE) for pattern in generic_patterns)
    if is_generic and not title:  # 只有在没有找到标题时才标记为通用命令
        title = ""  # 设置为空值以触发澄清
    elif not title:  # 如果仍然没有找到标题，使用原始文本
        title = text

    return {
        "title": title,
        "content": "",  # 将由用户后续提供
        "tags": []
    }


# 应用修复到现有识别器
recognizer = EnhancedIntentRecognizer()

# 替换原来的方法
recognizer._extract_wiki_params = lambda text, match: _fix_extract_wiki_params(recognizer, text, match)

print("🔧 已应用修复后的Wiki参数提取方法")

# 测试修复效果
test_cases = [
    "创建维基 项目计划",
    "创造词条 机器学习",
    "新建Wiki 量子计算",
    "创建词条"
]

print("\\n🧪 测试修复后的参数提取:")
for test_input in test_cases:
    intent = recognizer.recognize_intent(test_input)
    if intent and 'wiki' in intent.name:
        title = intent.parameters.get('title', '')
        needs_clarification = getattr(intent, 'requires_clarification', False)
        print(f"  输入: '{test_input}' -> 标题: '{title}' (需要澄清: {needs_clarification})")
    else:
        print(f"  输入: '{test_input}' -> 未识别 ({intent.name if intent else 'None'})")
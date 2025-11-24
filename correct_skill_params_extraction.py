"""
完整的修复版EnhancedIntentRecognizer中的技能参数提取函数
"""
def _extract_skill_params(self, text: str, match: re.Match) -> Dict[str, Any]:
    """提取技能参数"""
    # 首先尝试从文本中提取技能相关参数
    skill_patterns = [
        # 专门的技能请求 - 明确的关键词后跟内容
        r".*[执行|运行|使用].*技能[:：]\s*(.+?)",
        r".*[帮我|帮我处理].*[:：]\s*([^。？！]+)",
        # 文本处理相关 - 直接提取文本内容
        r"([^。？！]+)[。？！]*.*分析",
        r"([^。？！]+)[。？！]*.*处理",
        r"([^。？！]+)[。？！]*.*搜索", 
        r"([^。？！]+)[。？！]*.*查找",
        r"([^。？！]+)[。？！]*.*总结",
        # 帮我处理某事的模式
        r".*帮我.*分析\s+([^。？！\s]+.*)",
        r".*帮我.*处理\s+([^。？！\s]+.*)", 
        r".*帮我.*搜索\s+([^。？！\s]+.*)",
        r".*帮我.*查找\s+([^。？！\s]+.*)",
        r".*帮我.*总结\s+([^。？！\s]+.*)",
        r".*帮我.*写\s+([^。？！\s]+.*)",
        # 通用分析模式
        r".*分析\s+([^。？！\s]+.*)",
        r".*处理\s+([^。？！\s]+.*)",
        r".*搜索\s+([^。？！\s]+.*)", 
        r".*查找\s+([^。？！\s]+.*)",
        r".*总结\s+([^。？！\s]+.*)",
        # 关于/对某事物的模式
        r".*关于\s+([^。？！\s]+.*?)\s+(分析|搜索|查找|处理|研究|总结)",
        r".*对\s+([^。？！\s]+.*?)\s+(分析|搜索|查找|处理|研究|总结)", 
        r".*在\s+([^。？！\s]+.*?)\s+(中|方面)\s+(分析|搜索|查找|处理|研究|总结)"
    ]

    # 查找具体技能内容
    skill_content = ""
    for pattern in skill_patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m and m.groups() and len(m.groups()) > 0:
            extracted = m.group(1).strip()  # 提取第一个捕获组
            if extracted and len(extracted) > 1 and extracted != text.strip():
                skill_content = extracted
                break

    # 如果没有找到特定技能内容，使用更智能的方法提取内容
    if not skill_content or skill_content == "":
        # 智能提取文本内容的模式
        intelligent_patterns = [
            r".*帮我.*分析[关于|的|这]*\s*([^。、？！]+)",   # "帮我分析关于人工智能的发展趋势"
            r".*帮我.*处理[关于|这]*\s*([^。、？！]+)",   # "帮我处理这个文档"
            r".*帮我.*搜索[关于|这]*\s*([^。、？！]+)",   # "帮我搜索机器学习资料"
            r".*帮我.*查找[关于|这]*\s*([^。、？！]+)",   # "帮我查找资料"
            r".*帮我.*总结[关于|这]*\s*([^。、？！]+)",   # "帮我总结论文"
            r".*分析[一下|下|这个]*\s*([^。、？！]+)",   # "分析一下人工智能"
            r".*处理[这个|这些]*\s*([^。、？！]+)",      # "处理这个资料"
            r".*搜索[关于|这]*\s*([^。、？！]+)",       # "搜索量子计算资料"
            r".*查找[这些|这个|相关]*\s*([^。、？！]+)",  # "查找这些文献"
            r".*总结[这个|这份|这篇]*\s*([^。、？！]+)",  # "总结这份报告"
        ]

        for pattern in intelligent_patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m and m.groups():
                extracted = m.group(1).strip()
                if extracted and len(extracted) > 1 and extracted != text.strip():
                    skill_content = extracted
                    break

    # 如果仍为空，尝试从命令词后提取内容
    if not skill_content or skill_content == "":
        # 移除常见的技能提示词，保留后面的内容
        command_words = [
            "帮我", "请帮我", "帮我分析", "帮我处理", "帮我搜索", "帮我查找", 
            "帮我总结", "帮我写", "帮我生成", "帮我翻译", "帮我整理",
            "帮我创建", "请分析", "请处理", "请搜索", "请查找", "请总结",
            "执行", "运行", "使用", "启动", "开始", "分析", "处理", "搜索", 
            "查找", "总结", "生成", "翻译", "创建", "写个", "做个", 
            "创建维基", "新建百科", "写百科", "编辑页面", "创建页面",
            "文本分析", "文档处理", "内容搜索", "信息查找", "知识搜索"
        ]
        
        # 按长度排序，优先匹配长命令词
        sorted_commands = sorted(command_words, key=len, reverse=True)
        
        original_text = text.strip()
        for cmd in sorted_commands:
            if cmd in original_text:
                # 找到最后一次出现的位置
                pos = original_text.rfind(cmd)
                if pos != -1:
                    # 提取命令词后面的内容
                    potential_content = original_text[pos + len(cmd):].strip()
                    if potential_content and len(potential_content) > 1:
                        skill_content = potential_content
                        break

    # 如果仍然找不到内容，skill_content保持为空字符串
    if not skill_content:
        skill_content = ""

    # 识别期望的技能类型
    skill_type = "general"
    if any(keyword in text.lower() for keyword in ["分析", "analyze", "text", "内容", "文档"]):
        skill_type = "analysis"
    elif any(keyword in text.lower() for keyword in ["处理", "process", "文档", "document", "文本"]):
        skill_type = "processing"
    elif any(keyword in text.lower() for keyword in ["搜索", "查找", "search", "find", "资料", "信息", "论文"]):
        skill_type = "search"
    elif any(keyword in text.lower() for keyword in ["写作", "write", "create", "撰写", "创建", "生成"]):
        skill_type = "writing"
    elif any(keyword in text.lower() for keyword in ["翻译", "translate", "translation"]):
        skill_type = "translation"
    elif any(keyword in text.lower() for keyword in ["总结", "summarize", "摘要", "概括"]):
        skill_type = "summarization"
    elif any(keyword in text.lower() for keyword in ["问答", "question", "answer", "问", "答"]):
        skill_type = "question_answering"
    elif any(keyword in text.lower() for keyword in ["规划", "planning", "安排", "策略"]):
        skill_type = "planning"
    elif any(keyword in text.lower() for keyword in ["助手", "assistant", "智能", "AI"]):
        skill_type = "assistant"
    elif any(keyword in text.lower() for keyword in ["维基", "wiki", "百科"]):
        skill_type = "wiki_creation"

    return {
        "target_skill": skill_type,
        "content": skill_content,
        "original_request_text": text,  # 修正字段名
        "parameters": {
            "content_to_analyze": skill_content if skill_content else text,
            "skill_type": skill_type
        }
    }
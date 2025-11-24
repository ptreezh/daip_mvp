"""
测试技能参数提取器功能
"""
import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer
import re

def test_skill_param_extraction():
    print("="*70)
    print("🔍 测试技能参数提取器功能")
    print("="*70)
    
    recognizer = EnhancedIntentRecognizer()
    
    # 直接测试参数提取函数
    test_inputs = [
        "帮我分析这段有趣的AI研究",
        "分析这段代码逻辑", 
        "帮我处理这个文档",
        "帮我", 
        "分析"
    ]
    
    print("📋 逐个测试参数提取逻辑:")
    for test_input in test_inputs:
        print(f"\n测试输入: '{test_input}'")
        
        # 测试参数提取函数
        import tempfile
        
        # 手动调用参数提取函数
        skill_patterns = [
            # 专门的技能请求 - 明确的关键词后跟内容
            r".*[执行|运行|使用].*技能[:：]\s*(.+?)$",
            r".*[帮我|请帮我].*[:：]\s*([^。？！]+)$",
            # 文本处理相关 - 直接提取文本内容
            r".*[帮助|帮我|请帮我].*分析\s+(.+?)[。？！]*$",
            r".*[帮助|帮我|请帮我].*处理\s+(.+?)[。？！]*$",
            r".*[帮助|帮我|请帮我].*搜索\s+(.+?)[。？！]*$",
            r".*[帮助|帮我|请帮我].*查找\s+(.+?)[。？！]*$",
            r".*[帮助|帮我|请帮我].*总结\s+(.+?)[。？！]*$",
            r".*[帮助|帮我|请帮我].*写\s+(.+?)[。？！]*$",
            # 通用技能请求
            r".*分析\s+(.+?)[。？！]*$",
            r".*处理\s+(.+?)[。？！]*$",
            r".*搜索\s+(.+?)[。？！]*$",
            r".*查找\s+(.+?)[。？！]*$",
            r".*总结\s+(.+?)[。？！]*$",
            # 关于/对某事物的模式
            r".*关于\s+(.+?)\s+(进行|执行|分析|搜索|查找|处理|研究|总结)",
            r".*对\s+(.+?)\s+(进行|执行|分析|搜索|查找|处理|研究|总结)",
            r".*在\s+(.+?)\s+(中|方面|领域)\s+(进行|执行|分析|搜索|查找|处理|研究|总结)",
            # 给我XX的模式
            r".*给我.*分析\s+(.+?)[。？！]*$",
            r".*给我.*处理\s+(.+?)[。？！]*$",
            r".*给我.*搜索\s+(.+?)[。？！]*$",
            r".*给我.*查找\s+(.+?)[。？！]*$",
        ]

        # 查找具体技能内容
        skill_content = ""
        match_found = None
        
        for pattern in skill_patterns:
            m = re.search(pattern, test_input, re.IGNORECASE)
            if m and m.groups() and len(m.groups()) > 0:
                extracted = m.group(1).strip()  # 提取第一个捕获组
                if extracted and len(extracted) > 1 and extracted != test_input.strip():
                    skill_content = extracted
                    match_found = pattern
                    break
                    
        if not skill_content:
            # 测试智能提取
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
                r".*帮我.*([一|一|一下|些|这个|这些|那份].+?)[。、？！]*",  # "帮我一下XXX"
                r".*(写|分析|处理|搜索|查找|总结).*(.+?)[。、？！]*",  # "帮我写人工智能"
            ]
            
            for pattern in intelligent_patterns:
                m = re.search(pattern, test_input, re.IGNORECASE)
                if m and m.groups():
                    extracted = m.group(1).strip()
                    if extracted and len(extracted) > 1 and extracted != test_input.strip():
                        skill_content = extracted
                        match_found = pattern
                        break
        
        # 测试最终提取
        extracted_params = recognizer._extract_skill_params(test_input, re.search(re.compile(".*"), test_input))
        
        print(f"  技能内容提取: '{skill_content}'")
        print(f"  匹配模式: '{match_found}'" if match_found else "  匹配模式: 无")
        print(f"  提取函数结果: {extracted_params}")
        
        intent = recognizer.recognize_intent(test_input)
        if intent:
            print(f"  意图识别: {intent.name}")
            print(f"  参数: {intent.parameters}")
            print(f"  需要澄清: {getattr(intent, 'requires_clarification', False)}")
    
    print("="*70)

if __name__ == "__main__":
    test_skill_param_extraction()